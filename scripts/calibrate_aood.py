"""Amendment A3: fit the action-conditioned OOD detector (fit split, ID) and record its ID-validation scores.
Exactly the v1.1 calibration recipe (scripts/run_task4.py calibrate) with the detector swapped; no shifted data, no final data.

  python3 scripts/calibrate_aood.py --seeds 0-9 --jobs 8
Writes results/task4/calib/ens_s<k>/{aood.npz, aood_val_scores.npz} and results/task4/calib/aood_frozen.json.
"""
from _common import ROOT  # noqa: F401

import argparse
import hashlib
import json
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from pathlib import Path

import numpy as np

FIT_OFFSET, CONFIG = 30_000, "configs/sim32_id_ensemble.yaml"
OUT = ROOT / "results/task4"


def _plain(cfg, ens, ood):
    from src.evaluation.assurance_factory import build_assured
    acfg = replace(cfg.assurance, use_monitor=False, use_uncertainty=False, use_ood=False)
    return build_assured(cfg, ens, ood, np.inf, np.inf, keep_log=True, acfg=acfg)


def _one(task):
    k, n_fit, n_cal = task
    import torch
    torch.set_num_threads(1)
    from src.assurance.action_ood import ActionConditionedOOD
    from src.assurance.ood import MahalanobisOOD
    from src.config import load_config
    from src.evaluation.assurance_factory import build_ensemble
    from src.evaluation.evaluator import make_env
    from src.evaluation.harness import run_episode_ext
    from src.evaluation.reproducibility import SPLIT_OFFSET
    cfg = load_config(ROOT / CONFIG)
    ens = build_ensemble(cfg, lambda j: OUT / "train" / f"ens_s{k}" / f"m{j}" / "checkpoints" / "best_val.pt", k)
    env, ev = make_env(cfg.env, 0)
    # 1) fit data: plain-ensemble rollouts on ID fit maps -> (obs, proposed action)
    pol = _plain(cfg, ens, MahalanobisOOD().fit(np.random.default_rng(0).normal(size=(500, 59))))
    pol.attach(env.explored_map, env.max_battery)
    X, inner = [], pol.ens.q_matrix
    pol.ens.q_matrix = lambda o: (X.append(np.array(o, float)), inner(o))[1]
    for s in range(FIT_OFFSET, FIT_OFFSET + n_fit):
        run_episode_ext(env, ev, pol, s)
    pol.ens.q_matrix = inner                      # remove the spy (the ensemble object is shared with pol2)
    A = np.array([d["policy_action"] for d in pol.log])
    X = np.stack(X)
    assert len(X) == len(A)
    det = ActionConditionedOOD(shrinkage=cfg.assurance.ood_shrinkage).bind(ens).fit(X, A)
    # 2) windowed scores of the plain ensemble on ID VALIDATION maps
    pol2 = _plain(cfg, ens, det)
    pol2.attach(env.explored_map, env.max_battery)
    off = SPLIT_OFFSET["val"]
    for s in range(off, off + n_cal):
        run_episode_ext(env, ev, pol2, s)
    sc = np.array([d["ood"] for d in pol2.log])
    d = OUT / "calib" / f"ens_s{k}"
    det.save(d / "aood.npz")
    np.savez(d / "aood_val_scores.npz", ood=sc)
    return k, len(X), det.counts.tolist(), len(sc), float(np.percentile(sc, 95))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default="0-9")
    ap.add_argument("--fit-maps", type=int, default=200)
    ap.add_argument("--cal-maps", type=int, default=100)
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args()
    lo, _, hi = a.seeds.partition("-")
    seeds = list(range(int(lo), int(hi or lo) + 1))
    frozen = {}
    with ProcessPoolExecutor(a.jobs, mp_context=multiprocessing.get_context("spawn")) as ex:
        for k, nfit, counts, ncal, tau in ex.map(_one, [(k, a.fit_maps, a.cal_maps) for k in seeds]):
            print(f"  seed {k}: fit on {nfit} obs (per action {counts}), calibration {ncal} ID-val steps, tau@95 = {tau:.3f}")
            h = hashlib.sha256()
            for f in ("aood.npz", "aood_val_scores.npz"):
                h.update((OUT / "calib" / f"ens_s{k}" / f).read_bytes())
            frozen[str(k)] = {"sha256": h.hexdigest(), "fit_maps": a.fit_maps, "cal_maps": a.cal_maps}
    (OUT / "calib" / "aood_frozen.json").write_text(json.dumps(frozen, indent=2))


if __name__ == "__main__":
    main()
