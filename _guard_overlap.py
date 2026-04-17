"""Correct analysis: account for overlap between tests when evaluating guard impact."""
import json
from collections import Counter

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

T3R = [[1,2,0],[1,2,0],[1,2,0]]
T3L = [[1,1,1],[2,2,2],[0,0,0]]
T5B = [[0,2,1],[1,0,2],[2,1,0]]
NL1 = [[0,0,0],[1,1,0],[1,2,2]]

def first_letter(s):
    for c in s:
        if c.isalpha(): return c
    return None
def last_letter(s):
    for c in reversed(s):
        if c.isalpha(): return c
    return None

def get_separators(e1_str, e2_str, t5b_guard=None, nl1_guard=None):
    """Return set of tests that separate. Apply guards if provided."""
    e1L, e1R = e1_str.split('=', 1); e1L, e1R = e1L.strip(), e1R.strip()
    e2L, e2R = e2_str.split('=', 1); e2L, e2R = e2L.strip(), e2R.strip()
    seps = set()
    
    # Structural
    if first_letter(e1L) == first_letter(e1R) and first_letter(e2L) != first_letter(e2R):
        seps.add('LP')
    if last_letter(e1L) == last_letter(e1R) and last_letter(e2L) != last_letter(e2R):
        seps.add('RP')
    e1ls, e1rs = '*' in e1L, '*' in e1R
    e2ls, e2rs = '*' in e2L, '*' in e2R
    e1_c0 = (e1ls and e1rs) or (not e1ls and not e1rs)
    e2_c0 = (e2ls and e2rs) or (not e2ls and not e2rs)
    if e1_c0 and not e2_c0: seps.add('C0')
    e1_lv = set(c for c in e1L if c.isalpha()); e1_rv = set(c for c in e1R if c.isalpha())
    e2_lv = set(c for c in e2L if c.isalpha()); e2_rv = set(c for c in e2R if c.isalpha())
    # VARS
    if e1ls and e1rs: e1vh = e1_lv == e1_rv
    elif not e1ls and not e1rs: e1vh = e1L == e1R
    else:
        b = e1L if not e1ls else e1R
        e1vh = (e1_rv if not e1ls else e1_lv) == {b.strip()}
    if e2ls and e2rs: e2vh = e2_lv == e2_rv
    elif not e2ls and not e2rs: e2vh = e2L == e2R
    else:
        b = e2L if not e2ls else e2R
        e2vh = (e2_rv if not e2ls else e2_lv) == {b.strip()}
    if e1vh and not e2vh: seps.add('VARS')
    # COUNT2
    e1lc = Counter(c for c in e1L if c.isalpha())
    e1rc = Counter(c for c in e1R if c.isalpha())
    e2lc = Counter(c for c in e2L if c.isalpha())
    e2rc = Counter(c for c in e2R if c.isalpha())
    e1c2 = all(e1lc.get(v,0)%2==e1rc.get(v,0)%2 for v in set(e1lc)|set(e1rc))
    e2c2 = all(e2lc.get(v,0)%2==e2rc.get(v,0)%2 for v in set(e2lc)|set(e2rc))
    if e1c2 and not e2c2: seps.add('COUNT2')
    # LDEPTH
    if first_letter(e1L) == first_letter(e1R):
        def ldepth(s):
            t = parse_tree(s)
            d = 0
            while isinstance(t, tuple): d += 1; t = t[1]
            return d
        e1_ld = ldepth(e1L) % 2 == ldepth(e1R) % 2
        if first_letter(e2L) == first_letter(e2R):
            e2_ld = ldepth(e2L) % 2 == ldepth(e2R) % 2
        else:
            e2_ld = False
        if e1_ld and not e2_ld: seps.add('LDEPTH')
    
    # Magma tests
    e1Lt = parse_tree(e1L); e1Rt = parse_tree(e1R)
    e2Lt = parse_tree(e2L); e2Rt = parse_tree(e2R)
    all_v = sorted(get_vars(e1Lt)|get_vars(e1Rt)|get_vars(e2Lt)|get_vars(e2Rt))
    n = len(all_v)
    seen = []
    for c in e1_str + e2_str:
        if c.isalpha() and c not in seen: seen.append(c)
    asgn = {v: i%3 for i,v in enumerate(seen)}
    asgn_z = {v: 0 for v in seen}
    
    # T3R, T3L (with all-zeros check)
    for mname, table in [("T3R", T3R), ("T3L", T3L)]:
        try:
            if eval_tree(e1Lt, asgn, table) != eval_tree(e1Rt, asgn, table): continue
            if eval_tree(e1Lt, asgn_z, table) != eval_tree(e1Rt, asgn_z, table): continue
            if eval_tree(e2Lt, asgn, table) != eval_tree(e2Rt, asgn, table):
                seps.add(mname)
        except: pass
    
    # T5B (with optional guard)
    if n < 4:
        try:
            if eval_tree(e1Lt, asgn, T5B) == eval_tree(e1Rt, asgn, T5B):
                blocked = False
                if t5b_guard:
                    g = {v: 1 for v in seen} if t5b_guard == 'all-1' else None
                    if g and eval_tree(e1Lt, g, T5B) != eval_tree(e1Rt, g, T5B):
                        blocked = True
                if not blocked:
                    if eval_tree(e2Lt, asgn, T5B) != eval_tree(e2Rt, asgn, T5B):
                        seps.add('T5B')
        except: pass
    
    # NL1 (with optional guard)
    if n < 4:
        try:
            if eval_tree(e1Lt, asgn, NL1) == eval_tree(e1Rt, asgn, NL1):
                blocked = False
                if nl1_guard:
                    g = {v: i%2 for i,v in enumerate(seen)} if nl1_guard == '01-alt' else None
                    if g and eval_tree(e1Lt, g, NL1) != eval_tree(e1Rt, g, NL1):
                        blocked = True
                if not blocked:
                    if eval_tree(e2Lt, asgn, NL1) != eval_tree(e2Rt, asgn, NL1):
                        seps.add('NL1')
        except: pass
    
    return seps

for pool_name, pool_file in [("hard (competition)", "data/hf_cache/hard.jsonl"), 
                              ("hard3", "data/hf_cache/hard3.jsonl"),
                              ("normal", "data/hf_cache/normal.jsonl")]:
    try:
        with open(pool_file) as f:
            problems = [json.loads(l) for l in f]
    except:
        continue
    
    true_p = [p for p in problems if p['answer']]
    false_p = [p for p in problems if not p['answer']]
    
    # Current: no guards
    # Option A: T5B all-ones guard only
    # Option B: NL1 01-alt guard only
    # Option C: Both guards
    
    for config_name, t5bg, nl1g in [
        ("Current", None, None),
        ("T5B all-ones only", "all-1", None),
        ("NL1 01-alt only", None, "01-alt"),
        ("Both guards", "all-1", "01-alt"),
    ]:
        tp = fn = tn = fp = 0
        for p in true_p:
            s = get_separators(p['equation1'], p['equation2'], t5b_guard=t5bg, nl1_guard=nl1g)
            if s: fn += 1
            else: tp += 1
        for p in false_p:
            s = get_separators(p['equation1'], p['equation2'], t5b_guard=t5bg, nl1_guard=nl1g)
            if s: tn += 1
            else: fp += 1
        total = tp + tn
        print(f"  {pool_name} | {config_name}: {total}/{len(problems)} ({100*total/len(problems):.1f}%) TP={tp} FN={fn} TN={tn} FP={fp}")
    print()
