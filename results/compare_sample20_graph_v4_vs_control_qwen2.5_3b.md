# Sample20 Graph V4 vs Control

Sample manifest: results\control_balanced_sample20_seed29_manifest.json

Counts: total=20, true=10, false=10, normal=16, hard=4

| Run | Model | Cheatsheet | Total | Acc | F1 | TRUE acc | FALSE acc | Avg s |
|---|---|---|---:|---:|---:|---:|---:|---:|
| sample20_graph_v4 | qwen2.5:3b | cheatsheets/graph_v4.txt | 20 | 0.5000 | 0.0000 | 0.0000 | 1.0000 | 4.44 |
| same20_no_cheatsheet | qwen2.5:3b | (none) | 20 | 0.3500 | 0.0000 | 0.0000 | 0.7000 | 9.54 |
| full120_no_cheatsheet | qwen2.5:3b | (none) | 120 | 0.4917 | 0.1159 | 0.0667 | 0.9167 | 9.31 |

## Delta vs same20 no-cheatsheet

- accuracy: +0.1500
- f1: +0.0000
- true_accuracy: +0.0000
- false_accuracy: +0.3000
- avg_time_s: -5.10

## Delta vs full120 no-cheatsheet

- accuracy: +0.0083
- f1: -0.1159
- true_accuracy: -0.0667
- false_accuracy: +0.0833
- avg_time_s: -4.87
