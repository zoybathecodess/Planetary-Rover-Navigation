"""ONE experiment interface for every method of the study (Task 5): baselines, shielded DQN/PPO, ensemble, and the
runtime-assurance system with its ablation variants. Orchestration side (loads checkpoints, uses the evaluator).

Method spec grammar:   astar | reactive | random | dqn | dqn_shield | ppo | ppo_shield | ens
                       assured[-<variant>][@<percentile>]      e.g.  assured   assured-no_ood@95   assured-monitor_only@90
Artefact layout (written by run_task3.py / run_task4.py):
   results/task3/train/{dqn,ppo}_s<k>/checkpoints/best_val.pt      results/task4/train/ens_s<k>/m<j>/checkpoints/best_val.pt
   results/task4/calib/ens_s<k>/{ood.npz,id_val_scores.npz}
"""
from __future__ import annotations

import csv
import json
import math
import re
import time
from dataclasses import replace
from pathlib import Path

import numpy as np

from src.evaluation.harness import ROW_FIELDS, evaluate_method, run_episode_ext
from src.evaluation.reproducibility import SPLIT_OFFSET

VARIANTS = {"full": {}, "no_ood": {"use_ood": False}, "no_unc": {"use_uncertainty": False}, "no_monitor": {"use_monitor": False},
            "no_stop": {"allow_stop": False}, "monitor_only": {"use_ood": False, "use_uncertainty": False},
            "unc_only": {"use_ood": False, "use_monitor": False}, "ood_only": {"use_uncertainty": False, "use_monitor": False},
            # amendment A1 (H3, protocol/amendment_A1_h3.json): same system, energy-blind fallback planner
            "fb_blind": {"fallback": "energy_blind"}, "fb_blind_no_stop": {"fallback": "energy_blind", "allow_stop": False}}
SEEDLESS = ("astar", "reactive", "random", "astar_monitor")
PRESETS = ("id", "terrain_shift", "sensor_shift", "dynamics_shift", "combined_shift")
VALID_REASONS = ("goal", "battery_depleted", "timeout", "safe_stop")
TRAIN_CONFIG = {"dqn": "configs/sim32_id.yaml", "ppo": "configs/sim32_id_ppo.yaml", "ens": "configs/sim32_id_ensemble.yaml"}
_SPEC = re.compile(r"^(?P<kind>[a-z_]+?)(?:-(?P<variant>[a-z_]+))?(?:@(?P<pct>\d+(?:\.\d+)?))?$")


def parse_method(spec: str) -> dict:
    m = _SPEC.match(spec)
    if not m:
        raise ValueError(f"bad method spec {spec!r}")
    kind, variant, pct = m["kind"], m["variant"], m["pct"]
    if kind == "assured":
        variant = variant or "full"
        if variant not in VARIANTS:
            raise ValueError(f"unknown assured variant {variant!r}; choose from {sorted(VARIANTS)}")
        return {"kind": "assured", "variant": variant, "pct": float(pct or 95.0), "spec": spec}
    if kind not in SEEDLESS + ("dqn", "dqn_shield", "ppo", "ppo_shield", "ens") or variant or pct:
        raise ValueError(f"unknown method {spec!r}")
    return {"kind": kind, "variant": None, "pct": None, "spec": spec}


def method_tag(spec: str, seed: int) -> str:
    m = parse_method(spec)
    if m["kind"] in SEEDLESS:
        return m["kind"]
    if m["kind"] == "assured":
        return f"assured{'' if m['variant'] == 'full' else '-' + m['variant']}_p{int(m['pct'])}_s{seed}"
    return f"{m['kind']}_s{seed}"


def checkpoint_paths(spec: str, seed: int, root: Path, ckpt: str = "best_val", n_members: int = 5) -> list[Path]:
    m = parse_method(spec)
    k = m["kind"]
    if k in SEEDLESS:
        return []
    if k in ("dqn", "dqn_shield", "ppo", "ppo_shield"):
        return [root / "results/task3/train" / f"{k.split('_')[0]}_s{seed}" / "checkpoints" / f"{ckpt}.pt"]
    return [root / "results/task4/train" / f"ens_s{seed}" / f"m{j}" / "checkpoints" / f"{ckpt}.pt" for j in range(n_members)]


