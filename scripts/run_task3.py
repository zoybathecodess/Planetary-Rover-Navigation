"""Task 3 pipeline: train DQN on 10 seeds, evaluate every baseline through ONE harness, report mean +/- CI over seeds.

  python scripts/run_task3.py train  --jobs 4                      # DQN seeds 0-9 (skips finished runs; --force to redo)
  python scripts/run_task3.py eval   --split val  --jobs 4         # choose nothing on test; look at val first
  python scripts/run_task3.py eval   --split test --jobs 4 --presets id
  python scripts/run_task3.py report --split test
  python scripts/run_task3.py curves                               # training stability across seeds (gate for adding PPO)
  python scripts/run_task3.py train --algo ppo --jobs 4            # PPO seeds 0-9 (uses configs/sim32_id_ppo.yaml)
  python scripts/run_task3.py curves --algo ppo
Training uses the in-distribution config only. Checkpoints: best_val.pt (best greedy SR on validation maps during
training; validation maps only) and final.pt. Evaluation maps: val = seeds 10000+, test = 20000+ (never trained on).
"""
from _common import ROOT  # noqa: F401

import argparse
import csv
import json
import math
import multiprocessing
import platform
import re
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from pathlib import Path

import numpy as np

T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228, 11: 2.201,
        12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131, 16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086, 21: 2.080,
        22: 2.074, 23: 2.069, 24: 2.064, 25: 2.060, 26: 2.056, 27: 2.052, 28: 2.048, 29: 2.045, 30: 2.042}
SEEDED = ("dqn", "dqn_shield", "ppo", "ppo_shield")  # trained per seed
SEEDLESS = ("astar", "reactive")        # no training: one deterministic evaluation
ALL_METHODS = ("astar", "reactive", "dqn", "dqn_shield", "ppo", "ppo_shield")


def parse_seeds(s: str) -> list[int]:
    out = []
    for part in s.split(","):
        a, _, b = part.partition("-")
        out += list(range(int(a), int(b) + 1)) if b else [int(a)]
    return out


def run_dir(out: Path, seed: int, algo: str = "dqn") -> Path:
    return out / "train" / f"{algo}_s{seed}"


