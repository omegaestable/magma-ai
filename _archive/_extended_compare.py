"""Extended comparison: T3R/T3L + single-assignment T4A/XOR additions."""
import json

def parse_expr(s):
    s = s.strip()
    depth = 0; sp = -1
    for i, c in enumerate(s):
        if c == '(': depth += 1
        elif c == ')': depth -= 1
        elif c == '*' and depth == 0: sp = i
    if sp >= 0: return ('*', parse_expr(s[:sp].strip()), parse_expr(s[sp+1:].strip()))
    if s.startswith('(') and s.endswith(')'): return parse_expr(s[1:-1])
    return ('var', s)

def eval_expr(ast, a, t):
    if ast[0] == 'var': return a[ast[1]]
    return t[eval_expr(ast[1], a, t)][eval_expr(ast[2], a, t)]

T3R = [[1,2,0],[1,2,0],[1,2,0]]
T3L = [[1,1,1],[2,2,2],[0,0,0]]
T4A = [[0,1,2],[2,0,1],[1,2,0]]
XOR = [[0,1,2],[1,2,0],[2,0,1]]
# T5B: a*b = (a+2b) mod 3 (from v27a analysis)
T5B = [[0,2,1],[1,0,2],[2,1,0]]

def get_vars(e1, e2):
    seen = []
    for s in [e1, e2]:
        for c in s:
            if c.isalpha() and c not in seen: seen.append(c)
    return seen

def check_sep(e1_l, e1_r, e2_l, e2_r, asgn, table):
    try:
        e1lv = eval_expr(e1_l, asgn, table)
        e1rv = eval_expr(e1_r, asgn, table)
        if e1lv != e1rv: return False
        e2lv = eval_expr(e2_l, asgn, table)
        e2rv = eval_expr(e2_r, asgn, table)
        return e2lv != e2rv
    except:
        return False

problems = [json.loads(l) for l in open('data/benchmark/hard3_balanced50_true10_false40_rotation0020_20260417_002534.jsonl')]

# Define test configurations
configs = {
    'T3R_def': (T3R, lambda vl: {v: [0,1,2][i%3] for i,v in enumerate(vl)}),
    'T3L_def': (T3L, lambda vl: {v: [0,1,2][i%3] for i,v in enumerate(vl)}),
    'T4A_A1': (T4A, lambda vl: {v: 1 for v in vl}),
    'T4A_A2': (T4A, lambda vl: {v: [1,2][i%2] for i,v in enumerate(vl)}),
    'T4A_A3': (T4A, lambda vl: {v: [2,0][i%2] for i,v in enumerate(vl)}),
    'T4A_A4': (T4A, lambda vl: {v: [0,1,2][i%3] for i,v in enumerate(vl)}),
    'XOR_A1': (XOR, lambda vl: {v: (0 if i==0 else 1) for i,v in enumerate(vl)}),
    'XOR_A2': (XOR, lambda vl: {v: [1,2,0][i%3] for i,v in enumerate(vl)}),
    'T5B_def': (T5B, lambda vl: {v: [0,1,2][i%3] for i,v in enumerate(vl)}),
    'T5B_A1': (T5B, lambda vl: {v: 1 for v in vl}),
}

# Compute catches for each config
results = {}
for cname, (table, asgn_fn) in configs.items():
    catches = set()
    fns = set()
    for p in problems:
        e1, e2 = p['equation1'], p['equation2']
        e1p = e1.split(' = '); e2p = e2.split(' = ')
        e1_l, e1_r = parse_expr(e1p[0]), parse_expr(e1p[1])
        e2_l, e2_r = parse_expr(e2p[0]), parse_expr(e2p[1])
        vl = get_vars(e1, e2)
        asgn = asgn_fn(vl)
        if check_sep(e1_l, e1_r, e2_l, e2_r, asgn, table):
            if p['answer'] is True: fns.add(p['id'])
            else: catches.add(p['id'])
    results[cname] = (catches, fns)
    print(f"{cname:12s}: FALSE {len(catches):2d}/40, FN {len(fns)}")

# Now test combinations: v26c base + each addition
base = results['T3R_def'][0] | results['T3L_def'][0]
base_fn = results['T3R_def'][1] | results['T3L_def'][1]

print(f"\nBase (T3R+T3L): FALSE {len(base)}/40, FN {len(base_fn)}")

# Try adding each single test to the base
additions = ['T4A_A1', 'T4A_A2', 'T4A_A3', 'T4A_A4', 'XOR_A1', 'XOR_A2', 'T5B_def', 'T5B_A1']
print("\n=== Adding ONE more test to T3R+T3L ===")
for add in additions:
    combo_catches = base | results[add][0]
    combo_fn = base_fn | results[add][1]
    new = results[add][0] - base
    new_fn = results[add][1] - base_fn
    print(f"  +{add:12s}: FALSE {len(combo_catches):2d}/40 (+{len(new)}), FN {len(combo_fn)} (+{len(new_fn)}), net +{len(new)-len(new_fn)}")

# Try adding TWO more tests
print("\n=== Adding TWO more tests to T3R+T3L (best combos) ===")
from itertools import combinations
best = (0, None)
for a1, a2 in combinations(additions, 2):
    combo = base | results[a1][0] | results[a2][0]
    fn = base_fn | results[a1][1] | results[a2][1]
    net = len(combo) - len(fn) - (len(base) - len(base_fn))
    if net > best[0]:
        best = (net, (a1, a2, len(combo), len(fn)))
    # Also print all
    new_c = (results[a1][0] | results[a2][0]) - base
    new_f = (results[a1][1] | results[a2][1]) - base_fn
    # Only print interesting ones
    if len(new_c) > len(new_f) + 1:
        print(f"  +{a1}+{a2}: FALSE {len(combo)}/40 (+{len(new_c)}), FN {len(fn)} (+{len(new_f)})")

print(f"\nBest net improvement: {best}")
