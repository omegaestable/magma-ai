"""Find subset of assignments that maximizes T4A+XOR coverage efficiently."""
import json
from itertools import product
from collections import Counter

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
    seen = set()
    result = []
    for c in s:
        if c.isalpha() and c not in seen:
            seen.add(c)
            result.append(c)
    return result

def t4a(a, b): return (2*a + b) % 3
def xor3(a, b): return (a + b) % 3
def t3r(a, b): return (b+1) % 3
def t3l(a, b): return (a+1) % 3

# 1. Variable counts
print("=== Variable distribution in FALSE problems ===")
var_counts = Counter()
for p in false_problems:
    vs = get_variables(p["equation1"] + " " + p["equation2"])
    var_counts[len(vs)] += 1
for n, c in sorted(var_counts.items()):
    print(f"  {n} variables: {c} problems")

# 2. Greedy assignment strategy selection for T4A
print("\n=== Greedy strategy selection for T4A ===")
# Enumerate all "canonical" assignments up to 5 vars
# A strategy = tuple of values for variables in first-appearance order
# For 2-var: (0,0),(0,1),(0,2),(1,0),(1,1),(1,2),(2,0),(2,1),(2,2) = 9
# For 3-var: 27, etc.
# We want to find a SMALL set of assignment PATTERNS that covers most problems

# Represent each strategy as: what value to assign to 1st, 2nd, 3rd, 4th, 5th var
# Since vars can be up to 5, we use patterns of length 5

patterns_to_try = [
    (0, 1, 2, 0, 1),  # default
    (1, 1, 1, 1, 1),  # all-1
    (2, 2, 2, 2, 2),  # all-2
    (1, 0, 2, 1, 0),  # reversed
    (0, 0, 1, 0, 0),  # mostly-0
    (1, 2, 0, 1, 2),  # shifted
    (2, 0, 1, 2, 0),  # shifted2
    (0, 2, 1, 0, 2),  # swap12
    (1, 0, 0, 0, 0),  # 1-then-0
    (0, 1, 1, 1, 1),  # 0-then-1
    (2, 1, 0, 2, 1),  # reverse
    (0, 0, 0, 0, 0),  # all-0
    (1, 1, 0, 0, 0),  # 1,1,0...
    (1, 2, 1, 2, 1),  # alternating 1,2
    (2, 0, 2, 0, 2),  # alternating 2,0
]

# Compute coverage matrix (problem x pattern)
coverage = {}  # pid -> set of pattern indices that work
for p in false_problems:
    combined = p["equation1"] + " " + p["equation2"]
    vs = get_variables(combined)
    n = len(vs)
    pid = p["id"]
    coverage[pid] = set()
    for pi, pat in enumerate(patterns_to_try):
        var_map = {v: pat[i] for i, v in enumerate(vs)}
        if separates(p["equation1"], p["equation2"], t4a, var_map):
            coverage[pid].add(pi)

# Greedy set cover
uncovered = set(pid for pid, s in coverage.items() if len(s) > 0)
selected = []
while uncovered:
    best_pi = max(range(len(patterns_to_try)), 
                  key=lambda pi: sum(1 for pid in uncovered if pi in coverage[pid]))
    new_covered = {pid for pid in uncovered if best_pi in coverage[pid]}
    if not new_covered:
        break
    selected.append(best_pi)
    uncovered -= new_covered
    print(f"  Select pattern {best_pi} {patterns_to_try[best_pi]}: covers {len(new_covered)} new (total uncovered: {len(uncovered)})")

print(f"\n  Selected {len(selected)} patterns covering {36 - len(uncovered)}/36 T4A-separable problems")

# 3. Same for XOR
print("\n=== Greedy strategy selection for XOR ===")
coverage_xor = {}
for p in false_problems:
    combined = p["equation1"] + " " + p["equation2"]
    vs = get_variables(combined)
    pid = p["id"]
    coverage_xor[pid] = set()
    for pi, pat in enumerate(patterns_to_try):
        var_map = {v: pat[i] for i, v in enumerate(vs)}
        if separates(p["equation1"], p["equation2"], xor3, var_map):
            coverage_xor[pid].add(pi)

