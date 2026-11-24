# Amendment A3 — action-conditioned OOD gate

Mean ± 95% t-interval over 10 system seeds; 500 identical final-split maps per condition.

### id

| Method | success | unsafe | collisions | intervention_rate | safe_stop_rate | energy_used |
|---|---|---|---|---|---|---|
| assured@95 | 0.982 ± 0.004 | 0.035 ± 0.005 | 0.209 ± 0.017 | 0.049 ± 0.005 | 0.018 ± 0.004 | 94.724 ± 1.641 |
| assured-no_ood@95 | 0.983 ± 0.004 | 0.035 ± 0.004 | 0.210 ± 0.016 | 0.026 ± 0.006 | 0.017 ± 0.004 | 95.250 ± 1.843 |
| assured-aood@95 | 0.984 ± 0.004 | 0.035 ± 0.004 | 0.210 ± 0.015 | 0.033 ± 0.007 | 0.016 ± 0.004 | 95.023 ± 1.832 |
| assured-ood_only@95 | 0.971 ± 0.006 | 0.909 ± 0.280 | 1.056 ± 0.269 | 0.032 ± 0.009 | 0.019 ± 0.004 | 96.237 ± 1.634 |
| assured-aood_only@95 | 0.982 ± 0.007 | 1.390 ± 0.227 | 1.532 ± 0.227 | 0.019 ± 0.005 | 0.018 ± 0.007 | 96.758 ± 1.632 |

### terrain_shift

| Method | success | unsafe | collisions | intervention_rate | safe_stop_rate | energy_used |
|---|---|---|---|---|---|---|
| assured@95 | 0.929 ± 0.008 | 0.028 ± 0.005 | 0.304 ± 0.013 | 0.080 ± 0.011 | 0.071 ± 0.008 | 142.057 ± 1.333 |
| assured-no_ood@95 | 0.929 ± 0.007 | 0.027 ± 0.005 | 0.299 ± 0.015 | 0.057 ± 0.009 | 0.071 ± 0.007 | 142.366 ± 1.290 |
| assured-aood@95 | 0.930 ± 0.009 | 0.028 ± 0.005 | 0.305 ± 0.011 | 0.072 ± 0.011 | 0.070 ± 0.009 | 142.108 ± 1.349 |
| assured-ood_only@95 | 0.895 ± 0.011 | 1.752 ± 0.448 | 1.954 ± 0.430 | 0.034 ± 0.010 | 0.069 ± 0.009 | 144.676 ± 1.511 |
| assured-aood_only@95 | 0.913 ± 0.011 | 1.456 ± 0.462 | 1.676 ± 0.445 | 0.046 ± 0.012 | 0.087 ± 0.011 | 143.521 ± 1.230 |

### sensor_shift

| Method | success | unsafe | collisions | intervention_rate | safe_stop_rate | energy_used |
|---|---|---|---|---|---|---|
| assured@95 | 0.927 ± 0.004 | 0.592 ± 0.018 | 0.908 ± 0.015 | 0.939 ± 0.015 | 0.073 ± 0.004 | 106.433 ± 0.653 |
| assured-no_ood@95 | 0.959 ± 0.002 | 0.316 ± 0.019 | 0.515 ± 0.035 | 0.044 ± 0.004 | 0.041 ± 0.002 | 103.890 ± 1.432 |
| assured-aood@95 | 0.959 ± 0.002 | 0.317 ± 0.019 | 0.517 ± 0.033 | 0.054 ± 0.007 | 0.041 ± 0.002 | 103.573 ± 1.596 |
| assured-ood_only@95 | 0.931 ± 0.004 | 0.610 ± 0.016 | 0.932 ± 0.014 | 0.939 ± 0.015 | 0.069 ± 0.004 | 106.904 ± 0.553 |
| assured-aood_only@95 | 0.979 ± 0.005 | 1.980 ± 0.246 | 2.127 ± 0.255 | 0.026 ± 0.006 | 0.021 ± 0.005 | 105.515 ± 1.605 |

### dynamics_shift

