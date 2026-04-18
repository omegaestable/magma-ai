"""Diagnose hard3 r22 FN problems - TRUE problems predicted FALSE.
These should default to TRUE, so something caused a spurious separation."""
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
            return False, vals
    return True, None

def check_eq_allzeros(eq_str, table):
    parts = eq_str.split('=', 1)
    lhs_str, rhs_str = parts[0].strip(), parts[1].strip()
    variables = sorted(get_vars(lhs_str) | get_vars(rhs_str))
    vals = {v: 0 for v in variables}
    l = eval_expr(lhs_str, vals, table)
    r = eval_expr(rhs_str, vals, table)
    return l == r, l, r

# FN problems from hard3 r22 (TRUE predicted FALSE)
fn_problems = [
    ('hard3_0323', 'x = ((y * z) * y) * (x * y)', 'x = y * (((z * x) * x) * x)', 51.9),
    ('hard3_0176', 'x = ((x * y) * y) * (y * z)', 'x = ((y * (z * z)) * x) * x', 66.2),
    ('hard3_0154', 'x = (y * ((x * y) * y)) * z', 'x = (y * (x * (z * y))) * x', 134.2),
]

for pid, eq1, eq2, time_s in fn_problems:
    vars_eq1 = get_vars(eq1)
    vars_eq2 = get_vars(eq2)
    nv = max(len(vars_eq1), len(vars_eq2))
    print(f"\n{'='*60}")
    print(f"{pid} (gt=TRUE, pred=FALSE, {time_s}s, {nv}v)")
    print(f"  eq1: {eq1}")
    print(f"  eq2: {eq2}")
    
    # Check structural tests
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
    
    tests = {}
    tests['LP'] = (first_letter(lhs1)==first_letter(rhs1), first_letter(lhs2)==first_letter(rhs2))
    tests['RP'] = (last_letter(lhs1)==last_letter(rhs1), last_letter(lhs2)==last_letter(rhs2))
    tests['C0'] = (('*' in lhs1)==('*' in rhs1), ('*' in lhs2)==('*' in rhs2))
    
    print(f"  Structural: LP E1={'H' if tests['LP'][0] else 'F'} E2={'H' if tests['LP'][1] else 'F'} | RP E1={'H' if tests['RP'][0] else 'F'} E2={'H' if tests['RP'][1] else 'F'} | C0 E1={'H' if tests['C0'][0] else 'F'} E2={'H' if tests['C0'][1] else 'F'}")
    
    for sname, (e1h, e2h) in tests.items():
        if e1h and not e2h:
            print(f"  *** SPURIOUS STRUCTURAL SEP on {sname}! (but eq is TRUE)")
    
    # Check magma tests
    for name, table in MAGMAS.items():
        if name in ('T5B', 'NL1') and nv >= 4:
            print(f"  {name}: SKIP (4+ vars)")
            continue
        
        # Default assignment (first-appearance order)
        all_text = eq1 + ' ' + eq2
        seen = []
        for c in all_text:
            if c.isalpha() and c not in seen:
                seen.append(c)
        default_assign = {v: i % 3 for i, v in enumerate(seen)}
        
        # Check E1 with default
        e1_def_holds, e1_def_ce = check_equation_full(eq1, table)
        # Check E1 with all-zeros
        e1_az_holds, e1_az_l, e1_az_r = check_eq_allzeros(eq1, table)
        # Check E2
        e2_def_holds, e2_def_ce = check_equation_full(eq2, table)
        
        print(f"  {name}: E1_full={'HOLD' if e1_def_holds else 'FAIL'} E1_az={'HOLD' if e1_az_holds else f'FAIL({e1_az_l}!={e1_az_r})'} E2_full={'HOLD' if e2_def_holds else 'FAIL'}")
        
        if e1_def_holds and not e2_def_holds:
            print(f"  *** {name} SEPARATES (E1=HOLD, E2=FAIL) — but ground truth is TRUE!")
            print(f"    This means either ground truth is wrong OR our magma check is buggy")
        if e1_def_holds and e1_az_holds and e2_def_holds:
            print(f"    → Both hold, no separation. Model must have made a computation error.")
        if not e1_def_holds:
            print(f"    → E1 fails on this magma, so model should skip to next test.")
        if not e1_az_holds:
            print(f"    → E1 all-zeros fails, model should skip to next test.")
