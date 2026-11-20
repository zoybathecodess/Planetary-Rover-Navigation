"""Task 4: ensemble, OOD detector, safety monitor, fallback, controller, safe-stop, logs, information boundary."""
import ast
import importlib.util
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

import numpy as np

from src.assurance import layout as L
from src.assurance.controller import RuntimeAssuranceController
from src.assurance.ensemble import EnsemblePolicy
from src.assurance.monitor import SafetyMonitor
from src.assurance.ood import MahalanobisOOD, WindowedScore
from src.config import AssuranceConfig, Config, DQNConfig
from src.environment import terrain as T
from src.environment.advanced_env import FEATURES
from src.evaluation.evaluator import make_env
from src.evaluation.harness import evaluate_method, run_episode_ext
from src.policies.astar_battery import BatteryAwareAStar
from tests.test_task3 import blank_map, cfg32, fake_obs, flat, known_map, quiet

ROOT = Path(__file__).resolve().parents[1]
HAS_TORCH = importlib.util.find_spec("torch") is not None
ACFG = AssuranceConfig()


class StubEns:
    """Ensemble stand-in: fixed per-member Q rows."""
    def __init__(self, q): self.q = np.asarray(q, float)
    def q_matrix(self, obs): return self.q
    summarise = staticmethod(EnsemblePolicy.summarise)


def free_window():
    return np.full((5, 5), 0.2)


def controller(q, ood_score=1.0, tau_unc=1.0, tau_ood=3.0, grid=None, cfg=ACFG, battery=1.0, pos=(10, 10), goal=(20, 20), window=None):
    ood = MahalanobisOOD(); ood.mu = np.zeros(len(L.OOD_FEATURES)); ood.prec = np.eye(len(L.OOD_FEATURES))
    ood.score = lambda obs: ood_score
    c = RuntimeAssuranceController(StubEns(q), ood, BatteryAwareAStar(), cfg, tau_unc, tau_ood, keep_log=True)
    m = known_map(flat() if grid is None else grid)
    c.attach(lambda: m, 250)
    obs = fake_obs(pos, goal, battery, window=free_window() if window is None else window)
    obs[L.IDX_STEPS] = 0.1
    return c, obs


class TestLayout(unittest.TestCase):
    def test_indices_match_env_features(self):
        self.assertEqual(FEATURES[L.IDX_SLIP], "slip_estimate")
        self.assertEqual(FEATURES[L.IDX_CONF], "sensor_confidence")
        self.assertEqual(FEATURES[L.IDX_BATT], "battery_ratio")
        self.assertEqual(FEATURES[L.IDX_STEPS], "steps_ratio")
        self.assertEqual(FEATURES[L.WIN0], "win_r-2_c-2")
        self.assertEqual(FEATURES[L.VIS0], "visits_r-2_c-2")
        self.assertNotIn(0, L.OOD_FEATURES); self.assertNotIn(L.IDX_COV, L.OOD_FEATURES)
        self.assertTrue(all(i < L.VIS0 for i in L.OOD_FEATURES))


class TestSafeStop(unittest.TestCase):
    def test_safe_stop_is_terminal_free_and_not_success(self):
        env, ev = make_env(quiet(), 0)
        env.reset(seed=1)
        b = env.battery
        obs, r, done, info = env.safe_stop()
        self.assertTrue(done); self.assertEqual((r, info["reason"], info["energy_used"], env.battery), (0.0, "safe_stop", 0, b))
        with self.assertRaises(RuntimeError):
            env.safe_stop()
        with self.assertRaises(RuntimeError):
            env.step(0)

    def test_harness_maps_stop_action_and_never_counts_success(self):
        env, ev = make_env(quiet(), 0)

        class Stopper:
            stats = None
            def act(self, obs): return L.STOP_ACTION
        row = run_episode_ext(env, ev, Stopper(), 3)
        self.assertEqual((row["reason"], row["success"], row["steps"], row["energy_used"]), ("safe_stop", 0, 0, 0))
        self.assertEqual(row["attempted_unsafe"], 0)


