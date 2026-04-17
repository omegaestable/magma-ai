"""Check the 2 new FN problems: hard3_0257 and hard3_0155."""
import json, itertools

TARGET_IDS = {"hard3_0257", "hard3_0155"}

def parse_tree(s):
    """Parse equation side into a tree. Returns (op, left, right) or variable string."""
    s = s.strip()
    if not s:
        return s
    # Remove outer parens if they match
    if s.startswith('('):
        depth = 0
        for i, c in enumerate(s):
            if c == '(': depth += 1
            elif c == ')': depth -= 1
            if depth == 0:
                if i == len(s) - 1:
                    return parse_tree(s[1:-1])
                break
    # Find top-level *
    depth = 0
    for i, c in enumerate(s):
        if c == '(': depth += 1
        elif c == ')': depth -= 1
        elif c == '*' and depth == 0:
            left = parse_tree(s[:i])
            right = parse_tree(s[i+1:])
            return ('*', left, right)
    return s.strip()

def get_vars(tree):
    if isinstance(tree, str):
        return {tree}
    return get_vars(tree[1]) | get_vars(tree[2])

def eval_tree(tree, assign, table):
    if isinstance(tree, str):
        return assign[tree]
    l = eval_tree(tree[1], assign, table)
    r = eval_tree(tree[2], assign, table)
    return table[l][r]

# Magma tables
T3R = [[1,2,0],[1,2,0],[1,2,0]]   # a*b = next(b)
T3L = [[1,1,1],[2,2,2],[0,0,0]]   # a*b = next(a)
T5B = [[0,2,1],[1,0,2],[2,1,0]]   # a*b = (a+2b)%3
NL1 = [[0,0,0],[1,1,0],[1,2,2]]

MAGMAS = {"T3R": T3R, "T3L": T3L, "T5B": T5B, "NL1": NL1}

def first_letter(s):
    for c in s:
        if c.isalpha(): return c
    return None

def last_letter(s):
    for c in reversed(s):
        if c.isalpha(): return c
    return None

def has_star(s):
    return '*' in s

def check_structural(eq_str):
    """Returns dict of test results (HOLD/FAIL) for one equation."""
    lhs, rhs = eq_str.split('=', 1)
    lhs, rhs = lhs.strip(), rhs.strip()
    results = {}
    # LP
    results['LP'] = 'HOLD' if first_letter(lhs) == first_letter(rhs) else 'FAIL'
    # RP
    results['RP'] = 'HOLD' if last_letter(lhs) == last_letter(rhs) else 'FAIL'
    # C0
    l_star = has_star(lhs)
    r_star = has_star(rhs)
    if l_star and r_star:
        results['C0'] = 'HOLD'
    elif not l_star and not r_star:
        results['C0'] = 'HOLD' if lhs.strip() == rhs.strip() else 'FAIL'
    else:
        results['C0'] = 'FAIL'
    # VARS
    l_vars = set(c for c in lhs if c.isalpha())
    r_vars = set(c for c in rhs if c.isalpha())
    if l_star and r_star:
        results['VARS'] = 'HOLD' if l_vars == r_vars else 'FAIL'
    elif not l_star and not r_star:
        results['VARS'] = 'HOLD' if lhs.strip() == rhs.strip() else 'FAIL'
    else:
        bare = lhs.strip() if not l_star else rhs.strip()
        star_side_vars = r_vars if not l_star else l_vars
        results['VARS'] = 'HOLD' if star_side_vars == {bare} else 'FAIL'
    # COUNT2
    from collections import Counter
    l_counts = Counter(c for c in lhs if c.isalpha())
    r_counts = Counter(c for c in rhs if c.isalpha())
    all_letters = set(l_counts) | set(r_counts)
    count2_hold = all(l_counts.get(v,0) % 2 == r_counts.get(v,0) % 2 for v in all_letters)
    results['COUNT2'] = 'HOLD' if count2_hold else 'FAIL'
    # LDEPTH
    if results['LP'] == 'FAIL':
        results['LDEPTH'] = 'FAIL'
    else:
        def ldepth(s):
            t = parse_tree(s)
            d = 0
            while isinstance(t, tuple):
                d += 1
                t = t[1]  # go left
            return d
        ld_l = ldepth(lhs)
        ld_r = ldepth(rhs)
        results['LDEPTH'] = 'HOLD' if ld_l % 2 == ld_r % 2 else 'FAIL'
    return results

