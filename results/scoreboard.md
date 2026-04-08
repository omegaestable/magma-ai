# Paid Model Scoreboard

Generated: 2026-04-08 04:05:51 UTC
Runs indexed: 41
Benchmarks indexed: 11
Models indexed: 1

Paid-model runs only. Local/free runs are excluded from this view.
Cost is exact when token usage was saved in the run JSON; otherwise it is reconstructed from the prompt/response text and priced with current OpenRouter weighted-average input/output rates.

## Pricing Basis

| Model | Input $/1M | Output $/1M |
| --- | ---: | ---: |
| Gemini 2.5 Pro | $0.956 | $10.020 |
| Llama 3.3 70B | $0.342 | $0.563 |
| Qwen3.5 122B | $0.384 | $2.880 |

## Highlights

| View | Run |
| --- | --- |
| Best overall | Llama 3.3 70B on normal_balanced60_true30_false30_rotation0002_20260403_185904.jsonl with v23 · F1 93.8% · Acc 93.3% · Cost $0.045 |
| Lowest cost | Llama 3.3 70B on magma_eval_test_10.jsonl with magma_eval_test · Cost $0.006 · F1 85.7% |
| Fastest avg time | Llama 3.3 70B on hard3_balanced40_true20_false20_rotation0002_20260403_185904.jsonl with v23 · Avg 9.25s · F1 66.7% |

## Best By Benchmark And Model

| Benchmark File | Difficulty | Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| hard3_balanced20_true10_false10_rotation0001_20260403_163406.jsonl | hard3 | Llama 3.3 70B | v23 | 20 | 50.0% | 66.7% | 100.0% | 0.0% | 100.0% | 16.13 | $0.015 |
| hard3_balanced40_true20_false20_rotation0002_20260403_185904.jsonl | hard3 | Llama 3.3 70B | v24j | 40 | 72.5% | 78.4% | 100.0% | 45.0% | 100.0% | 23.98 | $0.059 |
| hard_balanced40_true20_false20_rotation0001_20260403_163406.jsonl | hard | Llama 3.3 70B | v23 | 40 | 55.0% | 69.0% | 100.0% | 10.0% | 100.0% | 13.88 | $0.030 |
| magma_eval_test_10.jsonl | magma | Llama 3.3 70B | magma_eval_test | 8 | 87.5% | 85.7% | 100.0% | 80.0% | 100.0% | 15.85 | $0.006 |
| normal_balanced10_true5_false5_seed0.jsonl | normal | Llama 3.3 70B | v23b | 10 | 90.0% | 90.9% | 100.0% | 80.0% | 100.0% | 14.72 | $0.009 |
| normal_balanced10_true5_false5_seed1.jsonl | normal | Llama 3.3 70B | v23b | 10 | 80.0% | 83.3% | 100.0% | 60.0% | 100.0% | 15.80 | $0.009 |
| normal_balanced20_true10_false10_seed0.jsonl | normal | Llama 3.3 70B | v23b | 20 | 90.0% | 90.9% | 100.0% | 80.0% | 100.0% | 17.37 | $0.018 |
| normal_balanced20_true10_false10_seed1.jsonl | normal | Llama 3.3 70B | v23b | 20 | 85.0% | 87.0% | 100.0% | 70.0% | 100.0% | 14.05 | $0.018 |
| normal_balanced20_true10_false10_seed2.jsonl | normal | Llama 3.3 70B | v23 | 20 | 90.0% | 90.9% | 100.0% | 80.0% | 100.0% | 10.99 | $0.015 |
| normal_balanced60_true30_false30_rotation0001_20260403_163406.jsonl | normal | Llama 3.3 70B | v23 | 60 | 88.3% | 89.5% | 100.0% | 76.7% | 100.0% | 13.10 | $0.045 |
| normal_balanced60_true30_false30_rotation0002_20260403_185904.jsonl | normal | Llama 3.3 70B | v23 | 60 | 93.3% | 93.8% | 100.0% | 86.7% | 100.0% | 9.33 | $0.045 |

## All Paid Runs By Benchmark

### hard3_balanced20_true10_false10_rotation0001_20260403_163406.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Llama 3.3 70B | v23 | 20 | 50.0% | 66.7% | 100.0% | 0.0% | 100.0% | 16.13 | $0.015 | 2026-04-03 11:04:25 |

