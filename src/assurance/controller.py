"""Runtime-assurance controller: ensemble policy -> {uncertainty gate, OOD gate, safety monitor} -> accept | fallback | stop.

Decision per step (onboard information only: the observation and the env's public explored map):
  1. propose a = argmax of the ensemble's mean Q; u = std across members of Q[a]; s = windowed Mahalanobis score.
  2. reasons = monitor rules violated by a  +  "uncertainty" if u > tau_u  +  "ood" if s > tau_s.
  3. no reasons                      -> ACCEPT a.
  4. reasons                         -> FALLBACK: battery-aware A* ranks the moves; take the best one that passes the HARD
                                        monitor rules. If there is no energy-feasible route, or no ranked move passes -> STOP.
  `hold_steps` > 0 keeps the fallback in command for that many steps after an uncertainty/OOD trigger (default 0).
Every decision is returned as a record (and kept in `self.log` when `keep_log`), so interventions can be audited.
"""
from __future__ import annotations

from collections import Counter

import numpy as np

from src.assurance.layout import IDX_BATT, IDX_STEPS, STOP_ACTION
from src.assurance.monitor import SafetyMonitor
from src.assurance.ood import WindowedScore


class RuntimeAssuranceController:
    name = "assured"

    def __init__(self, ensemble, ood, fallback, cfg, tau_unc: float, tau_ood: float, nominal_energy=(1.0, 3.0, 5.0),
                 keep_log: bool = False):
        self.ens, self.ood, self.fb, self.cfg = ensemble, ood, fallback, cfg
        self.tau_unc, self.tau_ood = float(tau_unc), float(tau_ood)
        self.monitor = SafetyMonitor(cfg.slip_threshold, nominal_energy)
        self.win = WindowedScore(cfg.ood_window)
        self.keep_log, self.log = keep_log, []
        self._get_map, self._hold, self._t = None, 0, 0
        self.stats = {"decisions": 0, "interventions": 0, "no_safe_action": 0, "by_rule": Counter(),
                      "fallback": 0, "stops": 0, "unc_alarms": 0, "ood_alarms": 0, "monitor_rejects": 0}
        self.last_decision: dict = {}

    def attach(self, get_map, battery_capacity: float) -> None:
        self._get_map = get_map
        self.monitor.attach(battery_capacity)
        self.fb.attach(get_map, battery_capacity)

    def reset(self) -> None:
        self.win.reset(); self._hold = 0; self._t = 0

    def act(self, obs) -> int:
        if not np.all(np.isfinite(obs)):          # corrupted observation: no component can be trusted -> halt
            self.stats["decisions"] += 1; self.stats["interventions"] += 1; self.stats["stops"] += 1
            self.stats["no_safe_action"] += 1; self.stats["by_rule"]["invalid_observation"] += 1
            self.last_decision = {"t": self._t, "policy_action": None, "action": STOP_ACTION, "source": "stop",
                                  "reasons": ["invalid_observation"], "unc": None, "margin": None, "ood": None,
                                  "battery": None, "stop_cause": "invalid_observation", "route_energy_est": None}
            if self.keep_log:
                self.log.append(self.last_decision)
            self._t += 1
            return STOP_ACTION
        m = self._get_map()
        if float(obs[IDX_STEPS]) == 0.0:      # first decision of an episode (observation says so): clear per-episode state
            self.reset()
        q = self.ens.q_matrix(obs)
        a, unc, margin = self.ens.summarise(q)
        score = self.win.update(self.ood.score(obs, a) if getattr(self.ood, "needs_action", False) else self.ood.score(obs))
        reasons = self.monitor.check(obs, a, m) if self.cfg.use_monitor else []
        unc_alarm = bool(self.cfg.use_uncertainty and unc > self.tau_unc)
        ood_alarm = bool(self.cfg.use_ood and score > self.tau_ood)
        if unc_alarm:
            reasons.append("uncertainty")
        if ood_alarm:
            reasons.append("ood")
        if self.cfg.hold_steps and (unc_alarm or ood_alarm):
            self._hold = self.cfg.hold_steps
        elif self._hold > 0:
            self._hold -= 1
            reasons.append("hold")
        st = self.stats
        st["decisions"] += 1
        st["unc_alarms"] += unc_alarm; st["ood_alarms"] += ood_alarm
        st["monitor_rejects"] += any(r not in ("uncertainty", "ood", "hold") for r in reasons)
        source, final, cause, est = "policy", a, None, {}
        if reasons:
            st["interventions"] += 1
            for r in reasons:
                st["by_rule"][r] += 1
            final, source, cause, est = self._fallback(obs, m, a)
            st["fallback" if source == "fallback" else "stops"] += 1
            st["no_safe_action"] += source == "stop"
        self.last_decision = {"t": self._t, "policy_action": a, "action": final, "source": source, "reasons": reasons,
                              "unc": round(unc, 5), "margin": round(margin, 5), "ood": round(score, 4),
                              "battery": round(float(obs[IDX_BATT]) * self.monitor._capacity, 1), "stop_cause": cause,
                              "route_energy_est": None if "energy_to_goal" not in est else round(est["energy_to_goal"], 1)}
        if self.keep_log:
            self.log.append(self.last_decision)
        self._t += 1
        return final

    def _fallback(self, obs, m, policy_action):
        info = self.fb.analyse(obs, m)
        if not info["feasible"] and self.cfg.allow_stop:
            return STOP_ACTION, "stop", "infeasible_route", info
        for a in info["ranked"]:
            if not self.monitor.check(obs, a, m, hard_only=True):
                return a, "fallback", None, info
        if not self.cfg.allow_stop:      # ablation only: keep the best-ranked move (or the policy's) instead of halting
            return (info["ranked"][0] if info["ranked"] else policy_action), "fallback", None, info
        return STOP_ACTION, "stop", "all_moves_vetoed", info
