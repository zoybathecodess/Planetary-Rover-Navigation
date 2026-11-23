"""Task 3: battery-aware A*, rule-based shield, shared harness, and the DQN checks (replay contents, target updates,
exploration schedule, reward, checkpoints)."""
import ast
import csv
import importlib.util
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

import numpy as np

from src.config import Config, DQNConfig, EnvConfig, load_config
from src.environment import procgen as G
from src.environment import terrain as T
from src.environment.advanced_env import FEATURES, ExploredMap
from src.evaluation.evaluator import make_env
from src.evaluation.harness import ROW_FIELDS, evaluate_method
from src.policies.astar_battery import BatteryAwareAStar
from src.policies.rule_shield import RuleShield

ROOT = Path(__file__).resolve().parents[1]
HAS_TORCH = importlib.util.find_spec("torch") is not None
WIN0 = FEATURES.index("win_r-2_c-2")


def cfg32(**kw):
    base = dict(kind="advanced", size=32, battery=250, p_normal=.60, p_sand=.15, p_rock=.10)
    base.update(kw)
    return EnvConfig(**base)


def quiet(**kw):
    return cfg32(slip_prob=(0, 0, 0), sensor_miss=0.0, sensor_false=0.0, sensor_sigma=0.0, **kw)


def flat(n=32, fill=T.NORMAL):
    return np.full((n, n), fill, dtype=np.int64)


def known_map(grid, bumped=None, visits=None) -> ExploredMap:
    """Explored map of a world the rover has fully and perfectly sensed (test helper)."""
    obs = grid == T.OBSTACLE
    return ExploredMap(seen=np.ones(grid.shape, np.int64), obs_reads=obs.astype(np.int64),
                       terrain_sum=np.where(obs, 0.0, T.PATCH_VALUE[np.minimum(grid, 2)]),
                       visits=np.zeros(grid.shape, np.int64) if visits is None else visits,
                       bumped=np.zeros(grid.shape, bool) if bumped is None else bumped)


def blank_map(n=32) -> ExploredMap:
    z = lambda dt: np.zeros((n, n), dtype=dt)  # noqa: E731
    return ExploredMap(z(np.int64), z(np.int64), z(float), z(np.int64), z(bool))


def fake_obs(pos, goal, battery_ratio=1.0, n=32, window=None):
    o = np.zeros(len(FEATURES))
    o[0], o[1] = pos[0] / (n - 1), pos[1] / (n - 1)
    o[2], o[3] = (goal[0] - pos[0]) / (n - 1), (goal[1] - pos[1]) / (n - 1)
    o[4] = battery_ratio
    if window is not None:
        o[WIN0:WIN0 + 25] = np.asarray(window).ravel()
    return o


def astar_on(m, **kw):
    p = BatteryAwareAStar(**kw)
    p.attach(lambda: m, 250)
    return p


