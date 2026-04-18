"""Check which remaining FALSE problems have separators in v28c's test suite."""
import itertools

# v28c magma tests (3-element tables, 0-indexed)
MAGMAS = {
    'T3R': [[0,2,0],[1,1,2],[1,0,0]],
    'T3L': [[0,1,1],[2,1,0],[0,2,0]],
    'T5B': [[0,0,0],[1,1,2],[0,2,1]],
    'NL1': [[0,2,2],[2,1,0],[1,0,0]],
}

def eval_expr(expr, vals, table, size=3):
    """Evaluate expression in magma."""
    if expr.isalpha() and len(expr) == 1:
        return vals[expr]
    # Find the main operator
    depth = 0
    for i in range(len(expr)):
        if expr[i] == '(':
            depth += 1
        elif expr[i] == ')':
            depth -= 1
        elif expr[i] == '*' and depth == 0:
            left = eval_expr(expr[:i].strip(), vals, table, size)
            right = eval_expr(expr[i+1:].strip(), vals, table, size)
            return table[left][right]
    # Strip outer parens
    if expr.startswith('(') and expr.endswith(')'):
        return eval_expr(expr[1:-1].strip(), vals, table, size)
    raise ValueError(f"Cannot parse: {expr}")

def parse_equation(eq_str):
    """Parse 'lhs = rhs' into (lhs, rhs)."""
    parts = eq_str.split('=', 1)
    return parts[0].strip(), parts[1].strip()

def get_vars(expr):
    """Get variables from expression."""
    return set(c for c in expr if c.isalpha())

def check_equation(eq_str, table, size=3):
    """Check if equation holds for all assignments in given magma."""
    lhs_str, rhs_str = parse_equation(eq_str)
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

# Remaining FALSE problems from r22
false_remaining = [
    ('hard2_0105', 'x = y * ((y * (y * x)) * x)', 'x * (x * y) = y * (x * y)'),
    ('hard2_0051', 'x = (y * ((y * x) * x)) * y', 'x * (x * y) = z * (z * y)'),
    ('hard2_0045', 'x * x = ((y * z) * w) * u', 'x * y = x * ((x * z) * y)'),
    ('hard2_0167', 'x = (x * ((y * x) * y)) * y', 'x * y = x * ((y * x) * z)'),
    ('hard2_0076', '(x * y) * x = (z * w) * u', 'x * (x * y) = (z * w) * z'),
    ('hard2_0194', 'x = (y * ((y * x) * x)) * y', 'x = (y * (x * (y * x))) * y'),
    ('hard2_0125', 'x = ((x * (y * z)) * z) * x', 'x = ((x * x) * (y * y)) * x'),
    ('hard2_0196', 'x = (y * ((y * x) * x)) * y', 'x = x * ((y * y) * (z * y))'),
    ('hard2_0139', 'x = (x * y) * ((z * w) * x)', 'x * y = ((x * z) * x) * y'),
]

print("Remaining FALSE problems — separator check\n")
for pid, eq1, eq2 in false_remaining:
    vars1 = get_vars(eq1.split('=')[0]) | get_vars(eq1.split('=')[1])
    vars2 = get_vars(eq2.split('=')[0]) | get_vars(eq2.split('=')[1])
    nv1 = len(vars1)
    nv2 = len(vars2)
    separators = []
    for name, table in MAGMAS.items():
        # Check skip condition (4+ vars)
        skip_str = ""
        if name in ('T5B', 'NL1') and (nv1 >= 4 or nv2 >= 4):
            skip_str = " [SKIP: 4+vars]"
        e1_holds = check_equation(eq1, table)
        e2_holds = check_equation(eq2, table)
        if e1_holds and not e2_holds:
            separators.append(f"{name}(eq1✓eq2✗){skip_str}")
        elif not e1_holds and e2_holds:
            separators.append(f"{name}(eq1✗eq2✓){skip_str}")
    
    status = ', '.join(separators) if separators else '❌ No separator'
    print(f"  {pid}: {status}")
    print(f"    eq1 ({nv1}v): {eq1}")
    print(f"    eq2 ({nv2}v): {eq2}")
    print()

# Also check with all-zeros substitution
print("\n--- All-zeros dual check ---")
for pid, eq1, eq2 in false_remaining:
    for name, table in MAGMAS.items():
        vars1 = get_vars(eq1.split('=')[0]) | get_vars(eq1.split('=')[1])
        vars2 = get_vars(eq2.split('=')[0]) | get_vars(eq2.split('=')[1])
        nv = max(len(vars1), len(vars2))
        if name in ('T5B', 'NL1') and nv >= 4:
            continue
        # All-zeros check: set all vars to 0
        vals = {v: 0 for v in sorted(vars1 | vars2)}
        try:
            lhs1, rhs1 = parse_equation(eq1)
            lhs2, rhs2 = parse_equation(eq2)
            e1_az = eval_expr(lhs1, vals, table) == eval_expr(rhs1, vals, table)
            e2_az = eval_expr(lhs2, vals, table) == eval_expr(rhs2, vals, table)
            # Full check
            e1_full = check_equation(eq1, table)
            e2_full = check_equation(eq2, table)
            
            # Separation = e1 holds but e2 doesn't (in either default or all-zeros)
            # Default assigns all vars to distinct values 0,1,2,...
            if e1_az and not e2_az and not (e1_full and not e2_full):
                print(f"  {pid}: {name} separates on ALL-ZEROS only (eq1_az={e1_az}, eq2_az={e2_az})")
        except:
            pass
