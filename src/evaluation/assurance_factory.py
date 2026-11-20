"""Build the Task-4 policies (plain ensemble, full runtime-assurance controller) from checkpoints + frozen calibration."""
from __future__ import annotations

from src.assurance.controller import RuntimeAssuranceController
from src.assurance.ensemble import EnsemblePolicy
from src.assurance.ood import MahalanobisOOD
from src.evaluation.evaluator import make_env


def member_seed(system_seed: int, j: int) -> int:
    return 1000 * (system_seed + 1) + j


def build_ensemble(cfg, ckpt_dir_for_member, system_seed: int) -> EnsemblePolicy:
    probe, _ = make_env(cfg.env, 0)
    from src.agents.ensemble_member import EnsembleMemberDQN
    members = []
    for j in range(cfg.assurance.n_members):
        a = EnsembleMemberDQN(probe.obs_dim, probe.n_actions, cfg.dqn, seed=member_seed(system_seed, j))
        a.load(str(ckpt_dir_for_member(j)))
        members.append(a)
    return EnsemblePolicy(members)


def build_assured(cfg, ensemble, ood: MahalanobisOOD, tau_unc: float, tau_ood: float, keep_log: bool = False, seed: int = 0,
                  acfg=None):
    from src.policies.astar_battery import BatteryAwareAStar
    fb = BatteryAwareAStar(nominal_energy=cfg.env.ref_energy_cost, seed=seed)
    return RuntimeAssuranceController(ensemble, ood, fb, acfg or cfg.assurance, tau_unc, tau_ood, cfg.env.ref_energy_cost, keep_log)
