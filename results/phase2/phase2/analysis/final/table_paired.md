Paired differences (A − B) over system seeds on identical maps; 95% t interval; exact sign-flip p; Holm-adjusted across the conditions within each (comparison, metric).
For success higher is better; for collisions/unsafe lower is better.


### primary comparisons — success

| Condition | Comparison | n | A − B | 95% CI | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|
| id | assured vs A* | 10 | -0.0158 | [-0.0202, -0.0114] | 0.0020 | 0.0098 * |
| terrain_shift | assured vs A* | 10 | -0.0410 | [-0.0492, -0.0328] | 0.0020 | 0.0098 * |
| sensor_shift | assured vs A* | 10 | -0.0734 | [-0.0770, -0.0698] | 0.0020 | 0.0098 * |
| dynamics_shift | assured vs A* | 10 | -0.0204 | [-0.0242, -0.0166] | 0.0020 | 0.0098 * |
| combined_shift | assured vs A* | 10 | -0.0884 | [-0.0941, -0.0827] | 0.0020 | 0.0098 * |
| id | assured vs A*+monitor | 10 | +0.0022 | [-0.0022, +0.0066] | 0.3320 | 0.6641 |
| terrain_shift | assured vs A*+monitor | 10 | -0.0230 | [-0.0312, -0.0148] | 0.0020 | 0.0098 * |
| sensor_shift | assured vs A*+monitor | 10 | -0.0054 | [-0.0090, -0.0018] | 0.0156 | 0.0625 |
| dynamics_shift | assured vs A*+monitor | 10 | +0.0016 | [-0.0022, +0.0054] | 0.5000 | 0.6641 |
| combined_shift | assured vs A*+monitor | 10 | -0.0064 | [-0.0121, -0.0007] | 0.0469 | 0.1406 |
| id | assured vs DQN | 10 | +0.0612 | [+0.0439, +0.0785] | 0.0020 | 0.0098 * |
| terrain_shift | assured vs DQN | 10 | +0.1310 | [+0.1070, +0.1550] | 0.0020 | 0.0098 * |
| sensor_shift | assured vs DQN | 10 | +0.0152 | [+0.0001, +0.0303] | 0.0312 | 0.0312 * |
| dynamics_shift | assured vs DQN | 10 | +0.0778 | [+0.0606, +0.0950] | 0.0020 | 0.0098 * |
| combined_shift | assured vs DQN | 10 | +0.1892 | [+0.1323, +0.2461] | 0.0020 | 0.0098 * |
| id | assured vs DQN+shield | 10 | +0.0482 | [+0.0317, +0.0647] | 0.0020 | 0.0098 * |
| terrain_shift | assured vs DQN+shield | 10 | +0.1074 | [+0.0865, +0.1283] | 0.0020 | 0.0098 * |
| sensor_shift | assured vs DQN+shield | 10 | +0.0042 | [-0.0153, +0.0237] | 0.7461 | 0.7461 |
| dynamics_shift | assured vs DQN+shield | 10 | +0.0620 | [+0.0486, +0.0754] | 0.0020 | 0.0098 * |
| combined_shift | assured vs DQN+shield | 10 | +0.1986 | [+0.1413, +0.2559] | 0.0020 | 0.0098 * |
| id | assured vs PPO+shield | 10 | +0.0720 | [+0.0490, +0.0950] | 0.0020 | 0.0098 * |
| terrain_shift | assured vs PPO+shield | 10 | +0.1466 | [+0.1113, +0.1819] | 0.0020 | 0.0098 * |
| sensor_shift | assured vs PPO+shield | 10 | +0.0204 | [-0.0024, +0.0432] | 0.0840 | 0.0840 |
| dynamics_shift | assured vs PPO+shield | 10 | +0.0848 | [+0.0634, +0.1062] | 0.0020 | 0.0098 * |
| combined_shift | assured vs PPO+shield | 10 | +0.2096 | [+0.1671, +0.2521] | 0.0020 | 0.0098 * |
| id | assured vs ensemble | 10 | +0.0162 | [+0.0100, +0.0224] | 0.0020 | 0.0098 * |
| terrain_shift | assured vs ensemble | 10 | +0.0424 | [+0.0360, +0.0488] | 0.0020 | 0.0098 * |
| sensor_shift | assured vs ensemble | 10 | -0.0376 | [-0.0440, -0.0312] | 0.0020 | 0.0098 * |
| dynamics_shift | assured vs ensemble | 10 | +0.0230 | [+0.0180, +0.0280] | 0.0020 | 0.0098 * |
| combined_shift | assured vs ensemble | 10 | -0.0072 | [-0.0205, +0.0061] | 0.2734 | 0.2734 |
| id | assured vs uncertainty-gated | 10 | -0.0040 | [-0.0072, -0.0008] | 0.0312 | 0.1172 |
| terrain_shift | assured vs uncertainty-gated | 10 | +0.0008 | [-0.0054, +0.0070] | 0.8301 | 0.8438 |
| sensor_shift | assured vs uncertainty-gated | 10 | -0.0572 | [-0.0620, -0.0524] | 0.0020 | 0.0098 * |
| dynamics_shift | assured vs uncertainty-gated | 10 | -0.0018 | [-0.0062, +0.0026] | 0.4219 | 0.8438 |
| combined_shift | assured vs uncertainty-gated | 10 | -0.0180 | [-0.0321, -0.0039] | 0.0293 | 0.1172 |

