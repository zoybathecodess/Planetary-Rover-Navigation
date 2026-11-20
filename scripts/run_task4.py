"""Task 4 pipeline: ensembles -> OOD fit + threshold calibration (in-distribution validation only) -> evaluation -> report.

  python scripts/run_task4.py train     --jobs 4                  # 10 system seeds x 5 members (skips finished; --force)
  python scripts/run_task4.py calibrate                           # fit Mahalanobis, freeze thresholds (ID validation only)
  python scripts/run_task4.py eval --split val  --jobs 4          # look at validation first
  python scripts/run_task4.py eval --split test --jobs 4          # once, after the design is frozen
  python scripts/run_task4.py report --split test
Information boundary: fit/calibration/evaluation use only observations + the env's public explored map. Evaluation scoring
(ground truth) lives in src/evaluation/*. Fit maps are seeds 30000+ (training generator), calibration maps are the
ID VALIDATION maps (10000+), evaluation maps are val (10000+) / test (20000+). Shifted data is never used for calibration.
"""
from _common import ROOT  # noqa: F401

import argparse
import csv
import hashlib
import json
import math
import multiprocessing
import re
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from pathlib import Path

import numpy as np

FIT_OFFSET = 30_000
CONFIG = "configs/sim32_id_ensemble.yaml"


def parse_seeds(s):
    out = []
    for part in s.split(","):
        a, _, b = part.partition("-")
        out += list(range(int(a), int(b) + 1)) if b else [int(a)]
    return out


def member_dir(out, k, j):
    return out / "train" / f"ens_s{k}" / f"m{j}"


def ckpt_path(out, k, j, name="best_val"):
    return member_dir(out, k, j) / "checkpoints" / f"{name}.pt"


