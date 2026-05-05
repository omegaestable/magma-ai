"""Impact of adding all-zeros check to T5B and NL1 specifically."""
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
MAGMAS = {"T3R": T3R, "T3L": T3L, "T5B": T5B, "NL1": NL1}

def first_letter(s):
    for c in s:
        if c.isalpha(): return c
    return None
def last_letter(s):
    for c in reversed(s):
        if c.isalpha(): return c
    return None

def check_structural_sep(e1, e2):
    """Return list of structural tests that separate E1,E2."""
    e1L, e1R = e1.split('=', 1); e1L, e1R = e1L.strip(), e1R.strip()
    e2L, e2R = e2.split('=', 1); e2L, e2R = e2L.strip(), e2R.strip()
    seps = []
    # LP
    e1h = first_letter(e1L) == first_letter(e1R)
    e2h = first_letter(e2L) == first_letter(e2R)
    if e1h and not e2h: seps.append('LP')
    # RP
    e1h = last_letter(e1L) == last_letter(e1R)
    e2h = last_letter(e2L) == last_letter(e2R)
    if e1h and not e2h: seps.append('RP')
    # C0
    e1l_star, e1r_star = '*' in e1L, '*' in e1R
    e2l_star, e2r_star = '*' in e2L, '*' in e2R
    e1h = (e1l_star and e1r_star) or (not e1l_star and not e1r_star and e1L==e1R)
    e2h = (e2l_star and e2r_star) or (not e2l_star and not e2r_star and e2L==e2R)
    if not (e1l_star == e1r_star or (not e1l_star and not e1r_star)): e1h = e1l_star == e1r_star
    if not (e2l_star == e2r_star or (not e2l_star and not e2r_star)): e2h = e2l_star == e2r_star
    # Simplified C0
    e1_c0 = (e1l_star and e1r_star) or (not e1l_star and not e1r_star)
    e2_c0 = (e2l_star and e2r_star) or (not e2l_star and not e2r_star)
    if e1_c0 and not e2_c0: seps.append('C0')
    # VARS
    e1_lv = set(c for c in e1L if c.isalpha())
    e1_rv = set(c for c in e1R if c.isalpha())
    e2_lv = set(c for c in e2L if c.isalpha())
    e2_rv = set(c for c in e2R if c.isalpha())
    if e1l_star and e1r_star: e1_vars_h = e1_lv == e1_rv
    elif not e1l_star and not e1r_star: e1_vars_h = e1L == e1R
    else:
        bare = e1L if not e1l_star else e1R
        star_vars = e1_rv if not e1l_star else e1_lv
        e1_vars_h = star_vars == {bare.strip()}
    if e2l_star and e2r_star: e2_vars_h = e2_lv == e2_rv
    elif not e2l_star and not e2r_star: e2_vars_h = e2L == e2R
    else:
        bare = e2L if not e2l_star else e2R
        star_vars = e2_rv if not e2l_star else e2_lv
        e2_vars_h = star_vars == {bare.strip()}
    if e1_vars_h and not e2_vars_h: seps.append('VARS')
    # COUNT2
    from collections import Counter
    e1_lc = Counter(c for c in e1L if c.isalpha())
    e1_rc = Counter(c for c in e1R if c.isalpha())
    e2_lc = Counter(c for c in e2L if c.isalpha())
    e2_rc = Counter(c for c in e2R if c.isalpha())
    e1_c2 = all(e1_lc.get(v,0)%2==e1_rc.get(v,0)%2 for v in set(e1_lc)|set(e1_rc))
    e2_c2 = all(e2_lc.get(v,0)%2==e2_rc.get(v,0)%2 for v in set(e2_lc)|set(e2_rc))
    if e1_c2 and not e2_c2: seps.append('COUNT2')
    # LDEPTH (simplified)
    if first_letter(e1L) == first_letter(e1R):
        def ldepth(s):
            t = parse_tree(s)
            d=0
            while isinstance(t,tuple): d+=1; t=t[1]
            return d
        e1_ld = ldepth(e1L)%2 == ldepth(e1R)%2
        if first_letter(e2L) == first_letter(e2R):
            e2_ld = ldepth(e2L)%2 == ldepth(e2R)%2
        else:
            e2_ld = False  # LP fails for E2 → LDEPTH=FAIL
        if e1_ld and not e2_ld: seps.append('LDEPTH')
    return seps

