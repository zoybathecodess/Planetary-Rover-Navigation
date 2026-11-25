# Amendment A4 — real-terrain tiles under shifted physics

450 real_final tiles; mean ± 95% t-interval over 10 seeds (Wilson over tiles for seedless methods).

### real_hirise (A2, ID physics, for reference)

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

### real_sensor

| Method | success | unsafe | collisions | energy_used | intervention_rate | safe_stop_rate | depleted_rate |
|---|---|---|---|---|---|---|---|
| astar | 0.991 [0.977, 0.997] | 0.382 | 0.784 | 81.402 | — | 0.000 [0.000, 0.008] | 0.009 [0.003, 0.023] |
| astar_monitor | 0.956 [0.932, 0.971] | 0.176 | 0.536 | 84.991 | 0.074 | 0.044 [0.029, 0.068] | 0.000 [0.000, 0.008] |
| reactive | 0.960 [0.938, 0.975] | 2.027 | 2.124 | 88.902 | — | 0.000 [0.000, 0.008] | 0.040 [0.025, 0.062] |
| dqn | 0.958 ± 0.007 | 2.829 ± 0.435 | 2.917 ± 0.455 | 90.460 ± 2.911 | — | 0.000 ± 0.000 | 0.042 ± 0.007 |
| dqn_shield | 0.965 ± 0.005 | 0.352 ± 0.099 | 0.496 ± 0.102 | 90.507 ± 3.052 | 0.039 ± 0.005 | 0.000 ± 0.000 | 0.035 ± 0.005 |
| ppo | 0.956 ± 0.004 | 6.115 ± 1.113 | 6.116 ± 1.114 | 92.005 ± 1.423 | — | 0.000 ± 0.000 | 0.044 ± 0.004 |
| ppo_shield | 0.965 ± 0.009 | 0.540 ± 0.159 | 0.665 ± 0.166 | 92.263 ± 1.577 | 0.050 ± 0.008 | 0.000 ± 0.000 | 0.035 ± 0.009 |
| ens | 0.980 ± 0.004 | 1.716 ± 0.226 | 1.789 ± 0.228 | 84.950 ± 1.038 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.020 ± 0.004 |
| assured-unc_only@95 | 0.986 ± 0.003 | 1.043 ± 0.250 | 1.125 ± 0.255 | 83.571 ± 1.098 | 0.011 ± 0.003 | 0.014 ± 0.003 | 0.000 ± 0.000 |
| assured@95 | 0.962 ± 0.002 | 0.180 ± 0.013 | 0.417 ± 0.031 | 83.280 ± 0.443 | 0.896 ± 0.032 | 0.038 ± 0.002 | 0.000 ± 0.000 |
| assured-no_stop@95 | 0.996 ± 0.001 | 0.190 ± 0.013 | 0.441 ± 0.031 | 85.712 ± 0.458 | 0.898 ± 0.031 | 0.000 ± 0.000 | 0.004 ± 0.001 |
| assured-aood@95 | 0.962 ± 0.004 | 0.124 ± 0.010 | 0.214 ± 0.018 | 81.480 ± 0.870 | 0.027 ± 0.003 | 0.038 ± 0.004 | 0.000 ± 0.000 |
| assured-monitor_only@95 | 0.955 ± 0.005 | 0.120 ± 0.013 | 0.209 ± 0.021 | 81.731 ± 0.842 | 0.016 ± 0.001 | 0.045 ± 0.005 | 0.000 ± 0.000 |
| assured-no_ood@95 | 0.962 ± 0.004 | 0.120 ± 0.011 | 0.211 ± 0.018 | 81.511 ± 0.817 | 0.023 ± 0.002 | 0.038 ± 0.004 | 0.000 ± 0.000 |

### real_dynamics