def missing_artefacts(spec: str, seed: int, root: Path, ckpt: str = "best_val") -> list[Path]:
    need = checkpoint_paths(spec, seed, root, ckpt)
    if parse_method(spec)["kind"] == "assured":
        need += [root / "results/task4/calib" / f"ens_s{seed}" / f for f in ("ood.npz", "id_val_scores.npz")]
    return [p for p in need if not p.exists()]


def build_method(spec: str, seed: int, root: Path, ckpt: str = "best_val", keep_log: bool = False):
    from src.config import load_config
    from src.evaluation.harness import build_policy
    m, root = parse_method(spec), Path(root)
    k = m["kind"]
    if k == "astar_monitor":
        from src.assurance.controller import RuntimeAssuranceController
        from src.assurance.ensemble import AStarProposer
        from src.assurance.ood import MahalanobisOOD
        from src.policies.astar_battery import BatteryAwareAStar
        cfg = load_config(root / TRAIN_CONFIG["ens"])
        planner = BatteryAwareAStar(nominal_energy=cfg.env.ref_energy_cost, seed=0)
        dummy = MahalanobisOOD().fit(np.random.default_rng(0).normal(size=(500, 59)))
        pol = RuntimeAssuranceController(AStarProposer(planner), dummy, planner, replace(cfg.assurance, use_ood=False, use_uncertainty=False),
                                         np.inf, np.inf, cfg.env.ref_energy_cost)
        pol.name = "astar_monitor"
        return pol
    if k in SEEDLESS or k in ("dqn", "dqn_shield", "ppo", "ppo_shield"):
        base = "dqn" if k.startswith("dqn") else "ppo" if k.startswith("ppo") else None
        cfg = load_config(root / TRAIN_CONFIG[base or "dqn"])
        ck = str(checkpoint_paths(spec, seed, root, ckpt)[0]) if k not in SEEDLESS else None
        return build_policy(k, cfg, ck, seed=seed)
    cfg = load_config(root / TRAIN_CONFIG["ens"])
    from src.assurance.ood import MahalanobisOOD
    from src.evaluation.assurance_factory import build_assured, build_ensemble
    ens = build_ensemble(cfg, lambda j: checkpoint_paths(spec, seed, root, ckpt)[j], seed)
    calib = root / "results/task4/calib" / f"ens_s{seed}"
    if k == "ens":
        dummy = MahalanobisOOD().fit(np.random.default_rng(0).normal(size=(500, 59)))
        pol = build_assured(cfg, ens, dummy, np.inf, np.inf, acfg=replace(cfg.assurance, use_monitor=False, use_uncertainty=False, use_ood=False))
        pol.name = "ens"
        return pol
    ood = MahalanobisOOD.load(calib / "ood.npz")
    z = np.load(calib / "id_val_scores.npz")
    tu, to = float(np.percentile(z["unc"], m["pct"])), float(np.percentile(z["ood"], m["pct"]))
    return build_assured(cfg, ens, ood, tu, to, keep_log=keep_log, seed=seed, acfg=replace(cfg.assurance, **VARIANTS[m["variant"]]))


