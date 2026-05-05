"""Verify spot-check soundness: at specific assignments under T3R/T3L,
does the spot check produce any false positives on TRUE pairs?"""
import json, itertools

with open("data/benchmark/hard3_balanced40_true20_false20_rotation0002_20260403_185904.jsonl") as f:
    lines = [json.loads(l) for l in f]

false_pairs = [l for l in lines if l["answer"] is False]
true_pairs = [l for l in lines if l["answer"] is True]

# Also check normal benchmark
with open("data/benchmark/normal_balanced60_true30_false30_rotation0002_20260403_185904.jsonl") as f:
    normal_lines = [json.loads(l) for l in f]
normal_true = [l for l in normal_lines if l["answer"] is True]
normal_false = [l for l in normal_lines if l["answer"] is False]


def parse_expr(s):
    s = s.strip()
    while s.startswith('(') and s.endswith(')'):
        d = 0; matched = True
        for i, c in enumerate(s):
            if c == '(': d += 1
            elif c == ')': d -= 1
            if d == 0 and i < len(s) - 1: matched = False; break
        if matched: s = s[1:-1].strip()
        else: break
    depth = 0
    for i, c in enumerate(s):
        if c == '(': depth += 1
        elif c == ')': depth -= 1
        elif c == '*' and depth == 0:
            return ('op', parse_expr(s[:i].strip()), parse_expr(s[i+1:].strip()))
    return ('var', s.strip())


def eval_tree(tree, assignment, op_table, n):
    if tree[0] == 'var': return assignment[tree[1]]
    l = eval_tree(tree[1], assignment, op_table, n)
    r = eval_tree(tree[2], assignment, op_table, n)
    return op_table[l * n + r]


def get_variables(tree):
    if tree[0] == 'var': return {tree[1]}
    return get_variables(tree[1]) | get_variables(tree[2])


def get_ordered_vars(eq_str):
    """Get variables in order of first appearance."""
    import re
    seen = []
    for m in re.finditer(r'[a-z]', eq_str):
        v = m.group()
        if v not in seen:
            seen.append(v)
    return seen


# T3R: a*b = (b+1) mod 3
T3R = [1,2,0, 1,2,0, 1,2,0]
# T3L: a*b = (a+1) mod 3
T3L = [1,1,1, 2,2,2, 0,0,0]

def spot_check(e1_str, e2_str, op_table, n=3):
    """Single-assignment spot check. Returns 'SEP' if E1 passes but E2 fails."""
    vars_ordered = get_ordered_vars(e1_str + " " + e2_str)
    # Assign 0,1,2,0,1,... to variables in order of appearance
    assignment = {v: i % n for i, v in enumerate(vars_ordered)}
    
    e1l, e1r = e1_str.split("=", 1)
    e2l, e2r = e2_str.split("=", 1)
    
    t1l, t1r = parse_expr(e1l), parse_expr(e1r)
    t2l, t2r = parse_expr(e2l), parse_expr(e2r)
    
    e1_lhs = eval_tree(t1l, assignment, op_table, n)
    e1_rhs = eval_tree(t1r, assignment, op_table, n)
    e2_lhs = eval_tree(t2l, assignment, op_table, n)
    e2_rhs = eval_tree(t2r, assignment, op_table, n)
    
    e1_pass = (e1_lhs == e1_rhs)
    e2_pass = (e2_lhs == e2_rhs)
    
    return e1_pass and not e2_pass, (e1_lhs, e1_rhs, e2_lhs, e2_rhs, assignment)


def multi_spot_check(e1_str, e2_str, op_table, n=3):
    """Try multiple assignments. Returns SEP if any separates."""
    vars_ordered = get_ordered_vars(e1_str + " " + e2_str)
    k = len(vars_ordered)
    
    e1l, e1r = e1_str.split("=", 1)
    e2l, e2r = e2_str.split("=", 1)
    t1l, t1r = parse_expr(e1l), parse_expr(e1r)
    t2l, t2r = parse_expr(e2l), parse_expr(e2r)
    
    # Try a few specific assignments
    test_assignments = [
        {v: i % n for i, v in enumerate(vars_ordered)},  # 0,1,2,0,...
        {v: (i+1) % n for i, v in enumerate(vars_ordered)},  # 1,2,0,1,...
        {v: (i+2) % n for i, v in enumerate(vars_ordered)},  # 2,0,1,2,...
        {v: 0 for v in vars_ordered},  # all zeros
        {v: 1 for v in vars_ordered},  # all ones
    ]
    
    for assignment in test_assignments:
        e1_lhs = eval_tree(t1l, assignment, op_table, n)
        e1_rhs = eval_tree(t1r, assignment, op_table, n)
        e2_lhs = eval_tree(t2l, assignment, op_table, n)
        e2_rhs = eval_tree(t2r, assignment, op_table, n)
        
        if e1_lhs == e1_rhs and e2_lhs != e2_rhs:
            return True, assignment
    
    return False, None


