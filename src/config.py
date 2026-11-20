"""Typed configuration loaded from YAML. One file fully describes a run."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from typing import Any

import yaml


@dataclass
class EnvConfig:
    size: int = 10
    battery: int = 100
    # terrain probabilities (obstacle probability is the remainder)
    p_normal: float = 0.55
    p_sand: float = 0.15
    p_rock: float = 0.15
    # "onboard": 15-d, policy-facing, no full-map information
    # "legacy17": original 17-d vector incl. Dijkstra cost-to-goal/budget-margin (reproduction/ablation ONLY)
    obs_mode: str = "onboard"
    # per-step reward term that uses full-map Dijkstra (training-signal only, never observed)
    reward_privileged_shaping: bool = False
    max_steps: int | None = None  # default: battery (cannot trigger, every action costs >= 1)
    map_retry_limit: int = 1000
    ensure_energy_feasible: bool = True
    # ---- Task 2 (kind == "advanced"): 32x32 partially observable simulator. Ignored by the basic env. ----
    kind: str = "basic"                 # "basic" = Task-1 10x10 env | "advanced" = Task-2 POMDP env
    gen_corr: int = 2                   # terrain clustering: # of 3x3 box-blur passes over the noise fields (0 = i.i.d.)
    max_opt_cost_frac: float = 0.6      # map accepted only if reference optimal cost <= frac * battery (slack for slip/detours)
    ref_energy_cost: tuple = (1, 3, 5)  # nominal energy table used ONLY for map acceptance (keeps maps identical across dynamics shifts)
    energy_cost: tuple = (1, 3, 5)      # TRUE energy per entered cell: (normal, sand, rock)
    slip_prob: tuple = (0.02, 0.10, 0.05)  # TRUE slip probability by terrain of the cell the rover stands on
    sensor_miss: float = 0.05           # TRUE P(obstacle not detected)
    sensor_false: float = 0.02          # TRUE P(free cell reported as obstacle)
    sensor_sigma: float = 0.05          # TRUE std-dev of the terrain reading (reading scale 0..1)


@dataclass
class DQNConfig:
    gamma: float = 0.99
    lr: float = 5e-4
    eps_start: float = 1.0
    eps_min: float = 0.05
    eps_decay: float = 0.992  # per episode (as in original)
    buffer_size: int = 50_000
    batch_size: int = 128
    warmup_steps: int = 2_000
    target_update_freq: int = 500
    grad_clip: float = 1.0
    hidden: tuple[int, ...] = (256, 256, 128)
    # ---- Task 4 ensemble members (defaults = plain Double DQN, i.e. unchanged Task-3 behaviour) ----
    prior_scale: float = 0.0            # randomized prior function: Q = f_theta(s) + prior_scale * p(s), p fixed & random
    prior_hidden: tuple[int, ...] = (64, 64)
    bootstrap: bool = False             # online bootstrap: each stored transition gets weight ~ Poisson(1) for this member


@dataclass
class PPOConfig:
    gamma: float = 0.99
    lam: float = 0.95
    clip: float = 0.2
    lr: float = 3e-4
    epochs: int = 10
    entropy_coef: float = 0.05
    value_coef: float = 0.5
    minibatch: int = 64
    rollout_steps: int = 512
    grad_clip: float = 0.5
    hidden: tuple[int, ...] = (256, 256)
    # Rewards are multiplied by this inside GAE only (env reward is untouched). Episode returns reach ~100-150
    # (goal bonus), so the unscaled critic loss dominates the shared trunk and the clipped gradient norm.
    # 1.0 = original behaviour; 0.02 puts returns near O(1-3).
    reward_scale: float = 1.0


@dataclass
class AssuranceConfig:
    """Task 4 runtime-assurance settings. Thresholds are NOT stored here: they are calibrated on in-distribution
    VALIDATION maps (scripts/run_task4.py calibrate) and frozen in results/task4/assurance/*/thresholds.json."""
    n_members: int = 5
    unc_percentile: float = 95.0        # uncertainty gate threshold = this percentile of ID-validation scores
    ood_percentile: float = 99.0        # OOD gate threshold = this percentile of ID-validation (windowed) scores
    ood_window: int = 10                # OOD score = mean Mahalanobis distance of the last `ood_window` observations
    ood_shrinkage: float = 0.1          # covariance shrinkage toward its diagonal (numerical stability)
    fit_episodes: int = 200             # training-stream episodes used to fit the OOD detector
    slip_threshold: float = 0.15        # monitor rule `uncertain_movement`: slip_estimate at/above this ...
    hold_steps: int = 0                 # keep the fallback in control for this many steps after a trip (0 = per-step)
    feasibility_margin: float = 1.0     # stop if (min estimated energy to goal) * margin > battery
    use_uncertainty: bool = True
    use_ood: bool = True
    use_monitor: bool = True
    allow_stop: bool = True      # False = ablation: never end the episode; keep driving on the best ranked move


@dataclass
class RunConfig:
    seed: int = 0
    episodes: int = 1500
    eval_every: int = 100        # greedy evaluation on fixed validation maps
    eval_episodes: int = 50
    val_seed_offset: int = 10_000  # validation maps: seeds 10_000...
    test_seed_offset: int = 20_000  # test maps: seeds 20_000... (never used for selection)
    torch_threads: int = 1       # tiny MLPs are fastest on 1 thread; avoids oversubscription
    log_margin: bool = False     # evaluator-side budget margin each step (costs one Dijkstra/step)
    out_dir: str = "results/run"


@dataclass
class Config:
    env: EnvConfig = field(default_factory=EnvConfig)
    dqn: DQNConfig = field(default_factory=DQNConfig)
    ppo: PPOConfig = field(default_factory=PPOConfig)
    assurance: AssuranceConfig = field(default_factory=AssuranceConfig)
    run: RunConfig = field(default_factory=RunConfig)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _fill(cls, data: dict | None):
    data = dict(data or {})
    names = {f.name for f in fields(cls)}
    unknown = set(data) - names
    if unknown:
        raise KeyError(f"Unknown keys for {cls.__name__}: {sorted(unknown)}")
    for k in ("hidden", "prior_hidden"):
        if k in data:
            data[k] = tuple(data[k])
    return cls(**data)


def load_config(path: str | Path, overrides: dict[str, Any] | None = None) -> Config:
    raw = yaml.safe_load(Path(path).read_text()) or {}
    unknown = set(raw) - {"env", "dqn", "ppo", "assurance", "run"}
    if unknown:
        raise KeyError(f"Unknown top-level config sections: {sorted(unknown)}")
    cfg = Config(
        env=_fill(EnvConfig, raw.get("env")),
        dqn=_fill(DQNConfig, raw.get("dqn")),
        ppo=_fill(PPOConfig, raw.get("ppo")),
        assurance=_fill(AssuranceConfig, raw.get("assurance")),
        run=_fill(RunConfig, raw.get("run")),
    )
    for dotted, value in (overrides or {}).items():  # e.g. {"run.seed": 3}
        section, key = dotted.split(".")
        setattr(getattr(cfg, section), key, value)
    return cfg
