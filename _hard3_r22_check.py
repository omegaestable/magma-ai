"""Check which hard3 r22 FALSE problems have separators in v28c's test suite."""
import json, itertools

# Load the hard3 r22 data
with open('data/benchmark/hard3_balanced30_true15_false15_rotation0022_20260417_145804.jsonl') as f:
    problems = [json.loads(line) for line in f]

false_problems = [p for p in problems if not p['answer']]
print(f"Total FALSE problems: {len(false_problems)}\n")

MAGMAS = {
    'T3R': [[0,2,0],[1,1,2],[1,0,0]],
    'T3L': [[0,1,1],[2,1,0],[0,2,0]],
    'T5B': [[0,0,0],[1,1,2],[0,2,1]],  # NL1 table transposed is wrong, let me use correct
    'NL1': [[0,0,0],[1,1,0],[1,2,2]],
}

def eval_expr(expr, vals, table, size=3):
    expr = expr.strip()
    if expr.isalpha() and len(expr) == 1:
        return vals[expr]
    depth = 0
    for i in range(len(expr)):
        if expr[i] == '(':
            depth += 1
        elif expr[i] == ')':
            depth -= 1
        elif expr[i] == '*' and depth == 0:
            left = eval_expr(expr[:i], vals, table, size)
            right = eval_expr(expr[i+1:], vals, table, size)
            return table[left][right]
    if expr.startswith('(') and expr.endswith(')'):
        return eval_expr(expr[1:-1], vals, table, size)
    raise ValueError(f"Cannot parse: {expr}")

def get_vars(expr):
    return set(c for c in expr if c.isalpha())

def check_equation(eq_str, table, size=3):
    parts = eq_str.split('=', 1)
    lhs_str, rhs_str = parts[0].strip(), parts[1].strip()
    variables = sorted(get_vars(lhs_str) | get_vars(rhs_str))
    for assignment in itertools.product(range(size), repeat=len(variables)):
        vals = dict(zip(variables, assignment))
        try:
            l = eval_expr(lhs_str, vals, table, size)
            r = eval_expr(rhs_str, vals, table, size)
            if l != r:
                return False
        except:
            return None
    return True

def check_structural(eq1, eq2):
    """Check 6 structural tests, return list of separating tests."""
    separators = []
    lhs1, rhs1 = eq1.split('=', 1)
    lhs2, rhs2 = eq2.split('=', 1)
    lhs1, rhs1 = lhs1.strip(), rhs1.strip()
    lhs2, rhs2 = lhs2.strip(), rhs2.strip()
    
    # LP
    def first_letter(s):
        for c in s:
            if c.isalpha(): return c
        return None
    def last_letter(s):
        for c in reversed(s):
            if c.isalpha(): return c
        return None
    
    lp_e1 = first_letter(lhs1) == first_letter(rhs1)
    lp_e2 = first_letter(lhs2) == first_letter(rhs2)
    if lp_e1 and not lp_e2: separators.append('LP')
    
    rp_e1 = last_letter(lhs1) == last_letter(rhs1)
    rp_e2 = last_letter(lhs2) == last_letter(rhs2)
    if rp_e1 and not rp_e2: separators.append('RP')
    
    c0_e1 = ('*' in lhs1) == ('*' in rhs1)
    c0_e2 = ('*' in lhs2) == ('*' in rhs2)
    if c0_e1 and not c0_e2: separators.append('C0')
    
    # VARS
    def var_set(s): return set(c for c in s if c.isalpha())
    vs_e1 = var_set(lhs1) == var_set(rhs1) if ('*' in lhs1 and '*' in rhs1) else True
    vs_e2 = var_set(lhs2) == var_set(rhs2) if ('*' in lhs2 and '*' in rhs2) else True
    if vs_e1 and not vs_e2: separators.append('VARS')
    
    # COUNT2
    def count_vars(s):
        counts = {}
        for c in s:
            if c.isalpha():
                counts[c] = counts.get(c, 0) + 1
        return counts
    
    def count2_holds(l, r):
        cl, cr = count_vars(l), count_vars(r)
        all_vars = set(cl.keys()) | set(cr.keys())
        return all(cl.get(v,0) % 2 == cr.get(v,0) % 2 for v in all_vars)
    
    ct2_e1 = count2_holds(lhs1, rhs1)
    ct2_e2 = count2_holds(lhs2, rhs2)
    if ct2_e1 and not ct2_e2: separators.append('COUNT2')
    
    return separators

for p in false_problems:
    pid = p['id']
    eq1 = p['equation1']
    eq2 = p['equation2']
    vars1 = get_vars(eq1)
    vars2 = get_vars(eq2)
    nv = max(len(vars1), len(vars2))
    
    # Structural tests
    struct_seps = check_structural(eq1, eq2)
    
    # Magma tests
    magma_seps = []
    for name, table in MAGMAS.items():
        if name in ('T5B', 'NL1') and nv >= 4:
            continue
        e1_holds = check_equation(eq1, table)
        e2_holds = check_equation(eq2, table)
        if e1_holds and not e2_holds:
            magma_seps.append(name)
    
    all_seps = struct_seps + magma_seps
    status = ', '.join(all_seps) if all_seps else '❌ No separator'
    print(f"  {pid}: {status}  ({nv}v)")
    print(f"    eq1: {eq1}")
    print(f"    eq2: {eq2}")