# ------------------------------------------------------------------ train
def _train_one(args):
    cfg, seed, out, force, algo = args
    d = run_dir(out, seed, algo)
    if (d / "summary.json").exists() and not force:
        return seed, "skipped (done)", 0.0
    t0 = time.time()
    env = {**__import__("os").environ, "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}
    r = subprocess.run([sys.executable, str(ROOT / f"scripts/train_{algo}.py"), "--config", cfg, "--seed", str(seed), "--out", str(d)],
                       capture_output=True, text=True, env=env)
    return seed, (r.stdout.strip().splitlines() or [""])[-1] if r.returncode == 0 else f"FAILED: {r.stderr[-400:]}", time.time() - t0


def cmd_train(a):
    out = ROOT / a.out
    out.mkdir(parents=True, exist_ok=True)
    seeds = parse_seeds(a.seeds)
    try:
        import torch
        commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip()
        manifest = {"seeds": seeds, "config": a.config, "git_commit": commit, "python": platform.python_version(),
                    "torch": torch.__version__, "numpy": np.__version__, "platform": platform.platform(),
                    "started": time.strftime("%Y-%m-%d %H:%M:%S")}
        (out / f"manifest_{a.algo}.json").write_text(json.dumps(manifest, indent=2))
    except Exception as e:  # manifest is best-effort
        print("manifest skipped:", e)
    print(f"training {a.algo.upper()} seeds {seeds} with {a.jobs} parallel job(s), config {a.config}")
    with ThreadPoolExecutor(a.jobs) as ex:
        for seed, msg, dt in ex.map(_train_one, [(a.config, s, out, a.force, a.algo) for s in seeds]):
            print(f"  seed {seed}: {msg}  ({dt / 60:.1f} min)")


# ------------------------------------------------------------------ eval
def _eval_one(task):
    kind, seed, ckpt_name, preset, split, n_maps, out, cfg_train = task
    import torch
    torch.set_num_threads(1)
    from src.config import load_config
    from src.evaluation.harness import SPLIT_OFFSET, build_policy, evaluate_method
    out = Path(out)
    cfg = load_config(ROOT / cfg_train)
    tag = kind if kind in SEEDLESS else f"{kind}_s{seed}"
    dest = out / "eval" / split / preset
    ckpt = None if kind in SEEDLESS else str(run_dir(out, seed, kind.split("_")[0]) / "checkpoints" / f"{ckpt_name}.pt")
    if ckpt and not Path(ckpt).exists():
        return tag, preset, "missing checkpoint " + ckpt
    pol = build_policy(kind, cfg, ckpt, seed=seed)
    off = SPLIT_OFFSET[split]
    _, summ = evaluate_method(pol, ROOT / f"configs/sim32_{preset}.yaml", range(off, off + n_maps), tag, preset, dest / f"{tag}.csv")
    (dest / f"{tag}.json").write_text(json.dumps(summ, indent=2, default=float))
    return tag, preset, f"SR {summ['success_rate']:.2f}"


def cmd_eval(a):
    from src.evaluation.reproducibility import claim_split
    claim_split(ROOT, a.split, "run_task3 eval")
    out = ROOT / a.out
    seeds, presets = parse_seeds(a.seeds), a.presets.split(",")
    tasks = []
    for p in presets:
        for kind in a.methods.split(","):
            for s in ([0] if kind in SEEDLESS else seeds):
                tasks.append((kind, s, a.ckpt, p, a.split, a.n_maps, str(out), a.config))
    print(f"{len(tasks)} evaluation tasks ({a.split} maps x {a.n_maps}, presets {presets}, ckpt={a.ckpt})")
    with ProcessPoolExecutor(a.jobs, mp_context=multiprocessing.get_context("spawn")) as ex:
        for tag, preset, msg in ex.map(_eval_one, tasks):
            print(f"  {preset:15} {tag:14} {msg}")


# ------------------------------------------------------------------ report
def wilson(k, n, z=1.96):
    if n == 0:
        return float("nan"), float("nan")
    p, d = k / n, 1 + z * z / n
    c, h = (p + z * z / (2 * n)) / d, z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def _load(path):
    with open(path) as f:
        return list(csv.DictReader(f))


def _mean_of(rows, key, only_success=False):
    v = [float(r[key]) for r in rows if (not only_success or r["success"] == "1") and r[key] not in ("", "nan")]
    return float(np.mean(v)) if v else float("nan")


def cmd_report(a):
    out = ROOT / a.out
    if not (out / "eval" / a.split).exists():
        print(f"no {a.split} evaluation results under {out / 'eval'} yet: run `eval --split {a.split}` after `train` finishes")
        return
    lines, csv_rows = [], []
    for preset_dir in sorted((out / "eval" / a.split).glob("*")):
        preset = preset_dir.name
        lines += [f"\n### {preset} — {a.split} maps\n", "| Method | Success rate | 95% CI | n | Collisions/ep | Unsafe attempts/ep | Energy / optimal | Battery left (success) | Steps | Intervention rate |",
                  "|---|---|---|---|---|---|---|---|---|---|"]
        for kind in ALL_METHODS:
            pat = re.compile(rf"{kind}\.csv" if kind in SEEDLESS else rf"{kind}_s\d+\.csv")  # exact: dqn_s* must not match dqn_shield_s*
            files = sorted(f for f in preset_dir.glob("*.csv") if pat.fullmatch(f.name))
            if not files:
                continue
            per_seed = [_load(f) for f in files]
            allr = [r for rows in per_seed for r in rows]
            srs = np.array([np.mean([int(r["success"]) for r in rows]) for rows in per_seed])
            if kind in SEEDLESS:
                k, n = int(sum(int(r["success"]) for r in allr)), len(allr)
                lo, hi = wilson(k, n)
                sr_txt, ci_txt, n_txt = f"{k / n:.3f}", f"[{lo:.3f}, {hi:.3f}] (Wilson over maps)", f"{n} maps"
            else:
                m, sd = srs.mean(), srs.std(ddof=1) if len(srs) > 1 else float("nan")
                h = T975.get(len(srs) - 1, 1.96) * sd / math.sqrt(len(srs)) if len(srs) > 1 else float("nan")
                lo_, hi_ = max(0.0, m - h), min(1.0, m + h)  # clipped to [0,1]
                sr_txt, ci_txt, n_txt = f"{m:.3f} ± {sd:.3f}", f"[{lo_:.3f}, {hi_:.3f}] (t over {len(srs)} seeds)", f"{len(srs)}x{len(per_seed[0])}"
            dec = sum(int(r["decisions"]) for r in allr)
            interv = f"{sum(int(r['interventions']) for r in allr) / dec:.3f}" if kind.endswith("_shield") and dec else "—"
            row = [kind, sr_txt, ci_txt, n_txt, f"{_mean_of(allr, 'collisions'):.2f}", f"{_mean_of(allr, 'attempted_unsafe'):.2f}",
                   f"{_mean_of(allr, 'energy_ratio', True):.2f}", f"{_mean_of(allr, 'battery_left', True):.0f}", f"{_mean_of(allr, 'steps'):.0f}", interv]
            lines.append("| " + " | ".join(row) + " |")
            csv_rows.append([preset, a.split] + row)
            if kind in SEEDED:
                lines.append(f"|   per-seed SR | {', '.join(f'{x:.2f}' for x in srs)} | | | | | | | | |")
    text = "\n".join(lines)
    print(text)
    (out / f"report_{a.split}.md").write_text(text + "\n")
    with open(out / f"summary_{a.split}.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["preset", "split", "method", "success_rate", "ci95", "n", "collisions_per_ep", "unsafe_per_ep",
                    "energy_ratio", "battery_left_success", "steps", "intervention_rate"])
        w.writerows(csv_rows)