### hard3_balanced40_true20_false20_rotation0002_20260403_185904.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Llama 3.3 70B | v24j | 40 | 72.5% | 78.4% | 100.0% | 45.0% | 100.0% | 23.98 | $0.059 | 2026-04-07 19:58:15 |
| Llama 3.3 70B | v24j | 40 | 65.0% | 73.1% | 95.0% | 35.0% | 100.0% | 20.25 | $0.059 | 2026-04-07 20:19:38 |
| Llama 3.3 70B | v24i | 40 | 62.5% | 71.7% | 95.0% | 30.0% | 97.5% | 20.81 | $0.057 | 2026-04-07 17:33:37 |
| Llama 3.3 70B | v23 | 40 | 50.0% | 66.7% | 100.0% | 0.0% | 100.0% | 9.25 | $0.030 | 2026-04-03 13:14:53 |
| Llama 3.3 70B | v23c | 40 | 50.0% | 66.7% | 100.0% | 0.0% | 100.0% | 16.74 | $0.039 | 2026-04-03 18:28:26 |
| Llama 3.3 70B | v24h | 40 | 50.0% | 66.7% | 100.0% | 0.0% | 97.5% | 9.73 | $0.037 | 2026-04-06 19:40:09 |
| Llama 3.3 70B | v24j | 40 | 52.5% | 65.5% | 90.0% | 15.0% | 100.0% | 20.19 | $0.055 | 2026-04-07 18:39:50 |
| Llama 3.3 70B | v23 | 40 | 45.0% | 60.7% | 85.0% | 5.0% | 85.0% | 15.93 | $0.047 | 2026-04-03 15:12:37 |
| Llama 3.3 70B | v24b | 40 | 42.5% | 59.7% | 85.0% | 0.0% | 97.5% | 21.61 | $0.043 | 2026-04-05 17:47:13 |

### hard_balanced40_true20_false20_rotation0001_20260403_163406.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Llama 3.3 70B | v23 | 40 | 55.0% | 69.0% | 100.0% | 10.0% | 100.0% | 13.88 | $0.030 | 2026-04-03 10:58:51 |

### magma_eval_test_10.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Llama 3.3 70B | magma_eval_test | 8 | 87.5% | 85.7% | 100.0% | 80.0% | 100.0% | 15.85 | $0.006 | 2026-04-05 18:23:13 |

### normal_balanced10_true5_false5_seed0.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Llama 3.3 70B | v23b | 10 | 90.0% | 90.9% | 100.0% | 80.0% | 100.0% | 14.72 | $0.009 | 2026-04-03 17:10:38 |
| Llama 3.3 70B | v23c | 10 | 90.0% | 90.9% | 100.0% | 80.0% | 100.0% | 20.05 | $0.009 | 2026-04-03 17:34:05 |
| Llama 3.3 70B | v23a | 10 | 70.0% | 76.9% | 100.0% | 40.0% | 100.0% | 22.29 | $0.012 | 2026-04-03 17:03:38 |

### normal_balanced10_true5_false5_seed1.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Llama 3.3 70B | v23b | 10 | 80.0% | 83.3% | 100.0% | 60.0% | 100.0% | 15.80 | $0.009 | 2026-04-03 17:13:27 |
| Llama 3.3 70B | v23c | 10 | 80.0% | 83.3% | 100.0% | 60.0% | 100.0% | 13.31 | $0.009 | 2026-04-03 17:36:25 |

### normal_balanced20_true10_false10_seed0.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Llama 3.3 70B | v23b | 20 | 90.0% | 90.9% | 100.0% | 80.0% | 100.0% | 17.37 | $0.018 | 2026-04-03 17:20:01 |
| Llama 3.3 70B | v23c | 20 | 90.0% | 90.9% | 100.0% | 80.0% | 100.0% | 15.16 | $0.019 | 2026-04-03 17:49:02 |
| Llama 3.3 70B | v24a | 20 | 85.0% | 85.7% | 90.0% | 80.0% | 100.0% | 16.01 | $0.025 | 2026-04-05 16:36:58 |

