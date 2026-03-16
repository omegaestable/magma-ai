"""Simulate the cheatsheet rules to predict accuracy on benchmarks."""
import json
import re

def normalize(eq):
    return eq.replace(' ', '')

def parse_sides(eq):
    return eq.split('=', 1)

def count_ops(s):
    return s.count('*')

def get_vars(s):
    return set(re.findall(r'[a-z]', s))

def is_bare_var(s):
    return len(s) == 1 and s.isalpha()

def leftmost_var(s):
    for c in s:
        if c.isalpha(): return c
    return None

def rightmost_var(s):
    for c in reversed(s):
        if c.isalpha(): return c
    return None

def is_singleton_forcing(eq):
    lhs, rhs = parse_sides(eq)
    if is_bare_var(lhs) and lhs not in get_vars(rhs): return True
    if is_bare_var(rhs) and rhs not in get_vars(lhs): return True
    return False

def is_balanced(eq):
    lhs, rhs = parse_sides(eq)
    return count_ops(lhs) == count_ops(rhs)

def is_left_absorptive(eq):
    """E1 has form x=x*EXPR where EXPR has a variable != x"""
    lhs, rhs = parse_sides(eq)
    if not is_bare_var(lhs): return False
    x = lhs
    if not rhs.startswith(x + '*'): return False
    # Check if the EXPR part (after x*) has a variable != x
    expr = rhs[2:]  # skip "x*"
    other_vars = get_vars(expr) - {x}
    return len(other_vars) > 0

def is_right_absorptive(eq):
    """E1 has form x=EXPR*x where EXPR has a variable != x"""
    lhs, rhs = parse_sides(eq)
    if not is_bare_var(lhs): return False
    x = lhs
    if not rhs.endswith('*' + x): return False
    # Check if the EXPR part (before *x) has a variable != x
    expr = rhs[:-2]  # skip "*x"
    # But need to be careful: rhs could be "(stuff)*x"
    # Actually the simple endswith check might be wrong for nested expressions
    # Let me use a more careful approach: the rightmost * at the top level
    # should have x as the right operand
    # For now, use the simple check
    other_vars = get_vars(expr) - {x}
    return len(other_vars) > 0

def left_proj_satisfies(eq):
    """Under a*b=a, expressions reduce to leftmost variable."""
    lhs, rhs = parse_sides(eq)
    return leftmost_var(lhs) == leftmost_var(rhs)

def right_proj_satisfies(eq):
    lhs, rhs = parse_sides(eq)
    return rightmost_var(lhs) == rightmost_var(rhs)

def const_satisfies(eq):
    lhs, rhs = parse_sides(eq)
    lhs_has_op = count_ops(lhs) > 0
    rhs_has_op = count_ops(rhs) > 0
    if lhs_has_op and rhs_has_op: return True
    if not lhs_has_op and not rhs_has_op:
        return lhs == rhs  # both bare vars, must be same
    return False

def is_constant_forcing(eq):
    """Check if E1 forces constant operation."""
    lhs, rhs = parse_sides(eq)
    # Both sides must have * and total distinct vars >= 3
    if count_ops(lhs) == 0 or count_ops(rhs) == 0: return False
    all_vars = get_vars(lhs) | get_vars(rhs)
    if len(all_vars) < 3: return False
    # Also check it's not just left/right absorptive
    if is_bare_var(lhs) or is_bare_var(rhs): return False
    return True

def simulate(fname, label):
    with open(fname) as f:
        problems = [json.loads(l) for l in f]
    
    correct = 0
    incorrect = 0
    unsolved = 0
    true_correct = 0
    true_incorrect = 0
    false_correct = 0
    false_incorrect = 0
    true_unsolved = 0
    false_unsolved = 0
    
    for p in problems:
        e1 = normalize(p['equation1'])
        e2 = normalize(p['equation2'])
        answer = p['answer']
        
        prediction = None
        
        # Step 2: Singleton
        if is_singleton_forcing(e1):
            prediction = True
        
        # Step 3: Trivial target
        elif e2 == 'x=x':
            prediction = True
        
        # Step 4-5: Left absorptive
        elif is_left_absorptive(e1):
            prediction = left_proj_satisfies(e2)
        
        # Step 4-5: Right absorptive
        elif is_right_absorptive(e1):
            prediction = right_proj_satisfies(e2)
        
        # Step 4-5: Constant forcing (rough check)
        elif is_constant_forcing(e1):
            prediction = const_satisfies(e2)
        
        # Step 6a: Balance test
        elif is_balanced(e1) and not is_balanced(e2):
            prediction = False
        
        # Step 6b: Singleton target
        elif parse_sides(e2)[0] != parse_sides(e2)[1] and is_bare_var(parse_sides(e2)[0]) and is_bare_var(parse_sides(e2)[1]):
            prediction = False
        
        # Step 7: Counterexample magmas
        elif left_proj_satisfies(e1) and not left_proj_satisfies(e2):
            prediction = False
        elif right_proj_satisfies(e1) and not right_proj_satisfies(e2):
            prediction = False
        elif const_satisfies(e1) and not const_satisfies(e2):
            prediction = False
        
        if prediction is None:
            unsolved += 1
            if answer:
                true_unsolved += 1
            else:
                false_unsolved += 1
        elif prediction == answer:
            correct += 1
            if answer:
                true_correct += 1
            else:
                false_correct += 1
        else:
            incorrect += 1
            if answer:
                true_incorrect += 1
            else:
                false_incorrect += 1
    
    total = len(problems)
    print(f"\n{label} ({total} problems):")
    print(f"  Correct: {correct} ({100*correct/total:.1f}%)")
    print(f"  Incorrect: {incorrect} ({100*incorrect/total:.1f}%)")
    print(f"  Unsolved: {unsolved} ({100*unsolved/total:.1f}%)")
    print(f"  TRUE correct/incorrect/unsolved: {true_correct}/{true_incorrect}/{true_unsolved}")
    print(f"  FALSE correct/incorrect/unsolved: {false_correct}/{false_incorrect}/{false_unsolved}")
    
    # If unsolved defaults to FALSE
    default_false = correct + false_unsolved
    print(f"  If unsolved→FALSE: {default_false}/{total} ({100*default_false/total:.1f}%)")
    # If unsolved defaults to TRUE
    default_true = correct + true_unsolved
    print(f"  If unsolved→TRUE: {default_true}/{total} ({100*default_true/total:.1f}%)")

simulate('data/benchmark/hard.jsonl', 'HARD')
simulate('data/benchmark/normal.jsonl', 'NORMAL')
