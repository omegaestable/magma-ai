# Paid Model Scoreboard

Generated: 2026-03-22 15:59:12 UTC
Runs indexed: 57
Benchmarks indexed: 19
Models indexed: 3

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
| Best overall | Qwen3.5 122B on normal_balanced12_true6_false6_seed0.jsonl with V13 · F1 100.0% · Acc 100.0% · Cost $0.024 |
| Lowest cost | Llama 3.3 70B on hard1_balanced14_true7_false7_seed0.jsonl with Control · Cost $0.005 · F1 0.0% |
| Fastest avg time | Llama 3.3 70B on normal_balanced20_true10_false10_seed1.jsonl with v14_proof_required · Avg 7.08s · F1 0.0% |

## Best By Benchmark And Model

| Benchmark File | Difficulty | Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| hard1_balanced14_true7_false7_seed0.jsonl | hard1 | Llama 3.3 70B | V13 | 14 | 57.1% | 66.7% | 85.7% | 28.6% | 100.0% | 17.90 | $0.017 |
| hard1_balanced6_true3_false3_seed0.jsonl | hard1 | Gemini 2.5 Pro | V13 | 6 | 50.0% | 57.1% | 66.7% | 33.3% | 100.0% | 12.48 | $0.018 |
| hard2_balanced14_true7_false7_seed0.jsonl | hard2 | Llama 3.3 70B | V13 | 14 | 50.0% | 58.8% | 71.4% | 28.6% | 100.0% | 15.73 | $0.018 |
| hard2_balanced14_true7_false7_seed0.jsonl | hard2 | Qwen3.5 122B | V13 | 14 | 57.1% | 70.0% | 100.0% | 14.3% | 100.0% | 71.25 | $0.514 |
| normal_balanced10_true5_false5_seed0.jsonl | normal | Llama 3.3 70B | V12 | 10 | 50.0% | 66.7% | 100.0% | 0.0% | 100.0% | 34.22 | $0.012 |
| normal_balanced10_true5_false5_seed0_v10_proof_required_playground_parity.jsonl | normal | Llama 3.3 70B | V10 | 10 | 40.0% | 50.0% | 60.0% | 20.0% | 90.0% | 11.48 | $0.015 |
| normal_balanced10_true5_false5_seed0_v13_proof_required_fixed2_playground_parity.jsonl | normal | Llama 3.3 70B | V13 | 10 | 60.0% | 71.4% | 100.0% | 20.0% | 100.0% | 28.08 | $0.016 |
| normal_balanced10_true5_false5_seed0_v13_proof_required_fixed_playground_parity.jsonl | normal | Llama 3.3 70B | V13 | 10 | 70.0% | 72.7% | 80.0% | 60.0% | 100.0% | 10.48 | $0.015 |
| normal_balanced10_true5_false5_seed0_v13_proof_required_playground_parity.jsonl | normal | Llama 3.3 70B | V13 | 10 | 50.0% | 66.7% | 100.0% | 0.0% | 100.0% | 18.48 | $0.017 |
| normal_balanced10_true5_false5_seed0_v13_proof_required_trimmed_playground_parity.jsonl | normal | Llama 3.3 70B | V13 | 10 | 10.0% | 18.2% | 20.0% | 0.0% | 100.0% | 17.74 | $0.017 |
| normal_balanced12_true6_false6_seed0.jsonl | normal | Llama 3.3 70B | V13 | 12 | 75.0% | 76.9% | 83.3% | 66.7% | 100.0% | 13.35 | $0.015 |
| normal_balanced12_true6_false6_seed0.jsonl | normal | Qwen3.5 122B | V13 | 12 | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 53.29 | $0.024 |
| normal_balanced12_true6_false6_seed0_v10_proof_required_playground_parity.jsonl | normal | Llama 3.3 70B | V10 | 12 | 41.7% | 53.3% | 66.7% | 16.7% | 83.3% | 34.45 | $0.017 |
| normal_balanced12_true6_false6_seed0_v13_proof_required_fixed2_playground_parity.jsonl | normal | Llama 3.3 70B | V13 | 12 | 66.7% | 75.0% | 100.0% | 33.3% | 100.0% | 11.14 | $0.019 |
| normal_balanced12_true6_false6_seed0_v13_proof_required_fixed_playground_parity.jsonl | normal | Llama 3.3 70B | V13 | 12 | 50.0% | 25.0% | 16.7% | 83.3% | 100.0% | 20.76 | $0.019 |
| normal_balanced12_true6_false6_seed0_v13_proof_required_playground_parity.jsonl | normal | Llama 3.3 70B | V13 | 12 | 50.0% | 66.7% | 100.0% | 0.0% | 83.3% | 22.67 | $0.021 |
| normal_balanced12_true6_false6_seed0_v13_proof_required_trimmed_playground_parity.jsonl | normal | Llama 3.3 70B | V13 | 12 | 66.7% | 66.7% | 66.7% | 66.7% | 100.0% | 40.10 | $0.021 |
| normal_balanced12_true6_false6_seed0_vcontrol_playground_parity.jsonl | normal | Llama 3.3 70B | vcontrol | 12 | 50.0% | 0.0% | 0.0% | 100.0% | 100.0% | 22.49 | $0.006 |
| normal_balanced20_true10_false10_seed0.jsonl | normal | Llama 3.3 70B | candidate_cycle0005 | 20 | 60.0% | 66.7% | 80.0% | 40.0% | 100.0% | 22.05 | $0.031 |
| normal_balanced20_true10_false10_seed1.jsonl | normal | Llama 3.3 70B | V13 | 20 | 50.0% | 61.5% | 80.0% | 20.0% | 100.0% | 11.35 | $0.031 |
| normal_balanced20_true10_false10_seed2.jsonl | normal | Llama 3.3 70B | V13 | 20 | 40.0% | 57.1% | 80.0% | 0.0% | 100.0% | 21.35 | $0.031 |

