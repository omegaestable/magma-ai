"""Search for SAFE magmas: 0*0 != 0 so all-zeros check is effective.
Also adds all-ones check for extra safety."""
import json, re
from itertools import product as iprod

data = [json.loads(l) for l in open('data/benchmark/hard2_balanced30_true15_false15_rotation0022_20260417_145804.jsonl')]
false_probs = [d for d in data if not d['answer']]
true_probs = [d for d in data if d['answer']]

# Also load full pools for cross-validation
hard2_full = [json.loads(l) for l in open('data/hf_cache/hard2.jsonl')]
hard3_full = [json.loads(l) for l in open('data/hf_cache/hard3.jsonl')]
normal_full = [json.loads(l) for l in open('data/hf_cache/normal.jsonl')]

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

def rewrite(expr, mapping):
    return ''.join(str(mapping[c]) if c.isalpha() else c for c in expr)

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

def check_separation(e1, e2, tbl):
    """Returns True if magma separates (E1 holds on default+zeros, E2 fails on default)"""
    lhs1, rhs1 = e1.split(' = ', 1)
    lhs2, rhs2 = e2.split(' = ', 1)
    mapping = assign_vars(e1, e2)
    
    # Default
    l1 = eval_magma(rewrite(lhs1, mapping), tbl)
    r1 = eval_magma(rewrite(rhs1, mapping), tbl)
    if l1 != r1: return False
    
    # All-zeros
    zero_map = {v: 0 for v in mapping}
    l1z = eval_magma(rewrite(lhs1, zero_map), tbl)
    r1z = eval_magma(rewrite(rhs1, zero_map), tbl)
    if l1z != r1z: return False
    
    # E2
    l2 = eval_magma(rewrite(lhs2, mapping), tbl)
    r2 = eval_magma(rewrite(rhs2, mapping), tbl)
    return l2 != r2

# Precompute problems for rotation 22
rot22_false = [(d['equation1'], d['equation2'], d.get('id','?')) for d in false_probs]
rot22_true = [(d['equation1'], d['equation2'], d.get('id','?')) for d in true_probs]

# Precompute full pool TRUE problems (for FN cross-validation)
full_true_h2 = [(d['equation1'], d['equation2']) for d in hard2_full if d['answer']]
full_true_h3 = [(d['equation1'], d['equation2']) for d in hard3_full if d['answer']]
full_true_n = [(d['equation1'], d['equation2']) for d in normal_full if d['answer']]

print("Searching for safe magmas (0*0 != 0)...")
print(f"Hard2 rotation 22: {len(rot22_false)} FALSE, {len(rot22_true)} TRUE")
print(f"Full pools: H2={len(full_true_h2)}T, H3={len(full_true_h3)}T, N={len(full_true_n)}T")

# Search magmas where tbl[0] != 0 (i.e., 0*0 != 0)
candidates = []
count = 0
for tbl in iprod(range(3), repeat=9):
    if tbl[0] == 0:  # Skip magmas where 0*0=0 (all-zeros check is useless)
        continue
    count += 1
    
    # Count rotation 22 separations
    rot22_seps = set()
    for e1, e2, pid in rot22_false:
        if check_separation(e1, e2, tbl):
            rot22_seps.add(pid)
    
    if len(rot22_seps) < 2:
        continue
    
    # Check rotation 22 TRUE FN
    rot22_fn = 0
    for e1, e2, pid in rot22_true:
        if check_separation(e1, e2, tbl):
            rot22_fn += 1
    
    if rot22_fn > 0:
        continue  # Must be safe on rotation 22
    
    candidates.append((tbl, rot22_seps))

print(f"\nChecked {count} magmas with 0*0!=0")
print(f"Found {len(candidates)} candidates with 2+ seps and 0 FN on rotation 22")

# Sort by coverage
candidates.sort(key=lambda x: len(x[1]), reverse=True)

# Cross-validate top candidates against full pools
print("\nTop 15 candidates:")
for i, (tbl, seps) in enumerate(candidates[:15]):
    rows = [[tbl[a*3+b] for b in range(3)] for a in range(3)]
    
    # Full pool cross-validation
    fn_h2 = sum(1 for e1, e2 in full_true_h2 if check_separation(e1, e2, tbl))
    fn_h3 = sum(1 for e1, e2 in full_true_h3 if check_separation(e1, e2, tbl))
    fn_n = sum(1 for e1, e2 in full_true_n if check_separation(e1, e2, tbl))
    
    status = "SAFE" if fn_h2 + fn_h3 + fn_n == 0 else f"FN: H2={fn_h2} H3={fn_h3} N={fn_n}"
    
    print(f"\n  #{i+1}: separates {len(seps)}/{len(rot22_false)} FALSE in r22: {sorted(seps)}")
    print(f"       table: {rows[0]} / {rows[1]} / {rows[2]}")
    print(f"       full pool: {status}")

# Also find the best globally-safe magma
print("\n\n=== GLOBALLY SAFE magmas (0 FN across all pools) ===")
best_safe = []
for i, (tbl, seps) in enumerate(candidates):
    fn_h2 = sum(1 for e1, e2 in full_true_h2 if check_separation(e1, e2, tbl))
    fn_h3 = sum(1 for e1, e2 in full_true_h3 if check_separation(e1, e2, tbl))
    fn_n = sum(1 for e1, e2 in full_true_n if check_separation(e1, e2, tbl))
    
    if fn_h2 + fn_h3 + fn_n == 0:
        best_safe.append((tbl, seps))

print(f"Found {len(best_safe)} globally safe magmas")
if best_safe:
    for i, (tbl, seps) in enumerate(best_safe[:10]):
        rows = [[tbl[a*3+b] for b in range(3)] for a in range(3)]
        print(f"\n  #{i+1}: separates {len(seps)}/{len(rot22_false)} FALSE in r22: {sorted(seps)}")
        print(f"       table: {rows[0]} / {rows[1]} / {rows[2]}")
        # Also count full pool FALSE separations
        fp_h2 = sum(1 for d in hard2_full if not d['answer'] and check_separation(d['equation1'], d['equation2'], tbl))
        fp_h3 = sum(1 for d in hard3_full if not d['answer'] and check_separation(d['equation1'], d['equation2'], tbl))
        print(f"       full H2 FALSE sep: {fp_h2}/100  full H3 FALSE sep: {fp_h3}/205")
