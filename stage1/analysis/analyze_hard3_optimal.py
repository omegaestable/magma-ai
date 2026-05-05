"""Find optimal magma combination for hard3 FALSE separation."""
import json, itertools, time
from collections import defaultdict

with open("data/benchmark/hard3_balanced40_true20_false20_rotation0002_20260403_185904.jsonl") as f:
    lines = [json.loads(l) for l in f]

false_pairs = [l for l in lines if l["answer"] is False]
true_pairs = [l for l in lines if l["answer"] is True]


def parse_expr(s):
    s = s.strip()
    while s.startswith('(') and s.endswith(')'):
        d = 0; matched = True
        for i, c in enumerate(s):
            if c == '(': d += 1
            elif c == ')': d -= 1
            if d == 0 and i < len(s) - 1: matched = False; break
        if matched: s = s[1:-1].strip()
        else: break
    depth = 0
    for i, c in enumerate(s):
        if c == '(': depth += 1
        elif c == ')': depth -= 1
        elif c == '*' and depth == 0:
            return ('op', parse_expr(s[:i].strip()), parse_expr(s[i+1:].strip()))
    return ('var', s.strip())


def eval_tree(tree, assignment, op_table, n):
    if tree[0] == 'var': return assignment[tree[1]]
    l = eval_tree(tree[1], assignment, op_table, n)
    r = eval_tree(tree[2], assignment, op_table, n)
    return op_table[l * n + r]


def get_variables(tree):
    if tree[0] == 'var': return {tree[1]}
    return get_variables(tree[1]) | get_variables(tree[2])


def equation_holds(lhs, rhs, op_table, n, variables):
    for vals in itertools.product(range(n), repeat=len(variables)):
        a = dict(zip(variables, vals))
        if eval_tree(lhs, a, op_table, n) != eval_tree(rhs, a, op_table, n):
            return False
    return True


def parse_pair(p):
    e1l, e1r = p["equation1"].split("=", 1)
    e2l, e2r = p["equation2"].split("=", 1)
    t1l, t1r = parse_expr(e1l), parse_expr(e1r)
    t2l, t2r = parse_expr(e2l), parse_expr(e2r)
    vs = sorted(get_variables(t1l) | get_variables(t1r) | get_variables(t2l) | get_variables(t2r))
    return (p["id"], t1l, t1r, t2l, t2r, vs)


parsed_false = [parse_pair(p) for p in false_pairs]
parsed_true = [parse_pair(p) for p in true_pairs]

# Build coverage map: for each 3-element magma, which FALSE pairs does it separate?
n = 3
magma_coverage = {}  # op_tuple -> set of pair_ids caught
pair_separators = defaultdict(list)  # pair_id -> list of op_tuples

print("Building coverage map for all 3-element magmas...")
start = time.time()

for op_tuple in itertools.product(range(n), repeat=n*n):
    op_table = list(op_tuple)
    caught = set()
    for pid, t1l, t1r, t2l, t2r, vs in parsed_false:
        if equation_holds(t1l, t1r, op_table, n, vs):
            if not equation_holds(t2l, t2r, op_table, n, vs):
                caught.add(pid)
    if caught:
        magma_coverage[op_tuple] = caught
        for pid in caught:
            pair_separators[pid].append(op_tuple)

print(f"Done in {time.time()-start:.1f}s. {len(magma_coverage)} magmas have at least 1 catch.")

# Check FP for all separating magmas
print("\nChecking FALSE POSITIVE rates for all separating magmas...")
magma_fp = {}
for op_tuple in magma_coverage:
    op_table = list(op_tuple)
    fps = 0
    for pid, t1l, t1r, t2l, t2r, vs in parsed_true:
        if equation_holds(t1l, t1r, op_table, n, vs):
            if not equation_holds(t2l, t2r, op_table, n, vs):
                fps += 1
    magma_fp[op_tuple] = fps

# Find magmas with 0 FP
zero_fp_magmas = {k: v for k, v in magma_coverage.items() if magma_fp[k] == 0}
print(f"Magmas with 0 FP: {len(zero_fp_magmas)}")

