"""Battery-aware A* over the EXPLORED map (Task 3 baseline). Onboard information only.

Plans on `explored_map()` (what the rover has sensed/touched) plus its own position, goal offset and battery.
It never sees the true grid. Every cell gets an explicit expected cost:

  known free cell      nominal energy of its estimated terrain class (normal/sand/rock = documented nominal table)
  UNKNOWN cell         `unknown_energy` + a risk premium that GROWS as the battery drains (less reserve = less gambling)
  believed obstacle    soft wall (`obstacle_penalty`): a false detection cannot deadlock the planner; a collision later
                       proves it (`bumped`) and the cell becomes a hard wall
  revisited cell       small `visit_penalty` per prior visit (breaks ping-pong loops caused by slips / sensor noise)

It replans every step. `last_plan` records the estimate so the Task-4 monitor/logs can use it.
Nominal energies are the rover's DOCUMENTED estimates: under a dynamics shift the true costs differ and A* is not told.
"""
from __future__ import annotations

import heapq

import numpy as np

_DELTAS = ((-1, 0), (1, 0), (0, -1), (0, 1))  # same action convention as the env (defined locally on purpose)


class BatteryAwareAStar:
    name = "battery_astar"

    def __init__(self, nominal_energy=(1.0, 3.0, 5.0), unknown_energy: float = 2.0, unknown_risk: float = 1.0,
                 risk_battery_gain: float = 2.0, obstacle_penalty: float = 40.0, visit_penalty: float = 0.3,
                 feasibility_margin: float = 1.0, seed: int = 0):
        if min(nominal_energy) < 1 or unknown_energy < 1:
            raise ValueError("all expected cell costs must be >= 1 (keeps the Manhattan heuristic admissible)")
        self.nominal = tuple(float(v) for v in nominal_energy)
        self.unknown_energy, self.unknown_risk, self.risk_gain = unknown_energy, unknown_risk, risk_battery_gain
        self.obstacle_penalty, self.visit_penalty, self.margin = obstacle_penalty, visit_penalty, feasibility_margin
        self.rng = np.random.default_rng(seed)
        self._get_map, self._capacity = None, None
        self.last_plan: dict = {}

    def attach(self, get_map, battery_capacity: float) -> None:
        """`get_map` = the env's public `explored_map` (onboard). `battery_capacity` = the rover's nominal capacity."""
        self._get_map, self._capacity = get_map, float(battery_capacity)

    # ------------------------------------------------------------------ cost model
    def _grids(self, m, battery_ratio: float):
        known = m.seen > 0
        tm = m.terrain_mean
        e = np.where(np.nan_to_num(tm, nan=0.0) < 0.15, self.nominal[0],
                     np.where(np.nan_to_num(tm, nan=0.0) < 0.45, self.nominal[1], self.nominal[2]))
        of = np.nan_to_num(m.obstacle_frac, nan=0.0)
        soft = known & (of > 0.5)
        premium = self.unknown_risk * (1.0 + self.risk_gain * (1.0 - battery_ratio))
        energy = np.where(known, e, self.unknown_energy)           # pure energy estimate (for the feasibility check)
        cost = np.where(known, e, self.unknown_energy + premium)   # planning cost
        cost = np.where(soft, self.obstacle_penalty, cost) + self.visit_penalty * np.minimum(m.visits, 3)
        cost = np.where(m.bumped, np.inf, cost)
        return cost, np.where(soft, 1.0, energy), ~known

    def _astar(self, cost, start, goal):
        n = cost.shape[0]
        g = np.full((n, n), np.inf)
        g[start] = 0.0
        parent = {}
        h = lambda p: abs(p[0] - goal[0]) + abs(p[1] - goal[1])  # noqa: E731  (every cell costs >= 1)
        heap = [(h(start), 0.0, start)]
        while heap:
            _, gc, cur = heapq.heappop(heap)
            if cur == goal:
                path = [cur]
                while cur != start:
                    cur = parent[cur]
                    path.append(cur)
                return path[::-1], gc
            if gc > g[cur]:
                continue
            for dr, dc in _DELTAS:
                nxt = (cur[0] + dr, cur[1] + dc)
                if 0 <= nxt[0] < n and 0 <= nxt[1] < n and np.isfinite(cost[nxt]):
                    ng = gc + cost[nxt]
                    if ng < g[nxt]:
                        g[nxt] = ng
                        parent[nxt] = cur
                        heapq.heappush(heap, (ng + h(nxt), ng, nxt))
        return None, np.inf

    @staticmethod
    def _cost_to_goal(cost, goal):
        """Reverse Dijkstra: cheapest total entering-cost from every cell to `goal` (inf where unreachable)."""
        n = cost.shape[0]
        togo = np.full((n, n), np.inf)
        togo[goal] = 0.0
        heap = [(0.0, goal)]
        while heap:
            c, cur = heapq.heappop(heap)
            if c > togo[cur]:
                continue
            for dr, dc in _DELTAS:
                p = (cur[0] + dr, cur[1] + dc)       # p -> cur costs cost[cur]
                if 0 <= p[0] < n and 0 <= p[1] < n and np.isfinite(cost[cur]):
                    nc = c + cost[cur]
                    if nc < togo[p]:
                        togo[p] = nc
                        heapq.heappush(heap, (nc, p))
        return togo

    def analyse(self, obs, m) -> dict:
        """For the runtime-assurance fallback: every first move ranked by (cost of entering the neighbour + cost-to-go),
        plus whether an ENERGY-feasible route exists (cheapest estimated route energy * margin <= battery)."""
        n = m.seen.shape[0]
        pos = (int(round(obs[0] * (n - 1))), int(round(obs[1] * (n - 1))))
        goal = (pos[0] + int(round(obs[2] * (n - 1))), pos[1] + int(round(obs[3] * (n - 1))))
        cost, energy, unknown = self._grids(m, float(obs[4]))
        togo = self._cost_to_goal(cost, goal)
        etogo = self._cost_to_goal(np.where(m.bumped, np.inf, energy), goal)
        scores = {}
        for a, (dr, dc) in enumerate(_DELTAS):
            nb = (pos[0] + dr, pos[1] + dc)
            if 0 <= nb[0] < n and 0 <= nb[1] < n and np.isfinite(cost[nb]) and np.isfinite(togo[nb]):
                scores[a] = float(cost[nb] + togo[nb])
        battery = float(obs[4]) * self._capacity
        e_min = float(etogo[pos])
        return {"ranked": sorted(scores, key=lambda a: (scores[a], a)), "scores": scores, "energy_to_goal": e_min,
                "battery": battery, "feasible": bool(np.isfinite(e_min) and e_min * self.margin <= battery)}

    # ------------------------------------------------------------------ policy
    def act(self, obs) -> int:
        if self._get_map is None:
            raise RuntimeError("call attach(env.explored_map, env.max_battery) before act()")
        m = self._get_map()
        n = m.seen.shape[0]
        pos = (int(round(obs[0] * (n - 1))), int(round(obs[1] * (n - 1))))
        goal = (pos[0] + int(round(obs[2] * (n - 1))), pos[1] + int(round(obs[3] * (n - 1))))
        cost, energy, unknown = self._grids(m, float(obs[4]))
        path, total = self._astar(cost, pos, goal)
        battery = float(obs[4]) * self._capacity
        if path is None or len(path) < 2:
            self.last_plan = {"path": None, "cost": np.inf, "energy_est": np.inf, "feasible": False, "n_unknown": 0}
            return int(self.rng.integers(4))
        cells = path[1:]
        e_est = float(sum(energy[c] for c in cells))
        self.last_plan = {"path": path, "cost": float(total), "energy_est": e_est,
                          "feasible": e_est * self.margin <= battery, "n_unknown": int(sum(unknown[c] for c in cells))}
        step = (path[1][0] - pos[0], path[1][1] - pos[1])
        return _DELTAS.index(step)
