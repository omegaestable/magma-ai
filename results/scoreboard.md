# Paid Model Scoreboard

Generated: 2026-03-20 17:53:34 UTC
Runs indexed: 11
Benchmarks indexed: 5
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
| Best overall | Qwen3.5 122B on normal_balanced12_true6_false6_seed0.jsonl with V13 · F1 100.0% · Acc 100.0% · Cost $0.022 |
| Lowest cost | Llama 3.3 70B on hard1_balanced14_true7_false7_seed0.jsonl with Control · Cost $0.006 · F1 0.0% |
| Fastest avg time | Gemini 2.5 Pro on hard1_balanced6_true3_false3_seed0.jsonl with V10 · Avg 11.35s · F1 28.6% |

## Best By Benchmark And Model

| Benchmark File | Difficulty | Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| hard1_balanced14_true7_false7_seed0.jsonl | hard1 | Llama 3.3 70B | V13 | 14 | 57.1% | 66.7% | 85.7% | 28.6% | 100.0% | 17.90 | $0.015 |
| hard1_balanced6_true3_false3_seed0.jsonl | hard1 | Gemini 2.5 Pro | V13 | 6 | 50.0% | 57.1% | 66.7% | 33.3% | 100.0% | 12.48 | $0.016 |
| hard2_balanced14_true7_false7_seed0.jsonl | hard2 | Llama 3.3 70B | V13 | 14 | 50.0% | 58.8% | 71.4% | 28.6% | 100.0% | 15.73 | $0.018 |
| hard2_balanced14_true7_false7_seed0.jsonl | hard2 | Qwen3.5 122B | V13 | 14 | 57.1% | 70.0% | 100.0% | 14.3% | 100.0% | 71.25 | $0.514 |
| normal_balanced10_true5_false5_seed0.jsonl | normal | Llama 3.3 70B | V12 | 10 | 50.0% | 66.7% | 100.0% | 0.0% | 100.0% | 34.22 | $0.011 |
| normal_balanced12_true6_false6_seed0.jsonl | normal | Llama 3.3 70B | V13 | 12 | 75.0% | 76.9% | 83.3% | 66.7% | 100.0% | 13.35 | $0.013 |
| normal_balanced12_true6_false6_seed0.jsonl | normal | Qwen3.5 122B | V13 | 12 | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 53.29 | $0.022 |

## All Paid Runs By Benchmark

### hard1_balanced14_true7_false7_seed0.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Llama 3.3 70B | V13 | 14 | 57.1% | 66.7% | 85.7% | 28.6% | 100.0% | 17.90 | $0.015 | 2026-03-20 10:31:36 |
| Llama 3.3 70B | V10 | 14 | 57.1% | 66.7% | 85.7% | 28.6% | 92.9% | 46.47 | $0.019 | 2026-03-20 10:27:17 |
| Llama 3.3 70B | Control | 14 | 50.0% | 0.0% | 0.0% | 100.0% | 92.9% | 25.97 | $0.006 | 2026-03-20 10:39:32 |

### hard1_balanced6_true3_false3_seed0.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Gemini 2.5 Pro | V13 | 6 | 50.0% | 57.1% | 66.7% | 33.3% | 100.0% | 12.48 | $0.016 | 2026-03-20 10:52:35 |
| Gemini 2.5 Pro | V10 | 6 | 16.7% | 28.6% | 33.3% | 0.0% | 100.0% | 11.35 | $0.017 | 2026-03-20 10:46:27 |

### hard2_balanced14_true7_false7_seed0.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Qwen3.5 122B | V13 | 14 | 57.1% | 70.0% | 100.0% | 14.3% | 100.0% | 71.25 | $0.514 | 2026-03-20 11:53:10 |
| Llama 3.3 70B | V13 | 14 | 50.0% | 58.8% | 71.4% | 28.6% | 100.0% | 15.73 | $0.018 | 2026-03-20 11:33:11 |

### normal_balanced10_true5_false5_seed0.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Llama 3.3 70B | V12 | 10 | 50.0% | 66.7% | 100.0% | 0.0% | 100.0% | 34.22 | $0.011 | 2026-03-20 09:04:09 |

### normal_balanced12_true6_false6_seed0.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Qwen3.5 122B | V13 | 12 | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 53.29 | $0.022 | 2026-03-20 09:54:35 |
| Qwen3.5 122B | V10 | 12 | 83.3% | 85.7% | 100.0% | 66.7% | 100.0% | 45.99 | $0.021 | 2026-03-20 09:43:49 |
| Llama 3.3 70B | V13 | 12 | 75.0% | 76.9% | 83.3% | 66.7% | 100.0% | 13.35 | $0.013 | 2026-03-20 09:24:02 |