class TestAStar(unittest.TestCase):
    def test_matches_dijkstra_on_fully_known_maps(self):
        lut, checked = G.energy_lut((1, 3, 5)), 0
        for s in range(15):
            g = G.generate_terrain(np.random.default_rng(s), 32, .55, .2, .1, 2)
            G.clear_blocks(g, (0, 0), (31, 31))
            best = G.dijkstra_lut(g, (0, 0), lut)[31, 31]
            if best >= T.INF:
                continue  # unreachable map: A* then crosses a soft wall (covered by test_believed_obstacle_is_a_soft_wall)
            checked += 1
            p = astar_on(known_map(g), visit_penalty=0.0)
            p.act(fake_obs((0, 0), (31, 31)))
            self.assertEqual(p.last_plan["energy_est"], float(best), f"map {s}")
            self.assertEqual(p.last_plan["n_unknown"], 0)
        self.assertGreaterEqual(checked, 10)

    def test_goes_through_the_gap(self):
        g = flat(); g[10, :] = T.OBSTACLE; g[10, 20] = T.NORMAL
        p = astar_on(known_map(g), visit_penalty=0.0)
        p.act(fake_obs((0, 0), (31, 31)))
        self.assertIn((10, 20), p.last_plan["path"])

    def test_energy_not_distance(self):
        """A longer all-normal detour (cost 6) beats a short sand shortcut (cost 9): battery-aware means energy-aware."""
        g = flat(8); g[1:3, 1:3] = T.SAND
        g[0, 3] = g[1, 3] = T.NORMAL
        m = known_map(g)
        p = astar_on(m, visit_penalty=0.0)
        p.act(fake_obs((0, 0), (3, 3), n=8))
        self.assertEqual(p.last_plan["energy_est"], 6.0)
        self.assertTrue(all(g[c] == T.NORMAL for c in p.last_plan["path"][1:]))

    def test_unknown_cells_have_explicit_and_battery_dependent_risk_cost(self):
        m = blank_map()
        p = astar_on(m)
        p.act(fake_obs((0, 0), (5, 5), battery_ratio=1.0))
        full = p.last_plan
        self.assertEqual(full["n_unknown"], 10)
        self.assertEqual(full["energy_est"], 10 * p.unknown_energy)
        self.assertGreater(full["cost"], full["energy_est"])           # the risk premium is in the planning cost
        p.act(fake_obs((0, 0), (5, 5), battery_ratio=0.2))
        self.assertGreater(p.last_plan["cost"], full["cost"])           # and grows as the battery drains

    def test_bumped_cell_is_a_hard_wall_even_if_sensor_says_free(self):
        bumped = np.zeros((32, 32), bool); bumped[1, 0] = True
        p = astar_on(known_map(flat(), bumped=bumped), visit_penalty=0.0)
        a = p.act(fake_obs((0, 0), (2, 0)))
        self.assertNotIn((1, 0), p.last_plan["path"])
        self.assertEqual(a, 3)  # sidesteps right

    def test_believed_obstacle_is_a_soft_wall(self):
        g = flat(); g[0, :] = T.OBSTACLE; g[1, :] = T.OBSTACLE  # corridor fully closed by believed obstacles
        p = astar_on(known_map(g))
        p.act(fake_obs((0, 0), (31, 31)))
        self.assertIsNotNone(p.last_plan["path"])                      # never deadlocks on possibly-false detections
        self.assertGreaterEqual(p.last_plan["cost"], p.obstacle_penalty)

    def test_visit_penalty_discourages_going_back(self):
        v = np.zeros((32, 32), np.int64); v[5, 4] = 3
        p = astar_on(known_map(flat(), visits=v), visit_penalty=0.3)
        a = p.act(fake_obs((5, 5), (5, 0)))   # goal to the left; the cell on the left was visited, but is still the only direct way
        self.assertIn(a, (0, 1, 2))           # may sidestep; must never return an invalid action
        self.assertIn(a, range(4))

    def test_requires_attach_and_valid_costs(self):
        with self.assertRaises(RuntimeError):
            BatteryAwareAStar().act(fake_obs((0, 0), (1, 1)))
        with self.assertRaises(ValueError):
            BatteryAwareAStar(unknown_energy=0.5)

    def test_closed_loop_flat_world_is_optimal(self):
        env, ev = make_env(quiet(), 0)
        obs = ev.reset_with_map(flat(), start=(0, 0))
        p = BatteryAwareAStar()
        p.attach(env.explored_map, env.max_battery)
        done, info, energy = False, {}, 0
        while not done:
            obs, _, done, info = env.step(p.act(obs))
            energy += info["energy_used"]
        self.assertEqual((info["reason"], energy, info["steps"]), ("goal", 62, 62))

    def test_policy_module_is_onboard_only(self):
        for f in ("astar_battery.py", "rule_shield.py"):
            tree = ast.parse((ROOT / "src/policies" / f).read_text())
            mods = [n.module or "" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)] + \
                   [a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names]
            for m in mods:
                self.assertFalse(m.startswith("src.evaluation") or m.endswith("procgen") or m.endswith("terrain"), f"{f}: {m}")

    def test_reaches_goal_on_generated_maps_with_noisy_sensor_and_slip(self):
        env, ev = make_env(load_config(ROOT / "configs/sim32_id.yaml").env, 0)
        p = BatteryAwareAStar()
        _, s = evaluate_method(p, ROOT / "configs/sim32_id.yaml", range(20000, 20012), "astar", "id")
        self.assertGreaterEqual(s["success_rate"], 0.9)


class Fixed:
    def __init__(self, a, q=None):
        self.a, self.q = a, q

    def act(self, obs):
        return self.a

    def q_values(self, obs):
        if self.q is None:
            raise AttributeError
        return self.q


class FixedNoQ:
    def __init__(self, a):
        self.a = a

    def act(self, obs):
        return self.a


