"""Find the absolute best 3+3 pattern combo for T4A+XOR."""
import json
from itertools import product, combinations

with open("data/benchmark/hard3_balanced50_true10_false40_rotation0020_20260417_002534.jsonl") as f:
    problems = [json.loads(line) for line in f]
false_problems = [p for p in problems if p["answer"] is False]

def tokenize(s):
    tokens = []
    for c in s.strip():
        if c in '()*': tokens.append(c)
        elif c.isalpha(): tokens.append(c)
    return tokens

def parse_expr(tokens, pos, op_func, var_map):
    val, pos = parse_atom(tokens, pos, op_func, var_map)
    if pos < len(tokens) and tokens[pos] == '*':
        pos += 1; val2, pos = parse_expr(tokens, pos, op_func, var_map); val = op_func(val, val2)
    return val, pos

def parse_atom(tokens, pos, op_func, var_map):
    if tokens[pos] == '(':
        pos += 1; val, pos = parse_expr(tokens, pos, op_func, var_map)
        if pos < len(tokens) and tokens[pos] == ')': pos += 1
        return val, pos
    return var_map[tokens[pos]], pos + 1

def eval_side(s, op_func, var_map):
    val, _ = parse_expr(tokenize(s), 0, op_func, var_map); return val

def separates(eq1, eq2, op, vm):
    try:
        e1l = eval_side(eq1.split('=')[0], op, vm); e1r = eval_side(eq1.split('=')[1], op, vm)
        if e1l != e1r: return False
        e2l = eval_side(eq2.split('=')[0], op, vm); e2r = eval_side(eq2.split('=')[1], op, vm)
        return e2l != e2r
    except: return False

def get_vars(s):
    seen = set(); r = []
    for c in s:
        if c.isalpha() and c not in seen: seen.add(c); r.append(c)
    return r

def t4a(a, b): return (2*a + b) % 3
def xor3(a, b): return (a + b) % 3

# All useful patterns (up to 5 vars)
ALL_PATS = list(product(range(3), repeat=5))
# But that's 243. Too many combos. Use top 15.
TOP_PATS = [
    (0,1,2,0,1), (1,1,1,1,1), (2,2,2,2,2), (1,0,2,1,0),
    (0,0,1,0,0), (1,2,0,1,2), (2,0,1,2,0), (0,2,1,0,2),
    (1,0,0,0,0), (0,1,1,1,1), (2,1,0,2,1), (0,0,0,0,0),
    (1,1,0,0,0), (1,2,1,2,1), (2,0,2,0,2),
]

# Precompute T4A coverage per pattern
t4a_cov = {}
for pi, pat in enumerate(TOP_PATS):
    t4a_cov[pi] = set()
    for p in false_problems:
        vs = get_vars(p["equation1"] + " " + p["equation2"])
        vm = {v: pat[i] for i, v in enumerate(vs)}
        if separates(p["equation1"], p["equation2"], t4a, vm):
            t4a_cov[pi].add(p["id"])

# Best triple for T4A among top patterns
print("=== Best T4A triples ===")
best_3 = None; best_3_count = 0
for combo in combinations(range(len(TOP_PATS)), 3):
    covered = set()
    for pi in combo: covered |= t4a_cov[pi]
    if len(covered) > best_3_count:
        best_3_count = len(covered)
        best_3 = combo
    if len(covered) >= 29:
        print(f"  {[TOP_PATS[i] for i in combo]}: {len(covered)}/40")
print(f"Best T4A triple: {[TOP_PATS[i] for i in best_3]}: {best_3_count}/40")

# Precompute XOR coverage per pattern
xor_cov = {}
for pi, pat in enumerate(TOP_PATS):
    xor_cov[pi] = set()
    for p in false_problems:
        vs = get_vars(p["equation1"] + " " + p["equation2"])
        vm = {v: pat[i] for i, v in enumerate(vs)}
        if separates(p["equation1"], p["equation2"], xor3, vm):
            xor_cov[pi].add(p["id"])

# For the best T4A triple, what XOR pair gives best additional coverage?
print(f"\n=== Best XOR additions to T4A best triple ===")
t4a_covered = set()
for pi in best_3: t4a_covered |= t4a_cov[pi]
remaining = set(p["id"] for p in false_problems) - t4a_covered
print(f"After T4A triple: {len(t4a_covered)}/40, remaining: {len(remaining)}")
print(f"Remaining: {sorted(remaining)}")

# What XOR patterns cover remaining?
for pi, pat in enumerate(TOP_PATS):
    hits = xor_cov[pi] & remaining
    if hits:
        print(f"  XOR pat {pat}: covers {len(hits)} remaining: {sorted(hits)}")

# Best XOR pair for remaining
best_xor_pair = None; best_xor_count = 0
for combo in combinations(range(len(TOP_PATS)), 2):
    covered_xor = set()
    for pi in combo: covered_xor |= (xor_cov[pi] & remaining)
    if len(covered_xor) > best_xor_count:
        best_xor_count = len(covered_xor)
        best_xor_pair = combo
    if len(covered_xor) >= len(remaining) - 1:
        print(f"  XOR pair {[TOP_PATS[i] for i in combo]}: covers {len(covered_xor)}/{len(remaining)} remaining")
print(f"Best XOR pair for remaining: {[TOP_PATS[i] for i in best_xor_pair]}: {best_xor_count}/{len(remaining)}")

# Final combined tally
total = set(t4a_covered)
for pi in best_xor_pair: total |= xor_cov[pi]
print(f"\nFinal: T4A({best_3_count}) + XOR({best_xor_count}) = {len(total)}/40")

still_missing = set(p["id"] for p in false_problems) - total
print(f"Still missing: {sorted(still_missing)}")
for pid in still_missing:
    p = next(pp for pp in false_problems if pp["id"] == pid)
    print(f"  {pid}: E1={p['equation1']}, E2={p['equation2']}")
