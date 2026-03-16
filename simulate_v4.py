"""Simulate graph_v4.txt rules on benchmarks to verify accuracy."""
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

def is_singleton_forcing(eq):
    lhs, rhs = parse_sides(eq)
    if is_bare_var(lhs) and lhs not in get_vars(rhs): return True
    if is_bare_var(rhs) and rhs not in get_vars(lhs): return True
    return False

def is_left_absorptive_v2(eq):
    """x=x*EXPR where first var in EXPR ≠ x and appears once in EXPR."""
    lhs, rhs = parse_sides(eq)
    if not is_bare_var(lhs): return False
    x = lhs
    if not rhs.startswith(x + '*'): return False
    expr = rhs[2:]
    fv = leftmost_var(expr)
    if fv is None or fv == x: return False
    return len(re.findall(fv, expr)) == 1

def is_right_absorptive_v2(eq):
    """x=EXPR*x where first var in EXPR ≠ x and appears once in EXPR."""
    lhs, rhs = parse_sides(eq)
    if not is_bare_var(lhs): return False
    x = lhs
    if not rhs.endswith('*' + x): return False
    expr = rhs[:-2]
    fv = leftmost_var(expr)
    if fv is None or fv == x: return False
    return len(re.findall(fv, expr)) == 1

def left_proj_satisfies(eq):
    lhs, rhs = parse_sides(eq)
    return leftmost_var(lhs) == leftmost_var(rhs)

def right_proj_satisfies(eq):
    lhs, rhs = parse_sides(eq)
    return rightmost_var(lhs) == rightmost_var(rhs)

def const_satisfies(eq):
    lhs, rhs = parse_sides(eq)
    lo = count_ops(lhs) > 0
    ro = count_ops(rhs) > 0
    if lo and ro: return True
    if not lo and not ro: return lhs == rhs
    return False

def parity_satisfies(eq):
    """XOR model: count variable occurrences, check parity match."""
    lhs, rhs = parse_sides(eq)
    all_vars = get_vars(lhs) | get_vars(rhs)
    for v in all_vars:
        lcount = len(re.findall(v, lhs))
        rcount = len(re.findall(v, rhs))
        if (lcount % 2) != (rcount % 2):
            return False
    return True

def is_balanced(eq):
    lhs, rhs = parse_sides(eq)
    return count_ops(lhs) == count_ops(rhs)

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
    errors_detail = []
    rule_correct = {}
    
    for p in problems:
        e1 = normalize(p['equation1'])
        e2 = normalize(p['equation2'])
        answer = p['answer']
        
        prediction = None
        rule = None
        
        # Step 1: Singleton
        if is_singleton_forcing(e1):
            prediction, rule = True, 'singleton'
        
        # Step 2: Trivial
        elif e2 == 'x=x':
            prediction, rule = True, 'trivial'
        
        # Step 3: Left projection
        elif is_left_absorptive_v2(e1):
            prediction = left_proj_satisfies(e2)
            rule = 'left_abs'
        
        # Step 4: Right projection
        elif is_right_absorptive_v2(e1):
            prediction = right_proj_satisfies(e2)
            rule = 'right_abs'
        
        # Step 5: Counterexample magmas
        elif left_proj_satisfies(e1) and not left_proj_satisfies(e2):
            prediction, rule = False, 'counter_lp'
        elif right_proj_satisfies(e1) and not right_proj_satisfies(e2):
            prediction, rule = False, 'counter_rp'
        elif const_satisfies(e1) and not const_satisfies(e2):
            prediction, rule = False, 'counter_const'
        elif parity_satisfies(e1) and not parity_satisfies(e2):
            prediction, rule = False, 'counter_xor'
        
        # Step 6: Structural
        elif is_balanced(e1) and not is_balanced(e2):
            prediction, rule = False, 'balance'
        
        # Step 6b: Singleton target
        elif (parse_sides(e2)[0] != parse_sides(e2)[1] and 
              is_bare_var(parse_sides(e2)[0]) and is_bare_var(parse_sides(e2)[1])):
            prediction, rule = False, 'singleton_target'
        
        if prediction is None:
            unsolved += 1
            rule = 'unsolved'
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
        
        key = f"{rule}_{'T' if answer else 'F'}"
        rule_correct[key] = rule_correct.get(key, 0) + 1
    
    total = len(problems)
    print(f"\n{'='*60}")
    print(f"{label} ({total} problems):")
    print(f"  Correct: {correct} ({100*correct/total:.1f}%)")
    print(f"  Incorrect: {incorrect} ({100*incorrect/total:.1f}%)")
    print(f"  Unsolved: {unsolved} ({100*unsolved/total:.1f}%)")
    print(f"  TRUE:  correct={true_correct}, incorrect={true_incorrect}, unsolved={true_unsolved}")
    print(f"  FALSE: correct={false_correct}, incorrect={false_incorrect}, unsolved={false_unsolved}")
    
    default_false = correct + false_unsolved
    print(f"\n  If unsolved→FALSE: {default_false}/{total} ({100*default_false/total:.1f}%)")
    true_recall = true_correct / (true_correct + true_incorrect + true_unsolved) if (true_correct + true_incorrect + true_unsolved) > 0 else 0
    false_recall = (false_correct + false_unsolved) / (false_correct + false_incorrect + false_unsolved) if (false_correct + false_incorrect + false_unsolved) > 0 else 0
    print(f"  TRUE recall: {true_recall:.1%}")
    print(f"  FALSE recall: {false_recall:.1%}")
    
    print(f"\n  Rule breakdown:")
    for key in sorted(rule_correct.keys()):
        print(f"    {key:25} {rule_correct[key]}")
    
    if errors_detail:
        print(f"\n  ERRORS ({len(errors_detail)}):")
        for pid, e1, e2, ans, pred, r in errors_detail:
            print(f"    {pid}: {r} | {e1} → {e2} | ans={ans} pred={pred}")

simulate('data/benchmark/hard.jsonl', 'HARD')
simulate('data/benchmark/normal.jsonl', 'NORMAL')