| Method | success | unsafe | collisions | energy_used | intervention_rate | safe_stop_rate | depleted_rate |
|---|---|---|---|---|---|---|---|
| astar | 0.991 [0.977, 0.997] | 0.093 | 1.513 | 90.920 | — | 0.000 [0.000, 0.008] | 0.009 [0.003, 0.023] |
| astar_monitor | 0.987 [0.971, 0.994] | 0.036 | 1.358 | 91.813 | 0.030 | 0.013 [0.006, 0.029] | 0.000 [0.000, 0.008] |
| reactive | 0.953 [0.930, 0.969] | 0.389 | 0.729 | 93.398 | — | 0.000 [0.000, 0.008] | 0.047 [0.031, 0.070] |
| dqn | 0.960 ± 0.005 | 2.662 ± 0.614 | 3.025 ± 0.689 | 94.884 ± 4.710 | — | 0.000 ± 0.000 | 0.040 ± 0.005 |
| dqn_shield | 0.966 ± 0.004 | 0.168 ± 0.048 | 0.670 ± 0.143 | 94.140 ± 4.653 | 0.020 ± 0.003 | 0.000 ± 0.000 | 0.034 ± 0.004 |
| ppo | 0.950 ± 0.005 | 5.887 ± 1.203 | 5.980 ± 1.258 | 99.497 ± 2.078 | — | 0.000 ± 0.000 | 0.050 ± 0.005 |
| ppo_shield | 0.957 ± 0.006 | 0.424 ± 0.113 | 0.807 ± 0.185 | 98.231 ± 2.070 | 0.033 ± 0.005 | 0.000 ± 0.000 | 0.043 ± 0.006 |
| ens | 0.973 ± 0.004 | 1.711 ± 0.421 | 1.941 ± 0.437 | 89.177 ± 1.966 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.027 ± 0.004 |
| assured-unc_only@95 | 0.981 ± 0.004 | 1.021 ± 0.267 | 1.282 ± 0.277 | 87.755 ± 1.886 | 0.010 ± 0.002 | 0.019 ± 0.004 | 0.000 ± 0.000 |
| assured@95 | 0.987 ± 0.002 | 0.015 ± 0.004 | 0.326 ± 0.065 | 86.907 ± 1.885 | 0.067 ± 0.012 | 0.013 ± 0.002 | 0.000 ± 0.000 |
| assured-no_stop@95 | 0.989 ± 0.001 | 0.020 ± 0.005 | 0.342 ± 0.066 | 87.430 ± 1.903 | 0.070 ± 0.012 | 0.000 ± 0.000 | 0.011 ± 0.001 |
| assured-aood@95 | 0.985 ± 0.003 | 0.013 ± 0.004 | 0.324 ± 0.064 | 87.178 ± 1.959 | 0.023 ± 0.003 | 0.015 ± 0.003 | 0.000 ± 0.000 |
| assured-monitor_only@95 | 0.978 ± 0.003 | 0.013 ± 0.004 | 0.316 ± 0.061 | 87.531 ± 1.945 | 0.012 ± 0.001 | 0.022 ± 0.003 | 0.000 ± 0.000 |
| assured-no_ood@95 | 0.984 ± 0.003 | 0.013 ± 0.004 | 0.320 ± 0.063 | 87.248 ± 1.939 | 0.020 ± 0.002 | 0.016 ± 0.003 | 0.000 ± 0.000 |

### real_combined