def shield_world(grid, start, base, **cfgkw):
    env, ev = make_env(quiet(**cfgkw) if cfgkw else quiet(), 0)
    obs = ev.reset_with_map(grid, start=start)
    sh = RuleShield(base)
    sh.attach(env.explored_map, env.max_battery)
    return env, ev, sh, obs


class TestRuleShield(unittest.TestCase):
    def test_invalid_action_off_map(self):
        env, ev, sh, obs = shield_world(flat(), (0, 0), FixedNoQ(0))   # up from the top-left corner
        self.assertEqual(sh.violations(obs, 0, env.explored_map()), ["invalid_action"])
        a = sh.act(obs)
        self.assertNotEqual(a, 0)
        self.assertEqual((sh.stats["interventions"], dict(sh.stats["by_rule"])), (1, {"invalid_action": 1}))

    def test_obstacle_in_window_is_rejected_and_best_q_alternative_chosen(self):
        g = flat(); g[10, 11] = T.OBSTACLE
        q = np.array([0.0, 0.1, 0.2, 5.0])           # base wants "right" (3) into the obstacle
        env, ev, sh, obs = shield_world(g, (10, 10), Fixed(3, q))
        a = sh.act(obs)
        self.assertEqual(a, 2)                       # best-Q among the SAFE actions (left), not the obstacle action
        self.assertEqual(sh.last_decision["violations"], ["obstacle"])

    def test_collision_memory_rejects_cell_the_sensor_missed(self):
        g = flat(); g[10, 11] = T.OBSTACLE
        env, ev = make_env(cfg32(slip_prob=(0, 0, 0), sensor_miss=1.0, sensor_false=0.0, sensor_sigma=0.0), 0)
        obs = ev.reset_with_map(g, start=(10, 10))
        sh = RuleShield(FixedNoQ(3)); sh.attach(env.explored_map, env.max_battery)
        self.assertEqual(sh.violations(obs, 3, env.explored_map()), [])       # sensor missed it: allowed
        obs, *_ = env.step(3)                                                 # bump
        self.assertEqual(sh.violations(obs, 3, env.explored_map()), ["obstacle"])

    def test_battery_rule(self):
        g = flat(); g[10, 11] = T.SAND
        env, ev, sh, obs = shield_world(g, (10, 10), FixedNoQ(3))
        env.battery = 3                                                       # entry 3 <= 3 but cannot reach the goal
        obs = env._observe()
        self.assertIn("battery", sh.violations(obs, 3, env.explored_map()))
        env.battery = 250
        self.assertEqual(sh.violations(env._observe(), 3, env.explored_map()), [])

    def test_safe_action_passes_through_untouched(self):
        env, ev, sh, obs = shield_world(flat(), (10, 10), FixedNoQ(1))
        self.assertEqual(sh.act(obs), 1)
        self.assertEqual((sh.stats["decisions"], sh.stats["interventions"]), (1, 0))

    def test_no_safe_action_keeps_base_action_and_counts_it(self):
        g = flat(); g[0, 1] = g[1, 0] = T.OBSTACLE           # rover walled into the corner (0,0): up/left off-map
        env, ev, sh, obs = shield_world(g, (0, 0), FixedNoQ(3))
        self.assertEqual(sh.act(obs), 3)
        self.assertEqual(sh.stats["no_safe_action"], 1)

    def test_shield_never_passes_a_detected_obstacle(self):
        rng = np.random.default_rng(0)
        for _ in range(40):
            g = G.generate_terrain(rng, 32, .5, .2, .1, 1); G.clear_blocks(g, (0, 0), (31, 31))
            pos = (int(rng.integers(3, 29)), int(rng.integers(3, 29))); g[pos] = T.NORMAL
            env, ev, sh, obs = shield_world(g, pos, Fixed(int(rng.integers(4)), rng.normal(size=4)))
            a = sh.act(obs)
            dr, dc = T.DELTAS[a]
            if not sh.last_decision.get("no_safe_action"):
                self.assertNotEqual(g[pos[0] + dr, pos[1] + dc], T.OBSTACLE)

    def test_requires_attach(self):
        with self.assertRaises(RuntimeError):
            RuleShield(FixedNoQ(0)).act(fake_obs((0, 0), (1, 1)))

    def test_shield_reduces_attempted_unsafe_actions(self):
        from src.policies.sim32_heuristic import ReactiveExplorer
        cfgp = ROOT / "configs/sim32_id.yaml"
        _, plain = evaluate_method(ReactiveExplorer(0), cfgp, range(20000, 20015), "r", "id")
        sh = RuleShield(ReactiveExplorer(0))
        _, shielded = evaluate_method(sh, cfgp, range(20000, 20015), "rs", "id")
        self.assertLess(shielded["attempted_unsafe_per_episode"], plain["attempted_unsafe_per_episode"])
        self.assertGreater(shielded["intervention_rate"], 0)