class TestMonitor(unittest.TestCase):
    def mon(self, **kw):
        m = SafetyMonitor(**kw); m.attach(250); return m

    def test_accepts_clear_move(self):
        self.assertEqual(self.mon().check(fake_obs((10, 10), (20, 20), window=free_window()), 1, known_map(flat())), [])

    def test_invalid_action_off_map(self):
        self.assertEqual(self.mon().check(fake_obs((0, 5), (20, 20), window=free_window()), 0, known_map(flat())), ["invalid_action"])

    def test_obstacle_seen_in_window_and_in_memory_and_bumped(self):
        w = free_window(); w[3, 2] = 1.0   # cell below
        self.assertIn("obstacle_proximity", self.mon().check(fake_obs((10, 10), (20, 20), window=w), 1, known_map(flat())))
        g = flat(); g[11, 10] = T.OBSTACLE
        self.assertIn("obstacle_proximity", self.mon().check(fake_obs((10, 10), (20, 20), window=free_window()), 1, known_map(g)))
        bm = known_map(flat()); bm.bumped[11, 10] = True
        self.assertIn("obstacle_proximity", self.mon().check(fake_obs((10, 10), (20, 20), window=free_window()), 1, bm))

    def test_battery_feasibility(self):
        o = fake_obs((10, 10), (20, 20), battery_ratio=19 / 250, window=free_window())   # 19 left, Manhattan 20 -> after move 18 < 19
        self.assertIn("battery_feasibility", self.mon().check(o, 1, known_map(flat())))
        o = fake_obs((10, 10), (20, 20), battery_ratio=0.5, window=free_window())
        self.assertNotIn("battery_feasibility", self.mon().check(o, 1, known_map(flat())))

    def test_uncertain_movement_needs_slip_and_a_side_hazard_and_is_policy_only(self):
        g = flat(); g[10, 11] = T.OBSTACLE         # moving down (1): sideways cells are (10,9) and (10,11)
        w = free_window(); w[2, 3] = 1.0
        o = fake_obs((10, 10), (20, 20), window=w); o[L.IDX_SLIP] = 0.30
        self.assertEqual(self.mon().check(o, 1, known_map(g)), ["uncertain_movement"])
        self.assertEqual(self.mon().check(o, 1, known_map(g), hard_only=True), [])
        o[L.IDX_SLIP] = 0.05
        self.assertEqual(self.mon().check(o, 1, known_map(g)), [])
        o[L.IDX_SLIP] = 0.30
        self.assertEqual(self.mon().check(fake_obs((10, 10), (20, 20), window=free_window()) + 0 * o, 1, known_map(flat())), [])


class TestOOD(unittest.TestCase):
    def data(self, n, shift=0.0, seed=0):
        r = np.random.default_rng(seed)
        X = np.zeros((n, 59)); X[:, 9:34] = r.normal(0.3, 0.1, (n, 25)) + shift; X[:, 6] = r.normal(0.1, 0.02, n)
        X[:, 7] = r.uniform(0.5, 1, n); X[:, 4] = r.uniform(0.3, 1, n); X[:, 5] = 1 - X[:, 4] + r.normal(0, .02, n)
        return X

    def test_in_distribution_scores_near_one_and_shift_is_higher(self):
        d = MahalanobisOOD().fit(self.data(4000))
        idv, sh = d.scores(self.data(1000, seed=1)), d.scores(self.data(1000, shift=0.15, seed=2))
        self.assertAlmostEqual(float(idv.mean()), 1.0, delta=0.3)
        self.assertGreater(float(sh.mean()), 3 * float(idv.mean()))

    def test_percentile_threshold_sets_the_false_alarm_rate(self):
        d = MahalanobisOOD().fit(self.data(4000))
        cal, held = d.scores(self.data(3000, seed=3)), d.scores(self.data(3000, seed=4))
        for p in (90, 99):
            self.assertAlmostEqual(float((held > np.percentile(cal, p)).mean()), 1 - p / 100, delta=0.015)

    def test_score_matches_batch_and_roundtrip_and_ignores_position(self):
        X = self.data(600); d = MahalanobisOOD().fit(X)
        self.assertAlmostEqual(d.score(X[5]), float(d.scores(X)[5]), places=9)
        with tempfile.TemporaryDirectory() as t:
            d.save(Path(t) / "o.npz"); d2 = MahalanobisOOD.load(Path(t) / "o.npz")
        self.assertAlmostEqual(d2.score(X[7]), d.score(X[7]), places=9)
        y = X[9].copy(); y[[0, 1, 2, 3, L.IDX_COV]] = 0.9; y[L.VIS0:] = 5
        self.assertAlmostEqual(d.score(y), d.score(X[9]), places=9)

    def test_fit_needs_enough_data_and_window_smooths(self):
        with self.assertRaises(ValueError):
            MahalanobisOOD().fit(self.data(50))
        w = WindowedScore(3)
        self.assertEqual([w.update(v) for v in (3, 0, 0, 0)], [3, 1.5, 1, 0])


