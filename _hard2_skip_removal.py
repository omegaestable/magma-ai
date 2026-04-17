"""Check what happens if we REMOVE the 4+ variable skip for T5B and NL1.
This tests whether allowing T5B/NL1 on 4+ var problems adds separations without FN risk."""
import json, re

hard2_full = [json.loads(l) for l in open('data/hf_cache/hard2.jsonl')]
hard3_full = [json.loads(l) for l in open('data/hf_cache/hard3.jsonl')]
normal_full = [json.loads(l) for l in open('data/hf_cache/normal.jsonl')]
rot22 = [json.loads(l) for l in open('data/benchmark/hard2_balanced30_true15_false15_rotation0022_20260417_145804.jsonl')]

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

t5b = lambda a, b: (a + 2*b) % 3
nl1_tbl = {(0,0):0,(0,1):0,(0,2):0,(1,0):1,(1,1):1,(1,2):0,(2,0):1,(2,1):2,(2,2):2}
nl1 = lambda a, b: nl1_tbl[(a, b)]

def check_sep(e1, e2, fn):
    lhs1, rhs1 = e1.split(' = ', 1)
    lhs2, rhs2 = e2.split(' = ', 1)
    mapping = assign_vars(e1, e2)
    
    l1 = eval_magma(rewrite(lhs1, mapping), [fn(a,b) for a in range(3) for b in range(3)])
    r1 = eval_magma(rewrite(rhs1, mapping), [fn(a,b) for a in range(3) for b in range(3)])
    if l1 != r1: return False
    
    zero_map = {v: 0 for v in mapping}
    l1z = eval_magma(rewrite(lhs1, zero_map), [fn(a,b) for a in range(3) for b in range(3)])
    r1z = eval_magma(rewrite(rhs1, zero_map), [fn(a,b) for a in range(3) for b in range(3)])
    if l1z != r1z: return False
    
    l2 = eval_magma(rewrite(lhs2, mapping), [fn(a,b) for a in range(3) for b in range(3)])
    r2 = eval_magma(rewrite(rhs2, mapping), [fn(a,b) for a in range(3) for b in range(3)])
    return l2 != r2

def count_vars(e1):
    return len(set(c for c in e1 if c.isalpha()))

# Check skipped problems (4+ vars) in rotation 22
print("=== Rotation 22: problems currently SKIPPED by T5B/NL1 (4+ vars) ===")
for d in rot22:
    nvars = count_vars(d['equation1'])
    if nvars >= 4:
        gt = 'T' if d['answer'] else 'F'
        t5b_sep = check_sep(d['equation1'], d['equation2'], t5b)
        nl1_sep = check_sep(d['equation1'], d['equation2'], nl1)
        risk = ""
        if d['answer'] and (t5b_sep or nl1_sep):
            risk = " ⚠️ FN RISK!"
        elif not d['answer'] and (t5b_sep or nl1_sep):
            risk = " ← would catch!"
        print(f"  {d.get('id','?'):12s} gt={gt} vars={nvars} T5B={'SEP' if t5b_sep else '  -'} NL1={'SEP' if nl1_sep else '  -'}{risk}")

# Full pool analysis: what's the FN risk of removing the skip?
print("\n=== Full pool: FN risk of removing 4+ var skip ===")
for pool_name, pool in [("hard2", hard2_full), ("hard3", hard3_full), ("normal", normal_full)]:
    true_probs = [d for d in pool if d['answer']]
    false_probs = [d for d in pool if not d['answer']]
    
    # Count 4+ var skipped
    t5b_fn = 0
    nl1_fn = 0
    t5b_tp = 0
    nl1_tp = 0
    skipped_true = 0
    skipped_false = 0
    
    for d in pool:
        nvars = count_vars(d['equation1'])
        if nvars < 4:
            continue
        
        if d['answer']:
            skipped_true += 1
            if check_sep(d['equation1'], d['equation2'], t5b):
                t5b_fn += 1
            if check_sep(d['equation1'], d['equation2'], nl1):
                nl1_fn += 1
        else:
            skipped_false += 1
            if check_sep(d['equation1'], d['equation2'], t5b):
                t5b_tp += 1
            if check_sep(d['equation1'], d['equation2'], nl1):
                nl1_tp += 1
    
    print(f"\n  {pool_name}: {skipped_true} TRUE + {skipped_false} FALSE with 4+ vars")
    print(f"    T5B: would catch {t5b_tp} FALSE, FN risk on {t5b_fn} TRUE")
    print(f"    NL1: would catch {nl1_tp} FALSE, FN risk on {nl1_fn} TRUE")
    
    # Net value
    for name, tp, fn in [("T5B", t5b_tp, t5b_fn), ("NL1", nl1_tp, nl1_fn)]:
        if tp > 0 or fn > 0:
            print(f"    {name} net: +{tp} correct, -{fn} wrong")
