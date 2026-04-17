"""Determine the optimal pattern set for v26g by simulating model behavior."""
import json
from itertools import product

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
        pos += 1
        val2, pos = parse_expr(tokens, pos, op_func, var_map)
        val = op_func(val, val2)
    return val, pos

def parse_atom(tokens, pos, op_func, var_map):
    if pos >= len(tokens):
        raise ValueError("Unexpected end")
    if tokens[pos] == '(':
        pos += 1
        val, pos = parse_expr(tokens, pos, op_func, var_map)
        if pos < len(tokens) and tokens[pos] == ')':
            pos += 1
        return val, pos
    elif tokens[pos].isalpha():
        return var_map[tokens[pos]], pos + 1
    else:
        raise ValueError(f"Unexpected: {tokens[pos]}")

def eval_side(s, op_func, var_map):
    toks = tokenize(s)
    val, _ = parse_expr(toks, 0, op_func, var_map)
    return val

def separates(eq1, eq2, op_func, var_map):
    try:
        e1_l = eval_side(eq1.split('=')[0], op_func, var_map)
        e1_r = eval_side(eq1.split('=')[1], op_func, var_map)
        if e1_l != e1_r: return False
        e2_l = eval_side(eq2.split('=')[0], op_func, var_map)
        e2_r = eval_side(eq2.split('=')[1], op_func, var_map)
        return e2_l != e2_r
    except: return False

def get_variables(s):
    seen = set(); result = []
    for c in s:
        if c.isalpha() and c not in seen:
            seen.add(c); result.append(c)
    return result

def t4a(a, b): return (2*a + b) % 3
def xor3(a, b): return (a + b) % 3
def t3l(a, b): return (a + 1) % 3

# Candidate pattern sets for T4A (varying number of patterns)
# Pattern: values assigned to 1st, 2nd, 3rd, 4th, 5th variable
candidates = {
    "default_only": [(0,1,2,0,1)],
    "default+all1": [(0,1,2,0,1), (1,1,1,1,1)],
    "default+all1+alt12": [(0,1,2,0,1), (1,1,1,1,1), (1,2,1,2,1)],
    "default+all1+alt12+alt20": [(0,1,2,0,1), (1,1,1,1,1), (1,2,1,2,1), (2,0,2,0,2)],
    "best_greedy_3": [(0,1,2,0,1), (1,2,1,2,1), (1,1,1,1,1)],
    "best_greedy_4": [(0,1,2,0,1), (1,2,1,2,1), (1,1,1,1,1), (2,0,2,0,2)],
}

# For each candidate set, compute T4A coverage
print("=== T4A coverage with pattern sets ===")
for name, patterns in candidates.items():
    count = 0
    for p in false_problems:
        combined = p["equation1"] + " " + p["equation2"]
        vs = get_variables(combined)
        found = False
        for pat in patterns:
            var_map = {v: pat[i] for i, v in enumerate(vs)}
            if separates(p["equation1"], p["equation2"], t4a, var_map):
                found = True
                break
        if found: count += 1
    print(f"  {name}: {count}/40")

# Now simulate: T4A (N patterns) + XOR (M patterns) + T3L (default)
print("\n=== Combined: T4A + XOR + T3L coverage ===")
xor_patterns = {
    "xor_2": [(0,1,1,1,1), (1,2,0,1,2)],
    "xor_3": [(0,1,1,1,1), (1,2,0,1,2), (1,0,0,0,0)],
}

for t4a_name, t4a_pats in candidates.items():
    for xor_name, xor_pats in xor_patterns.items():
        count = 0
        for p in false_problems:
            combined = p["equation1"] + " " + p["equation2"]
            vs = get_variables(combined)
            found = False
            # Try T4A
            for pat in t4a_pats:
                var_map = {v: pat[i] for i, v in enumerate(vs)}
                if separates(p["equation1"], p["equation2"], t4a, var_map):
                    found = True; break
            if not found:
                # Try XOR
                for pat in xor_pats:
                    var_map = {v: pat[i] for i, v in enumerate(vs)}
                    if separates(p["equation1"], p["equation2"], xor3, var_map):
                        found = True; break
            if not found:
                # Try T3L default
                var_map = {v: i%3 for i, v in enumerate(vs)}
                if separates(p["equation1"], p["equation2"], t3l, var_map):
                    found = True
            if found: count += 1
        if count >= 30:
            print(f"  {t4a_name} + {xor_name} + T3L_default: {count}/40")

# THE KEY QUESTION: what's the simplest approach that gets >=35/40?
# Try: T4A_3 + XOR_3 + T3L_default = ?
print("\n=== Recommended: best_greedy_3 T4A + xor_3 + T3L ===")
t4a_pats = [(0,1,2,0,1), (1,2,1,2,1), (1,1,1,1,1)]
xor_pats = [(0,1,1,1,1), (1,2,0,1,2), (1,0,0,0,0)]
t3l_default = True
caught_by = {"T4A": [], "XOR": [], "T3L": [], "NONE": []}
for p in false_problems:
    combined = p["equation1"] + " " + p["equation2"]
    vs = get_variables(combined)
    found_by = None
    for pat in t4a_pats:
        var_map = {v: pat[i] for i, v in enumerate(vs)}
        if separates(p["equation1"], p["equation2"], t4a, var_map):
            found_by = "T4A"; break
    if not found_by:
        for pat in xor_pats:
            var_map = {v: pat[i] for i, v in enumerate(vs)}
            if separates(p["equation1"], p["equation2"], xor3, var_map):
                found_by = "XOR"; break
    if not found_by:
        var_map = {v: i%3 for i, v in enumerate(vs)}
        if separates(p["equation1"], p["equation2"], t3l, var_map):
            found_by = "T3L"
    if not found_by:
        found_by = "NONE"
    caught_by[found_by].append(p["id"])

for key, pids in caught_by.items():
    print(f"  {key}: {len(pids)} problems")
    if key == "NONE":
        for pid in pids:
            p = next(pp for pp in false_problems if pp["id"] == pid)
            print(f"    {pid}: E1={p['equation1']}, E2={p['equation2']}")

# Check if more XOR patterns help the NONE
print("\n=== Checking NONE problems with exhaustive XOR ===")
for pid in caught_by["NONE"]:
    p = next(pp for pp in false_problems if pp["id"] == pid)
    combined = p["equation1"] + " " + p["equation2"]
    vs = get_variables(combined)
    n = len(vs)
    for assignment in product(range(3), repeat=n):
        var_map = dict(zip(vs, assignment))
        if separates(p["equation1"], p["equation2"], xor3, var_map):
            print(f"  {pid}: XOR works with {dict(zip(vs, assignment))}")
            break
    else:
        # Try T3L exhaustive
        for assignment in product(range(3), repeat=n):
            var_map = dict(zip(vs, assignment))
            if separates(p["equation1"], p["equation2"], t3l, var_map):
                print(f"  {pid}: T3L works with {dict(zip(vs, assignment))}")
                break
        else:
            print(f"  {pid}: STILL NONE after XOR+T3L exhaustive")
