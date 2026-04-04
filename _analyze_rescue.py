"""Analyze all rotation0002 failures to find which structural properties could rescue them."""
import json
import re
from pathlib import Path
from collections import Counter
from v21_verify_structural_rules import (
    rule_LP, rule_RP, rule_C0, rule_AND, rule_XOR, rule_XNOR, rule_Z3A,
    leftmost_leaf, rightmost_leaf, has_star, var_counts, var_set, count_stars
)

results_dir = Path("results")

# Deduplicate failures by equation pair
seen = set()
all_fails = []
for f in sorted(results_dir.glob("sim_*.json")):
    if "rotation0002" not in f.name:
        continue
    data = json.loads(f.read_text(encoding="utf-8"))
    for r in data["results"]:
        if r["correct"]:
            continue
        key = (r["equation1"], r["equation2"])
        if key in seen:
            continue
        seen.add(key)
        all_fails.append(r)

print(f"Unique failing pairs: {len(all_fails)}")

# For each failure, compute ALL structural properties
def analyze_pair(eq1, eq2):
    l1, r1 = eq1.split(" = ", 1)
    l2, r2 = eq2.split(" = ", 1)
    
    tests = {}
    for name, fn in [("LP", rule_LP), ("RP", rule_RP), ("C0", rule_C0), 
                       ("VARS", rule_AND), ("XOR", rule_XOR), ("XNOR", rule_XNOR), ("Z3A", rule_Z3A)]:
        e1_h = fn(l1, r1)
        e2_h = fn(l2, r2)
        tests[name] = {"e1": e1_h, "e2": e2_h, "separates": e1_h and not e2_h}
    
    # Additional properties
    props = {}
    
    # Total var count per side
    props["e1_lhs_vars"] = sum(var_counts(l1).values())
    props["e1_rhs_vars"] = sum(var_counts(r1).values())
    props["e2_lhs_vars"] = sum(var_counts(l2).values())
    props["e2_rhs_vars"] = sum(var_counts(r2).values())
    
    # Star counts
    props["e1_lhs_stars"] = count_stars(l1)
    props["e1_rhs_stars"] = count_stars(r1)
    props["e2_lhs_stars"] = count_stars(l2)
    props["e2_rhs_stars"] = count_stars(r2)
    
    # Variable count symmetry: is total_vars(LHS) == total_vars(RHS)?
    props["e1_vcnt_symmetric"] = props["e1_lhs_vars"] == props["e1_rhs_vars"]
    props["e2_vcnt_symmetric"] = props["e2_lhs_vars"] == props["e2_rhs_vars"]
    
    # Star count symmetry (is this an idempotent form?)
    props["e1_scnt_symmetric"] = props["e1_lhs_stars"] == props["e1_rhs_stars"]
    props["e2_scnt_symmetric"] = props["e2_lhs_stars"] == props["e2_rhs_stars"]
    
    # New variable check: does E2 introduce variables not in E1?
    e1_vars = var_set(l1) | var_set(r1)
    e2_vars = var_set(l2) | var_set(r2)
    props["e2_new_vars"] = e2_vars - e1_vars
    props["e1_new_vars"] = e1_vars - e2_vars
    
    # Depth (count of nested *)
    def depth(expr):
        max_d, cur_d = 0, 0
        for c in expr:
            if c == '(':
                cur_d += 1
                max_d = max(max_d, cur_d)
            elif c == ')':
                cur_d -= 1
        return max_d
    
    props["e1_lhs_depth"] = depth(l1)
    props["e1_rhs_depth"] = depth(r1)
    props["e2_lhs_depth"] = depth(l2)
    props["e2_rhs_depth"] = depth(r2)
    
    # Is one side a bare variable?
    props["e1_lhs_bare"] = not has_star(l1)
    props["e1_rhs_bare"] = not has_star(r1)
    props["e2_lhs_bare"] = not has_star(l2)
    props["e2_rhs_bare"] = not has_star(r2)
    
    # Potential VCNT separation: E1 has same total var count on both sides, E2 doesn't
    props["vcnt_separates"] = props["e1_vcnt_symmetric"] and not props["e2_vcnt_symmetric"]
    
    # Potential SCNT separation: E1 has same star count on both sides, E2 doesn't 
    props["scnt_separates"] = props["e1_scnt_symmetric"] and not props["e2_scnt_symmetric"]
    
    return tests, props

# Analyze all failures
vcnt_catches = []
scnt_catches = []
xor_catches = []
any_structural = []

print("\n=== DETAILED FAILURE ANALYSIS ===\n")
for r in all_fails:
    tests, props = analyze_pair(r["equation1"], r["equation2"])
    seps = [n for n, t in tests.items() if t["separates"]]
    
    source = "normal" if "normal" in r["id"] else "hard3"
    print(f"[{r['id']}] gt={r['ground_truth']} pred={r['predicted']} source={source}")
    print(f"  E1: {r['equation1']}")
    print(f"  E2: {r['equation2']}")
    print(f"  Standard seps: {seps}")
    print(f"  VCNT separates: {props['vcnt_separates']} (E1 sym={props['e1_vcnt_symmetric']} E2 sym={props['e2_vcnt_symmetric']})")
    print(f"  SCNT separates: {props['scnt_separates']} (E1 sym={props['e1_scnt_symmetric']} E2 sym={props['e2_scnt_symmetric']})")
    print(f"  E1 vars: L={props['e1_lhs_vars']} R={props['e1_rhs_vars']} | E2 vars: L={props['e2_lhs_vars']} R={props['e2_rhs_vars']}")
    print(f"  E1 stars: L={props['e1_lhs_stars']} R={props['e1_rhs_stars']} | E2 stars: L={props['e2_lhs_stars']} R={props['e2_rhs_stars']}")
    print(f"  E2 new vars in E2 not E1: {props['e2_new_vars']}")
    print()
    
    if seps:
        any_structural.append(r["id"])
    if props["vcnt_separates"]:
        vcnt_catches.append(r["id"])
    if props["scnt_separates"]:
        scnt_catches.append(r["id"])
    if "XOR" in seps:
        xor_catches.append(r["id"])

print("=== SUMMARY ===")
print(f"Total unique failures: {len(all_fails)}")
print(f"Caught by existing 7 structural tests: {len(any_structural)} — {any_structural}")
print(f"Caught by VCNT (var count symmetry): {len(vcnt_catches)} — {vcnt_catches}")
print(f"Caught by SCNT (star count symmetry): {len(scnt_catches)} — {scnt_catches}")
print(f"Caught by XOR specifically: {len(xor_catches)} — {xor_catches}")
print(f"Uncatchable by any text test: {len(all_fails) - len(set(any_structural + vcnt_catches + scnt_catches))}")
