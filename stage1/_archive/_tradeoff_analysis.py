"""Analyze tradeoffs: keep vs remove T5B/NL1 on competition hard.jsonl."""
import json, itertools

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

def get_all_separators(e1, e2, extra_checks=None):
    """Return dict: test_name -> True if separates. extra_checks: list of additional E1 assignments."""
    e1L, e1R = e1.split('=', 1); e1L, e1R = e1L.strip(), e1R.strip()
    e2L, e2R = e2.split('=', 1); e2L, e2R = e2L.strip(), e2R.strip()
    seps = {}
    
    # LP
    e1h = first_letter(e1L) == first_letter(e1R)
    e2h = first_letter(e2L) == first_letter(e2R)
    if e1h and not e2h: seps['LP'] = True
    
    # RP
    e1h = last_letter(e1L) == last_letter(e1R)
    e2h = last_letter(e2L) == last_letter(e2R)
    if e1h and not e2h: seps['RP'] = True
    
    # C0
    e1ls, e1rs = '*' in e1L, '*' in e1R
    e2ls, e2rs = '*' in e2L, '*' in e2R
    e1_c0 = (e1ls and e1rs) or (not e1ls and not e1rs)
    e2_c0 = (e2ls and e2rs) or (not e2ls and not e2rs)
    if e1_c0 and not e2_c0: seps['C0'] = True
    
    # VARS
    e1_lv = set(c for c in e1L if c.isalpha())
    e1_rv = set(c for c in e1R if c.isalpha())
    e2_lv = set(c for c in e2L if c.isalpha())
    e2_rv = set(c for c in e2R if c.isalpha())
    if e1ls and e1rs: e1vh = e1_lv == e1_rv
    elif not e1ls and not e1rs: e1vh = e1L == e1R
    else:
        b = e1L if not e1ls else e1R
        sv = e1_rv if not e1ls else e1_lv
        e1vh = sv == {b.strip()}
    if e2ls and e2rs: e2vh = e2_lv == e2_rv
    elif not e2ls and not e2rs: e2vh = e2L == e2R
    else:
        b = e2L if not e2ls else e2R
        sv = e2_rv if not e2ls else e2_lv
        e2vh = sv == {b.strip()}
    if e1vh and not e2vh: seps['VARS'] = True
    
    # COUNT2
    from collections import Counter
    e1lc = Counter(c for c in e1L if c.isalpha())
    e1rc = Counter(c for c in e1R if c.isalpha())
    e2lc = Counter(c for c in e2L if c.isalpha())
    e2rc = Counter(c for c in e2R if c.isalpha())
    e1c2 = all(e1lc.get(v,0)%2==e1rc.get(v,0)%2 for v in set(e1lc)|set(e1rc))
    e2c2 = all(e2lc.get(v,0)%2==e2rc.get(v,0)%2 for v in set(e2lc)|set(e2rc))
    if e1c2 and not e2c2: seps['COUNT2'] = True
    
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
        if e1_ld and not e2_ld: seps['LDEPTH'] = True
    
    # SPINE
    # Simplified - skip for now
    
    # Magma tests
    e1Lt = parse_tree(e1L); e1Rt = parse_tree(e1R)
    e2Lt = parse_tree(e2L); e2Rt = parse_tree(e2R)
    all_v = sorted(get_vars(e1Lt)|get_vars(e1Rt)|get_vars(e2Lt)|get_vars(e2Rt))
    n = len(all_v)
    seen = []
    for c in e1 + e2:
        if c.isalpha() and c not in seen: seen.append(c)
    asgn = {v: i%3 for i,v in enumerate(seen)}
    asgn_z = {v: 0 for v in seen}
    
    # Additional guard assignments
    all_assigns = [asgn, asgn_z]
    if extra_checks:
        for ec in extra_checks:
            all_assigns.append({v: ec[i%len(ec)] for i,v in enumerate(seen)})
    
    for mname, table in [("T3R", T3R), ("T3L", T3L)]:
        try:
            e1_ok = True
            for a in all_assigns:
                if eval_tree(e1Lt, a, table) != eval_tree(e1Rt, a, table):
                    e1_ok = False; break
            if not e1_ok: continue
            if eval_tree(e2Lt, asgn, table) != eval_tree(e2Rt, asgn, table):
                seps[mname] = True
        except: pass
    
    for mname, table in [("T5B", T5B), ("NL1", NL1)]:
        if n >= 4: continue
        try:
            # Current cheatsheet: E1 checked on default only (1-check)
            if eval_tree(e1Lt, asgn, table) != eval_tree(e1Rt, asgn, table):
                continue
            # With extra checks
            if extra_checks:
                e1_ok = True
                for a in all_assigns:
                    if eval_tree(e1Lt, a, table) != eval_tree(e1Rt, a, table):
                        e1_ok = False; break
                if not e1_ok: continue
            if eval_tree(e2Lt, asgn, table) != eval_tree(e2Rt, asgn, table):
                seps[mname] = True
        except: pass
    
    return seps

