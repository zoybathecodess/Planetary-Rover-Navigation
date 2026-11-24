"""Action-conditioned OOD detector (amendment A3): class-conditional Mahalanobis in the policy's own feature space.

For ensemble member k, h_k(o) is the last hidden layer of its TRAINABLE network (the frozen random prior is excluded).
Classes are the ensemble's proposed action a. Per member: class means mu_{k,a} and one shared (within-class) covariance,
regularised exactly like the v1.1 detector (shrinkage toward the diagonal + tiny ridge).

    score(o, a) = mean_k (h_k - mu_{k,a})^T Sigma_k^{-1} (h_k - mu_{k,a}) / d

Unlike the raw-observation detector it ignores input changes the policy's representation discards (e.g. sensor noise the
network has learned to be insensitive to), and asks "is THIS proposal made in an unfamiliar context?".
Onboard: uses only the observation and the policy's own network.
"""
from __future__ import annotations

import numpy as np
import torch

MIN_CLASS = 256        # classes with fewer fit samples use the pooled mean (pre-registered in amendment A3)


def member_features(member, obs) -> np.ndarray:
    """Last hidden layer (post-activation) of a member's trainable net."""
    net = member.model.net if hasattr(member.model, "net") else member.model
    with torch.no_grad():
        x = torch.as_tensor(np.asarray(obs), dtype=torch.float32)
        if x.dim() == 1:
            x = x.unsqueeze(0)
        return net[:-1](x).numpy()


class ActionConditionedOOD:
    needs_action = True

    def __init__(self, shrinkage: float = 0.1, n_actions: int = 4):
        self.shrinkage, self.n_actions = float(shrinkage), int(n_actions)
        self.mu = self.prec = None          # (K, A, d), (K, d, d)
        self.counts = None
        self.members = None

    def bind(self, ensemble) -> "ActionConditionedOOD":
        self.members = ensemble.members
        return self

    def features(self, obs) -> np.ndarray:
        """(K, d) for one observation, or (K, N, d) for a batch."""
        f = np.stack([member_features(m, obs) for m in self.members])
        return f[:, 0] if np.asarray(obs).ndim == 1 else f

    def fit(self, X: np.ndarray, actions: np.ndarray) -> "ActionConditionedOOD":
        F = self.features(np.asarray(X, float))                  # (K, N, d)
        actions = np.asarray(actions, int)
        K, N, d = F.shape
        self.counts = np.array([(actions == a).sum() for a in range(self.n_actions)])
        mu = np.zeros((K, self.n_actions, d)); prec = np.zeros((K, d, d))
        for k in range(K):
            pooled = F[k].mean(0)
            for a in range(self.n_actions):
                mu[k, a] = F[k][actions == a].mean(0) if self.counts[a] >= MIN_CLASS else pooled
            R = F[k] - mu[k, actions]                            # within-class residuals
            S = R.T @ R / max(N - 1, 1)
            S = (1 - self.shrinkage) * S + self.shrinkage * np.diag(np.diag(S))
            S = S + np.eye(d) * 1e-6 * max(float(np.trace(S)) / d, 1e-12)
            prec[k] = np.linalg.inv(S)
        self.mu, self.prec = mu, prec
        return self

    def score(self, obs, action: int) -> float:
        f = self.features(obs)                                   # (K, d)
        z = f - self.mu[:, int(action)]
        return float(np.mean(np.einsum("kd,kde,ke->k", z, self.prec, z)) / f.shape[1])

    def save(self, path) -> None:
        np.savez(path, mu=self.mu, prec=self.prec, counts=self.counts, shrinkage=self.shrinkage, n_actions=self.n_actions)

    @classmethod
    def load(cls, path, ensemble) -> "ActionConditionedOOD":
        z = np.load(path)
        o = cls(float(z["shrinkage"]), int(z["n_actions"]))
        o.mu, o.prec, o.counts = z["mu"], z["prec"], z["counts"]
        return o.bind(ensemble)
