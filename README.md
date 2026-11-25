# planetary-rover-marec

Code for *Uncertainty-Gated Runtime Assurance for Learning-Based Planetary Rover Navigation* (MAREC).

## Status

| Task | What | Status | Read |
|---|---|---|---|
| 1 | Audit of the original 10×10 DQN/PPO project; leak-free onboard observations, seeding, val/test split, tests | Done | `docs/AUDIT_NOTES.md`, `docs/OBSERVATION_SCHEMA.md` |
| 2 | 32×32 partially observable simulator (5×5 noisy sensor, slip, explored map, shift presets) | Done | `docs/OBSERVATION_SCHEMA_V2.md` |
| 3 | Baselines over 10 seeds: battery-aware A*, reactive, DQN, PPO, and DQN/PPO behind a rule shield | Done | `docs/TASK3_BASELINES.md`, `results/task3/report_test.md` |
| 4 | Uncertainty / OOD monitor | Next | |
| 7 | Evaluation under terrain, sensor and dynamics shift | Planned (harness already supports the presets) | |

## Layout

```
configs/        YAML configs: 10x10 baselines, legacy17 reproduction, sim32 presets (id + shifts), PPO entropy sweep
src/
  environment/  rover_env.py (10x10), advanced_env.py + procgen.py (32x32), terrain.py
  evaluation/   evaluator.py (ONLY place that reads the hidden map), harness.py, runner.py, replay.py
  agents/       dqn_agent.py, ppo_agent.py, replay_buffer.py   (see only observations)
  policies/     astar_battery.py, rule_shield.py, sim32_heuristic.py, baseline_policies.py
  training/     agent-agnostic training loops
  utils/        JSONL step logger, run metadata (git hash, versions, config)
scripts/        train_dqn.py, train_ppo.py, run_task3.py, run_reference.py, audit_legacy.py, diagnose_ppo.py, visualize_sim.py
tests/          unit / leakage / parity / seeding / training-loop tests
results/        committed run outputs (task3/, audit/, reference_10x10/, logs/, ...)
legacy/         original project, byte-for-byte (also at git tag v0.0-original); used by tests/test_legacy_parity.py
```

## Quick start
```
make setup         # virtualenv + deps (requirements.txt)
make all-checks    # tests + legacy audit + torch-free reference run (no torch needed)
make smoke         # exercises the torch agents (~1 min)
make repro-check   # same seed twice => identical logs
make baselines     # Task 1: full 10x10 DQN/PPO runs, both reward variants
```
Task 3 (32×32) runs through `scripts/run_task3.py` — see `docs/TASK3_BASELINES.md`.
Recover the untouched original at any time: `git checkout v0.0-original`.

## Rules for later tasks
* Anything an agent, monitor or fallback planner uses must come from `obs`/`info` of the env (or `env.explored_map()` on 32×32). `tests/test_no_leakage.py` and `tests/test_sim32.py` fail the build otherwise.
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
