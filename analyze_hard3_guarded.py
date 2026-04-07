"""Guarded spot-check: only run T3R when E1 has RP=HOLD, T3L when E1 has LP=HOLD.
This makes the check mathematically sound (spot=universal under these guards)."""
import json, re, itertools

def load_benchmark(path):
    with open(path) as f:
        return [json.loads(l) for l in f]

hard3 = load_benchmark("data/benchmark/hard3_balanced40_true20_false20_rotation0002_20260403_185904.jsonl")
normal = load_benchmark("data/benchmark/normal_balanced60_true30_false30_rotation0002_20260403_185904.jsonl")

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

def first_letter(s):
    m = re.search(r'[a-z]', s)
    return m.group() if m else '?'

def last_letter(s):
    m = re.search(r'[a-z](?=[^a-z]*$)', s)
    return m.group() if m else '?'

def has_star(s):
    return '*' in s

def get_ordered_vars(eq_str):
    seen = []
    for m in re.finditer(r'[a-z]', eq_str):
        v = m.group()
        if v not in seen: seen.append(v)
    return seen

T3R = [1,2,0, 1,2,0, 1,2,0]  # a*b = (b+1)%3
T3L = [1,1,1, 2,2,2, 0,0,0]  # a*b = (a+1)%3

def structural_tests(e1, e2):
    """Run LP, RP, C0. Return dict of results."""
    e1l, e1r = e1.split('=', 1)
    e2l, e2r = e2.split('=', 1)
    results = {}
    
    # LP
    e1_lp = first_letter(e1l) == first_letter(e1r)
    e2_lp = first_letter(e2l) == first_letter(e2r)
    results['LP'] = ('HOLD' if e1_lp else 'FAIL', 'HOLD' if e2_lp else 'FAIL')
    
    # RP
    e1_rp = last_letter(e1l) == last_letter(e1r)
    e2_rp = last_letter(e2l) == last_letter(e2r)
    results['RP'] = ('HOLD' if e1_rp else 'FAIL', 'HOLD' if e2_rp else 'FAIL')
    
    # C0
    e1_c0_l, e1_c0_r = has_star(e1l), has_star(e1r)
    e2_c0_l, e2_c0_r = has_star(e2l), has_star(e2r)
    e1_c0 = (e1_c0_l == e1_c0_r)  # both have * or both don't
    e2_c0 = (e2_c0_l == e2_c0_r)
    results['C0'] = ('HOLD' if e1_c0 else 'FAIL', 'HOLD' if e2_c0 else 'FAIL')
    
    # VARS
    e1_vl = set(re.findall(r'[a-z]', e1l))
    e1_vr = set(re.findall(r'[a-z]', e1r))
    e2_vl = set(re.findall(r'[a-z]', e2l))
    e2_vr = set(re.findall(r'[a-z]', e2r))
    
    # Simplified VARS: same set = HOLD
    if has_star(e1l) and has_star(e1r):
        e1_vars = e1_vl == e1_vr
    elif not has_star(e1l) and not has_star(e1r):
        e1_vars = e1_vl == e1_vr
    else:
        bare = e1_vl if not has_star(e1l) else e1_vr
        star = e1_vr if not has_star(e1l) else e1_vl
        e1_vars = star == bare
    
    if has_star(e2l) and has_star(e2r):
        e2_vars = e2_vl == e2_vr
    elif not has_star(e2l) and not has_star(e2r):
        e2_vars = e2_vl == e2_vr
    else:
        bare = e2_vl if not has_star(e2l) else e2_vr
        star = e2_vr if not has_star(e2l) else e2_vl
        e2_vars = star == bare
    
    results['VARS'] = ('HOLD' if e1_vars else 'FAIL', 'HOLD' if e2_vars else 'FAIL')
    
    return results

def has_structural_sep(results):
    """Check if any test shows E1=HOLD, E2=FAIL."""
    for test, (e1r, e2r) in results.items():
        if e1r == 'HOLD' and e2r == 'FAIL':
            return True
    return False

def guarded_t3r_check(e1, e2, struct_results):
    """T3R check, ONLY if E1 RP=HOLD. Sound because RP=HOLD means
    T3R universal check = spot check at any single assignment."""
    e1_rp = struct_results['RP'][0]
    if e1_rp != 'HOLD':
        return False  # Not applicable
    
    vars_ordered = get_ordered_vars(e1 + " " + e2)
    
    e1l, e1r = e1.split('=', 1)
    e2l, e2r = e2.split('=', 1)
    t1l, t1r = parse_expr(e1l), parse_expr(e1r)
    t2l, t2r = parse_expr(e2l), parse_expr(e2r)
    
    # Single assignment is sufficient when E1 RP=HOLD
    assignment = {v: i % 3 for i, v in enumerate(vars_ordered)}
    
    e1_lhs = eval_tree(t1l, assignment, T3R, 3)
    e1_rhs = eval_tree(t1r, assignment, T3R, 3)
    e2_lhs = eval_tree(t2l, assignment, T3R, 3)
    e2_rhs = eval_tree(t2r, assignment, T3R, 3)
    
    return (e1_lhs == e1_rhs) and (e2_lhs != e2_rhs)

