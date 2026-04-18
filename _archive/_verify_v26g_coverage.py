"""Verify exactly which problems v26g's patterns cover."""
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

# v26g patterns exactly as in cheatsheet
T4A_PATS = [
    lambda vs: {v: 1 for v in vs},                                          # A1: all=1
    lambda vs: {v: [1,2][i%2] for i,v in enumerate(vs)},                    # A2: cycle 1,2
    lambda vs: {v: [2,0][i%2] for i,v in enumerate(vs)},                    # A3: cycle 2,0
    lambda vs: {v: i%3 for i,v in enumerate(vs)},                           # A4: default 0,1,2
]

XOR_PATS = [
    lambda vs: {v: (0 if i==0 else 1) for i,v in enumerate(vs)},           # A1: 0,1,1,...
    lambda vs: {v: [1,2,0][i%3] for i,v in enumerate(vs)},                 # A2: cycle 1,2,0
]

# Check coverage
caught_by = {"T4A": [], "XOR": [], "NONE": []}
for p in false_problems:
    combined = p["equation1"] + " " + p["equation2"]
    vs = get_vars(combined)
    found = None
    
    # Try T4A patterns
    for pi, pat_fn in enumerate(T4A_PATS):
        vm = pat_fn(vs)
        if separates(p["equation1"], p["equation2"], t4a, vm):
            found = f"T4A_A{pi+1}"
            break
    
    if not found:
        # Try XOR patterns
        for pi, pat_fn in enumerate(XOR_PATS):
            vm = pat_fn(vs)
            if separates(p["equation1"], p["equation2"], xor3, vm):
                found = f"XOR_A{pi+1}"
                break
    
    if found:
        key = "T4A" if found.startswith("T4A") else "XOR"
        caught_by[key].append((p["id"], found))
    else:
        caught_by["NONE"].append(p["id"])

print(f"T4A: {len(caught_by['T4A'])}/40")
for pid, test in caught_by['T4A']:
    print(f"  {pid}: {test}")
print(f"XOR: {len(caught_by['XOR'])}/40") 
for pid, test in caught_by['XOR']:
    print(f"  {pid}: {test}")
print(f"NONE: {len(caught_by['NONE'])}/40")
for pid in caught_by['NONE']:
    p = next(pp for pp in false_problems if pp['id'] == pid)
    print(f"  {pid}: E1={p['equation1']}, E2={p['equation2']}")

total = len(caught_by['T4A']) + len(caught_by['XOR'])
print(f"\nTotal coverage: {total}/40 ({total/40*100:.1f}%)")

# Also check: which of v26c's 21 FP errors would v26g catch?
v26c_fps = ['hard3_0010','hard3_0084','hard3_0166','hard3_0070','hard3_0073',
            'hard3_0328','hard3_0045','hard3_0357','hard3_0083','hard3_0280',
            'hard3_0293','hard3_0342','hard3_0050','hard3_0383','hard3_0086',
            'hard3_0201','hard3_0349','hard3_0062','hard3_0074','hard3_0108',
            'hard3_0191']
print(f"\n=== v26c FP errors covered by v26g tests ===")
covered_fps = [fp for fp in v26c_fps if fp not in caught_by['NONE']]
uncovered_fps = [fp for fp in v26c_fps if fp in caught_by['NONE']]
print(f"Would catch: {len(covered_fps)}/21 FP errors")
print(f"Uncovered FP errors: {uncovered_fps}")