@unittest.skipUnless(HAS_TORCH, "torch not installed")
class TestEnsemble(unittest.TestCase):
    def setUp(self):
        import torch
        torch.set_num_threads(1)
        self.cfg = Config(env=cfg32(), dqn=DQNConfig(hidden=(16,), prior_scale=10.0, prior_hidden=(16,), bootstrap=True))
        self.env, _ = make_env(self.cfg.env, 0)

    def agent(self, seed):
        from src.agents.ensemble_member import EnsembleMemberDQN
        return EnsembleMemberDQN(self.env.obs_dim, self.env.n_actions, self.cfg.dqn, seed=seed)

    def test_members_differ_and_prior_is_frozen_and_checkpointed(self):
        a, b = self.agent(1), self.agent(2)
        o = self.env.reset(seed=1)
        self.assertGreater(float(np.abs(a.q_values(o) - b.q_values(o)).max()), 0.1)   # random prior => diversity at init
        before = [p.detach().clone() for n, p in a.model.named_parameters() if "prior" in n]
        r = np.random.default_rng(0)
        for _ in range(200):
            a.buffer.add(r.normal(size=self.env.obs_dim), int(r.integers(4)), float(r.normal()), r.normal(size=self.env.obs_dim), False)
        for _ in range(20):
            a.learn()
        self.assertGreater(a.train_step, 0)
        after = [p.detach().clone() for n, p in a.model.named_parameters() if "prior" in n]
        self.assertTrue(all(np.array_equal(x.numpy(), y.numpy()) for x, y in zip(before, after)))
        self.assertFalse(any(p.requires_grad for n, p in a.model.named_parameters() if "prior" in n))
        with tempfile.TemporaryDirectory() as t:
            a.save(str(Path(t) / "m.pt")); c = self.agent(99); c.load(str(Path(t) / "m.pt"))
        np.testing.assert_allclose(a.q_values(o), c.q_values(o), rtol=1e-6)

    def test_bootstrap_weights_are_poisson_one(self):
        from src.agents.ensemble_member import BootstrapReplayBuffer
        b = BootstrapReplayBuffer(5000, self.env.obs_dim, 3, True)
        s = np.zeros(self.env.obs_dim)
        for _ in range(4000):
            b.add(s, 0, 0.0, s, False)
        w = b.w[:4000]
        off = BootstrapReplayBuffer(10, 4, 0, False)
        off.add(np.zeros(4), 0, 0., np.zeros(4), False)
        self.assertEqual(float(off.w[0]), 1.0)
        self.assertAlmostEqual(float(w.mean()), 1.0, delta=0.08)
        self.assertAlmostEqual(float((w == 0).mean()), np.exp(-1), delta=0.04)

    def test_summarise_picks_mean_argmax_and_reports_std_of_that_action(self):
        q = np.array([[1, 5, 2, 0], [1, 7, 2, 0], [1, 3, 2, 0.]])
        a, u, margin = EnsemblePolicy.summarise(q)
        self.assertEqual(a, 1); self.assertAlmostEqual(u, 2.0); self.assertAlmostEqual(margin, 3.0)
        with self.assertRaises(ValueError):
            EnsemblePolicy([object()])


