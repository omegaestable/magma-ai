"""Check TN impact: how many FALSE problems lose T5B separation when adding all-ones check."""
import json

def parse_tree(s):
    s = s.strip()
    if not s: return s
    if s.startswith('('):
        depth = 0
        for i, c in enumerate(s):
            if c == '(': depth += 1
            elif c == ')': depth -= 1
            if depth == 0:
                if i == len(s) - 1: return parse_tree(s[1:-1])
                break
    depth = 0
    for i, c in enumerate(s):
        if c == '(': depth += 1
        elif c == ')': depth -= 1
        elif c == '*' and depth == 0:
            return ('*', parse_tree(s[:i]), parse_tree(s[i+1:]))
    return s.strip()

def get_vars(tree):
    if isinstance(tree, str): return {tree}
    return get_vars(tree[1]) | get_vars(tree[2])

def eval_tree(tree, assign, table):
    if isinstance(tree, str): return assign[tree]
    l = eval_tree(tree[1], assign, table)
    r = eval_tree(tree[2], assign, table)
    return table[l][r]

T5B = [[0,2,1],[1,0,2],[2,1,0]]
NL1 = [[0,0,0],[1,1,0],[1,2,2]]

with open('data/hf_cache/hard.jsonl') as f:
    problems = [json.loads(l) for l in f]

false_p = [p for p in problems if not p['answer']]

# Check T5B TNs: how many FALSE have T5B separation with default only vs default+all-ones
t5b_tn_current = 0
t5b_tn_with_guard = 0
t5b_lost = []

nl1_tn_current = 0
nl1_tn_with_guard = 0  # with 01-alt guard
nl1_lost = []

for p in false_p:
    e1L_s, e1R_s = p['equation1'].split('=', 1)
    e2L_s, e2R_s = p['equation2'].split('=', 1)
    e1L = parse_tree(e1L_s.strip()); e1R = parse_tree(e1R_s.strip())
    e2L = parse_tree(e2L_s.strip()); e2R = parse_tree(e2R_s.strip())
    all_v = get_vars(e1L)|get_vars(e1R)|get_vars(e2L)|get_vars(e2R)
    n = len(all_v)
    
    seen = []
    for c in p['equation1'] + p['equation2']:
        if c.isalpha() and c not in seen: seen.append(c)
    asgn = {v: i%3 for i,v in enumerate(seen)}
    asgn_ones = {v: 1 for v in seen}
    asgn_01 = {v: i%2 for i,v in enumerate(seen)}
    
    # T5B
    if n < 4:
        try:
            e1_default_ok = eval_tree(e1L, asgn, T5B) == eval_tree(e1R, asgn, T5B)
            if e1_default_ok:
                e2_default_fail = eval_tree(e2L, asgn, T5B) != eval_tree(e2R, asgn, T5B)
                if e2_default_fail:
                    t5b_tn_current += 1
                    # Check all-ones guard
                    e1_ones_ok = eval_tree(e1L, asgn_ones, T5B) == eval_tree(e1R, asgn_ones, T5B)
                    if e1_ones_ok:
                        t5b_tn_with_guard += 1
                    else:
                        t5b_lost.append(p['id'])
        except: pass
    
    # NL1
    if n < 4:
        try:
            e1_default_ok = eval_tree(e1L, asgn, NL1) == eval_tree(e1R, asgn, NL1)
            if e1_default_ok:
                e2_default_fail = eval_tree(e2L, asgn, NL1) != eval_tree(e2R, asgn, NL1)
                if e2_default_fail:
                    nl1_tn_current += 1
                    # Check 01-alt guard
                    e1_01_ok = eval_tree(e1L, asgn_01, NL1) == eval_tree(e1R, asgn_01, NL1)
                    if e1_01_ok:
                        nl1_tn_with_guard += 1
                    else:
                        nl1_lost.append(p['id'])
        except: pass

print(f"T5B on FALSE problems:")
print(f"  Current TN: {t5b_tn_current}")
print(f"  With all-ones guard: {t5b_tn_with_guard}")
print(f"  Lost: {t5b_tn_current - t5b_tn_with_guard}")
if t5b_lost:
    print(f"  Lost IDs: {t5b_lost[:10]}...")

print(f"\nNL1 on FALSE problems:")
print(f"  Current TN: {nl1_tn_current}")
print(f"  With 01-alt guard: {nl1_tn_with_guard}")
print(f"  Lost: {nl1_tn_current - nl1_tn_with_guard}")
if nl1_lost:
    print(f"  Lost IDs: {nl1_lost[:10]}...")

print(f"\nCombined impact (T5B+NL1 guards):")
print(f"  Gained TPs: +7 (T5B) + 3 (NL1) = +10")
print(f"  Lost TNs: -{t5b_tn_current - t5b_tn_with_guard} (T5B) - {nl1_tn_current - nl1_tn_with_guard} (NL1)")
net = 10 - (t5b_tn_current - t5b_tn_with_guard) - (nl1_tn_current - nl1_tn_with_guard)
print(f"  Net: {'+' if net > 0 else ''}{net}")

# Also check impact on hard3 and normal
for pool_name, pool_file in [("hard3", "data/hf_cache/hard3.jsonl"), ("normal", "data/hf_cache/normal.jsonl")]:
    try:
        with open(pool_file) as f:
            pool = [json.loads(l) for l in f]
    except:
        continue
    
    tp_gain = 0; tn_loss = 0
    for p in pool:
        e1L_s, e1R_s = p['equation1'].split('=', 1)
        e2L_s, e2R_s = p['equation2'].split('=', 1)
        e1L = parse_tree(e1L_s.strip()); e1R = parse_tree(e1R_s.strip())
        e2L = parse_tree(e2L_s.strip()); e2R = parse_tree(e2R_s.strip())
        all_v = get_vars(e1L)|get_vars(e1R)|get_vars(e2L)|get_vars(e2R)
        n = len(all_v)
        if n >= 4: continue
        
        seen = []
        for c in p['equation1'] + p['equation2']:
            if c.isalpha() and c not in seen: seen.append(c)
        asgn = {v: i%3 for i,v in enumerate(seen)}
        asgn_ones = {v: 1 for v in seen}
        asgn_01 = {v: i%2 for i,v in enumerate(seen)}
        
        for mname, table, guard_asgn in [("T5B", T5B, asgn_ones), ("NL1", NL1, asgn_01)]:
            try:
                e1_ok = eval_tree(e1L, asgn, table) == eval_tree(e1R, asgn, table)
                if not e1_ok: continue
                e2_fail = eval_tree(e2L, asgn, table) != eval_tree(e2R, asgn, table)
                if not e2_fail: continue
                # This is a separation. Would guard block it?
                e1_guard_ok = eval_tree(e1L, guard_asgn, table) == eval_tree(e1R, guard_asgn, table)
                if not e1_guard_ok:
                    # Guard blocks this separation
                    if p['answer']:
                        tp_gain += 1  # Was false sep on TRUE, now fixed
                    else:
                        tn_loss += 1  # Was correct sep on FALSE, now blocked
            except: pass
    
    print(f"\n{pool_name}: TP gain={tp_gain}, TN loss={tn_loss}, net={tp_gain - tn_loss}")