## All Paid Runs By Benchmark

### hard1_balanced14_true7_false7_seed0.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Llama 3.3 70B | V13 | 14 | 57.1% | 66.7% | 85.7% | 28.6% | 100.0% | 17.90 | $0.017 | 2026-03-20 10:31:36 |
| Llama 3.3 70B | V10 | 14 | 57.1% | 66.7% | 85.7% | 28.6% | 92.9% | 46.47 | $0.018 | 2026-03-20 10:27:17 |
| Llama 3.3 70B | Control | 14 | 50.0% | 0.0% | 0.0% | 100.0% | 92.9% | 25.97 | $0.005 | 2026-03-20 10:39:32 |

### hard1_balanced6_true3_false3_seed0.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Gemini 2.5 Pro | V13 | 6 | 50.0% | 57.1% | 66.7% | 33.3% | 100.0% | 12.48 | $0.018 | 2026-03-20 10:52:35 |
| Gemini 2.5 Pro | V10 | 6 | 16.7% | 28.6% | 33.3% | 0.0% | 100.0% | 11.35 | $0.016 | 2026-03-20 10:46:27 |

### hard2_balanced14_true7_false7_seed0.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Qwen3.5 122B | V13 | 14 | 57.1% | 70.0% | 100.0% | 14.3% | 100.0% | 71.25 | $0.514 | 2026-03-20 11:53:10 |
| Llama 3.3 70B | V13 | 14 | 50.0% | 58.8% | 71.4% | 28.6% | 100.0% | 15.73 | $0.018 | 2026-03-20 11:33:11 |

### normal_balanced10_true5_false5_seed0.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Llama 3.3 70B | V12 | 10 | 50.0% | 66.7% | 100.0% | 0.0% | 100.0% | 34.22 | $0.012 | 2026-03-20 09:04:09 |
| Llama 3.3 70B | V13 | 10 | 50.0% | 66.7% | 100.0% | 0.0% | 100.0% | 27.83 | $0.016 | 2026-03-20 21:33:39 |
| Llama 3.3 70B | V10 | 10 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 51.30 | $0.015 | 2026-03-20 21:28:42 |

### normal_balanced10_true5_false5_seed0_v10_proof_required_playground_parity.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Llama 3.3 70B | V10 | 10 | 40.0% | 50.0% | 60.0% | 20.0% | 90.0% | 11.48 | $0.015 | 2026-03-20 21:49:17 |

### normal_balanced10_true5_false5_seed0_v13_proof_required_fixed2_playground_parity.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Llama 3.3 70B | V13 | 10 | 60.0% | 71.4% | 100.0% | 20.0% | 100.0% | 28.08 | $0.016 | 2026-03-20 23:38:56 |

### normal_balanced10_true5_false5_seed0_v13_proof_required_fixed_playground_parity.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Llama 3.3 70B | V13 | 10 | 70.0% | 72.7% | 80.0% | 60.0% | 100.0% | 10.48 | $0.015 | 2026-03-20 23:29:27 |

### normal_balanced10_true5_false5_seed0_v13_proof_required_playground_parity.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Llama 3.3 70B | V13 | 10 | 50.0% | 66.7% | 100.0% | 0.0% | 100.0% | 18.48 | $0.017 | 2026-03-20 21:53:40 |

### normal_balanced10_true5_false5_seed0_v13_proof_required_trimmed_playground_parity.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Llama 3.3 70B | V13 | 10 | 10.0% | 18.2% | 20.0% | 0.0% | 100.0% | 17.74 | $0.017 | 2026-03-20 23:23:42 |