def cmd_curves(a):
    """Greedy validation success during training, per checkpoint episode, across seeds (stability check)."""
    out = ROOT / a.out
    runs = {s: _load(run_dir(out, s, a.algo) / "eval_greedy_val.csv") for s in parse_seeds(a.seeds)
            if (run_dir(out, s, a.algo) / "eval_greedy_val.csv").exists()}
    if not runs:
        print("no training runs found")
        return
    eps = sorted({int(r["episode"]) for rows in runs.values() for r in rows})
    lines = [f"{a.algo.upper()}: greedy validation success during training ({len(runs)} seeds; each point = {a.n_maps_curve} maps)\n",
             "| episode | mean | sd | min | max | seeds below 0.5 |", "|---|---|---|---|---|---|"]
    csv_rows = []
    for e in eps:
        v = np.array([float(r["success_rate"]) for rows in runs.values() for r in rows if int(r["episode"]) == e])
        sd = v.std(ddof=1) if len(v) > 1 else float("nan")
        lines.append(f"| {e} | {v.mean():.2f} | {sd:.2f} | {v.min():.2f} | {v.max():.2f} | {int((v < 0.5).sum())}/{len(v)} |")
        csv_rows.append([e, v.mean(), sd, v.min(), v.max(), int((v < 0.5).sum()), len(v)])
    final = np.array([float(rows[-1]["success_rate"]) for rows in runs.values()])
    lines.append(f"\nLast checkpoint: mean {final.mean():.2f}, min {final.min():.2f} over {len(final)} seeds. "
                 f"STABILITY GATE for adding PPO: mean >= 0.80 and min >= 0.60 -> {'PASS' if final.mean() >= 0.8 and final.min() >= 0.6 else 'NOT YET'}")
    print("\n".join(lines))
    (out / f"learning_curve_val_{a.algo}.md").write_text("\n".join(lines) + "\n")
    with open(out / "learning_curve_val.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["episode", "mean", "sd", "min", "max", "n_below_0.5", "n_seeds"])
        w.writerows(csv_rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["train", "eval", "report", "curves"])
    ap.add_argument("--config", default="configs/sim32_id.yaml", help="TRAINING config (in-distribution)")
    ap.add_argument("--seeds", default="0-9")
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--out", default="results/task3")
    ap.add_argument("--split", choices=["val", "test"], default="val")
    ap.add_argument("--presets", default="id")
    ap.add_argument("--methods", default=",".join(ALL_METHODS))
    ap.add_argument("--n-maps", type=int, default=200)
    ap.add_argument("--ckpt", choices=["best_val", "final"], default="best_val", help="best_val = best greedy SR on VALIDATION maps during training")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--algo", choices=["dqn", "ppo"], default="dqn", help="train/curves: which learner")
    ap.add_argument("--n-maps-curve", type=int, default=50, help="validation maps per curve point (= run.eval_episodes)")
    args = ap.parse_args()
    if args.algo == "ppo" and args.config == "configs/sim32_id.yaml":
        args.config = "configs/sim32_id_ppo.yaml"  # same env, plus the PPO settings chosen on validation maps
    {"train": cmd_train, "eval": cmd_eval, "report": cmd_report, "curves": cmd_curves}[args.cmd](args)


if __name__ == "__main__":  # required: worker processes re-import this file (macOS/Windows spawn)
    main()