### normal_balanced20_true10_false10_seed1.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Llama 3.3 70B | v23b | 20 | 85.0% | 87.0% | 100.0% | 70.0% | 100.0% | 14.05 | $0.018 | 2026-04-03 17:26:18 |
| Llama 3.3 70B | v23c | 20 | 85.0% | 87.0% | 100.0% | 70.0% | 100.0% | 19.22 | $0.018 | 2026-04-03 17:42:58 |

### normal_balanced20_true10_false10_seed2.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Llama 3.3 70B | v23 | 20 | 90.0% | 90.9% | 100.0% | 80.0% | 100.0% | 10.99 | $0.015 | 2026-04-03 10:12:34 |
| Llama 3.3 70B | v23c | 20 | 90.0% | 90.9% | 100.0% | 80.0% | 100.0% | 12.02 | $0.018 | 2026-04-03 17:53:09 |

### normal_balanced60_true30_false30_rotation0001_20260403_163406.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Llama 3.3 70B | v23 | 60 | 88.3% | 89.5% | 100.0% | 76.7% | 100.0% | 13.10 | $0.045 | 2026-04-03 10:49:24 |

### normal_balanced60_true30_false30_rotation0002_20260403_185904.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Llama 3.3 70B | v23 | 60 | 93.3% | 93.8% | 100.0% | 86.7% | 100.0% | 9.33 | $0.045 | 2026-04-03 13:08:38 |
| Llama 3.3 70B | v23c | 60 | 93.3% | 93.8% | 100.0% | 86.7% | 100.0% | 13.11 | $0.056 | 2026-04-03 18:13:14 |
| Llama 3.3 70B | v24j | 60 | 93.3% | 93.8% | 100.0% | 86.7% | 100.0% | 14.06 | $0.076 | 2026-04-07 18:26:07 |
| Llama 3.3 70B | v24h | 60 | 91.7% | 92.3% | 100.0% | 83.3% | 100.0% | 13.31 | $0.053 | 2026-04-06 19:16:41 |
| Llama 3.3 70B | v24i | 60 | 91.7% | 92.3% | 100.0% | 83.3% | 98.3% | 16.40 | $0.079 | 2026-04-07 17:19:18 |
| Llama 3.3 70B | v24b | 60 | 91.7% | 92.3% | 100.0% | 83.3% | 95.0% | 17.67 | $0.061 | 2026-04-05 17:28:29 |
| Llama 3.3 70B | v24g | 60 | 91.7% | 92.1% | 96.7% | 86.7% | 100.0% | 18.96 | $0.066 | 2026-04-06 18:45:25 |
| Llama 3.3 70B | v24j | 60 | 91.7% | 92.1% | 96.7% | 86.7% | 100.0% | 19.39 | $0.081 | 2026-04-07 19:41:43 |
| Llama 3.3 70B | v24c | 60 | 91.7% | 91.8% | 93.3% | 90.0% | 98.3% | 17.39 | $0.071 | 2026-04-05 18:51:39 |
| Llama 3.3 70B | v24j | 60 | 90.0% | 90.9% | 100.0% | 80.0% | 100.0% | 14.74 | $0.082 | 2026-04-07 20:20:47 |
| Llama 3.3 70B | v24f | 60 | 90.0% | 90.6% | 96.7% | 83.3% | 100.0% | 14.32 | $0.067 | 2026-04-06 18:19:17 |
| Llama 3.3 70B | v24e | 60 | 90.0% | 90.3% | 93.3% | 86.7% | 98.3% | 13.78 | $0.068 | 2026-04-06 17:59:56 |
| Llama 3.3 70B | v24d | 60 | 88.3% | 88.5% | 90.0% | 86.7% | 96.7% | 23.39 | $0.069 | 2026-04-05 19:25:45 |
| Llama 3.3 70B | v24a | 60 | 88.3% | 88.5% | 90.0% | 86.7% | 96.7% | 17.61 | $0.075 | 2026-04-05 17:04:29 |
| Llama 3.3 70B | v23 | 60 | 80.0% | 78.6% | 73.3% | 86.7% | 86.7% | 14.46 | $0.066 | 2026-04-03 15:01:40 |
| Llama 3.3 70B | v24j | 60 | 66.7% | 73.0% | 90.0% | 43.3% | 96.7% | 23.20 | $0.068 | 2026-04-07 19:21:30 |
