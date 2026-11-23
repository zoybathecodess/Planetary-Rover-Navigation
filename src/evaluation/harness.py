"""ONE evaluation interface for every Task-3+ method (A*, reactive, DQN, shielded DQN, later PPO / the assurance system).

Fairness by construction:
  * a method is just an object with `act(obs) -> int` (+ optional `attach`, `stats`, `last_decision`);
  * every method sees the SAME maps, start/goal, battery and noise: an episode is fully determined by (preset, seed),
    and the slip and sensor streams consume a fixed number of draws per step, so methods that take the same number of
    steps see the same random numbers (common random numbers -> paired comparisons are valid);
  * success == terminal reason "goal"; all rows come from the same code path.
Metrics added to the Task-1 runner row: attempted_unsafe (commanded move into an obstacle/off-map, judged by the
evaluator from ground truth), interventions/decisions (shield), plan_ms (decision latency).
"""
from __future__ import annotations

import csv
import time
from pathlib import Path

import numpy as np

from src.assurance.layout import STOP_ACTION
from src.config import Config, load_config
from src.evaluation.evaluator import make_env
from src.evaluation.runner import summarise

ROW_FIELDS = ["method", "preset", "map", "success", "reason", "steps", "reward", "battery_left", "energy_used", "collisions",
              "attempted_unsafe", "interventions", "decisions", "no_safe_action", "fallback_steps", "unc_alarms", "ood_alarms", "monitor_rejects", "optimal_cost", "energy_ratio", "plan_ms"]
from src.evaluation.reproducibility import SPLIT_OFFSET  # noqa: E402  (val/test/fit/final/pilot; single source of truth)


class GreedyAgentPolicy:
    """Greedy (argmax) evaluation wrapper for DQN/PPO agents; exposes q_values when the agent has them."""

    def __init__(self, agent, name: str):
        self.agent, self.name = agent, name

    def act(self, obs) -> int:
        return self.agent.act(obs, greedy=True)

    def q_values(self, obs):
        return self.agent.q_values(obs)


def _attach(policy, env) -> None:
    for p in (policy, getattr(policy, "base", None)):
        if p is not None and hasattr(p, "attach"):
            p.attach(env.explored_map, env.max_battery)  # the env's PUBLIC onboard API only


def _stat_snapshot(policy) -> tuple[int, ...]:
    s = getattr(policy, "stats", None)
    if not s:
        return (0,) * 7
    return (s["decisions"], s["interventions"], s["no_safe_action"], s.get("fallback", 0), s.get("unc_alarms", 0),
            s.get("ood_alarms", 0), s.get("monitor_rejects", 0))


def run_episode_ext(env, ev, policy, seed: int, method: str = "", preset: str = "") -> dict:
    obs = env.reset(seed=seed)
    d0 = _stat_snapshot(policy)
    energy = collisions = unsafe = 0
    total_r, done, info, t_dec = 0.0, False, {}, 0.0
    while not done:
        t0 = time.perf_counter()
        a = int(policy.act(obs))
        t_dec += time.perf_counter() - t0
        if a == STOP_ACTION:                       # runtime-assurance halt: ends the episode as a "safe_stop"
            obs, r, done, info = env.safe_stop()
            total_r += r
            continue
        unsafe += ev.commanded_cell_unsafe(a)
        obs, r, done, info = env.step(a)
        total_r += r
        energy += info["energy_used"]
        collisions += info["event"].endswith("collision")
    d1 = _stat_snapshot(policy)
    ok = info["reason"] == "goal"
    return {"method": method, "preset": preset, "map": env.map_id, "success": int(ok), "reason": info["reason"],
            "steps": info["steps"], "reward": round(total_r, 3), "battery_left": env.battery, "energy_used": energy,
            "collisions": int(collisions), "attempted_unsafe": int(unsafe), "interventions": d1[1] - d0[1],
            "decisions": d1[0] - d0[0], "no_safe_action": d1[2] - d0[2], "fallback_steps": d1[3] - d0[3],
            "unc_alarms": d1[4] - d0[4], "ood_alarms": d1[5] - d0[5], "monitor_rejects": d1[6] - d0[6], "optimal_cost": ev.optimal_cost,
            "energy_ratio": (energy / ev.optimal_cost) if ok else float("nan"),
            "plan_ms": 1000.0 * t_dec / max(info["steps"], 1)}


def evaluate_method(policy, cfg_path, seeds, method: str, preset: str, out_csv=None):
    """Fresh env per call (same cfg, same seed list -> same episodes for every method). Returns (rows, summary)."""
    cfg = load_config(cfg_path)
    env, ev = make_env(cfg.env, 0)
    _attach(policy, env)
    rows = [run_episode_ext(env, ev, policy, s, method, preset) for s in seeds]
    summ = summarise(rows)
    n = len(rows)
    summ["reasons"]["safe_stop"] = sum(r["reason"] == "safe_stop" for r in rows)
    summ.update({"attempted_unsafe_per_episode": sum(r["attempted_unsafe"] for r in rows) / n,
                 "mean_energy_used": float(np.mean([r["energy_used"] for r in rows])),
                 "mean_plan_ms": float(np.mean([r["plan_ms"] for r in rows])),
                 "intervention_rate": (sum(r["interventions"] for r in rows) / max(sum(r["decisions"] for r in rows), 1))
                 if any(r["decisions"] for r in rows) else None})
    if out_csv:
        Path(out_csv).parent.mkdir(parents=True, exist_ok=True)
        with open(out_csv, "w", newline="") as f:
            w = csv.DictWriter(f, ROW_FIELDS)
            w.writeheader()
            w.writerows(rows)
    return rows, summ


def build_policy(kind: str, cfg: Config, ckpt: str | None = None, seed: int = 0):
    """kind: random | reactive | astar | dqn | dqn_shield | ppo | ppo_shield"""
    from src.policies.astar_battery import BatteryAwareAStar
    from src.policies.baseline_policies import RandomPolicy
    from src.policies.rule_shield import RuleShield
    from src.policies.sim32_heuristic import ReactiveExplorer
    if kind == "random":
        return RandomPolicy(seed)
    if kind == "reactive":
        return ReactiveExplorer(seed)
    if kind == "astar":
        return BatteryAwareAStar(nominal_energy=cfg.env.ref_energy_cost, seed=seed)
    if kind in ("dqn", "dqn_shield"):
        from src.agents.dqn_agent import DQNAgent
        probe, _ = make_env(cfg.env, 0)
        agent = DQNAgent(probe.obs_dim, probe.n_actions, cfg.dqn, seed=seed)
        agent.load(ckpt)
        base = GreedyAgentPolicy(agent, "dqn")
        return base if kind == "dqn" else RuleShield(base, nominal_energy=cfg.env.ref_energy_cost)
    if kind in ("ppo", "ppo_shield"):
        from src.agents.ppo_agent import PPOAgent
        probe, _ = make_env(cfg.env, 0)
        agent = PPOAgent(probe.obs_dim, probe.n_actions, cfg.ppo, seed=seed)
        agent.load(ckpt)
        base = GreedyAgentPolicy(agent, "ppo")  # greedy (argmax) deployment, as for DQN; q_values = logits
        return base if kind == "ppo" else RuleShield(base, nominal_energy=cfg.env.ref_energy_cost)
    raise ValueError(f"unknown method {kind!r}")
