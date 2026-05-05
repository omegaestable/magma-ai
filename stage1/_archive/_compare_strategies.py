"""Compare T3R/T3L (v26c) vs T4A-universal, and their combination."""
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

# Magma tables
T3R = [[1,2,0],[1,2,0],[1,2,0]]  # a*b = (b+1) mod 3, ignores a
T3L = [[1,1,1],[2,2,2],[0,0,0]]  # a*b = (a+1) mod 3, ignores b
T4A = [[0,1,2],[2,0,1],[1,2,0]]  # a*b = (2a+b) mod 3
XOR = [[0,1,2],[1,2,0],[2,0,1]]  # a*b = (a+b) mod 3

def get_vars(e1, e2):
    seen = []
    for s in [e1, e2]:
        for c in s:
            if c.isalpha() and c not in seen: seen.append(c)
    return seen

# v26c-style default assignment: first=0, second=1, third=2, then cycle
def default_asgn(vl):
    return {v: [0,1,2][i % 3] for i, v in enumerate(vl)}

problems = [json.loads(l) for l in open('data/benchmark/hard3_balanced50_true10_false40_rotation0020_20260417_002534.jsonl')]

def check_separation(e1_l, e1_r, e2_l, e2_r, asgn, table):
    """Check if assignment separates (E1 holds, E2 fails) in given magma."""
    try:
        e1lv = eval_expr(e1_l, asgn, table)
        e1rv = eval_expr(e1_r, asgn, table)
        if e1lv != e1rv: return False  # E1 doesn't hold
        e2lv = eval_expr(e2_l, asgn, table)
        e2rv = eval_expr(e2_r, asgn, table)
        return e2lv != e2rv  # Separation if E2 fails
    except:
        return False

def check_universal_sep(e1_l, e1_r, e2_l, e2_r, vl, table, assignments):
    """Check if E1 holds on ALL assignments; if so, check if E2 fails on any."""
    for a in assignments:
        try:
            if eval_expr(e1_l, a, table) != eval_expr(e1_r, a, table):
                return False  # E1 fails on this assignment, not universal
        except:
            return False
    # E1 holds on all! Check E2
    for a in assignments:
        try:
            if eval_expr(e2_l, a, table) != eval_expr(e2_r, a, table):
                return True  # E2 fails → separation
        except:
            pass
    return False

t4a_asgs = lambda vl: [
    {v: 1 for v in vl},
    {v: [1,2][i%2] for i,v in enumerate(vl)},
    {v: [2,0][i%2] for i,v in enumerate(vl)},
    {v: [0,1,2][i%3] for i,v in enumerate(vl)},
]

# Count catches for each strategy
t3r_catches = set()
t3l_catches = set()
t4a_uni_catches = set()
t3r_fn = set()
t3l_fn = set()
t4a_uni_fn = set()

for p in problems:
    e1, e2 = p['equation1'], p['equation2']
    e1p = e1.split(' = '); e2p = e2.split(' = ')
    e1_l, e1_r = parse_expr(e1p[0]), parse_expr(e1p[1])
    e2_l, e2_r = parse_expr(e2p[0]), parse_expr(e2p[1])
    vl = get_vars(e1, e2)
    da = default_asgn(vl)
    
    pid = p['id']
    is_true = p['answer'] is True
    
    # T3R with default assignment
    if check_separation(e1_l, e1_r, e2_l, e2_r, da, T3R):
        if is_true: t3r_fn.add(pid)
        else: t3r_catches.add(pid)
    
    # T3L with default assignment
    if check_separation(e1_l, e1_r, e2_l, e2_r, da, T3L):
        if is_true: t3l_fn.add(pid)
        else: t3l_catches.add(pid)
    
    # T4A universal
    if check_universal_sep(e1_l, e1_r, e2_l, e2_r, vl, T4A, t4a_asgs(vl)):
        if is_true: t4a_uni_fn.add(pid)
        else: t4a_uni_catches.add(pid)

print("=== Individual strategies ===")
print(f"T3R (default asgn):       FALSE caught: {len(t3r_catches)}/40, FN: {len(t3r_fn)}")
print(f"T3L (default asgn):       FALSE caught: {len(t3l_catches)}/40, FN: {len(t3l_fn)}")
print(f"T4A universal (all 4):    FALSE caught: {len(t4a_uni_catches)}/40, FN: {len(t4a_uni_fn)}")

# Combinations
t3rl = t3r_catches | t3l_catches
t3rl_fn = t3r_fn | t3l_fn
print(f"\nT3R+T3L (v26c rescue):    FALSE caught: {len(t3rl)}/40, FN: {len(t3rl_fn)}")
print(f"  T3R-only: {t3r_catches - t3l_catches}")
print(f"  T3L-only: {t3l_catches - t3r_catches}")

combo = t3rl | t4a_uni_catches
combo_fn = t3rl_fn | t4a_uni_fn
print(f"\nT3R+T3L+T4A-uni (v26h):   FALSE caught: {len(combo)}/40, FN: {len(combo_fn)}")
new_from_t4a = t4a_uni_catches - t3rl
print(f"  NEW from T4A-uni: {len(new_from_t4a)} → {new_from_t4a}")

# Project 50/50 accuracy
for name, catches, fns in [("v26c T3R+T3L", t3rl, t3rl_fn), 
                            ("v26h +T4A-uni", combo, combo_fn)]:
    true_correct = 10 - len(fns)
    false_correct = len(catches)
    # At 10T/40F (our benchmark)
    pct = 100 * (true_correct + false_correct) / 50
    # At 10T/10F (50/50)
    # Scale FALSE: catches/40 × 10
    false_50 = round(len(catches) / 40 * 10, 1)
    pct_50 = 100 * (true_correct + false_50) / 20
    print(f"\n{name}:")
    print(f"  At 10T/40F: TRUE {true_correct}/10, FALSE {false_correct}/40, Overall {true_correct+false_correct}/50 = {pct:.1f}%")
    print(f"  At 10T/10F: TRUE {true_correct}/10, FALSE ~{false_50}/10, Overall ~{true_correct+false_50}/20 = {pct_50:.1f}%")