# ------------------------------------------------------------------ train
def _train_member(args):
    cfg, k, j, out, force = args
    from src.evaluation.assurance_factory import member_seed
    d = member_dir(out, k, j)
    if (d / "summary.json").exists() and not force:
        return k, j, "skipped (done)", 0.0
    t0 = time.time()
    import os
    env = {**os.environ, "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}
    r = subprocess.run([sys.executable, str(ROOT / "scripts/train_member.py"), "--config", cfg, "--seed", str(member_seed(k, j)),
                        "--out", str(d)], capture_output=True, text=True, env=env)
    return k, j, (r.stdout.strip().splitlines() or [""])[-1] if r.returncode == 0 else f"FAILED: {r.stderr[-400:]}", time.time() - t0


def cmd_train(a):
    out = ROOT / a.out
    out.mkdir(parents=True, exist_ok=True)
    from src.config import load_config
    nm = load_config(ROOT / a.config).assurance.n_members
    tasks = [(a.config, k, j, out, a.force) for k in parse_seeds(a.seeds) for j in range(nm)]
    print(f"training {len(tasks)} ensemble members with {a.jobs} job(s), config {a.config}")
    with ThreadPoolExecutor(a.jobs) as ex:
        for k, j, msg, dt in ex.map(_train_member, tasks):
            print(f"  system seed {k} member {j}: {msg}  ({dt / 60:.1f} min)")


# ------------------------------------------------------------------ calibrate
def _load_system(cfg, out, k, name="best_val"):
    from src.evaluation.assurance_factory import build_ensemble
    return build_ensemble(cfg, lambda j: ckpt_path(out, k, j, name), k)


def _rollout_logs(cfg, ens, ood, seeds, keep_obs=False):
    """Run the PLAIN ensemble (no gates/monitor/fallback) on the seeds; return per-step (unc, windowed score[, obs])."""
    from dataclasses import replace
    from src.evaluation.assurance_factory import build_assured
    from src.evaluation.evaluator import make_env
    from src.evaluation.harness import run_episode_ext
    env, ev = make_env(cfg.env, 0)
    acfg = replace(cfg.assurance, use_monitor=False, use_uncertainty=False, use_ood=False)
    pol = build_assured(cfg, ens, ood, np.inf, np.inf, keep_log=True, acfg=acfg)
    pol.attach(env.explored_map, env.max_battery)
    obs_all = []
    if keep_obs:
        inner = pol.ens.q_matrix

        def spy(o):
            obs_all.append(np.array(o, dtype=float))
            return inner(o)
        pol.ens.q_matrix = spy
    for s in seeds:
        run_episode_ext(env, ev, pol, s)
    unc = np.array([d["unc"] for d in pol.log]); sc = np.array([d["ood"] for d in pol.log])
    return unc, sc, (np.stack(obs_all) if keep_obs else None)


def _calibrate_one(task):
    k, out, n_fit, n_cal, name = task
    import torch
    torch.set_num_threads(1)
    from src.assurance.ood import MahalanobisOOD
    from src.config import load_config
    from src.evaluation.harness import SPLIT_OFFSET
    cfg = load_config(ROOT / CONFIG)
    out = Path(out)
    ens = _load_system(cfg, out, k, name)
    # 1) fit the OOD detector on fresh ID maps from the training generator (ensemble's own trajectories)
    _, _, X = _rollout_logs(cfg, ens, MahalanobisOOD().fit(np.random.default_rng(0).normal(size=(500, 59))), range(FIT_OFFSET, FIT_OFFSET + n_fit), keep_obs=True)
    ood = MahalanobisOOD(shrinkage=cfg.assurance.ood_shrinkage).fit(X)
    # 2) per-step scores on ID VALIDATION maps -> percentile thresholds
    off = SPLIT_OFFSET["val"]
    unc, sc, _ = _rollout_logs(cfg, ens, ood, range(off, off + n_cal))
    d = out / "calib" / f"ens_s{k}"
    d.mkdir(parents=True, exist_ok=True)
    ood.save(d / "ood.npz")
    np.savez(d / "id_val_scores.npz", unc=unc, ood=sc)
    return k, len(X), len(unc), float(np.percentile(unc, 95)), float(np.percentile(sc, 99))


def thresholds(out, k, unc_pct, ood_pct):
    z = np.load(out / "calib" / f"ens_s{k}" / "id_val_scores.npz")
    return float(np.percentile(z["unc"], unc_pct)), float(np.percentile(z["ood"], ood_pct))


def cmd_calibrate(a):
    out = ROOT / a.out
    tasks = [(k, str(out), a.fit_maps, a.cal_maps, a.ckpt) for k in parse_seeds(a.seeds)]
    frozen = {}
    with ProcessPoolExecutor(a.jobs, mp_context=multiprocessing.get_context("spawn")) as ex:
        for k, nfit, ncal, tu, to in ex.map(_calibrate_one, tasks):
            print(f"  system seed {k}: OOD fit on {nfit} obs, calibration on {ncal} ID-val steps  "
                  f"tau_unc(p95)={tu:.4f} tau_ood(p99)={to:.3f}")
    for k in parse_seeds(a.seeds):
        h = hashlib.sha256()
        for f in ("ood.npz", "id_val_scores.npz"):
            h.update((out / "calib" / f"ens_s{k}" / f).read_bytes())
        frozen[str(k)] = {"sha256": h.hexdigest(), "fit_maps": a.fit_maps, "cal_maps": a.cal_maps, "ckpt": a.ckpt}
    (out / "calib" / "frozen.json").write_text(json.dumps(frozen, indent=2))
    print("calibration artefacts written + hashed ->", out / "calib" / "frozen.json")


# ------------------------------------------------------------------ eval
def _eval_one(task):
    kind, k, pct, preset, split, n_maps, out, ckpt_name, log_maps = task
    import torch
    torch.set_num_threads(1)
    from src.evaluation.assurance_factory import build_assured
    from src.assurance.ood import MahalanobisOOD
    from src.config import load_config
    from src.evaluation.harness import SPLIT_OFFSET, evaluate_method
    cfg = load_config(ROOT / CONFIG)
    out = Path(out)
    ens = _load_system(cfg, out, k, ckpt_name)
    tag = f"{kind}_p{int(pct)}_s{k}" if kind == "assured" else f"{kind}_s{k}"
    if kind == "ens":
        from dataclasses import replace
        pol = build_assured(cfg, ens, MahalanobisOOD().fit(np.random.default_rng(0).normal(size=(500, 59))), np.inf, np.inf,
                            acfg=replace(cfg.assurance, use_monitor=False, use_uncertainty=False, use_ood=False))
        pol.name = "ens"
    else:
        ood = MahalanobisOOD.load(out / "calib" / f"ens_s{k}" / "ood.npz")
        tu, to = thresholds(out, k, pct, pct)
        pol = build_assured(cfg, ens, ood, tu, to, keep_log=log_maps > 0, seed=k)
    dest = out / "eval" / split / preset
    off = SPLIT_OFFSET[split]
    cfg_path = ROOT / f"configs/sim32_{preset}.yaml"
    seeds = list(range(off, off + n_maps))
    rows, summ = evaluate_method(pol, cfg_path, seeds, tag, preset, dest / f"{tag}.csv")
    if kind == "assured" and log_maps:
        # intervention logs for the first maps: re-run those episodes with logging on (same seeds -> same episodes)
        import json as _j
        from src.evaluation.evaluator import make_env
        from src.evaluation.harness import run_episode_ext
        env, ev = make_env(load_config(cfg_path).env, 0)
        pol.attach(env.explored_map, env.max_battery)
        (dest / "logs").mkdir(parents=True, exist_ok=True)
        with open(dest / "logs" / f"{tag}.jsonl", "w") as f:
            for s in seeds[:log_maps]:
                pol.log.clear()
                r = run_episode_ext(env, ev, pol, s, tag, preset)
                f.write(_j.dumps({"map_seed": s, "reason": r["reason"], "success": r["success"], "decisions": pol.log}) + "\n")
    (dest / f"{tag}.json").write_text(json.dumps(summ, indent=2, default=float))
    return tag, preset, f"SR {summ['success_rate']:.2f}  stops {summ['reasons'].get('safe_stop', 0)}"


def cmd_eval(a):
    out = ROOT / a.out
    seeds, presets = parse_seeds(a.seeds), a.presets.split(",")
    pcts = [float(p) for p in a.pcts.split(",")]
    tasks = []
    for p in presets:
        for k in seeds:
            tasks.append(("ens", k, 0, p, a.split, a.n_maps, str(out), a.ckpt, 0))
            tasks += [("assured", k, pc, p, a.split, a.n_maps, str(out), a.ckpt, a.log_maps if pc == pcts[0] else 0) for pc in pcts]
    print(f"{len(tasks)} evaluation tasks ({a.split} x {a.n_maps} maps, presets {presets}, percentiles {pcts})")
    with ProcessPoolExecutor(a.jobs, mp_context=multiprocessing.get_context("spawn")) as ex:
        for tag, preset, msg in ex.map(_eval_one, tasks):
            print(f"  {preset:15} {tag:20} {msg}")


# ------------------------------------------------------------------ report
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228}


