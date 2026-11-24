Paired differences (A − B) over system seeds on identical maps; 95% t interval; exact sign-flip p; Holm-adjusted across the conditions within each (comparison, metric).
For success higher is better; for collisions/unsafe lower is better.


### primary comparisons — success

| Condition | Comparison | n | A − B | 95% CI | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|
| id | assured vs A* | 10 | -0.0170 | [-0.0266, -0.0074] | 0.0078 | 0.0156 * |
| terrain_shift | assured vs A* | 10 | -0.0560 | [-0.0726, -0.0394] | 0.0020 | 0.0098 * |
| sensor_shift | assured vs A* | 10 | -0.0320 | [-0.0376, -0.0264] | 0.0020 | 0.0098 * |
| dynamics_shift | assured vs A* | 10 | -0.0140 | [-0.0230, -0.0050] | 0.0156 | 0.0156 * |
| combined_shift | assured vs A* | 10 | -0.0950 | [-0.1011, -0.0889] | 0.0020 | 0.0098 * |
| id | assured vs A*+monitor | 10 | +0.0030 | [-0.0066, +0.0126] | 0.6406 | 0.6406 |
| terrain_shift | assured vs A*+monitor | 10 | -0.0360 | [-0.0526, -0.0194] | 0.0020 | 0.0098 * |
| sensor_shift | assured vs A*+monitor | 10 | +0.0280 | [+0.0224, +0.0336] | 0.0020 | 0.0098 * |
| dynamics_shift | assured vs A*+monitor | 10 | +0.0160 | [+0.0070, +0.0250] | 0.0156 | 0.0312 * |
| combined_shift | assured vs A*+monitor | 10 | +0.0350 | [+0.0289, +0.0411] | 0.0020 | 0.0098 * |
| id | assured vs DQN | 10 | +0.0270 | [+0.0148, +0.0392] | 0.0039 | 0.0098 * |
| terrain_shift | assured vs DQN | 10 | +0.0960 | [+0.0596, +0.1324] | 0.0020 | 0.0098 * |
| sensor_shift | assured vs DQN | 10 | +0.0550 | [+0.0368, +0.0732] | 0.0020 | 0.0098 * |
| dynamics_shift | assured vs DQN | 10 | +0.0690 | [+0.0382, +0.0998] | 0.0039 | 0.0098 * |
| combined_shift | assured vs DQN | 10 | +0.2030 | [+0.1313, +0.2747] | 0.0020 | 0.0098 * |
| id | assured vs DQN+shield | 10 | +0.0240 | [+0.0032, +0.0448] | 0.0234 | 0.0234 * |
| terrain_shift | assured vs DQN+shield | 10 | +0.0940 | [+0.0588, +0.1292] | 0.0020 | 0.0098 * |
| sensor_shift | assured vs DQN+shield | 10 | +0.0450 | [+0.0256, +0.0644] | 0.0039 | 0.0117 * |
| dynamics_shift | assured vs DQN+shield | 10 | +0.0560 | [+0.0372, +0.0748] | 0.0039 | 0.0117 * |
| combined_shift | assured vs DQN+shield | 10 | +0.2430 | [+0.1619, +0.3241] | 0.0020 | 0.0098 * |
| id | assured vs PPO+shield | 10 | +0.0530 | [+0.0219, +0.0841] | 0.0078 | 0.0098 * |
| terrain_shift | assured vs PPO+shield | 10 | +0.1180 | [+0.0781, +0.1579] | 0.0020 | 0.0098 * |
| sensor_shift | assured vs PPO+shield | 10 | +0.0530 | [+0.0291, +0.0769] | 0.0020 | 0.0098 * |
| dynamics_shift | assured vs PPO+shield | 10 | +0.0840 | [+0.0658, +0.1022] | 0.0020 | 0.0098 * |
| combined_shift | assured vs PPO+shield | 10 | +0.2600 | [+0.1842, +0.3358] | 0.0020 | 0.0098 * |
| id | assured vs ensemble | 10 | +0.0210 | [+0.0101, +0.0319] | 0.0078 | 0.0312 * |
| terrain_shift | assured vs ensemble | 10 | +0.0190 | [-0.0052, +0.0432] | 0.1367 | 0.2734 |
| sensor_shift | assured vs ensemble | 10 | +0.0100 | [-0.0001, +0.0201] | 0.0859 | 0.2578 |
| dynamics_shift | assured vs ensemble | 10 | +0.0290 | [+0.0211, +0.0369] | 0.0020 | 0.0098 * |
| combined_shift | assured vs ensemble | 10 | -0.0090 | [-0.0307, +0.0127] | 0.4258 | 0.4258 |
| id | assured vs uncertainty-gated | 10 | +0.0000 | [-0.0034, +0.0034] | 1.0000 | 1.0000 |
| terrain_shift | assured vs uncertainty-gated | 10 | +0.0030 | [-0.0128, +0.0188] | 0.7734 | 1.0000 |
| sensor_shift | assured vs uncertainty-gated | 10 | -0.0100 | [-0.0189, -0.0011] | 0.0605 | 0.2422 |
| dynamics_shift | assured vs uncertainty-gated | 10 | +0.0120 | [+0.0054, +0.0186] | 0.0078 | 0.0391 * |
| combined_shift | assured vs uncertainty-gated | 10 | -0.0160 | [-0.0443, +0.0123] | 0.2637 | 0.7910 |

