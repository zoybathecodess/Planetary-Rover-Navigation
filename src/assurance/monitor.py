"""Safety monitor: explicit, testable local rules over onboard information only (observation + explored map).

  invalid_action       the move would leave the map                                           (hard)
  obstacle_proximity   the target cell is believed blocked: seen in the 5x5 window, majority of past readings, or
                       proven by an earlier collision                                         (hard)
  battery_feasibility  entry energy (nominal table, from the reading) exceeds the battery, or battery after the move is
                       below the Manhattan distance left (>= 1 energy per step)               (hard)
  uncertain_movement   slip is believed likely (slip_estimate >= slip_threshold) AND a cell the rover could slide into
                       sideways (perpendicular to the move, from the CURRENT cell) is a believed obstacle or the map edge.
                       Judges trust in a COMMANDED move, so it applies to the policy action only (`hard_only=False`).
Rules are checked in this order and all violated rules are returned.
"""
from __future__ import annotations

import numpy as np

from src.assurance.layout import (DELTAS, IDX_BATT, IDX_SLIP, OBSTACLE_READING, R, W, WIN0, perpendicular)

RULES = ("invalid_action", "obstacle_proximity", "battery_feasibility", "uncertain_movement")


class SafetyMonitor:
    def __init__(self, slip_threshold: float = 0.15, nominal_energy=(1.0, 3.0, 5.0)):
        self.slip_threshold, self.nominal = float(slip_threshold), tuple(float(v) for v in nominal_energy)
        self._capacity = None

    def attach(self, battery_capacity: float) -> None:
        self._capacity = float(battery_capacity)

    @staticmethod
    def _blocked(obs, m, dr: int, dc: int, x: int, y: int, n: int) -> bool:
        tx, ty = x + dr, y + dc
        if not (0 <= tx < n and 0 <= ty < n):
            return True
        if float(obs[WIN0 + (R + dr) * W + (R + dc)]) >= OBSTACLE_READING or m.bumped[tx, ty]:
            return True
        b = m.obstacle_frac[tx, ty]
        return bool(not np.isnan(b) and b > 0.5)

    def check(self, obs, action: int, m, hard_only: bool = False) -> list[str]:
        n = m.seen.shape[0]
        x, y = int(round(obs[0] * (n - 1))), int(round(obs[1] * (n - 1)))
        gx, gy = x + int(round(obs[2] * (n - 1))), y + int(round(obs[3] * (n - 1)))
        dr, dc = DELTAS[action]
        tx, ty = x + dr, y + dc
        if not (0 <= tx < n and 0 <= ty < n):
            return ["invalid_action"]
        out = []
        if self._blocked(obs, m, dr, dc, x, y, n):
            out.append("obstacle_proximity")
        reading = float(obs[WIN0 + (R + dr) * W + (R + dc)])
        entry = 1.0 if reading >= OBSTACLE_READING else (self.nominal[0] if reading < 0.15 else self.nominal[1] if reading < 0.45 else self.nominal[2])
        battery = float(obs[IDX_BATT]) * self._capacity
        if entry > battery or battery - entry < abs(tx - gx) + abs(ty - gy):
            out.append("battery_feasibility")
        if not hard_only and float(obs[IDX_SLIP]) >= self.slip_threshold:
            if any(self._blocked(obs, m, pr, pc, x, y, n) for pr, pc in (DELTAS[a] for a in perpendicular(action))):
                out.append("uncertain_movement")
        return out