### normal_balanced12_true6_false6_seed0.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Qwen3.5 122B | V13 | 12 | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 53.29 | $0.024 | 2026-03-20 09:54:35 |
| Qwen3.5 122B | V10 | 12 | 83.3% | 85.7% | 100.0% | 66.7% | 100.0% | 45.99 | $0.021 | 2026-03-20 09:43:49 |
| Llama 3.3 70B | V13 | 12 | 75.0% | 76.9% | 83.3% | 66.7% | 100.0% | 13.35 | $0.015 | 2026-03-20 09:24:02 |

### normal_balanced12_true6_false6_seed0_v10_proof_required_playground_parity.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Llama 3.3 70B | V10 | 12 | 41.7% | 53.3% | 66.7% | 16.7% | 83.3% | 34.45 | $0.017 | 2026-03-20 22:42:00 |

### normal_balanced12_true6_false6_seed0_v13_proof_required_fixed2_playground_parity.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Llama 3.3 70B | V13 | 12 | 66.7% | 75.0% | 100.0% | 33.3% | 100.0% | 11.14 | $0.019 | 2026-03-20 23:41:11 |

### normal_balanced12_true6_false6_seed0_v13_proof_required_fixed_playground_parity.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Llama 3.3 70B | V13 | 12 | 50.0% | 25.0% | 16.7% | 83.3% | 100.0% | 20.76 | $0.019 | 2026-03-20 23:33:37 |

### normal_balanced12_true6_false6_seed0_v13_proof_required_playground_parity.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Llama 3.3 70B | V13 | 12 | 50.0% | 66.7% | 100.0% | 0.0% | 83.3% | 22.67 | $0.021 | 2026-03-20 22:46:44 |

### normal_balanced12_true6_false6_seed0_v13_proof_required_trimmed_playground_parity.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Llama 3.3 70B | V13 | 12 | 66.7% | 66.7% | 66.7% | 66.7% | 100.0% | 40.10 | $0.021 | 2026-03-20 23:04:47 |

### normal_balanced12_true6_false6_seed0_vcontrol_playground_parity.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Llama 3.3 70B | vcontrol | 12 | 50.0% | 0.0% | 0.0% | 100.0% | 100.0% | 22.49 | $0.006 | 2026-03-20 22:51:23 |

### normal_balanced20_true10_false10_seed0.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Llama 3.3 70B | candidate_cycle0005 | 20 | 60.0% | 66.7% | 80.0% | 40.0% | 100.0% | 22.05 | $0.031 | 2026-03-21 17:49:56 |
| Llama 3.3 70B | V13 | 20 | 50.0% | 64.3% | 90.0% | 10.0% | 100.0% | 18.02 | $0.031 | 2026-03-21 00:12:47 |
| Llama 3.3 70B | candidate_cycle0004 | 20 | 50.0% | 61.5% | 80.0% | 20.0% | 100.0% | 19.11 | $0.032 | 2026-03-21 16:35:35 |
| Llama 3.3 70B | V13 | 20 | 45.0% | 59.3% | 80.0% | 10.0% | 100.0% | 30.16 | $0.032 | 2026-03-21 16:20:51 |
| Llama 3.3 70B | v16_early_false_signal | 20 | 50.0% | 37.5% | 30.0% | 70.0% | 100.0% | 15.81 | $0.031 | 2026-03-22 09:28:49 |
| Llama 3.3 70B | v16_early_false_signal | 20 | 50.0% | 37.5% | 30.0% | 70.0% | 100.0% | 46.25 | $0.033 | 2026-03-21 21:00:27 |
| Llama 3.3 70B | v16_early_false_signal | 20 | 50.0% | 28.6% | 20.0% | 80.0% | 100.0% | 26.01 | $0.032 | 2026-03-21 21:44:06 |
| Llama 3.3 70B | v17_corrected | 20 | 50.0% | 0.0% | 0.0% | 100.0% | 100.0% | 18.23 | $0.024 | 2026-03-22 09:44:50 |
| Llama 3.3 70B | candidate_cycle0004 | 20 | 50.0% | 0.0% | 0.0% | 100.0% | 100.0% | 22.74 | $0.025 | 2026-03-21 20:11:56 |
| Llama 3.3 70B | candidate_cycle0003 | 20 | 50.0% | 0.0% | 0.0% | 100.0% | 100.0% | 17.44 | $0.026 | 2026-03-21 09:28:54 |
| Llama 3.3 70B | v14_proof_required | 20 | 50.0% | 0.0% | 0.0% | 100.0% | 100.0% | 13.04 | $0.027 | 2026-03-21 17:28:54 |
| Llama 3.3 70B | v14_proof_required | 20 | 50.0% | 0.0% | 0.0% | 100.0% | 100.0% | 13.89 | $0.027 | 2026-03-22 09:17:09 |
| Llama 3.3 70B | v17_corrected | 20 | 50.0% | 0.0% | 0.0% | 100.0% | 100.0% | 58.43 | $0.061 | 2026-03-21 22:44:08 |
| Llama 3.3 70B | v17_corrected | 20 | 50.0% | 0.0% | 0.0% | 100.0% | 100.0% | 185.55 | $0.074 | 2026-03-21 23:03:28 |

