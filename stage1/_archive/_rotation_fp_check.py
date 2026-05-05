"""Check which FALSE problems in competition hard r23 are structurally separable."""
import json, re

def t3r(a, b): return (b + 1) % 3
def t3l(a, b): return (a + 1) % 3
def t5b(a, b): return (a + 2*b) % 3

NL1_TABLE = [[0,0,0],[1,1,0],[1,2,2]]
def nl1(a, b): return NL1_TABLE[a][b]

def eval_magma(s, op):
    s = s.strip()
    while s.startswith('(') and s.endswith(')'):
        depth = 0; balanced = True
        for i, c in enumerate(s):
            if c == '(': depth += 1
            elif c == ')': depth -= 1
            if depth == 0 and i < len(s)-1: balanced = False; break
        if balanced: s = s[1:-1].strip()
        else: break
    if s.isdigit(): return int(s)
    depth = 0; main_star = -1
    for i, c in enumerate(s):
        if c == '(': depth += 1
        elif c == ')': depth -= 1
        elif c == '*' and depth == 0: main_star = i; break
    if main_star == -1: return int(s)
    left = s[:main_star].strip(); right = s[main_star+1:].strip()
    return op(eval_magma(left, op), eval_magma(right, op))

def sub_vars(expr, asgn):
    return ''.join(str(asgn[c]) if c.isalpha() else c for c in expr)

def get_first_occurrence_order(eq1, eq2):
    seen = []
    for c in re.findall(r'[a-z]', eq1 + ' ' + eq2):
        if c not in seen: seen.append(c)
    return {v: i % 3 for i, v in enumerate(seen)}

def check_separates(eq1_l, eq1_r, eq2_l, eq2_r, op, assignments):
    """Check if any assignment separates (E1 holds but E2 fails)."""
    for asgn in assignments:
        try:
            e1l = eval_magma(sub_vars(eq1_l, asgn), op)
            e1r = eval_magma(sub_vars(eq1_r, asgn), op)
            e2l = eval_magma(sub_vars(eq2_l, asgn), op)
            e2r = eval_magma(sub_vars(eq2_r, asgn), op)
            if e1l == e1r and e2l != e2r:
                return True
        except:
            pass
    return False

# Structural tests
def lp(expr):
    s = expr.strip()
    for c in s:
        if c.isalpha(): return c
        if c not in '( ': break
    return None

def rp(expr):
    s = expr.strip()
    for c in reversed(s):
        if c.isalpha(): return c
        if c not in ') ': break
    return None

def has_star(expr):
    return '*' in expr

def get_vars_set(expr):
    return set(re.findall(r'[a-z]', expr))

def structural_separates(eq1, eq2):
    """Check if any of the 6 structural tests separate."""
    e1_parts = eq1.split('='); e2_parts = eq2.split('=')
    e1l, e1r = e1_parts[0].strip(), e1_parts[1].strip()
    e2l, e2r = e2_parts[0].strip(), e2_parts[1].strip()
    
    tests = []
    # LP
    e1_lp = lp(e1l) == lp(e1r)
    e2_lp = lp(e2l) == lp(e2r)
    if e1_lp and not e2_lp: return 'LP'
    
    # RP
    e1_rp = rp(e1l) == rp(e1r)
    e2_rp = rp(e2l) == rp(e2r)
    if e1_rp and not e2_rp: return 'RP'
    
    # C0
    e1_c0_l = has_star(e1l); e1_c0_r = has_star(e1r)
    e2_c0_l = has_star(e2l); e2_c0_r = has_star(e2r)
    e1_c0 = (e1_c0_l == e1_c0_r) if (e1_c0_l and e1_c0_r) else (not e1_c0_l and not e1_c0_r and lp(e1l) == lp(e1r))
    e2_c0 = (e2_c0_l == e2_c0_r) if (e2_c0_l and e2_c0_r) else (not e2_c0_l and not e2_c0_r and lp(e2l) == lp(e2r))
    # Simplified: both have * or neither has * and same var
    e1_c0 = (e1_c0_l and e1_c0_r) or (not e1_c0_l and not e1_c0_r)
    e2_c0 = (e2_c0_l and e2_c0_r) or (not e2_c0_l and not e2_c0_r)
    if e1_c0 and not e2_c0: return 'C0'
    
    return None

with open('data/benchmark/hard_balanced30_true15_false15_rotation0023_20260417_155001.jsonl') as f:
    rotation = [json.loads(l) for l in f]

false_problems = [(i+1, p) for i, p in enumerate(rotation) if not p['answer']]
print(f'{len(false_problems)} FALSE problems in rotation\n')

for pos, p in false_problems:
    pid = p['id']
    eq1, eq2 = p['equation1'], p['equation2']
    e1_parts = eq1.split('='); e2_parts = eq2.split('=')
    e1l, e1r = e1_parts[0].strip(), e1_parts[1].strip()
    e2l, e2r = e2_parts[0].strip(), e2_parts[1].strip()
    
    # Check structural
    struct = structural_separates(eq1, eq2)
    
    # Check magma tests
    all_vars = sorted(set(re.findall(r'[a-z]', eq1 + eq2)))
    default_asgn = get_first_occurrence_order(eq1, eq2)
    zeros_asgn = {v: 0 for v in all_vars}
    ones_asgn = {v: 1 for v in all_vars}
    assignments = [default_asgn, zeros_asgn, ones_asgn]
    
    # Generate more assignments for exhaustive check
    from itertools import product
    n = len(all_vars)
    all_assignments = []
    for combo in product(range(3), repeat=n):
        all_assignments.append(dict(zip(all_vars, combo)))
    
    magma_seps = []
    for name, op in [('T3R', t3r), ('T3L', t3l), ('T5B', t5b), ('NL1', nl1)]:
        if check_separates(e1l, e1r, e2l, e2r, op, [default_asgn, zeros_asgn]):
            magma_seps.append(name)
    
    any_sep = struct or magma_seps
    status = f'struct={struct} magma={magma_seps}' if any_sep else 'NO SEPARATOR'
    print(f'  [{pos:2d}/30] {pid}: {status}')

print('\nDone.')
