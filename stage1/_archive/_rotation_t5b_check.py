"""Check which TRUE problems in competition hard r23 are vulnerable to T5B unsoundness."""
import json, re

def t5b(a, b):
    return (a + 2*b) % 3

def eval_magma(s, op):
    s = s.strip()
    while s.startswith('(') and s.endswith(')'):
        depth = 0
        balanced = True
        for i, c in enumerate(s):
            if c == '(': depth += 1
            elif c == ')': depth -= 1
            if depth == 0 and i < len(s)-1:
                balanced = False
                break
        if balanced:
            s = s[1:-1].strip()
        else:
            break
    if s.isdigit():
        return int(s)
    depth = 0
    main_star = -1
    for i, c in enumerate(s):
        if c == '(': depth += 1
        elif c == ')': depth -= 1
        elif c == '*' and depth == 0:
            main_star = i
            break
    if main_star == -1:
        return int(s)
    left = s[:main_star].strip()
    right = s[main_star+1:].strip()
    a_val = eval_magma(left, op)
    b_val = eval_magma(right, op)
    return op(a_val, b_val)

def sub_vars(expr, asgn):
    return ''.join(str(asgn[c]) if c.isalpha() else c for c in expr)

def check_t5b(eq1_l, eq1_r, eq2_l, eq2_r, assignment):
    try:
        e1l = eval_magma(sub_vars(eq1_l, assignment), t5b)
        e1r = eval_magma(sub_vars(eq1_r, assignment), t5b)
        e2l = eval_magma(sub_vars(eq2_l, assignment), t5b)
        e2r = eval_magma(sub_vars(eq2_r, assignment), t5b)
        return e1l == e1r, e2l == e2r
    except:
        return None, None

with open('data/benchmark/hard_balanced30_true15_false15_rotation0023_20260417_155001.jsonl') as f:
    rotation = [json.loads(l) for l in f]

rot_true = [p for p in rotation if p['answer'] == True]
print(f'Rotation has {len(rot_true)} TRUE problems')

for p in rot_true:
    pid = p['id']
    eq1_parts = p['equation1'].split('=')
    eq2_parts = p['equation2'].split('=')
    eq1_l, eq1_r = eq1_parts[0].strip(), eq1_parts[1].strip()
    eq2_l, eq2_r = eq2_parts[0].strip(), eq2_parts[1].strip()
    
    all_vars = sorted(set(re.findall(r'[a-z]', p['equation1'] + p['equation2'])))
    if len(all_vars) > 3:
        continue
    
    seen = []
    for c in re.findall(r'[a-z]', p['equation1'] + ' ' + p['equation2']):
        if c not in seen:
            seen.append(c)
    default_asgn = {v: i % 3 for i, v in enumerate(seen)}
    
    e1_def, e2_def = check_t5b(eq1_l, eq1_r, eq2_l, eq2_r, default_asgn)
    
    if e1_def and not e2_def:
        ones_asgn = {v: 1 for v in all_vars}
        e1_ones, _ = check_t5b(eq1_l, eq1_r, eq2_l, eq2_r, ones_asgn)
        status = "CAUGHT by v28d" if not e1_ones else "NOT caught"
        print(f'  {pid}: T5B false sep! All-ones E1={e1_ones} → {status}')

print('\nDone.')
