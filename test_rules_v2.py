"""Test refined absorptive rules v2: leftmost var check + appears-once check."""
import json
import re

def normalize(eq): return eq.replace(' ', '')
def parse_sides(eq): return eq.split('=', 1)
def count_ops(s): return s.count('*')
def get_vars(s): return set(re.findall(r'[a-z]', s))
def is_bare_var(s): return len(s) == 1 and s.isalpha()
def leftmost_var(s):
    for c in s:
        if c.isalpha(): return c
    return None
def rightmost_var(s):
    for c in reversed(s):
        if c.isalpha(): return c
    return None
def left_proj_satisfies(eq):
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
    if not lhs_has_op and not rhs_has_op: return lhs == rhs
    return False
def is_balanced(eq):
    lhs, rhs = parse_sides(eq)
    return count_ops(lhs) == count_ops(rhs)

def is_left_absorptive_v2(eq):
    """x=x*EXPR where leftmost var in EXPR is v != x and v appears once in EXPR."""
    lhs, rhs = parse_sides(eq)
    if not is_bare_var(lhs): return False
    x = lhs
    if not rhs.startswith(x + '*'): return False
    expr = rhs[2:]
    first_var = leftmost_var(expr)
    if first_var is None or first_var == x: return False
    # Count occurrences of first_var in expr
    count = len(re.findall(first_var, expr))
    return count == 1

def is_right_absorptive_v2(eq):
    """x=EXPR*x where leftmost var in EXPR is v != x and v appears once in EXPR."""
    lhs, rhs = parse_sides(eq)
    if not is_bare_var(lhs): return False
    x = lhs
    if not rhs.endswith('*' + x): return False
    expr = rhs[:-2]
    first_var = leftmost_var(expr)
    if first_var is None or first_var == x: return False
    count = len(re.findall(first_var, expr))
    return count == 1

def simulate_v2(fname, label):
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
    errors_detail = []
    
    for p in problems:
        e1 = normalize(p['equation1'])
        e2 = normalize(p['equation2'])
        answer = p['answer']
        
        prediction = None
        rule = None
        
        # Singleton
        lhs1, rhs1 = parse_sides(e1)
        if is_bare_var(lhs1) and lhs1 not in get_vars(rhs1):
            prediction, rule = True, 'singleton'
        elif is_bare_var(rhs1) and rhs1 not in get_vars(lhs1):
            prediction, rule = True, 'singleton'
        # Trivial target
        elif e2 == 'x=x':
            prediction, rule = True, 'trivial'
        # Left absorptive (v2)
        elif is_left_absorptive_v2(e1):
            prediction, rule = left_proj_satisfies(e2), 'left_abs'
        # Right absorptive (v2)
        elif is_right_absorptive_v2(e1):
            prediction, rule = right_proj_satisfies(e2), 'right_abs'
        # NO constant-forcing rule (removed)
        # Balance test
        elif is_balanced(e1) and not is_balanced(e2):
            prediction, rule = False, 'balance'
        # Counterexample magmas
        elif left_proj_satisfies(e1) and not left_proj_satisfies(e2):
            prediction, rule = False, 'counter_left'
        elif right_proj_satisfies(e1) and not right_proj_satisfies(e2):
            prediction, rule = False, 'counter_right'
        elif const_satisfies(e1) and not const_satisfies(e2):
            prediction, rule = False, 'counter_const'
        
        if prediction is None:
            unsolved += 1
            if answer: true_unsolved += 1
            else: false_unsolved += 1
        elif prediction == answer:
            correct += 1
            if answer: true_correct += 1
            else: false_correct += 1
        else:
            incorrect += 1
            if answer: true_incorrect += 1
            else: false_incorrect += 1
            errors_detail.append((p['id'], e1, e2, answer, prediction, rule))
    
    total = len(problems)
    print(f"\n{label} ({total} problems):")
    print(f"  Correct: {correct} ({100*correct/total:.1f}%)")
    print(f"  Incorrect: {incorrect} ({100*incorrect/total:.1f}%)")
    print(f"  Unsolved: {unsolved} ({100*unsolved/total:.1f}%)")
    print(f"  TRUE correct/incorrect/unsolved: {true_correct}/{true_incorrect}/{true_unsolved}")
    print(f"  FALSE correct/incorrect/unsolved: {false_correct}/{false_incorrect}/{false_unsolved}")
    
    default_false = correct + false_unsolved
    print(f"  If unsolved->FALSE: {default_false}/{total} ({100*default_false/total:.1f}%)")
    
    if errors_detail:
        print(f"\n  Errors ({len(errors_detail)}):")
        for pid, e1, e2, ans, pred, rule in errors_detail[:20]:
            print(f"    {pid}: {e1} -> {e2} ans={ans} pred={pred} rule={rule}")
        if len(errors_detail) > 20:
            print(f"    ... and {len(errors_detail)-20} more")

simulate_v2('data/benchmark/hard.jsonl', 'HARD')
simulate_v2('data/benchmark/normal.jsonl', 'NORMAL')
