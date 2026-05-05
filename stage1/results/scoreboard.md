# Paid Model Scoreboard

Generated: 2026-04-18 01:15:44 UTC
Runs indexed: 108
Benchmarks indexed: 67
Models indexed: 3

Paid-model runs only. Local/free runs are excluded from this view.
Cost is exact when token usage was saved in the run JSON; otherwise it is reconstructed from the prompt/response text and priced with current OpenRouter weighted-average input/output rates.

## Pricing Basis

| Model | Input $/1M | Output $/1M |
| --- | ---: | ---: |
| Gemini 2.5 Pro | $0.956 | $10.020 |
| Llama 3.3 70B | $0.342 | $0.563 |
| Qwen3.5 122B | $0.384 | $2.880 |
| GPT-OSS-120B | $0.500 | $1.500 |
| Gemma 4 31B IT | $0.200 | $0.400 |

## Highlights

| View | Run |
| --- | --- |
| Best overall | Llama 3.3 70B on normal_balanced50_true10_false40_rotation0012_20260413_161807_v26b_llama-3-3-70b-instruct.jsonl with v26b · F1 100.0% · Acc 100.0% · Cost $0.007 |
| Lowest cost | Llama 3.3 70B on gate_normal_30_30_v23c_llama-3-3-70b-instruct.jsonl with v23c · Cost $0.001 · F1 0.0% |
| Fastest avg time | Llama 3.3 70B on gate_normal_30_30_v23c_llama-3-3-70b-instruct.jsonl with v23c · Avg 0.00s · F1 0.0% |

## Best By Benchmark And Model

