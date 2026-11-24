# planetary-rover-marec — Phase 1 / Task 1 baseline

Audited, reproducible starting point for *Uncertainty-Gated Runtime Assurance for Learning-Based Planetary Rover Navigation* (MAREC).
Read **`docs/AUDIT_NOTES.md`** first, then **`docs/OBSERVATION_SCHEMA.md`**.

```
configs/      YAML: three reference configs (onboard, onboard+shaping, legacy17)
src/
  environment/  rover_env.py (policy-facing), terrain.py (pure helpers)
  evaluation/   evaluator.py (ONLY place that reads the hidden map), runner.py (metrics, Wilson CIs)
  agents/       dqn_agent.py, ppo_agent.py, replay_buffer.py   (see only observations)
  policies/     torch-free reference policies (random, onboard-greedy)
  training/     agent-agnostic training loops
  utils/        JSONL step logger, run metadata (git hash, versions, config)
scripts/      audit_legacy.py, run_reference.py, train_dqn.py, train_ppo.py
tests/        27 tests: accounting, seeding, leakage, legacy parity, loops, docs sync
legacy/       original project, byte-for-byte (also at git tag v0.0-original)
```

## Quick start
```
python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt   # or: make setup
make all-checks    # tests + legacy audit + torch-free reference run   (~30 s, no torch needed)
make smoke         # first thing to run on your machine: exercises the torch agents (~1 min)
make repro-check   # same seed twice => identical logs
make baselines     # full DQN/PPO runs, 1500 episodes, both reward variants
```
Recover the untouched original at any time: `git checkout v0.0-original`.

## Rules for later tasks
* Anything an agent, monitor or fallback planner uses must come from `obs`/`info` of `RoverEnv`. `tests/test_no_leakage.py` fails the build otherwise.
* Never pick thresholds/hyper-parameters on test seeds (20 000+); use validation seeds (10 000+).
* Success is `info["reason"] == "goal"`. Never infer it from reward.

## Phase 2 status (2026-11-24)
* Confirmatory campaign v1.1: `results/phase2/phase2/` (tables in `analysis/final/`), freeze tag `v5.1-freeze`.
* Amendment A1 (hypothesis H3, energy-blind fallback): pre-registration `protocol/amendment_A1_h3.json`, freeze tag
  `v6.1-freeze-A1`, run `results/phase2/h3/`, analysis `python3 scripts/analyse_h3.py`.
* Amendment A3 (action-conditioned OOD gate): pre-registration `protocol/amendment_A3_action_ood.json`, calibration
  `python3 scripts/calibrate_aood.py`, freeze tag `v6.2-freeze-A3`, run `results/phase2/a3/`, analysis `python3 scripts/analyse_a3.py`.
* Amendment A2 (real terrain): pre-registration `protocol/amendment_A2_real_terrain.json`; raw HiRISE DTMs in `data/hirise/`
  (git-ignored; hashes in `data/hirise_sha256.txt`), tiles `python3 scripts/build_real_maps.py` -> `data/real_tiles/`,
  freeze tag `v6.3-freeze-A2`, run `results/phase2/a2/`, analysis `python3 scripts/analyse_a2.py`.
* Amendment A4 (real terrain + shifted physics): `protocol/amendment_A4_real_shift.json`, configs `configs/sim32_real_*.yaml`,
  freeze tag `v6.4-freeze-A4`, run `results/phase2/a4/`, analysis `python3 scripts/analyse_a4.py`.
* Literature check: `docs/RELATED_WORK.md`. Planned real-terrain extension: `docs/REAL_TERRAIN_EXTENSION.md`.
* Figures: `python3 scripts/make_figures.py` → `paper/figures/`. Manuscript (IEEEtran): `paper/main.tex` + `paper/references.bib`.
