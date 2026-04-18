"""Diagnose hard3 r22 FN with CORRECT equations from JSONL."""
import itertools

MAGMAS = {
    'T3R': [[0,2,0],[1,1,2],[1,0,0]],
    'T3L': [[0,1,1],[2,1,0],[0,2,0]],
    'T5B': [[0,0,0],[1,1,2],[0,2,1]],
    'NL1': [[0,0,0],[1,1,0],[1,2,2]],
}

def eval_expr(expr, vals, table):
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
            left = eval_expr(expr[:i], vals, table)
            right = eval_expr(expr[i+1:], vals, table)
            return table[left][right]
    if expr.startswith('(') and expr.endswith(')'):
        return eval_expr(expr[1:-1], vals, table)
    raise ValueError(f"Cannot parse: {expr}")

def get_vars(expr):
    return set(c for c in expr if c.isalpha())

def check_equation_full(eq_str, table, size=3):
    parts = eq_str.split('=', 1)
    lhs_str, rhs_str = parts[0].strip(), parts[1].strip()
    variables = sorted(get_vars(lhs_str) | get_vars(rhs_str))
    for assignment in itertools.product(range(size), repeat=len(variables)):
        vals = dict(zip(variables, assignment))
        l = eval_expr(lhs_str, vals, table)
        r = eval_expr(rhs_str, vals, table)
        if l != r:
            return False
    return True

# CORRECT equations from JSONL
fn_problems = [
    ('hard3_0323', 'x = ((y * (z * w)) * z) * x', 'x = x * (x * (y * (y * x)))'),
    ('hard3_0176', 'x = (y * z) * (y * (x * z))', 'x = (y * ((y * y) * x)) * y'),
    ('hard3_0154', 'x = y * (((x * x) * z) * x)', 'x * y = z * (y * (x * y))'),
]

for pid, eq1, eq2 in fn_problems:
    nv1 = len(get_vars(eq1))
    nv2 = len(get_vars(eq2))
    nv = max(nv1, nv2)
    print(f"\n{'='*60}")
    print(f"{pid} (gt=TRUE, pred=FALSE, {nv}v)")
    print(f"  eq1 ({nv1}v): {eq1}")
    print(f"  eq2 ({nv2}v): {eq2}")
    
    lhs1, rhs1 = eq1.split('=', 1)
    lhs2, rhs2 = eq2.split('=', 1)
    lhs1, rhs1 = lhs1.strip(), rhs1.strip()
    lhs2, rhs2 = lhs2.strip(), rhs2.strip()
    
    def first_letter(s):
        for c in s:
            if c.isalpha(): return c
        return None
    def last_letter(s):
        for c in reversed(s):
            if c.isalpha(): return c
        return None
    
    fl1l, fl1r = first_letter(lhs1), first_letter(rhs1)
    fl2l, fl2r = first_letter(lhs2), first_letter(rhs2)
    ll1l, ll1r = last_letter(lhs1), last_letter(rhs1)
    ll2l, ll2r = last_letter(lhs2), last_letter(rhs2)
    
    lp_e1 = fl1l == fl1r
    lp_e2 = fl2l == fl2r
    rp_e1 = ll1l == ll1r
    rp_e2 = ll2l == ll2r
    c0_e1 = ('*' in lhs1) == ('*' in rhs1)
    c0_e2 = ('*' in lhs2) == ('*' in rhs2)
    
    print(f"  LP: E1 {fl1l}→{fl1r} {'H' if lp_e1 else 'F'} | E2 {fl2l}→{fl2r} {'H' if lp_e2 else 'F'} → {'SEP!' if lp_e1 and not lp_e2 else 'no sep'}")
    print(f"  RP: E1 {ll1l}→{ll1r} {'H' if rp_e1 else 'F'} | E2 {ll2l}→{ll2r} {'H' if rp_e2 else 'F'} → {'SEP!' if rp_e1 and not rp_e2 else 'no sep'}")
    print(f"  C0: E1 {'H' if c0_e1 else 'F'} | E2 {'H' if c0_e2 else 'F'} → {'SEP!' if c0_e1 and not c0_e2 else 'no sep'}")
    
    for name, table in MAGMAS.items():
        if name in ('T5B', 'NL1') and nv >= 4:
            print(f"  {name}: SKIP (4+ vars)")
            continue
        e1_holds = check_equation_full(eq1, table)
        e2_holds = check_equation_full(eq2, table)
        print(f"  {name}: E1={'HOLD' if e1_holds else 'FAIL'}, E2={'HOLD' if e2_holds else 'FAIL'} → {'SEP!' if e1_holds and not e2_holds else 'no sep'}")
    
    print(f"  → No test should separate, model should say TRUE. This is an EXECUTION ERROR.")
