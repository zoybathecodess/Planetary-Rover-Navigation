"""Observation layout of the Task-2 simulator (59-d) as used by the onboard assurance components, and the stop sentinel.
A test (tests/test_assurance.py) checks these indices against `advanced_env.FEATURES`, so the two cannot drift apart."""
STOP_ACTION = -1          # returned by a policy/controller instead of a move: "halt, end the episode as a safe stop"
N_ACTIONS = 4
DELTAS = ((-1, 0), (1, 0), (0, -1), (0, 1))   # 0 up, 1 down, 2 left, 3 right (same as the env)
R, W = 2, 5
IDX_X, IDX_Y, IDX_GDX, IDX_GDY, IDX_BATT, IDX_STEPS, IDX_SLIP, IDX_CONF, IDX_COV = range(9)
WIN0 = 9                  # 5x5 noisy readings, row-major
VIS0 = 34                 # 5x5 visit counts
OBSTACLE_READING = 0.999  # a reading >= this means "obstacle detected" (or map edge)
# OOD detector features: evidence about the ENVIRONMENT, SENSOR and DYNAMICS, not about where the rover happens to be:
# the 25 window readings (terrain statistics, sensor noise), slip estimate, sensor confidence, battery and step ratios
# (their joint relation reveals the energy cost per step). Position, goal offset, coverage and visit counts are excluded.
OOD_FEATURES = tuple(range(WIN0, WIN0 + W * W)) + (IDX_SLIP, IDX_CONF, IDX_BATT, IDX_STEPS)


def perpendicular(action: int) -> tuple[int, int]:
    return (2, 3) if action in (0, 1) else (0, 1)