### primary comparisons — collisions

| Condition | Comparison | n | A − B | 95% CI | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|
| id | assured vs A* | 10 | -0.5048 | [-0.5217, -0.4879] | 0.0020 | 0.0098 * |
| terrain_shift | assured vs A* | 10 | -0.6658 | [-0.6785, -0.6531] | 0.0020 | 0.0098 * |
| sensor_shift | assured vs A* | 10 | -0.8624 | [-0.8779, -0.8469] | 0.0020 | 0.0098 * |
| dynamics_shift | assured vs A* | 10 | -0.9792 | [-1.0261, -0.9323] | 0.0020 | 0.0098 * |
| combined_shift | assured vs A* | 10 | -1.2108 | [-1.2256, -1.1960] | 0.0020 | 0.0098 * |
| id | assured vs A*+monitor | 10 | -0.3488 | [-0.3657, -0.3319] | 0.0020 | 0.0098 * |
| terrain_shift | assured vs A*+monitor | 10 | -0.3538 | [-0.3665, -0.3411] | 0.0020 | 0.0098 * |
| sensor_shift | assured vs A*+monitor | 10 | -0.1544 | [-0.1699, -0.1389] | 0.0020 | 0.0098 * |
| dynamics_shift | assured vs A*+monitor | 10 | -0.8912 | [-0.9381, -0.8443] | 0.0020 | 0.0098 * |
| combined_shift | assured vs A*+monitor | 10 | -0.2088 | [-0.2236, -0.1940] | 0.0020 | 0.0098 * |
| id | assured vs DQN | 10 | -5.7056 | [-7.7976, -3.6136] | 0.0020 | 0.0098 * |
| terrain_shift | assured vs DQN | 10 | -7.6476 | [-8.7169, -6.5783] | 0.0020 | 0.0098 * |
| sensor_shift | assured vs DQN | 10 | -4.4508 | [-5.3644, -3.5372] | 0.0020 | 0.0098 * |
| dynamics_shift | assured vs DQN | 10 | -4.8208 | [-6.2329, -3.4087] | 0.0020 | 0.0098 * |
| combined_shift | assured vs DQN | 10 | -4.8600 | [-5.4653, -4.2547] | 0.0020 | 0.0098 * |
| id | assured vs DQN+shield | 10 | -0.3550 | [-0.5353, -0.1747] | 0.0020 | 0.0098 * |
| terrain_shift | assured vs DQN+shield | 10 | -0.7316 | [-0.9136, -0.5496] | 0.0020 | 0.0098 * |
| sensor_shift | assured vs DQN+shield | 10 | -0.0512 | [-0.2074, +0.1050] | 0.4707 | 0.4707 |
| dynamics_shift | assured vs DQN+shield | 10 | -0.4500 | [-0.6309, -0.2691] | 0.0020 | 0.0098 * |
| combined_shift | assured vs DQN+shield | 10 | -0.3668 | [-0.5773, -0.1563] | 0.0020 | 0.0098 * |
| id | assured vs PPO+shield | 10 | -1.0854 | [-1.5660, -0.6048] | 0.0020 | 0.0098 * |
| terrain_shift | assured vs PPO+shield | 10 | -1.6812 | [-2.4557, -0.9067] | 0.0020 | 0.0098 * |
| sensor_shift | assured vs PPO+shield | 10 | -0.6560 | [-1.0566, -0.2554] | 0.0020 | 0.0098 * |
| dynamics_shift | assured vs PPO+shield | 10 | -1.0738 | [-1.4716, -0.6760] | 0.0020 | 0.0098 * |
| combined_shift | assured vs PPO+shield | 10 | -1.4652 | [-2.2347, -0.6957] | 0.0020 | 0.0098 * |
| id | assured vs ensemble | 10 | -1.9164 | [-2.3997, -1.4331] | 0.0020 | 0.0098 * |
| terrain_shift | assured vs ensemble | 10 | -2.8544 | [-3.3866, -2.3222] | 0.0020 | 0.0098 * |
| sensor_shift | assured vs ensemble | 10 | -1.8072 | [-2.1381, -1.4763] | 0.0020 | 0.0098 * |
| dynamics_shift | assured vs ensemble | 10 | -1.5464 | [-2.0106, -1.0822] | 0.0020 | 0.0098 * |
| combined_shift | assured vs ensemble | 10 | -1.5540 | [-1.8211, -1.2869] | 0.0020 | 0.0098 * |
| id | assured vs uncertainty-gated | 10 | -1.1142 | [-1.3401, -0.8883] | 0.0020 | 0.0098 * |
| terrain_shift | assured vs uncertainty-gated | 10 | -1.0384 | [-1.4679, -0.6089] | 0.0020 | 0.0098 * |
| sensor_shift | assured vs uncertainty-gated | 10 | -0.9970 | [-1.3369, -0.6571] | 0.0020 | 0.0098 * |
| dynamics_shift | assured vs uncertainty-gated | 10 | -0.7602 | [-0.9737, -0.5467] | 0.0020 | 0.0098 * |
| combined_shift | assured vs uncertainty-gated | 10 | -0.1978 | [-0.4095, +0.0139] | 0.0566 | 0.0566 |