| Method | success | unsafe | collisions | energy_used | intervention_rate | safe_stop_rate | depleted_rate |
|---|---|---|---|---|---|---|---|
| astar | 0.989 [0.974, 0.995] | 0.389 | 1.487 | 92.427 | — | 0.000 [0.000, 0.008] | 0.011 [0.005, 0.026] |
| astar_monitor | 0.944 [0.919, 0.962] | 0.191 | 1.142 | 95.382 | 0.083 | 0.056 [0.038, 0.081] | 0.000 [0.000, 0.008] |
| reactive | 0.958 [0.935, 0.973] | 1.742 | 1.949 | 101.784 | — | 0.000 [0.000, 0.008] | 0.042 [0.027, 0.065] |
| dqn | 0.952 ± 0.008 | 2.462 ± 0.381 | 2.738 ± 0.444 | 103.271 ± 3.794 | — | 0.000 ± 0.000 | 0.048 ± 0.008 |
| dqn_shield | 0.953 ± 0.006 | 0.317 ± 0.057 | 0.747 ± 0.126 | 104.350 ± 4.070 | 0.038 ± 0.004 | 0.000 ± 0.000 | 0.047 ± 0.006 |
| ppo | 0.947 ± 0.003 | 5.172 ± 1.047 | 5.278 ± 1.054 | 105.702 ± 1.645 | — | 0.000 ± 0.000 | 0.053 ± 0.003 |
| ppo_shield | 0.953 ± 0.005 | 0.527 ± 0.148 | 0.875 ± 0.166 | 106.957 ± 1.688 | 0.049 ± 0.007 | 0.000 ± 0.000 | 0.047 ± 0.005 |
| ens | 0.971 ± 0.004 | 1.458 ± 0.260 | 1.672 ± 0.262 | 97.162 ± 1.329 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.029 ± 0.004 |
| assured-unc_only@95 | 0.977 ± 0.004 | 0.944 ± 0.165 | 1.186 ± 0.171 | 95.644 ± 1.293 | 0.012 ± 0.002 | 0.023 ± 0.004 | 0.000 ± 0.001 |
| assured@95 | 0.952 ± 0.003 | 0.184 ± 0.009 | 0.866 ± 0.041 | 94.254 ± 0.348 | 0.915 ± 0.024 | 0.048 ± 0.003 | 0.000 ± 0.000 |
| assured-no_stop@95 | 0.985 ± 0.001 | 0.198 ± 0.011 | 0.914 ± 0.047 | 97.510 ± 0.474 | 0.917 ± 0.025 | 0.000 ± 0.000 | 0.015 ± 0.001 |
| assured-aood@95 | 0.953 ± 0.004 | 0.115 ± 0.010 | 0.382 ± 0.034 | 93.413 ± 0.944 | 0.042 ± 0.004 | 0.047 ± 0.004 | 0.000 ± 0.000 |
| assured-monitor_only@95 | 0.948 ± 0.004 | 0.116 ± 0.012 | 0.381 ± 0.035 | 93.577 ± 0.969 | 0.030 ± 0.001 | 0.052 ± 0.004 | 0.000 ± 0.000 |
| assured-no_ood@95 | 0.953 ± 0.004 | 0.114 ± 0.011 | 0.379 ± 0.034 | 93.349 ± 0.916 | 0.038 ± 0.002 | 0.047 ± 0.004 | 0.000 ± 0.000 |

## Paired differences (A − B); Holm across the three conditions per (comparison, metric)