| Benchmark File | Difficulty | Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| gate_normal_30_30_v23c_gemma-4-31b-it.jsonl | normal | Gemma 4 31B IT | v23c | 60 | 93.3% | 93.8% | 100.0% | 86.7% | 100.0% | 47.13 | $0.035 |
| gate_normal_30_30_v23c_gpt-oss-120b.jsonl | normal | GPT-OSS-120B | v23c | 60 | 93.3% | 93.8% | 100.0% | 86.7% | 100.0% | 14.31 | $0.138 |
| gate_normal_30_30_v23c_llama-3-3-70b-instruct.jsonl | normal | Llama 3.3 70B | v23c | 60 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.00 | $0.001 |
| gate_normal_30_30_v24j_gemma-4-31b-it.jsonl | normal | Gemma 4 31B IT | v24j | 60 | 93.3% | 93.8% | 100.0% | 86.7% | 100.0% | 66.23 | $0.051 |
| gate_normal_30_30_v24j_gpt-oss-120b.jsonl | normal | GPT-OSS-120B | v24j | 60 | 95.0% | 95.2% | 100.0% | 90.0% | 100.0% | 5.97 | $0.167 |
| gate_normal_50_50_v24j_gpt-oss-120b.jsonl | normal | GPT-OSS-120B | v24j | 100 | 94.0% | 94.3% | 100.0% | 88.0% | 100.0% | 5.50 | $0.282 |
| gate_normal_50_50_v24j_llama-3-3-70b-instruct.jsonl | normal | Llama 3.3 70B | v24j | 1 | 100.0% | 100.0% | 100.0% | 0.0% | 100.0% | 18.20 | $0.001 |
| hard2_balanced20_true10_false10_rotation0017_20260415_021226_v26f_gpt-oss-120b.jsonl | hard2 | GPT-OSS-120B | v26f | 20 | 40.0% | 50.0% | 60.0% | 20.0% | 95.0% | 73.03 | $0.104 |
| hard2_balanced30_true15_false15_rotation0013_20260414_010332_v26f_gpt-oss-120b.jsonl | hard2 | GPT-OSS-120B | v26f | 30 | 23.3% | 37.8% | 46.7% | 0.0% | 76.7% | 46.19 | $0.120 |
| hard2_balanced50_true10_false40_rotation0012_20260413_161807_v26b_gpt-oss-120b.jsonl | hard2 | GPT-OSS-120B | v26b | 50 | 20.0% | 33.3% | 100.0% | 0.0% | 100.0% | 31.09 | $0.171 |
| hard2_false30_distill_20260412_v26a_gpt-oss-120b.jsonl | hard2 | GPT-OSS-120B | v26a | 30 | 6.7% | 0.0% | 0.0% | 6.7% | 100.0% | 17.36 | $0.104 |
| hard2_v26a_gpt-oss-120b.jsonl | hard2 | GPT-OSS-120B | v26a | 20 | 40.0% | 57.1% | 100.0% | 0.0% | 100.0% | 12.49 | $0.067 |
| hard2_v26b_gpt-oss-120b.jsonl | hard2 | GPT-OSS-120B | v26b | 20 | 40.0% | 57.1% | 100.0% | 0.0% | 100.0% | 6.96 | $0.066 |
| hard3_balanced20_true10_false10_rotation0001_20260403_163406.jsonl | hard3 | Llama 3.3 70B | v23 | 20 | 50.0% | 66.7% | 100.0% | 0.0% | 100.0% | 16.13 | $0.015 |
| hard3_balanced20_true10_false10_rotation0010_20260413_032310_v26a_gpt-oss-120b.jsonl | hard3 | GPT-OSS-120B | v26a | 20 | 65.0% | 74.1% | 100.0% | 30.0% | 100.0% | 16.85 | $0.072 |
| hard3_balanced20_true10_false10_rotation0011_20260413_042258_v26b_gpt-oss-120b.jsonl | hard3 | GPT-OSS-120B | v26b | 20 | 75.0% | 80.0% | 100.0% | 50.0% | 100.0% | 14.37 | $0.078 |
| hard3_balanced20_true10_false10_rotation0017_20260415_021226_v26f_gpt-oss-120b.jsonl | hard3 | GPT-OSS-120B | v26f | 20 | 70.0% | 75.0% | 90.0% | 50.0% | 90.0% | 54.66 | $0.095 |
| hard3_balanced30_true0_false30_rotation0007_20260412_031528_v26a_gpt-oss-120b.jsonl | hard3 | GPT-OSS-120B | v26a | 30 | 36.7% | 0.0% | 0.0% | 36.7% | 100.0% | 12.13 | $0.113 |
| hard3_balanced30_true15_false15_rotation0008_20260412_034307_v26a_gpt-oss-120b.jsonl | hard3 | GPT-OSS-120B | v26a | 30 | 70.0% | 76.9% | 100.0% | 40.0% | 100.0% | 8.98 | $0.111 |
| hard3_balanced40_true20_false20_rotation0002_20260403_185904.jsonl | hard3 | Llama 3.3 70B | v24j | 40 | 72.5% | 78.4% | 100.0% | 45.0% | 100.0% | 23.98 | $0.059 |
| hard3_balanced40_true20_false20_rotation0002_20260403_185904_v24j_gpt-oss-120b.jsonl | hard3 | GPT-OSS-120B | v24j | 40 | 62.5% | 72.7% | 100.0% | 25.0% | 100.0% | 12.70 | $0.137 |
| hard3_balanced40_true20_false20_rotation0002_20260403_185904_v26a_gpt-oss-120b.jsonl | hard3 | GPT-OSS-120B | v26a | 40 | 70.0% | 76.9% | 100.0% | 40.0% | 100.0% | 11.77 | $0.154 |
| hard3_balanced40_true20_false20_rotation0014_20260415_014503_v26f_gpt-oss-120b.jsonl | hard3 | GPT-OSS-120B | v26f | 40 | 65.0% | 69.6% | 80.0% | 50.0% | 90.0% | 71.44 | $0.195 |
| hard3_balanced50_true10_false40_rotation0012_20260413_161807_v26b_gpt-oss-120b.jsonl | hard3 | GPT-OSS-120B | v26b | 50 | 50.0% | 44.4% | 100.0% | 37.5% | 100.0% | 31.52 | $0.194 |
| hard3_balanced50_true10_false40_rotation0012_20260413_161807_v26c_gpt-oss-120b.jsonl | hard3 | GPT-OSS-120B | v26c | 50 | 46.0% | 37.2% | 80.0% | 37.5% | 98.0% | 52.73 | $0.246 |
| hard3_balanced50_true10_false40_rotation0012_20260413_161807_v26d_gpt-oss-120b.jsonl | hard3 | GPT-OSS-120B | v26d | 50 | 68.0% | 55.6% | 100.0% | 60.0% | 100.0% | 41.89 | $0.270 |
| hard3_balanced60_true30_false30_rotation0006_20260411_222025_v23c_gpt-oss-120b.jsonl | hard3 | GPT-OSS-120B | v23c | 60 | 50.0% | 66.7% | 100.0% | 0.0% | 100.0% | 7.17 | $0.149 |
| hard3_balanced60_true30_false30_rotation0006_20260411_222025_v24j_gpt-oss-120b.jsonl | hard3 | GPT-OSS-120B | v24j | 60 | 58.3% | 70.6% | 100.0% | 16.7% | 100.0% | 7.58 | $0.196 |
| hard_balanced20_true10_false10_rotation0005_20260411_203024_v23c_gemma-4-31b-it.jsonl | hard | Gemma 4 31B IT | v23c | 20 | 55.0% | 69.0% | 100.0% | 10.0% | 100.0% | 53.35 | $0.012 |
| hard_balanced20_true10_false10_rotation0005_20260411_203024_v23c_gpt-oss-120b.jsonl | hard | GPT-OSS-120B | v23c | 20 | 55.0% | 69.0% | 100.0% | 10.0% | 100.0% | 23.40 | $0.050 |
| hard_balanced20_true10_false10_rotation0005_20260411_203024_v24j_gemma-4-31b-it.jsonl | hard | Gemma 4 31B IT | v24j | 20 | 55.0% | 69.0% | 100.0% | 10.0% | 100.0% | 59.79 | $0.018 |
| hard_balanced20_true10_false10_rotation0005_20260411_203024_v24j_gpt-oss-120b.jsonl | hard | GPT-OSS-120B | v24j | 20 | 55.0% | 69.0% | 100.0% | 10.0% | 100.0% | 18.69 | $0.066 |
| hard_balanced40_true20_false20_rotation0001_20260403_163406.jsonl | hard | Llama 3.3 70B | v23 | 40 | 55.0% | 69.0% | 100.0% | 10.0% | 100.0% | 13.88 | $0.030 |
| hard_v24j_llama-3-3-70b-instruct.jsonl | hard | Llama 3.3 70B | v24j | 200 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.00 | $0.144 |
| magma_eval_test_10.jsonl | magma | Llama 3.3 70B | magma_eval_test | 8 | 87.5% | 85.7% | 100.0% | 80.0% | 100.0% | 15.85 | $0.006 |
| mixed_hard23_balanced60_true30_false30_rotation0013_20260414_010332_v26d_gpt-oss-120b.jsonl | mixed | GPT-OSS-120B | v26d | 60 | 65.0% | 71.2% | 86.7% | 43.3% | 98.3% | 49.25 | $0.324 |
| mixed_hard23_balanced60_true30_false30_rotation0013_20260414_010332_v26e_gpt-oss-120b.jsonl | mixed | GPT-OSS-120B | v26e | 60 | 56.7% | 69.8% | 100.0% | 13.3% | 100.0% | 37.65 | $0.263 |
| normal_balanced10_true5_false5_seed0.jsonl | normal | Llama 3.3 70B | v23b | 10 | 90.0% | 90.9% | 100.0% | 80.0% | 100.0% | 14.72 | $0.009 |
| normal_balanced10_true5_false5_seed1.jsonl | normal | Llama 3.3 70B | v23b | 10 | 80.0% | 83.3% | 100.0% | 60.0% | 100.0% | 15.80 | $0.009 |
| normal_balanced20_true10_false10_rotation0005_20260411_203024_v23c_gemma-4-31b-it.jsonl | normal | Gemma 4 31B IT | v23c | 20 | 85.0% | 87.0% | 100.0% | 70.0% | 100.0% | 30.57 | $0.012 |
| normal_balanced20_true10_false10_rotation0005_20260411_203024_v23c_gpt-oss-120b.jsonl | normal | GPT-OSS-120B | v23c | 20 | 85.0% | 87.0% | 100.0% | 70.0% | 100.0% | 15.63 | $0.048 |
| normal_balanced20_true10_false10_rotation0005_20260411_203024_v24j_gemma-4-31b-it.jsonl | normal | Gemma 4 31B IT | v24j | 20 | 85.0% | 87.0% | 100.0% | 70.0% | 100.0% | 44.08 | $0.017 |
| normal_balanced20_true10_false10_rotation0005_20260411_203024_v24j_gpt-oss-120b.jsonl | normal | GPT-OSS-120B | v24j | 20 | 85.0% | 87.0% | 100.0% | 70.0% | 100.0% | 10.64 | $0.058 |
| normal_balanced20_true10_false10_rotation0010_20260413_032310_v26a_gpt-oss-120b.jsonl | normal | GPT-OSS-120B | v26a | 20 | 95.0% | 95.2% | 100.0% | 90.0% | 100.0% | 10.06 | $0.060 |
| normal_balanced20_true10_false10_rotation0011_20260413_042258_v26b_gpt-oss-120b.jsonl | normal | GPT-OSS-120B | v26b | 20 | 95.0% | 95.2% | 100.0% | 90.0% | 100.0% | 8.65 | $0.059 |
| normal_balanced20_true10_false10_seed0.jsonl | normal | Llama 3.3 70B | v23b | 20 | 90.0% | 90.9% | 100.0% | 80.0% | 100.0% | 17.37 | $0.018 |
| normal_balanced20_true10_false10_seed0_v24j_gpt-oss-120b.jsonl | normal | GPT-OSS-120B | v24j | 20 | 90.0% | 90.9% | 100.0% | 80.0% | 100.0% | 13.87 | $0.055 |
| normal_balanced20_true10_false10_seed0_v24j_llama-3-3-70b-instruct.jsonl | normal | Llama 3.3 70B | v24j | 20 | 80.0% | 80.0% | 80.0% | 80.0% | 100.0% | 234.38 | $0.027 |
| normal_balanced20_true10_false10_seed0_v26a_gemma-4-31b-it.jsonl | normal | Gemma 4 31B IT | v26a | 20 | 90.0% | 90.9% | 100.0% | 80.0% | 100.0% | 76.26 | $0.018 |
| normal_balanced20_true10_false10_seed0_v26a_gpt-oss-120b.jsonl | normal | GPT-OSS-120B | v26a | 20 | 90.0% | 90.9% | 100.0% | 80.0% | 100.0% | 12.70 | $0.060 |
| normal_balanced20_true10_false10_seed0_v26a_llama-3-3-70b-instruct.jsonl | normal | Llama 3.3 70B | v26a | 1 | 100.0% | 0.0% | 0.0% | 100.0% | 100.0% | 199.41 | $0.001 |
| normal_balanced20_true10_false10_seed1.jsonl | normal | Llama 3.3 70B | v23b | 20 | 85.0% | 87.0% | 100.0% | 70.0% | 100.0% | 14.05 | $0.018 |
| normal_balanced20_true10_false10_seed2.jsonl | normal | Llama 3.3 70B | v23 | 20 | 90.0% | 90.9% | 100.0% | 80.0% | 100.0% | 10.99 | $0.015 |
| normal_balanced30_true0_false30_rotation0007_20260412_031528_v26a_gpt-oss-120b.jsonl | normal | GPT-OSS-120B | v26a | 30 | 83.3% | 0.0% | 0.0% | 83.3% | 100.0% | 7.74 | $0.088 |
| normal_balanced30_true15_false15_rotation0008_20260412_034307_v26a_gpt-oss-120b.jsonl | normal | GPT-OSS-120B | v26a | 30 | 90.0% | 90.9% | 100.0% | 80.0% | 100.0% | 9.10 | $0.091 |
| normal_balanced30_true15_false15_rotation0009_20260412_040515_v26a_gpt-oss-120b.jsonl | normal | GPT-OSS-120B | v26a | 30 | 80.0% | 83.3% | 100.0% | 60.0% | 100.0% | 11.91 | $0.090 |
| normal_balanced40_true20_false20_rotation0014_20260415_014503_v26f_gpt-oss-120b.jsonl | normal | GPT-OSS-120B | v26f | 40 | 80.0% | 81.0% | 85.0% | 75.0% | 100.0% | 41.62 | $0.175 |
| normal_balanced40_true20_false20_rotation0018_20260415_041933_v27a_gpt-oss-120b.jsonl | normal | GPT-OSS-120B | v27a | 40 | 67.5% | 58.1% | 45.0% | 90.0% | 100.0% | 30.25 | $0.151 |
| normal_balanced50_true10_false40_rotation0012_20260413_161807_v26b_gpt-oss-120b.jsonl | normal | GPT-OSS-120B | v26b | 50 | 84.0% | 71.4% | 100.0% | 80.0% | 100.0% | 23.70 | $0.149 |
| normal_balanced50_true10_false40_rotation0012_20260413_161807_v26b_llama-3-3-70b-instruct.jsonl | normal | Llama 3.3 70B | v26b | 5 | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 14.92 | $0.007 |
| normal_balanced50_true10_false40_rotation0012_20260413_161807_v26c_gpt-oss-120b.jsonl | normal | GPT-OSS-120B | v26c | 50 | 92.0% | 83.3% | 100.0% | 90.0% | 100.0% | 29.40 | $0.166 |
| normal_balanced50_true10_false40_rotation0012_20260413_161807_v26d_gpt-oss-120b.jsonl | normal | GPT-OSS-120B | v26d | 50 | 92.0% | 80.0% | 80.0% | 95.0% | 96.0% | 24.01 | $0.188 |
| normal_balanced60_true30_false30_rotation0001_20260403_163406.jsonl | normal | Llama 3.3 70B | v23 | 60 | 88.3% | 89.5% | 100.0% | 76.7% | 100.0% | 13.10 | $0.045 |
| normal_balanced60_true30_false30_rotation0002_20260403_185904.jsonl | normal | Llama 3.3 70B | v23 | 60 | 93.3% | 93.8% | 100.0% | 86.7% | 100.0% | 9.33 | $0.045 |
| normal_balanced60_true30_false30_rotation0013_20260414_010332_v26d_gpt-oss-120b.jsonl | normal | GPT-OSS-120B | v26d | 60 | 76.7% | 73.1% | 63.3% | 90.0% | 93.3% | 38.09 | $0.247 |
| normal_balanced60_true30_false30_rotation0013_20260414_010332_v26e_gpt-oss-120b.jsonl | normal | GPT-OSS-120B | v26e | 60 | 90.0% | 90.9% | 100.0% | 80.0% | 100.0% | 17.18 | $0.216 |
| normal_v23c_llama-3-3-70b-instruct.jsonl | normal | Llama 3.3 70B | v23c | 1 | 100.0% | 100.0% | 100.0% | 0.0% | 100.0% | 252.54 | $0.001 |

