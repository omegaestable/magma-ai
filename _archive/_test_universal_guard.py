"""Test: require E1 to hold on ALL T4A (or all XOR) assignments, then check E2."""
import json

def parse_expr(s):
    s = s.strip()
    depth = 0
    split_pos = -1
    for i, c in enumerate(s):
        if c == '(': depth += 1
        elif c == ')': depth -= 1
        elif c == '*' and depth == 0: split_pos = i
    if split_pos >= 0:
        return ('*', parse_expr(s[:split_pos].strip()), parse_expr(s[split_pos+1:].strip()))
    if s.startswith('(') and s.endswith(')'):
        return parse_expr(s[1:-1])
    return ('var', s)

def eval_expr(ast, asgn, table):
    if ast[0] == 'var': return asgn[ast[1]]
    return table[eval_expr(ast[1], asgn, table)][eval_expr(ast[2], asgn, table)]

T4A = [[0,1,2],[2,0,1],[1,2,0]]
XOR = [[0,1,2],[1,2,0],[2,0,1]]

def get_vars(e1, e2):
    seen = []
    for s in [e1, e2]:
        for c in s:
            if c.isalpha() and c not in seen: seen.append(c)
    return seen

def t4a_assignments(vl):
    return [
        ('A1', {v: 1 for v in vl}),
        ('A2', {v: [1,2][i%2] for i,v in enumerate(vl)}),
        ('A3', {v: [2,0][i%2] for i,v in enumerate(vl)}),
        ('A4', {v: [0,1,2][i%3] for i,v in enumerate(vl)}),
    ]

def xor_assignments(vl):
    return [
        ('A1', {v: (0 if i==0 else 1) for i,v in enumerate(vl)}),
        ('A2', {v: [1,2,0][i%3] for i,v in enumerate(vl)}),
    ]

problems = [json.loads(l) for l in open('data/benchmark/hard3_balanced50_true10_false40_rotation0020_20260417_002534.jsonl')]

print("=== STRATEGY: E1 must hold on ALL same-magma assignments ===\n")

true_correct = 0
false_correct = 0
true_total = 0
false_total = 0

for p in problems:
    e1, e2 = p['equation1'], p['equation2']
    e1_parts = e1.split(' = ')
    e2_parts = e2.split(' = ')
    e1_l, e1_r = parse_expr(e1_parts[0]), parse_expr(e1_parts[1])
    e2_l, e2_r = parse_expr(e2_parts[0]), parse_expr(e2_parts[1])
    vl = get_vars(e1, e2)
    
    predicted_false = False
    
    # Check T4A: E1 must hold on ALL 4 assignments
    t4a_asgs = t4a_assignments(vl)
    e1_all_hold = True
    e2_any_fail = False
    for aname, avals in t4a_asgs:
        try:
            e1_lv = eval_expr(e1_l, avals, T4A)
            e1_rv = eval_expr(e1_r, avals, T4A)
        except:
            e1_all_hold = False
            break
        if e1_lv != e1_rv:
            e1_all_hold = False
            break
    
    if e1_all_hold:
        for aname, avals in t4a_asgs:
            try:
                e2_lv = eval_expr(e2_l, avals, T4A)
                e2_rv = eval_expr(e2_r, avals, T4A)
            except:
                continue
            if e2_lv != e2_rv:
                e2_any_fail = True
                break
        if e2_any_fail:
            predicted_false = True
    
    # Check XOR: E1 must hold on ALL 2 assignments
    if not predicted_false:
        xor_asgs = xor_assignments(vl)
        e1_all_hold = True
        for aname, avals in xor_asgs:
            try:
                e1_lv = eval_expr(e1_l, avals, XOR)
                e1_rv = eval_expr(e1_r, avals, XOR)
            except:
                e1_all_hold = False
                break
            if e1_lv != e1_rv:
                e1_all_hold = False
                break
        
        if e1_all_hold:
            for aname, avals in xor_asgs:
                try:
                    e2_lv = eval_expr(e2_l, avals, XOR)
                    e2_rv = eval_expr(e2_r, avals, XOR)
                except:
                    continue
                if e2_lv != e2_rv:
                    predicted_false = True
                    break
    
    is_true = p['answer'] is True
    if is_true:
        true_total += 1
        if not predicted_false:
            true_correct += 1
        else:
            print(f"  FN: {p['id']} E1={e1}")
    else:
        false_total += 1
        if predicted_false:
            false_correct += 1

print(f"\nTRUE accuracy: {true_correct}/{true_total} ({100*true_correct/true_total:.0f}%)")
print(f"FALSE accuracy: {false_correct}/{false_total} ({100*false_correct/false_total:.1f}%)")
print(f"Overall: {true_correct+false_correct}/{true_total+false_total} ({100*(true_correct+false_correct)/(true_total+false_total):.1f}%)")

# Baseline comparison
print(f"\nBaselines:")
print(f"v26c actual:   TRUE 90% (9/10), FALSE 47.5% (19/40), overall 56% (28/50)")
print(f"v26g current:  TRUE 10% (1/10), FALSE 92.5% (37/40), overall 76% (38/50)")
