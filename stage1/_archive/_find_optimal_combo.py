"""Find the best single-assignment strategy: 1 T4A + 1 XOR assignment."""
import json
from itertools import product

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

T4A = [[0,1,2],[2,0,1],[1,2,0]]
XOR = [[0,1,2],[1,2,0],[2,0,1]]

def get_vars(e1, e2):
    seen = []
    for s in [e1, e2]:
        for c in s:
            if c.isalpha() and c not in seen: seen.append(c)
    return seen

problems = [json.loads(l) for l in open('data/benchmark/hard3_balanced50_true10_false40_rotation0020_20260417_002534.jsonl')]

t4a_patterns = [
    ('A1:all-1', lambda vl: {v: 1 for v in vl}),
    ('A2:cyc12', lambda vl: {v: [1,2][i%2] for i,v in enumerate(vl)}),
    ('A3:cyc20', lambda vl: {v: [2,0][i%2] for i,v in enumerate(vl)}),
    ('A4:def012', lambda vl: {v: [0,1,2][i%3] for i,v in enumerate(vl)}),
]
xor_patterns = [
    ('A1:0-1s', lambda vl: {v: (0 if i==0 else 1) for i,v in enumerate(vl)}),
    ('A2:cyc120', lambda vl: {v: [1,2,0][i%3] for i,v in enumerate(vl)}),
]

# Test EVERY combination of 1 T4A + 1 XOR pattern
print("=== Single-assignment per magma: 1 T4A + 1 XOR ===\n")
print(f"{'T4A':<12} {'XOR':<12} {'TRUE':>6} {'FALSE':>6} {'Overall':>8} {'FN':>4} {'FP':>4}")
print("-" * 60)

best_overall = 0
best_combo = None

for t_name, t_fn in t4a_patterns:
    for x_name, x_fn in xor_patterns:
        true_c = 0; false_c = 0; true_t = 0; false_t = 0
        fn = 0; fp = 0
        
        for p in problems:
            e1, e2 = p['equation1'], p['equation2']
            e1p = e1.split(' = '); e2p = e2.split(' = ')
            e1_l, e1_r = parse_expr(e1p[0]), parse_expr(e1p[1])
            e2_l, e2_r = parse_expr(e2p[0]), parse_expr(e2p[1])
            vl = get_vars(e1, e2)
            
            pred_false = False
            # Check T4A with single assignment
            a = t_fn(vl)
            try:
                if eval_expr(e1_l, a, T4A) == eval_expr(e1_r, a, T4A):
                    if eval_expr(e2_l, a, T4A) != eval_expr(e2_r, a, T4A):
                        pred_false = True
            except: pass
            
            # Check XOR with single assignment
            if not pred_false:
                a = x_fn(vl)
                try:
                    if eval_expr(e1_l, a, XOR) == eval_expr(e1_r, a, XOR):
                        if eval_expr(e2_l, a, XOR) != eval_expr(e2_r, a, XOR):
                            pred_false = True
                except: pass
            
            is_true = p['answer'] is True
            if is_true:
                true_t += 1
                if not pred_false: true_c += 1
                else: fn += 1
            else:
                false_t += 1
                if pred_false: false_c += 1
                else: fp += 1
        
        tot = true_c + false_c
        pct = 100 * tot / (true_t + false_t)
        print(f"{t_name:<12} {x_name:<12} {true_c:2}/{true_t:<4} {false_c:2}/{false_t:<4} {tot:2}/{true_t+false_t}={pct:5.1f}% {fn:4} {fp:4}")
        if tot > best_overall:
            best_overall = tot
            best_combo = (t_name, x_name)

print(f"\nBest combo: {best_combo} with {best_overall}/50")

# Also test: 2 T4A + 1 XOR 
print("\n=== 2 T4A + 1 XOR ===\n")
from itertools import combinations
best2 = 0
for (t1n, t1f), (t2n, t2f) in combinations(t4a_patterns, 2):
    for xn, xf in xor_patterns:
        true_c = 0; false_c = 0; true_t = 0; false_t = 0
        for p in problems:
            e1, e2 = p['equation1'], p['equation2']
            e1p = e1.split(' = '); e2p = e2.split(' = ')
            e1_l, e1_r = parse_expr(e1p[0]), parse_expr(e1p[1])
            e2_l, e2_r = parse_expr(e2p[0]), parse_expr(e2p[1])
            vl = get_vars(e1, e2)
            
            pred_false = False
            for fn_maker, table in [(t1f, T4A), (t2f, T4A), (xf, XOR)]:
                a = fn_maker(vl)
                try:
                    if eval_expr(e1_l, a, table) == eval_expr(e1_r, a, table):
                        if eval_expr(e2_l, a, table) != eval_expr(e2_r, a, table):
                            pred_false = True; break
                except: pass
            
            is_true = p['answer'] is True
            if is_true:
                true_t += 1
                if not pred_false: true_c += 1
            else:
                false_t += 1
                if pred_false: false_c += 1
        
        tot = true_c + false_c
        if tot > best2:
            best2 = tot
            best2_combo = (t1n, t2n, xn, true_c, false_c)

print(f"Best 2T4A+1XOR: {best2_combo[:3]} → TRUE {best2_combo[3]}/10 FALSE {best2_combo[4]}/40 Overall {best2}/50")
