# Task 4 — Runtime-assurance system

Pipeline per decision (onboard information only: the 59-d observation + `env.explored_map()`):

    ensemble (5 DQN members) ──► proposed action a, uncertainty u
    Mahalanobis OOD score s (windowed) ─┐
    safety monitor rules on a ──────────┼─► any alarm? ──no──► ACCEPT a
    uncertainty gate u > τ_u ───────────┘          │yes
                                                   ▼
                       FALLBACK: battery-aware A* ranks moves; take the best that passes the hard monitor rules
                       no energy-feasible route, or no ranked move passes ──► SAFE STOP (episode ends, reason `safe_stop`)

## Components (all in `src/assurance/`, onboard)
| File | Role |
|---|---|
| `src/agents/ensemble_member.py` | One member: Double DQN + **randomised prior** + **bootstrapped replay** |
| `ensemble.py` | Mean-Q action; `u` = std across members of the chosen action's Q (raw, not normalised) |
| `ood.py` | Mahalanobis detector (`MahalanobisOOD`) + `WindowedScore` |
| `monitor.py` | Rule monitor: `invalid_action`, `obstacle_proximity`, `battery_feasibility`, `uncertain_movement` |
| `controller.py` | Accept / fallback / stop logic, counters (`stats`), per-decision records (`log`) |
| `layout.py` | Observation indices + `STOP_ACTION=-1` (checked against `FEATURES` by a test) |
| `src/policies/astar_battery.py` | `analyse()`: ranked first moves (reverse Dijkstra) + energy feasibility, used as fallback |
| `src/evaluation/assurance_factory.py` | Builds ensemble / controller from checkpoints (orchestration, not onboard) |

## Ensemble diversity (both methods, as requested)
1. **Randomised prior functions** (Osband et al. 2018): `Q_k(s) = f_k(s) + β·p_k(s)`, `p_k` a frozen random MLP
   (64-64, Tanh, orthogonal init, seed-determined), `β = prior_scale = 10`. The prior is part of the checkpoint, so
   a loaded member reproduces the trained one exactly (tested). Only `f_k` is trained.
2. **Bootstrapped replay**: each stored transition gets a Poisson(1) weight (own RNG per member) multiplying its
   Huber loss — the online-bootstrap approximation of resampling the data with replacement (tested: mean 1, P(0)=e⁻¹).
Members differ in network init, prior, replay sampling, exploration stream (seed `1000·(system_seed+1)+j`).
Config: `configs/sim32_id_ensemble.yaml` (`dqn.prior_scale`, `dqn.prior_hidden`, `dqn.bootstrap`). Setting
`prior_scale: 0, bootstrap: false` gives a plain independent-seeds ensemble for an ablation.

## OOD detector
Features (`layout.OOD_FEATURES`, 29-d): the 25 noisy window readings, slip estimate, sensor confidence, battery and
step ratios — evidence about terrain statistics, sensor noise and dynamics/energy, **not** about where the rover is
(position, goal offset, coverage, visit counts excluded; tested). Score = Mahalanobis² / d, covariance shrunk 10 %
towards its diagonal. Fit on the ensemble's own trajectories over 200 fresh ID maps from the training generator
(seeds 30000+). The gate uses the mean of the last `ood_window=10` scores.

## Thresholds (in-distribution validation only)
τ_u and τ_s are percentiles of the per-step score distributions of the plain ensemble on the ID validation maps
(seeds 10000–10099). **No shifted data is used anywhere in calibration.** Defaults: 95th (u), 99th (s). The
evaluation sweeps `--pcts 95,99,90` (applied to both gates) and the report has one row per percentile = the
**sensitivity analysis**. The percentile is the target per-step false-alarm rate on ID data (tested with held-out data).
Calibration arrays, the fitted detector and a SHA-256 are stored in `results/task4/calib/` (`frozen.json`).

## Monitor rules
| Rule | Fires when | Applies to |
|---|---|---|
| `invalid_action` | move leaves the map | all |
| `obstacle_proximity` | target believed blocked (window ≥ .999, majority of past readings, or bumped) | all |
| `battery_feasibility` | entry energy > battery, or battery after move < Manhattan distance left | all |
| `uncertain_movement` | slip estimate ≥ 0.15 and a perpendicular neighbour is a believed obstacle / edge | policy action only |

## Fallback and safe stop
Fallback = battery-aware A* (Task 3). Moves are ranked by cost-of-entering + cost-to-goal; the first one passing the
hard rules is used. **Safe stop** is a new terminal reason `safe_stop`: `env.safe_stop()` ends the episode with zero
energy and zero reward. It is **not a success** (success = reason `goal`) and is reported as its own rate, so it can
never hide inside the success rate. It happens when (a) the cheapest estimated route energy exceeds the battery, or
(b) every ranked move is vetoed. Energy-infeasibility is judged from the *believed* map (unknown cells carry the
A* risk premium), so a stop can be conservative — the stop rate quantifies that cost.

## Information boundary
No module in `src/assurance/` imports the evaluator, generator or terrain, nor touches private env state (AST test).
`act(obs)` gets only the observation; the explored map arrives via `attach(env.explored_map, capacity)`.
Ground truth is used only by the evaluator for scoring (`attempted_unsafe`, optimal cost).

## Intervention logs
`eval --log-maps 5` re-runs the first maps of the first percentile and writes `eval/<split>/<preset>/logs/*.jsonl`:
per decision `{t, policy_action, action, source (policy|fallback|stop), reasons, unc, margin, ood}`.
Counters per episode go into the CSVs (`interventions, fallback_steps, unc_alarms, ood_alarms, monitor_rejects`).

## Running it
    python3 scripts/run_task4.py train     --jobs 4
    python3 scripts/run_task4.py calibrate --jobs 4
    python3 scripts/run_task4.py eval      --split val  --jobs 4
    python3 scripts/run_task4.py report    --split val
    (after the design is frozen)  eval --split test ; report --split test

## Known limits / things to check in the results
* `prior_scale=10` was fixed a priori, not tuned. Check in the `val` report that the **uncertainty alarm rate on shifted
  presets exceeds the ID rate**; if it does not, the uncertainty gate adds little and that is a finding to report, not
  something to fix on test. If you change `prior_scale`, change it once, on validation, and document it.
* Calibration maps (ID val) are also the maps used for `best_val` checkpoint selection; the thresholds are therefore
  slightly optimistic for ID. A fresh calibration split would remove this (use `--cal-maps` on other seeds) if needed.
* Under strong shift the OOD gate may fire almost every step, making the system behave like A* (it is then a
  detector + fallback, not a learned-policy system). The fallback/alarm columns show this directly.
* The fallback is not collision-free under noisy sensors/slip; the report gives collisions for it.
