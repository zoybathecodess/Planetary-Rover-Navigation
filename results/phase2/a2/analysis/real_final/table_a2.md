# Amendment A2 — real-terrain transfer (HiRISE tiles, ID physics)

450 real_final tiles; mean ± 95% t-interval over 10 seeds (Wilson over tiles for seedless methods).

| Method | success | unsafe | collisions | energy_used | intervention_rate | safe_stop_rate | depleted_rate |
|---|---|---|---|---|---|---|---|
| astar | 0.996 [0.984, 0.999] | 0.102 | 0.569 | 79.716 | — | 0.000 [0.000, 0.008] | 0.004 [0.001, 0.016] |
| astar_monitor | 0.991 [0.977, 0.997] | 0.040 | 0.496 | 80.833 | 0.021 | 0.009 [0.003, 0.023] | 0.000 [0.000, 0.008] |
| reactive | 0.960 [0.938, 0.975] | 0.440 | 0.564 | 82.276 | — | 0.000 [0.000, 0.008] | 0.040 [0.025, 0.062] |
| dqn | 0.965 ± 0.006 | 3.198 ± 0.880 | 3.305 ± 0.898 | 83.983 ± 4.015 | — | 0.000 ± 0.000 | 0.035 ± 0.006 |
| dqn_shield | 0.972 ± 0.006 | 0.231 ± 0.075 | 0.398 ± 0.104 | 83.106 ± 3.677 | 0.021 ± 0.004 | 0.000 ± 0.000 | 0.028 ± 0.006 |
| ppo | 0.950 ± 0.005 | 7.526 ± 1.865 | 7.506 ± 1.876 | 88.779 ± 2.324 | — | 0.000 ± 0.000 | 0.050 ± 0.005 |
| ppo_shield | 0.962 ± 0.008 | 0.508 ± 0.188 | 0.631 ± 0.213 | 86.529 ± 1.865 | 0.037 ± 0.008 | 0.000 ± 0.000 | 0.038 ± 0.008 |
| ens | 0.980 ± 0.004 | 1.902 ± 0.401 | 1.976 ± 0.405 | 78.788 ± 1.414 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.020 ± 0.004 |
| assured-unc_only@95 | 0.992 ± 0.002 | 1.072 ± 0.295 | 1.161 ± 0.298 | 77.655 ± 1.399 | 0.008 ± 0.001 | 0.008 ± 0.002 | 0.000 ± 0.001 |
| assured@95 | 0.996 ± 0.002 | 0.019 ± 0.004 | 0.118 ± 0.025 | 76.571 ± 1.209 | 0.033 ± 0.008 | 0.004 ± 0.002 | 0.000 ± 0.000 |
| assured-no_stop@95 | 0.997 ± 0.002 | 0.023 ± 0.005 | 0.123 ± 0.024 | 76.734 ± 1.184 | 0.034 ± 0.008 | 0.000 ± 0.000 | 0.003 ± 0.002 |
| assured-aood@95 | 0.994 ± 0.003 | 0.015 ± 0.003 | 0.117 ± 0.021 | 76.891 ± 1.330 | 0.015 ± 0.002 | 0.006 ± 0.003 | 0.000 ± 0.000 |
| assured-monitor_only@95 | 0.987 ± 0.003 | 0.014 ± 0.003 | 0.115 ± 0.025 | 77.239 ± 1.262 | 0.005 ± 0.001 | 0.013 ± 0.003 | 0.000 ± 0.000 |
| assured-no_ood@95 | 0.993 ± 0.002 | 0.014 ± 0.004 | 0.116 ± 0.023 | 76.990 ± 1.318 | 0.012 ± 0.002 | 0.007 ± 0.002 | 0.000 ± 0.000 |

## Transfer: procedural ID → real terrain (success / unsafe)

| Method | ID success | real success | ID unsafe | real unsafe |
|---|---|---|---|---|
| astar | 0.998 | 0.996 | 0.270 | 0.102 |
| astar_monitor | 0.980 | 0.991 | 0.096 | 0.040 |
| reactive | 0.798 | 0.960 | 2.914 | 0.440 |
| dqn | 0.921 | 0.965 | 5.791 | 3.198 |
| dqn_shield | 0.934 | 0.972 | 0.313 | 0.231 |
| ppo | 0.876 | 0.950 | 16.770 | 7.526 |
| ppo_shield | 0.910 | 0.962 | 1.052 | 0.508 |
| ens | 0.966 | 0.980 | 1.992 | 1.902 |
| assured-unc_only@95 | 0.986 | 0.992 | 1.176 | 1.072 |
| assured@95 | 0.982 | 0.996 | 0.035 | 0.019 |
| assured-no_stop@95 | 0.987 | 0.997 | 0.063 | 0.023 |
| assured-aood@95 | 0.984 | 0.994 | 0.035 | 0.015 |
| assured-monitor_only@95 | 0.970 | 0.987 | 0.035 | 0.014 |
| assured-no_ood@95 | 0.983 | 0.993 | 0.035 | 0.014 |

## Paired differences (A − B); Holm across the comparisons of a family, per metric