## All Paid Runs By Benchmark

### gate_normal_30_30_v23c_gemma-4-31b-it.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Gemma 4 31B IT | v23c | 60 | 93.3% | 93.8% | 100.0% | 86.7% | 100.0% | 47.13 | $0.035 | 2026-04-11 14:13:52 |

### gate_normal_30_30_v23c_gpt-oss-120b.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GPT-OSS-120B | v23c | 60 | 93.3% | 93.8% | 100.0% | 86.7% | 100.0% | 14.31 | $0.138 | 2026-04-11 13:34:44 |
| GPT-OSS-120B | v23c | 60 | 78.3% | 79.4% | 83.3% | 73.3% | 78.3% | 8.35 | $0.108 | 2026-04-11 13:33:01 |

### gate_normal_30_30_v23c_llama-3-3-70b-instruct.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Llama 3.3 70B | v23c | 60 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.00 | $0.001 | 2026-04-11 13:25:10 |

### gate_normal_30_30_v24j_gemma-4-31b-it.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Gemma 4 31B IT | v24j | 60 | 93.3% | 93.8% | 100.0% | 86.7% | 100.0% | 66.23 | $0.051 | 2026-04-11 17:26:55 |

### gate_normal_30_30_v24j_gpt-oss-120b.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GPT-OSS-120B | v24j | 60 | 95.0% | 95.2% | 100.0% | 90.0% | 100.0% | 5.97 | $0.167 | 2026-04-11 16:26:30 |