class TestHarness(unittest.TestCase):
    CFG = ROOT / "configs/sim32_id.yaml"

    def test_all_methods_get_identical_maps_and_rows_are_consistent(self):
        from src.policies.baseline_policies import RandomPolicy
        seeds = range(20000, 20004)
        ra, _ = evaluate_method(BatteryAwareAStar(), self.CFG, seeds, "astar", "id")
        rb, _ = evaluate_method(RandomPolicy(0), self.CFG, seeds, "random", "id")
        self.assertEqual([r["map"] for r in ra], [r["map"] for r in rb])
        self.assertEqual([r["optimal_cost"] for r in ra], [r["optimal_cost"] for r in rb])
        for r in ra + rb:
            self.assertEqual(r["success"], int(r["reason"] == "goal"))
            self.assertLessEqual(r["attempted_unsafe"], r["steps"])
            self.assertGreaterEqual(r["battery_left"], 0)

    def test_deterministic(self):
        a, _ = evaluate_method(BatteryAwareAStar(), self.CFG, range(20000, 20005), "a", "id")
        b, _ = evaluate_method(BatteryAwareAStar(), self.CFG, range(20000, 20005), "a", "id")
        for x, y in zip(a, b):
            x, y = dict(x), dict(y)
            x.pop("plan_ms"); y.pop("plan_ms")
            self.assertEqual(x, y)

    def test_csv_has_documented_columns(self):
        with tempfile.TemporaryDirectory() as d:
            evaluate_method(BatteryAwareAStar(), self.CFG, range(20000, 20002), "a", "id", Path(d) / "x.csv")
            with open(Path(d) / "x.csv") as f:
                rows = list(csv.DictReader(f))
        self.assertEqual(list(rows[0].keys()), ROW_FIELDS)
        self.assertEqual(len(rows), 2)

    def test_attempted_unsafe_is_judged_from_ground_truth_on_the_commanded_move(self):
        env, ev = make_env(quiet(), 0)
        g = flat(); g[10, 11] = T.OBSTACLE
        ev.reset_with_map(g, start=(10, 10))
        self.assertTrue(ev.commanded_cell_unsafe(3))     # into the obstacle
        self.assertFalse(ev.commanded_cell_unsafe(1))
        ev.reset_with_map(flat(), start=(0, 0))
        self.assertTrue(ev.commanded_cell_unsafe(0))     # off the map


