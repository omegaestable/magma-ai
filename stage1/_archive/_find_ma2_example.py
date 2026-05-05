#!/usr/bin/env python3
"""Find a worked example for MA2 magma [[0,2,1],[0,1,2],[0,1,2]]."""
import json
from distill import check_equation, parse_equation_tree, eval_tree

MA2 = [[0,2,1],[0,1,2],[0,1,2]]
MA1 = [[2,1,2],[2,2,2],[2,2,2]]

def cycling_assign(eq1, eq2):
    seen = set(); ordered = []
    for ch in (eq1 + " " + eq2):
        if ch.isalpha() and ch not in seen:
            seen.add(ch); ordered.append(ch)
    return {v: i % 3 for i, v in enumerate(ordered)}

def eval_eq(eq, assignment, table):
    lhs, rhs = parse_equation_tree(eq)
    return eval_tree(lhs, assignment, table), eval_tree(rhs, assignment, table)

files = [
    "results/sim_normal_balanced50_true10_false40_rotation0012_20260413_161807_v26b_gpt-oss-120b_20260413_105355.json",
    "results/sim_hard3_balanced50_true10_false40_rotation0012_20260413_161807_v26b_gpt-oss-120b_20260413_120531.json",
    "results/sim_hard2_balanced50_true10_false40_rotation0012_20260413_161807_v26b_gpt-oss-120b_20260413_123558.json",
]

for fpath in files:
    d = json.load(open(fpath, encoding="utf-8"))
    for row in d["results"]:
        if row["ground_truth"] is False and row["predicted"] is True:
            eq1 = row["equation1"]
            eq2 = row["equation2"]
            # MA2 catches but MA1 doesn't
            if check_equation(eq1, MA2) and not check_equation(eq2, MA2):
                if not (check_equation(eq1, MA1) and not check_equation(eq2, MA1)):
                    assignment = cycling_assign(eq1, eq2)
                    l1, r1 = eval_eq(eq1, assignment, MA2)
                    l2, r2 = eval_eq(eq2, assignment, MA2)
                    if l1 == r1 and l2 != r2 and len(eq1) < 40 and len(eq2) < 40:
                        print(f"ID: {row['id']}")
                        print(f"  E1: {eq1}")
                        print(f"  E2: {eq2}")
                        print(f"  Assignment: {assignment}")
                        print(f"  E1: {l1} = {r1} ✓")
                        print(f"  E2: {l2} ≠ {r2} → SEP")
                        print()
