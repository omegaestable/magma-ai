"""Explore potential new structural tests for hard2 FALSE problems.

Tests various structural properties to see which could separate hard2 FALSE pairs.
"""

def parse_tree(s):
    """Parse expression into tree. Returns ('var', name) or ('*', left, right)."""
    s = s.strip()
    # Find the main * operator (not inside parens)
    depth = 0
    for i in range(len(s)):
        if s[i] == '(':
            depth += 1
        elif s[i] == ')':
            depth -= 1
        elif s[i] == '*' and depth == 0:
            left = parse_tree(s[:i])
            right = parse_tree(s[i+1:])
            return ('*', left, right)
    # Strip outer parens
    if s.startswith('(') and s.endswith(')'):
        return parse_tree(s[1:-1])
    # Must be a variable
    return ('var', s.strip())

def tree_depth(t):
    """Max depth of parse tree."""
    if t[0] == 'var':
        return 0
    return 1 + max(tree_depth(t[1]), tree_depth(t[2]))

def left_depth(t):
    """Depth following left branch only."""
    if t[0] == 'var':
        return 0
    return 1 + left_depth(t[1])

def right_depth(t):
    """Depth following right branch only."""
    if t[0] == 'var':
        return 0
    return 1 + right_depth(t[2])

def op_count(t):
    """Total * operations."""
    if t[0] == 'var':
        return 0
    return 1 + op_count(t[1]) + op_count(t[2])

def leaf_count(t):
    """Total variable occurrences (leaves)."""
    if t[0] == 'var':
        return 1
    return leaf_count(t[1]) + leaf_count(t[2])

def get_vars(t):
    """Get variables used."""
    if t[0] == 'var':
        return {t[1]}
    return get_vars(t[1]) | get_vars(t[2])

def rightmost_var(t):
    """Rightmost leaf variable."""
    if t[0] == 'var':
        return t[1]
    return rightmost_var(t[2])

def leftmost_var(t):
    """Leftmost leaf variable."""
    if t[0] == 'var':
        return t[1]
    return leftmost_var(t[1])

def left_count(t, var):
    """Count how many times var appears in left children."""
    if t[0] == 'var':
        return 0
    left_has = var_count_tree(t[1], var)
    right_has = left_count(t[2], var)
    return left_has + right_has

def var_count_tree(t, var):
    """Count occurrences of var in tree."""
    if t[0] == 'var':
        return 1 if t[1] == var else 0
    return var_count_tree(t[1], var) + var_count_tree(t[2], var)

def right_left_balance(t):
    """Ratio of right subtree depth to left subtree depth."""
    if t[0] == 'var':
        return 0
    return right_depth(t) - left_depth(t)

def compute_features(expr):
    """Compute all structural features for an expression."""
    tree = parse_tree(expr)
    return {
        'depth': tree_depth(tree),
        'ldepth': left_depth(tree),
        'rdepth': right_depth(tree),
        'ops': op_count(tree),
        'leaves': leaf_count(tree),
        'nvars': len(get_vars(tree)),
        'lvar': leftmost_var(tree),
        'rvar': rightmost_var(tree),
        'balance': right_left_balance(tree),
    }

# Hard2 FP problems (FALSE but predicted TRUE — no separator in our suite)
fp_problems = [
    ('hard2_0182', 'x = (y * x) * (y * (x * x))', 'x * y = ((x * y) * x) * y'),
    ('hard2_0150', 'x = (x * y) * ((y * x) * y)', 'x * y = (x * (y * x)) * y'),
    ('hard2_0122', 'x = (y * (x * x)) * (y * x)', 'x * y = (x * (y * x)) * y'),
    ('hard2_0014', 'x = ((x * y) * x) * (y * x)', 'x * y = ((x * z) * x) * y'),
    ('hard2_0105', 'x = y * ((y * (y * x)) * x)', 'x * (x * y) = y * (x * y)'),
    ('hard2_0051', 'x = (y * ((y * x) * x)) * y', 'x * (x * y) = z * (z * y)'),
    ('hard2_0045', 'x * x = ((y * z) * w) * u', 'x * y = x * ((x * z) * y)'),
    ('hard2_0167', 'x = (x * ((y * x) * y)) * y', 'x * y = x * ((y * x) * z)'),
    ('hard2_0076', '(x * y) * x = (z * w) * u', 'x * (x * y) = (z * w) * z'),
    # Remaining from rotation:
    ('hard2_0194', 'x = (y * ((y * x) * x)) * y', 'x = (y * (x * (y * x))) * y'),
    ('hard2_0196', 'x = (y * ((y * x) * x)) * y', 'x = x * ((y * y) * (z * y))'),
    ('hard2_0139', 'x = (x * y) * ((z * w) * x)', 'x * y = ((x * z) * x) * y'),
]

