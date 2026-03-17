import json
import re
from pathlib import Path

v4 = json.loads(Path('results/control_balanced120_qwen2.5_3b_graph_v4_revised_20260316.json').read_text())
nc = json.loads(Path('results/control_no_cheatsheet_qwen2.5_3b_balanced120_seed17.json').read_text())

results_v4 = v4['results']
results_nc = nc['results']

true_misses_v4 = [r for r in results_v4 if r['ground_truth'] == True and not r['correct']]
true_hits_v4 = [r for r in results_v4 if r['ground_truth'] == True and r['correct']]
false_misses_v4 = [r for r in results_v4 if r['ground_truth'] == False and not r['correct']]

print(f"v4: TRUE hits={len(true_hits_v4)}, TRUE misses={len(true_misses_v4)}, FALSE misses={len(false_misses_v4)}")

def vars_in(expr):
    return set(re.findall(r'\b[a-z]\b', expr))

def leftmost_var(expr):
    m = re.search(r'\b[a-z]\b', expr)
    return m.group() if m else None

def rightmost_var(expr):
    matches = re.findall(r'\b[a-z]\b', expr)
    return matches[-1] if matches else None

def parse_eq(eq):
    """Return (lhs, rhs) splitting on first = not inside parens."""
    depth = 0
    for i, c in enumerate(eq):
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
        elif c == '=' and depth == 0:
            return eq[:i].strip(), eq[i+1:].strip()
    return eq, ''

def classify_e1(e1_eq):
    """Classify E1 into a proof-family category."""
    lhs, rhs = parse_eq(e1_eq)
    lhs_vars = vars_in(lhs)
    rhs_vars = vars_in(rhs)
    
    # SINGLETON: LHS is a bare variable absent from RHS
    if len(lhs) <= 2 and lhs.strip().isalpha() and lhs.strip() not in rhs_vars:
        return 'SINGLETON'
    
    # LEFT-PROJECTION: LHS is bare var, RHS starts with that var
    if lhs.strip() in 'xyzwuv' and len(lhs.strip()) == 1:
        x = lhs.strip()
        if rhs.startswith(x + ' *') or rhs.startswith(x + '*'):
            return 'LEFT-PROJ'
        if rhs.startswith(x + ' ') or (len(rhs) > 0 and rhs[0] == x):
            pass  # maybe
    
    # More careful checks
    x = lhs.strip()
    if len(x) == 1 and x.isalpha():
        # LEFT-PROJ: x = x * EXPR
        if re.match(rf'^{x}\s*\*', rhs):
            return 'LEFT-PROJ'
        # RIGHT-PROJ: RHS ends in * x
        if re.search(rf'\*\s*{x}\s*$', rhs):
            return 'RIGHT-PROJ'
        # Check if x not in rhs at all -> singleton
        if x not in rhs_vars:
            return 'SINGLETON'
    
    return 'COMPLEX'

# Categorize all TRUE misses
print()
from collections import Counter
categories = Counter()
print("--- TRUE MISSES BY CATEGORY ---")
for r in true_misses_v4:
    e1 = r['equation1']
    e2 = r['equation2']
    cat = classify_e1(e1)
    categories[cat] += 1
    lhs1, rhs1 = parse_eq(e1)
    lhs2, rhs2 = parse_eq(e2)
    lm1, rm1 = leftmost_var(rhs1), rightmost_var(rhs1)
    lm2_l, rm2_l = leftmost_var(lhs2), rightmost_var(lhs2)
    lm2_r, rm2_r = leftmost_var(rhs2), rightmost_var(rhs2)
    detail = ''
    if cat == 'LEFT-PROJ':
        same = (lm2_l == lm2_r)
        detail = f'E2-leftmost: ({lm2_l} vs {lm2_r}) same={same}'
    elif cat == 'RIGHT-PROJ':
        same = (rm2_l == rm2_r)
        detail = f'E2-rightmost: ({rm2_l} vs {rm2_r}) same={same}'
    elif cat == 'SINGLETON':
        detail = 'should be trivially TRUE'
    print(f"  [{cat}] {r['id']}: {e1}  =>  {e2}  | {detail}")

print()
print("Category counts:", dict(categories))
print()
print("--- TRUE HITS ---")
for r in true_hits_v4:
    e1 = r['equation1']
    cat = classify_e1(e1)
    print(f"  [{cat}] {r['id']}: {e1}  =>  {r['equation2']}")
