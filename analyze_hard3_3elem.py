"""Check 3-element magmas for hard3 FALSE separation. 3^9 = 19683 possible ops."""
import json, re, itertools, time

with open("data/benchmark/hard3_balanced40_true20_false20_rotation0002_20260403_185904.jsonl") as f:
    lines = [json.loads(l) for l in f]

false_pairs = [l for l in lines if l["answer"] is False]
true_pairs = [l for l in lines if l["answer"] is True]


def parse_expr(s):
    s = s.strip()
    while s.startswith('(') and s.endswith(')'):
        d = 0
        matched = True
        for i, c in enumerate(s):
            if c == '(': d += 1
            elif c == ')': d -= 1
            if d == 0 and i < len(s) - 1:
                matched = False
                break
        if matched:
            s = s[1:-1].strip()
        else:
            break
    depth = 0
    for i, c in enumerate(s):
        if c == '(': depth += 1
        elif c == ')': depth -= 1
        elif c == '*' and depth == 0:
            return ('op', parse_expr(s[:i].strip()), parse_expr(s[i+1:].strip()))
    return ('var', s.strip())


def eval_tree(tree, assignment, op_table, n):
    if tree[0] == 'var':
        return assignment[tree[1]]
    left = eval_tree(tree[1], assignment, op_table, n)
    right = eval_tree(tree[2], assignment, op_table, n)
    return op_table[left * n + right]


def get_variables(tree):
    if tree[0] == 'var': return {tree[1]}
    return get_variables(tree[1]) | get_variables(tree[2])


def equation_holds(lhs, rhs, op_table, n, variables):
    for vals in itertools.product(range(n), repeat=len(variables)):
        a = dict(zip(variables, vals))
        if eval_tree(lhs, a, op_table, n) != eval_tree(rhs, a, op_table, n):
            return False
    return True


# Pre-parse all pairs
parsed_false = []
for p in false_pairs:
    e1l, e1r = p["equation1"].split("=", 1)
    e2l, e2r = p["equation2"].split("=", 1)
    t1l, t1r = parse_expr(e1l), parse_expr(e1r)
    t2l, t2r = parse_expr(e2l), parse_expr(e2r)
    vs = sorted(get_variables(t1l) | get_variables(t1r) | get_variables(t2l) | get_variables(t2r))
    parsed_false.append((p["id"], t1l, t1r, t2l, t2r, vs))

parsed_true = []
for p in true_pairs:
    e1l, e1r = p["equation1"].split("=", 1)
    e2l, e2r = p["equation2"].split("=", 1)
    t1l, t1r = parse_expr(e1l), parse_expr(e1r)
    t2l, t2r = parse_expr(e2l), parse_expr(e2r)
    vs = sorted(get_variables(t1l) | get_variables(t1r) | get_variables(t2l) | get_variables(t2r))
    parsed_true.append((p["id"], t1l, t1r, t2l, t2r, vs))


print("Checking 3-element magmas (19683 operations)...")
start = time.time()

# For each FALSE pair, find which 3-element magmas separate it
pair_sep_count = {pid: 0 for pid, *_ in parsed_false}
total_seps = {}

n = 3
checked = 0
for op_tuple in itertools.product(range(n), repeat=n*n):
    op_table = list(op_tuple)
    checked += 1
    if checked % 2000 == 0:
        elapsed = time.time() - start
        print(f"  Checked {checked}/19683 ops ({elapsed:.1f}s)...")
    
    for pid, t1l, t1r, t2l, t2r, vs in parsed_false:
        e1_holds = equation_holds(t1l, t1r, op_table, n, vs)
        if not e1_holds:
            continue
        e2_holds = equation_holds(t2l, t2r, op_table, n, vs)
        if not e2_holds:
            pair_sep_count[pid] += 1
            if pid not in total_seps:
                total_seps[pid] = []
            if len(total_seps[pid]) < 3:  # Store first 3 separating magmas
                total_seps[pid].append(op_tuple)

elapsed = time.time() - start
print(f"\nDone in {elapsed:.1f}s")

print("\n" + "=" * 80)
print("HARD3 FALSE: 3-ELEMENT MAGMA SEPARATION RESULTS")
print("=" * 80)
for pid, *_ in parsed_false:
    cnt = pair_sep_count[pid]
    examples = total_seps.get(pid, [])
    if cnt > 0:
        # Format first example as 3x3 table
        ex = examples[0]
        table = [[ex[i*3+j] for j in range(3)] for i in range(3)]
        print(f"{pid}: {cnt} separating magmas found. First: {table}")
    else:
        print(f"{pid}: NONE")

sep_found = sum(1 for v in pair_sep_count.values() if v > 0)
print(f"\nSeparable by some 3-element magma: {sep_found}/{len(false_pairs)}")
print(f"Unseparable: {len(false_pairs) - sep_found}/{len(false_pairs)}")

# Check FP rate for the most common separating magmas
if total_seps:
    # Collect all first-separating magmas
    all_first = set()
    for pid, exs in total_seps.items():
        for ex in exs:
            all_first.add(ex)
    
    print(f"\nChecking {len(all_first)} unique separating magmas for FP against TRUE pairs...")
    best_magma = None
    best_net = -999
    
    for op_tuple in all_first:
        op_table = list(op_tuple)
        catches = 0
        fps = 0
        for pid, t1l, t1r, t2l, t2r, vs in parsed_false:
            e1 = equation_holds(t1l, t1r, op_table, n, vs)
            if e1 and not equation_holds(t2l, t2r, op_table, n, vs):
                catches += 1
        for pid, t1l, t1r, t2l, t2r, vs in parsed_true:
            e1 = equation_holds(t1l, t1r, op_table, n, vs)
            if e1 and not equation_holds(t2l, t2r, op_table, n, vs):
                fps += 1
        net = catches - fps
        if net > best_net:
            best_net = net
            best_magma = op_tuple
            best_catches = catches
            best_fps = fps
    
    table = [[best_magma[i*3+j] for j in range(3)] for i in range(3)]
    print(f"\nBest single 3-element magma:")
    print(f"  Table: {table}")
    print(f"  Catches: {best_catches}/{len(false_pairs)} FALSE")
    print(f"  FP: {best_fps}/{len(true_pairs)} TRUE")
    print(f"  Net: {best_net:+d}")
