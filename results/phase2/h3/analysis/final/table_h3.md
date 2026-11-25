# Amendment A1 — H3: battery-aware vs energy-blind fallback

Mean ± 95% t-interval over 10 system seeds; 500 identical final-split maps per condition.
EFI = energy-feasible intervention rate: among episodes where the fallback acted, share not ending in battery depletion.

### id

| Method | EFI | fallback success | depleted | success | safe stop | energy used | collisions | unsafe |
|---|---|---|---|---|---|---|---|---|
| assured-fb_blind@95 | 1.000 ± 0.000 | 0.987 ± 0.007 | 0.000 ± 0.000 | 0.992 ± 0.003 | 0.008 ± 0.003 | 94.942 ± 1.479 | 0.208 ± 0.016 | 0.035 ± 0.004 |
| assured-fb_blind_no_stop@95 | 0.989 ± 0.006 | 0.989 ± 0.006 | 0.005 ± 0.003 | 0.995 ± 0.003 | 0.000 ± 0.000 | 95.267 ± 1.502 | 0.215 ± 0.016 | 0.041 ± 0.005 |
| assured-no_stop@95 | 0.969 ± 0.012 | 0.969 ± 0.012 | 0.013 ± 0.004 | 0.987 ± 0.004 | 0.000 ± 0.000 | 95.311 ± 1.753 | 0.239 ± 0.017 | 0.063 ± 0.007 |
| assured@95 | 1.000 ± 0.000 | 0.963 ± 0.013 | 0.000 ± 0.000 | 0.982 ± 0.004 | 0.018 ± 0.004 | 94.724 ± 1.641 | 0.209 ± 0.017 | 0.035 ± 0.005 |

### terrain_shift

| Method | EFI | fallback success | depleted | success | safe stop | energy used | collisions | unsafe |
|---|---|---|---|---|---|---|---|---|
| assured-fb_blind@95 | 1.000 ± 0.001 | 0.875 ± 0.020 | 0.000 ± 0.000 | 0.933 ± 0.008 | 0.066 ± 0.008 | 143.854 ± 1.187 | 0.287 ± 0.010 | 0.026 ± 0.006 |
| assured-fb_blind_no_stop@95 | 0.879 ± 0.020 | 0.879 ± 0.020 | 0.063 ± 0.009 | 0.937 ± 0.009 | 0.000 ± 0.000 | 145.513 ± 1.346 | 0.299 ± 0.011 | 0.030 ± 0.006 |
| assured-no_stop@95 | 0.882 ± 0.017 | 0.882 ± 0.017 | 0.061 ± 0.007 | 0.939 ± 0.007 | 0.000 ± 0.000 | 144.696 ± 1.539 | 0.396 ± 0.023 | 0.109 ± 0.013 |
| assured@95 | 1.000 ± 0.000 | 0.867 ± 0.020 | 0.000 ± 0.000 | 0.929 ± 0.008 | 0.071 ± 0.008 | 142.057 ± 1.333 | 0.304 ± 0.013 | 0.028 ± 0.005 |

### sensor_shift

| Method | EFI | fallback success | depleted | success | safe stop | energy used | collisions | unsafe |
|---|---|---|---|---|---|---|---|---|
| assured-fb_blind@95 | 1.000 ± 0.000 | 0.931 ± 0.006 | 0.000 ± 0.000 | 0.924 ± 0.005 | 0.076 ± 0.005 | 145.512 ± 1.232 | 1.266 ± 0.019 | 0.751 ± 0.017 |
| assured-fb_blind_no_stop@95 | 0.987 ± 0.001 | 0.987 ± 0.001 | 0.013 ± 0.001 | 0.987 ± 0.001 | 0.000 ± 0.000 | 150.278 ± 1.533 | 1.316 ± 0.023 | 0.776 ± 0.020 |
| assured-no_stop@95 | 0.982 ± 0.001 | 0.982 ± 0.001 | 0.018 ± 0.001 | 0.982 ± 0.001 | 0.000 ± 0.000 | 110.290 ± 0.614 | 0.988 ± 0.016 | 0.652 ± 0.018 |
| assured@95 | 1.000 ± 0.000 | 0.934 ± 0.004 | 0.000 ± 0.000 | 0.927 ± 0.004 | 0.073 ± 0.004 | 106.433 ± 0.653 | 0.908 ± 0.015 | 0.592 ± 0.018 |