### normal_balanced20_true10_false10_seed1.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Llama 3.3 70B | V13 | 20 | 50.0% | 61.5% | 80.0% | 20.0% | 100.0% | 11.35 | $0.031 | 2026-03-21 16:24:39 |
| Llama 3.3 70B | candidate_cycle0004 | 20 | 50.0% | 61.5% | 80.0% | 20.0% | 100.0% | 13.56 | $0.033 | 2026-03-21 16:40:07 |
| Llama 3.3 70B | V13 | 20 | 45.0% | 59.3% | 80.0% | 10.0% | 100.0% | 25.75 | $0.031 | 2026-03-21 00:21:22 |
| Llama 3.3 70B | candidate_cycle0005 | 20 | 40.0% | 53.8% | 70.0% | 10.0% | 100.0% | 16.49 | $0.031 | 2026-03-21 17:55:26 |
| Llama 3.3 70B | v16_early_false_signal | 20 | 45.0% | 26.7% | 20.0% | 70.0% | 100.0% | 29.68 | $0.031 | 2026-03-21 21:10:21 |
| Llama 3.3 70B | candidate_cycle0004 | 20 | 50.0% | 0.0% | 0.0% | 100.0% | 100.0% | 18.97 | $0.022 | 2026-03-21 20:18:16 |
| Llama 3.3 70B | v17_corrected | 20 | 50.0% | 0.0% | 0.0% | 100.0% | 100.0% | 23.50 | $0.024 | 2026-03-22 09:52:41 |
| Llama 3.3 70B | candidate_cycle0003 | 20 | 50.0% | 0.0% | 0.0% | 100.0% | 100.0% | 28.22 | $0.026 | 2026-03-21 09:38:19 |
| Llama 3.3 70B | v14_proof_required | 20 | 50.0% | 0.0% | 0.0% | 100.0% | 100.0% | 7.08 | $0.026 | 2026-03-22 09:19:31 |
| Llama 3.3 70B | v16_early_false_signal | 20 | 35.0% | 0.0% | 0.0% | 70.0% | 100.0% | 16.13 | $0.032 | 2026-03-22 09:34:12 |

### normal_balanced20_true10_false10_seed2.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Llama 3.3 70B | V13 | 20 | 40.0% | 57.1% | 80.0% | 0.0% | 100.0% | 21.35 | $0.031 | 2026-03-21 00:28:29 |
| Llama 3.3 70B | candidate_cycle0005 | 20 | 40.0% | 53.8% | 70.0% | 10.0% | 100.0% | 13.46 | $0.032 | 2026-03-21 17:59:55 |
| Llama 3.3 70B | V13 | 20 | 35.0% | 51.8% | 70.0% | 0.0% | 100.0% | 13.68 | $0.031 | 2026-03-21 16:29:13 |
| Llama 3.3 70B | candidate_cycle0004 | 20 | 35.0% | 48.0% | 60.0% | 10.0% | 100.0% | 15.05 | $0.034 | 2026-03-21 16:45:08 |
| Llama 3.3 70B | v16_early_false_signal | 20 | 55.0% | 40.0% | 30.0% | 80.0% | 100.0% | 13.65 | $0.032 | 2026-03-22 09:38:45 |
| Llama 3.3 70B | v16_early_false_signal | 20 | 50.0% | 28.6% | 20.0% | 80.0% | 100.0% | 52.30 | $0.037 | 2026-03-21 21:27:48 |
| Llama 3.3 70B | v17_corrected | 20 | 50.0% | 0.0% | 0.0% | 100.0% | 100.0% | 18.35 | $0.023 | 2026-03-22 09:58:48 |
| Llama 3.3 70B | candidate_cycle0003 | 20 | 50.0% | 0.0% | 0.0% | 100.0% | 100.0% | 13.22 | $0.026 | 2026-03-21 09:42:44 |
| Llama 3.3 70B | v14_proof_required | 20 | 50.0% | 0.0% | 0.0% | 100.0% | 100.0% | 12.07 | $0.027 | 2026-03-22 09:23:32 |