### primary comparisons — collisions

| Condition | Comparison | n | A − B | 95% CI | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|
| id | assured vs A* | 10 | -0.4530 | [-0.4899, -0.4161] | 0.0020 | 0.0098 * |
| terrain_shift | assured vs A* | 10 | -0.4880 | [-0.5266, -0.4494] | 0.0020 | 0.0098 * |
| sensor_shift | assured vs A* | 10 | -0.9420 | [-0.9895, -0.8945] | 0.0020 | 0.0098 * |
| dynamics_shift | assured vs A* | 10 | -1.2960 | [-1.3550, -1.2370] | 0.0020 | 0.0098 * |
| combined_shift | assured vs A* | 10 | -0.9680 | [-1.0166, -0.9194] | 0.0020 | 0.0098 * |
| id | assured vs A*+monitor | 10 | -0.2830 | [-0.3199, -0.2461] | 0.0020 | 0.0098 * |
| terrain_shift | assured vs A*+monitor | 10 | -0.2680 | [-0.3066, -0.2294] | 0.0020 | 0.0098 * |
| sensor_shift | assured vs A*+monitor | 10 | -0.0120 | [-0.0595, +0.0355] | 0.6074 | 0.6074 |
| dynamics_shift | assured vs A*+monitor | 10 | -0.8560 | [-0.9150, -0.7970] | 0.0020 | 0.0098 * |
| combined_shift | assured vs A*+monitor | 10 | -0.1180 | [-0.1666, -0.0694] | 0.0039 | 0.0098 * |
| id | assured vs DQN | 10 | -4.5440 | [-6.0141, -3.0739] | 0.0020 | 0.0098 * |
| terrain_shift | assured vs DQN | 10 | -6.9950 | [-8.2331, -5.7569] | 0.0020 | 0.0098 * |
| sensor_shift | assured vs DQN | 10 | -4.5340 | [-5.7926, -3.2754] | 0.0020 | 0.0098 * |
| dynamics_shift | assured vs DQN | 10 | -4.5100 | [-6.3871, -2.6329] | 0.0020 | 0.0098 * |
| combined_shift | assured vs DQN | 10 | -5.0720 | [-5.8867, -4.2573] | 0.0020 | 0.0098 * |
| id | assured vs DQN+shield | 10 | -0.1880 | [-0.2958, -0.0802] | 0.0078 | 0.0156 * |
| terrain_shift | assured vs DQN+shield | 10 | -0.8640 | [-1.2212, -0.5068] | 0.0020 | 0.0098 * |
| sensor_shift | assured vs DQN+shield | 10 | -0.0310 | [-0.2690, +0.2070] | 0.7910 | 0.7910 |
| dynamics_shift | assured vs DQN+shield | 10 | -0.6050 | [-0.8069, -0.4031] | 0.0020 | 0.0098 * |
| combined_shift | assured vs DQN+shield | 10 | -0.7490 | [-1.1358, -0.3622] | 0.0039 | 0.0117 * |
| id | assured vs PPO+shield | 10 | -0.6600 | [-1.0547, -0.2653] | 0.0020 | 0.0098 * |
| terrain_shift | assured vs PPO+shield | 10 | -1.9100 | [-2.8142, -1.0058] | 0.0020 | 0.0098 * |
| sensor_shift | assured vs PPO+shield | 10 | -0.5330 | [-0.9128, -0.1532] | 0.0059 | 0.0098 * |
| dynamics_shift | assured vs PPO+shield | 10 | -0.6890 | [-1.1715, -0.2065] | 0.0020 | 0.0098 * |
| combined_shift | assured vs PPO+shield | 10 | -2.0410 | [-3.2825, -0.7995] | 0.0020 | 0.0098 * |
| id | assured vs ensemble | 10 | -1.3890 | [-1.8049, -0.9731] | 0.0020 | 0.0098 * |
| terrain_shift | assured vs ensemble | 10 | -3.6420 | [-4.6395, -2.6445] | 0.0020 | 0.0098 * |
| sensor_shift | assured vs ensemble | 10 | -1.3230 | [-1.6103, -1.0357] | 0.0020 | 0.0098 * |
| dynamics_shift | assured vs ensemble | 10 | -1.0190 | [-1.5510, -0.4870] | 0.0020 | 0.0098 * |
| combined_shift | assured vs ensemble | 10 | -1.9470 | [-2.4295, -1.4645] | 0.0020 | 0.0098 * |
| id | assured vs uncertainty-gated | 10 | -0.6860 | [-0.9598, -0.4122] | 0.0020 | 0.0098 * |
| terrain_shift | assured vs uncertainty-gated | 10 | -1.4030 | [-1.7961, -1.0099] | 0.0020 | 0.0098 * |
| sensor_shift | assured vs uncertainty-gated | 10 | -0.9040 | [-1.2110, -0.5970] | 0.0020 | 0.0098 * |
| dynamics_shift | assured vs uncertainty-gated | 10 | -0.4470 | [-0.6500, -0.2440] | 0.0020 | 0.0098 * |
| combined_shift | assured vs uncertainty-gated | 10 | -0.3340 | [-0.6194, -0.0486] | 0.0312 | 0.0312 * |