### dynamics_shift

| Method | EFI | fallback success | depleted | success | safe stop | energy used | collisions | unsafe |
|---|---|---|---|---|---|---|---|---|
| assured-fb_blind@95 | 0.999 ± 0.001 | 0.969 ± 0.010 | 0.000 ± 0.001 | 0.979 ± 0.006 | 0.020 ± 0.006 | 118.256 ± 1.478 | 0.738 ± 0.062 | 0.033 ± 0.005 |
| assured-fb_blind_no_stop@95 | 0.971 ± 0.010 | 0.971 ± 0.010 | 0.018 ± 0.006 | 0.982 ± 0.006 | 0.000 ± 0.000 | 118.760 ± 1.513 | 0.749 ± 0.064 | 0.039 ± 0.007 |
| assured-no_stop@95 | 0.971 ± 0.007 | 0.971 ± 0.007 | 0.017 ± 0.004 | 0.983 ± 0.004 | 0.000 ± 0.000 | 113.687 ± 1.494 | 0.709 ± 0.049 | 0.059 ± 0.008 |
| assured@95 | 1.000 ± 0.000 | 0.966 ± 0.007 | 0.000 ± 0.000 | 0.978 ± 0.004 | 0.022 ± 0.004 | 112.958 ± 1.459 | 0.675 ± 0.047 | 0.032 ± 0.004 |

### combined_shift

| Method | EFI | fallback success | depleted | success | safe stop | energy used | collisions | unsafe |
|---|---|---|---|---|---|---|---|---|
| assured-fb_blind@95 | 0.996 ± 0.001 | 0.269 ± 0.011 | 0.004 ± 0.001 | 0.267 ± 0.011 | 0.730 ± 0.011 | 221.880 ± 0.393 | 2.285 ± 0.037 | 0.572 ± 0.010 |
| assured-fb_blind_no_stop@95 | 0.277 ± 0.012 | 0.277 ± 0.012 | 0.723 ± 0.012 | 0.277 ± 0.012 | 0.000 ± 0.000 | 240.126 ± 0.628 | 2.540 ± 0.046 | 0.659 ± 0.014 |
| assured-no_stop@95 | 0.749 ± 0.006 | 0.749 ± 0.006 | 0.251 ± 0.006 | 0.749 ± 0.006 | 0.000 ± 0.000 | 200.900 ± 0.595 | 2.033 ± 0.016 | 0.677 ± 0.008 |
| assured@95 | 0.999 ± 0.001 | 0.717 ± 0.006 | 0.001 ± 0.001 | 0.712 ± 0.006 | 0.287 ± 0.005 | 188.430 ± 0.507 | 1.799 ± 0.015 | 0.561 ± 0.006 |

## Paired differences (A − B), Holm across the five conditions per (comparison, metric)

### battery-aware vs energy-blind fallback — energy_feasible_intervention_rate  (PRIMARY)

| Condition | n | A − B | 95% CI | p (perm) | p (Holm) |
|---|---|---|---|---|---|
| id | 10 | +0.0000 | [+0.0000, +0.0000] | 1.0000 | 1.0000 |
| terrain_shift | 10 | +0.0004 | [-0.0005, +0.0013] | 1.0000 | 1.0000 |
| sensor_shift | 10 | +0.0000 | [+0.0000, +0.0000] | 1.0000 | 1.0000 |
| dynamics_shift | 10 | +0.0008 | [-0.0004, +0.0019] | 0.5000 | 1.0000 |
| combined_shift | 10 | +0.0022 | [+0.0012, +0.0033] | 0.0078 | 0.0391 * |