### primary comparisons — unsafe

| Condition | Comparison | n | A − B | 95% CI | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|
| id | assured vs A* | 10 | -0.2350 | [-0.2400, -0.2300] | 0.0020 | 0.0098 * |
| terrain_shift | assured vs A* | 10 | -0.3616 | [-0.3665, -0.3567] | 0.0020 | 0.0098 * |
| sensor_shift | assured vs A* | 10 | -0.8178 | [-0.8360, -0.7996] | 0.0020 | 0.0098 * |
| dynamics_shift | assured vs A* | 10 | -0.2564 | [-0.2605, -0.2523] | 0.0020 | 0.0098 * |
| combined_shift | assured vs A* | 10 | -0.9328 | [-0.9388, -0.9268] | 0.0020 | 0.0098 * |
| id | assured vs A*+monitor | 10 | -0.0610 | [-0.0660, -0.0560] | 0.0020 | 0.0098 * |
| terrain_shift | assured vs A*+monitor | 10 | -0.0576 | [-0.0625, -0.0527] | 0.0020 | 0.0098 * |
| sensor_shift | assured vs A*+monitor | 10 | -0.0978 | [-0.1160, -0.0796] | 0.0020 | 0.0098 * |
| dynamics_shift | assured vs A*+monitor | 10 | -0.0724 | [-0.0765, -0.0683] | 0.0020 | 0.0098 * |
| combined_shift | assured vs A*+monitor | 10 | -0.0708 | [-0.0768, -0.0648] | 0.0020 | 0.0098 * |
| id | assured vs DQN | 10 | -5.7558 | [-7.8410, -3.6706] | 0.0020 | 0.0098 * |
| terrain_shift | assured vs DQN | 10 | -7.8336 | [-8.9083, -6.7589] | 0.0020 | 0.0098 * |
| sensor_shift | assured vs DQN | 10 | -4.6176 | [-5.5080, -3.7272] | 0.0020 | 0.0098 * |
| dynamics_shift | assured vs DQN | 10 | -4.9742 | [-6.3295, -3.6189] | 0.0020 | 0.0098 * |
| combined_shift | assured vs DQN | 10 | -5.7278 | [-6.3342, -5.1214] | 0.0020 | 0.0098 * |
| id | assured vs DQN+shield | 10 | -0.2780 | [-0.4167, -0.1393] | 0.0020 | 0.0098 * |
| terrain_shift | assured vs DQN+shield | 10 | -0.6670 | [-0.8412, -0.4928] | 0.0020 | 0.0098 * |
| sensor_shift | assured vs DQN+shield | 10 | -0.1000 | [-0.2444, +0.0444] | 0.1543 | 0.1543 |
| dynamics_shift | assured vs DQN+shield | 10 | -0.2980 | [-0.3758, -0.2202] | 0.0020 | 0.0098 * |
| combined_shift | assured vs DQN+shield | 10 | -0.6748 | [-0.9413, -0.4083] | 0.0020 | 0.0098 * |
| id | assured vs PPO+shield | 10 | -1.0166 | [-1.4937, -0.5395] | 0.0020 | 0.0098 * |
| terrain_shift | assured vs PPO+shield | 10 | -1.5884 | [-2.3671, -0.8097] | 0.0020 | 0.0098 * |
| sensor_shift | assured vs PPO+shield | 10 | -0.7130 | [-1.0960, -0.3300] | 0.0020 | 0.0098 * |
| dynamics_shift | assured vs PPO+shield | 10 | -0.9374 | [-1.3399, -0.5349] | 0.0020 | 0.0098 * |
| combined_shift | assured vs PPO+shield | 10 | -1.7446 | [-2.5562, -0.9330] | 0.0020 | 0.0098 * |
| id | assured vs ensemble | 10 | -1.9574 | [-2.4434, -1.4714] | 0.0020 | 0.0098 * |
| terrain_shift | assured vs ensemble | 10 | -2.9658 | [-3.5146, -2.4170] | 0.0020 | 0.0098 * |
| sensor_shift | assured vs ensemble | 10 | -1.9852 | [-2.3088, -1.6616] | 0.0020 | 0.0098 * |
| dynamics_shift | assured vs ensemble | 10 | -1.7100 | [-2.1894, -1.2306] | 0.0020 | 0.0098 * |
| combined_shift | assured vs ensemble | 10 | -2.1988 | [-2.4518, -1.9458] | 0.0020 | 0.0098 * |
| id | assured vs uncertainty-gated | 10 | -1.1408 | [-1.3774, -0.9042] | 0.0020 | 0.0098 * |
| terrain_shift | assured vs uncertainty-gated | 10 | -1.0768 | [-1.5147, -0.6389] | 0.0020 | 0.0098 * |
| sensor_shift | assured vs uncertainty-gated | 10 | -1.1560 | [-1.4910, -0.8210] | 0.0020 | 0.0098 * |
| dynamics_shift | assured vs uncertainty-gated | 10 | -0.8630 | [-1.0803, -0.6457] | 0.0020 | 0.0098 * |
| combined_shift | assured vs uncertainty-gated | 10 | -0.7100 | [-0.9219, -0.4981] | 0.0020 | 0.0098 * |