def check_separation(e1_str, e2_str):
    """Check all tests for separation between e1 and e2."""
    e1_tests = check_structural(e1_str)
    e2_tests = check_structural(e2_str)
    
    separators = []
    for test in ['LP', 'RP', 'C0', 'VARS', 'COUNT2', 'LDEPTH']:
        if e1_tests[test] == 'HOLD' and e2_tests[test] == 'FAIL':
            separators.append(test)
    
    # Parse equations
    e1_lhs_str, e1_rhs_str = e1_str.split('=', 1)
    e2_lhs_str, e2_rhs_str = e2_str.split('=', 1)
    e1_lhs = parse_tree(e1_lhs_str.strip())
    e1_rhs = parse_tree(e1_rhs_str.strip())
    e2_lhs = parse_tree(e2_lhs_str.strip())
    e2_rhs = parse_tree(e2_rhs_str.strip())
    
    all_vars = sorted(get_vars(e1_lhs) | get_vars(e1_rhs) | get_vars(e2_lhs) | get_vars(e2_rhs))
    n_vars = len(all_vars)
    
    # Variable assignment: first appearance order
    assign_default = {}
    counter = 0
    for v in all_vars:
        # First appearance in E1 then E2
        pass
    # Use first-appearance across both equations as in the cheatsheet
    seen = []
    for c in e1_str + e2_str:
        if c.isalpha() and c not in seen:
            seen.append(c)
    for i, v in enumerate(seen):
        assign_default[v] = i % 3  # wraps: 0,1,2,0,1,...
    
    # Check magma tests
    for name, table in MAGMAS.items():
        if name in ('T5B', 'NL1') and n_vars >= 4:
            print(f"    {name}: SKIPPED (4+ vars)")
            continue
        
        # Default assignment check
        try:
            e1_l_val = eval_tree(e1_lhs, assign_default, table)
            e1_r_val = eval_tree(e1_rhs, assign_default, table)
        except:
            print(f"    {name}: ERROR evaluating E1")
            continue
            
        if e1_l_val != e1_r_val:
            print(f"    {name}: E1 FAILS (default) {e1_l_val}≠{e1_r_val} → skip")
            continue
        
        # All-zeros check
        assign_zeros = {v: 0 for v in all_vars}
        e1_l_z = eval_tree(e1_lhs, assign_zeros, table)
        e1_r_z = eval_tree(e1_rhs, assign_zeros, table)
        if e1_l_z != e1_r_z:
            print(f"    {name}: E1 FAILS (all-zeros) {e1_l_z}≠{e1_r_z} → skip")
            continue
        
        # E2 check
        e2_l_val = eval_tree(e2_lhs, assign_default, table)
        e2_r_val = eval_tree(e2_rhs, assign_default, table)
        if e2_l_val != e2_r_val:
            separators.append(name)
            print(f"    {name}: E1 match, E2 mismatch {e2_l_val}≠{e2_r_val} → SEPARATION")
        else:
            print(f"    {name}: E1 match, E2 match → no sep")
    
    return separators

with open('data/benchmark/hard3_balanced30_true15_false15_rotation0022_20260417_145804.jsonl') as f:
    for line in f:
        d = json.loads(line)
        if d['id'] in TARGET_IDS:
            pid = d['id']
            gt = d['answer']
            e1 = d['equation1']
            e2 = d['equation2']
            
            all_vars_list = []
            for c in e1 + ' ' + e2:
                if c.isalpha() and c not in all_vars_list:
                    all_vars_list.append(c)
            
            print(f"{'='*60}")
            print(f"{pid}  gt={gt}  vars={len(all_vars_list)} ({','.join(all_vars_list)})")
            print(f"  E1: {e1}")
            print(f"  E2: {e2}")
            print()
            
            e1_tests = check_structural(e1)
            e2_tests = check_structural(e2)
            print(f"  Structural tests:")
            for test in ['LP', 'RP', 'C0', 'VARS', 'COUNT2', 'LDEPTH']:
                sep = "SEP!" if e1_tests[test]=='HOLD' and e2_tests[test]=='FAIL' else ""
                print(f"    {test}: E1={e1_tests[test]} E2={e2_tests[test]} {sep}")
            
            print(f"  Magma tests:")
            seps = check_separation(e1, e2)
            
            if seps:
                print(f"\n  SEPARATORS: {seps}")
                print(f"  → This is an execution error if gt=T (tests shouldn't fire)")
            else:
                print(f"\n  NO SEPARATORS found")
                if gt:
                    print(f"  → Correct: no test should say FALSE. Model FN is execution error.")
                else:
                    print(f"  → Structural ceiling: tests can't detect this FALSE pair.")
            print()
