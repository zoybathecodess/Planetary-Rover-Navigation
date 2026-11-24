"""Unified experiment runner (Task 5): every method x preset x system seed through ONE code path, with a manifest per run.

  python3 scripts/run_experiment.py pilot                              # small debugging run (never a paper result)
  python3 scripts/run_experiment.py run --name phase2 --split final --seeds 0-9 --n-maps 500
  python3 scripts/run_experiment.py validate --run results/phase2/phase2 --split final
Method specs: see src/evaluation/experiment.py (e.g. assured-no_ood@95). Held-out splits are logged in results/test_access.jsonl;
the confirmatory 'final' split refuses to run unless `python3 scripts/freeze.py verify` is clean.
"""
from _common import ROOT  # noqa: F401

import argparse
import csv
import json
import multiprocessing
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

PILOT_METHODS = "astar,reactive,dqn,dqn_shield,ppo,ppo_shield,ens,assured,assured-monitor_only,assured-unc_only,assured-ood_only"
# full campaign = every method named in protocol/analysis_plan.json
DEFAULT_METHODS = ("astar,astar_monitor,reactive,dqn,dqn_shield,ppo,ppo_shield,ens,assured,assured@90,assured@99,assured-monitor_only,assured-unc_only,"
                   "assured-ood_only,assured-no_ood,assured-no_unc,assured-no_monitor,assured-no_stop")


def parse_seeds(s):
    out = []
    for part in s.split(","):
        a, _, b = part.partition("-")
        out += list(range(int(a), int(b) + 1)) if b else [int(a)]
    return out


def _tasks(a, out):
    from src.evaluation.experiment import SEEDLESS, parse_method
    tasks = []
    for preset in a.presets.split(","):
        for spec in a.methods.split(","):
            kind = parse_method(spec)["kind"]
            for k in ([0] if kind in SEEDLESS else parse_seeds(a.seeds)):
                tasks.append({"root": str(ROOT), "out": str(out), "spec": spec, "seed": k, "preset": preset, "split": a.split,
                              "n_maps": a.n_maps, "ckpt": a.ckpt, "log_maps": a.log_maps if spec == "assured" else 0})
    return tasks


def cmd_run(a, pilot=False):
    from src.evaluation.experiment import run_cell
    from src.evaluation.reproducibility import artefact_hashes, claim_split, run_manifest, write_manifest
    claim_split(ROOT, a.split, f"run_experiment {'pilot' if pilot else a.name}", allow_unfrozen=a.allow_unfrozen)
    out = ROOT / a.out / a.name
    tasks = _tasks(a, out)
    cfgs = sorted(str(p.relative_to(ROOT)) for p in (ROOT / "configs").glob("*.yaml"))
    man = run_manifest(ROOT, kind="pilot" if pilot else "experiment", configs=cfgs, seeds=a.seeds,
                       extra={"methods": a.methods.split(","), "presets": a.presets.split(","), "split": a.split, "n_maps": a.n_maps,
                              "ckpt": a.ckpt, "map_seeds": [SPLIT_OFFSET_[a.split], SPLIT_OFFSET_[a.split] + a.n_maps - 1]},
                       artefacts=artefact_hashes(ROOT))
    write_manifest(out, man)
    print(f"{len(tasks)} cells -> {out}  (split={a.split}, {a.n_maps} maps, jobs={a.jobs})")
    t0, results = time.time(), []
    with ProcessPoolExecutor(a.jobs, mp_context=multiprocessing.get_context("spawn")) as ex:
        for r in ex.map(run_cell, tasks):
            results.append(r)
            if r["status"] == "ok":
                flag = "" if not r["problems"] else f"  !! {len(r['problems'])} consistency problem(s)"
                print(f"  {r['preset']:15} {r['tag']:30} SR {r['sr']:.2f}  stops {r['stops']:3}  {r['spe']:.2f} s/ep{flag}")
            else:
                print(f"  {r['preset']:15} {r['tag']:30} SKIPPED (missing {r['detail']})")
    (out / "cells.json").write_text(json.dumps(results, indent=2, default=float))
    problems = [p for r in results if r["status"] == "ok" for p in r["problems"]]
    pair = _pairing(out, a.split)
    print(f"\nwall {time.time() - t0:.0f}s   cells ok {sum(r['status'] == 'ok' for r in results)}/{len(results)}   "
          f"consistency problems {len(problems)}   pairing problems {len(pair)}")
    for p in (problems + pair)[:20]:
        print("   ", p)
    if pilot:
        _runtime_estimate(results, a)


