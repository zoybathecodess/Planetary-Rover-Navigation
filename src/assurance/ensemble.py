"""Ensemble of independently trained DQN members: mean-Q action, per-action disagreement. Onboard (observation-only)."""
from __future__ import annotations

import numpy as np


class EnsemblePolicy:
    """Acts greedily on the mean Q over members. `q_matrix(obs)` -> (K, n_actions) full per-member Q-values."""
    name = "ens"

    def __init__(self, members):
        if len(members) < 2:
            raise ValueError("an ensemble needs at least 2 members")
        self.members = list(members)

    @classmethod
    def from_checkpoints(cls, paths, obs_dim: int, n_actions: int, dqn_cfg, base_seed: int = 0):
        from src.agents.ensemble_member import EnsembleMemberDQN
        members = []
        for i, p in enumerate(paths):
            a = EnsembleMemberDQN(obs_dim, n_actions, dqn_cfg, seed=base_seed + i)
            a.load(p)   # restores the (seed-specific) frozen prior as part of the state dict
            members.append(a)
        return cls(members)

    def q_matrix(self, obs) -> np.ndarray:
        return np.stack([m.q_values(obs) for m in self.members])

    @staticmethod
    def summarise(q: np.ndarray) -> tuple[int, float, float]:
        """(chosen action, std across members of that action's Q, std of the action-value margin)."""
        mean = q.mean(0)
        a = int(np.argmax(mean))
        return a, float(q[:, a].std(ddof=1)), float(mean.max() - np.sort(mean)[-2])

    def act(self, obs) -> int:
        return int(np.argmax(self.q_matrix(obs).mean(0)))


class AStarProposer:
    """Adapter: lets the controller treat the battery-aware A* planner as the 'proposing policy' (one-hot Q, zero disagreement).
    Used for the A*+monitor baseline: same monitor, same fallback, same safe-stop semantics, but no learned component."""
    name = "astar_proposer"

    def __init__(self, planner):
        self.planner = planner

    def q_matrix(self, obs) -> np.ndarray:
        q = np.zeros((3, 4))
        q[:, int(self.planner.act(obs))] = 1.0
        return q

    summarise = staticmethod(EnsemblePolicy.summarise)
