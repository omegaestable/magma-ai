"""Test hybrid approach: per-magma threshold."""
import json
from itertools import combinations

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

# Try multiple strategies
strategies = [
    # (name, t4a_threshold, xor_threshold)
    ("v26g current (1,1)", 1, 1),
    ("safe (2,2)", 2, 2),
    ("t4a-safe (2,1)", 2, 1),
    ("t4a-2-xor-2", 2, 2),
    ("t4a-3-xor-1", 3, 1),
    ("t4a-3-xor-2", 3, 2),
]

for sname, t4a_thresh, xor_thresh in strategies:
    true_c = 0; false_c = 0; true_t = 0; false_t = 0
    fn_list = []; fp_list = []
    
    for p in problems:
        e1, e2 = p['equation1'], p['equation2']
        e1p = e1.split(' = '); e2p = e2.split(' = ')
        e1_l, e1_r = parse_expr(e1p[0]), parse_expr(e1p[1])
        e2_l, e2_r = parse_expr(e2p[0]), parse_expr(e2p[1])
        vl = get_vars(e1, e2)
        
        t4a_asgs = [
            {v: 1 for v in vl},
            {v: [1,2][i%2] for i,v in enumerate(vl)},
            {v: [2,0][i%2] for i,v in enumerate(vl)},
            {v: [0,1,2][i%3] for i,v in enumerate(vl)},
        ]
        xor_asgs = [
            {v: (0 if i==0 else 1) for i,v in enumerate(vl)},
            {v: [1,2,0][i%3] for i,v in enumerate(vl)},
        ]
        
        predicted_false = False
        
        # T4A pass
        e1_holds = 0
        e2_fails = False
        for a in t4a_asgs:
            try:
                if eval_expr(e1_l, a, T4A) == eval_expr(e1_r, a, T4A):
                    e1_holds += 1
                    if eval_expr(e2_l, a, T4A) != eval_expr(e2_r, a, T4A):
                        e2_fails = True
            except: pass
        if e1_holds >= t4a_thresh and e2_fails:
            predicted_false = True
        
        # XOR pass
        if not predicted_false:
            e1_holds = 0
            e2_fails = False
            for a in xor_asgs:
                try:
                    if eval_expr(e1_l, a, XOR) == eval_expr(e1_r, a, XOR):
                        e1_holds += 1
                        if eval_expr(e2_l, a, XOR) != eval_expr(e2_r, a, XOR):
                            e2_fails = True
                except: pass
            if e1_holds >= xor_thresh and e2_fails:
                predicted_false = True
        
        is_true = p['answer'] is True
        if is_true:
            true_t += 1
            if not predicted_false: true_c += 1
            else: fn_list.append(p['id'])
        else:
            false_t += 1
            if predicted_false: false_c += 1
            else: fp_list.append(p['id'])
    
    tot = true_c + false_c
    print(f"{sname:20s}: TRUE {true_c}/{true_t} ({100*true_c/true_t:5.1f}%) | FALSE {false_c}/{false_t} ({100*false_c/false_t:5.1f}%) | Overall {tot}/{true_t+false_t} ({100*tot/(true_t+false_t):5.1f}%)")
    if fn_list: print(f"  FN: {fn_list}")
