"""Verify unsoundness: check if exhaustive E1 verification eliminates false separations on TRUE problems."""
import json, itertools

def parse_tree(s):
    s = s.strip()
    if not s: return s
    if s.startswith('('):
        depth = 0
        for i, c in enumerate(s):
            if c == '(': depth += 1
            elif c == ')': depth -= 1
            if depth == 0:
                if i == len(s) - 1: return parse_tree(s[1:-1])
                break
    depth = 0
    for i, c in enumerate(s):
        if c == '(': depth += 1
        elif c == ')': depth -= 1
        elif c == '*' and depth == 0:
            return ('*', parse_tree(s[:i]), parse_tree(s[i+1:]))
    return s.strip()

def get_vars(tree):
    if isinstance(tree, str): return {tree}
    return get_vars(tree[1]) | get_vars(tree[2])

def eval_tree(tree, assign, table):
    if isinstance(tree, str): return assign[tree]
    l = eval_tree(tree[1], assign, table)
    r = eval_tree(tree[2], assign, table)
    return table[l][r]

T3R = [[1,2,0],[1,2,0],[1,2,0]]
T3L = [[1,1,1],[2,2,2],[0,0,0]]
T5B = [[0,2,1],[1,0,2],[2,1,0]]
NL1 = [[0,0,0],[1,1,0],[1,2,2]]
MAGMAS = {"T3R": T3R, "T3L": T3L, "T5B": T5B, "NL1": NL1}

def e1_holds_universally(e1_lhs, e1_rhs, all_vars, table):
    """Check if E1 holds for ALL variable assignments on this magma."""
    for vals in itertools.product(range(3), repeat=len(all_vars)):
        assign = dict(zip(all_vars, vals))
        if eval_tree(e1_lhs, assign, table) != eval_tree(e1_rhs, assign, table):
            return False
    return True

def e2_fails_somewhere(e2_lhs, e2_rhs, all_vars, table):
    """Check if E2 fails for SOME variable assignment on this magma."""
    for vals in itertools.product(range(3), repeat=len(all_vars)):
        assign = dict(zip(all_vars, vals))
        if eval_tree(e2_lhs, assign, table) != eval_tree(e2_rhs, assign, table):
            return True, dict(zip(all_vars, vals))
    return False, None

with open('data/hf_cache/hard.jsonl') as f:
    problems = [json.loads(l) for l in f]

true_problems = [p for p in problems if p['answer']]

print(f"TRUE problems: {len(true_problems)}")
print()

# Check with exhaustive E1 verification
sound_false_count = 0  # Still falsely separated even with exhaustive check
unsound_fixed = 0  # Fixed by exhaustive check

# Also check: with ONLY 2 assignments (default + all-zeros) - how many false seps?
two_check_false = 0
one_check_false = 0  # With ONLY default assignment (current T5B/NL1 behavior)

for p in true_problems:
    e1_lhs_s, e1_rhs_s = p['equation1'].split('=', 1)
    e2_lhs_s, e2_rhs_s = p['equation2'].split('=', 1)
    e1_lhs = parse_tree(e1_lhs_s.strip())
    e1_rhs = parse_tree(e1_rhs_s.strip())
    e2_lhs = parse_tree(e2_lhs_s.strip())
    e2_rhs = parse_tree(e2_rhs_s.strip())
    
    all_vars_set = get_vars(e1_lhs)|get_vars(e1_rhs)|get_vars(e2_lhs)|get_vars(e2_rhs)
    all_vars = sorted(all_vars_set)
    n_vars = len(all_vars)
    
    seen = []
    for c in p['equation1'] + p['equation2']:
        if c.isalpha() and c not in seen: seen.append(c)
    assign_default = {v: i%3 for i,v in enumerate(seen)}
    assign_zeros = {v: 0 for v in seen}
    
    for name, table in MAGMAS.items():
        if name in ('T5B','NL1') and n_vars >= 4:
            continue
        
        # 1-check: just default assignment
        try:
            e1_l = eval_tree(e1_lhs, assign_default, table)
            e1_r = eval_tree(e1_rhs, assign_default, table)
        except:
            continue
        if e1_l != e1_r:
            continue
        
        e2_l = eval_tree(e2_lhs, assign_default, table)
        e2_r = eval_tree(e2_rhs, assign_default, table)
        
        if e2_l != e2_r:
            one_check_false += 1
            
            # 2-check: add all-zeros
            e1_lz = eval_tree(e1_lhs, assign_zeros, table)
            e1_rz = eval_tree(e1_rhs, assign_zeros, table)
            if e1_lz == e1_rz:
                two_check_false += 1
                
                # Exhaustive check
                if e1_holds_universally(e1_lhs, e1_rhs, all_vars, table):
                    sound_false_count += 1
                    print(f"  STILL UNSOUND: {p['id']} via {name} (E1 holds universally but E2 fails)")
                    print(f"    E1: {p['equation1']}")
                    print(f"    E2: {p['equation2']}")
                    print(f"    vars: {n_vars}")
                else:
                    unsound_fixed += 1
                    # Find the failing assignment
                    for vals in itertools.product(range(3), repeat=n_vars):
                        a = dict(zip(all_vars, vals))
                        if eval_tree(e1_lhs, a, table) != eval_tree(e1_rhs, a, table):
                            break
            else:
                unsound_fixed += 1

