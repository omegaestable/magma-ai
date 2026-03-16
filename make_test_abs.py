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

test = []
true_count = 0
false_count = 0
for p in problems:
    e1 = normalize(p['equation1'])
    if p['answer'] and (is_left_absorptive_v2(e1) or is_right_absorptive_v2(e1)):
        test.append(p)
        true_count += 1
        if true_count >= 10:
            break

for p in problems:
    if not p['answer']:
        test.append(p)
        false_count += 1
        if false_count >= 10:
            break

with open('data/benchmark/test_abs.jsonl', 'w') as f:
    for p in test:
        f.write(json.dumps(p) + '\n')
print(f"Wrote {len(test)} problems ({true_count} TRUE, {false_count} FALSE)")
for p in test[:5]:
    e1 = normalize(p['equation1'])
    pid = p["id"]
    ans = p["answer"]
    print(f"  {pid}: {e1} -> ans={ans}")
