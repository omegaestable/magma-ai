"""Quick check: which of the 5 normal FP misses are caught by T3L vs T3R."""

def _matching_paren(s, pos):
    depth = 0
    for i in range(pos, len(s)):
        if s[i] == '(':
            depth += 1
        elif s[i] == ')':
            depth -= 1
            if depth == 0:
                return i
    return -1


def _eval(s, magma):
    s = s.strip()
    if s.isdigit():
        return int(s)
    while s.startswith('(') and _matching_paren(s, 0) == len(s) - 1:
        s = s[1:-1].strip()
    if s.isdigit():
        return int(s)
    depth = 0
    main_star = -1
    for i, c in enumerate(s):
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
        elif c == '*' and depth == 0:
            main_star = i
            break
    if main_star == -1:
        return int(s)
    left = s[:main_star].strip()
    right = s[main_star + 1:].strip()
    a = _eval(left, magma)
    b = _eval(right, magma)
    if magma == 't3r':
        return (b + 1) % 3
    else:
        return (a + 1) % 3


import json, sys

problems = []

# Load from JSONL files passed as args, or use defaults
files = sys.argv[1:] if len(sys.argv) > 1 else []
if files:
    for fpath in files:
        with open(fpath) as f:
            for line in f:
                d = json.loads(line)
                if d.get('answer') == False or str(d.get('answer')).lower() == 'false':
                    problems.append((d['id'], d['equation1'], d['equation2']))
else:
    problems = [
        ('normal_0223', 'x = ((y * (x * y)) * x) * y', 'x = ((y * (z * w)) * u) * z'),
        ('normal_0299', 'x * x = x * ((x * y) * y)', 'x * x = ((x * x) * y) * z'),
        ('normal_0453', 'x = ((y * y) * x) * (x * x)', '(x * y) * z = (x * w) * z'),
        ('normal_0045', 'x * y = x * (x * x)', 'x * y = (x * x) * y'),
        ('normal_0997', 'x = (y * z) * (x * (z * x))', 'x * x = (y * (y * y)) * x'),
    ]

import re

def last_letter(s):
    """Last letter in the expression (skip trailing parens)."""
    for c in reversed(s.strip()):
        if c.isalpha():
            return c
    return None

def first_letter(s):
    """First letter (skip leading parens)."""
    for c in s.strip():
        if c.isalpha():
            return c
    return None

t3r_sep = 0
t3l_sep = 0
t3r_gated_sep = 0
both_sep = 0
either_sep = 0
total = 0

for pid, e1, e2 in problems:
    total += 1
    all_text = e1 + ' ' + e2
    seen = []
    for c in all_text:
        if c.isalpha() and c not in seen:
            seen.append(c)
    assign = {v: i % 3 for i, v in enumerate(seen)}

    e1_l, e1_r = e1.split('=', 1)
    e2_l, e2_r = e2.split('=', 1)

    # Check RP gate: last letter of E1_L vs E1_R
    rp_e1_hold = last_letter(e1_l) == last_letter(e1_r)

    seps = {}
    for magma in ['t3r', 't3l']:
        def subst(expr):
            for v in sorted(assign, key=lambda x: -len(x)):
                expr = expr.replace(v, str(assign[v]))
            return expr

        e1_ls = subst(e1_l)
        e1_rs = subst(e1_r)
        e2_ls = subst(e2_l)
        e2_rs = subst(e2_r)

        e1_lv = _eval(e1_ls, magma)
        e1_rv = _eval(e1_rs, magma)
        e2_lv = _eval(e2_ls, magma)
        e2_rv = _eval(e2_rs, magma)

        e1_holds = e1_lv == e1_rv
        e2_holds = e2_lv == e2_rv
        sep = e1_holds and not e2_holds
        seps[magma] = sep

    if seps['t3r']:
        t3r_sep += 1
        if rp_e1_hold:
            t3r_gated_sep += 1
    if seps['t3l']:
        t3l_sep += 1
    if seps['t3r'] and seps['t3l']:
        both_sep += 1
    if seps['t3r'] or seps['t3l']:
        either_sep += 1
        rp_tag = "RP=HOLD" if rp_e1_hold else "RP=FAIL"
        caught_by = []
        if seps['t3r']:
            caught_by.append(f"T3R({rp_tag})")
        if seps['t3l']:
            caught_by.append("T3L")
        print(f"  {pid}: {' + '.join(caught_by)}")

print(f"\nTotal: {total}")
print(f"T3R catches (any): {t3r_sep}")
print(f"T3R catches (with RP gate): {t3r_gated_sep}")
print(f"T3L catches: {t3l_sep}")
print(f"Both catch: {both_sep}")
print(f"Either catches: {either_sep}")
print(f"T3L-only (T3R misses): {t3l_sep - both_sep}")
print(f"T3R-only (T3L misses): {t3r_sep - both_sep}")
print(f"T3R gated-blocked: {t3r_sep - t3r_gated_sep}")