### secondary comparisons — success

| Condition | Comparison | n | A − B | 95% CI | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|
| id | stop vs no-stop | 10 | -0.0052 | [-0.0064, -0.0040] | 0.0020 | 0.0098 * |
| terrain_shift | stop vs no-stop | 10 | -0.0096 | [-0.0123, -0.0069] | 0.0020 | 0.0098 * |
| sensor_shift | stop vs no-stop | 10 | -0.0550 | [-0.0578, -0.0522] | 0.0020 | 0.0098 * |
| dynamics_shift | stop vs no-stop | 10 | -0.0050 | [-0.0064, -0.0036] | 0.0020 | 0.0098 * |
| combined_shift | stop vs no-stop | 10 | -0.0374 | [-0.0399, -0.0349] | 0.0020 | 0.0098 * |
| id | full vs monitor-only | 10 | +0.0122 | [+0.0070, +0.0174] | 0.0020 | 0.0098 * |
| terrain_shift | full vs monitor-only | 10 | +0.0310 | [+0.0250, +0.0370] | 0.0020 | 0.0098 * |
| sensor_shift | full vs monitor-only | 10 | -0.0146 | [-0.0215, -0.0077] | 0.0020 | 0.0098 * |
| dynamics_shift | full vs monitor-only | 10 | +0.0178 | [+0.0135, +0.0221] | 0.0020 | 0.0098 * |
| combined_shift | full vs monitor-only | 10 | +0.0266 | [+0.0151, +0.0381] | 0.0020 | 0.0098 * |
| id | full vs no-OOD | 10 | -0.0006 | [-0.0020, +0.0008] | 0.5312 | 1.0000 |
| terrain_shift | full vs no-OOD | 10 | +0.0002 | [-0.0020, +0.0024] | 1.0000 | 1.0000 |
| sensor_shift | full vs no-OOD | 10 | -0.0320 | [-0.0363, -0.0277] | 0.0020 | 0.0098 * |
| dynamics_shift | full vs no-OOD | 10 | +0.0002 | [-0.0020, +0.0024] | 1.0000 | 1.0000 |
| combined_shift | full vs no-OOD | 10 | +0.0054 | [-0.0113, +0.0221] | 0.5547 | 1.0000 |
| id | full vs no-uncertainty | 10 | +0.0098 | [+0.0062, +0.0134] | 0.0020 | 0.0098 * |
| terrain_shift | full vs no-uncertainty | 10 | +0.0270 | [+0.0224, +0.0316] | 0.0020 | 0.0098 * |
| sensor_shift | full vs no-uncertainty | 10 | +0.0000 | [+0.0000, +0.0000] | 1.0000 | 1.0000 |
| dynamics_shift | full vs no-uncertainty | 10 | +0.0090 | [+0.0039, +0.0141] | 0.0078 | 0.0234 * |
| combined_shift | full vs no-uncertainty | 10 | +0.0000 | [+0.0000, +0.0000] | 1.0000 | 1.0000 |
| id | full vs no-monitor | 10 | -0.0036 | [-0.0061, -0.0011] | 0.0078 | 0.0234 * |
| terrain_shift | full vs no-monitor | 10 | -0.0000 | [-0.0032, +0.0032] | 1.0000 | 1.0000 |
| sensor_shift | full vs no-monitor | 10 | -0.0040 | [-0.0055, -0.0025] | 0.0020 | 0.0098 * |
| dynamics_shift | full vs no-monitor | 10 | -0.0010 | [-0.0028, +0.0008] | 0.3672 | 0.7344 |
| combined_shift | full vs no-monitor | 10 | -0.0050 | [-0.0078, -0.0022] | 0.0020 | 0.0098 * |
| id | monitor-only vs ensemble | 10 | +0.0040 | [-0.0010, +0.0090] | 0.1270 | 0.1270 |
| terrain_shift | monitor-only vs ensemble | 10 | +0.0114 | [+0.0067, +0.0161] | 0.0039 | 0.0117 * |
| sensor_shift | monitor-only vs ensemble | 10 | -0.0230 | [-0.0299, -0.0161] | 0.0020 | 0.0098 * |
| dynamics_shift | monitor-only vs ensemble | 10 | +0.0052 | [+0.0027, +0.0077] | 0.0039 | 0.0117 * |
| combined_shift | monitor-only vs ensemble | 10 | -0.0338 | [-0.0464, -0.0212] | 0.0020 | 0.0098 * |