# Also include TRUE NEGATIVES (correctly identified FALSE)
tn_problems = [
    ('hard2_0192', 'x = y * (y * (x * (x * y)))', 'x * y = (z * x) * (z * y)'),
    ('hard2_0090', 'x = ((x * y) * x) * (y * x)', 'x * y = (y * (x * y)) * x'),
]

print("=== Looking for structural tests that can separate hard2 FALSE problems ===\n")

# Test each potential structural feature as a SEPARATION test
# For it to work: E1 must have the property, E2 must NOT (or vice versa)
print("Feature analysis per problem:\n")

for pid, eq1, eq2 in fp_problems + tn_problems:
    lhs1, rhs1 = eq1.split('=', 1)
    lhs2, rhs2 = eq2.split('=', 1)
    
    f_lhs1 = compute_features(lhs1)
    f_rhs1 = compute_features(rhs1)
    f_lhs2 = compute_features(lhs2)
    f_rhs2 = compute_features(rhs2)
    
    # Test: depth parity of LHS (left side of equation)
    dp_e1 = f_lhs1['depth'] % 2 == f_rhs1['depth'] % 2
    dp_e2 = f_lhs2['depth'] % 2 == f_rhs2['depth'] % 2
    
    # Test: rdepth parity
    rd_e1 = f_lhs1['rdepth'] % 2 == f_rhs1['rdepth'] % 2
    rd_e2 = f_lhs2['rdepth'] % 2 == f_rhs2['rdepth'] % 2
    
    # Test: op count mod 2
    oc_e1 = f_lhs1['ops'] % 2 == f_rhs1['ops'] % 2
    oc_e2 = f_lhs2['ops'] % 2 == f_rhs2['ops'] % 2
    
    # Test: leaf count mod 2 (same as COUNT2 for each var, but total)
    lc_e1 = f_lhs1['leaves'] % 2 == f_rhs1['leaves'] % 2
    lc_e2 = f_lhs2['leaves'] % 2 == f_rhs2['leaves'] % 2
    
    # Test: op count mod 3
    oc3_e1 = f_lhs1['ops'] % 3 == f_rhs1['ops'] % 3
    oc3_e2 = f_lhs2['ops'] % 3 == f_rhs2['ops'] % 3
    
    # Test: balance difference
    bal_e1 = f_lhs1['balance'] == f_rhs1['balance']
    bal_e2 = f_lhs2['balance'] == f_rhs2['balance']
    
    # Test: depth mod 3
    d3_e1 = f_lhs1['depth'] % 3 == f_rhs1['depth'] % 3
    d3_e2 = f_lhs2['depth'] % 3 == f_rhs2['depth'] % 3
    
    # Test: rdepth mod 3
    rd3_e1 = f_lhs1['rdepth'] % 3 == f_rhs1['rdepth'] % 3
    rd3_e2 = f_lhs2['rdepth'] % 3 == f_rhs2['rdepth'] % 3
    
    separators = []
    for test_name, e1_hold, e2_hold in [
        ('depth%2', dp_e1, dp_e2),
        ('rdepth%2', rd_e1, rd_e2),
        ('ops%2', oc_e1, oc_e2),
        ('leaves%2', lc_e1, lc_e2),
        ('ops%3', oc3_e1, oc3_e2),
        ('balance', bal_e1, bal_e2),
        ('depth%3', d3_e1, d3_e2),
        ('rdepth%3', rd3_e1, rd3_e2),
    ]:
        if e1_hold and not e2_hold:
            separators.append(test_name)
    
    is_tn = pid in ('hard2_0192', 'hard2_0090')
    label = "TN" if is_tn else "FP"
    sep_str = ', '.join(separators) if separators else '❌ None'
    print(f"  {pid} [{label}]: {sep_str}")
    if separators:
        print(f"    eq1: {eq1}")
        print(f"    eq2: {eq2}")
        for test_name, e1_hold, e2_hold in [
            ('depth%2', dp_e1, dp_e2),
            ('rdepth%2', rd_e1, rd_e2),
            ('ops%2', oc_e1, oc_e2),
            ('leaves%2', lc_e1, lc_e2),
            ('ops%3', oc3_e1, oc3_e2),
            ('balance', bal_e1, bal_e2),
            ('depth%3', d3_e1, d3_e2),
            ('rdepth%3', rd3_e1, rd3_e2),
        ]:
            if e1_hold and not e2_hold:
                print(f"      {test_name}: E1=HOLD E2=FAIL → separation!")

