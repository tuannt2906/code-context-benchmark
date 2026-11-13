# Results - oracle_trace_haiku-20261113-202029

- Created: 2026-11-13T20:20:29; dataset v1 (sha 5e550060fea81413); fixture 8da947b42b62564d; prompt p1; ccbench 1.0.0
- Providers (effective parameters): `{"claude-haiku-5-5": {"model": "haiku", "temperature": null, "seed": null, "unsupported": ["temperature", "seed"], "effort": null}}`
- Records: 64 (ok 64, errors 0); scored from raw responses with scorer s2

## Accuracy and cost per condition

| model | strategy | budget | n | acc % [95% CI] | L1 | L2 | L3 | L4 | L5 | ctx recall | evid. P | evid. R | est ctx tok | input tok | out tok | latency s | cost/task $ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude-haiku-5-5 | oracle_trace | unbounded | 64 | 95.3 [87.1, 98.4] | 100.0 | 100.0 | 92.3 | 100.0 | 87.5 | 100.0 | 91.5 | 77.2 | 4666 | 5702 | 942 | 8.2 | 0.0016 |

## Pre-registered hypotheses

### claude-haiku-5-5


## Other diagnostics

```json
{
  "flip_rate": null,
  "token_calibration": {
    "claude-haiku-5-5": {
      "n": 64,
      "intercept_tokens": 627.2729161602592,
      "slope_actual_per_estimated": 0.9316177638483963
    }
  },
  "model_rank_agreement": {},
  "n_records": 64,
  "n_ok": 64,
  "n_errors": 0
}
```

## Charts