### battery-aware vs energy-blind fallback — fallback_success

| Condition | n | A − B | 95% CI | p (perm) | p (Holm) |
|---|---|---|---|---|---|
| id | 10 | -0.0236 | [-0.0345, -0.0127] | 0.0020 | 0.0098 * |
| terrain_shift | 10 | -0.0081 | [-0.0158, -0.0003] | 0.0547 | 0.1641 |
| sensor_shift | 10 | +0.0024 | [-0.0036, +0.0084] | 0.3750 | 0.7500 |
| dynamics_shift | 10 | -0.0029 | [-0.0105, +0.0047] | 0.3984 | 0.7500 |
| combined_shift | 10 | +0.4484 | [+0.4360, +0.4608] | 0.0020 | 0.0098 * |

### battery-aware vs energy-blind fallback — depleted_rate

| Condition | n | A − B | 95% CI | p (perm) | p (Holm) |
|---|---|---|---|---|---|
| id | 10 | +0.0000 | [+0.0000, +0.0000] | 1.0000 | 1.0000 |
| terrain_shift | 10 | -0.0002 | [-0.0007, +0.0003] | 1.0000 | 1.0000 |
| sensor_shift | 10 | +0.0000 | [+0.0000, +0.0000] | 1.0000 | 1.0000 |
| dynamics_shift | 10 | -0.0004 | [-0.0010, +0.0002] | 0.5000 | 1.0000 |
| combined_shift | 10 | -0.0022 | [-0.0033, -0.0011] | 0.0078 | 0.0391 * |

### battery-aware vs energy-blind fallback — success

| Condition | n | A − B | 95% CI | p (perm) | p (Holm) |
|---|---|---|---|---|---|
| id | 10 | -0.0096 | [-0.0138, -0.0054] | 0.0020 | 0.0098 * |
| terrain_shift | 10 | -0.0044 | [-0.0087, -0.0001] | 0.0547 | 0.1641 |
| sensor_shift | 10 | +0.0024 | [-0.0035, +0.0083] | 0.4297 | 0.8594 |
| dynamics_shift | 10 | -0.0016 | [-0.0061, +0.0029] | 0.4961 | 0.8594 |
| combined_shift | 10 | +0.4450 | [+0.4327, +0.4573] | 0.0020 | 0.0098 * |

### battery-aware vs energy-blind fallback — energy_used

| Condition | n | A − B | 95% CI | p (perm) | p (Holm) |
|---|---|---|---|---|---|
| id | 10 | -0.2180 | [-0.5301, +0.0941] | 0.1426 | 0.1426 |
| terrain_shift | 10 | -1.7978 | [-2.3668, -1.2288] | 0.0020 | 0.0098 * |
| sensor_shift | 10 | -39.0790 | [-39.7906, -38.3674] | 0.0020 | 0.0098 * |
| dynamics_shift | 10 | -5.2978 | [-6.9623, -3.6333] | 0.0020 | 0.0098 * |
| combined_shift | 10 | -33.4502 | [-34.1458, -32.7546] | 0.0020 | 0.0098 * |

### battery-aware vs energy-blind fallback — safe_stop_rate

| Condition | n | A − B | 95% CI | p (perm) | p (Holm) |
|---|---|---|---|---|---|
| id | 10 | +0.0096 | [+0.0054, +0.0138] | 0.0020 | 0.0098 * |
| terrain_shift | 10 | +0.0046 | [+0.0004, +0.0088] | 0.0469 | 0.1406 |
| sensor_shift | 10 | -0.0024 | [-0.0083, +0.0035] | 0.4297 | 0.7422 |
| dynamics_shift | 10 | +0.0020 | [-0.0024, +0.0064] | 0.3711 | 0.7422 |
| combined_shift | 10 | -0.4428 | [-0.4553, -0.4303] | 0.0020 | 0.0098 * |

### battery-aware vs energy-blind fallback — collisions