uncovered_xor = set(pid for pid, s in coverage_xor.items() if len(s) > 0)
selected_xor = []
while uncovered_xor:
    best_pi = max(range(len(patterns_to_try)),
                  key=lambda pi: sum(1 for pid in uncovered_xor if pi in coverage_xor[pid]))
    new_covered = {pid for pid in uncovered_xor if best_pi in coverage_xor[pid]}
    if not new_covered: break
    selected_xor.append(best_pi)
    uncovered_xor -= new_covered
    print(f"  Select pattern {best_pi} {patterns_to_try[best_pi]}: covers {len(new_covered)} new (total uncovered: {len(uncovered_xor)})")

# 4. For each FALSE problem, SIMPLEST separating approach
print("\n=== Simplest separation per problem ===")
# Priority: T4A default → T4A all-1 → T4A other → XOR default → XOR all-1 → T3R/T3L
for p in false_problems:
    combined = p["equation1"] + " " + p["equation2"]
    vs = get_variables(combined)
    n = len(vs)
    pid = p["id"]
    
    # Try exhaustive for T4A
    best_t4a = None
    for assignment in product(range(3), repeat=n):
        var_map = dict(zip(vs, assignment))
        if separates(p["equation1"], p["equation2"], t4a, var_map):
            best_t4a = assignment
            break
    
    if best_t4a is None:
        # Try XOR
        best_xor = None
        for assignment in product(range(3), repeat=n):
            var_map = dict(zip(vs, assignment))
            if separates(p["equation1"], p["equation2"], xor3, var_map):
                best_xor = assignment
                break
        if best_xor is None:
            # Try T3R/T3L
            for mag_name, mag_fn in [("T3R", t3r), ("T3L", t3l)]:
                for assignment in product(range(3), repeat=n):
                    var_map = dict(zip(vs, assignment))
                    if separates(p["equation1"], p["equation2"], mag_fn, var_map):
                        print(f"  {pid} ({n}v): {mag_name} with {dict(zip(vs, assignment))}")
                        break
                else:
                    continue
                break
            else:
                print(f"  {pid} ({n}v): NO separation found!")
        else:
            print(f"  {pid} ({n}v): XOR with {dict(zip(vs, best_xor))}")
    # Only print T4A for undefault assignments
    elif best_t4a != tuple(i%3 for i in range(n)):
        print(f"  {pid} ({n}v): T4A with {dict(zip(vs, best_t4a))} (non-default)")

# 5. What if model tries just TWO assignments? 
print("\n=== Coverage with just 2 assignment patterns per magma ===")
# For each pair of patterns, compute T4A coverage
from itertools import combinations
best_pair = None
best_pair_count = 0
for p1, p2 in combinations(range(len(patterns_to_try)), 2):
    count = sum(1 for pid in coverage if p1 in coverage[pid] or p2 in coverage[pid])
    if count > best_pair_count:
        best_pair_count = count
        best_pair = (p1, p2)
print(f"Best T4A pair: patterns {best_pair} = {[patterns_to_try[i] for i in best_pair]} → {best_pair_count}/36 T4A-separable")

# Also check: what if we use ALL assignments exhaustively for problems with ≤3 vars?
print("\n=== T4A exhaustive for ≤3 vars, default for 4+ ===")
count = 0
for p in false_problems:
    vs = get_variables(p["equation1"] + " " + p["equation2"])
    n = len(vs)
    found = False
    if n <= 3:
        for assignment in product(range(3), repeat=n):
            var_map = dict(zip(vs, assignment))
            if separates(p["equation1"], p["equation2"], t4a, var_map):
                found = True
                break
    else:
        # Try default only for 4+ vars
        var_map = {v: i%3 for i, v in enumerate(vs)}
        found = separates(p["equation1"], p["equation2"], t4a, var_map)
    if found: count += 1
print(f"  T4A (exhaustive ≤3, default 4+): {count}/40")

# Check how many have 2 vars
print("\n=== T4A exhaustive coverage by variable count ===")
for nv in range(2, 6):
    subset = [p for p in false_problems if len(get_variables(p["equation1"]+" "+p["equation2"])) == nv]
    if not subset: continue
    count = 0
    for p in subset:
        vs = get_variables(p["equation1"] + " " + p["equation2"])
        for assignment in product(range(3), repeat=nv):
            var_map = dict(zip(vs, assignment))
            if separates(p["equation1"], p["equation2"], t4a, var_map):
                count += 1
                break
    print(f"  {nv} vars: {count}/{len(subset)} separable by T4A (exhaustive)")
