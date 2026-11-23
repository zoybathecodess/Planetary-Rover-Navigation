# Phase 2 experiment protocol (frozen defaults)

The machine-readable version is `protocol/phase2_protocol.json`; its hash is part of `protocol/freeze.json`.
Items under "Open for Task 6" may still be decided before the confirmatory run; nothing else changes after the freeze.

## Design
* **Simulator:** 32×32 partially observable rover world, battery 250, 59-d observation; five conditions: `id`, `terrain_shift`,
  `sensor_shift`, `dynamics_shift`, `combined_shift` (parameters in `configs/sim32_<preset>.yaml`, hashed in the freeze).
* **Training:** in-distribution only. DQN, PPO and a 5-member ensemble (randomised priors + bootstrapped replay) for each
  of 10 system seeds (0–9). Checkpoint = best greedy success on validation maps.
* **Maps / splits** (all deterministic, one map per seed):

| Split | Seeds | Used for |
|---|---|---|
| train | env stream (`SeedSequence([seed, 0x5EED, i])`) | learning |
| val | 10000+ | checkpoint selection; OOD/uncertainty threshold calibration (ID preset only) |
| fit | 30000+ | OOD detector fitting (ID) |
| test | 20000+ | **reserved/exploratory**: Task 1/3 training scripts printed its greedy success rate, never used for a decision |
| **final** | **40000+** | **confirmatory evaluation**; untouched before the freeze, guarded and logged |
| pilot | 60000+ | debugging and runtime only; never a result |

  Disjointness is tested by hashing the generated terrain grids (train stream vs every split).
* **Methods:** A*, reactive, DQN, DQN+rule shield, PPO, PPO+rule shield, plain ensemble, and the runtime-assurance system
  `assured@95` (primary) with its sensitivity (`@90`, `@99`) and ablation variants (`monitor_only`, `unc_only`, `ood_only`,
  `no_ood`, `no_unc`, `no_monitor`, `no_stop`). Two operating points are reported for the proposed system:
  safe stop enabled (safety-first) and `no_stop` (mission-first).
* **Thresholds:** percentiles (95 primary; 90, 99 sensitivity) of per-step scores of the plain ensemble on ID validation maps;
  numerical values per system seed are stored in the freeze.
* **Metrics:** success (terminal reason `goal`; a safe stop is a mission failure reported separately), collisions and
  attempted unsafe moves per episode, steps, energy used, battery left, intervention/fallback/safe-stop rates, per-condition results.
* **Statistics:** learned methods: mean ± 95 % t-interval over system seeds; paired differences over matched (map, seed) pairs;
  deterministic methods: Wilson interval over maps. Every method sees the same maps in the same order.

## Known limitations (recorded, not silently changed)
1. The `test` split (20000+) was displayed by Task 1/3 training summaries, so it is not used for confirmatory claims.
   (Those numbers were not used for any model or design decision; selection used validation maps only.)
2. Ensemble `prior_scale=10` and the rule-monitor parameters (slip threshold 0.15, feasibility margin 1.0) were set a priori, not tuned.
3. OOD thresholds are calibrated on the same ID validation maps used for checkpoint selection; slightly optimistic for ID.
4. Under sensor and combined shift the OOD gate fires on ~95 % of steps; the system then behaves largely like the A* fallback
   (see ablations: the rule monitor accounts for most of the collision reduction).
5. Safe stop costs ~6 points of success in `combined_shift` (validation); it is a safety/mission trade-off, reported as two operating points.
6. The A* fallback uses a nominal energy table and is not collision-free under noisy sensing; its collisions are reported.
7. All findings are simulation results; nothing here supports claims about real planetary rovers.

## Open for Task 6
* Number of maps per preset (default 200), choice of paired test and multiplicity correction.
* Whether `test` is dropped or reported as exploratory.
