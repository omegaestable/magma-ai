"""Brute-force search: find 3-element magmas that separate hard2 FALSE problems.
Tests all 19,683 possible 3-element magma operations."""
import json, re
from itertools import product as iprod

data = [json.loads(l) for l in open('data/benchmark/hard2_balanced30_true15_false15_rotation0022_20260417_145804.jsonl')]
false_probs = [d for d in data if not d['answer']]
true_probs = [d for d in data if d['answer']]

def assign_vars(e1, e2):
    full = e1 + ' ' + e2
    seen = []
    for c in full:
        if c.isalpha() and c not in seen:
            seen.append(c)
    mapping = {}
    for i, v in enumerate(seen):
        mapping[v] = i % 3
    return mapping

def eval_magma(expr, tbl):
    s = expr.replace(' ', '')
    while '*' in s:
        m = re.search(r'\((\d)\*(\d)\)', s)
        if not m:
            m = re.search(r'(\d)\*(\d)', s)
        if not m:
            break
        a, b = int(m.group(1)), int(m.group(2))
        s = s[:m.start()] + str(tbl[a*3+b]) + s[m.end():]
    s = s.replace('(', '').replace(')', '')
    return int(s) if s.isdigit() else -1

def rewrite(expr, mapping):
    return ''.join(str(mapping[c]) if c.isalpha() else c for c in expr)

# Precompute equation data
problems = []
for d in false_probs:
    e1 = d['equation1']
    e2 = d['equation2']
    lhs1, rhs1 = e1.split(' = ', 1)
    lhs2, rhs2 = e2.split(' = ', 1)
    mapping = assign_vars(e1, e2)
    nvars = len(mapping)
    # Rewrite with default and all-zeros assignments
    zero_map = {v: 0 for v in mapping}
    problems.append({
        'id': d.get('id', '?'),
        'nvars': nvars,
        'lhs1_def': rewrite(lhs1, mapping), 'rhs1_def': rewrite(rhs1, mapping),
        'lhs2_def': rewrite(lhs2, mapping), 'rhs2_def': rewrite(rhs2, mapping),
        'lhs1_zero': rewrite(lhs1, zero_map), 'rhs1_zero': rewrite(rhs1, zero_map),
    })

# Also prepare TRUE problems for safety check
true_problems = []
for d in true_probs:
    e1 = d['equation1']
    e2 = d['equation2']
    lhs1, rhs1 = e1.split(' = ', 1)
    lhs2, rhs2 = e2.split(' = ', 1)
    mapping = assign_vars(e1, e2)
    zero_map = {v: 0 for v in mapping}
    true_problems.append({
        'id': d.get('id', '?'),
        'lhs1_def': rewrite(lhs1, mapping), 'rhs1_def': rewrite(rhs1, mapping),
        'lhs2_def': rewrite(lhs2, mapping), 'rhs2_def': rewrite(rhs2, mapping),
        'lhs1_zero': rewrite(lhs1, zero_map), 'rhs1_zero': rewrite(rhs1, zero_map),
    })

print("Searching all 19,683 3-element magmas...")
print("(A magma is a 3x3 table: tbl[a*3+b] gives a*b result)")

# For each unseparated problem, find all magmas that separate it
# tbl is a tuple of 9 values, each 0-2
unseparated = [p for p in problems if p['id'] != 'hard2_0090']  # 0090 already solved by T5B

# Track which magmas separate which problems
best_magmas = {}  # magma_tuple -> set of separated problem IDs

count = 0
for tbl in iprod(range(3), repeat=9):
    count += 1
    if count % 5000 == 0:
        print(f"  checked {count}/19683...", end='\r')
    
    separated = set()
    for p in unseparated:
        # Check E1 with default vars
        l1 = eval_magma(p['lhs1_def'], tbl)
        r1 = eval_magma(p['rhs1_def'], tbl)
        if l1 != r1:
            continue  # E1 doesn't hold → no separation
        
        # Check E1 with all-zeros
        l1z = eval_magma(p['lhs1_zero'], tbl)
        r1z = eval_magma(p['rhs1_zero'], tbl)
        if l1z != r1z:
            continue  # E1 doesn't hold on all-zeros → no separation
        
        # Check E2 with default vars
        l2 = eval_magma(p['lhs2_def'], tbl)
        r2 = eval_magma(p['rhs2_def'], tbl)
        if l2 != r2:
            separated.add(p['id'])
    
    if len(separated) >= 2:
        best_magmas[tbl] = separated

print(f"\nChecked all 19,683 magmas.")
print(f"Found {len(best_magmas)} magmas that separate 2+ problems")

# Find the best magma by coverage
if best_magmas:
    sorted_magmas = sorted(best_magmas.items(), key=lambda x: len(x[1]), reverse=True)
    print("\nTop 10 magmas by coverage:")
    for i, (tbl, seps) in enumerate(sorted_magmas[:10]):
        # Format as table
        rows = []
        for a in range(3):
            row = [tbl[a*3+b] for b in range(3)]
            rows.append(row)
        print(f"\n  #{i+1}: separates {len(seps)} problems: {sorted(seps)}")
        print(f"       a*b table: {rows[0]} / {rows[1]} / {rows[2]}")
        
        # Check safety: does this magma cause FNs on TRUE problems?
        fn_risk = []
        for tp in true_problems:
            l1 = eval_magma(tp['lhs1_def'], tbl)
            r1 = eval_magma(tp['rhs1_def'], tbl)
            if l1 != r1:
                continue
            l1z = eval_magma(tp['lhs1_zero'], tbl)
            r1z = eval_magma(tp['rhs1_zero'], tbl)
            if l1z != r1z:
                continue
            l2 = eval_magma(tp['lhs2_def'], tbl)
            r2 = eval_magma(tp['rhs2_def'], tbl)
            if l2 != r2:
                fn_risk.append(tp['id'])
        
        if fn_risk:
            print(f"       ⚠️  FN RISK on TRUE: {fn_risk}")
        else:
            print(f"       ✅ SAFE (no FN risk on any TRUE problem)")

# Also check single-separator magmas
single_seps = {}
for tbl in iprod(range(3), repeat=9):
    for p in unseparated:
        l1 = eval_magma(p['lhs1_def'], tbl)
        r1 = eval_magma(p['rhs1_def'], tbl)
        if l1 != r1:
            continue
        l1z = eval_magma(p['lhs1_zero'], tbl)
        r1z = eval_magma(p['rhs1_zero'], tbl)
        if l1z != r1z:
            continue
        l2 = eval_magma(p['lhs2_def'], tbl)
        r2 = eval_magma(p['rhs2_def'], tbl)
        if l2 != r2:
            if p['id'] not in single_seps:
                single_seps[p['id']] = 0
            single_seps[p['id']] += 1

print(f"\n=== Per-problem separator counts (3-element magmas) ===")
for p in unseparated:
    count = single_seps.get(p['id'], 0)
    print(f"  {p['id']:12s} ({p['nvars']} vars): {count:5d} separating magmas found")

total_separable = sum(1 for p in unseparated if single_seps.get(p['id'], 0) > 0)
print(f"\n{total_separable + 1}/{len(false_probs)} FALSE problems have a 3-element magma separator")
print(f"(+1 for hard2_0090 already covered by T5B)")
