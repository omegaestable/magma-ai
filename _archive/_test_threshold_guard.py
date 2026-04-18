"""Test multi-assignment confirmation: require E1 to hold on >=2 assignments."""
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
    return [
        ('T4A_A1', {v: 1 for v in vl}, T4A),
        ('T4A_A2', {v: [1,2][i%2] for i,v in enumerate(vl)}, T4A),
        ('T4A_A3', {v: [2,0][i%2] for i,v in enumerate(vl)}, T4A),
        ('T4A_A4', {v: [0,1,2][i%3] for i,v in enumerate(vl)}, T4A),
        ('XOR_A1', {v: (0 if i==0 else 1) for i,v in enumerate(vl)}, XOR),
        ('XOR_A2', {v: [1,2,0][i%3] for i,v in enumerate(vl)}, XOR),
    ]

problems = [json.loads(l) for l in open('data/benchmark/hard3_balanced50_true10_false40_rotation0020_20260417_002534.jsonl')]

# Strategy: For each problem, count how many assignments have E1 hold.
# If E1 holds on >=2 assignments AND E2 fails on any of those, declare FALSE.
# If E1 holds on only 1 assignment, separation is unreliable → skip.

print("=== STRATEGY: Require E1 to hold on >=N assignments before accepting separation ===\n")

for threshold in [2, 3]:
    print(f"\n--- Threshold: E1 must hold on >= {threshold} assignments ---")
    
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
        assignments = make_assignments(vl)
        
        # Count E1 holds and E1+E2 separations
        e1_holds_count = 0
        separation_found = False
        
        for aname, avals, table in assignments:
            try:
                e1_lv = eval_expr(e1_l, avals, table)
                e1_rv = eval_expr(e1_r, avals, table)
            except:
                continue
            if e1_lv == e1_rv:
                e1_holds_count += 1
                try:
                    e2_lv = eval_expr(e2_l, avals, table)
                    e2_rv = eval_expr(e2_r, avals, table)
                except:
                    continue
                if e2_lv != e2_rv:
                    separation_found = True
        
        # Apply threshold: only declare FALSE if E1 holds on >=threshold AND separation exists
        predicted_false = separation_found and e1_holds_count >= threshold
        
        is_true = p['answer'] is True
        if is_true:
            true_total += 1
            if not predicted_false:  # We'd say TRUE (correct)
                true_correct += 1
        else:
            false_total += 1
            if predicted_false:  # We'd say FALSE (correct)
                false_correct += 1
    
    print(f"  TRUE accuracy: {true_correct}/{true_total} ({100*true_correct/true_total:.0f}%)")
    print(f"  FALSE accuracy (rescue only): {false_correct}/{false_total} ({100*false_correct/false_total:.0f}%)")
    print(f"  Overall: {true_correct+false_correct}/{true_total+false_total} ({100*(true_correct+false_correct)/(true_total+false_total):.0f}%)")

# Also test: current strategy (threshold=1, stop at first sep)
print(f"\n--- Current v26g strategy (threshold=1) ---")
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
    assignments = make_assignments(vl)
    
    predicted_false = False
    for aname, avals, table in assignments:
        try:
            e1_lv = eval_expr(e1_l, avals, table)
            e1_rv = eval_expr(e1_r, avals, table)
            e2_lv = eval_expr(e2_l, avals, table)
            e2_rv = eval_expr(e2_r, avals, table)
        except:
            continue
        if e1_lv == e1_rv and e2_lv != e2_rv:
            predicted_false = True
            break
    
    is_true = p['answer'] is True
    if is_true:
        true_total += 1
        if not predicted_false:
            true_correct += 1
    else:
        false_total += 1
        if predicted_false:
            false_correct += 1

print(f"  TRUE accuracy: {true_correct}/{true_total} ({100*true_correct/true_total:.0f}%)")
print(f"  FALSE accuracy (rescue only): {false_correct}/{false_total} ({100*false_correct/false_total:.0f}%)")
print(f"  Overall: {true_correct+false_correct}/{true_total+false_total} ({100*(true_correct+false_correct)/(true_total+false_total):.0f}%)")
