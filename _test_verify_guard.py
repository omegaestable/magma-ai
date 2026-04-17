"""Test whether 'verify E1 with all-2' guard would save TRUE problems from FN."""
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

def make_assignments(vl):
    return {
        'T4A_A1': ({v: 1 for v in vl}, T4A),
        'T4A_A2': ({v: [1,2][i%2] for i,v in enumerate(vl)}, T4A),
        'T4A_A3': ({v: [2,0][i%2] for i,v in enumerate(vl)}, T4A),
        'T4A_A4': ({v: [0,1,2][i%3] for i,v in enumerate(vl)}, T4A),
        'XOR_A1': ({v: (0 if i==0 else 1) for i,v in enumerate(vl)}, XOR),
        'XOR_A2': ({v: [1,2,0][i%3] for i,v in enumerate(vl)}, XOR),
    }

problems = [json.loads(l) for l in open('data/benchmark/hard3_balanced50_true10_false40_rotation0020_20260417_002534.jsonl')]
true_probs = [p for p in problems if p['answer'] is True]

# Verification assignment: all-2
def make_verify(vl, table_name):
    table = T4A if table_name == 'T4A' else XOR
    return {v: 2 for v in vl}, table

print("=== Testing all-2 verification guard on TRUE problems ===\n")

saved_by_all2 = 0
not_saved = 0

for p in true_probs:
    e1, e2 = p['equation1'], p['equation2']
    e1_parts = e1.split(' = ')
    e2_parts = e2.split(' = ')
    e1_l, e1_r = parse_expr(e1_parts[0]), parse_expr(e1_parts[1])
    e2_l, e2_r = parse_expr(e2_parts[0]), parse_expr(e2_parts[1])
    vl = get_vars(e1, e2)
    assignments = make_assignments(vl)
    
    print(f"{p['id']}: E1={e1}")
    
    for aname, (avals, table) in assignments.items():
        try:
            e1_lv = eval_expr(e1_l, avals, table)
            e1_rv = eval_expr(e1_r, avals, table)
            e2_lv = eval_expr(e2_l, avals, table)
            e2_rv = eval_expr(e2_r, avals, table)
        except:
            continue
        
        if e1_lv == e1_rv and e2_lv != e2_rv:
            # False separation found! Check verification
            tname = 'T4A' if 'T4A' in aname else 'XOR'
            verify_asgn, verify_table = make_verify(vl, tname)
            try:
                ve1_l = eval_expr(e1_l, verify_asgn, verify_table)
                ve1_r = eval_expr(e1_r, verify_asgn, verify_table)
            except:
                print(f"  {aname}: false sep, verification ERROR")
                continue
            
            if ve1_l != ve1_r:
                print(f"  {aname}: false sep → all-2 check: E1 fails ({ve1_l}≠{ve1_r}) → SAVED!")
                saved_by_all2 += 1
            else:
                # Also check E2 with all-2
                try:
                    ve2_l = eval_expr(e2_l, verify_asgn, verify_table)
                    ve2_r = eval_expr(e2_r, verify_asgn, verify_table)
                except:
                    print(f"  {aname}: false sep → all-2 E1 holds but E2 check ERROR")
                    not_saved += 1
                    continue
                if ve2_l != ve2_r:
                    print(f"  {aname}: false sep → all-2 E1 holds, E2 also fails → NOT SAVED (double false sep)")
                    not_saved += 1
                else:
                    print(f"  {aname}: false sep → all-2 E1 holds, E2 holds → SAVED (inconsistent)")
                    saved_by_all2 += 1
            break  # Only check first false separation (model stops at first)
    else:
        print(f"  SAFE: no false separation")

print(f"\n=== Summary ===")
print(f"Saved by all-2 guard: {saved_by_all2}/10")
print(f"Not saved: {not_saved}/10")

# Now check: does all-2 guard break any legitimate FALSE detections?
print(f"\n=== Checking FALSE problems: does all-2 guard break legitimate separations? ===")
false_probs = [p for p in problems if p['answer'] is False]
broken = 0
total_sep = 0
for p in false_probs:
    e1, e2 = p['equation1'], p['equation2']
    e1_parts = e1.split(' = ')
    e2_parts = e2.split(' = ')
    e1_l, e1_r = parse_expr(e1_parts[0]), parse_expr(e1_parts[1])
    e2_l, e2_r = parse_expr(e2_parts[0]), parse_expr(e2_parts[1])
    vl = get_vars(e1, e2)
    assignments = make_assignments(vl)
    
    for aname, (avals, table) in assignments.items():
        try:
            e1_lv = eval_expr(e1_l, avals, table)
            e1_rv = eval_expr(e1_r, avals, table)
            e2_lv = eval_expr(e2_l, avals, table)
            e2_rv = eval_expr(e2_r, avals, table)
        except:
            continue
        
        if e1_lv == e1_rv and e2_lv != e2_rv:
            total_sep += 1
            tname = 'T4A' if 'T4A' in aname else 'XOR'
            verify_asgn, verify_table = make_verify(vl, tname)
            try:
                ve1_l = eval_expr(e1_l, verify_asgn, verify_table)
                ve1_r = eval_expr(e1_r, verify_asgn, verify_table)
            except:
                continue
            if ve1_l != ve1_r:
                broken += 1
            break

print(f"Legitimate separations found: {total_sep}/40")
print(f"Broken by all-2 guard: {broken}/40")
print(f"Still working: {total_sep - broken}/40")
