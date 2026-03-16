"""Analyze how many benchmark problems each rule can solve."""
import json
import re

def normalize(eq_str):
    return eq_str.replace(' ', '')

def parse_sides(eq):
    parts = eq.split('=', 1)
    return parts[0], parts[1]

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
    lhs_vars = get_vars(lhs)
    rhs_vars = get_vars(rhs)
    if is_bare_var(lhs) and lhs not in rhs_vars:
        return True
    if is_bare_var(rhs) and rhs not in lhs_vars:
        return True
    return False

def is_balanced(eq):
    lhs, rhs = parse_sides(eq)
    return count_ops(lhs) == count_ops(rhs)

def left_proj_sat(eq):
    lhs, rhs = parse_sides(eq)
    return leftmost_var(lhs) == leftmost_var(rhs)

def right_proj_sat(eq):
    lhs, rhs = parse_sides(eq)
    return rightmost_var(lhs) == rightmost_var(rhs)

def const_sat(eq):
    lhs, rhs = parse_sides(eq)
    return count_ops(lhs) > 0 and count_ops(rhs) > 0

for fname, label in [('data/benchmark/hard.jsonl', 'HARD'), ('data/benchmark/normal.jsonl', 'NORMAL')]:
    stats = {'r1_true': 0, 'r2_true': 0, 'r5_false': 0, 'r6_false': 0, 'r7_false': 0,
             'unsolved': 0, 'total': 0, 'unsolved_true': 0, 'unsolved_false': 0}

    with open(fname) as f:
        for line in f:
            d = json.loads(line)
            e1 = normalize(d['equation1'])
            e2 = normalize(d['equation2'])
            answer = d['answer']
            stats['total'] += 1
            
            # R1: singleton test
            if is_singleton_forcing(e1):
                stats['r1_true'] += 1
                continue
            
            # R2: E2 is x=x
            if e2 == 'x=x':
                stats['r2_true'] += 1
                continue
            
            # R5: balance test
            if is_balanced(e1) and not is_balanced(e2):
                stats['r5_false'] += 1
                continue
            
            # R6: counterexample magmas
            lp1, lp2 = left_proj_sat(e1), left_proj_sat(e2)
            rp1, rp2 = right_proj_sat(e1), right_proj_sat(e2)
            co1, co2 = const_sat(e1), const_sat(e2)
            
            if (lp1 and not lp2) or (rp1 and not rp2) or (co1 and not co2):
                stats['r6_false'] += 1
                continue
            
            # R7: E2 is x=y
            lhs2, rhs2 = parse_sides(e2)
            if is_bare_var(lhs2) and is_bare_var(rhs2) and lhs2 != rhs2:
                stats['r7_false'] += 1
                continue
            
            stats['unsolved'] += 1
            if answer:
                stats['unsolved_true'] += 1
            else:
                stats['unsolved_false'] += 1

    print(f"\n{label} benchmark rule coverage:")
    solved = stats['total'] - stats['unsolved']
    for k, v in stats.items():
        print(f"  {k}: {v}")
    print(f"  solved: {solved}")
    print(f"  solved%: {solved / stats['total'] * 100:.1f}%")
