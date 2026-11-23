"""Run manifests, freeze/verify, and the test-access ledger (Task 5). Orchestration side: never imported by onboard code.

* `run_manifest(...)`   everything needed to reproduce / audit one run: command line, git commit + dirty flag, library and
                        machine info, config files (sha256 + parsed), seed lists, split offsets, checkpoint ids (sha256),
                        calibration (OOD detector, threshold arrays) hashes.
* `freeze_manifest()`   the same for the whole code base + all trained artefacts; written once to protocol/freeze.json.
* `verify_freeze(root)` recomputes it and lists every difference (code, configs, checkpoints, calibration, thresholds).
* `claim_split(...)`    every evaluation on a held-out split is appended to results/test_access.jsonl; the confirmatory
                        'final' split additionally refuses to run unless the freeze verifies.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

SPLIT_OFFSET = {"val": 10_000, "test": 20_000, "fit": 30_000, "final": 40_000, "pilot": 60_000}
HELD_OUT = ("test", "final")
FREEZE_PATH = "protocol/freeze.json"
CODE_GLOBS = ("src/**/*.py", "scripts/*.py", "configs/*.yaml", "tests/*.py", "protocol/phase2_protocol.json")


def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _git(root: Path, *args) -> str | None:
    try:
        r = subprocess.run(["git", *args], capture_output=True, text=True, cwd=root, timeout=20)
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception:
        return None


def git_state(root: Path) -> dict:
    commit = _git(root, "rev-parse", "HEAD")
    status = _git(root, "status", "--porcelain", "--untracked-files=no")
    return {"commit": commit, "dirty": bool(status) if status is not None else None, "tag": _git(root, "describe", "--tags", "--always")}


def software_info() -> dict:
    info = {"python": platform.python_version(), "platform": platform.platform(), "machine": platform.machine(),
            "processor": platform.processor(), "cpu_count": os.cpu_count()}
    for mod in ("numpy", "torch", "yaml"):
        try:
            info[mod] = __import__(mod).__version__
        except Exception:
            info[mod] = None
    return info


def hash_tree(root: Path, globs=CODE_GLOBS) -> dict[str, str]:
    out = {}
    for g in globs:
        for p in sorted(root.glob(g)):
            if p.is_file() and "__pycache__" not in p.parts:
                out[str(p.relative_to(root))] = sha256_file(p)
    return out


def artefact_hashes(root: Path) -> dict[str, str]:
    """Checkpoints (best_val.pt / final.pt) and calibration files of every trained run found under results/."""
    out = {}
    for pat in ("results/*/train/*/checkpoints/*.pt", "results/*/train/*/*/checkpoints/*.pt", "results/*/calib/*/*.npz"):
        for p in sorted(root.glob(pat)):
            out[str(p.relative_to(root))] = sha256_file(p)
    return out


def run_manifest(root: Path, *, kind: str, configs=(), seeds=None, extra=None, artefacts=None) -> dict:
    root = Path(root)
    cfgs = {}
    for c in configs:
        p = Path(c) if Path(c).is_absolute() else root / c
        if p.exists():
            cfgs[str(Path(c))] = {"sha256": sha256_file(p), "text": p.read_text()}
    return {"kind": kind, "created": time.strftime("%Y-%m-%d %H:%M:%S %z"), "argv": sys.argv, "git": git_state(root),
            "software": software_info(), "configs": cfgs, "seeds": seeds, "split_offsets": SPLIT_OFFSET,
            "artefacts": artefacts or {}, **(extra or {})}


def write_manifest(out_dir, manifest: dict, name: str = "run_manifest.json") -> Path:
    p = Path(out_dir); p.mkdir(parents=True, exist_ok=True)
    (p / name).write_text(json.dumps(manifest, indent=2, default=str))
    return p / name


# ------------------------------------------------------------------ thresholds
def thresholds_table(root: Path, pcts=(90.0, 95.0, 99.0)) -> dict:
    """Frozen alarm thresholds per system seed and percentile, recomputed from the stored in-distribution validation scores."""
    import numpy as np
    out = {}
    for d in sorted((root / "results").glob("*/calib/ens_s*")):
        z = np.load(d / "id_val_scores.npz")
        out[str(d.relative_to(root))] = {f"p{int(p)}": {"tau_unc": float(np.percentile(z["unc"], p)), "tau_ood": float(np.percentile(z["ood"], p))}
                                         for p in pcts}
    return out


# ------------------------------------------------------------------ freeze / verify
def freeze_manifest(root: Path, protocol: dict | None = None) -> dict:
    root = Path(root)
    return {"created": time.strftime("%Y-%m-%d %H:%M:%S %z"), "git": git_state(root), "software": software_info(),
            "code": hash_tree(root), "artefacts": artefact_hashes(root), "thresholds": thresholds_table(root),
            "split_offsets": SPLIT_OFFSET, "protocol": protocol or {}}


def diff_freeze(frozen: dict, now: dict) -> list[str]:
    problems = []
    for section in ("code", "artefacts"):
        a, b = frozen.get(section, {}), now.get(section, {})
        problems += [f"{section}: changed   {k}" for k in sorted(a) if k in b and a[k] != b[k]]
        problems += [f"{section}: missing   {k}" for k in sorted(a) if k not in b]
        problems += [f"{section}: new file  {k}" for k in sorted(b) if k not in a and section == "code"]
    if frozen.get("thresholds") != now.get("thresholds"):
        problems.append("thresholds: differ from the frozen values")
    if frozen.get("split_offsets") != now.get("split_offsets"):
        problems.append("split offsets differ")
    return problems


def verify_freeze(root: Path) -> list[str]:
    root = Path(root)
    p = root / FREEZE_PATH
    if not p.exists():
        return [f"no freeze manifest at {FREEZE_PATH}: run `python3 scripts/freeze.py freeze` first"]
    frozen = json.loads(p.read_text())
    return diff_freeze(frozen, freeze_manifest(root))


# ------------------------------------------------------------------ held-out split ledger
class SplitAccessError(RuntimeError):
    pass


def claim_split(root: Path, split: str, purpose: str, allow_unfrozen: bool = False) -> None:
    """Record every use of a held-out split. 'final' (confirmatory) requires a verified freeze."""
    root = Path(root)
    if split not in SPLIT_OFFSET:
        raise ValueError(f"unknown split {split!r}")
    if split == "final" and not allow_unfrozen:
        problems = verify_freeze(root)
        if problems:
            raise SplitAccessError("refusing to evaluate on the 'final' split: the code/artefacts do not match the freeze:\n  " +
                                   "\n  ".join(problems[:15]))
    if split in HELD_OUT:
        ledger = root / "results" / "test_access.jsonl"
        ledger.parent.mkdir(parents=True, exist_ok=True)
        with open(ledger, "a") as f:
            f.write(json.dumps({"time": time.strftime("%Y-%m-%d %H:%M:%S %z"), "split": split, "purpose": purpose,
                                "git": git_state(root), "argv": sys.argv}) + "\n")