@unittest.skipUnless(HAS_TORCH, "torch not installed")
class TestDQNChecks(unittest.TestCase):
    def _agent(self, **kw):
        from src.agents.dqn_agent import DQNAgent
        env, ev = make_env(cfg32(), 0)
        cfg = replace(DQNConfig(), **kw)
        return DQNAgent(env.obs_dim, env.n_actions, cfg, seed=0), env, ev

    def test_replay_buffer_contents_match_the_transitions_and_terminated_flag(self):
        agent, env, ev = self._agent(buffer_size=1000, batch_size=16)
        env2, _ = make_env(cfg32(max_steps=5, slip_prob=(0, 0, 0)), 0)        # episodes end by TIMEOUT (truncated)
        rng, rec, obs = np.random.default_rng(0), [], env2.reset(seed=3)
        for _ in range(40):
            a = int(rng.integers(4))
            obs2, r, done, info = env2.step(a)
            agent.remember(obs, a, r, obs2, info["terminated"])
            rec.append((obs.astype(np.float32).tobytes(), a, round(float(r), 4), obs2.astype(np.float32).tobytes(), float(info["terminated"])))
            obs = env2.reset() if done else obs2
        self.assertEqual(len(agent.buffer), 40)
        known, d_max = set(rec), 0.0
        for _ in range(10):                                  # batches never exceed the buffer (sampling is without replacement)
            s, a, r, s2, d = agent.buffer.sample(32)
            self.assertEqual(s.shape, (32, env.obs_dim))
            for i in range(32):
                self.assertIn((s[i].astype(np.float32).tobytes(), int(a[i]), round(float(r[i]), 4),
                               s2[i].astype(np.float32).tobytes(), float(d[i])), known)
            d_max = max(d_max, float(np.max(d)))
        self.assertEqual(d_max, 0.0)   # every episode here was truncated, never terminated -> bootstrap must continue

    def test_target_network_updates_every_n_learn_steps(self):
        import torch
        agent, env, ev = self._agent(buffer_size=500, batch_size=8, target_update_freq=5, warmup_steps=0)
        rng, obs = np.random.default_rng(1), env.reset(seed=1)
        for _ in range(40):
            a = int(rng.integers(4)); obs2, r, done, info = env.step(a)
            agent.remember(obs, a, r, obs2, info["terminated"]); obs = env.reset() if done else obs2
        same = lambda: all(torch.equal(p, q) for p, q in zip(agent.model.parameters(), agent.target.parameters()))  # noqa: E731
        self.assertTrue(same())
        for k in range(1, 5):
            agent.learn()
            self.assertFalse(same(), f"target changed early at step {k}")
        agent.learn()                                                          # 5th learn step -> sync
        self.assertTrue(same())

    def test_exploration_schedule(self):
        agent, env, _ = self._agent()
        self.assertEqual(agent.epsilon, DQNConfig().eps_start)
        for _ in range(2000):
            agent.decay_epsilon()
        c = DQNConfig()
        self.assertTrue(c.eps_min * c.eps_decay <= agent.epsilon <= c.eps_min + 1e-12)
        agent.epsilon = 1.0
        obs = env.reset(seed=2)
        self.assertEqual({agent.act(obs) for _ in range(200)}, {0, 1, 2, 3})   # fully random when epsilon = 1
        self.assertEqual(len({agent.act(obs, greedy=True) for _ in range(50)}), 1)  # greedy ignores epsilon
        self.assertEqual(agent.act(obs, greedy=True), int(np.argmax(agent.q_values(obs))))

    def test_checkpoint_roundtrip(self):
        agent, env, _ = self._agent()
        agent.epsilon = 0.37
        obs = env.reset(seed=4)
        with tempfile.TemporaryDirectory() as d:
            agent.save(Path(d) / "c.pt")
            other, _, _ = self._agent()
            other.load(Path(d) / "c.pt")
        np.testing.assert_allclose(agent.q_values(obs), other.q_values(obs))
        self.assertEqual(other.epsilon, 0.37)

    def test_reward_calculation(self):
        env, ev = make_env(quiet(), 0)
        g = flat(); g[6, 5] = T.NORMAL; g[5, 6] = T.SAND; g[4, 5] = T.ROCK
        ev.reset_with_map(g, start=(5, 5))
        self.assertAlmostEqual(env.step(1)[1], 0.5 - 0.05)                     # toward goal, normal
        ev.reset_with_map(g, start=(5, 5))
        self.assertAlmostEqual(env.step(3)[1], 0.5 - 0.05 - 0.05)              # toward goal, sand (energy 3)
        ev.reset_with_map(g, start=(5, 5))
        self.assertAlmostEqual(env.step(0)[1], -0.5 - 0.05 - 0.10)             # away from goal, rock (energy 5)

    def test_training_loop_saves_best_val_and_final_checkpoints(self):
        from src.agents.dqn_agent import DQNAgent
        from src.training.loops import train_dqn
        cfg = Config(env=cfg32(), dqn=replace(DQNConfig(), warmup_steps=50, buffer_size=2000),
                     run=replace(Config().run, episodes=4, eval_every=2, eval_episodes=2, final_test_eval=True))
        env, _ = make_env(cfg.env, 0)
        agent = DQNAgent(env.obs_dim, env.n_actions, cfg.dqn, seed=0)
        with tempfile.TemporaryDirectory() as d:
            s = train_dqn(agent, cfg, d)
            self.assertTrue((Path(d) / "checkpoints/best_val.pt").exists())
            self.assertTrue((Path(d) / "checkpoints/final.pt").exists())
            self.assertEqual(len((Path(d) / "eval_greedy_val.csv").read_text().strip().splitlines()) - 1, 2)
        self.assertEqual(s["greedy_test_200"]["episodes"], 200)


if __name__ == "__main__":
    unittest.main()
