"""Debug incorrect predictions from rule simulation."""
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

def is_left_absorptive(eq):
    lhs, rhs = parse_sides(eq)
    if not is_bare_var(lhs): return False
    x = lhs
    if not rhs.startswith(x + '*'): return False
    expr = rhs[2:]
    other_vars = get_vars(expr) - {x}
    return len(other_vars) > 0

def is_right_absorptive(eq):
    lhs, rhs = parse_sides(eq)
    if not is_bare_var(lhs): return False
    x = lhs
    if not rhs.endswith('*' + x): return False
    expr = rhs[:-2]
    other_vars = get_vars(expr) - {x}
    return len(other_vars) > 0

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

def is_constant_forcing(eq):
    lhs, rhs = parse_sides(eq)
    if count_ops(lhs) == 0 or count_ops(rhs) == 0: return False
    all_vars = get_vars(lhs) | get_vars(rhs)
    if len(all_vars) < 3: return False
    if is_bare_var(lhs) or is_bare_var(rhs): return False
    return True

# Load hard benchmark
with open('data/benchmark/hard.jsonl') as f:
    problems = [json.loads(l) for l in f]

# Find false positives (predicted TRUE but answer is FALSE) 
false_positives = []
for p in problems:
    e1 = normalize(p['equation1'])
    e2 = normalize(p['equation2'])
    answer = p['answer']
    
    prediction = None
    rule_used = None
    
    if is_singleton_forcing(e1):
        prediction = True
        rule_used = 'singleton'
    elif e2 == 'x=x':
        prediction = True
        rule_used = 'trivial'
    elif is_left_absorptive(e1):
        prediction = left_proj_satisfies(e2)
        rule_used = 'left_abs'
    elif is_right_absorptive(e1):
        prediction = right_proj_satisfies(e2)
        rule_used = 'right_abs'
    elif is_constant_forcing(e1):
        prediction = const_satisfies(e2)
        rule_used = 'const'
    
    if prediction is not None and prediction != answer:
        false_positives.append((p['id'], e1, e2, answer, prediction, rule_used))

print(f"Incorrect predictions: {len(false_positives)}")
for pid, e1, e2, ans, pred, rule in false_positives[:30]:
    print(f"  {pid}: {e1} -> {e2}")
    print(f"    Answer={ans}, Predicted={pred}, Rule={rule}")