### gate_normal_50_50_v24j_gpt-oss-120b.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GPT-OSS-120B | v24j | 100 | 94.0% | 94.3% | 100.0% | 88.0% | 100.0% | 5.50 | $0.282 | 2026-04-11 11:58:25 |
| GPT-OSS-120B | v24j | 100 | 93.0% | 93.5% | 100.0% | 86.0% | 100.0% | 5.13 | $0.282 | 2026-04-11 12:13:43 |
| GPT-OSS-120B | v24j | 100 | 92.0% | 92.5% | 98.0% | 86.0% | 99.0% | 4.57 | $0.278 | 2026-04-11 11:40:07 |

### gate_normal_50_50_v24j_llama-3-3-70b-instruct.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Llama 3.3 70B | v24j | 1 | 100.0% | 100.0% | 100.0% | 0.0% | 100.0% | 18.20 | $0.001 | 2026-04-11 12:04:55 |
| Llama 3.3 70B | v24j | 100 | 93.0% | 93.3% | 98.0% | 88.0% | 100.0% | 15.95 | $0.136 | 2026-04-11 12:40:23 |
| Llama 3.3 70B | v24j | 100 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.00 | $0.072 | 2026-04-11 11:40:40 |

### hard2_balanced20_true10_false10_rotation0017_20260415_021226_v26f_gpt-oss-120b.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GPT-OSS-120B | v26f | 20 | 40.0% | 50.0% | 60.0% | 20.0% | 95.0% | 73.03 | $0.104 | 2026-04-14 20:37:00 |

