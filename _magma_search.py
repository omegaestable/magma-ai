"""Search for small magmas satisfying E1076, E917, E73 (the hard cluster targets)."""
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

def check_eq(parsed, table):
    lhs, rhs = parsed
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

def find_failing(parsed, table):
    lhs, rhs = parsed
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

# Parse key equations
key_ids = [4, 63, 73, 99, 206, 255, 450, 650, 854, 917, 1076, 1119, 1289, 1312, 1648, 1729]
parsed_eqs = {eid: parse_eq(eqs[eid - 1]) for eid in key_ids}

# Search size-2 magmas for E1076
print("=== Searching size-2 magmas satisfying E1076 ===")
e1076 = parsed_eqs[1076]
count = 0
for table in itertools.product(range(2), repeat=4):
    t = [list(table[i*2:(i+1)*2]) for i in range(2)]
    if check_eq(e1076, t):
        count += 1
        # Check which other key eqs this magma satisfies
        sats = [eid for eid in key_ids if check_eq(parsed_eqs[eid], t)]
        print(f"  Table {t}: satisfies {sats}")
print(f"  Total: {count} magmas")

# Search size-3 magmas for E1076
print("\n=== Searching size-3 magmas satisfying E1076 ===")
count = 0
found = []
for table_flat in itertools.product(range(3), repeat=9):
    t = [list(table_flat[i*3:(i+1)*3]) for i in range(3)]
    if check_eq(e1076, t):
        count += 1
        if count <= 5:
            sats = [eid for eid in key_ids if check_eq(parsed_eqs[eid], t)]
            refs = [eid for eid in key_ids if not check_eq(parsed_eqs[eid], t)]
            print(f"  Table {t}: satisfies E{sats} refutes E{refs}")
            found.append(t)
print(f"  Total: {count} size-3 magmas satisfying E1076")

# Search size-2 magmas for E917 (Hardy-Ramanujan)
print("\n=== Checking which size-2 magmas satisfy E917 ===")
e917 = parsed_eqs[917]
for table in itertools.product(range(2), repeat=4):
    t = [list(table[i*2:(i+1)*2]) for i in range(2)]
    if check_eq(e917, t):
        sats = [eid for eid in key_ids if check_eq(parsed_eqs[eid], t)]
        refs = [eid for eid in key_ids if not check_eq(parsed_eqs[eid], t)]
        print(f"  Table {t}: satisfies E{sats} refutes E{refs}")

# For E1076 found magmas, check which refute E99 (key hard pair E1076->E99)
if found:
    print("\n=== E1076 satisfying magma details ===")
    t = found[0]
    e99 = parsed_eqs[99]
    print(f"Table: {t}")
    print(f"  E1076 satisfied: {check_eq(e1076, t)}")
    print(f"  E99 satisfied: {check_eq(e99, t)}")
    if not check_eq(e99, t):
        fail = find_failing(e99, t)
        if fail:
            asgn, l, r = fail
            print(f"  E99 fails at {asgn}: LHS={l}, RHS={r}")

# Also search for the "best" size-3 CE that covers E1076 but refutes the most
print("\n=== Best E1076-satisfying size-3 magma (max refutations) ===")
best_table = None
best_refs = 0
for table_flat in itertools.product(range(3), repeat=9):
    t = [list(table_flat[i*3:(i+1)*3]) for i in range(3)]
    if not check_eq(e1076, t):
        continue
    refs = sum(1 for eid in key_ids if eid != 1076 and not check_eq(parsed_eqs[eid], t))
    if refs > best_refs:
        best_refs = refs
        best_table = [row[:] for row in t]
if best_table:
    sats = [eid for eid in key_ids if check_eq(parsed_eqs[eid], best_table)]
    refs = [eid for eid in key_ids if not check_eq(parsed_eqs[eid], best_table)]
    print(f"  Best table: {best_table}")
    print(f"  Satisfies: E{sats}")
    print(f"  Refutes: E{refs}")
    # Show failing substitution for each refuted eq
    for eid in refs[:5]:
        fail = find_failing(parsed_eqs[eid], best_table)
        if fail:
            asgn, l, r = fail
            print(f"  E{eid} fails at {asgn}: LHS={l}, RHS={r}")