| Method | success | unsafe | collisions | intervention_rate | safe_stop_rate | energy_used |
|---|---|---|---|---|---|---|
| assured@95 | 0.978 ± 0.004 | 0.032 ± 0.004 | 0.675 ± 0.047 | 0.123 ± 0.019 | 0.022 ± 0.004 | 112.958 ± 1.459 |
| assured-no_ood@95 | 0.977 ± 0.005 | 0.031 ± 0.005 | 0.634 ± 0.044 | 0.041 ± 0.005 | 0.022 ± 0.005 | 113.513 ± 1.799 |
| assured-aood@95 | 0.978 ± 0.005 | 0.031 ± 0.005 | 0.636 ± 0.047 | 0.049 ± 0.007 | 0.022 ± 0.004 | 113.190 ± 1.882 |
| assured-ood_only@95 | 0.969 ± 0.005 | 0.562 ± 0.152 | 1.149 ± 0.124 | 0.102 ± 0.023 | 0.025 ± 0.003 | 113.823 ± 1.810 |
| assured-aood_only@95 | 0.970 ± 0.007 | 1.029 ± 0.166 | 1.559 ± 0.173 | 0.024 ± 0.006 | 0.030 ± 0.007 | 114.634 ± 2.051 |

### combined_shift

| Method | success | unsafe | collisions | intervention_rate | safe_stop_rate | energy_used |
|---|---|---|---|---|---|---|
| assured@95 | 0.712 ± 0.006 | 0.561 ± 0.006 | 1.799 ± 0.015 | 0.955 ± 0.007 | 0.287 ± 0.005 | 188.430 ± 0.507 |
| assured-no_ood@95 | 0.706 ± 0.018 | 0.319 ± 0.027 | 1.131 ± 0.060 | 0.171 ± 0.017 | 0.293 ± 0.017 | 188.804 ± 1.126 |
| assured-aood@95 | 0.707 ± 0.016 | 0.319 ± 0.026 | 1.139 ± 0.061 | 0.203 ± 0.020 | 0.292 ± 0.016 | 188.794 ± 1.335 |
| assured-ood_only@95 | 0.717 ± 0.007 | 0.566 ± 0.006 | 1.813 ± 0.018 | 0.955 ± 0.008 | 0.282 ± 0.006 | 189.272 ± 0.577 |
| assured-aood_only@95 | 0.722 ± 0.015 | 1.454 ± 0.178 | 2.147 ± 0.172 | 0.099 ± 0.022 | 0.278 ± 0.015 | 191.292 ± 1.049 |

## Paired differences (A − B); Holm across conditions per (comparison, metric)

### action-OOD vs raw-OOD (full system) — success  (PRIMARY)

| Condition | n | A − B | 95% CI | p (perm) | p (Holm) |
|---|---|---|---|---|---|
| id | 10 | +0.0018 | [+0.0004, +0.0032] | 0.0312 | 0.1250 |
| terrain_shift | 10 | +0.0008 | [-0.0028, +0.0044] | 0.7031 | 1.0000 |
| sensor_shift | 10 | +0.0328 | [+0.0286, +0.0370] | 0.0020 | 0.0098 * |
| dynamics_shift | 10 | +0.0004 | [-0.0015, +0.0023] | 0.8125 | 1.0000 |
| combined_shift | 10 | -0.0046 | [-0.0196, +0.0104] | 0.6094 | 1.0000 |

### action-OOD vs raw-OOD (full system) — unsafe  (PRIMARY)

| Condition | n | A − B | 95% CI | p (perm) | p (Holm) |
|---|---|---|---|---|---|
| id | 10 | +0.0004 | [-0.0020, +0.0028] | 0.8750 | 1.0000 |
| terrain_shift | 10 | -0.0000 | [-0.0027, +0.0027] | 1.0000 | 1.0000 |
| sensor_shift | 10 | -0.2750 | [-0.3023, -0.2477] | 0.0020 | 0.0098 * |
| dynamics_shift | 10 | -0.0006 | [-0.0033, +0.0021] | 0.7422 | 1.0000 |
| combined_shift | 10 | -0.2426 | [-0.2699, -0.2153] | 0.0020 | 0.0098 * |