def magma_sep(e1, e2, use_allzeros=True, magmas_to_check=None):
    """Return list of magma tests that separate. If use_allzeros, check E1 on all-zeros too."""
    e1L_s, e1R_s = e1.split('=', 1)
    e2L_s, e2R_s = e2.split('=', 1)
    e1L = parse_tree(e1L_s.strip()); e1R = parse_tree(e1R_s.strip())
    e2L = parse_tree(e2L_s.strip()); e2R = parse_tree(e2R_s.strip())
    all_v = sorted(get_vars(e1L)|get_vars(e1R)|get_vars(e2L)|get_vars(e2R))
    n = len(all_v)
    seen = []
    for c in e1 + e2:
        if c.isalpha() and c not in seen: seen.append(c)
    asgn = {v: i%3 for i,v in enumerate(seen)}
    asgn_z = {v: 0 for v in seen}
    seps = []
    for name, table in (magmas_to_check or MAGMAS).items():
        if name in ('T5B','NL1') and n >= 4: continue
        try:
            if eval_tree(e1L, asgn, table) != eval_tree(e1R, asgn, table): continue
            if use_allzeros:
                if eval_tree(e1L, asgn_z, table) != eval_tree(e1R, asgn_z, table): continue
            if eval_tree(e2L, asgn, table) != eval_tree(e2R, asgn, table):
                seps.append(name)
        except: pass
    return seps

with open('data/hf_cache/hard.jsonl') as f:
    problems = [json.loads(l) for l in f]

true_p = [p for p in problems if p['answer']]
false_p = [p for p in problems if not p['answer']]

# Current cheatsheet behavior:
# T3R, T3L: use all-zeros check
# T5B, NL1: NO all-zeros check (1-check only)
# Proposed: add all-zeros to T5B and NL1

# Score with current behavior
tp_curr = 0; tn_curr = 0; fp_curr = 0; fn_curr = 0
tp_prop = 0; tn_prop = 0; fp_prop = 0; fn_prop = 0

for p in true_p:
    # Current: T3R/T3L with 2-check, T5B/NL1 with 1-check
    struct_s = check_structural_sep(p['equation1'], p['equation2'])
    t3_s = magma_sep(p['equation1'], p['equation2'], use_allzeros=True, magmas_to_check={"T3R": T3R, "T3L": T3L})
    t5_s = magma_sep(p['equation1'], p['equation2'], use_allzeros=False, magmas_to_check={"T5B": T5B, "NL1": NL1})
    curr_sep = struct_s + t3_s + t5_s
    
    # Proposed: all with 2-check
    t5_prop = magma_sep(p['equation1'], p['equation2'], use_allzeros=True, magmas_to_check={"T5B": T5B, "NL1": NL1})
    prop_sep = struct_s + t3_s + t5_prop
    
    if curr_sep: fn_curr += 1
    else: tp_curr += 1
    if prop_sep: fn_prop += 1
    else: tp_prop += 1

for p in false_p:
    struct_s = check_structural_sep(p['equation1'], p['equation2'])
    t3_s = magma_sep(p['equation1'], p['equation2'], use_allzeros=True, magmas_to_check={"T3R": T3R, "T3L": T3L})
    t5_s = magma_sep(p['equation1'], p['equation2'], use_allzeros=False, magmas_to_check={"T5B": T5B, "NL1": NL1})
    curr_sep = struct_s + t3_s + t5_s
    
    t5_prop = magma_sep(p['equation1'], p['equation2'], use_allzeros=True, magmas_to_check={"T5B": T5B, "NL1": NL1})
    prop_sep = struct_s + t3_s + t5_prop
    
    if curr_sep: tn_curr += 1
    else: fp_curr += 1
    if prop_sep: tn_prop += 1
    else: fp_prop += 1

