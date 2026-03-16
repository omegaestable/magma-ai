"""Test refined left/right absorptive rules against benchmark errors."""
import json
import re

def normalize(eq): return eq.replace(' ', '')
def parse_sides(eq): return eq.split('=', 1)
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

def is_left_absorptive_old(eq):
    lhs, rhs = parse_sides(eq)
    if not is_bare_var(lhs): return False
    x = lhs
    if not rhs.startswith(x + '*'): return False
    expr = rhs[2:]
    other_vars = get_vars(expr) - {x}
    return len(other_vars) > 0

def is_left_absorptive_new(eq):
    lhs, rhs = parse_sides(eq)
    if not is_bare_var(lhs): return False
    x = lhs
    if not rhs.startswith(x + '*'): return False
    expr = rhs[2:]
    other_vars = get_vars(expr) - {x}
    if len(other_vars) == 0: return False
    first_var = leftmost_var(expr)
    return first_var != x

def is_right_absorptive_old(eq):
    lhs, rhs = parse_sides(eq)
    if not is_bare_var(lhs): return False
    x = lhs
    if not rhs.endswith('*' + x): return False
    expr = rhs[:-2]
    other_vars = get_vars(expr) - {x}
    return len(other_vars) > 0

def is_right_absorptive_new(eq):
    lhs, rhs = parse_sides(eq)
    if not is_bare_var(lhs): return False
    x = lhs
    if not rhs.endswith('*' + x): return False
    expr = rhs[:-2]
    other_vars = get_vars(expr) - {x}
    if len(other_vars) == 0: return False
    last_var = rightmost_var(expr)
    return last_var != x

with open('data/benchmark/hard.jsonl') as f:
    problems = [json.loads(l) for l in f]

print('=== LEFT ABSORPTIVE ERRORS (old) ===')
for p in problems:
    e1 = normalize(p['equation1'])
    e2 = normalize(p['equation2'])
    answer = p['answer']
    if is_left_absorptive_old(e1):
        pred = left_proj_satisfies(e2)
        if pred != answer:
            new_class = is_left_absorptive_new(e1)
            pid = p["id"]
            print(f'  {pid}: {e1} -> {e2} ans={answer} new_would_match={new_class}')

print()
print('=== RIGHT ABSORPTIVE ERRORS (old) ===')
for p in problems:
    e1 = normalize(p['equation1'])
    e2 = normalize(p['equation2'])
    answer = p['answer']
    if is_right_absorptive_old(e1):
        pred = right_proj_satisfies(e2)
        if pred != answer:
            new_class = is_right_absorptive_new(e1)
            pid = p["id"]
            print(f'  {pid}: {e1} -> {e2} ans={answer} new_would_match={new_class}')

print()
print('=== IMPACT SUMMARY ===')
new_left_correct = 0
new_left_errors = 0
new_right_correct = 0
new_right_errors = 0

for p in problems:
    e1 = normalize(p['equation1'])
    e2 = normalize(p['equation2'])
    answer = p['answer']
    
    if is_left_absorptive_new(e1):
        pred = left_proj_satisfies(e2)
        if pred == answer:
            new_left_correct += 1
        else:
            new_left_errors += 1
    
    if is_right_absorptive_new(e1):
        pred = right_proj_satisfies(e2)
        if pred == answer:
            new_right_correct += 1
        else:
            new_right_errors += 1

print(f'NEW left_abs: {new_left_correct} correct, {new_left_errors} errors')
print(f'NEW right_abs: {new_right_correct} correct, {new_right_errors} errors')
print(f'OLD left_abs: 24 correct TRUE, 5 errors')
print(f'OLD right_abs: 22 correct TRUE, 11 errors')