print(f"\nSummary:")
print(f"  1-check false separations (current T5B/NL1): {one_check_false}")
print(f"  2-check false separations (current T3R/T3L): {two_check_false}")
print(f"  Exhaustive-check false separations: {sound_false_count}")
print(f"  Fixed by adding checks: {one_check_false - sound_false_count}")
print()

# Now check impact on FALSE problems
false_problems = [p for p in problems if not p['answer']]
lost_true_negatives = 0
gained_true_positives = one_check_false - sound_false_count  # FPs we'd prevent

# Check how many FALSE problems are ONLY separated by the tests that become more strict
for p in false_problems:
    e1_lhs_s, e1_rhs_s = p['equation1'].split('=', 1)
    e2_lhs_s, e2_rhs_s = p['equation2'].split('=', 1)
    e1_lhs = parse_tree(e1_lhs_s.strip())
    e1_rhs = parse_tree(e1_rhs_s.strip())
    e2_lhs = parse_tree(e2_lhs_s.strip())
    e2_rhs = parse_tree(e2_rhs_s.strip())
    
    all_vars_set = get_vars(e1_lhs)|get_vars(e1_rhs)|get_vars(e2_lhs)|get_vars(e2_rhs)
    all_vars = sorted(all_vars_set)
    n_vars = len(all_vars)
    
    seen = []
    for c in p['equation1'] + p['equation2']:
        if c.isalpha() and c not in seen: seen.append(c)
    assign_default = {v: i%3 for i,v in enumerate(seen)}
    
    has_any_sep = False  # Any test (structural or magma) separates
    has_some_sound_sep = False  # Any test that remains valid after exhaustive check
    
    # Check structural tests
    from collections import Counter
    e1_str = p['equation1']
    e2_str = p['equation2']
    
    def first_letter(s):
        for c in s:
            if c.isalpha(): return c
        return None
    def last_letter(s):
        for c in reversed(s):
            if c.isalpha(): return c
        return None
    
    e1_l_str, e1_r_str = e1_str.split('=', 1)
    e2_l_str, e2_r_str = e2_str.split('=', 1)
    
    struct_tests = {
        'LP': lambda l,r: first_letter(l) == first_letter(r),
        'RP': lambda l,r: last_letter(l) == last_letter(r),
    }
    
    # Quick structural check
    for tname, fn in struct_tests.items():
        e1_hold = fn(e1_l_str.strip(), e1_r_str.strip())
        e2_hold = fn(e2_l_str.strip(), e2_r_str.strip())
        if e1_hold and not e2_hold:
            has_any_sep = True
            has_some_sound_sep = True
    
    # Check magma tests with exhaustive E1 verification
    for name, table in MAGMAS.items():
        if name in ('T5B','NL1') and n_vars >= 4:
            continue
        try:
            e1_l = eval_tree(e1_lhs, assign_default, table)
            e1_r = eval_tree(e1_rhs, assign_default, table)
        except:
            continue
        if e1_l != e1_r: continue
        
        e2_l = eval_tree(e2_lhs, assign_default, table)
        e2_r = eval_tree(e2_rhs, assign_default, table)
        if e2_l != e2_r:
            has_any_sep = True
            if e1_holds_universally(e1_lhs, e1_rhs, all_vars, table):
                has_some_sound_sep = True
    
    if has_any_sep and not has_some_sound_sep:
        lost_true_negatives += 1

print(f"Impact on FALSE problems:")
print(f"  FALSE only separated by unsound tests: {lost_true_negatives}")
print(f"  (These would become FP if we add exhaustive checking)")
print()
print(f"Net impact of exhaustive E1 checking:")
print(f"  Gained TPs (prevent false sep on TRUE): +{gained_true_positives}")
print(f"  Lost TNs (can no longer catch some FALSE): -{lost_true_negatives}")
print(f"  Net: {'+' if gained_true_positives - lost_true_negatives > 0 else ''}{gained_true_positives - lost_true_negatives}")
