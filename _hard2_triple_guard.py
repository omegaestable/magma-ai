"""Check if adding all-ones check eliminates FN risks for top candidate magmas."""
import json, re

hard2_full = [json.loads(l) for l in open('data/hf_cache/hard2.jsonl')]
hard3_full = [json.loads(l) for l in open('data/hf_cache/hard3.jsonl')]
normal_full = [json.loads(l) for l in open('data/hf_cache/normal.jsonl')]

# Current rotation
rot22 = [json.loads(l) for l in open('data/benchmark/hard2_balanced30_true15_false15_rotation0022_20260417_145804.jsonl')]
rot22_false = [d for d in rot22 if not d['answer']]
rot22_true = [d for d in rot22 if d['answer']]

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

def check_with_triple_guard(e1, e2, tbl):
    """3-point check: default + all-zeros + all-ones. Returns True if separates."""
    lhs1, rhs1 = e1.split(' = ', 1)
    lhs2, rhs2 = e2.split(' = ', 1)
    mapping = assign_vars(e1, e2)
    
    # Check 1: default vars
    l1 = eval_magma(rewrite(lhs1, mapping), tbl)
    r1 = eval_magma(rewrite(rhs1, mapping), tbl)
    if l1 != r1: return False
    
    # Check 2: all-zeros
    zero_map = {v: 0 for v in mapping}
    l1z = eval_magma(rewrite(lhs1, zero_map), tbl)
    r1z = eval_magma(rewrite(rhs1, zero_map), tbl)
    if l1z != r1z: return False
    
    # Check 3: all-ones
    ones_map = {v: 1 for v in mapping}
    l1o = eval_magma(rewrite(lhs1, ones_map), tbl)
    r1o = eval_magma(rewrite(rhs1, ones_map), tbl)
    if l1o != r1o: return False
    
    # E2 check
    l2 = eval_magma(rewrite(lhs2, mapping), tbl)
    r2 = eval_magma(rewrite(rhs2, mapping), tbl)
    return l2 != r2

# Candidates to evaluate (from previous search)
candidates = [
    ((1,0,2,0,0,2,2,2,2), "#10 from prev"),  # 7/15, H2=0,H3=4,N=3
    ((1,0,2,0,0,2,2,0,1), "#2 from prev"),    # 8/15, H2=16,H3=23,N=90
    ((1,0,2,0,0,1,2,1,2), "#1 from prev"),    # 8/15, H2=20,H3=35,N=108
    ((1,0,2,0,0,2,2,1,2), "#4 from prev"),    # 8/15, H2=10,H3=12,N=54
    ((1,0,2,0,0,2,2,2,1), "#9 from prev"),    # 7/15, H2=2,H3=15,N=34
]

# Also check original top magma [0,0,2]/[0,2,2]/[2,0,1] with triple check
candidates.append(((0,0,2,0,2,2,2,0,1), "orig #1 (0*0=0)"))

print("=== Triple-guard check (default + all-zeros + all-ones) ===\n")

for tbl, label in candidates:
    rows = [[tbl[a*3+b] for b in range(3)] for a in range(3)]
    
    # Rotation 22 coverage
    rot22_seps = sum(1 for d in rot22_false 
                     if check_with_triple_guard(d['equation1'], d['equation2'], tbl))
    rot22_fn = sum(1 for d in rot22_true 
                   if check_with_triple_guard(d['equation1'], d['equation2'], tbl))
    
    # Full pool cross-validation
    fn_h2 = sum(1 for d in hard2_full if d['answer'] and 
                check_with_triple_guard(d['equation1'], d['equation2'], tbl))
    fn_h3 = sum(1 for d in hard3_full if d['answer'] and 
                check_with_triple_guard(d['equation1'], d['equation2'], tbl))
    fn_n = sum(1 for d in normal_full if d['answer'] and 
               check_with_triple_guard(d['equation1'], d['equation2'], tbl))
    
    sep_h2 = sum(1 for d in hard2_full if not d['answer'] and 
                 check_with_triple_guard(d['equation1'], d['equation2'], tbl))
    sep_h3 = sum(1 for d in hard3_full if not d['answer'] and 
                 check_with_triple_guard(d['equation1'], d['equation2'], tbl))
    
    print(f"{label}")
    print(f"  Table: {rows[0]} / {rows[1]} / {rows[2]}")
    print(f"  R22: {rot22_seps}/15 FALSE sep, {rot22_fn} FN")
    print(f"  Full pool FN: H2={fn_h2}/100 H3={fn_h3}/195 N={fn_n}/500")
    print(f"  Full pool FALSE sep: H2={sep_h2}/100 H3={sep_h3}/205")
    total_fn = fn_h2 + fn_h3 + fn_n
    print(f"  {'✅ GLOBALLY SAFE' if total_fn == 0 else f'⚠️  Total FN risk: {total_fn}'}")
    print()

# Now do exhaustive search with triple guard for globally safe magmas with 0*0!=0
print("\n=== Exhaustive safe search with triple guard ===")
from itertools import product as iprod

best_safe = []
for tbl in iprod(range(3), repeat=9):
    if tbl[0] == 0:
        continue
    
    seps = sum(1 for d in rot22_false 
               if check_with_triple_guard(d['equation1'], d['equation2'], tbl))
    if seps < 3:
        continue
    
    # Quick check: any FN on rotation 22?
    fn = sum(1 for d in rot22_true 
             if check_with_triple_guard(d['equation1'], d['equation2'], tbl))
    if fn > 0:
        continue
    
    # Full pool check
    fn_h2 = sum(1 for d in hard2_full if d['answer'] and 
                check_with_triple_guard(d['equation1'], d['equation2'], tbl))
    if fn_h2 > 0:
        continue
    fn_h3 = sum(1 for d in hard3_full if d['answer'] and 
                check_with_triple_guard(d['equation1'], d['equation2'], tbl))
    if fn_h3 > 0:
        continue
    fn_n = sum(1 for d in normal_full if d['answer'] and 
               check_with_triple_guard(d['equation1'], d['equation2'], tbl))
    if fn_n > 0:
        continue
    
    sep_h2_full = sum(1 for d in hard2_full if not d['answer'] and 
                      check_with_triple_guard(d['equation1'], d['equation2'], tbl))
    sep_h3_full = sum(1 for d in hard3_full if not d['answer'] and 
                      check_with_triple_guard(d['equation1'], d['equation2'], tbl))
    
    best_safe.append((tbl, seps, sep_h2_full, sep_h3_full))

best_safe.sort(key=lambda x: x[1], reverse=True)
print(f"Found {len(best_safe)} globally safe magmas with 3+ separations on r22")

for i, (tbl, seps, sh2, sh3) in enumerate(best_safe[:10]):
    rows = [[tbl[a*3+b] for b in range(3)] for a in range(3)]
    print(f"\n  #{i+1}: R22 sep={seps}/15, full H2={sh2}/100, full H3={sh3}/205")
    print(f"       table: {rows[0]} / {rows[1]} / {rows[2]}")
