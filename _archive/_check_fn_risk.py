"""Check which TRUE problems are at risk of false negatives from T4A/XOR assignments."""
import json, re, itertools

def parse_expr(s):
    """Parse equation expression into an AST."""
    s = s.strip()
    # Find the top-level * operation (rightmost * not inside parens)
    depth = 0
    split_pos = -1
    for i, c in enumerate(s):
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
        elif c == '*' and depth == 0:
            split_pos = i
    if split_pos >= 0:
        left = s[:split_pos].strip()
        right = s[split_pos+1:].strip()
        return ('*', parse_expr(left), parse_expr(right))
    # Remove outer parens
    if s.startswith('(') and s.endswith(')'):
        return parse_expr(s[1:-1])
    return ('var', s)

def eval_expr(ast, assignment, table):
    """Evaluate an AST with given variable assignment and magma table."""
    if ast[0] == 'var':
        return assignment[ast[1]]
    left = eval_expr(ast[1], assignment, table)
    right = eval_expr(ast[2], assignment, table)
    return table[left][right]

def get_vars_ordered(e1, e2):
    """Get variables in order of first appearance scanning E1 then E2."""
    seen = []
    for s in [e1, e2]:
        for c in s:
            if c.isalpha() and c not in seen:
                seen.append(c)
    return seen

# T4A: a*b = (2a+b) mod 3
T4A = [[0,1,2],[2,0,1],[1,2,0]]
# XOR: a*b = (a+b) mod 3
XOR = [[0,1,2],[1,2,0],[2,0,1]]

# Assignments
def make_assignments(vars_list):
    n = len(vars_list)
    assignments = {}
    # T4A A1: all=1
    assignments['T4A_A1'] = {v: 1 for v in vars_list}
    # T4A A2: cycle 1,2
    assignments['T4A_A2'] = {v: [1,2][i%2] for i,v in enumerate(vars_list)}
    # T4A A3: cycle 2,0
    assignments['T4A_A3'] = {v: [2,0][i%2] for i,v in enumerate(vars_list)}
    # T4A A4: cycle 0,1,2
    assignments['T4A_A4'] = {v: [0,1,2][i%3] for i,v in enumerate(vars_list)}
    # XOR A1: 1st=0, rest=1
    assignments['XOR_A1'] = {v: (0 if i==0 else 1) for i,v in enumerate(vars_list)}
    # XOR A2: cycle 1,2,0
    assignments['XOR_A2'] = {v: [1,2,0][i%3] for i,v in enumerate(vars_list)}
    return assignments

problems = [json.loads(l) for l in open('data/benchmark/hard3_balanced50_true10_false40_rotation0020_20260417_002534.jsonl')]
true_probs = [p for p in problems if p['answer'] is True]

for p in true_probs:
    e1 = p['equation1']
    e2 = p['equation2']
    e1_parts = e1.split(' = ')
    e2_parts = e2.split(' = ')
    
    e1_l = parse_expr(e1_parts[0])
    e1_r = parse_expr(e1_parts[1])
    e2_l = parse_expr(e2_parts[0])
    e2_r = parse_expr(e2_parts[1])
    
    vars_list = get_vars_ordered(e1, e2)
    assignments = make_assignments(vars_list)
    
    print(f"\n{p['id']}: E1={e1}  E2={e2}")
    print(f"  Vars: {vars_list}")
    
    false_sep = False
    for aname, avals in assignments.items():
        table = T4A if 'T4A' in aname else XOR
        try:
            e1_lv = eval_expr(e1_l, avals, table)
            e1_rv = eval_expr(e1_r, avals, table)
            e2_lv = eval_expr(e2_l, avals, table)
            e2_rv = eval_expr(e2_r, avals, table)
        except (KeyError, IndexError) as ex:
            print(f"  {aname}: ERROR {ex}")
            continue
        
        e1_holds = (e1_lv == e1_rv)
        e2_holds = (e2_lv == e2_rv)
        
        if e1_holds and not e2_holds:
            print(f"  {aname}: {avals} -> E1={e1_lv}={e1_rv}✓ E2={e2_lv}≠{e2_rv} -> FALSE SEPARATION!")
            false_sep = True
        elif e1_holds:
            print(f"  {aname}: {avals} -> E1✓ E2✓ (both hold)")
        else:
            pass  # E1 fails, skip silently
    
    if not false_sep:
        print(f"  -> SAFE: no false separation from any assignment")