### hard2_balanced30_true15_false15_rotation0013_20260414_010332_v26f_gpt-oss-120b.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GPT-OSS-120B | v26f | 30 | 23.3% | 37.8% | 46.7% | 0.0% | 76.7% | 46.19 | $0.120 | 2026-04-14 21:42:06 |

### hard2_balanced50_true10_false40_rotation0012_20260413_161807_v26b_gpt-oss-120b.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GPT-OSS-120B | v26b | 50 | 20.0% | 33.3% | 100.0% | 0.0% | 100.0% | 31.09 | $0.171 | 2026-04-13 12:35:58 |

### hard2_false30_distill_20260412_v26a_gpt-oss-120b.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GPT-OSS-120B | v26a | 30 | 6.7% | 0.0% | 0.0% | 6.7% | 100.0% | 17.36 | $0.104 | 2026-04-11 21:31:59 |

### hard2_v26a_gpt-oss-120b.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GPT-OSS-120B | v26a | 20 | 40.0% | 57.1% | 100.0% | 0.0% | 100.0% | 12.49 | $0.067 | 2026-04-12 21:57:38 |

### hard2_v26b_gpt-oss-120b.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GPT-OSS-120B | v26b | 20 | 40.0% | 57.1% | 100.0% | 0.0% | 100.0% | 6.96 | $0.066 | 2026-04-12 22:33:54 |

### hard3_balanced20_true10_false10_rotation0001_20260403_163406.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Llama 3.3 70B | v23 | 20 | 50.0% | 66.7% | 100.0% | 0.0% | 100.0% | 16.13 | $0.015 | 2026-04-03 11:04:25 |

### hard3_balanced20_true10_false10_rotation0010_20260413_032310_v26a_gpt-oss-120b.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GPT-OSS-120B | v26a | 20 | 65.0% | 74.1% | 100.0% | 30.0% | 100.0% | 16.85 | $0.072 | 2026-04-12 21:53:20 |