| Condition | n | A − B | 95% CI | p (perm) | p (Holm) |
|---|---|---|---|---|---|
| id | 10 | +0.0008 | [-0.0095, +0.0111] | 0.9023 | 0.9023 |
| terrain_shift | 10 | +0.0168 | [+0.0036, +0.0300] | 0.0293 | 0.0586 |
| sensor_shift | 10 | -0.3582 | [-0.3747, -0.3417] | 0.0020 | 0.0098 * |
| dynamics_shift | 10 | -0.0636 | [-0.1056, -0.0216] | 0.0059 | 0.0176 * |
| combined_shift | 10 | -0.4856 | [-0.5323, -0.4389] | 0.0020 | 0.0098 * |

### battery-aware vs energy-blind fallback — unsafe

| Condition | n | A − B | 95% CI | p (perm) | p (Holm) |
|---|---|---|---|---|---|
| id | 10 | -0.0004 | [-0.0024, +0.0016] | 0.8125 | 0.8359 |
| terrain_shift | 10 | +0.0022 | [-0.0012, +0.0056] | 0.2188 | 0.6562 |
| sensor_shift | 10 | -0.1586 | [-0.1789, -0.1383] | 0.0020 | 0.0098 * |
| dynamics_shift | 10 | -0.0016 | [-0.0054, +0.0022] | 0.4180 | 0.8359 |
| combined_shift | 10 | -0.0104 | [-0.0239, +0.0031] | 0.1289 | 0.5156 |

### battery-aware vs energy-blind fallback (no stop) — energy_feasible_intervention_rate  (PRIMARY)

| Condition | n | A − B | 95% CI | p (perm) | p (Holm) |
|---|---|---|---|---|---|
| id | 10 | -0.0196 | [-0.0302, -0.0089] | 0.0020 | 0.0098 * |
| terrain_shift | 10 | +0.0029 | [-0.0062, +0.0120] | 0.4844 | 0.9688 |
| sensor_shift | 10 | -0.0054 | [-0.0076, -0.0032] | 0.0039 | 0.0117 * |
| dynamics_shift | 10 | +0.0000 | [-0.0080, +0.0081] | 0.9961 | 0.9961 |
| combined_shift | 10 | +0.4718 | [+0.4590, +0.4846] | 0.0020 | 0.0098 * |

### battery-aware vs energy-blind fallback (no stop) — fallback_success

| Condition | n | A − B | 95% CI | p (perm) | p (Holm) |
|---|---|---|---|---|---|
| id | 10 | -0.0196 | [-0.0302, -0.0089] | 0.0020 | 0.0098 * |
| terrain_shift | 10 | +0.0029 | [-0.0062, +0.0120] | 0.4844 | 0.9688 |
| sensor_shift | 10 | -0.0054 | [-0.0076, -0.0032] | 0.0039 | 0.0117 * |
| dynamics_shift | 10 | +0.0000 | [-0.0080, +0.0081] | 0.9961 | 0.9961 |
| combined_shift | 10 | +0.4718 | [+0.4590, +0.4846] | 0.0020 | 0.0098 * |

### battery-aware vs energy-blind fallback (no stop) — depleted_rate

| Condition | n | A − B | 95% CI | p (perm) | p (Holm) |
|---|---|---|---|---|---|
| id | 10 | +0.0080 | [+0.0037, +0.0123] | 0.0020 | 0.0098 * |
| terrain_shift | 10 | -0.0014 | [-0.0064, +0.0036] | 0.5938 | 1.0000 |
| sensor_shift | 10 | +0.0054 | [+0.0032, +0.0076] | 0.0039 | 0.0117 * |
| dynamics_shift | 10 | -0.0002 | [-0.0050, +0.0046] | 1.0000 | 1.0000 |
| combined_shift | 10 | -0.4718 | [-0.4846, -0.4590] | 0.0020 | 0.0098 * |

### battery-aware vs energy-blind fallback (no stop) — success