### primary comparisons — unsafe

| Condition | Comparison | n | A − B | 95% CI | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|
| id | assured vs A* | 10 | -0.1900 | [-0.2035, -0.1765] | 0.0020 | 0.0098 * |
| terrain_shift | assured vs A* | 10 | -0.2110 | [-0.2234, -0.1986] | 0.0020 | 0.0098 * |
| sensor_shift | assured vs A* | 10 | -0.7820 | [-0.8186, -0.7454] | 0.0020 | 0.0098 * |
| dynamics_shift | assured vs A* | 10 | -0.2990 | [-0.3139, -0.2841] | 0.0020 | 0.0098 * |
| combined_shift | assured vs A* | 10 | -0.8160 | [-0.8336, -0.7984] | 0.0020 | 0.0098 * |
| id | assured vs A*+monitor | 10 | -0.0400 | [-0.0535, -0.0265] | 0.0020 | 0.0098 * |
| terrain_shift | assured vs A*+monitor | 10 | -0.0610 | [-0.0734, -0.0486] | 0.0020 | 0.0098 * |
| sensor_shift | assured vs A*+monitor | 10 | -0.0220 | [-0.0586, +0.0146] | 0.2246 | 0.2246 |
| dynamics_shift | assured vs A*+monitor | 10 | -0.1190 | [-0.1339, -0.1041] | 0.0020 | 0.0098 * |
| combined_shift | assured vs A*+monitor | 10 | -0.1460 | [-0.1636, -0.1284] | 0.0020 | 0.0098 * |
| id | assured vs DQN | 10 | -4.6020 | [-6.1041, -3.0999] | 0.0020 | 0.0098 * |
| terrain_shift | assured vs DQN | 10 | -7.1650 | [-8.4563, -5.8737] | 0.0020 | 0.0098 * |
| sensor_shift | assured vs DQN | 10 | -4.7370 | [-5.9835, -3.4905] | 0.0020 | 0.0098 * |
| dynamics_shift | assured vs DQN | 10 | -4.6420 | [-6.5244, -2.7596] | 0.0020 | 0.0098 * |
| combined_shift | assured vs DQN | 10 | -5.9720 | [-6.8536, -5.0904] | 0.0020 | 0.0098 * |
| id | assured vs DQN+shield | 10 | -0.1590 | [-0.2759, -0.0421] | 0.0039 | 0.0098 * |
| terrain_shift | assured vs DQN+shield | 10 | -0.8280 | [-1.2337, -0.4223] | 0.0020 | 0.0098 * |
| sensor_shift | assured vs DQN+shield | 10 | -0.1160 | [-0.3301, +0.0981] | 0.2676 | 0.2676 |
| dynamics_shift | assured vs DQN+shield | 10 | -0.4830 | [-0.7213, -0.2447] | 0.0020 | 0.0098 * |
| combined_shift | assured vs DQN+shield | 10 | -1.1320 | [-1.5897, -0.6743] | 0.0020 | 0.0098 * |
| id | assured vs PPO+shield | 10 | -0.6070 | [-0.9491, -0.2649] | 0.0020 | 0.0098 * |
| terrain_shift | assured vs PPO+shield | 10 | -1.8630 | [-2.7735, -0.9525] | 0.0020 | 0.0098 * |
| sensor_shift | assured vs PPO+shield | 10 | -0.5720 | [-0.9290, -0.2150] | 0.0059 | 0.0098 * |
| dynamics_shift | assured vs PPO+shield | 10 | -0.5460 | [-0.9423, -0.1497] | 0.0020 | 0.0098 * |
| combined_shift | assured vs PPO+shield | 10 | -2.3840 | [-3.6962, -1.0718] | 0.0020 | 0.0098 * |
| id | assured vs ensemble | 10 | -1.4590 | [-1.8726, -1.0454] | 0.0020 | 0.0098 * |
| terrain_shift | assured vs ensemble | 10 | -3.7720 | [-4.7800, -2.7640] | 0.0020 | 0.0098 * |
| sensor_shift | assured vs ensemble | 10 | -1.5320 | [-1.8380, -1.2260] | 0.0020 | 0.0098 * |
| dynamics_shift | assured vs ensemble | 10 | -1.1270 | [-1.6697, -0.5843] | 0.0020 | 0.0098 * |
| combined_shift | assured vs ensemble | 10 | -2.6510 | [-3.1129, -2.1891] | 0.0020 | 0.0098 * |
| id | assured vs uncertainty-gated | 10 | -0.7330 | [-1.0028, -0.4632] | 0.0020 | 0.0098 * |
| terrain_shift | assured vs uncertainty-gated | 10 | -1.4600 | [-1.8710, -1.0490] | 0.0020 | 0.0098 * |
| sensor_shift | assured vs uncertainty-gated | 10 | -1.0940 | [-1.4158, -0.7722] | 0.0020 | 0.0098 * |
| dynamics_shift | assured vs uncertainty-gated | 10 | -0.4960 | [-0.7182, -0.2738] | 0.0020 | 0.0098 * |
| combined_shift | assured vs uncertainty-gated | 10 | -0.9070 | [-1.2186, -0.5954] | 0.0020 | 0.0098 * |

