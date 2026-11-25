"""Amendment A1 (H3): energy-blind fallback variant is wired correctly and leaves the default system untouched."""
import unittest
from dataclasses import replace

import numpy as np

from src.config import AssuranceConfig
from src.evaluation.experiment import VARIANTS, parse_method
from src.policies.astar_battery import BatteryAwareAStar, EnergyBlindAStar


class _Map:
    def __init__(self, n=8):
        self.seen = np.ones((n, n)); self.terrain_mean = np.zeros((n, n)); self.terrain_mean[:, 3] = 0.9   # rock column
        self.obstacle_frac = np.zeros((n, n)); self.visits = np.zeros((n, n)); self.bumped = np.zeros((n, n), bool)


def _obs(n=8, pos=(0, 0), goal=(0, 7), batt=0.02):
    o = np.zeros(59); o[0], o[1] = pos[0] / (n - 1), pos[1] / (n - 1)
    o[2], o[3] = (goal[0] - pos[0]) / (n - 1), (goal[1] - pos[1]) / (n - 1); o[4] = batt
    return o


class TestH3(unittest.TestCase):
    def test_variants_parse(self):
        self.assertEqual(parse_method("assured-fb_blind@95")["variant"], "fb_blind")
        self.assertEqual(VARIANTS["fb_blind_no_stop"], {"fallback": "energy_blind", "allow_stop": False})

    def test_default_fallback_is_battery_aware(self):
        self.assertEqual(AssuranceConfig().fallback, "battery")
        for v, kw in VARIANTS.items():
            if not v.startswith("fb_blind"):
                self.assertEqual(replace(AssuranceConfig(), **kw).fallback, "battery")

    def test_blind_ignores_terrain_energy_and_feasibility(self):
        m, o = _Map(), _obs()
        aware, blind = BatteryAwareAStar(), EnergyBlindAStar()
        for p in (aware, blind):
            p.attach(lambda: m, 250.0)
        ca, _, _ = aware._grids(m, 0.5); cb, _, _ = blind._grids(m, 0.5)
        self.assertEqual(ca[0, 3], 5.0); self.assertEqual(cb[0, 3], 1.0)
        self.assertFalse(aware.analyse(o, m)["feasible"])        # 5 J battery, route needs > 5
        self.assertTrue(blind.analyse(o, m)["feasible"])


if __name__ == "__main__":
    unittest.main()