### action-OOD vs raw-OOD (full system) — collisions

| Condition | n | A − B | 95% CI | p (perm) | p (Holm) |
|---|---|---|---|---|---|
| id | 10 | +0.0004 | [-0.0081, +0.0089] | 0.9648 | 1.0000 |
| terrain_shift | 10 | +0.0006 | [-0.0074, +0.0086] | 0.9062 | 1.0000 |
| sensor_shift | 10 | -0.3908 | [-0.4315, -0.3501] | 0.0020 | 0.0098 * |
| dynamics_shift | 10 | -0.0386 | [-0.0556, -0.0216] | 0.0020 | 0.0098 * |
| combined_shift | 10 | -0.6600 | [-0.7324, -0.5876] | 0.0020 | 0.0098 * |

### action-OOD vs raw-OOD (full system) — intervention_rate

| Condition | n | A − B | 95% CI | p (perm) | p (Holm) |
|---|---|---|---|---|---|
| id | 10 | -0.0155 | [-0.0232, -0.0078] | 0.0039 | 0.0098 * |
| terrain_shift | 10 | -0.0075 | [-0.0138, -0.0011] | 0.0332 | 0.0332 * |
| sensor_shift | 10 | -0.8855 | [-0.9016, -0.8694] | 0.0020 | 0.0098 * |
| dynamics_shift | 10 | -0.0734 | [-0.0934, -0.0533] | 0.0020 | 0.0098 * |
| combined_shift | 10 | -0.7526 | [-0.7731, -0.7320] | 0.0020 | 0.0098 * |

### action-OOD vs raw-OOD (full system) — safe_stop_rate

| Condition | n | A − B | 95% CI | p (perm) | p (Holm) |
|---|---|---|---|---|---|
| id | 10 | -0.0018 | [-0.0032, -0.0004] | 0.0312 | 0.1250 |
| terrain_shift | 10 | -0.0008 | [-0.0044, +0.0028] | 0.7031 | 1.0000 |
| sensor_shift | 10 | -0.0328 | [-0.0370, -0.0286] | 0.0020 | 0.0098 * |
| dynamics_shift | 10 | -0.0006 | [-0.0025, +0.0013] | 0.6406 | 1.0000 |
| combined_shift | 10 | +0.0052 | [-0.0096, +0.0200] | 0.5508 | 1.0000 |

### action-OOD vs raw-OOD (full system) — energy_used

| Condition | n | A − B | 95% CI | p (perm) | p (Holm) |
|---|---|---|---|---|---|
| id | 10 | +0.2992 | [+0.0197, +0.5787] | 0.0312 | 0.1250 |
| terrain_shift | 10 | +0.0512 | [-0.1689, +0.2713] | 0.6074 | 1.0000 |
| sensor_shift | 10 | -2.8598 | [-4.5795, -1.1401] | 0.0078 | 0.0391 * |
| dynamics_shift | 10 | +0.2326 | [-0.3849, +0.8501] | 0.4453 | 1.0000 |
| combined_shift | 10 | +0.3640 | [-1.2907, +2.0187] | 0.6309 | 1.0000 |

### action-OOD vs no OOD (full system) — success  (PRIMARY)

| Condition | n | A − B | 95% CI | p (perm) | p (Holm) |
|---|---|---|---|---|---|
| id | 10 | +0.0012 | [-0.0000, +0.0024] | 0.1094 | 0.5469 |
| terrain_shift | 10 | +0.0010 | [-0.0026, +0.0046] | 0.6562 | 1.0000 |
| sensor_shift | 10 | +0.0008 | [-0.0017, +0.0033] | 0.6250 | 1.0000 |
| dynamics_shift | 10 | +0.0006 | [-0.0011, +0.0023] | 0.5938 | 1.0000 |
| combined_shift | 10 | +0.0008 | [-0.0022, +0.0038] | 0.6641 | 1.0000 |

### action-OOD vs no OOD (full system) — unsafe  (PRIMARY)