def _rows(path):
    with open(path) as f:
        return list(csv.DictReader(f))


def _stat(vals):
    v = [x for x in vals if not math.isnan(x)]
    if not v:
        return "—"
    m = float(np.mean(v))
    if len(v) < 2:
        return f"{m:.3f}"
    return f"{m:.3f} ± {T975.get(len(v) - 1, 1.96) * float(np.std(v, ddof=1)) / math.sqrt(len(v)):.3f}"


def _per_seed(files):
    out = {"sr": [], "col": [], "unsafe": [], "stop": [], "interv": [], "fb": [], "energy": [], "unc": [], "ood": []}
    for f in files:
        r = _rows(f)
        n = len(r)
        dec = sum(float(x["decisions"]) for x in r) or float("nan")
        out["sr"].append(sum(int(x["success"]) for x in r) / n)
        out["col"].append(np.mean([float(x["collisions"]) for x in r]))
        out["unsafe"].append(np.mean([float(x["attempted_unsafe"]) for x in r]))
        out["stop"].append(sum(x["reason"] == "safe_stop" for x in r) / n)
        out["interv"].append(sum(float(x["interventions"]) for x in r) / dec)
        out["fb"].append(sum(float(x["fallback_steps"]) for x in r) / dec)
        out["unc"].append(sum(float(x["unc_alarms"]) for x in r) / dec)
        out["ood"].append(sum(float(x["ood_alarms"]) for x in r) / dec)
        e = [float(x["energy_ratio"]) for x in r if x["success"] == "1" and x["energy_ratio"] not in ("", "nan")]
        out["energy"].append(float(np.mean(e)) if e else float("nan"))
    return out


