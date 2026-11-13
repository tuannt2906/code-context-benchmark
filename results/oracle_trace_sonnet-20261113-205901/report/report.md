# Results - oracle_trace_sonnet-20261113-205901

- Created: 2026-11-13T20:59:01; dataset v1 (sha 5e550060fea81413); fixture 8da947b42b62564d; prompt p1; ccbench 1.0.0
- Providers (effective parameters): `{"claude-sonnet-5-5": {"model": "sonnet", "temperature": null, "seed": null, "unsupported": ["temperature", "seed"], "effort": null}}`
- Records: 64 (ok 64, errors 0); scored from raw responses with scorer s2

## Accuracy and cost per condition

| model | strategy | budget | n | acc % [95% CI] | L1 | L2 | L3 | L4 | L5 | ctx recall | evid. P | evid. R | est ctx tok | input tok | out tok | latency s | cost/task $ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude-sonnet-5-5 | oracle_trace | unbounded | 64 | 96.9 [89.3, 99.1] | 100.0 | 100.0 | 100.0 | 100.0 | 87.5 | 100.0 | 90.6 | 80.2 | 4666 | 5679 | 450 | 4.6 | 0.0272 |

## Pre-registered hypotheses

### claude-sonnet-5-5


## Other diagnostics

```json
{
  "flip_rate": null,
  "token_calibration": {
    "claude-sonnet-5-5": {
      "n": 64,
      "intercept_tokens": 604.2729161602592,
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