### secondary comparisons — collisions

| Condition | Comparison | n | A − B | 95% CI | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|
| id | stop vs no-stop | 10 | -0.0298 | [-0.0375, -0.0221] | 0.0020 | 0.0098 * |
| terrain_shift | stop vs no-stop | 10 | -0.0920 | [-0.1072, -0.0768] | 0.0020 | 0.0098 * |
| sensor_shift | stop vs no-stop | 10 | -0.0802 | [-0.0895, -0.0709] | 0.0020 | 0.0098 * |
| dynamics_shift | stop vs no-stop | 10 | -0.0344 | [-0.0422, -0.0266] | 0.0020 | 0.0098 * |
| combined_shift | stop vs no-stop | 10 | -0.2342 | [-0.2466, -0.2218] | 0.0020 | 0.0098 * |
| id | full vs monitor-only | 10 | +0.0060 | [-0.0017, +0.0137] | 0.1250 | 0.1250 |
| terrain_shift | full vs monitor-only | 10 | +0.0344 | [+0.0201, +0.0487] | 0.0039 | 0.0098 * |
| sensor_shift | full vs monitor-only | 10 | +0.3956 | [+0.3518, +0.4394] | 0.0020 | 0.0098 * |
| dynamics_shift | full vs monitor-only | 10 | +0.0706 | [+0.0512, +0.0900] | 0.0020 | 0.0098 * |
| combined_shift | full vs monitor-only | 10 | +0.7408 | [+0.6798, +0.8018] | 0.0020 | 0.0098 * |
| id | full vs no-OOD | 10 | -0.0004 | [-0.0059, +0.0051] | 0.9316 | 0.9316 |
| terrain_shift | full vs no-OOD | 10 | +0.0052 | [-0.0032, +0.0136] | 0.2109 | 0.4219 |
| sensor_shift | full vs no-OOD | 10 | +0.3928 | [+0.3495, +0.4361] | 0.0020 | 0.0098 * |
| dynamics_shift | full vs no-OOD | 10 | +0.0412 | [+0.0234, +0.0590] | 0.0020 | 0.0098 * |
| combined_shift | full vs no-OOD | 10 | +0.6680 | [+0.5966, +0.7394] | 0.0020 | 0.0098 * |
| id | full vs no-uncertainty | 10 | +0.0064 | [+0.0014, +0.0114] | 0.0195 | 0.0586 |
| terrain_shift | full vs no-uncertainty | 10 | +0.0244 | [+0.0124, +0.0364] | 0.0059 | 0.0293 * |
| sensor_shift | full vs no-uncertainty | 10 | +0.0000 | [-0.0007, +0.0007] | 1.0000 | 1.0000 |
| dynamics_shift | full vs no-uncertainty | 10 | +0.0172 | [+0.0033, +0.0311] | 0.0098 | 0.0391 * |
| combined_shift | full vs no-uncertainty | 10 | +0.0000 | [+0.0000, +0.0000] | 1.0000 | 1.0000 |
| id | full vs no-monitor | 10 | -0.5726 | [-0.7479, -0.3973] | 0.0020 | 0.0098 * |
| terrain_shift | full vs no-monitor | 10 | -0.7682 | [-1.0825, -0.4539] | 0.0020 | 0.0098 * |
| sensor_shift | full vs no-monitor | 10 | -0.0244 | [-0.0353, -0.0135] | 0.0020 | 0.0098 * |
| dynamics_shift | full vs no-monitor | 10 | -0.3542 | [-0.4515, -0.2569] | 0.0020 | 0.0098 * |
| combined_shift | full vs no-monitor | 10 | -0.0134 | [-0.0209, -0.0059] | 0.0020 | 0.0098 * |
| id | monitor-only vs ensemble | 10 | -1.9224 | [-2.4044, -1.4404] | 0.0020 | 0.0098 * |
| terrain_shift | monitor-only vs ensemble | 10 | -2.8888 | [-3.4181, -2.3595] | 0.0020 | 0.0098 * |
| sensor_shift | monitor-only vs ensemble | 10 | -2.2028 | [-2.5028, -1.9028] | 0.0020 | 0.0098 * |
| dynamics_shift | monitor-only vs ensemble | 10 | -1.6170 | [-2.0779, -1.1561] | 0.0020 | 0.0098 * |
| combined_shift | monitor-only vs ensemble | 10 | -2.2948 | [-2.5230, -2.0666] | 0.0020 | 0.0098 * |

