"""Validate candidate magma [0,0,2]/[0,2,2]/[2,0,1] across FULL hard2 pool + hard3 + normal."""
import json, re

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

# Candidate magma: [0,0,2] / [0,2,2] / [2,0,1]
# table[a*3+b]:     0*0=0, 0*1=0, 0*2=2, 1*0=0, 1*1=2, 1*2=2, 2*0=2, 2*1=0, 2*2=1
CAND = (0, 0, 2, 0, 2, 2, 2, 0, 1)

def check_pair(e1, e2, tbl):
    """Returns (e1_holds_default, e1_holds_zeros, e2_holds_default, would_separate)"""
    lhs1, rhs1 = e1.split(' = ', 1)
    lhs2, rhs2 = e2.split(' = ', 1)
    mapping = assign_vars(e1, e2)
    
    # Default assignment
    l1 = eval_magma(rewrite(lhs1, mapping), tbl)
    r1 = eval_magma(rewrite(rhs1, mapping), tbl)
    e1_def = (l1 == r1)
    
    # All-zeros
    zero_map = {v: 0 for v in mapping}
    l1z = eval_magma(rewrite(lhs1, zero_map), tbl)
    r1z = eval_magma(rewrite(rhs1, zero_map), tbl)
    e1_zero = (l1z == r1z)
    
    # E2 default
    l2 = eval_magma(rewrite(lhs2, mapping), tbl)
    r2 = eval_magma(rewrite(rhs2, mapping), tbl)
    e2_def = (l2 == r2)
    
    # Separation: E1 holds both checks, E2 fails
    sep = e1_def and e1_zero and not e2_def
    return e1_def, e1_zero, e2_def, sep

def validate_dataset(filepath, label):
    data = [json.loads(l) for l in open(filepath)]
    true_probs = [d for d in data if d['answer']]
    false_probs = [d for d in data if not d['answer']]
    
    # Check FALSE: how many would this magma separate?
    sep_count = 0
    for d in false_probs:
        _, _, _, sep = check_pair(d['equation1'], d['equation2'], CAND)
        if sep:
            sep_count += 1
    
    # Check TRUE: any FN risk?
    fn_count = 0
    fn_ids = []
    for d in true_probs:
        _, _, _, sep = check_pair(d['equation1'], d['equation2'], CAND)
        if sep:
            fn_count += 1
            fn_ids.append(d.get('id', '?'))
    
    print(f"\n{label} ({len(data)} problems: {len(true_probs)}T, {len(false_probs)}F)")
    print(f"  FALSE separated: {sep_count}/{len(false_probs)} ({sep_count/len(false_probs)*100:.1f}%)")
    print(f"  TRUE FN risk:    {fn_count}/{len(true_probs)} ({fn_count/len(true_probs)*100:.1f}%)")
    if fn_ids:
        print(f"  FN problem IDs:  {fn_ids[:20]}")
    return sep_count, fn_count, len(false_probs), len(true_probs)

print("=== Validating candidate magma [0,0,2]/[0,2,2]/[2,0,1] ===")
print(f"Table: 0*0=0 0*1=0 0*2=2 | 1*0=0 1*1=2 1*2=2 | 2*0=2 2*1=0 2*2=1")

# Full pools from HF cache
for subset in ['hard2', 'hard3', 'normal']:
    path = f'data/hf_cache/{subset}.jsonl'
    try:
        validate_dataset(path, f"Full {subset} pool")
    except Exception as e:
        print(f"\n{subset}: {e}")

# Also check current rotation
validate_dataset('data/benchmark/hard2_balanced30_true15_false15_rotation0022_20260417_145804.jsonl', 
                 "Hard2 rotation 22 (current)")