class TestFallbackRanking(unittest.TestCase):
    def test_ranked_first_move_matches_straight_corridor_and_avoids_wall(self):
        g = flat(); g[11, 10] = T.OBSTACLE
        p = BatteryAwareAStar(); m = known_map(g); p.attach(lambda: m, 250)
        info = p.analyse(fake_obs((10, 10), (10, 20), window=free_window()), m)
        self.assertEqual(info["ranked"][0], 3)                  # right, toward the goal
        self.assertEqual(info["ranked"][-1], 1)                 # believed-blocked cell is a soft wall: ranked last (monitor vetoes it)
        self.assertTrue(info["feasible"])

    def test_infeasible_when_battery_cannot_cover_cheapest_route(self):
        p = BatteryAwareAStar(); m = known_map(flat()); p.attach(lambda: m, 250)
        self.assertFalse(p.analyse(fake_obs((0, 0), (30, 30), battery_ratio=40 / 250, window=free_window()), m)["feasible"])
        self.assertTrue(p.analyse(fake_obs((0, 0), (30, 30), battery_ratio=0.9, window=free_window()), m)["feasible"])


class TestController(unittest.TestCase):
    GOOD = [[0, 9, 1, 0], [0, 9.1, 1, 0], [0, 8.9, 1, 0]]       # picks action 1 (down), members agree

    def test_accept_when_everything_is_quiet(self):
        c, o = controller(self.GOOD)
        self.assertEqual(c.act(o), 1)
        d = c.last_decision
        self.assertEqual((d["source"], d["reasons"], d["policy_action"]), ("policy", [], 1))
        self.assertEqual(c.stats["interventions"], 0)

    def test_reject_on_uncertainty_and_fall_back(self):
        c, o = controller([[0, 2, 1, 0], [0, 9, 1, 0], [0, 5, 1, 0]], tau_unc=1.0)
        a = c.act(o)
        self.assertEqual(c.last_decision["source"], "fallback"); self.assertIn("uncertainty", c.last_decision["reasons"])
        self.assertIn(a, (1, 3))                                  # toward (20,20) from (10,10)
        self.assertEqual(c.stats["unc_alarms"], 1)

    def test_reject_on_ood_and_fall_back(self):
        c, o = controller(self.GOOD, ood_score=9.0, tau_ood=3.0)
        c.act(o)
        self.assertEqual((c.last_decision["source"], c.last_decision["reasons"]), ("fallback", ["ood"]))

    def test_monitor_veto_of_an_obstacle_action(self):
        g = flat(); g[11, 10] = T.OBSTACLE
        w = free_window(); w[3, 2] = 1.0
        c, o = controller(self.GOOD, grid=g, window=w)
        a = c.act(o)
        self.assertNotEqual(a, 1); self.assertIn("obstacle_proximity", c.last_decision["reasons"])
        self.assertEqual(c.last_decision["source"], "fallback")

    def test_stop_when_no_energy_feasible_route(self):
        c, o = controller(self.GOOD, ood_score=9.0, battery=45 / 250, pos=(0, 0), goal=(30, 30))
        self.assertEqual(c.act(o), L.STOP_ACTION)
        self.assertEqual(c.last_decision["source"], "stop"); self.assertEqual(c.stats["stops"], 1)

    def test_stop_on_energy_infeasible_route_that_passes_every_local_rule(self):
        # all rock (5 energy/cell): Manhattan bound is fine (100 left, 62 to go) but the real route costs ~310
        c, o = controller(self.GOOD, ood_score=9.0, battery=100 / 250, pos=(0, 0), goal=(31, 31), grid=flat(fill=T.ROCK),
                          window=np.full((5, 5), 0.6))
        self.assertEqual(c.monitor.check(o, 1, c._get_map(), hard_only=True), [])
        self.assertEqual(c.act(o), L.STOP_ACTION)
        self.assertEqual(c.last_decision["source"], "stop")

    def test_stop_when_every_move_is_vetoed(self):
        g = flat(); g[9, 10] = g[11, 10] = g[10, 9] = g[10, 11] = T.OBSTACLE
        c, o = controller(self.GOOD, grid=g, ood_score=9.0)
        self.assertEqual(c.act(o), L.STOP_ACTION)

    def test_ablation_switches_and_hold(self):
        c, o = controller(self.GOOD, ood_score=9.0, cfg=replace(ACFG, use_ood=False))
        self.assertEqual(c.act(o), 1)
        c, o = controller(self.GOOD, ood_score=9.0, cfg=replace(ACFG, hold_steps=2))
        c.act(o); c.win.reset(); c.ood.score = lambda obs: 1.0
        c.act(o); self.assertEqual(c.last_decision["reasons"], ["hold"])

    def test_log_records_every_decision_with_fields(self):
        c, o = controller(self.GOOD, ood_score=9.0)
        c.act(o); c.act(o)
        self.assertEqual(len(c.log), 2)
        self.assertEqual(set(c.log[0]), {"t", "policy_action", "action", "source", "reasons", "unc", "margin", "ood"})
        self.assertEqual(c.stats["decisions"], 2)

    def test_per_episode_state_resets_from_the_observation(self):
        c, o = controller(self.GOOD)
        c.win.update(100.0); o[L.IDX_STEPS] = 0.0
        c.act(o)
        self.assertLess(c.last_decision["ood"], 2.0)


