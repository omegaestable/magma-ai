"""Analyze which assignment strategies maximize T4A coverage and find minimal instruction set."""
import json
from itertools import product
from collections import Counter

# Load
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
        if e1_l != e1_r:
            return False
        e2_l = eval_side(eq2.split('=')[0], op_func, var_map)
        e2_r = eval_side(eq2.split('=')[1], op_func, var_map)
        return e2_l != e2_r
    except:
        return False

def get_variables(eq_str):
    seen = set()
    result = []
    for c in eq_str:
        if c.isalpha() and c not in seen:
            seen.add(c)
            result.append(c)
    return result

# Magma definitions
def t4a(a, b): return (2*a + b) % 3
def t3r(a, b): return (b + 1) % 3
def t3l(a, b): return (a + 1) % 3
def xor3(a, b): return (a + b) % 3
def t5b(a, b): return (a + 2*b) % 3
def sub3(a, b): return (a - b) % 3

MAGMAS = {"T4A": t4a, "T3R": t3r, "T3L": t3l, "XOR": xor3, "T5B": t5b, "SUB3": sub3}

# === For each FALSE problem, find which assignments work for T4A ===
print("=== T4A: Which assignment strategies work? ===")
assignment_strategies = {
    "default": lambda vs: {v: i % 3 for i, v in enumerate(vs)},
    "all_0": lambda vs: {v: 0 for v in vs},
    "all_1": lambda vs: {v: 1 for v in vs},
    "all_2": lambda vs: {v: 2 for v in vs},
    "0_1_cycle": lambda vs: {v: i % 2 for i, v in enumerate(vs)},
    "1_0_cycle": lambda vs: {v: (i+1) % 2 for i, v in enumerate(vs)},
    "0_1_2_cycle": lambda vs: {v: i % 3 for i, v in enumerate(vs)},
    "1_0_2_cycle": lambda vs: {v: [1,0,2][i%3] for i, v in enumerate(vs)},
    "2_1_0_cycle": lambda vs: {v: (2-i) % 3 for i, v in enumerate(vs)},
}

for strat_name, strat_fn in assignment_strategies.items():
    count = 0
    for p in false_problems:
        combined = p["equation1"] + " " + p["equation2"]
        vs = get_variables(combined)
        var_map = strat_fn(vs)
        if separates(p["equation1"], p["equation2"], t4a, var_map):
            count += 1
    print(f"  {strat_name}: {count}/40")

# === Find minimal set of strategies to cover all 40 ===
print("\n=== Finding minimal strategy combinations ===")
# for each problem, which strategies work?
prob_strats = {}
for p in false_problems:
    combined = p["equation1"] + " " + p["equation2"]
    vs = get_variables(combined)
    n_vars = len(vs)
    working = []
    for assignment in product(range(3), repeat=n_vars):
        var_map = dict(zip(vs, assignment))
        if separates(p["equation1"], p["equation2"], t4a, var_map):
            working.append(tuple(assignment))
    prob_strats[p["id"]] = working

# Problems T4A can't separate at all
unsep = [pid for pid, strats in prob_strats.items() if len(strats) == 0]
print(f"T4A can't separate {len(unsep)} problems: {unsep}")

# For T4A-separable ones, how many assignments work on average?
sep_probs = {pid: strats for pid, strats in prob_strats.items() if len(strats) > 0}
for pid in sorted(sep_probs):
    p = next(pp for pp in false_problems if pp["id"] == pid)
    vs = get_variables(p["equation1"] + " " + p["equation2"])
    total_possible = 3**len(vs)
    print(f"  {pid}: {len(sep_probs[pid])}/{total_possible} assignments work ({len(vs)} vars)")

# === What magma covers the T4A-unseparated problems? ===
print("\n=== Coverage of T4A-unseparated problems by other magmas ===")
for pid in unsep:
    p = next(pp for pp in false_problems if pp["id"] == pid)
    combined = p["equation1"] + " " + p["equation2"]
    vs = get_variables(combined)
    n_vars = len(vs)
    print(f"\n  {pid}: E1={p['equation1']}, E2={p['equation2']}")
    for mag_name, mag_fn in MAGMAS.items():
        if mag_name == "T4A": continue
        for assignment in product(range(3), repeat=n_vars):
            var_map = dict(zip(vs, assignment))
            if separates(p["equation1"], p["equation2"], mag_fn, var_map):
                print(f"    {mag_name} works with {dict(zip(vs, assignment))}")
                break

# === Best 2-magma combination ===
print("\n=== Best 2-magma combination with exhaustive search ===")
import itertools as it
best_combo = None
best_count = 0
for m1, m2 in it.combinations(MAGMAS.keys(), 2):
    count = 0
    for p in false_problems:
        combined = p["equation1"] + " " + p["equation2"]
        vs = get_variables(combined)
        n_vars = len(vs)
        found = False
        for mag_fn in [MAGMAS[m1], MAGMAS[m2]]:
            for assignment in product(range(3), repeat=n_vars):
                var_map = dict(zip(vs, assignment))
                if separates(p["equation1"], p["equation2"], mag_fn, var_map):
                    found = True
                    break
            if found: break
        if found: count += 1
    if count > best_count:
        best_count = count
        best_combo = (m1, m2)
    if count >= 38:
        print(f"  {m1}+{m2}: {count}/40")
print(f"Best combo: {best_combo} with {best_count}/40")