def guarded_t3l_check(e1, e2, struct_results):
    """T3L check, ONLY if E1 LP=HOLD."""
    e1_lp = struct_results['LP'][0]
    if e1_lp != 'HOLD':
        return False
    
    vars_ordered = get_ordered_vars(e1 + " " + e2)
    
    e1l, e1r = e1.split('=', 1)
    e2l, e2r = e2.split('=', 1)
    t1l, t1r = parse_expr(e1l), parse_expr(e1r)
    t2l, t2r = parse_expr(e2l), parse_expr(e2r)
    
    assignment = {v: i % 3 for i, v in enumerate(vars_ordered)}
    
    e1_lhs = eval_tree(t1l, assignment, T3L, 3)
    e1_rhs = eval_tree(t1r, assignment, T3L, 3)
    e2_lhs = eval_tree(t2l, assignment, T3L, 3)
    e2_rhs = eval_tree(t2r, assignment, T3L, 3)
    
    return (e1_lhs == e1_rhs) and (e2_lhs != e2_rhs)


def full_eval(pairs, label):
    """Full pipeline: structural tests + guarded magma checks."""
    results = {'tp': 0, 'tn': 0, 'fp': 0, 'fn': 0}
    details = []
    
    for p in pairs:
        pid = p['id']
        answer = p['answer']
        e1, e2 = p['equation1'], p['equation2']
        
        struct = structural_tests(e1, e2)
        struct_sep = has_structural_sep(struct)
        
        t3r_sep = False
        t3l_sep = False
        if not struct_sep:
            t3r_sep = guarded_t3r_check(e1, e2, struct)
            if not t3r_sep:
                t3l_sep = guarded_t3l_check(e1, e2, struct)
        
        predicted = False if (struct_sep or t3r_sep or t3l_sep) else True
        
        if answer is True and predicted is True: results['tp'] += 1
        elif answer is False and predicted is False: results['tn'] += 1
        elif answer is True and predicted is False:
            results['fp'] += 1
            method = 'struct' if struct_sep else ('T3R' if t3r_sep else 'T3L')
            details.append(f"  FP: {pid} ({method})")
        else:
            results['fn'] += 1
            details.append(f"  FN: {pid}")
    
    total = len(pairs)
    correct = results['tp'] + results['tn']
    acc = 100 * correct / total
    
    print(f"\n{label}:")
    print(f"  Accuracy: {correct}/{total} = {acc:.1f}%")
    print(f"  TP={results['tp']} TN={results['tn']} FP={results['fp']} FN={results['fn']}")
    for d in details:
        print(d)
    
    return results

print("=" * 80)
print("FULL PIPELINE: LP + RP + C0 + VARS + guarded T3R + guarded T3L")
print("=" * 80)

h3_results = full_eval(hard3, "Hard3 (40 pairs)")
n_results = full_eval(normal, "Normal (60 pairs)")

print("\n" + "=" * 80)
print("STRUCTURAL ONLY: LP + RP + C0 + VARS (v23c equivalent)")
print("=" * 80)

# For comparison: structural only
for p_list, label in [(hard3, "Hard3"), (normal, "Normal")]:
    res = {'tp': 0, 'tn': 0, 'fp': 0, 'fn': 0}
    for p in p_list:
        struct = structural_tests(p['equation1'], p['equation2'])
        predicted = False if has_structural_sep(struct) else True
        ans = p['answer']
        if ans is True and predicted is True: res['tp'] += 1
        elif ans is False and predicted is False: res['tn'] += 1
        elif ans is True and predicted is False: res['fp'] += 1
        else: res['fn'] += 1
    total = len(p_list)
    correct = res['tp'] + res['tn']
    print(f"\n{label}: {correct}/{total} = {100*correct/total:.1f}%")
    print(f"  TP={res['tp']} TN={res['tn']} FP={res['fp']} FN={res['fn']}")

# Also break down: which hard3 FALSE pairs does each method catch?
print("\n" + "=" * 80)
print("HARD3 FALSE PAIR BREAKDOWN")
print("=" * 80)
h3_false = [p for p in hard3 if p['answer'] is False]
for p in h3_false:
    e1, e2 = p['equation1'], p['equation2']
    struct = structural_tests(e1, e2)
    struct_sep = has_structural_sep(struct)
    t3r = guarded_t3r_check(e1, e2, struct) if not struct_sep else False
    t3l = guarded_t3l_check(e1, e2, struct) if not struct_sep and not t3r else False
    
    method = "struct" if struct_sep else ("T3R" if t3r else ("T3L" if t3l else "MISS"))
    rp_e1 = struct['RP'][0]
    lp_e1 = struct['LP'][0]
    print(f"  {p['id']}: {method:6s} (E1: LP={lp_e1}, RP={rp_e1})")