| Condition | n | A − B | 95% CI | p (perm) | p (Holm) |
|---|---|---|---|---|---|
| id | 10 | -0.0080 | [-0.0123, -0.0037] | 0.0020 | 0.0098 * |
| terrain_shift | 10 | +0.0014 | [-0.0036, +0.0064] | 0.5938 | 1.0000 |
| sensor_shift | 10 | -0.0054 | [-0.0076, -0.0032] | 0.0039 | 0.0117 * |
| dynamics_shift | 10 | +0.0002 | [-0.0046, +0.0050] | 1.0000 | 1.0000 |
| combined_shift | 10 | +0.4718 | [+0.4590, +0.4846] | 0.0020 | 0.0098 * |

### battery-aware vs energy-blind fallback (no stop) — energy_used

| Condition | n | A − B | 95% CI | p (perm) | p (Holm) |
|---|---|---|---|---|---|
| id | 10 | +0.0438 | [-0.3569, +0.4445] | 0.8047 | 0.8047 |
| terrain_shift | 10 | -0.8168 | [-1.3590, -0.2746] | 0.0020 | 0.0098 * |
| sensor_shift | 10 | -39.9874 | [-41.0869, -38.8879] | 0.0020 | 0.0098 * |
| dynamics_shift | 10 | -5.0728 | [-6.8055, -3.3401] | 0.0020 | 0.0098 * |
| combined_shift | 10 | -39.2260 | [-39.9494, -38.5026] | 0.0020 | 0.0098 * |

### battery-aware vs energy-blind fallback (no stop) — safe_stop_rate

| Condition | n | A − B | 95% CI | p (perm) | p (Holm) |
|---|---|---|---|---|---|
| id | 10 | +0.0000 | [+0.0000, +0.0000] | 1.0000 | 1.0000 |
| terrain_shift | 10 | +0.0000 | [+0.0000, +0.0000] | 1.0000 | 1.0000 |
| sensor_shift | 10 | +0.0000 | [+0.0000, +0.0000] | 1.0000 | 1.0000 |
| dynamics_shift | 10 | +0.0000 | [+0.0000, +0.0000] | 1.0000 | 1.0000 |
| combined_shift | 10 | +0.0000 | [+0.0000, +0.0000] | 1.0000 | 1.0000 |

### battery-aware vs energy-blind fallback (no stop) — collisions

| Condition | n | A − B | 95% CI | p (perm) | p (Holm) |
|---|---|---|---|---|---|
| id | 10 | +0.0242 | [+0.0115, +0.0369] | 0.0020 | 0.0098 * |
| terrain_shift | 10 | +0.0970 | [+0.0784, +0.1156] | 0.0020 | 0.0098 * |
| sensor_shift | 10 | -0.3286 | [-0.3481, -0.3091] | 0.0020 | 0.0098 * |
| dynamics_shift | 10 | -0.0396 | [-0.0830, +0.0038] | 0.0762 | 0.0762 |
| combined_shift | 10 | -0.5068 | [-0.5646, -0.4490] | 0.0020 | 0.0098 * |

### battery-aware vs energy-blind fallback (no stop) — unsafe

| Condition | n | A − B | 95% CI | p (perm) | p (Holm) |
|---|---|---|---|---|---|
| id | 10 | +0.0224 | [+0.0150, +0.0298] | 0.0020 | 0.0098 * |
| terrain_shift | 10 | +0.0794 | [+0.0669, +0.0919] | 0.0020 | 0.0098 * |
| sensor_shift | 10 | -0.1240 | [-0.1459, -0.1021] | 0.0020 | 0.0098 * |
| dynamics_shift | 10 | +0.0204 | [+0.0146, +0.0262] | 0.0020 | 0.0098 * |
| combined_shift | 10 | +0.0178 | [+0.0009, +0.0347] | 0.0508 | 0.0508 |

## Pre-registered decision

Primary comparison: battery-aware vs energy-blind fallback, metric EFI.
Significant improvement in: ['combined_shift']; significant deterioration in: none.
**H3: SUPPORTED**