# ------------------------------------------------------------------ consistency of recorded outcomes
def validate_rows(rows: list[dict], capacity: float | None = 250.0) -> list[str]:
    """Every episode row must tell one consistent story about how the episode ended. Returns a list of problems."""
    bad = []
    for r in rows:
        tag = f"{r.get('method')}/{r.get('preset')}/{r.get('map')}"
        reason, ok = r["reason"], int(float(r["success"]))
        if reason not in VALID_REASONS:
            bad.append(f"{tag}: unknown terminal reason {reason!r}")
        if ok != (reason == "goal"):
            bad.append(f"{tag}: success={ok} but reason={reason}")
        steps, energy, left = float(r["steps"]), float(r["energy_used"]), float(r["battery_left"])
        if capacity is not None and abs((capacity - energy) - left) > 1e-6:
            bad.append(f"{tag}: battery_left {left} != capacity {capacity} - energy_used {energy}")
        if left < 0:
            bad.append(f"{tag}: negative battery")
        if reason == "battery_depleted" and left > 0:
            bad.append(f"{tag}: battery_depleted with {left} left")
        if reason == "goal" and not (math.isfinite(float(r["energy_ratio"])) and float(r["energy_ratio"]) > 0):
            bad.append(f"{tag}: success without a valid energy_ratio")
        if reason != "goal" and r["energy_ratio"] not in ("", "nan") and math.isfinite(float(r["energy_ratio"])):
            bad.append(f"{tag}: energy_ratio defined for a failed episode")
        if reason == "safe_stop" and float(r["collisions"]) < 0:
            bad.append(f"{tag}: bad collisions")
        if steps < 0 or float(r["collisions"]) < 0 or float(r["attempted_unsafe"]) < 0:
            bad.append(f"{tag}: negative counter")
    return bad


def check_pairing(by_method: dict[str, list[dict]]) -> list[str]:
    """Same maps, same order, same optimal cost for every method within a (preset, split): required for paired tests."""
    bad, ref_name, ref = [], None, None
    for name, rows in by_method.items():
        sig = [(r["map"], r["optimal_cost"]) for r in rows]
        if ref is None:
            ref_name, ref = name, sig
        elif sig != ref:
            bad.append(f"{name}: episodes differ from {ref_name} (maps / optimal cost / count)")
    return bad


# ------------------------------------------------------------------ one cell = (method, system seed, preset)
def run_cell(task: dict) -> dict:
    import torch
    torch.set_num_threads(1)
    root, out = Path(task["root"]), Path(task["out"])
    spec, k, preset, split, n_maps = task["spec"], task["seed"], task["preset"], task["split"], task["n_maps"]
    tag = method_tag(spec, k)
    miss = missing_artefacts(spec, k, root, task.get("ckpt", "best_val"))
    if miss:
        return {"tag": tag, "preset": preset, "status": "missing", "detail": str(miss[0].relative_to(root))}
    pol = build_method(spec, k, root, task.get("ckpt", "best_val"), keep_log=task.get("log_maps", 0) > 0)
    dest = out / split / preset
    off = SPLIT_OFFSET[split]
    seeds = list(range(off, off + n_maps))
    t0 = time.perf_counter()
    rows, summ = evaluate_method(pol, root / f"configs/sim32_{preset}.yaml", seeds, tag, preset, dest / f"{tag}.csv")
    wall = time.perf_counter() - t0
    problems = validate_rows(rows)
    if task.get("log_maps", 0) > 0 and parse_method(spec)["kind"] == "assured":
        from src.config import load_config
        from src.evaluation.evaluator import make_env
        env, ev = make_env(load_config(root / f"configs/sim32_{preset}.yaml").env, 0)
        pol.attach(env.explored_map, env.max_battery)
        (dest / "logs").mkdir(parents=True, exist_ok=True)
        with open(dest / "logs" / f"{tag}.jsonl", "w") as f:
            for s in seeds[:task["log_maps"]]:
                pol.log.clear()
                r = run_episode_ext(env, ev, pol, s, tag, preset)
                f.write(json.dumps({"map_seed": s, "reason": r["reason"], "success": r["success"], "decisions": pol.log}) + "\n")
    summ.update({"wall_seconds": round(wall, 3), "seconds_per_episode": round(wall / n_maps, 4), "consistency_problems": problems})
    (dest / f"{tag}.json").write_text(json.dumps(summ, indent=2, default=float))
    return {"tag": tag, "preset": preset, "status": "ok", "sr": summ["success_rate"], "stops": summ["reasons"].get("safe_stop", 0),
            "wall": wall, "spe": wall / n_maps, "problems": problems}
