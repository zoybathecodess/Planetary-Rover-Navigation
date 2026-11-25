"""Task-2 simulator: 32x32 procedural terrain, 5x5 noisy local sensing, explored-map memory, slip, terrain energy.

Same policy-facing protocol as the Task-1 env (reset/step/obs_dim/n_actions/position/battery/steps/map_id/max_battery),
so `evaluation.runner`, the training loops and `make_env` work unchanged.

INFORMATION BOUNDARY (see docs/OBSERVATION_SCHEMA_V2.md)
  hidden (evaluator only): `_world` (true grid, optimal cost), TRUE slip/energy/sensor parameters, RNG streams.
  onboard (obs + `explored_map()`): position, goal offset, battery, step count, noisy 5x5 readings, visit counts,
  and quantities the rover can compute from its own history (slip estimate, sensor confidence, explored-map counts).

RANDOMNESS: each episode seed spawns THREE independent streams (map, slip, sensor). Changing sensor or dynamics
parameters therefore never changes the map, and sensor draws do not depend on terrain (fixed draws per step),
which keeps shifted conditions paired with the in-distribution ones.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from src.config import EnvConfig
from src.environment import procgen as G
from src.environment import terrain as T

R = 2                    # window radius -> 5x5
W = 2 * R + 1
OBSTACLE_READING = 1.0   # a reading >= 0.999 means "obstacle detected"; free-cell readings are clipped to <= 0.9
FREE_CLIP = 0.9
SCALARS = ("x_norm", "y_norm", "goal_dx", "goal_dy", "battery_ratio", "steps_ratio",
           "slip_estimate", "sensor_confidence", "coverage")
FEATURES = (SCALARS
            + tuple(f"win_r{i:+d}_c{j:+d}" for i in range(-R, R + 1) for j in range(-R, R + 1))
            + tuple(f"visits_r{i:+d}_c{j:+d}" for i in range(-R, R + 1) for j in range(-R, R + 1)))
SLIP_PRIOR = (1.0, 9.0)  # slip_estimate = (slips + 1) / (moves + 10): prior mean 0.1
CONF_ALPHA = 0.3         # EMA weight of the newest agreement fraction
# perpendicular actions (0,1 = vertical moves; 2,3 = horizontal moves)
_PERP = {0: (2, 3), 1: (2, 3), 2: (0, 1), 3: (0, 1)}


@dataclass
class _AdvWorld:
    """Hidden ground truth. Not exposed through the policy-facing API."""
    grid: np.ndarray
    start: tuple[int, int]
    goal: tuple[int, int]
    optimal_cost: int   # under the TRUE energy table
    map_id: str


@dataclass(frozen=True)
class ExploredMap:
    """Onboard snapshot of what the rover has sensed so far (all arrays are copies, shape size x size).

    seen:        number of times each cell fell inside the sensor window
    obs_reads:   how many of those readings said "obstacle"
    terrain_sum: sum of the non-obstacle readings (0..0.9 scale; 0=normal, ~0.3=sand, ~0.6=rock)
    visits:      times the rover stood on the cell
    bumped:      True where a collision PROVED the cell is an obstacle (touch is noise-free)
    """
    seen: np.ndarray
    obs_reads: np.ndarray
    terrain_sum: np.ndarray
    visits: np.ndarray
    bumped: np.ndarray

    @property
    def known(self) -> np.ndarray:
        return self.seen > 0

    @property
    def obstacle_frac(self) -> np.ndarray:
        """Fraction of readings that said obstacle (nan where never seen); `bumped` cells are 1.0."""
        with np.errstate(invalid="ignore", divide="ignore"):
            f = np.where(self.seen > 0, self.obs_reads / np.maximum(self.seen, 1), np.nan)
        return np.where(self.bumped, 1.0, f)

    @property
    def terrain_mean(self) -> np.ndarray:
        """Mean non-obstacle reading (nan where there is none)."""
        n_free = self.seen - self.obs_reads
        with np.errstate(invalid="ignore", divide="ignore"):
            return np.where(n_free > 0, self.terrain_sum / np.maximum(n_free, 1), np.nan)


class AdvancedRoverEnv:
    n_actions = 4
    window = W

    def __init__(self, cfg: EnvConfig, seed: int = 0):
        if cfg.kind != "advanced":
            raise ValueError(f"AdvancedRoverEnv needs cfg.kind == 'advanced', got {cfg.kind!r}")
        self.cfg = cfg
        self.size = cfg.size
        self.max_battery = cfg.battery
        self.max_steps = cfg.max_steps or cfg.battery  # every action costs >= 1 battery, so this cannot trigger unless
        #                                                max_steps < battery or a zero-cost action (e.g. stop) is added
        self.obs_dim = len(FEATURES)
        self.feature_names = FEATURES
        self._lut = G.energy_lut(cfg.energy_cost)          # TRUE energy table (hidden)
        self._ref_lut = G.energy_lut(cfg.ref_energy_cost)  # nominal table, map acceptance only
        self._slip = tuple(float(p) for p in cfg.slip_prob)  # TRUE slip by current terrain (hidden)
        self._base_seed = seed
        self._episode_index = 0
        self._world: _AdvWorld | None = None
        self.position = (0, 0)
        self.battery = self.max_battery
        self.steps = 0
        self._done = True

    # ------------------------------------------------------------------ episode setup
    def reset(self, seed: int | None = None) -> np.ndarray:
        """New episode. seed=None -> next map of this env's reproducible stream; int -> that exact episode."""
        if seed is None:
            ss = np.random.SeedSequence([self._base_seed, 0x5EED, self._episode_index])
            map_id = f"stream({self._base_seed},{self._episode_index})"
            self._episode_index += 1
        else:
            ss = np.random.SeedSequence([int(seed)])
            map_id = f"seed({seed})"
        map_ss, slip_ss, sens_ss = ss.spawn(3)
        rng, c = np.random.default_rng(map_ss), self.cfg
        start, goal = (0, 0), (self.size - 1, self.size - 1)
        if c.external_tiles:                     # amendment A2: real-terrain tile (generator side; the rover never sees it)
            grid = self._external_tile(seed)
            G.clear_blocks(grid, start, goal)
            true = G.dijkstra_lut(grid, start, self._lut)[goal]
            self._install_world(grid, start, goal, int(true), f"tile({seed})", (slip_ss, sens_ss))
            return self._observe()
        for _ in range(c.map_retry_limit):
            grid = G.generate_terrain(rng, self.size, c.p_normal, c.p_sand, c.p_rock, c.gen_corr)
            G.clear_blocks(grid, start, goal)
            ref = G.dijkstra_lut(grid, start, self._ref_lut)[goal]
            if ref >= T.INF or ref > c.max_opt_cost_frac * self.max_battery:
                continue
            true = G.dijkstra_lut(grid, start, self._lut)[goal]
            if c.ensure_energy_feasible and true > self.max_battery:
                continue
            break
        else:
            raise RuntimeError(f"No valid map after {c.map_retry_limit} attempts; check terrain probabilities/battery")
        self._install_world(grid, start, goal, int(true), map_id, (slip_ss, sens_ss))
        return self._observe()

    def _external_tile(self, seed):
        if seed is None:
            raise ValueError("external_tiles maps are evaluation-only: call reset(seed=<tile seed>)")
        if getattr(self, "_tiles", None) is None:
            from pathlib import Path
            p = Path(self.cfg.external_tiles)
            if not p.is_absolute():
                p = Path(__file__).resolve().parents[2] / p
            z = np.load(p)
            self._tiles = {int(s): g.astype(np.int64) for s, g in zip(z["seeds"], z["grids"])}
        if int(seed) not in self._tiles:
            raise KeyError(f"no real-terrain tile with seed {seed}")
        return self._tiles[int(seed)].copy()

    def _install_world(self, grid, start, goal, optimal_cost, map_id, streams=None) -> None:
        if streams is None:  # injected maps (evaluator.reset_with_map, tests): streams from the env's own seed
            ss = np.random.SeedSequence([self._base_seed, 0x1A7E, self._episode_index])
            self._episode_index += 1
            streams = tuple(ss.spawn(2))
        self._slip_rng, self._sens_rng = (np.random.default_rng(s) for s in streams)
        self._world = _AdvWorld(np.asarray(grid, dtype=np.int64).copy(), tuple(start), tuple(goal), int(optimal_cost), map_id)
        n = self.size
        self.position, self.battery, self.steps, self._done = tuple(start), self.max_battery, 0, False
        z = lambda dt: np.zeros((n, n), dtype=dt)  # noqa: E731
        self._seen, self._obs_reads, self._terr_sum = z(np.int64), z(np.int64), z(float)
        self._visits, self._bumped = z(np.int64), z(bool)
        self._visits[self.position] = 1
        self._slips, self._moves, self._conf = 0, 0, 1.0

    @property
    def map_id(self) -> str:
        """Seed label of the current map (reproducibility metadata, carries no terrain information)."""
        return self._world.map_id

    def explored_map(self) -> ExploredMap:
        """Onboard memory for the fallback planner / monitor (copies; contains only sensed information)."""
        return ExploredMap(self._seen.copy(), self._obs_reads.copy(), self._terr_sum.copy(),
                           self._visits.copy(), self._bumped.copy())

    # ------------------------------------------------------------------ sensing
    def _sense(self) -> np.ndarray:
        """Noisy 5x5 readings around the rover; updates the explored map and sensor confidence. Call once per step."""
        w, n, c = self._world, self.size, self.cfg
        x, y = self.position
        # FIXED number of draws per call (independent of terrain) -> streams stay aligned across maps/presets
        u = self._sens_rng.random((W, W))
        z = self._sens_rng.standard_normal((W, W))
        rows, cols = np.arange(x - R, x + R + 1)[:, None], np.arange(y - R, y + R + 1)[None, :]
        inb = (rows >= 0) & (rows < n) & (cols >= 0) & (cols < n)
        true = np.full((W, W), T.OBSTACLE, dtype=np.int64)
        true[inb] = w.grid[np.broadcast_to(rows, (W, W))[inb], np.broadcast_to(cols, (W, W))[inb]]
        is_obs = true == T.OBSTACLE
        free_val = np.clip(T.PATCH_VALUE[np.minimum(true, 2)] + c.sensor_sigma * z, 0.0, FREE_CLIP)
        missed_val = np.clip(c.sensor_sigma * z, 0.0, FREE_CLIP)  # a missed obstacle looks like (noisy) normal terrain
        reading = np.where(is_obs, np.where(u < c.sensor_miss, missed_val, OBSTACLE_READING),
                           np.where(u < c.sensor_false, OBSTACLE_READING, free_val))
        reading = np.where(inb, reading, OBSTACLE_READING)  # outside the map: known-blocked (map size is known)
        # --- sensor confidence: agreement of fresh readings with what memory already believed
        det = (reading >= 0.999) & inb
        prior_n = np.zeros((W, W), dtype=np.int64)
        prior_n[inb] = self._seen[np.broadcast_to(rows, (W, W))[inb], np.broadcast_to(cols, (W, W))[inb]]
        old = prior_n > 0
        if old.sum() >= 3:
            ri, ci = np.broadcast_to(rows, (W, W))[old], np.broadcast_to(cols, (W, W))[old]
            believed_obs = (self._obs_reads[ri, ci] / self._seen[ri, ci]) > 0.5
            n_free = np.maximum(self._seen[ri, ci] - self._obs_reads[ri, ci], 1)
            believed_val = self._terr_sum[ri, ci] / n_free
            d = det[old]
            r_old = reading[old]
            agree = np.where(d | believed_obs, d == believed_obs, np.abs(r_old - believed_val) < 0.25)
            self._conf = (1 - CONF_ALPHA) * self._conf + CONF_ALPHA * float(agree.mean())
        # --- explored-map update (in-bounds cells only)
        ri, ci = np.broadcast_to(rows, (W, W))[inb], np.broadcast_to(cols, (W, W))[inb]
        self._seen[ri, ci] += 1
        self._obs_reads[ri, ci] += det[inb]
        self._terr_sum[ri, ci] += np.where(det[inb], 0.0, reading[inb])
        return reading

    def _observe(self) -> np.ndarray:
        """Sense (consumes the sensor stream) and build the policy-facing vector. Exactly once per reset/step."""
        w, n = self._world, self.size
        x, y = self.position
        reading = self._sense()
        pad = np.pad(self._visits, R, constant_values=0)
        visits = np.minimum(pad[x:x + W, y:y + W], 3) / 3.0
        scalars = [x / (n - 1), y / (n - 1), (w.goal[0] - x) / (n - 1), (w.goal[1] - y) / (n - 1),
                   self.battery / self.max_battery, self.steps / self.max_battery,
                   (self._slips + SLIP_PRIOR[0]) / (self._moves + SLIP_PRIOR[0] + SLIP_PRIOR[1]),
                   self._conf, float((self._seen > 0).mean())]
        return np.concatenate([np.asarray(scalars, dtype=float), reading.ravel(), visits.ravel()])

    # ------------------------------------------------------------------ dynamics
    def step(self, action: int):
        """Returns (obs, reward, done, info). info keys: event, reason, terminated, truncated, energy_used, steps,
        battery, slipped (the rover can tell from odometry that it did not do what it commanded)."""
        if self._done:
            raise RuntimeError("step() called on a finished episode; call reset()")
        w, n = self._world, self.size
        self.steps += 1
        x, y = self.position
        # slip draws are ALWAYS made (2 per step) so the slip stream does not depend on terrain/decisions
        u_slip, u_dir = self._slip_rng.random(), int(self._slip_rng.integers(2))
        slipped = bool(u_slip < self._slip[int(w.grid[x, y])])
        a = _PERP[int(action)][u_dir] if slipped else int(action)
        self._moves += 1
        self._slips += slipped
        dx, dy = T.DELTAS[a]
        nx, ny = x + dx, y + dy
        info = {"event": "slip_move" if slipped else "move", "reason": None, "terminated": False,
                "truncated": False, "energy_used": 0, "slipped": slipped}

        out_of_bounds = not (0 <= nx < n and 0 <= ny < n)
        if out_of_bounds or w.grid[nx, ny] == T.OBSTACLE:
            info["event"] = "boundary_collision" if out_of_bounds else "obstacle_collision"
            if not out_of_bounds:
                self._bumped[nx, ny] = True  # touch is noise-free: memory now KNOWS this cell is an obstacle
            used = min(1, self.battery)
            self.battery -= used
            info["energy_used"] = used
            if self.battery <= 0:
                return self._finish(-10.0, "battery_depleted", info)
            return self._continue(-2.0, info)

        cost = int(self._lut[int(w.grid[nx, ny])])
        if cost > self.battery:  # cannot complete the move: stalls, battery spent
            info["event"], info["energy_used"], self.battery = "stalled", self.battery, 0
            return self._finish(-20.0, "battery_depleted", info)

        self.position = (nx, ny)
        self._visits[nx, ny] += 1
        self.battery -= cost
        info["energy_used"] = cost
        if (nx, ny) == w.goal:  # terminal bonus from the battery FRACTION left: no full-map quantity in the reward
            return self._finish(100.0 + 50.0 * self.battery / self.max_battery, "goal", info)
        if self.battery == 0:
            return self._finish(-20.0, "battery_depleted", info)
        old_d = abs(x - w.goal[0]) + abs(y - w.goal[1])
        new_d = abs(nx - w.goal[0]) + abs(ny - w.goal[1])
        # terrain penalty from the energy the rover FELT (observed), identical to the Task-1 values at costs 1/3/5
        reward = (old_d - new_d) * 0.5 - 0.05 - 0.025 * (cost - 1)
        return self._continue(reward, info)

    def safe_stop(self):
        """Runtime-assurance terminal action: the rover halts. Ends the episode with reason "safe_stop" (NOT a goal, NOT a
        failure of the vehicle): zero energy, zero reward, no step counted. Returns the same tuple as step()."""
        if self._done:
            raise RuntimeError("safe_stop() called on a finished episode; call reset()")
        info = {"event": "safe_stop", "reason": "safe_stop", "terminated": True, "truncated": False,
                "energy_used": 0, "slipped": False}
        self._done = True
        return self._observe(), 0.0, True, self._stamp(info)

    def _continue(self, reward, info):
        if self.steps >= self.max_steps:
            info["truncated"], info["reason"] = True, "timeout"
            self._done = True
        return self._observe(), reward, self._done, self._stamp(info)

    def _finish(self, reward, reason, info):
        info["terminated"], info["reason"] = True, reason
        self._done = True
        return self._observe(), reward, True, self._stamp(info)

    def _stamp(self, info):
        info["steps"], info["battery"] = self.steps, self.battery
        return info
