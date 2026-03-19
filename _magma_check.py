"""Temporary script: check which key equations each canonical magma satisfies."""
import itertools

def _find_matching(s, start):
    depth = 0
    for i in range(start, len(s)):
        if s[i] == '(':
            depth += 1
        elif s[i] == ')':
            depth -= 1
            if depth == 0:
                return i
    return -1

def _parse_expr(s):
    s = s.strip()
    if s.startswith('(') and _find_matching(s, 0) == len(s) - 1:
        s = s[1:-1].strip()
    depth = 0
    last_star = -1
    for i, c in enumerate(s):
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
        elif c == '*' and depth == 0:
            last_star = i
    if last_star >= 0:
        left = s[:last_star].strip()
        right = s[last_star + 1:].strip()
        return ('*', _parse_expr(left), _parse_expr(right))
    return ('var', s)

def parse_eq(s):
    s = s.replace('\u25c7', '*').strip()
    lhs, rhs = s.split('=', 1)
    return (_parse_expr(lhs.strip()), _parse_expr(rhs.strip()))

def _collect_vars(tree, vs):
    if tree[0] == 'var':
        vs.add(tree[1])
    else:
        _collect_vars(tree[1], vs)
        _collect_vars(tree[2], vs)

def eval_tree(tree, assignment, table):
    if tree[0] == 'var':
        return assignment[tree[1]]
    left = eval_tree(tree[1], assignment, table)
    right = eval_tree(tree[2], assignment, table)
    return table[left][right]

def check_eq(eq_str, table):
    lhs, rhs = parse_eq(eq_str)
    n = len(table)
    vs = set()
    _collect_vars(lhs, vs)
    _collect_vars(rhs, vs)
    vs = sorted(vs)
    for vals in itertools.product(range(n), repeat=len(vs)):
        assignment = dict(zip(vs, vals))
        if eval_tree(lhs, assignment, table) != eval_tree(rhs, assignment, table):
            return False
    return True

def find_failing(eq_str, table):
    """Find first failing assignment for an equation on a magma."""
    lhs, rhs = parse_eq(eq_str)
    n = len(table)
    vs = set()
    _collect_vars(lhs, vs)
    _collect_vars(rhs, vs)
    vs = sorted(vs)
    for vals in itertools.product(range(n), repeat=len(vs)):
        assignment = dict(zip(vs, vals))
        l = eval_tree(lhs, assignment, table)
        r = eval_tree(rhs, assignment, table)
        if l != r:
            return assignment, l, r
    return None

# Read equations
with open('data/exports/equations.txt', encoding='utf-8') as f:
    eqs = [line.strip() for line in f]

key_ids = [4, 63, 73, 99, 206, 255, 450, 650, 677, 854, 917, 1076, 1119, 1289, 1312, 1648, 1729]
key_eqs = {eid: eqs[eid - 1] for eid in key_ids}

magmas = {
    'LP':  [[0, 0], [1, 1]],
    'RP':  [[0, 1], [0, 1]],
    'C0':  [[0, 0], [0, 0]],
    'XOR': [[0, 1], [1, 0]],
    'Z3A': [[0, 1, 2], [1, 2, 0], [2, 0, 1]],
}

print("=== Equation Satisfaction Matrix ===")
header = f"{'Eq':>6}"
for m in magmas:
    header += f"  {m:>4}"
print(header)

for eid in key_ids:
    etxt = key_eqs[eid]
    row = f"E{eid:>4}"
    for mname, table in magmas.items():
        sat = check_eq(etxt, table)
        row += f"  {'  T' if sat else '  F':>4}"
    row += f"  {etxt}"
    print(row)

# Now for each magma, print which equations it satisfies and refutes
print("\n=== Per-Magma Summary ===")
for mname, table in magmas.items():
    sat_list = []
    ref_list = []
    for eid in key_ids:
        if check_eq(key_eqs[eid], table):
            sat_list.append(f"E{eid}")
        else:
            ref_list.append(f"E{eid}")
    print(f"\n{mname} (size {len(table)}):")
    print(f"  Satisfies: {', '.join(sat_list)}")
    print(f"  Refutes:   {', '.join(ref_list)}")

# Find useful counterexample pairs: E1 satisfied, E2 refuted
print("\n=== Useful CE Pairs (E1 sat, E2 ref) per Magma ===")
for mname, table in magmas.items():
    pairs = []
    for e1 in key_ids:
        if not check_eq(key_eqs[e1], table):
            continue
        for e2 in key_ids:
            if e1 == e2:
                continue
            if not check_eq(key_eqs[e2], table):
                fail = find_failing(key_eqs[e2], table)
                if fail:
                    asgn, lval, rval = fail
                    asgn_str = ','.join(f"{k}={v}" for k, v in asgn.items())
                    pairs.append(f"  E{e1} -> E{e2}: FALSE (CE: {mname} at {asgn_str}, LHS={lval}, RHS={rval})")
    if pairs:
        print(f"\n{mname}:")
        for p in pairs[:15]:  # Limit output
            print(p)
        if len(pairs) > 15:
            print(f"  ... and {len(pairs)-15} more")