print("=" * 80)
print("SPOT CHECK ANALYSIS: T3R (a*b = (b+1) mod 3)")
print("=" * 80)

# Hard3 FALSE — catches
print("\n--- Hard3 FALSE (want: catches) ---")
h3f_catches_single = 0
h3f_catches_multi = 0
for p in false_pairs:
    sep1, info1 = spot_check(p["equation1"], p["equation2"], T3R)
    sep_m, info_m = multi_spot_check(p["equation1"], p["equation2"], T3R)
    tag = "CATCH" if sep1 else "miss"
    tag_m = "CATCH" if sep_m else "miss"
    if sep1 or sep_m:
        vals = info1 if sep1 else None
        print(f"  {p['id']}: single={tag}, multi={tag_m}")
        h3f_catches_single += sep1
        h3f_catches_multi += sep_m

print(f"\n  Single-assignment catches: {h3f_catches_single}/20")
print(f"  Multi-assignment catches: {h3f_catches_multi}/20")

# Hard3 TRUE — false positives
print("\n--- Hard3 TRUE (want: 0 FP) ---")
h3t_fp_single = 0
h3t_fp_multi = 0
for p in true_pairs:
    sep1, _ = spot_check(p["equation1"], p["equation2"], T3R)
    sep_m, _ = multi_spot_check(p["equation1"], p["equation2"], T3R)
    if sep1:
        print(f"  FP! {p['id']} (single)")
        h3t_fp_single += 1
    if sep_m:
        print(f"  FP! {p['id']} (multi)")
        h3t_fp_multi += 1

print(f"\n  Single-assignment FP: {h3t_fp_single}/20")
print(f"  Multi-assignment FP: {h3t_fp_multi}/20")

# Normal FALSE — catches
print("\n--- Normal FALSE (bonus catches) ---")
nf_catches = 0
for p in normal_false:
    sep_m, _ = multi_spot_check(p["equation1"], p["equation2"], T3R)
    if sep_m:
        nf_catches += 1
        print(f"  Catch: {p['id']}")
print(f"\n  Normal FALSE multi catches: {nf_catches}/30")

# Normal TRUE — false positives
print("\n--- Normal TRUE (want: 0 FP) ---")
nt_fp = 0
for p in normal_true:
    sep_m, _ = multi_spot_check(p["equation1"], p["equation2"], T3R)
    if sep_m:
        print(f"  FP! {p['id']}")
        nt_fp += 1
print(f"\n  Normal TRUE multi FP: {nt_fp}/30")

print("\n" + "=" * 80)
print("SPOT CHECK ANALYSIS: T3L (a*b = (a+1) mod 3)")
print("=" * 80)

# Hard3 FALSE
print("\n--- Hard3 FALSE ---")
t3l_catches = 0
for p in false_pairs:
    sep_m, info = multi_spot_check(p["equation1"], p["equation2"], T3L)
    if sep_m:
        t3l_catches += 1
        print(f"  Catch: {p['id']} at {info}")
print(f"\n  T3L multi catches: {t3l_catches}/20")

# Hard3 TRUE
print("\n--- Hard3 TRUE ---")
t3l_fp = 0
for p in true_pairs:
    sep_m, _ = multi_spot_check(p["equation1"], p["equation2"], T3L)
    if sep_m:
        print(f"  FP! {p['id']}")
        t3l_fp += 1
print(f"\n  T3L multi FP: {t3l_fp}/20")

# Normal TRUE
print("\n--- Normal TRUE ---")
t3l_normal_fp = 0
for p in normal_true:
    sep_m, _ = multi_spot_check(p["equation1"], p["equation2"], T3L)
    if sep_m:
        print(f"  FP! {p['id']}")
        t3l_normal_fp += 1
print(f"\n  T3L Normal TRUE FP: {t3l_normal_fp}/30")

# Combined T3R+T3L 
print("\n" + "=" * 80)
print("COMBINED T3R + T3L (multi-assignment)")
print("=" * 80)
combined_catches = 0
caught_ids = []
for p in false_pairs:
    sep_r, _ = multi_spot_check(p["equation1"], p["equation2"], T3R)
    sep_l, _ = multi_spot_check(p["equation1"], p["equation2"], T3L)
    if sep_r or sep_l:
        combined_catches += 1
        caught_ids.append(p["id"])
        which = []
        if sep_r: which.append("T3R")
        if sep_l: which.append("T3L")
        print(f"  {p['id']}: {'+'.join(which)}")

print(f"\nCombined hard3 FALSE catches: {combined_catches}/20")
print(f"Hard3 total with default TRUE: {20 + combined_catches}/40 = {100*(20+combined_catches)/40:.1f}%")