### secondary comparisons — success

| Condition | Comparison | n | A − B | 95% CI | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|
| id | stop vs no-stop | 10 | +0.0000 | [+0.0000, +0.0000] | 1.0000 | 1.0000 |
| terrain_shift | stop vs no-stop | 10 | -0.0130 | [-0.0206, -0.0054] | 0.0078 | 0.0234 * |
| sensor_shift | stop vs no-stop | 10 | -0.0220 | [-0.0276, -0.0164] | 0.0020 | 0.0098 * |
| dynamics_shift | stop vs no-stop | 10 | -0.0030 | [-0.0065, +0.0005] | 0.2500 | 0.5000 |
| combined_shift | stop vs no-stop | 10 | -0.0620 | [-0.0701, -0.0539] | 0.0020 | 0.0098 * |
| id | full vs monitor-only | 10 | +0.0160 | [+0.0037, +0.0283] | 0.0312 | 0.0938 |
| terrain_shift | full vs monitor-only | 10 | +0.0100 | [-0.0017, +0.0217] | 0.1250 | 0.1250 |
| sensor_shift | full vs monitor-only | 10 | +0.0290 | [+0.0138, +0.0442] | 0.0039 | 0.0156 * |
| dynamics_shift | full vs monitor-only | 10 | +0.0270 | [+0.0169, +0.0371] | 0.0020 | 0.0098 * |
| combined_shift | full vs monitor-only | 10 | +0.0240 | [+0.0040, +0.0440] | 0.0312 | 0.0938 |
| id | full vs no-OOD | 10 | -0.0010 | [-0.0051, +0.0031] | 1.0000 | 1.0000 |
| terrain_shift | full vs no-OOD | 10 | -0.0030 | [-0.0098, +0.0038] | 0.5312 | 1.0000 |
| sensor_shift | full vs no-OOD | 10 | +0.0190 | [+0.0092, +0.0288] | 0.0078 | 0.0391 * |
| dynamics_shift | full vs no-OOD | 10 | +0.0120 | [+0.0039, +0.0201] | 0.0078 | 0.0391 * |
| combined_shift | full vs no-OOD | 10 | +0.0170 | [-0.0002, +0.0342] | 0.0703 | 0.2109 |
| id | full vs no-uncertainty | 10 | +0.0070 | [+0.0011, +0.0129] | 0.0625 | 0.1875 |
| terrain_shift | full vs no-uncertainty | 10 | +0.0120 | [+0.0046, +0.0194] | 0.0156 | 0.0625 |
| sensor_shift | full vs no-uncertainty | 10 | +0.0000 | [+0.0000, +0.0000] | 1.0000 | 1.0000 |
| dynamics_shift | full vs no-uncertainty | 10 | +0.0110 | [+0.0069, +0.0151] | 0.0039 | 0.0195 * |
| combined_shift | full vs no-uncertainty | 10 | +0.0000 | [+0.0000, +0.0000] | 1.0000 | 1.0000 |
| id | full vs no-monitor | 10 | -0.0010 | [-0.0051, +0.0031] | 1.0000 | 1.0000 |
| terrain_shift | full vs no-monitor | 10 | +0.0050 | [-0.0105, +0.0205] | 0.5977 | 1.0000 |
| sensor_shift | full vs no-monitor | 10 | +0.0020 | [-0.0010, +0.0050] | 0.5000 | 1.0000 |
| dynamics_shift | full vs no-monitor | 10 | +0.0030 | [-0.0018, +0.0078] | 0.3750 | 1.0000 |
| combined_shift | full vs no-monitor | 10 | +0.0020 | [-0.0046, +0.0086] | 0.7500 | 1.0000 |
| id | monitor-only vs ensemble | 10 | +0.0050 | [-0.0001, +0.0101] | 0.1250 | 0.3750 |
| terrain_shift | monitor-only vs ensemble | 10 | +0.0090 | [-0.0132, +0.0312] | 0.4297 | 0.8594 |
| sensor_shift | monitor-only vs ensemble | 10 | -0.0190 | [-0.0346, -0.0034] | 0.0352 | 0.1406 |
| dynamics_shift | monitor-only vs ensemble | 10 | +0.0020 | [-0.0036, +0.0076] | 0.6875 | 0.8594 |
| combined_shift | monitor-only vs ensemble | 10 | -0.0330 | [-0.0554, -0.0106] | 0.0156 | 0.0781 |