# Rank zero-FP magmas by coverage
ranked = sorted(zero_fp_magmas.items(), key=lambda x: -len(x[1]))

print("\n" + "=" * 80)
print("TOP 10 ZERO-FP 3-ELEMENT MAGMAS (by coverage)")
print("=" * 80)
for i, (op_tuple, caught) in enumerate(ranked[:10]):
    table = [[op_tuple[r*3+c] for c in range(3)] for r in range(3)]
    print(f"\n#{i+1}: Catches {len(caught)}/20 FALSE, 0 FP")
    print(f"  Table: {table}")
    print(f"  Catches: {sorted(caught)}")

# Greedy set cover with 0-FP constraint
print("\n" + "=" * 80)
print("GREEDY SET COVER (0-FP magmas only)")
print("=" * 80)

remaining = set(pid for pid, *_ in parsed_false if pid in pair_separators)
selected = []
covered = set()

while remaining:
    best_magma = None
    best_new = 0
    for op_tuple, caught in zero_fp_magmas.items():
        new_catches = len(caught - covered)
        if new_catches > best_new:
            best_new = new_catches
            best_magma = op_tuple
    if best_magma is None or best_new == 0:
        break
    selected.append(best_magma)
    newly_covered = zero_fp_magmas[best_magma] - covered
    covered |= zero_fp_magmas[best_magma]
    remaining -= zero_fp_magmas[best_magma]
    table = [[best_magma[r*3+c] for c in range(3)] for r in range(3)]
    print(f"\nStep {len(selected)}: +{best_new} new catches (total {len(covered)}/20)")
    print(f"  Table: {table}")
    print(f"  New catches: {sorted(newly_covered)}")

print(f"\n{'='*80}")
print(f"GREEDY RESULT: {len(selected)} magmas cover {len(covered)}/20 FALSE pairs with 0 FP")
print(f"Uncovered: {sorted(remaining)}")

# Also identify which pairs are unseparable at 3 elements
unsep_3 = set(pid for pid, *_ in parsed_false) - set(pair_separators.keys())
print(f"\nUnseparable by ANY 3-element magma ({len(unsep_3)}): {sorted(unsep_3)}")

# For each unseparable pair, check if they need 4-element magmas
# Quick check: try a few specific 4-element magmas from the proof data
print(f"\n{'='*80}")
print("CHECKING SPECIFIC 4-ELEMENT MAGMAS FOR UNSEPARABLE PAIRS")
print("=" * 80)

specific_4elem = {
    "ConstRows": [1,1,1,1, 2,2,2,2, 3,3,3,3, 0,0,0,0],  # hard3_0073 counterexample
    "BlockRepeat": [3,1,3,1, 3,1,3,1, 2,0,2,0, 2,0,2,0],  # hard3_0166 counterexample
    "T4L": [(i+1)%4 for i in range(4) for j in range(4)],  # Translation x*y=(x+1)%4
    "LeftZero4": [i for i in range(4) for j in range(4)],
    "RightZero4": [j for i in range(4) for j in range(4)],
}

unsep_parsed = [(pid, t1l, t1r, t2l, t2r, vs) for pid, t1l, t1r, t2l, t2r, vs in parsed_false if pid in unsep_3]

for name, op_table in specific_4elem.items():
    n4 = 4
    caught = set()
    fps = 0
    for pid, t1l, t1r, t2l, t2r, vs in unsep_parsed:
        if equation_holds(t1l, t1r, op_table, n4, vs):
            if not equation_holds(t2l, t2r, op_table, n4, vs):
                caught.add(pid)
    for pid, t1l, t1r, t2l, t2r, vs in parsed_true:
        if equation_holds(t1l, t1r, op_table, n4, vs):
            if not equation_holds(t2l, t2r, op_table, n4, vs):
                fps += 1
    table = [[op_table[r*4+c] for c in range(4)] for r in range(4)]
    print(f"\n{name}: Catches {len(caught)} unsep, FP={fps}")
    if caught:
        print(f"  Catches: {sorted(caught)}")
