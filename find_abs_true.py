import json, re

def normalize(eq): return eq.replace(' ', '')
def parse_sides(eq): return eq.split('=', 1)
def is_bare_var(s): return len(s) == 1 and s.isalpha()
def leftmost_var(s):
    for c in s:
        if c.isalpha(): return c
    return None

def is_left_absorptive_v2(eq):
    lhs, rhs = parse_sides(eq)
    if not is_bare_var(lhs): return False
    x = lhs
    if not rhs.startswith(x + '*'): return False
    expr = rhs[2:]
    fv = leftmost_var(expr)
    if fv is None or fv == x: return False
    return len(re.findall(fv, expr)) == 1

def is_right_absorptive_v2(eq):
    lhs, rhs = parse_sides(eq)
    if not is_bare_var(lhs): return False
    x = lhs
    if not rhs.endswith('*' + x): return False
    expr = rhs[:-2]
    fv = leftmost_var(expr)
    if fv is None or fv == x: return False
    return len(re.findall(fv, expr)) == 1

with open('data/benchmark/hard.jsonl') as f:
    problems = [json.loads(l) for l in f]

abs_true = []
for p in problems:
    e1 = normalize(p['equation1'])
    answer = p['answer']
    if answer and (is_left_absorptive_v2(e1) or is_right_absorptive_v2(e1)):
        abs_true.append(p['id'])

print(f"Absorptive TRUE problems: {len(abs_true)}")
indices = sorted(int(x.split("_")[1]) for x in abs_true)
print(f"Indices: {indices}")
print(f"Min: {min(indices)}, Max: {max(indices)}")