print("COMPETITION hard.jsonl (200 problems: 74T / 126F)")
print()
print(f"CURRENT (T5B/NL1 without all-zeros check):")
print(f"  TP: {tp_curr}  FN: {fn_curr}  (TRUE acc: {100*tp_curr/len(true_p):.1f}%)")
print(f"  TN: {tn_curr}  FP: {fp_curr}  (FALSE acc: {100*tn_curr/len(false_p):.1f}%)")
print(f"  Total: {tp_curr+tn_curr}/200 = {100*(tp_curr+tn_curr)/200:.1f}%")
print()
print(f"PROPOSED (T5B/NL1 WITH all-zeros check):")
print(f"  TP: {tp_prop}  FN: {fn_prop}  (TRUE acc: {100*tp_prop/len(true_p):.1f}%)")
print(f"  TN: {tn_prop}  FP: {fp_prop}  (FALSE acc: {100*tn_prop/len(false_p):.1f}%)")
print(f"  Total: {tp_prop+tn_prop}/200 = {100*(tp_prop+tn_prop)/200:.1f}%")
print()
print(f"DELTA: TP {tp_prop-tp_curr:+d}, TN {tn_prop-tn_curr:+d}, Net {(tp_prop+tn_prop)-(tp_curr+tn_curr):+d}")
print()

# Also check hard3 and normal pools
for pool_name, pool_file in [("hard3", "data/hf_cache/hard3.jsonl"), ("normal", "data/hf_cache/normal.jsonl")]:
    try:
        with open(pool_file) as f:
            pool = [json.loads(l) for l in f]
    except:
        print(f"Skipping {pool_name}: file not found")
        continue
    
    pool_true = [p for p in pool if p['answer']]
    pool_false = [p for p in pool if not p['answer']]
    
    curr_ok = 0; prop_ok = 0
    curr_fn = 0; prop_fn = 0
    curr_tn = 0; prop_tn = 0
    
    for p in pool_true:
        struct_s = check_structural_sep(p['equation1'], p['equation2'])
        t3_s = magma_sep(p['equation1'], p['equation2'], use_allzeros=True, magmas_to_check={"T3R": T3R, "T3L": T3L})
        t5_curr = magma_sep(p['equation1'], p['equation2'], use_allzeros=False, magmas_to_check={"T5B": T5B, "NL1": NL1})
        t5_prop = magma_sep(p['equation1'], p['equation2'], use_allzeros=True, magmas_to_check={"T5B": T5B, "NL1": NL1})
        if struct_s + t3_s + t5_curr: curr_fn += 1
        else: curr_ok += 1
        if struct_s + t3_s + t5_prop: prop_fn += 1
        else: prop_ok += 1
    
    for p in pool_false:
        struct_s = check_structural_sep(p['equation1'], p['equation2'])
        t3_s = magma_sep(p['equation1'], p['equation2'], use_allzeros=True, magmas_to_check={"T3R": T3R, "T3L": T3L})
        t5_curr = magma_sep(p['equation1'], p['equation2'], use_allzeros=False, magmas_to_check={"T5B": T5B, "NL1": NL1})
        t5_prop = magma_sep(p['equation1'], p['equation2'], use_allzeros=True, magmas_to_check={"T5B": T5B, "NL1": NL1})
        if struct_s + t3_s + t5_curr: curr_tn += 1
        if struct_s + t3_s + t5_prop: prop_tn += 1
    
    curr_total = curr_ok + curr_tn
    prop_total = prop_ok + prop_tn
    print(f"{pool_name} ({len(pool)} problems: {len(pool_true)}T / {len(pool_false)}F)")
    print(f"  Current: {curr_total}/{len(pool)} ({100*curr_total/len(pool):.1f}%), FN={curr_fn}")
    print(f"  Proposed: {prop_total}/{len(pool)} ({100*prop_total/len(pool):.1f}%), FN={prop_fn}")
    print(f"  Delta: TP {prop_ok-curr_ok:+d}, TN {prop_tn-curr_tn:+d}, Net {prop_total-curr_total:+d}")
    print()
