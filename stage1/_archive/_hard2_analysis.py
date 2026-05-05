"""Quick analysis: which hard2 FALSE problems can our magma suite separate?"""
import json, re

data = [json.loads(l) for l in open('data/benchmark/hard2_balanced30_true15_false15_rotation0022_20260417_145804.jsonl')]
false_probs = [d for d in data if not d['answer']]

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

def eval_magma(expr, table_fn):
    s = expr.replace(' ', '')
    while '*' in s:
        m = re.search(r'\((\d)\*(\d)\)', s)
        if not m:
            m = re.search(r'(\d)\*(\d)', s)
        if not m:
            break
        a, b = int(m.group(1)), int(m.group(2))
        s = s[:m.start()] + str(table_fn(a, b)) + s[m.end():]
    s = s.replace('(', '').replace(')', '')
    return int(s) if s.isdigit() else -1

# Magma definitions
t3r = lambda a, b: (b + 1) % 3
t3l = lambda a, b: (a + 1) % 3
t5b = lambda a, b: (a + 2*b) % 3
nl1_tbl = {(0,0):0,(0,1):0,(0,2):0,(1,0):1,(1,1):1,(1,2):0,(2,0):1,(2,1):2,(2,2):2}
nl1 = lambda a, b: nl1_tbl[(a, b)]

def rewrite(expr, mapping):
    return ''.join(str(mapping[c]) if c.isalpha() else c for c in expr)

print("=== Hard2 FALSE problems: magma separator analysis ===")
print(f"{'ID':12s} {'nv':3s} {'T3R':5s} {'T3L':5s} {'T5B':5s} {'NL1':5s} {'any':4s}")
print("-" * 45)

sep_count = 0
for d in false_probs:
    pid = d.get('id', '?')
    e1 = d['equation1']
    e2 = d['equation2']
    lhs1, rhs1 = e1.split(' = ', 1)
    lhs2, rhs2 = e2.split(' = ', 1)
    
    mapping = assign_vars(e1, e2)
    nvars = len(mapping)
    
    results = {}
    for name, fn in [('T3R', t3r), ('T3L', t3l), ('T5B', t5b), ('NL1', nl1)]:
        # Skip T5B and NL1 for 4+ vars (as cheatsheet does)
        if name in ('T5B', 'NL1') and nvars >= 4:
            results[name] = 'SKIP'
            continue
        
        l1 = eval_magma(rewrite(lhs1, mapping), fn)
        r1 = eval_magma(rewrite(rhs1, mapping), fn)
        l2 = eval_magma(rewrite(lhs2, mapping), fn)
        r2 = eval_magma(rewrite(rhs2, mapping), fn)
        
        e1_holds = (l1 == r1)
        e2_holds = (l2 == r2)
        
        # Also check all-zeros
        zero_map = {v: 0 for v in mapping}
        l1z = eval_magma(rewrite(lhs1, zero_map), fn)
        r1z = eval_magma(rewrite(rhs1, zero_map), fn)
        e1_holds_zero = (l1z == r1z)
        
        sep = e1_holds and e1_holds_zero and not e2_holds
        results[name] = 'SEP' if sep else '  -'
    
    any_sep = 'YES' if any(v == 'SEP' for v in results.values()) else ' NO'
    if any_sep == 'YES':
        sep_count += 1
    print(f"{pid:12s} {nvars:3d} {results['T3R']:5s} {results['T3L']:5s} {results['T5B']:5s} {results['NL1']:5s} {any_sep}")

print(f"\n{sep_count}/{len(false_probs)} FALSE problems have at least one magma separator")
print(f"Theoretical max FALSE acc with current suite: {sep_count}/{len(false_probs)} = {sep_count/len(false_probs)*100:.0f}%")
print(f"Theoretical max overall acc (all TRUE correct): {(15+sep_count)}/30 = {(15+sep_count)/30*100:.1f}%")