with open('data/hf_cache/hard.jsonl') as f:
    problems = [json.loads(l) for l in f]

true_p = [p for p in problems if p['answer']]
false_p = [p for p in problems if not p['answer']]

# Scenario 1: Current (T5B/NL1 with 1 check)
# Scenario 2: Without T5B/NL1
# Scenario 3: Without T5B/NL1 and T3R/T3L (structural only)
# Scenario 4: T5B/NL1 with extra guard: all-ones
# Scenario 5: T5B/NL1 with extra guard: all-ones + all-twos

scenarios = {
    "Current": {},
    "No T5B/NL1": {"skip_t5b_nl1": True},
    "Structural only": {"skip_all_magma": True},
    "Extra guards (1s,2s)": {"extra": [[1,1,1], [2,2,2]]},
    "Extra guards (1s,2s,01,02)": {"extra": [[1,1,1], [2,2,2], [0,1,0,1], [0,2,0,2]]},
}

for sname, opts in scenarios.items():
    tp = tn = fp = fn = 0
    
    for p in true_p:
        seps = get_all_separators(p['equation1'], p['equation2'], 
                                   extra_checks=opts.get('extra'))
        if opts.get('skip_t5b_nl1'):
            seps = {k:v for k,v in seps.items() if k not in ('T5B','NL1')}
        if opts.get('skip_all_magma'):
            seps = {k:v for k,v in seps.items() if k not in ('T3R','T3L','T5B','NL1')}
        if seps: fn += 1
        else: tp += 1
    
    for p in false_p:
        seps = get_all_separators(p['equation1'], p['equation2'],
                                   extra_checks=opts.get('extra'))
        if opts.get('skip_t5b_nl1'):
            seps = {k:v for k,v in seps.items() if k not in ('T5B','NL1')}
        if opts.get('skip_all_magma'):
            seps = {k:v for k,v in seps.items() if k not in ('T3R','T3L','T5B','NL1')}
        if seps: tn += 1
        else: fp += 1
    
    total = tp + tn
    print(f"{sname}:")
    print(f"  TP={tp} FN={fn} TN={tn} FP={fp}")
    print(f"  Score: {total}/200 = {100*total/200:.1f}%")
    print(f"  TRUE acc: {100*tp/len(true_p):.1f}%  FALSE acc: {100*tn/len(false_p):.1f}%")
    print()

# Also check by pool
print("="*60)
print("POOL COMPARISON")
for pool_name, pool_file in [("hard3", "data/hf_cache/hard3.jsonl"), ("normal", "data/hf_cache/normal.jsonl")]:
    try:
        with open(pool_file) as f:
            pool = [json.loads(l) for l in f]
    except:
        continue
    
    pool_t = [p for p in pool if p['answer']]
    pool_f = [p for p in pool if not p['answer']]
    
    for sname in ["Current", "No T5B/NL1"]:
        opts = scenarios[sname]
        tp = tn = fp = fn = 0
        for p in pool_t:
            seps = get_all_separators(p['equation1'], p['equation2'])
            if opts.get('skip_t5b_nl1'):
                seps = {k:v for k,v in seps.items() if k not in ('T5B','NL1')}
            if seps: fn += 1
            else: tp += 1
        for p in pool_f:
            seps = get_all_separators(p['equation1'], p['equation2'])
            if opts.get('skip_t5b_nl1'):
                seps = {k:v for k,v in seps.items() if k not in ('T5B','NL1')}
            if seps: tn += 1
            else: fp += 1
        print(f"  {pool_name} {sname}: {tp+tn}/{len(pool)} ({100*(tp+tn)/len(pool):.1f}%), FN={fn}")