### hard3_balanced20_true10_false10_rotation0011_20260413_042258_v26b_gpt-oss-120b.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GPT-OSS-120B | v26b | 20 | 75.0% | 80.0% | 100.0% | 50.0% | 100.0% | 14.37 | $0.078 | 2026-04-12 22:31:13 |

### hard3_balanced20_true10_false10_rotation0017_20260415_021226_v26f_gpt-oss-120b.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GPT-OSS-120B | v26f | 20 | 70.0% | 75.0% | 90.0% | 50.0% | 90.0% | 54.66 | $0.095 | 2026-04-14 21:15:54 |

### hard3_balanced30_true0_false30_rotation0007_20260412_031528_v26a_gpt-oss-120b.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GPT-OSS-120B | v26a | 30 | 36.7% | 0.0% | 0.0% | 36.7% | 100.0% | 12.13 | $0.113 | 2026-04-11 21:38:20 |

### hard3_balanced30_true15_false15_rotation0008_20260412_034307_v26a_gpt-oss-120b.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GPT-OSS-120B | v26a | 30 | 70.0% | 76.9% | 100.0% | 40.0% | 100.0% | 8.98 | $0.111 | 2026-04-11 21:55:45 |

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

### hard3_balanced40_true20_false20_rotation0002_20260403_185904_v24j_gpt-oss-120b.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GPT-OSS-120B | v24j | 40 | 62.5% | 72.7% | 100.0% | 25.0% | 100.0% | 12.70 | $0.137 | 2026-04-11 19:04:15 |

### hard3_balanced40_true20_false20_rotation0002_20260403_185904_v26a_gpt-oss-120b.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GPT-OSS-120B | v26a | 40 | 70.0% | 76.9% | 100.0% | 40.0% | 100.0% | 11.77 | $0.154 | 2026-04-11 19:18:18 |
| GPT-OSS-120B | v26a | 40 | 67.5% | 75.5% | 100.0% | 35.0% | 100.0% | 15.17 | $0.154 | 2026-04-11 18:55:17 |

### hard3_balanced40_true20_false20_rotation0014_20260415_014503_v26f_gpt-oss-120b.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GPT-OSS-120B | v26f | 40 | 65.0% | 69.6% | 80.0% | 50.0% | 90.0% | 71.44 | $0.195 | 2026-04-14 21:30:27 |

### hard3_balanced50_true10_false40_rotation0012_20260413_161807_v26b_gpt-oss-120b.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GPT-OSS-120B | v26b | 50 | 50.0% | 44.4% | 100.0% | 37.5% | 100.0% | 31.52 | $0.194 | 2026-04-13 12:05:31 |

### hard3_balanced50_true10_false40_rotation0012_20260413_161807_v26c_gpt-oss-120b.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GPT-OSS-120B | v26c | 50 | 46.0% | 37.2% | 80.0% | 37.5% | 98.0% | 52.73 | $0.246 | 2026-04-13 14:54:05 |

### hard3_balanced50_true10_false40_rotation0012_20260413_161807_v26d_gpt-oss-120b.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GPT-OSS-120B | v26d | 50 | 68.0% | 55.6% | 100.0% | 60.0% | 100.0% | 41.89 | $0.270 | 2026-04-13 19:01:23 |

### hard3_balanced60_true30_false30_rotation0006_20260411_222025_v23c_gpt-oss-120b.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GPT-OSS-120B | v23c | 60 | 50.0% | 66.7% | 100.0% | 0.0% | 100.0% | 7.17 | $0.149 | 2026-04-11 16:33:41 |

### hard3_balanced60_true30_false30_rotation0006_20260411_222025_v24j_gpt-oss-120b.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GPT-OSS-120B | v24j | 60 | 58.3% | 70.6% | 100.0% | 16.7% | 100.0% | 7.58 | $0.196 | 2026-04-11 16:41:21 |

### hard_balanced20_true10_false10_rotation0005_20260411_203024_v23c_gemma-4-31b-it.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Gemma 4 31B IT | v23c | 20 | 55.0% | 69.0% | 100.0% | 10.0% | 100.0% | 53.35 | $0.012 | 2026-04-11 14:58:53 |

### hard_balanced20_true10_false10_rotation0005_20260411_203024_v23c_gpt-oss-120b.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GPT-OSS-120B | v23c | 20 | 55.0% | 69.0% | 100.0% | 10.0% | 100.0% | 23.40 | $0.050 | 2026-04-11 14:44:08 |

### hard_balanced20_true10_false10_rotation0005_20260411_203024_v24j_gemma-4-31b-it.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Gemma 4 31B IT | v24j | 20 | 55.0% | 69.0% | 100.0% | 10.0% | 100.0% | 59.79 | $0.018 | 2026-04-11 15:33:31 |

### hard_balanced20_true10_false10_rotation0005_20260411_203024_v24j_gpt-oss-120b.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GPT-OSS-120B | v24j | 20 | 55.0% | 69.0% | 100.0% | 10.0% | 100.0% | 18.69 | $0.066 | 2026-04-11 14:53:57 |

