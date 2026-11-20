"""Mahalanobis out-of-distribution detector on the policy-facing observation (onboard, numpy only).

Fit on TRAINING-distribution observations only; the alarm threshold is set elsewhere, on in-distribution VALIDATION data.
score(obs) = (z - mu)^T Sigma_reg^-1 (z - mu) / d  for z = obs[OOD_FEATURES]   (~1 for in-distribution Gaussian data).
Sigma_reg = (1-a) Sigma + a diag(Sigma) + tiny ridge: near-constant features (e.g. map-edge cells) stay finite.
The gate uses a windowed mean of the last `window` scores so a single noisy reading does not trip it.
"""
from __future__ import annotations

from collections import deque

import numpy as np

from src.assurance.layout import OOD_FEATURES


class MahalanobisOOD:
    def __init__(self, features=OOD_FEATURES, shrinkage: float = 0.1):
        self.features, self.shrinkage = tuple(features), float(shrinkage)
        self.mu = self.prec = None
        self.n_fit = 0

    def fit(self, X: np.ndarray) -> "MahalanobisOOD":
        Z = np.asarray(X, dtype=float)[:, list(self.features)]
        if len(Z) < 10 * Z.shape[1]:
            raise ValueError(f"need >= {10 * Z.shape[1]} observations to fit {Z.shape[1]} features, got {len(Z)}")
        self.mu = Z.mean(0)
        S = np.cov(Z, rowvar=False)
        S = (1 - self.shrinkage) * S + self.shrinkage * np.diag(np.diag(S))
        S = S + np.eye(len(S)) * 1e-6 * max(float(np.trace(S)) / len(S), 1e-12)
        self.prec = np.linalg.inv(S)
        self.n_fit = len(Z)
        return self

    def score(self, obs) -> float:
        z = np.asarray(obs, dtype=float)[list(self.features)] - self.mu
        return float(z @ self.prec @ z) / len(z)

    def scores(self, X: np.ndarray) -> np.ndarray:
        Z = np.asarray(X, dtype=float)[:, list(self.features)] - self.mu
        return np.einsum("ij,jk,ik->i", Z, self.prec, Z) / Z.shape[1]

    def save(self, path) -> None:
        np.savez(path, mu=self.mu, prec=self.prec, features=np.array(self.features), shrinkage=self.shrinkage, n_fit=self.n_fit)

    @classmethod
    def load(cls, path) -> "MahalanobisOOD":
        d = np.load(path)
        o = cls(tuple(int(i) for i in d["features"]), float(d["shrinkage"]))
        o.mu, o.prec, o.n_fit = d["mu"], d["prec"], int(d["n_fit"])
        return o


class WindowedScore:
    """Mean of the last `window` scores (fewer at the start of an episode)."""

    def __init__(self, window: int):
        self.buf = deque(maxlen=max(1, int(window)))

    def reset(self) -> None:
        self.buf.clear()

    def update(self, score: float) -> float:
        self.buf.append(score)
        return float(np.mean(self.buf))