def _pairing(out, split):
    from src.evaluation.experiment import check_pairing
    bad = []
    for pdir in sorted((out / split).glob("*")):
        by = {f.stem: list(csv.DictReader(open(f))) for f in sorted(pdir.glob("*.csv"))}
        bad += [f"{pdir.name}: {p}" for p in check_pairing(by)]
    return bad


def _runtime_estimate(results, a, campaign_maps=500, campaign_seeds=10):
    from src.evaluation.experiment import SEEDLESS
    spe = {}
    for r in results:
        if r["status"] == "ok":
            spe.setdefault(r["tag"].rsplit("_s", 1)[0] if r["tag"] not in SEEDLESS else r["tag"], []).append(r["spe"])
    n_presets = 5      # a full campaign always covers all five presets
    total = 0.0
    print("\nruntime estimate for a full campaign (%d maps x %d seeds x %d presets), single core:" % (campaign_maps, campaign_seeds, n_presets))
    for tag, v in sorted(spe.items()):
        seeds = 1 if tag in SEEDLESS else campaign_seeds
        t = sum(v) / len(v) * campaign_maps * seeds * n_presets
        total += t
        print(f"  {tag:28} {sum(v) / len(v):6.2f} s/episode  -> {t / 3600:6.2f} core-hours")
    print(f"  TOTAL {total / 3600:.1f} core-hours  (~{total / 3600 / max(a.jobs, 1):.1f} h wall on {a.jobs} jobs)")


def cmd_validate(a):
    from src.evaluation.experiment import check_pairing, validate_rows
    base = ROOT / a.run / a.split
    n_bad = 0
    for pdir in sorted(base.glob("*")):
        by = {f.stem: list(csv.DictReader(open(f))) for f in sorted(pdir.glob("*.csv"))}
        for name, rows in by.items():
            for p in validate_rows(rows):
                n_bad += 1; print(pdir.name, name, p)
        for p in check_pairing(by):
            n_bad += 1; print(pdir.name, p)
    print("validation:", "CLEAN" if not n_bad else f"{n_bad} problem(s)")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("run", "pilot"):
        p = sub.add_parser(name)
        p.add_argument("--name", default="pilot" if name == "pilot" else "run")
        p.add_argument("--out", default="results/phase2" if name == "run" else "results/pilot")
        p.add_argument("--split", default="pilot" if name == "pilot" else "final")
        p.add_argument("--methods", default=PILOT_METHODS if name == "pilot" else DEFAULT_METHODS)
        p.add_argument("--presets", default="id,terrain_shift,sensor_shift,dynamics_shift,combined_shift")
        p.add_argument("--seeds", default="0-1" if name == "pilot" else "0-9")
        p.add_argument("--n-maps", type=int, default=10 if name == "pilot" else 500)
        p.add_argument("--ckpt", default="best_val")
        p.add_argument("--jobs", type=int, default=2)
        p.add_argument("--log-maps", type=int, default=5)
        p.add_argument("--allow-unfrozen", action="store_true", help="debugging only; the final split ignores a failed freeze check otherwise")
    v = sub.add_parser("validate")
    v.add_argument("--run", required=True)
    v.add_argument("--split", default="final")
    a = ap.parse_args()
    if a.cmd == "pilot":
        if a.split in ("test", "final"):
            raise SystemExit("pilot runs must not use a held-out split")
        cmd_run(a, pilot=True)
    elif a.cmd == "run":
        cmd_run(a)
    else:
        cmd_validate(a)


from src.evaluation.reproducibility import SPLIT_OFFSET as SPLIT_OFFSET_  # noqa: E402

if __name__ == "__main__":
    main()