### hard_balanced40_true20_false20_rotation0001_20260403_163406.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Llama 3.3 70B | v23 | 40 | 55.0% | 69.0% | 100.0% | 10.0% | 100.0% | 13.88 | $0.030 | 2026-04-03 10:58:51 |

### hard_v24j_llama-3-3-70b-instruct.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Llama 3.3 70B | v24j | 200 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.00 | $0.144 | 2026-04-11 11:25:13 |

### magma_eval_test_10.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Llama 3.3 70B | magma_eval_test | 8 | 87.5% | 85.7% | 100.0% | 80.0% | 100.0% | 15.85 | $0.006 | 2026-04-05 18:23:13 |

### mixed_hard23_balanced60_true30_false30_rotation0013_20260414_010332_v26d_gpt-oss-120b.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GPT-OSS-120B | v26d | 60 | 65.0% | 71.2% | 86.7% | 43.3% | 98.3% | 49.25 | $0.324 | 2026-04-13 19:53:14 |

### mixed_hard23_balanced60_true30_false30_rotation0013_20260414_010332_v26e_gpt-oss-120b.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GPT-OSS-120B | v26e | 60 | 56.7% | 69.8% | 100.0% | 13.3% | 100.0% | 37.65 | $0.263 | 2026-04-13 21:44:59 |

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

### normal_balanced20_true10_false10_rotation0005_20260411_203024_v23c_gemma-4-31b-it.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Gemma 4 31B IT | v23c | 20 | 85.0% | 87.0% | 100.0% | 70.0% | 100.0% | 30.57 | $0.012 | 2026-04-11 14:41:06 |

### normal_balanced20_true10_false10_rotation0005_20260411_203024_v23c_gpt-oss-120b.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GPT-OSS-120B | v23c | 20 | 85.0% | 87.0% | 100.0% | 70.0% | 100.0% | 15.63 | $0.048 | 2026-04-11 14:36:19 |

### normal_balanced20_true10_false10_rotation0005_20260411_203024_v24j_gemma-4-31b-it.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Gemma 4 31B IT | v24j | 20 | 85.0% | 87.0% | 100.0% | 70.0% | 100.0% | 44.08 | $0.017 | 2026-04-11 15:13:35 |

### normal_balanced20_true10_false10_rotation0005_20260411_203024_v24j_gpt-oss-120b.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GPT-OSS-120B | v24j | 20 | 85.0% | 87.0% | 100.0% | 70.0% | 100.0% | 10.64 | $0.058 | 2026-04-11 14:47:43 |

### normal_balanced20_true10_false10_rotation0010_20260413_032310_v26a_gpt-oss-120b.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GPT-OSS-120B | v26a | 20 | 95.0% | 95.2% | 100.0% | 90.0% | 100.0% | 10.06 | $0.060 | 2026-04-12 21:31:35 |

### normal_balanced20_true10_false10_rotation0011_20260413_042258_v26b_gpt-oss-120b.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GPT-OSS-120B | v26b | 20 | 95.0% | 95.2% | 100.0% | 90.0% | 100.0% | 8.65 | $0.059 | 2026-04-12 22:26:09 |

### normal_balanced20_true10_false10_seed0.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Llama 3.3 70B | v23b | 20 | 90.0% | 90.9% | 100.0% | 80.0% | 100.0% | 17.37 | $0.018 | 2026-04-03 17:20:01 |
| Llama 3.3 70B | v23c | 20 | 90.0% | 90.9% | 100.0% | 80.0% | 100.0% | 15.16 | $0.019 | 2026-04-03 17:49:02 |
| Llama 3.3 70B | v24a | 20 | 85.0% | 85.7% | 90.0% | 80.0% | 100.0% | 16.01 | $0.025 | 2026-04-05 16:36:58 |

### normal_balanced20_true10_false10_seed0_v24j_gpt-oss-120b.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GPT-OSS-120B | v24j | 20 | 90.0% | 90.9% | 100.0% | 80.0% | 100.0% | 13.87 | $0.055 | 2026-04-11 18:34:04 |

### normal_balanced20_true10_false10_seed0_v24j_llama-3-3-70b-instruct.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Llama 3.3 70B | v24j | 20 | 80.0% | 80.0% | 80.0% | 80.0% | 100.0% | 234.38 | $0.027 | 2026-04-11 19:44:20 |

### normal_balanced20_true10_false10_seed0_v26a_gemma-4-31b-it.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Gemma 4 31B IT | v26a | 20 | 90.0% | 90.9% | 100.0% | 80.0% | 100.0% | 76.26 | $0.018 | 2026-04-11 19:36:28 |
| Gemma 4 31B IT | v26a | 1 | 100.0% | 0.0% | 0.0% | 100.0% | 100.0% | 49.01 | $0.001 | 2026-04-11 20:59:41 |

