"""Training loops (agent-agnostic, torch-free). Agents are duck-typed:
   DQN-like: act(obs, greedy=False), remember(s,a,r,s2,terminated), learn(), decay_epsilon(), .epsilon
   PPO-like: sample(obs)->(a,logp,v), act(obs, greedy=True), value(obs), store(...), update(last_value)
Success is the env's terminal reason == 'goal' (never inferred from reward magnitude).
Reported training SR is training-time (exploring) behaviour; greedy evaluation on fixed validation maps is separate.
"""
from __future__ import annotations

import csv
import json
import time
from pathlib import Path

import numpy as np

from src.config import Config
from src.evaluation.evaluator import make_env
from src.evaluation.runner import evaluate

EP_FIELDS = ["episode", "reward", "success", "reason", "battery", "steps", "mean_margin", "epsilon"]
EVAL_FIELDS = ["episode", "success_rate", "ci_lo", "ci_hi", "mean_battery_left_success", "mean_steps",
               "goal", "battery_depleted", "timeout"]


class _Greedy:
    def __init__(self, agent):
        self.agent = agent

    def act(self, obs):
        return self.agent.act(obs, greedy=True)


class _Sampled:
    """Stochastic evaluation of a PPO-like agent (draws from the policy instead of argmax)."""
    def __init__(self, agent):
        self.agent = agent

    def act(self, obs):
        return self.agent.act(obs, greedy=False)


class _Writers:
    def __init__(self, out_dir: Path):
        out_dir.mkdir(parents=True, exist_ok=True)
        self.ep_f = (out_dir / "episodes.csv").open("w", newline="")
        self.ev_f = (out_dir / "eval_greedy_val.csv").open("w", newline="")
        self.ep, self.ev = csv.DictWriter(self.ep_f, EP_FIELDS), csv.DictWriter(self.ev_f, EVAL_FIELDS)
        self.ep.writeheader(); self.ev.writeheader()

    def close(self):
        self.ep_f.close(); self.ev_f.close()


def _eval(agent, cfg: Config, eval_env, eval_ev, offset: int, n: int):
    return evaluate(eval_env, eval_ev, _Greedy(agent), range(offset, offset + n))[1]


def _eval_row(episode, s):
    return {"episode": episode, "success_rate": s["success_rate"], "ci_lo": s["success_ci95"][0],
            "ci_hi": s["success_ci95"][1], "mean_battery_left_success": s["mean_battery_left_success"],
            "mean_steps": s["mean_steps"], **s["reasons"]}


def _finish(agent, cfg: Config, out_dir: Path, w: _Writers, success, battery, t0, n_steps, eval_env, eval_ev):
    w.close()
    val = _eval(agent, cfg, eval_env, eval_ev, cfg.run.val_seed_offset, 200)
    test = _eval(agent, cfg, eval_env, eval_ev, cfg.run.test_seed_offset, 200) if cfg.run.final_test_eval else None
    # PPO-like agents: also report the sampled policy on the same maps (after the greedy runs, so greedy numbers
    # and RNG streams are unchanged). A large greedy-vs-sampled gap means the argmax policy is not the trained one.
    sampled = ({"sampled_val_200": evaluate(eval_env, eval_ev, _Sampled(agent), range(cfg.run.val_seed_offset, cfg.run.val_seed_offset + 200))[1],
                **({"sampled_test_200": evaluate(eval_env, eval_ev, _Sampled(agent), range(cfg.run.test_seed_offset, cfg.run.test_seed_offset + 200))[1]}
                  if cfg.run.final_test_eval else {})}
               if hasattr(agent, "sample") else {})
    summary = {
        "episodes": len(success), "env_steps": n_steps, "wall_seconds": round(time.time() - t0, 1),
        "train_time_SR_last100": float(np.mean(success[-100:])), "train_time_battery_last100": float(np.mean(battery[-100:])),
        "train_time_min_battery": int(min(battery)),
        "greedy_val_200": val, **({"greedy_test_200": test} if test is not None else {}), **sampled,
        "note": "train_time_* include exploration (DQN eps>=eps_min, PPO sampling); greedy_* are the deployable policy",
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, default=float))
    if hasattr(agent, "save"):
        ck = out_dir / "checkpoints"; ck.mkdir(exist_ok=True)
        agent.save(ck / "final.pt")
    return summary


