import json, re
from pathlib import Path

rows = [json.loads(l) for l in Path('data/benchmark/control_balanced_normal100_hard20_seed17.jsonl').read_text().splitlines() if l.strip()]

def has_product(expr):
    return '*' in expr

def parse_eq(eq):
    depth = 0
    for i, c in enumerate(eq):
        if c == '(': depth += 1
        elif c == ')': depth -= 1
        elif c == '=' and depth == 0:
            return eq[:i].strip(), eq[i+1:].strip()
    return eq, ''

def vars_of(expr):
    return set(re.findall(r'\b[a-z]\b', expr))

false_rows = [r for r in rows if not r['answer']]
true_rows = [r for r in rows if r['answer']]
print(f'FALSE cases: {len(false_rows)}, TRUE cases: {len(true_rows)}')

# Check FALSE cases for "E1 both-sides-product AND E2 both-sides-product"
danger = []
for r in false_rows:
    e1 = r['equation1']
    e2 = r['equation2']
    lhs1, rhs1 = parse_eq(e1)
    lhs2, rhs2 = parse_eq(e2)
    if has_product(lhs1) and has_product(rhs1) and has_product(lhs2) and has_product(rhs2):
        danger.append(r)

print(f'\nFALSE rows E1 both-sides-* AND E2 both-sides-*: {len(danger)}')
for r in danger:
    print("  " + r['id'] + ": " + r['equation1'] + "  =>  " + r['equation2'])

# Singleton check: E1 LHS is bare x not in RHS
print()
false_singleton = []
for r in false_rows:
    e1 = r['equation1']
    lhs1, rhs1 = parse_eq(e1)
    x = lhs1.strip()
    if len(x) == 1 and x.isalpha() and x not in vars_of(rhs1):
        false_singleton.append(r)

print(f'FALSE rows where E1 singleton: {len(false_singleton)}')

# Left-proj check with x-in-EXPR analysis
print()
for r in false_rows:
    e1 = r['equation1']
    lhs1, rhs1 = parse_eq(e1)
    x = lhs1.strip()
    if len(x) == 1 and x.isalpha():
        if rhs1.startswith(x + ' *') or rhs1.startswith(x + '*'):
            idx = rhs1.index('*') + 1
            expr_part = rhs1[idx:].strip()
            x_in_expr = x in vars_of(expr_part)
            print("LEFT-PROJ FALSE: " + r['id'] + " x_in_EXPR=" + str(x_in_expr) + " E1=" + e1 + " => E2=" + r['equation2'])

# Right-proj check
print()
for r in false_rows:
    e1 = r['equation1']
    lhs1, rhs1 = parse_eq(e1)
    x = lhs1.strip()
    if len(x) == 1 and x.isalpha():
        if re.search(r'\*\s*' + x + r'\s*$', rhs1):
            print("RIGHT-PROJ FALSE: " + r['id'] + " E1=" + e1 + " => E2=" + r['equation2'])