### normal_balanced20_true10_false10_seed0_v26a_gpt-oss-120b.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GPT-OSS-120B | v26a | 20 | 90.0% | 90.9% | 100.0% | 80.0% | 100.0% | 12.70 | $0.060 | 2026-04-11 18:44:37 |
| GPT-OSS-120B | v26a | 20 | 90.0% | 90.9% | 100.0% | 80.0% | 100.0% | 4.39 | $0.061 | 2026-04-11 19:31:09 |

### normal_balanced20_true10_false10_seed0_v26a_llama-3-3-70b-instruct.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Llama 3.3 70B | v26a | 1 | 100.0% | 0.0% | 0.0% | 100.0% | 100.0% | 199.41 | $0.001 | 2026-04-11 21:03:07 |

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

### normal_balanced30_true0_false30_rotation0007_20260412_031528_v26a_gpt-oss-120b.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GPT-OSS-120B | v26a | 30 | 83.3% | 0.0% | 0.0% | 83.3% | 100.0% | 7.74 | $0.088 | 2026-04-11 21:19:59 |

### normal_balanced30_true15_false15_rotation0008_20260412_034307_v26a_gpt-oss-120b.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GPT-OSS-120B | v26a | 30 | 90.0% | 90.9% | 100.0% | 80.0% | 100.0% | 9.10 | $0.091 | 2026-04-11 21:47:55 |

### normal_balanced30_true15_false15_rotation0009_20260412_040515_v26a_gpt-oss-120b.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GPT-OSS-120B | v26a | 30 | 80.0% | 83.3% | 100.0% | 60.0% | 100.0% | 11.91 | $0.090 | 2026-04-11 22:29:42 |
| GPT-OSS-120B | v26a | 30 | 80.0% | 81.2% | 86.7% | 73.3% | 100.0% | 11.08 | $0.114 | 2026-04-11 22:11:06 |

### normal_balanced40_true20_false20_rotation0014_20260415_014503_v26f_gpt-oss-120b.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GPT-OSS-120B | v26f | 40 | 80.0% | 81.0% | 85.0% | 75.0% | 100.0% | 41.62 | $0.175 | 2026-04-14 20:12:48 |

### normal_balanced40_true20_false20_rotation0018_20260415_041933_v27a_gpt-oss-120b.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GPT-OSS-120B | v27a | 40 | 67.5% | 58.1% | 45.0% | 90.0% | 100.0% | 30.25 | $0.151 | 2026-04-14 22:39:43 |

### normal_balanced50_true10_false40_rotation0012_20260413_161807_v26b_gpt-oss-120b.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GPT-OSS-120B | v26b | 50 | 84.0% | 71.4% | 100.0% | 80.0% | 100.0% | 23.70 | $0.149 | 2026-04-13 10:53:55 |
| GPT-OSS-120B | v26b | 3 | 100.0% | 0.0% | 0.0% | 100.0% | 100.0% | 12.58 | $0.008 | 2026-04-13 10:23:39 |

### normal_balanced50_true10_false40_rotation0012_20260413_161807_v26b_llama-3-3-70b-instruct.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Llama 3.3 70B | v26b | 5 | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 14.92 | $0.007 | 2026-04-13 10:21:58 |

### normal_balanced50_true10_false40_rotation0012_20260413_161807_v26c_gpt-oss-120b.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GPT-OSS-120B | v26c | 50 | 92.0% | 83.3% | 100.0% | 90.0% | 100.0% | 29.40 | $0.166 | 2026-04-13 13:38:09 |
| GPT-OSS-120B | v26c | 50 | 86.0% | 72.0% | 90.0% | 85.0% | 98.0% | 22.41 | $0.126 | 2026-04-13 13:00:42 |

### normal_balanced50_true10_false40_rotation0012_20260413_161807_v26d_gpt-oss-120b.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GPT-OSS-120B | v26d | 50 | 92.0% | 80.0% | 80.0% | 95.0% | 96.0% | 24.01 | $0.188 | 2026-04-13 17:59:49 |

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

### normal_balanced60_true30_false30_rotation0013_20260414_010332_v26d_gpt-oss-120b.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GPT-OSS-120B | v26d | 60 | 76.7% | 73.1% | 63.3% | 90.0% | 93.3% | 38.09 | $0.247 | 2026-04-13 20:21:52 |

### normal_balanced60_true30_false30_rotation0013_20260414_010332_v26e_gpt-oss-120b.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GPT-OSS-120B | v26e | 60 | 90.0% | 90.9% | 100.0% | 80.0% | 100.0% | 17.18 | $0.216 | 2026-04-13 21:06:49 |

### normal_v23c_llama-3-3-70b-instruct.jsonl

| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Llama 3.3 70B | v23c | 1 | 100.0% | 100.0% | 100.0% | 0.0% | 100.0% | 252.54 | $0.001 | 2026-04-11 15:54:19 |