| Family | Comparison | Metric | Condition | A − B | 95% CI | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|
| primary | assured vs A* | success | real_sensor | -0.0291 | [-0.0309, -0.0274] | 0.0020 | 0.0059 * |
| primary | assured vs A* | success | real_dynamics | -0.0038 | [-0.0053, -0.0023] | 0.0039 | 0.0059 * |
| primary | assured vs A* | success | real_combined | -0.0369 | [-0.0401, -0.0337] | 0.0020 | 0.0059 * |
| primary | assured vs A* | unsafe | real_sensor | -0.2022 | [-0.2154, -0.1890] | 0.0020 | 0.0059 * |
| primary | assured vs A* | unsafe | real_dynamics | -0.0784 | [-0.0826, -0.0743] | 0.0020 | 0.0059 * |
| primary | assured vs A* | unsafe | real_combined | -0.2053 | [-0.2146, -0.1961] | 0.0020 | 0.0059 * |
| primary | assured vs A* | collisions | real_sensor | -0.3676 | [-0.3990, -0.3361] | 0.0020 | 0.0059 * |
| primary | assured vs A* | collisions | real_dynamics | -1.1871 | [-1.2525, -1.1217] | 0.0020 | 0.0059 * |
| primary | assured vs A* | collisions | real_combined | -0.6202 | [-0.6616, -0.5788] | 0.0020 | 0.0059 * |
| primary | assured vs A* | energy_used | real_sensor | +1.8780 | [+1.4349, +2.3211] | 0.0020 | 0.0059 * |
| primary | assured vs A* | energy_used | real_dynamics | -4.0131 | [-5.8977, -2.1285] | 0.0039 | 0.0059 * |
| primary | assured vs A* | energy_used | real_combined | +1.8273 | [+1.4788, +2.1758] | 0.0020 | 0.0059 * |
| primary | assured vs A* | intervention_rate | real_sensor | +nan | [+nan, +nan] | nan | nan |
| primary | assured vs A* | intervention_rate | real_dynamics | +nan | [+nan, +nan] | nan | nan |
| primary | assured vs A* | intervention_rate | real_combined | +nan | [+nan, +nan] | nan | nan |
| primary | assured vs A* | safe_stop_rate | real_sensor | +0.0380 | [+0.0363, +0.0397] | 0.0020 | 0.0059 * |
| primary | assured vs A* | safe_stop_rate | real_dynamics | +0.0127 | [+0.0112, +0.0142] | 0.0020 | 0.0059 * |
| primary | assured vs A* | safe_stop_rate | real_combined | +0.0480 | [+0.0448, +0.0512] | 0.0020 | 0.0059 * |
| primary | assured vs A* | depleted_rate | real_sensor | -0.0089 | [-0.0089, -0.0089] | 0.0020 | 0.0059 * |
| primary | assured vs A* | depleted_rate | real_dynamics | -0.0089 | [-0.0089, -0.0089] | 0.0020 | 0.0059 * |
| primary | assured vs A* | depleted_rate | real_combined | -0.0111 | [-0.0111, -0.0111] | 0.0020 | 0.0059 * |
| primary | assured vs A*+monitor | success | real_sensor | +0.0064 | [+0.0047, +0.0082] | 0.0020 | 0.0059 * |
| primary | assured vs A*+monitor | success | real_dynamics | +0.0007 | [-0.0008, +0.0022] | 0.5312 | 0.5312 |
| primary | assured vs A*+monitor | success | real_combined | +0.0076 | [+0.0044, +0.0108] | 0.0020 | 0.0059 * |
| primary | assured vs A*+monitor | unsafe | real_sensor | +0.0044 | [-0.0088, +0.0177] | 0.4922 | 0.4922 |
| primary | assured vs A*+monitor | unsafe | real_dynamics | -0.0207 | [-0.0248, -0.0165] | 0.0020 | 0.0059 * |
| primary | assured vs A*+monitor | unsafe | real_combined | -0.0076 | [-0.0168, +0.0017] | 0.0977 | 0.1953 |
| primary | assured vs A*+monitor | collisions | real_sensor | -0.1187 | [-0.1501, -0.0873] | 0.0020 | 0.0059 * |
| primary | assured vs A*+monitor | collisions | real_dynamics | -1.0316 | [-1.0969, -0.9662] | 0.0020 | 0.0059 * |
| primary | assured vs A*+monitor | collisions | real_combined | -0.2758 | [-0.3172, -0.2344] | 0.0020 | 0.0059 * |
| primary | assured vs A*+monitor | energy_used | real_sensor | -1.7109 | [-2.1539, -1.2678] | 0.0020 | 0.0059 * |
| primary | assured vs A*+monitor | energy_used | real_dynamics | -4.9064 | [-6.7910, -3.0219] | 0.0039 | 0.0059 * |
| primary | assured vs A*+monitor | energy_used | real_combined | -1.1282 | [-1.4767, -0.7797] | 0.0020 | 0.0059 * |
| primary | assured vs A*+monitor | intervention_rate | real_sensor | +0.8222 | [+0.7906, +0.8537] | 0.0020 | 0.0059 * |
| primary | assured vs A*+monitor | intervention_rate | real_dynamics | +0.0378 | [+0.0256, +0.0499] | 0.0039 | 0.0059 * |
| primary | assured vs A*+monitor | intervention_rate | real_combined | +0.8318 | [+0.8074, +0.8562] | 0.0020 | 0.0059 * |
| primary | assured vs A*+monitor | safe_stop_rate | real_sensor | -0.0064 | [-0.0082, -0.0047] | 0.0020 | 0.0059 * |
| primary | assured vs A*+monitor | safe_stop_rate | real_dynamics | -0.0007 | [-0.0022, +0.0008] | 0.5312 | 0.5312 |
| primary | assured vs A*+monitor | safe_stop_rate | real_combined | -0.0076 | [-0.0108, -0.0044] | 0.0020 | 0.0059 * |
| primary | assured vs A*+monitor | depleted_rate | real_sensor | +0.0000 | [+0.0000, +0.0000] | 1.0000 | 1.0000 |
| primary | assured vs A*+monitor | depleted_rate | real_dynamics | +0.0000 | [+0.0000, +0.0000] | 1.0000 | 1.0000 |
| primary | assured vs A*+monitor | depleted_rate | real_combined | +0.0000 | [+0.0000, +0.0000] | 1.0000 | 1.0000 |
| primary | assured vs ensemble | success | real_sensor | -0.0178 | [-0.0221, -0.0135] | 0.0020 | 0.0059 * |
| primary | assured vs ensemble | success | real_dynamics | +0.0147 | [+0.0101, +0.0192] | 0.0020 | 0.0059 * |
| primary | assured vs ensemble | success | real_combined | -0.0191 | [-0.0242, -0.0140] | 0.0020 | 0.0059 * |
| primary | assured vs ensemble | unsafe | real_sensor | -1.5360 | [-1.7655, -1.3065] | 0.0020 | 0.0059 * |
| primary | assured vs ensemble | unsafe | real_dynamics | -1.6960 | [-2.1142, -1.2778] | 0.0020 | 0.0059 * |
| primary | assured vs ensemble | unsafe | real_combined | -1.2744 | [-1.5327, -1.0162] | 0.0020 | 0.0059 * |
| primary | assured vs ensemble | collisions | real_sensor | -1.3720 | [-1.6052, -1.1388] | 0.0020 | 0.0059 * |
| primary | assured vs ensemble | collisions | real_dynamics | -1.6144 | [-2.0218, -1.2071] | 0.0020 | 0.0059 * |
| primary | assured vs ensemble | collisions | real_combined | -0.8058 | [-1.0766, -0.5350] | 0.0020 | 0.0059 * |
| primary | assured vs ensemble | energy_used | real_sensor | -1.6700 | [-2.9951, -0.3449] | 0.0254 | 0.0254 * |
| primary | assured vs ensemble | energy_used | real_dynamics | -2.2702 | [-2.7424, -1.7981] | 0.0020 | 0.0059 * |
| primary | assured vs ensemble | energy_used | real_combined | -2.9078 | [-4.3658, -1.4498] | 0.0059 | 0.0117 * |
| primary | assured vs ensemble | intervention_rate | real_sensor | +0.8965 | [+0.8649, +0.9281] | 0.0020 | 0.0059 * |
| primary | assured vs ensemble | intervention_rate | real_dynamics | +0.0673 | [+0.0552, +0.0795] | 0.0020 | 0.0059 * |
| primary | assured vs ensemble | intervention_rate | real_combined | +0.9151 | [+0.8907, +0.9395] | 0.0020 | 0.0059 * |
| primary | assured vs ensemble | safe_stop_rate | real_sensor | +0.0380 | [+0.0363, +0.0397] | 0.0020 | 0.0059 * |
| primary | assured vs ensemble | safe_stop_rate | real_dynamics | +0.0127 | [+0.0112, +0.0142] | 0.0020 | 0.0059 * |
| primary | assured vs ensemble | safe_stop_rate | real_combined | +0.0480 | [+0.0448, +0.0512] | 0.0020 | 0.0059 * |
| primary | assured vs ensemble | depleted_rate | real_sensor | -0.0202 | [-0.0239, -0.0165] | 0.0020 | 0.0059 * |
| primary | assured vs ensemble | depleted_rate | real_dynamics | -0.0273 | [-0.0314, -0.0233] | 0.0020 | 0.0059 * |
| primary | assured vs ensemble | depleted_rate | real_combined | -0.0289 | [-0.0327, -0.0251] | 0.0020 | 0.0059 * |
| primary | assured vs DQN+shield | success | real_sensor | -0.0027 | [-0.0072, +0.0018] | 0.2461 | 0.4922 |
| primary | assured vs DQN+shield | success | real_dynamics | +0.0216 | [+0.0171, +0.0261] | 0.0020 | 0.0059 * |
| primary | assured vs DQN+shield | success | real_combined | -0.0007 | [-0.0058, +0.0044] | 0.8438 | 0.8438 |
| primary | assured vs DQN+shield | unsafe | real_sensor | -0.1718 | [-0.2601, -0.0835] | 0.0020 | 0.0059 * |
| primary | assured vs DQN+shield | unsafe | real_dynamics | -0.1533 | [-0.2031, -0.1035] | 0.0020 | 0.0059 * |
| primary | assured vs DQN+shield | unsafe | real_combined | -0.1333 | [-0.1865, -0.0801] | 0.0020 | 0.0059 * |
| primary | assured vs DQN+shield | collisions | real_sensor | -0.0791 | [-0.1615, +0.0033] | 0.0508 | 0.0820 |
| primary | assured vs DQN+shield | collisions | real_dynamics | -0.3436 | [-0.4692, -0.2179] | 0.0020 | 0.0059 * |
| primary | assured vs DQN+shield | collisions | real_combined | +0.1198 | [+0.0116, +0.2280] | 0.0410 | 0.0820 |
| primary | assured vs DQN+shield | energy_used | real_sensor | -7.2269 | [-10.3571, -4.0967] | 0.0020 | 0.0059 * |
| primary | assured vs DQN+shield | energy_used | real_dynamics | -7.2331 | [-10.8919, -3.5743] | 0.0020 | 0.0059 * |
| primary | assured vs DQN+shield | energy_used | real_combined | -10.0960 | [-14.2665, -5.9255] | 0.0020 | 0.0059 * |
| primary | assured vs DQN+shield | intervention_rate | real_sensor | +0.8580 | [+0.8284, +0.8875] | 0.0020 | 0.0059 * |
| primary | assured vs DQN+shield | intervention_rate | real_dynamics | +0.0475 | [+0.0352, +0.0598] | 0.0020 | 0.0059 * |
| primary | assured vs DQN+shield | intervention_rate | real_combined | +0.8770 | [+0.8544, +0.8997] | 0.0020 | 0.0059 * |
| primary | assured vs DQN+shield | safe_stop_rate | real_sensor | +0.0380 | [+0.0363, +0.0397] | 0.0020 | 0.0059 * |
| primary | assured vs DQN+shield | safe_stop_rate | real_dynamics | +0.0127 | [+0.0112, +0.0142] | 0.0020 | 0.0059 * |
| primary | assured vs DQN+shield | safe_stop_rate | real_combined | +0.0480 | [+0.0448, +0.0512] | 0.0020 | 0.0059 * |
| primary | assured vs DQN+shield | depleted_rate | real_sensor | -0.0353 | [-0.0404, -0.0303] | 0.0020 | 0.0059 * |
| primary | assured vs DQN+shield | depleted_rate | real_dynamics | -0.0342 | [-0.0386, -0.0298] | 0.0020 | 0.0059 * |
| primary | assured vs DQN+shield | depleted_rate | real_combined | -0.0473 | [-0.0530, -0.0417] | 0.0020 | 0.0059 * |
| secondary | action-OOD vs raw-OOD | success | real_sensor | -0.0002 | [-0.0038, +0.0033] | 1.0000 | 1.0000 |
| secondary | action-OOD vs raw-OOD | success | real_dynamics | -0.0020 | [-0.0044, +0.0004] | 0.1562 | 0.4688 |
| secondary | action-OOD vs raw-OOD | success | real_combined | +0.0011 | [-0.0032, +0.0054] | 0.6602 | 1.0000 |
| secondary | action-OOD vs raw-OOD | unsafe | real_sensor | -0.0556 | [-0.0748, -0.0363] | 0.0020 | 0.0059 * |
| secondary | action-OOD vs raw-OOD | unsafe | real_dynamics | -0.0020 | [-0.0066, +0.0026] | 0.4062 | 0.4062 |
| secondary | action-OOD vs raw-OOD | unsafe | real_combined | -0.0687 | [-0.0809, -0.0564] | 0.0020 | 0.0059 * |
| secondary | action-OOD vs raw-OOD | collisions | real_sensor | -0.2024 | [-0.2434, -0.1615] | 0.0020 | 0.0059 * |
| secondary | action-OOD vs raw-OOD | collisions | real_dynamics | -0.0020 | [-0.0155, +0.0115] | 0.7715 | 0.7715 |
| secondary | action-OOD vs raw-OOD | collisions | real_combined | -0.4842 | [-0.5301, -0.4383] | 0.0020 | 0.0059 * |
| secondary | action-OOD vs raw-OOD | energy_used | real_sensor | -1.8007 | [-2.8730, -0.7284] | 0.0098 | 0.0293 * |
| secondary | action-OOD vs raw-OOD | energy_used | real_dynamics | +0.2711 | [+0.0252, +0.5170] | 0.0430 | 0.0859 |
| secondary | action-OOD vs raw-OOD | energy_used | real_combined | -0.8413 | [-1.8755, +0.1928] | 0.0898 | 0.0898 |
| secondary | action-OOD vs raw-OOD | intervention_rate | real_sensor | -0.8695 | [-0.9007, -0.8383] | 0.0020 | 0.0059 * |
| secondary | action-OOD vs raw-OOD | intervention_rate | real_dynamics | -0.0443 | [-0.0549, -0.0337] | 0.0020 | 0.0059 * |
| secondary | action-OOD vs raw-OOD | intervention_rate | real_combined | -0.8728 | [-0.8963, -0.8492] | 0.0020 | 0.0059 * |
| secondary | action-OOD vs raw-OOD | safe_stop_rate | real_sensor | +0.0002 | [-0.0033, +0.0038] | 1.0000 | 1.0000 |
| secondary | action-OOD vs raw-OOD | safe_stop_rate | real_dynamics | +0.0020 | [-0.0004, +0.0044] | 0.1562 | 0.4688 |
| secondary | action-OOD vs raw-OOD | safe_stop_rate | real_combined | -0.0011 | [-0.0054, +0.0032] | 0.6602 | 1.0000 |
| secondary | action-OOD vs raw-OOD | depleted_rate | real_sensor | +0.0000 | [+0.0000, +0.0000] | 1.0000 | 1.0000 |
| secondary | action-OOD vs raw-OOD | depleted_rate | real_dynamics | +0.0000 | [+0.0000, +0.0000] | 1.0000 | 1.0000 |
| secondary | action-OOD vs raw-OOD | depleted_rate | real_combined | +0.0000 | [+0.0000, +0.0000] | 1.0000 | 1.0000 |
| secondary | full vs monitor-only | success | real_sensor | +0.0071 | [+0.0034, +0.0108] | 0.0059 | 0.0117 * |
| secondary | full vs monitor-only | success | real_dynamics | +0.0093 | [+0.0068, +0.0119] | 0.0020 | 0.0059 * |
| secondary | full vs monitor-only | success | real_combined | +0.0036 | [-0.0013, +0.0084] | 0.1562 | 0.1562 |
| secondary | full vs monitor-only | unsafe | real_sensor | +0.0602 | [+0.0369, +0.0835] | 0.0020 | 0.0059 * |
| secondary | full vs monitor-only | unsafe | real_dynamics | +0.0016 | [-0.0029, +0.0061] | 0.5195 | 0.5195 |
| secondary | full vs monitor-only | unsafe | real_combined | +0.0678 | [+0.0560, +0.0795] | 0.0020 | 0.0059 * |
| secondary | full vs monitor-only | collisions | real_sensor | +0.2078 | [+0.1627, +0.2529] | 0.0020 | 0.0059 * |
| secondary | full vs monitor-only | collisions | real_dynamics | +0.0102 | [-0.0017, +0.0222] | 0.0918 | 0.0918 |
| secondary | full vs monitor-only | collisions | real_combined | +0.4856 | [+0.4365, +0.5346] | 0.0020 | 0.0059 * |
| secondary | full vs monitor-only | energy_used | real_sensor | +1.5491 | [+0.5210, +2.5772] | 0.0117 | 0.0234 * |
| secondary | full vs monitor-only | energy_used | real_dynamics | -0.6240 | [-0.9290, -0.3190] | 0.0020 | 0.0059 * |
| secondary | full vs monitor-only | energy_used | real_combined | +0.6769 | [-0.3947, +1.7485] | 0.1797 | 0.1797 |
| secondary | full vs monitor-only | intervention_rate | real_sensor | +0.8804 | [+0.8489, +0.9119] | 0.0020 | 0.0059 * |
| secondary | full vs monitor-only | intervention_rate | real_dynamics | +0.0554 | [+0.0436, +0.0672] | 0.0020 | 0.0059 * |
| secondary | full vs monitor-only | intervention_rate | real_combined | +0.8850 | [+0.8604, +0.9095] | 0.0020 | 0.0059 * |
| secondary | full vs monitor-only | safe_stop_rate | real_sensor | -0.0071 | [-0.0108, -0.0034] | 0.0059 | 0.0117 * |
| secondary | full vs monitor-only | safe_stop_rate | real_dynamics | -0.0093 | [-0.0119, -0.0068] | 0.0020 | 0.0059 * |
| secondary | full vs monitor-only | safe_stop_rate | real_combined | -0.0036 | [-0.0084, +0.0013] | 0.1562 | 0.1562 |
| secondary | full vs monitor-only | depleted_rate | real_sensor | +0.0000 | [+0.0000, +0.0000] | 1.0000 | 1.0000 |
| secondary | full vs monitor-only | depleted_rate | real_dynamics | +0.0000 | [+0.0000, +0.0000] | 1.0000 | 1.0000 |
| secondary | full vs monitor-only | depleted_rate | real_combined | +0.0000 | [+0.0000, +0.0000] | 1.0000 | 1.0000 |
