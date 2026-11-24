# Reproducing the study

All commands are run from the repository root. Long commands are prefixed with `caffeinate -i` on macOS (keeps the Mac awake).

## 0. Environment
Python 3.10+ with `numpy`, `torch`, `pyyaml`, `pytest`. Versions actually used are recorded in every run manifest
(`results/**/run_manifest.json`, key `software`) and in `protocol/freeze.json`.

## 1. Clean-clone check (needs no trained models)
    git clone <repo> rover_clean && cd rover_clean && git checkout <freeze tag>
    python3 -m pytest -q tests
    python3 scripts/run_experiment.py pilot --methods astar,reactive --seeds 0 --n-maps 5 --jobs 2

The pilot writes `results/pilot/pilot/` with one CSV per (method, preset), `run_manifest.json`, and prints
"consistency problems 0 / pairing problems 0" and a runtime estimate. Pilot runs use maps 60000+ and are never results.

## 2. Training (in-distribution only; seeds 0–9)
    caffeinate -i python3 scripts/run_task3.py train --jobs 4                    # DQN
    caffeinate -i python3 scripts/run_task3.py train --algo ppo --jobs 4         # PPO
    caffeinate -i python3 scripts/run_task4.py train --jobs 4                    # 10 ensembles x 5 members
    caffeinate -i python3 scripts/run_task4.py calibrate --jobs 4                # OOD fit + thresholds (ID validation only)
Training never evaluates on test maps (`run.final_test_eval: false`). Checkpoint = best greedy success on validation maps.

## 3. Freeze
    python3 scripts/freeze.py report         # runs all tests, writes docs/TEST_REPORT.md
    git add -A && git commit -m "Phase 1 freeze"
    python3 scripts/freeze.py freeze         # writes protocol/freeze.json (code, configs, checkpoint and calibration hashes, thresholds)
    git add protocol/freeze.json && git commit -m "Freeze manifest" && git tag v5.0-freeze
    python3 scripts/freeze.py verify         # must print CLEAN before any final evaluation

## 4. Pilot and dress rehearsal
    caffeinate -i python3 scripts/run_experiment.py pilot --jobs 4
    caffeinate -i python3 scripts/run_experiment.py run --name rehearsal --split val --seeds 0-9 --n-maps 100 --jobs 4
    python3 scripts/run_experiment.py validate --run results/phase2/rehearsal --split val
    python3 scripts/analyse.py --run results/phase2/rehearsal --split val      # same tables as the final analysis; not a result

## 5. Confirmatory evaluation (Phase 2; refuses to run unless `freeze.py verify` is clean)
    caffeinate -i python3 scripts/run_experiment.py run --name phase2 --split final --seeds 0-9 --n-maps 200 --jobs 4
    python3 scripts/run_experiment.py validate --run results/phase2/phase2 --split final

## 6. Analysis
    python3 scripts/analyse.py --run results/phase2/phase2 --split final
Tables land in `results/phase2/phase2/analysis/final/` (main, ablation, sensitivity, failure modes, paired comparisons with Holm-adjusted p). The analysis is fixed by `protocol/analysis_plan.json`.

Every use of `test` or `final` maps is appended to `results/test_access.jsonl` (time, split, git commit, command line).