| Family | Comparison | Metric | A − B | 95% CI | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|
| primary | assured vs A*+monitor | success | +0.0047 | [+0.0028, +0.0066] | 0.0020 | 0.0059 * |
| primary | assured vs ensemble | success | +0.0160 | [+0.0120, +0.0200] | 0.0020 | 0.0059 * |
| primary | assured vs DQN+shield | success | +0.0242 | [+0.0183, +0.0301] | 0.0020 | 0.0059 * |
| primary | assured vs A*+monitor | unsafe | -0.0209 | [-0.0249, -0.0168] | 0.0020 | 0.0059 * |
| primary | assured vs ensemble | unsafe | -1.8827 | [-2.2842, -1.4812] | 0.0020 | 0.0059 * |
| primary | assured vs DQN+shield | unsafe | -0.2120 | [-0.2893, -0.1347] | 0.0020 | 0.0059 * |
| primary | assured vs A*+monitor | collisions | -0.3773 | [-0.4023, -0.3523] | 0.0020 | 0.0059 * |
| primary | assured vs ensemble | collisions | -1.8576 | [-2.2631, -1.4520] | 0.0020 | 0.0059 * |
| primary | assured vs DQN+shield | collisions | -0.2798 | [-0.3788, -0.1808] | 0.0020 | 0.0059 * |
| primary | assured vs A*+monitor | energy_used | -4.2624 | [-5.4717, -3.0532] | 0.0039 | 0.0059 * |
| primary | assured vs ensemble | energy_used | -2.2171 | [-2.6182, -1.8161] | 0.0020 | 0.0059 * |
| primary | assured vs DQN+shield | energy_used | -6.5356 | [-9.5215, -3.5496] | 0.0020 | 0.0059 * |
| primary | assured vs A*+monitor | intervention_rate | +0.0115 | [+0.0039, +0.0190] | 0.0117 | 0.0156 * |
| primary | assured vs ensemble | intervention_rate | +0.0327 | [+0.0252, +0.0403] | 0.0020 | 0.0059 * |
| primary | assured vs DQN+shield | intervention_rate | +0.0121 | [+0.0054, +0.0188] | 0.0078 | 0.0156 * |
| primary | assured vs A*+monitor | safe_stop_rate | -0.0047 | [-0.0066, -0.0028] | 0.0020 | 0.0059 * |
| primary | assured vs ensemble | safe_stop_rate | +0.0042 | [+0.0023, +0.0061] | 0.0078 | 0.0156 * |
| primary | assured vs DQN+shield | safe_stop_rate | +0.0042 | [+0.0023, +0.0061] | 0.0078 | 0.0156 * |
| primary | assured vs A*+monitor | depleted_rate | +0.0000 | [+0.0000, +0.0000] | 1.0000 | 1.0000 |
| primary | assured vs ensemble | depleted_rate | -0.0202 | [-0.0238, -0.0167] | 0.0020 | 0.0059 * |
| primary | assured vs DQN+shield | depleted_rate | -0.0284 | [-0.0340, -0.0229] | 0.0020 | 0.0059 * |
| secondary | assured vs A* | success | +0.0002 | [-0.0017, +0.0021] | 1.0000 | 1.0000 |
| secondary | action-OOD vs raw-OOD | success | -0.0013 | [-0.0029, +0.0002] | 0.1562 | 0.3125 |
| secondary | full vs monitor-only | success | +0.0091 | [+0.0060, +0.0122] | 0.0039 | 0.0117 * |
| secondary | assured vs A* | unsafe | -0.0831 | [-0.0872, -0.0791] | 0.0020 | 0.0059 * |
| secondary | action-OOD vs raw-OOD | unsafe | -0.0044 | [-0.0067, -0.0022] | 0.0078 | 0.0156 * |
| secondary | full vs monitor-only | unsafe | +0.0047 | [+0.0019, +0.0074] | 0.0156 | 0.0156 * |
| secondary | assured vs A* | collisions | -0.4507 | [-0.4757, -0.4257] | 0.0020 | 0.0059 * |
| secondary | action-OOD vs raw-OOD | collisions | -0.0011 | [-0.0083, +0.0061] | 0.7969 | 0.7969 |
| secondary | full vs monitor-only | collisions | +0.0036 | [-0.0037, +0.0108] | 0.3203 | 0.6406 |
| secondary | assured vs A* | energy_used | -3.1447 | [-4.3539, -1.9354] | 0.0039 | 0.0078 * |
| secondary | action-OOD vs raw-OOD | energy_used | +0.3198 | [+0.0482, +0.5913] | 0.0254 | 0.0254 * |
| secondary | full vs monitor-only | energy_used | -0.6684 | [-0.8672, -0.4697] | 0.0020 | 0.0059 * |
| secondary | assured vs A* | intervention_rate | +nan | [+nan, +nan] | nan | nan |
| secondary | action-OOD vs raw-OOD | intervention_rate | -0.0172 | [-0.0239, -0.0106] | 0.0020 | 0.0039 * |
| secondary | full vs monitor-only | intervention_rate | +0.0272 | [+0.0201, +0.0344] | 0.0020 | 0.0039 * |
| secondary | assured vs A* | safe_stop_rate | +0.0042 | [+0.0023, +0.0061] | 0.0078 | 0.0156 * |
| secondary | action-OOD vs raw-OOD | safe_stop_rate | +0.0013 | [-0.0002, +0.0029] | 0.1562 | 0.1562 |
| secondary | full vs monitor-only | safe_stop_rate | -0.0091 | [-0.0122, -0.0060] | 0.0039 | 0.0117 * |
| secondary | assured vs A* | depleted_rate | -0.0044 | [-0.0044, -0.0044] | 0.0020 | 0.0059 * |
| secondary | action-OOD vs raw-OOD | depleted_rate | +0.0000 | [+0.0000, +0.0000] | 1.0000 | 1.0000 |
| secondary | full vs monitor-only | depleted_rate | +0.0000 | [+0.0000, +0.0000] | 1.0000 | 1.0000 |
