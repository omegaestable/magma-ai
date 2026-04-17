"""Check T3R/T3L unsoundness with >=4 vars across all pools."""
import json, re
from itertools import product

def t3r(a, b): return (b + 1) % 3
def t3l(a, b): return (a + 1) % 3

def eval_magma(s, op):
    s = s.strip()
    while s.startswith('(') and s.endswith(')'):
        depth = 0; balanced = True
        for i, c in enumerate(s):
            if c == '(': depth += 1
            elif c == ')': depth -= 1
            if depth == 0 and i < len(s) - 1: balanced = False; break
        if balanced: s = s[1:-1].strip()
        else: break
    if s.isdigit(): return int(s)
    depth = 0; main_star = -1
    for i, c in enumerate(s):
        if c == '(': depth += 1
        elif c == ')': depth -= 1
        elif c == '*' and depth == 0: main_star = i; break
    if main_star == -1: return int(s)
    left = s[:main_star].strip(); right = s[main_star + 1:].strip()
    return op(eval_magma(left, op), eval_magma(right, op))

def sub_vars(expr, asgn):
    return ''.join(str(asgn[c]) if c.isalpha() else c for c in expr)

def get_vars(eq1, eq2):
    seen = []
    for c in re.findall(r'[a-z]', eq1 + ' ' + eq2):
        if c not in seen: seen.append(c)
    return seen

def check_exhaustive(e1l, e1r, e2l, e2r, op, variables):
    """Check if E1 holds on ALL assignments and E2 fails on at least one."""
    e1_universal = True
    e2_has_fail = False
    for combo in product(range(3), repeat=len(variables)):
        asgn = dict(zip(variables, combo))
        try:
            v1l = eval_magma(sub_vars(e1l, asgn), op)
            v1r = eval_magma(sub_vars(e1r, asgn), op)
            v2l = eval_magma(sub_vars(e2l, asgn), op)
            v2r = eval_magma(sub_vars(e2r, asgn), op)
        except:
            return False, False
        if v1l != v1r:
            e1_universal = False
            break
        if v2l != v2r:
            e2_has_fail = True
    return e1_universal, e2_has_fail

def check_2check(e1l, e1r, e2l, e2r, op, variables):
    """Simulate current cheatsheet: default + all-zeros."""
    seen = get_vars(e1l + ' = ' + e1r, e2l + ' = ' + e2r)
    default = {v: i % 3 for i, v in enumerate(seen)}
    zeros = {v: 0 for v in variables}
    
    for asgn in [default, zeros]:
        try:
            v1l = eval_magma(sub_vars(e1l, asgn), op)
            v1r = eval_magma(sub_vars(e1r, asgn), op)
            if v1l != v1r:
                return False  # E1 fails, skip this magma
        except:
            return False
    
    # Both E1 checks pass. Check E2 with default:
    try:
        v2l = eval_magma(sub_vars(e2l, default), op)
        v2r = eval_magma(sub_vars(e2r, default), op)
        return v2l != v2r  # True = separation claimed
    except:
        return False

for pool_name, pool_path in [
    ('hard', 'data/hf_cache/hard.jsonl'),
    ('hard3', 'data/hf_cache/hard3.jsonl'),
    ('normal', 'data/hf_cache/normal.jsonl'),
]:
    try:
        with open(pool_path) as f:
            problems = [json.loads(l) for l in f]
    except FileNotFoundError:
        print(f'{pool_name}: file not found, skipping')
        continue
    
    true_problems = [p for p in problems if p['answer'] == True]
    
    for test_name, op in [('T3R', t3r), ('T3L', t3l)]:
        false_seps_2check = 0
        false_seps_2check_ge4 = 0
        true_seps_exhaustive = 0
        
        for p in true_problems:
            eq1, eq2 = p['equation1'], p['equation2']
            parts1 = eq1.split('='); parts2 = eq2.split('=')
            e1l, e1r = parts1[0].strip(), parts1[1].strip()
            e2l, e2r = parts2[0].strip(), parts2[1].strip()
            
            variables = sorted(set(re.findall(r'[a-z]', eq1 + eq2)))
            n_vars = len(variables)
            
            if check_2check(e1l, e1r, e2l, e2r, op, variables):
                # 2-check claims separation. Verify exhaustively.
                e1_univ, e2_fail = check_exhaustive(e1l, e1r, e2l, e2r, op, variables)
                if e1_univ and e2_fail:
                    pass  # legitimate separation — but this is a TRUE problem, shouldn't happen!
                    # Actually this CAN'T happen for TRUE problems
                else:
                    false_seps_2check += 1
                    if n_vars >= 4:
                        false_seps_2check_ge4 += 1
        
        print(f'{pool_name} {test_name}: {false_seps_2check} TRUE falsely separated by 2-check '
              f'({false_seps_2check_ge4} have >=4 vars)')
    
    # Also check: how many FALSE with >=4 vars are ONLY separable by T3R/T3L?
    false_problems = [p for p in problems if p['answer'] == False]
    t3r_only_ge4 = 0
    for p in false_problems:
        eq1, eq2 = p['equation1'], p['equation2']
        parts1 = eq1.split('='); parts2 = eq2.split('=')
        e1l, e1r = parts1[0].strip(), parts1[1].strip()
        e2l, e2r = parts2[0].strip(), parts2[1].strip()
        variables = sorted(set(re.findall(r'[a-z]', eq1 + eq2)))
        if len(variables) < 4:
            continue
        # Check if any structural test catches it
        # (simplified: just check if T3R/T3L is only separator among magma tests)
        has_t3r = check_2check(e1l, e1r, e2l, e2r, t3r, variables)
        has_t3l = check_2check(e1l, e1r, e2l, e2r, t3l, variables)
        if has_t3r or has_t3l:
            t3r_only_ge4 += 1
    print(f'{pool_name}: {t3r_only_ge4} FALSE with >=4 vars separable by T3R/T3L 2-check')
    print()
