"""Search for a 4-element magma separator for hard2 FALSE problems.
Instead of brute-force (4^16 = 4B too many), sample random magmas."""
import json, re, random

random.seed(42)

data = [json.loads(l) for l in open('data/benchmark/hard2_balanced30_true15_false15_rotation0022_20260417_145804.jsonl')]
false_probs = [d for d in data if not d['answer']]
true_probs = [d for d in data if d['answer']]

# Full pools
hard2_full = [json.loads(l) for l in open('data/hf_cache/hard2.jsonl')]
hard3_full = [json.loads(l) for l in open('data/hf_cache/hard3.jsonl')]

def assign_vars_mod4(e1, e2):
    full = e1 + ' ' + e2
    seen = []
    for c in full:
        if c.isalpha() and c not in seen:
            seen.append(c)
    mapping = {}
    for i, v in enumerate(seen):
        mapping[v] = i % 4
    return mapping

def rewrite(expr, mapping):
    return ''.join(str(mapping[c]) if c.isalpha() else c for c in expr)

def eval_magma4(expr, tbl):
    """Evaluate with a 4-element magma table (16 entries)."""
    s = expr.replace(' ', '')
    while '*' in s:
        m = re.search(r'\((\d)\*(\d)\)', s)
        if not m:
            m = re.search(r'(\d)\*(\d)', s)
        if not m:
            break
        a, b = int(m.group(1)), int(m.group(2))
        s = s[:m.start()] + str(tbl[a*4+b]) + s[m.end():]
    s = s.replace('(', '').replace(')', '')
    return int(s) if s.isdigit() else -1

def check_sep_4elem(e1, e2, tbl):
    """Dual-check with 4-element magma: default + all-zeros."""
    lhs1, rhs1 = e1.split(' = ', 1)
    lhs2, rhs2 = e2.split(' = ', 1)
    mapping = assign_vars_mod4(e1, e2)
    
    # Default
    l1 = eval_magma4(rewrite(lhs1, mapping), tbl)
    r1 = eval_magma4(rewrite(rhs1, mapping), tbl)
    if l1 != r1: return False
    
    # All-zeros
    zero_map = {v: 0 for v in mapping}
    l1z = eval_magma4(rewrite(lhs1, zero_map), tbl)
    r1z = eval_magma4(rewrite(rhs1, zero_map), tbl)
    if l1z != r1z: return False
    
    # E2
    l2 = eval_magma4(rewrite(lhs2, mapping), tbl)
    r2 = eval_magma4(rewrite(rhs2, mapping), tbl)
    return l2 != r2

# Sample random 4-element magmas
N_SAMPLES = 500000
print(f"Sampling {N_SAMPLES} random 4-element magmas...")

best = []
for trial in range(N_SAMPLES):
    if trial % 100000 == 0 and trial > 0:
        print(f"  {trial}/{N_SAMPLES}...")
    
    tbl = tuple(random.randint(0, 3) for _ in range(16))
    
    # Must have 0*0 != 0 for all-zeros check effectiveness
    if tbl[0] == 0:
        continue
    
    seps = set()
    for d in false_probs:
        if check_sep_4elem(d['equation1'], d['equation2'], tbl):
            seps.add(d.get('id', '?'))
    
    if len(seps) < 5:
        continue
    
    # Check rotation 22 TRUE
    fn = 0
    for d in true_probs:
        if check_sep_4elem(d['equation1'], d['equation2'], tbl):
            fn += 1
    
    if fn > 0:
        continue
    
    best.append((tbl, seps))

print(f"\nFound {len(best)} 4-element magmas with 5+ seps and 0 FN on r22")

# Sort by coverage
best.sort(key=lambda x: len(x[1]), reverse=True)

# Cross-validate top candidates
print("\nTop 10 candidates:")
for i, (tbl, seps) in enumerate(best[:10]):
    rows = [[tbl[a*4+b] for b in range(4)] for a in range(4)]
    
    fn_h2 = sum(1 for d in hard2_full if d['answer'] and 
                check_sep_4elem(d['equation1'], d['equation2'], tbl))
    fn_h3 = sum(1 for d in hard3_full if d['answer'] and 
                check_sep_4elem(d['equation1'], d['equation2'], tbl))
    
    sep_h2 = sum(1 for d in hard2_full if not d['answer'] and 
                 check_sep_4elem(d['equation1'], d['equation2'], tbl))
    
    print(f"\n  #{i+1}: R22 sep={len(seps)}/15: {sorted(seps)}")
    print(f"       table: {rows}")
    print(f"       Full H2: sep={sep_h2}/100F, FN={fn_h2}/100T")
    print(f"       Full H3: FN={fn_h3}/195T")
    total_fn = fn_h2 + fn_h3
    print(f"       {'✅ SAFE (H2+H3)' if total_fn == 0 else f'⚠️  FN risk: H2={fn_h2} H3={fn_h3}'}")
