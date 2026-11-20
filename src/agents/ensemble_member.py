"""Ensemble member for Task 4: Double DQN + randomized prior function + online-bootstrap replay weights.

Diversity (the plan asks for a documented anti-collapse method; we use BOTH):
  * Randomized prior functions (Osband et al., 2018): Q_k(s,.) = f_k(s,.) + prior_scale * p_k(s,.), where p_k is a FIXED,
    randomly initialised network that is never trained. The trainable f_k only has to explain the data it has seen; away from
    that data the random prior keeps members different, which is exactly the epistemic signal we want for OOD inputs.
    The prior lives inside the saved state_dict, so a checkpoint is self-contained.
  * Bootstrapped replay (online bootstrap, Oza & Russell): each transition a member stores receives an integer weight
    ~ Poisson(1) drawn from the MEMBER'S OWN RNG; the TD loss is weighted by it. Members therefore effectively train on
    different resamples of their (also different) experience, without discarding data on average.
Members are trained independently (own env interaction, own seed) by the agent-agnostic `train_dqn` loop.
"""
from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

from src.agents.dqn_agent import DQNAgent, mlp
from src.config import DQNConfig


class PriorQNet(nn.Module):
    """f(s) + beta * p(s); only `net` is trainable, `prior` is frozen."""

    def __init__(self, net: nn.Sequential, prior: nn.Sequential, beta: float):
        super().__init__()
        self.net, self.prior, self.beta = net, prior, float(beta)
        for p in self.prior.parameters():
            p.requires_grad_(False)

    def forward(self, x):
        out = self.net(x)
        return out + self.beta * self.prior(x) if self.beta else out


class BootstrapReplayBuffer:
    """Ring buffer that also stores a per-transition bootstrap weight. sample() -> (s, a, r, s2, done, w)."""

    def __init__(self, capacity: int, obs_dim: int, seed: int, bootstrap: bool):
        self.cap, self.n, self.i, self.bootstrap = capacity, 0, 0, bootstrap
        self.rng = np.random.default_rng(seed)
        self.s = np.zeros((capacity, obs_dim), np.float32); self.s2 = np.zeros((capacity, obs_dim), np.float32)
        self.a = np.zeros(capacity, np.int64); self.r = np.zeros(capacity, np.float32)
        self.d = np.zeros(capacity, np.float32); self.w = np.ones(capacity, np.float32)

    def add(self, s, a, r, s2, terminated) -> None:
        i = self.i
        self.s[i], self.a[i], self.r[i], self.s2[i], self.d[i] = s, a, r, s2, float(terminated)
        self.w[i] = float(self.rng.poisson(1.0)) if self.bootstrap else 1.0
        self.i, self.n = (i + 1) % self.cap, min(self.n + 1, self.cap)

    def sample(self, bs: int):
        idx = self.rng.choice(self.n, bs, replace=False)
        return self.s[idx], self.a[idx], self.r[idx], self.s2[idx], self.d[idx], self.w[idx]

    def __len__(self) -> int:
        return self.n


class EnsembleMemberDQN(DQNAgent):
    def __init__(self, obs_dim: int, n_actions: int, cfg: DQNConfig | None = None, seed: int = 0):
        super().__init__(obs_dim, n_actions, cfg, seed)
        c = self.cfg
        with torch.random.fork_rng():           # the prior is a deterministic function of the seed, independent of global state
            torch.manual_seed(seed + 7_777)
            prior = mlp(obs_dim, c.prior_hidden, n_actions, act=nn.Tanh)
            for m in prior.modules():
                if isinstance(m, nn.Linear):
                    nn.init.orthogonal_(m.weight, gain=1.0)
                    nn.init.zeros_(m.bias)
        self.model = PriorQNet(self.model, prior, c.prior_scale)
        self.target = PriorQNet(self.target, prior, c.prior_scale)  # same frozen prior object
        self.target.load_state_dict(self.model.state_dict())
        self.target.eval()
        self.optimizer = optim.Adam(self.model.net.parameters(), lr=c.lr, eps=1e-4)
        self.buffer = BootstrapReplayBuffer(c.buffer_size, obs_dim, seed, c.bootstrap)

    def learn(self) -> None:
        bs = self.cfg.batch_size
        if len(self.buffer) < bs:
            return
        s, a, r, s2, d, w = (torch.from_numpy(x) for x in self.buffer.sample(bs))
        with torch.no_grad():  # Double DQN target (prior included in both nets)
            best = self.model(s2).argmax(1, keepdim=True)
            target_q = r + self.cfg.gamma * self.target(s2).gather(1, best).squeeze(1) * (1.0 - d)
        current_q = self.model(s).gather(1, a.unsqueeze(1)).squeeze(1)
        loss = (w * F.smooth_l1_loss(current_q, target_q, reduction="none")).mean()
        self.optimizer.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(self.model.net.parameters(), self.cfg.grad_clip)
        self.optimizer.step()
        self.train_step += 1
        if self.train_step % self.cfg.target_update_freq == 0:
            self.target.load_state_dict(self.model.state_dict())
