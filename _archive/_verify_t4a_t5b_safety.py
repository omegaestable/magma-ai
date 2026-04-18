"""Verify T4A/T5B safety: check for false separations on TRUE problems."""
import json, re, sys

# ── Magma tables ──
T4A = [[0,1,2],[2,0,1],[1,2,0]]  # a*b = (2a+b) mod 3
T5B = [[0,2,1],[1,0,2],[2,1,0]]  # a*b = (a+2b) mod 3
T3R = [[1,2,0],[1,2,0],[1,2,0]]  # a*b = (b+1) mod 3
T3L = [[1,1,1],[2,2,2],[0,0,0]]  # a*b = (a+1) mod 3

def parse_expr(s):
    s = s.strip()
    if not s:
        raise ValueError("Empty expression")
    # Remove fully-wrapping parens
    while s[0] == '(' and _match(s, 0) == len(s)-1:
        s = s[1:-1].strip()
    # Find main * (leftmost at depth 0)
    depth = 0
    for i, c in enumerate(s):
        if c == '(': depth += 1
        elif c == ')': depth -= 1
        elif c == '*' and depth == 0:
            return ('*', parse_expr(s[:i]), parse_expr(s[i+1:]))
    return s.strip()  # leaf

def _match(s, pos):
    d = 1
    for i in range(pos+1, len(s)):
        if s[i] == '(': d += 1
        elif s[i] == ')':
            d -= 1
            if d == 0: return i
    return -1

def get_vars_ordered(e1, e2):
    seen = []
    for c in e1 + ' ' + e2:
        if c.isalpha() and c not in seen:
            seen.append(c)
    return seen

def default_assign(var_order):
    return {v: i % 3 for i, v in enumerate(var_order)}

def eval_tree(t, assign, table):
    if isinstance(t, str):
        return assign[t]
    a = eval_tree(t[1], assign, table)
    b = eval_tree(t[2], assign, table)
    return table[a][b]

def check_sep(e1_str, e2_str, table):
    """Returns 'SEP', 'E1_FAIL', or 'BOTH_HOLD'."""
    e1l, e1r = e1_str.split('=', 1)
    e2l, e2r = e2_str.split('=', 1)
    var_order = get_vars_ordered(e1_str, e2_str)
    assign = default_assign(var_order)
    n_vars = len(var_order)
    e1lv = eval_tree(parse_expr(e1l), assign, table)
    e1rv = eval_tree(parse_expr(e1r), assign, table)
    if e1lv != e1rv:
        return 'E1_FAIL', n_vars
    e2lv = eval_tree(parse_expr(e2l), assign, table)
    e2rv = eval_tree(parse_expr(e2r), assign, table)
    if e2lv != e2rv:
        return 'SEP', n_vars
    return 'BOTH_HOLD', n_vars

benchmarks = [
    ('hard3', 'data/benchmark/hard3_balanced50_true10_false40_rotation0020_20260417_002534.jsonl'),
    ('normal', 'data/benchmark/normal_balanced60_true30_false30_rotation0020_20260417_002534.jsonl'),
]

for bname, bpath in benchmarks:
    print(f"\n{'='*60}")
    print(f"  Benchmark: {bname}")
    print(f"{'='*60}")
    
    true_fn_t4a = []  # TRUE problems falsely separated by T4A
    true_fn_t5b = []
    false_catch_t4a = []  # FALSE problems caught by T4A
    false_catch_t5b = []
    true_safe = 0
    false_miss = 0
    
    with open(bpath) as f:
        for line in f:
            prob = json.loads(line)
            e1 = prob['equation1']
            e2 = prob['equation2']
            gt = prob['answer']
            pid = prob['id']
            
            r4, nv4 = check_sep(e1, e2, T4A)
            r5, nv5 = check_sep(e1, e2, T5B)
            
            if gt:  # TRUE problem
                if r4 == 'SEP':
                    true_fn_t4a.append((pid, nv4))
                if r5 == 'SEP':
                    true_fn_t5b.append((pid, nv5))
                if r4 != 'SEP' and r5 != 'SEP':
                    true_safe += 1
            else:  # FALSE problem
                if r4 == 'SEP':
                    false_catch_t4a.append((pid, nv4))
                elif r5 == 'SEP':
                    false_catch_t5b.append((pid, nv5))
                else:
                    false_miss += 1
    
    print(f"\n  TRUE problems safe (no FN from T4A or T5B): {true_safe}")
    print(f"  TRUE FN from T4A: {len(true_fn_t4a)}")
    for pid, nv in true_fn_t4a:
        print(f"    {pid} ({nv} vars)")
    print(f"  TRUE FN from T5B: {len(true_fn_t5b)}")
    for pid, nv in true_fn_t5b:
        print(f"    {pid} ({nv} vars)")

    print(f"\n  FALSE caught by T4A: {len(false_catch_t4a)}")
    for pid, nv in false_catch_t4a:
        print(f"    {pid} ({nv} vars)")
    print(f"  FALSE caught by T5B (not T4A): {len(false_catch_t5b)}")
    for pid, nv in false_catch_t5b:
        print(f"    {pid} ({nv} vars)")
    print(f"  FALSE missed by both: {false_miss}")

    # Check with 3-var gate
    fn_t4a_3v = [x for x in true_fn_t4a if x[1] <= 3]
    fn_t5b_3v = [x for x in true_fn_t5b if x[1] <= 3]
    catch_t4a_3v = [x for x in false_catch_t4a if x[1] <= 3]
    catch_t5b_3v = [x for x in false_catch_t5b if x[1] <= 3]
    
    print(f"\n  WITH ≤3-var gate:")
    print(f"    TRUE FN (T4A, ≤3 vars): {len(fn_t4a_3v)}")
    for pid, nv in fn_t4a_3v:
        print(f"      {pid} ({nv} vars)")
    print(f"    TRUE FN (T5B, ≤3 vars): {len(fn_t5b_3v)}")
    for pid, nv in fn_t5b_3v:
        print(f"      {pid} ({nv} vars)")
    print(f"    FALSE caught (T4A, ≤3 vars): {len(catch_t4a_3v)}")
    print(f"    FALSE caught (T5B, ≤3 vars): {len(catch_t5b_3v)}")