class TestEndToEnd(unittest.TestCase):
    def test_assured_controller_with_hand_made_ensemble_runs_whole_episodes_and_is_deterministic(self):
        class GreedyGoal:
            """Heuristic 'members' that disagree a bit: used to exercise the full loop without training."""
            def q_matrix(self, obs):
                g = np.array([-obs[2], obs[2], -obs[3], obs[3]])
                return np.stack([g + 0.01 * k * np.arange(4) for k in range(3)])
            summarise = staticmethod(EnsemblePolicy.summarise)
        def run():
            ood = MahalanobisOOD(); ood.mu = np.zeros(len(L.OOD_FEATURES)); ood.prec = np.eye(len(L.OOD_FEATURES)); ood.score = lambda o: 1.0
            c = RuntimeAssuranceController(GreedyGoal(), ood, BatteryAwareAStar(), ACFG, 10.0, 5.0, keep_log=True)
            with tempfile.TemporaryDirectory() as t:
                cfgp = Path(t) / "c.yaml"; cfgp.write_text((ROOT / "configs/sim32_id.yaml").read_text())
                return evaluate_method(c, cfgp, range(10000, 10004), "assured", "id")
        r1, s1 = run(); r2, s2 = run()
        self.assertEqual([(r["reason"], r["steps"]) for r in r1], [(r["reason"], r["steps"]) for r in r2])
        self.assertTrue(all(r["reason"] in ("goal", "battery_depleted", "timeout", "safe_stop") for r in r1))
        self.assertIn("safe_stop", s1["reasons"])


class TestInformationBoundary(unittest.TestCase):
    BANNED = ("src.evaluation", "procgen", "terrain")
    PRIVATE = ("_world", "_slip", "_lut", "ground_truth", "optimal_cost", "true_slip", "true_energy")

    def test_assurance_modules_import_no_ground_truth_and_touch_no_private_env_state(self):
        files = list((ROOT / "src/assurance").glob("*.py"))
        self.assertGreaterEqual(len(files), 6)
        for f in files:
            tree = ast.parse(f.read_text())
            for node in ast.walk(tree):
                mods = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or ""] if isinstance(node, ast.ImportFrom) else []
                for m in mods:
                    self.assertFalse(any(b in m for b in self.BANNED), f"{f.name} imports {m}")
                if isinstance(node, ast.Attribute):
                    self.assertNotIn(node.attr, self.PRIVATE, f"{f.name} uses {node.attr}")

    def test_controller_only_receives_obs_and_public_map(self):
        import inspect
        self.assertEqual(list(inspect.signature(RuntimeAssuranceController.act).parameters), ["self", "obs"])
        self.assertEqual(list(inspect.signature(RuntimeAssuranceController.attach).parameters), ["self", "get_map", "battery_capacity"])


if __name__ == "__main__":
    unittest.main()
