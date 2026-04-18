#!/usr/bin/env python3
"""Compare v26b/c/d/e eval scores."""
import json

files = [
    ("v26b normal50", "results/sim_normal_balanced50_true10_false40_rotation0012_20260413_161807_v26b_gpt-oss-120b_20260413_105355.json"),
    ("v26c normal50", "results/sim_normal_balanced50_true10_false40_rotation0012_20260413_161807_v26c_gpt-oss-120b_20260413_133809.json"),
    ("v26d normal50", "results/sim_normal_balanced50_true10_false40_rotation0012_20260413_161807_v26d_gpt-oss-120b_20260413_175949.json"),
    ("v26b hard3_50", "results/sim_hard3_balanced50_true10_false40_rotation0012_20260413_161807_v26b_gpt-oss-120b_20260413_120531.json"),
    ("v26c hard3_50", "results/sim_hard3_balanced50_true10_false40_rotation0012_20260413_161807_v26c_gpt-oss-120b_20260413_145405.json"),
    ("v26d hard3_50", "results/sim_hard3_balanced50_true10_false40_rotation0012_20260413_161807_v26d_gpt-oss-120b_20260413_190123.json"),
    ("v26b hard2_50", "results/sim_hard2_balanced50_true10_false40_rotation0012_20260413_161807_v26b_gpt-oss-120b_20260413_123558.json"),
    ("v26d normal60", "results/sim_normal_balanced60_true30_false30_rotation0013_20260414_010332_v26d_gpt-oss-120b_20260413_202152.json"),
    ("v26e normal60", "results/sim_normal_balanced60_true30_false30_rotation0013_20260414_010332_v26e_gpt-oss-120b_20260413_210649.json"),
    ("v26d mixed60", "results/sim_mixed_hard23_balanced60_true30_false30_rotation0013_20260414_010332_v26d_gpt-oss-120b_20260413_195314.json"),
    ("v26e mixed60", "results/sim_mixed_hard23_balanced60_true30_false30_rotation0013_20260414_010332_v26e_gpt-oss-120b_20260413_214459.json"),
]

for label, path in files:
    try:
        d = json.load(open(path, encoding="utf-8"))
        s = d["summary"]
        rows = d["results"]
        fp = sum(1 for r in rows if r.get("ground_truth") is False and r.get("predicted") is True)
        fn = sum(1 for r in rows if r.get("ground_truth") is True and r.get("predicted") is False)
        acc = s["accuracy"]
        pr = s["parse_rate"]
        print(f"{label:20s}: acc={acc:.1%} parse={pr:.1%} FP={fp} FN={fn}")
    except Exception as e:
        print(f"{label:20s}: ERROR {e}")