| Condition | n | A − B | 95% CI | p (perm) | p (Holm) |
|---|---|---|---|---|---|
| id | 10 | +0.0002 | [-0.0006, +0.0010] | 1.0000 | 1.0000 |
| terrain_shift | 10 | +0.0018 | [+0.0007, +0.0029] | 0.0156 | 0.0781 |
| sensor_shift | 10 | +0.0008 | [-0.0027, +0.0043] | 0.6934 | 1.0000 |
| dynamics_shift | 10 | -0.0002 | [-0.0016, +0.0012] | 1.0000 | 1.0000 |
| combined_shift | 10 | -0.0006 | [-0.0081, +0.0069] | 0.8906 | 1.0000 |

### action-OOD vs no OOD (full system) — collisions

| Condition | n | A − B | 95% CI | p (perm) | p (Holm) |
|---|---|---|---|---|---|
| id | 10 | -0.0000 | [-0.0049, +0.0049] | 1.0000 | 1.0000 |
| terrain_shift | 10 | +0.0058 | [-0.0016, +0.0132] | 0.1270 | 0.6348 |
| sensor_shift | 10 | +0.0020 | [-0.0018, +0.0058] | 0.3242 | 0.7344 |
| dynamics_shift | 10 | +0.0026 | [-0.0017, +0.0069] | 0.2344 | 0.7344 |
| combined_shift | 10 | +0.0080 | [-0.0042, +0.0202] | 0.1836 | 0.7344 |

### action-OOD vs no OOD (full system) — intervention_rate

| Condition | n | A − B | 95% CI | p (perm) | p (Holm) |
|---|---|---|---|---|---|
| id | 10 | +0.0073 | [+0.0051, +0.0094] | 0.0020 | 0.0098 * |
| terrain_shift | 10 | +0.0151 | [+0.0100, +0.0202] | 0.0020 | 0.0098 * |
| sensor_shift | 10 | +0.0096 | [+0.0060, +0.0131] | 0.0020 | 0.0098 * |
| dynamics_shift | 10 | +0.0082 | [+0.0053, +0.0111] | 0.0020 | 0.0098 * |
| combined_shift | 10 | +0.0324 | [+0.0234, +0.0414] | 0.0020 | 0.0098 * |

### action-OOD vs no OOD (full system) — safe_stop_rate

| Condition | n | A − B | 95% CI | p (perm) | p (Holm) |
|---|---|---|---|---|---|
| id | 10 | -0.0012 | [-0.0024, +0.0000] | 0.1094 | 0.5469 |
| terrain_shift | 10 | -0.0010 | [-0.0046, +0.0026] | 0.6562 | 1.0000 |
| sensor_shift | 10 | -0.0008 | [-0.0033, +0.0017] | 0.6250 | 1.0000 |
| dynamics_shift | 10 | -0.0006 | [-0.0023, +0.0011] | 0.5938 | 1.0000 |
| combined_shift | 10 | -0.0010 | [-0.0040, +0.0020] | 0.5664 | 1.0000 |

### action-OOD vs no OOD (full system) — energy_used

| Condition | n | A − B | 95% CI | p (perm) | p (Holm) |
|---|---|---|---|---|---|
| id | 10 | -0.2272 | [-0.3541, -0.1003] | 0.0020 | 0.0098 * |
| terrain_shift | 10 | -0.2578 | [-0.5260, +0.0104] | 0.0586 | 0.1172 |
| sensor_shift | 10 | -0.3174 | [-0.5062, -0.1286] | 0.0059 | 0.0176 * |
| dynamics_shift | 10 | -0.3224 | [-0.4726, -0.1722] | 0.0020 | 0.0098 * |
| combined_shift | 10 | -0.0102 | [-0.2880, +0.2676] | 0.9258 | 0.9258 |

## Pre-registered decisions

Comparison 1 (action-OOD vs raw-OOD): improvements under sensor/combined: ['sensor_shift/success', 'sensor_shift/unsafe', 'combined_shift/unsafe']; deteriorations anywhere: none.
**H2': SUPPORTED**

Comparison 2 (action-OOD vs no OOD): improvements: none; deteriorations: none.
**Action-conditioned OOD gate: NO ADDED VALUE**