### secondary comparisons — collisions

| Condition | Comparison | n | A − B | 95% CI | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|
| id | stop vs no-stop | 10 | -0.0190 | [-0.0314, -0.0066] | 0.0078 | 0.0156 * |
| terrain_shift | stop vs no-stop | 10 | -0.0900 | [-0.1274, -0.0526] | 0.0020 | 0.0098 * |
| sensor_shift | stop vs no-stop | 10 | -0.0390 | [-0.0431, -0.0349] | 0.0020 | 0.0098 * |
| dynamics_shift | stop vs no-stop | 10 | -0.0120 | [-0.0254, +0.0014] | 0.0625 | 0.0625 |
| combined_shift | stop vs no-stop | 10 | -0.2390 | [-0.2542, -0.2238] | 0.0020 | 0.0098 * |
| id | full vs monitor-only | 10 | +0.0240 | [+0.0034, +0.0446] | 0.0469 | 0.0859 |
| terrain_shift | full vs monitor-only | 10 | +0.0380 | [+0.0157, +0.0603] | 0.0078 | 0.0234 * |
| sensor_shift | full vs monitor-only | 10 | +0.4760 | [+0.4291, +0.5229] | 0.0020 | 0.0098 * |
| dynamics_shift | full vs monitor-only | 10 | +0.0680 | [+0.0074, +0.1286] | 0.0430 | 0.0859 |
| combined_shift | full vs monitor-only | 10 | +0.8160 | [+0.7318, +0.9002] | 0.0020 | 0.0098 * |
| id | full vs no-OOD | 10 | +0.0130 | [-0.0058, +0.0318] | 0.1855 | 0.3711 |
| terrain_shift | full vs no-OOD | 10 | +0.0050 | [-0.0135, +0.0235] | 0.6641 | 0.6641 |
| sensor_shift | full vs no-OOD | 10 | +0.4740 | [+0.4284, +0.5196] | 0.0020 | 0.0098 * |
| dynamics_shift | full vs no-OOD | 10 | +0.0500 | [+0.0083, +0.0917] | 0.0312 | 0.0938 |
| combined_shift | full vs no-OOD | 10 | +0.7120 | [+0.5957, +0.8283] | 0.0020 | 0.0098 * |
| id | full vs no-uncertainty | 10 | +0.0090 | [-0.0008, +0.0188] | 0.1250 | 0.5000 |
| terrain_shift | full vs no-uncertainty | 10 | +0.0200 | [+0.0012, +0.0388] | 0.0527 | 0.2637 |
| sensor_shift | full vs no-uncertainty | 10 | +0.0000 | [+0.0000, +0.0000] | 1.0000 | 1.0000 |
| dynamics_shift | full vs no-uncertainty | 10 | -0.0050 | [-0.0209, +0.0109] | 0.5625 | 1.0000 |
| combined_shift | full vs no-uncertainty | 10 | +0.0000 | [+0.0000, +0.0000] | 1.0000 | 1.0000 |
| id | full vs no-monitor | 10 | -0.3510 | [-0.5251, -0.1769] | 0.0020 | 0.0098 * |
| terrain_shift | full vs no-monitor | 10 | -0.8200 | [-0.9718, -0.6682] | 0.0020 | 0.0098 * |
| sensor_shift | full vs no-monitor | 10 | +0.0050 | [-0.0113, +0.0213] | 0.5625 | 0.5625 |
| dynamics_shift | full vs no-monitor | 10 | -0.2960 | [-0.4821, -0.1099] | 0.0020 | 0.0098 * |
| combined_shift | full vs no-monitor | 10 | -0.0290 | [-0.0569, -0.0011] | 0.0430 | 0.0859 |
| id | monitor-only vs ensemble | 10 | -1.4130 | [-1.8229, -1.0031] | 0.0020 | 0.0098 * |
| terrain_shift | monitor-only vs ensemble | 10 | -3.6800 | [-4.6677, -2.6923] | 0.0020 | 0.0098 * |
| sensor_shift | monitor-only vs ensemble | 10 | -1.7990 | [-2.0973, -1.5007] | 0.0020 | 0.0098 * |
| dynamics_shift | monitor-only vs ensemble | 10 | -1.0870 | [-1.5919, -0.5821] | 0.0020 | 0.0098 * |
| combined_shift | monitor-only vs ensemble | 10 | -2.7630 | [-3.2170, -2.3090] | 0.0020 | 0.0098 * |

