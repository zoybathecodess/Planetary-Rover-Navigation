"""Amendment A3: action-conditioned OOD detector and its wiring (default system unchanged)."""
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import torch
import torch.nn as nn

from src.assurance.action_ood import MIN_CLASS, ActionConditionedOOD
from src.config import AssuranceConfig
from src.evaluation.experiment import VARIANTS, parse_method


def _member(seed):
    torch.manual_seed(seed)
    return SimpleNamespace(model=SimpleNamespace(net=nn.Sequential(nn.Linear(59, 16), nn.ReLU(), nn.Linear(16, 4))))


class TestActionOOD(unittest.TestCase):
    def setUp(self):
        self.ens = SimpleNamespace(members=[_member(0), _member(1)])
        rng = np.random.default_rng(0)
        self.X = rng.normal(0, 0.1, size=(2000, 59))
        self.A = rng.choice(4, size=2000, p=[0.45, 0.45, 0.07, 0.03])
        self.det = ActionConditionedOOD().bind(self.ens).fit(self.X, self.A)

    def test_shifted_inputs_score_higher(self):
        rng = np.random.default_rng(1)
        ind = np.mean([self.det.score(x, 0) for x in rng.normal(0, 0.1, size=(50, 59))])
        far = np.mean([self.det.score(x, 0) for x in rng.normal(2.0, 1.0, size=(50, 59))])
        self.assertGreater(far, 5 * ind)

    def test_small_classes_use_pooled_mean(self):
        self.assertLess(self.det.counts[3], MIN_CLASS)
        for k in range(2):
            np.testing.assert_allclose(self.det.mu[k, 3], self.det.mu[k, 2])   # both pooled

    def test_save_load_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            self.det.save(Path(d) / "a.npz")
            det2 = ActionConditionedOOD.load(Path(d) / "a.npz", self.ens)
        self.assertAlmostEqual(self.det.score(self.X[0], 1), det2.score(self.X[0], 1), places=10)

    def test_wiring(self):
        self.assertEqual(AssuranceConfig().ood_kind, "raw")
        self.assertEqual(parse_method("assured-aood@95")["variant"], "aood")
        for v, kw in VARIANTS.items():
            if not v.startswith("aood"):
                self.assertEqual(replace(AssuranceConfig(), **kw).ood_kind, "raw")


if __name__ == "__main__":
    unittest.main()