def cmd_report(a):
    out = ROOT / a.out
    base = out / "eval" / a.split
    if not base.exists():
        print(f"no {a.split} results under {base}: run `eval --split {a.split}` first")
        return
    for pdir in sorted(base.glob("*")):
        lines = [f"\n### {pdir.name} — {a.split} maps (mean ± 95% CI over system seeds)\n",
                 "| Method | n seeds | Success | Collisions/ep | Unsafe attempts/ep | Safe-stop rate | Intervention rate | Fallback rate | Unc. alarms | OOD alarms | Energy/optimal |",
                 "|---|---|---|---|---|---|---|---|---|---|---|"]
        kinds = ["ens"] + sorted({re.sub(r"_s\d+\.csv$", "", f.name) for f in pdir.glob("assured_p*_s*.csv")},
                                 key=lambda s: int(re.search(r"p(\d+)", s).group(1)))
        for kind in kinds:
            files = sorted(f for f in pdir.glob("*.csv") if re.fullmatch(rf"{kind}_s\d+\.csv", f.name))
            if not files:
                continue
            s = _per_seed(files)
            label = "ensemble (no assurance)" if kind == "ens" else f"assured (percentile {kind.split('_p')[1]})"
            lines.append(f"| {label} | {len(files)} | {_stat(s['sr'])} | {_stat(s['col'])} | {_stat(s['unsafe'])} | {_stat(s['stop'])} | "
                         f"{_stat(s['interv'])} | {_stat(s['fb'])} | {_stat(s['unc'])} | {_stat(s['ood'])} | {_stat(s['energy'])} |")
        print("\n".join(lines))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("train", "calibrate", "eval", "report"):
        p = sub.add_parser(name)
        p.add_argument("--out", default="results/task4")
        p.add_argument("--seeds", default="0-9")
        p.add_argument("--jobs", type=int, default=2)
        if name == "train":
            p.add_argument("--config", default=CONFIG)
            p.add_argument("--force", action="store_true")
        if name == "calibrate":
            p.add_argument("--fit-maps", type=int, default=200)
            p.add_argument("--cal-maps", type=int, default=100)
            p.add_argument("--ckpt", default="best_val")
        if name == "eval":
            p.add_argument("--split", choices=("val", "test"), default="val")
            p.add_argument("--presets", default="id,terrain_shift,sensor_shift,dynamics_shift,combined_shift")
            p.add_argument("--n-maps", type=int, default=100)
            p.add_argument("--pcts", default="95,99,90")
            p.add_argument("--ckpt", default="best_val")
            p.add_argument("--log-maps", type=int, default=5)
        if name == "report":
            p.add_argument("--split", choices=("val", "test"), default="test")
    a = ap.parse_args()
    {"train": cmd_train, "calibrate": cmd_calibrate, "eval": cmd_eval, "report": cmd_report}[a.cmd](a)


if __name__ == "__main__":
    main()