def train_dqn(agent, cfg: Config, out_dir: str | Path) -> dict:
    out = Path(out_dir)
    env, ev = make_env(cfg.env, seed=cfg.run.seed)
    eval_env, eval_ev = make_env(cfg.env, seed=cfg.run.seed)
    rng, w, t0 = np.random.default_rng(cfg.run.seed + 1), _Writers(out), time.time()
    n_steps = 0
    obs = env.reset()
    for _ in range(cfg.dqn.warmup_steps):  # random-policy replay warm-up (as in the original)
        a = int(rng.integers(env.n_actions))
        obs2, r, done, info = env.step(a)
        agent.remember(obs, a, r, obs2, info["terminated"])
        obs = env.reset() if done else obs2
    success, battery, best_val = [], [], -1.0
    for ep in range(cfg.run.episodes):
        obs, total, margins, done = env.reset(), 0.0, [], False
        while not done:
            a = agent.act(obs)
            obs2, r, done, info = env.step(a)
            agent.remember(obs, a, r, obs2, info["terminated"])
            agent.learn()
            if cfg.run.log_margin:
                margins.append(ev.budget_margin())
            obs, total, n_steps = obs2, total + r, n_steps + 1
        agent.decay_epsilon()
        success.append(int(info["reason"] == "goal")); battery.append(env.battery)
        w.ep.writerow({"episode": ep + 1, "reward": round(total, 3), "success": success[-1], "reason": info["reason"],
                       "battery": env.battery, "steps": info["steps"],
                       "mean_margin": float(np.mean(margins)) if margins else "", "epsilon": round(agent.epsilon, 4)})
        if (ep + 1) % cfg.run.eval_every == 0:
            sv = _eval(agent, cfg, eval_env, eval_ev, cfg.run.val_seed_offset, cfg.run.eval_episodes)
            w.ev.writerow(_eval_row(ep + 1, sv))
            w.ep_f.flush(); w.ev_f.flush()
            if hasattr(agent, "save") and sv["success_rate"] >= best_val:  # selection uses VALIDATION maps only
                best_val = sv["success_rate"]
                (out / "checkpoints").mkdir(parents=True, exist_ok=True)
                agent.save(out / "checkpoints" / "best_val.pt")
    return _finish(agent, cfg, out, w, success, battery, t0, n_steps, eval_env, eval_ev)


def train_ppo(agent, cfg: Config, out_dir: str | Path) -> dict:
    out = Path(out_dir)
    env, ev = make_env(cfg.env, seed=cfg.run.seed)
    eval_env, eval_ev = make_env(cfg.env, seed=cfg.run.seed)
    w, t0 = _Writers(out), time.time()
    success, battery, n_steps, ep, best_val = [], [], 0, 0, -1.0
    obs, total, margins = env.reset(), 0.0, []
    while ep < cfg.run.episodes:
        a, logp, v = agent.sample(obs)
        obs2, r, done, info = env.step(a)
        # `done` (termination OR truncation) cuts GAE. Truncation cannot occur with max_steps=battery
        # (every action costs >= 1 battery); if max_steps is lowered, value bootstrapping on truncation is needed.
        agent.store(obs, a, logp, r, v, done)
        if cfg.run.log_margin:
            margins.append(ev.budget_margin())
        total, n_steps = total + r, n_steps + 1
        if done:
            success.append(int(info["reason"] == "goal")); battery.append(env.battery)
            w.ep.writerow({"episode": ep + 1, "reward": round(total, 3), "success": success[-1], "reason": info["reason"],
                           "battery": env.battery, "steps": info["steps"],
                           "mean_margin": float(np.mean(margins)) if margins else "", "epsilon": ""})
            ep += 1
            if ep % cfg.run.eval_every == 0:
                sv = _eval(agent, cfg, eval_env, eval_ev, cfg.run.val_seed_offset, cfg.run.eval_episodes)
                w.ev.writerow(_eval_row(ep, sv))
                w.ep_f.flush(); w.ev_f.flush()
                if hasattr(agent, "save") and sv["success_rate"] >= best_val:  # selection uses VALIDATION maps only
                    best_val = sv["success_rate"]
                    (out / "checkpoints").mkdir(parents=True, exist_ok=True)
                    agent.save(out / "checkpoints" / "best_val.pt")
            obs, total, margins = env.reset(), 0.0, []
        else:
            obs = obs2
        if n_steps % cfg.ppo.rollout_steps == 0:
            agent.update(0.0 if done else agent.value(obs))
    agent.update(0.0 if done else agent.value(obs))  # flush the partial rollout
    return _finish(agent, cfg, out, w, success, battery, t0, n_steps, eval_env, eval_ev)