### secondary comparisons — unsafe

| Condition | Comparison | n | A − B | 95% CI | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|
| id | stop vs no-stop | 10 | -0.0200 | [-0.0331, -0.0069] | 0.0078 | 0.0156 * |
| terrain_shift | stop vs no-stop | 10 | -0.0710 | [-0.1001, -0.0419] | 0.0020 | 0.0098 * |
| sensor_shift | stop vs no-stop | 10 | -0.0310 | [-0.0333, -0.0287] | 0.0020 | 0.0098 * |
| dynamics_shift | stop vs no-stop | 10 | -0.0090 | [-0.0169, -0.0011] | 0.0625 | 0.0625 |
| combined_shift | stop vs no-stop | 10 | -0.1520 | [-0.1614, -0.1426] | 0.0020 | 0.0098 * |
| id | full vs monitor-only | 10 | +0.0040 | [-0.0029, +0.0109] | 0.3594 | 1.0000 |
| terrain_shift | full vs monitor-only | 10 | +0.0020 | [-0.0025, +0.0065] | 0.6250 | 1.0000 |
| sensor_shift | full vs monitor-only | 10 | +0.3350 | [+0.2827, +0.3873] | 0.0020 | 0.0098 * |
| dynamics_shift | full vs monitor-only | 10 | -0.0010 | [-0.0081, +0.0061] | 1.0000 | 1.0000 |
| combined_shift | full vs monitor-only | 10 | +0.2400 | [+0.1966, +0.2834] | 0.0020 | 0.0098 * |
| id | full vs no-OOD | 10 | +0.0050 | [-0.0020, +0.0120] | 0.2344 | 0.7031 |
| terrain_shift | full vs no-OOD | 10 | -0.0010 | [-0.0033, +0.0013] | 1.0000 | 1.0000 |
| sensor_shift | full vs no-OOD | 10 | +0.3370 | [+0.2850, +0.3890] | 0.0020 | 0.0098 * |
| dynamics_shift | full vs no-OOD | 10 | -0.0020 | [-0.0086, +0.0046] | 0.7500 | 1.0000 |
| combined_shift | full vs no-OOD | 10 | +0.2050 | [+0.1474, +0.2626] | 0.0020 | 0.0098 * |
| id | full vs no-uncertainty | 10 | -0.0010 | [-0.0033, +0.0013] | 1.0000 | 1.0000 |
| terrain_shift | full vs no-uncertainty | 10 | +0.0020 | [-0.0010, +0.0050] | 0.5000 | 1.0000 |
| sensor_shift | full vs no-uncertainty | 10 | +0.0000 | [+0.0000, +0.0000] | 1.0000 | 1.0000 |
| dynamics_shift | full vs no-uncertainty | 10 | +0.0010 | [-0.0013, +0.0033] | 1.0000 | 1.0000 |
| combined_shift | full vs no-uncertainty | 10 | +0.0000 | [+0.0000, +0.0000] | 1.0000 | 1.0000 |
| id | full vs no-monitor | 10 | -0.3730 | [-0.5559, -0.1901] | 0.0020 | 0.0098 * |
| terrain_shift | full vs no-monitor | 10 | -0.8660 | [-1.0109, -0.7211] | 0.0020 | 0.0098 * |
| sensor_shift | full vs no-monitor | 10 | +0.0060 | [-0.0099, +0.0219] | 0.4922 | 0.5391 |
| dynamics_shift | full vs no-monitor | 10 | -0.2980 | [-0.4974, -0.0986] | 0.0020 | 0.0098 * |
| combined_shift | full vs no-monitor | 10 | -0.0100 | [-0.0269, +0.0069] | 0.2695 | 0.5391 |
| id | monitor-only vs ensemble | 10 | -1.4630 | [-1.8736, -1.0524] | 0.0020 | 0.0098 * |
| terrain_shift | monitor-only vs ensemble | 10 | -3.7740 | [-4.7790, -2.7690] | 0.0020 | 0.0098 * |
| sensor_shift | monitor-only vs ensemble | 10 | -1.8670 | [-2.1716, -1.5624] | 0.0020 | 0.0098 * |
| dynamics_shift | monitor-only vs ensemble | 10 | -1.1260 | [-1.6705, -0.5815] | 0.0020 | 0.0098 * |
| combined_shift | monitor-only vs ensemble | 10 | -2.8910 | [-3.3611, -2.4209] | 0.0020 | 0.0098 * |