### secondary comparisons — unsafe

| Condition | Comparison | n | A − B | 95% CI | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|
| id | stop vs no-stop | 10 | -0.0282 | [-0.0353, -0.0211] | 0.0020 | 0.0098 * |
| terrain_shift | stop vs no-stop | 10 | -0.0810 | [-0.0941, -0.0679] | 0.0020 | 0.0098 * |
| sensor_shift | stop vs no-stop | 10 | -0.0596 | [-0.0656, -0.0536] | 0.0020 | 0.0098 * |
| dynamics_shift | stop vs no-stop | 10 | -0.0278 | [-0.0339, -0.0217] | 0.0020 | 0.0098 * |
| combined_shift | stop vs no-stop | 10 | -0.1158 | [-0.1238, -0.1078] | 0.0020 | 0.0098 * |
| id | full vs monitor-only | 10 | -0.0002 | [-0.0029, +0.0025] | 1.0000 | 1.0000 |
| terrain_shift | full vs monitor-only | 10 | +0.0026 | [-0.0001, +0.0053] | 0.0781 | 0.2344 |
| sensor_shift | full vs monitor-only | 10 | +0.2752 | [+0.2458, +0.3046] | 0.0020 | 0.0098 * |
| dynamics_shift | full vs monitor-only | 10 | +0.0018 | [-0.0009, +0.0045] | 0.2109 | 0.4219 |
| combined_shift | full vs monitor-only | 10 | +0.2666 | [+0.2420, +0.2912] | 0.0020 | 0.0098 * |
| id | full vs no-OOD | 10 | -0.0002 | [-0.0027, +0.0023] | 1.0000 | 1.0000 |
| terrain_shift | full vs no-OOD | 10 | +0.0018 | [-0.0005, +0.0041] | 0.1562 | 0.4688 |
| sensor_shift | full vs no-OOD | 10 | +0.2758 | [+0.2468, +0.3048] | 0.0020 | 0.0098 * |
| dynamics_shift | full vs no-OOD | 10 | +0.0004 | [-0.0032, +0.0040] | 0.9062 | 1.0000 |
| combined_shift | full vs no-OOD | 10 | +0.2420 | [+0.2142, +0.2698] | 0.0020 | 0.0098 * |
| id | full vs no-uncertainty | 10 | -0.0002 | [-0.0016, +0.0012] | 1.0000 | 1.0000 |
| terrain_shift | full vs no-uncertainty | 10 | +0.0002 | [-0.0014, +0.0018] | 1.0000 | 1.0000 |
| sensor_shift | full vs no-uncertainty | 10 | +0.0002 | [-0.0003, +0.0007] | 1.0000 | 1.0000 |
| dynamics_shift | full vs no-uncertainty | 10 | +0.0012 | [+0.0002, +0.0022] | 0.0625 | 0.3125 |
| combined_shift | full vs no-uncertainty | 10 | +0.0000 | [+0.0000, +0.0000] | 1.0000 | 1.0000 |
| id | full vs no-monitor | 10 | -0.5908 | [-0.7742, -0.4074] | 0.0020 | 0.0098 * |
| terrain_shift | full vs no-monitor | 10 | -0.7964 | [-1.1175, -0.4753] | 0.0020 | 0.0098 * |
| sensor_shift | full vs no-monitor | 10 | -0.0182 | [-0.0294, -0.0070] | 0.0039 | 0.0098 * |
| dynamics_shift | full vs no-monitor | 10 | -0.3944 | [-0.5003, -0.2885] | 0.0020 | 0.0098 * |
| combined_shift | full vs no-monitor | 10 | -0.0048 | [-0.0096, +0.0000] | 0.0645 | 0.0645 |
| id | monitor-only vs ensemble | 10 | -1.9572 | [-2.4440, -1.4704] | 0.0020 | 0.0098 * |
| terrain_shift | monitor-only vs ensemble | 10 | -2.9684 | [-3.5174, -2.4194] | 0.0020 | 0.0098 * |
| sensor_shift | monitor-only vs ensemble | 10 | -2.2604 | [-2.5629, -1.9579] | 0.0020 | 0.0098 * |
| dynamics_shift | monitor-only vs ensemble | 10 | -1.7118 | [-2.1910, -1.2326] | 0.0020 | 0.0098 * |
| combined_shift | monitor-only vs ensemble | 10 | -2.4654 | [-2.7123, -2.2185] | 0.0020 | 0.0098 * |
