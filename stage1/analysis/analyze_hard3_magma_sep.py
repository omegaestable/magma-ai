"""
For each hard3 FALSE pair, check all 16 binary operations on {0,1}
to see which magmas provide E1-holds-but-E2-doesn't separation.
Also check all 81 operations on {0,1,2} to assess 3-element separation.
"""
import json, re, itertools

with open("data/benchmark/hard3_balanced40_true20_false20_rotation0002_20260403_185904.jsonl") as f:
    lines = [json.loads(l) for l in f]

false_pairs = [l for l in lines if l["answer"] is False]
true_pairs = [l for l in lines if l["answer"] is True]


def parse_expr(s):
    """Parse an equation expression into a tree. Returns a tree node."""
    s = s.strip()
    # Find the top-level * by tracking parenthesis depth
    depth = 0
    # We need to find a * at depth 0
    # But the expression might be wrapped in outer parens
    
    # Strip outer parentheses if the whole expression is wrapped
    while s.startswith('(') and s.endswith(')'):
        # Check if the outer parens match
        d = 0
        matched = True
        for i, c in enumerate(s):
            if c == '(':
                d += 1
            elif c == ')':
                d -= 1
            if d == 0 and i < len(s) - 1:
                matched = False
                break
        if matched:
            s = s[1:-1].strip()
        else:
            break
    
    # Find top-level *
    depth = 0
    star_pos = -1
    for i, c in enumerate(s):
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
        elif c == '*' and depth == 0:
            star_pos = i
            break  # Take leftmost top-level *
    
    if star_pos == -1:
        # Leaf variable
        return ('var', s.strip())
    else:
        left = s[:star_pos].strip()
        right = s[star_pos+1:].strip()
        return ('op', parse_expr(left), parse_expr(right))


def eval_tree(tree, assignment, op_table, domain_size):
    """Evaluate expression tree with given variable assignment and operation table."""
    if tree[0] == 'var':
        return assignment[tree[1]]
    else:
        left_val = eval_tree(tree[1], assignment, op_table, domain_size)
        right_val = eval_tree(tree[2], assignment, op_table, domain_size)
        return op_table[left_val * domain_size + right_val]


def get_variables(tree):
    """Get set of variables in expression tree."""
    if tree[0] == 'var':
        return {tree[1]}
    else:
        return get_variables(tree[1]) | get_variables(tree[2])


def equation_holds(lhs_tree, rhs_tree, op_table, domain_size):
    """Check if equation holds for ALL assignments over the domain."""
    variables = sorted(get_variables(lhs_tree) | get_variables(rhs_tree))
    for vals in itertools.product(range(domain_size), repeat=len(variables)):
        assignment = dict(zip(variables, vals))
        lhs_val = eval_tree(lhs_tree, assignment, op_table, domain_size)
        rhs_val = eval_tree(rhs_tree, assignment, op_table, domain_size)
        if lhs_val != rhs_val:
            return False
    return True


def check_separation(e1_str, e2_str, op_table, domain_size):
    """Check if E1 holds but E2 doesn't under given magma → separation."""
    e1_parts = e1_str.split('=', 1)
    e2_parts = e2_str.split('=', 1)
    
    e1_lhs = parse_expr(e1_parts[0])
    e1_rhs = parse_expr(e1_parts[1])
    e2_lhs = parse_expr(e2_parts[0])
    e2_rhs = parse_expr(e2_parts[1])
    
    e1_holds = equation_holds(e1_lhs, e1_rhs, op_table, domain_size)
    e2_holds = equation_holds(e2_lhs, e2_rhs, op_table, domain_size)
    
    return e1_holds and not e2_holds


# Generate all 16 binary operations on {0,1}
# op_table[a*2+b] = a*b
ops_2 = list(itertools.product([0, 1], repeat=4))

# Named operations
op_names_2 = {
    (0,0,0,0): "CONST0",
    (0,0,0,1): "AND",
    (0,0,1,0): "GT",  # x>y
    (0,0,1,1): "LEFT",
    (0,1,0,0): "LT",  # x<y
    (0,1,0,1): "RIGHT",
    (0,1,1,0): "XOR",
    (0,1,1,1): "OR",
    (1,0,0,0): "NOR",
    (1,0,0,1): "XNOR",
    (1,0,1,0): "NRIGHT",  # NOT right
    (1,0,1,1): "IMP",  # x >= y (implication)
    (1,1,0,0): "NLEFT",  # NOT left
    (1,1,0,1): "RIMP",  # x <= y (reverse implication)
    (1,1,1,0): "NAND",
    (1,1,1,1): "CONST1",
}

print("=" * 80)
print("HARD3 FALSE PAIRS: 2-ELEMENT MAGMA SEPARATION ANALYSIS")
print("=" * 80)

pair_separators = {}
for p in false_pairs:
    pid = p["id"]
    e1, e2 = p["equation1"], p["equation2"]
    seps = []
    for op in ops_2:
        if check_separation(e1, e2, list(op), 2):
            seps.append(op_names_2.get(op, str(op)))
    pair_separators[pid] = seps
    tag = ", ".join(seps) if seps else "NONE"
    print(f"{pid}: {tag}")

# Summary
sep_counts = {}
for pid, seps in pair_separators.items():
    for s in seps:
        sep_counts[s] = sep_counts.get(s, 0) + 1

print(f"\n{'='*80}")
print("SEPARATOR FREQUENCY (out of {0} FALSE pairs):".format(len(false_pairs)))
print("=" * 80)
for name, count in sorted(sep_counts.items(), key=lambda x: -x[1]):
    print(f"  {name:10s}: {count:2d}/{len(false_pairs)} ({100*count/len(false_pairs):.0f}%)")

unsep = sum(1 for v in pair_separators.values() if not v)
print(f"\nUnseparable by ANY 2-element magma: {unsep}/{len(false_pairs)}")

# Now check TRUE pairs for false positives
print(f"\n{'='*80}")
print("HARD3 TRUE PAIRS: FALSE POSITIVE CHECK (should all be 0)")
print("=" * 80)
fp_counts = {}
for p in true_pairs:
    pid = p["id"]
    e1, e2 = p["equation1"], p["equation2"]
    fps = []
    for op in ops_2:
        if check_separation(e1, e2, list(op), 2):
            fps.append(op_names_2.get(op, str(op)))
    if fps:
        print(f"  FP! {pid}: {', '.join(fps)}")
        for f in fps:
            fp_counts[f] = fp_counts.get(f, 0) + 1

if not fp_counts:
    print("  No false positives on TRUE pairs!")
else:
    print(f"\nFP frequency:")
    for name, count in sorted(fp_counts.items(), key=lambda x: -x[1]):
        print(f"  {name:10s}: {count:2d}/{len(true_pairs)} FP")

print(f"\n{'='*80}")
print("NET VALUE PER MAGMA (catches - FP):")
print("=" * 80)
for name in set(list(sep_counts.keys()) + list(fp_counts.keys())):
    catches = sep_counts.get(name, 0)
    fps = fp_counts.get(name, 0)
    net = catches - fps
    print(f"  {name:10s}: catches={catches:2d} FP={fps:2d} net={net:+d}")