print("\n\n=== Safety check: do these tests cause FN on TRUE problems? ===\n")

# Check the TRUE problems from rot22
true_problems = [
    ('hard2_0126', 'x = (y * ((x * x) * y)) * x', 'x = (((y * z) * w) * x) * x'),
    ('hard2_0005', 'x = (y * (x * x)) * (x * y)', 'x = (y * ((y * x) * y)) * x'),
    ('hard2_0127', 'x = y * (z * ((y * x) * y))', 'x = (y * (x * (z * x))) * x'),
    ('hard2_0110', 'x = (y * z) * (w * (x * x))', 'x = y * (((x * z) * x) * w)'),
    ('hard2_0097', 'x = y * (((x * z) * x) * w)', 'x = y * ((z * x) * (w * x))'),
    ('hard2_0140', 'x = (y * (y * (x * z))) * x', 'x = (y * z) * ((w * x) * x)'),
    ('hard2_0086', 'x = ((y * z) * w) * (x * x)', 'x = y * ((z * (w * x)) * x)'),
    ('hard2_0022', 'x = y * (((x * y) * z) * w)', 'x = (y * ((x * x) * y)) * x'),
    ('hard2_0121', 'x = y * (z * ((y * x) * y))', 'x = x * (((y * y) * x) * z)'),
]

for test_name_global in ['depth%2', 'rdepth%2', 'ops%2', 'leaves%2', 'ops%3', 'balance', 'depth%3', 'rdepth%3']:
    fn_count = 0
    for pid, eq1, eq2 in true_problems:
        lhs1, rhs1 = eq1.split('=', 1)
        lhs2, rhs2 = eq2.split('=', 1)
        f_lhs1 = compute_features(lhs1)
        f_rhs1 = compute_features(rhs1)
        f_lhs2 = compute_features(lhs2)
        f_rhs2 = compute_features(rhs2)
        
        if test_name_global == 'depth%2':
            e1h = f_lhs1['depth'] % 2 == f_rhs1['depth'] % 2
            e2h = f_lhs2['depth'] % 2 == f_rhs2['depth'] % 2
        elif test_name_global == 'rdepth%2':
            e1h = f_lhs1['rdepth'] % 2 == f_rhs1['rdepth'] % 2
            e2h = f_lhs2['rdepth'] % 2 == f_rhs2['rdepth'] % 2
        elif test_name_global == 'ops%2':
            e1h = f_lhs1['ops'] % 2 == f_rhs1['ops'] % 2
            e2h = f_lhs2['ops'] % 2 == f_rhs2['ops'] % 2
        elif test_name_global == 'leaves%2':
            e1h = f_lhs1['leaves'] % 2 == f_rhs1['leaves'] % 2
            e2h = f_lhs2['leaves'] % 2 == f_rhs2['leaves'] % 2
        elif test_name_global == 'ops%3':
            e1h = f_lhs1['ops'] % 3 == f_rhs1['ops'] % 3
            e2h = f_lhs2['ops'] % 3 == f_rhs2['ops'] % 3
        elif test_name_global == 'balance':
            e1h = f_lhs1['balance'] == f_rhs1['balance']
            e2h = f_lhs2['balance'] == f_rhs2['balance']
        elif test_name_global == 'depth%3':
            e1h = f_lhs1['depth'] % 3 == f_rhs1['depth'] % 3
            e2h = f_lhs2['depth'] % 3 == f_rhs2['depth'] % 3
        elif test_name_global == 'rdepth%3':
            e1h = f_lhs1['rdepth'] % 3 == f_rhs1['rdepth'] % 3
            e2h = f_lhs2['rdepth'] % 3 == f_rhs2['rdepth'] % 3
        
        if e1h and not e2h:
            fn_count += 1
    
    print(f"  {test_name_global:12s}: would cause {fn_count}/{len(true_problems)} FN on hard2 TRUE r22")
