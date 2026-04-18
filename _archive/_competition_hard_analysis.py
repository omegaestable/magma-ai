"""Analyze separability of competition hard.jsonl pool using our test suite."""
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

def check_structural(eq_str):
    lhs, rhs = eq_str.split('=', 1)
    lhs, rhs = lhs.strip(), rhs.strip()
    results = {}
    results['LP'] = 'HOLD' if first_letter(lhs) == first_letter(rhs) else 'FAIL'
    results['RP'] = 'HOLD' if last_letter(lhs) == last_letter(rhs) else 'FAIL'
    l_star, r_star = '*' in lhs, '*' in rhs
    if l_star and r_star: results['C0'] = 'HOLD'
    elif not l_star and not r_star: results['C0'] = 'HOLD' if lhs.strip() == rhs.strip() else 'FAIL'
    else: results['C0'] = 'FAIL'
    l_vars = set(c for c in lhs if c.isalpha())
    r_vars = set(c for c in rhs if c.isalpha())
    if l_star and r_star: results['VARS'] = 'HOLD' if l_vars == r_vars else 'FAIL'
    elif not l_star and not r_star: results['VARS'] = 'HOLD' if lhs.strip() == rhs.strip() else 'FAIL'
    else:
        bare = lhs.strip() if not l_star else rhs.strip()
        star_vars = r_vars if not l_star else l_vars
        results['VARS'] = 'HOLD' if star_vars == {bare} else 'FAIL'
    from collections import Counter
    l_c = Counter(c for c in lhs if c.isalpha())
    r_c = Counter(c for c in rhs if c.isalpha())
    all_l = set(l_c) | set(r_c)
    results['COUNT2'] = 'HOLD' if all(l_c.get(v,0)%2==r_c.get(v,0)%2 for v in all_l) else 'FAIL'
    if results['LP'] == 'FAIL': results['LDEPTH'] = 'FAIL'
    else:
        def ldepth(s):
            t = parse_tree(s)
            d = 0
            while isinstance(t, tuple): d += 1; t = t[1]
            return d
        results['LDEPTH'] = 'HOLD' if ldepth(lhs)%2 == ldepth(rhs)%2 else 'FAIL'
    return results

def find_separators(e1_str, e2_str):
    e1_t = check_structural(e1_str)
    e2_t = check_structural(e2_str)
    seps = []
    for test in ['LP','RP','C0','VARS','COUNT2','LDEPTH']:
        if e1_t[test]=='HOLD' and e2_t[test]=='FAIL':
            seps.append(test)
    
    e1_lhs_s, e1_rhs_s = e1_str.split('=',1)
    e2_lhs_s, e2_rhs_s = e2_str.split('=',1)
    e1_lhs = parse_tree(e1_lhs_s.strip())
    e1_rhs = parse_tree(e1_rhs_s.strip())
    e2_lhs = parse_tree(e2_lhs_s.strip())
    e2_rhs = parse_tree(e2_rhs_s.strip())
    
    all_vars = sorted(get_vars(e1_lhs)|get_vars(e1_rhs)|get_vars(e2_lhs)|get_vars(e2_rhs))
    n_vars = len(all_vars)
    
    seen = []
    for c in e1_str + e2_str:
        if c.isalpha() and c not in seen: seen.append(c)
    assign = {v: i%3 for i,v in enumerate(seen)}
    assign_z = {v: 0 for v in seen}
    
    for name, table in MAGMAS.items():
        if name in ('T5B','NL1') and n_vars >= 4:
            continue
        try:
            e1_l = eval_tree(e1_lhs, assign, table)
            e1_r = eval_tree(e1_rhs, assign, table)
            if e1_l != e1_r: continue
            e1_lz = eval_tree(e1_lhs, assign_z, table)
            e1_rz = eval_tree(e1_rhs, assign_z, table)
            if e1_lz != e1_rz: continue
            e2_l = eval_tree(e2_lhs, assign, table)
            e2_r = eval_tree(e2_rhs, assign, table)
            if e2_l != e2_r: seps.append(name)
        except: pass
    
    return seps

# Read the full hard.jsonl pool
with open('data/hf_cache/hard.jsonl') as f:
    problems = [json.loads(l) for l in f]

true_problems = [p for p in problems if p['answer']]
false_problems = [p for p in problems if not p['answer']]

print(f"Competition hard.jsonl: {len(problems)} total ({len(true_problems)}T / {len(false_problems)}F)")
print()

# Analyze FALSE problems: how many can we separate?
sep_count = 0
sep_by_test = {}
unsep_count = 0

for p in false_problems:
    seps = find_separators(p['equation1'], p['equation2'])
    if seps:
        sep_count += 1
        for s in seps:
            sep_by_test[s] = sep_by_test.get(s, 0) + 1
    else:
        unsep_count += 1

print(f"FALSE problems ({len(false_problems)} total):")
print(f"  Separable: {sep_count} ({100*sep_count/len(false_problems):.1f}%)")
print(f"  Unseparable: {unsep_count} ({100*unsep_count/len(false_problems):.1f}%)")
print(f"  Separators: {dict(sorted(sep_by_test.items(), key=lambda x:-x[1]))}")

# Analyze TRUE problems: check for false positives (tests that wrongly separate)
fp_count = 0
fp_by_test = {}
for p in true_problems:
    seps = find_separators(p['equation1'], p['equation2'])
    if seps:
        fp_count += 1
        for s in seps:
            fp_by_test[s] = fp_by_test.get(s, 0) + 1

print(f"\nTRUE problems ({len(true_problems)} total):")
print(f"  Would be wrongly separated (UNSOUND): {fp_count} ({100*fp_count/len(true_problems):.1f}%)")
if fp_by_test:
    print(f"  False separators: {dict(sorted(fp_by_test.items(), key=lambda x:-x[1]))}")

# Best possible score
best_tp = len(true_problems) - fp_count
best_tn = sep_count
total_best = best_tp + best_tn
print(f"\nBest possible score (zero execution errors):")
print(f"  TP: {best_tp}/{len(true_problems)}")
print(f"  TN: {best_tn}/{len(false_problems)}")
print(f"  Total: {total_best}/{len(problems)} = {100*total_best/len(problems):.1f}%")

# Now check what the 30-problem rotation looks like
print(f"\n{'='*60}")
print("Rotation 23 sample (30 problems: 15T/15F):")
with open('data/benchmark/hard_balanced30_true15_false15_rotation0023_20260417_155001.jsonl') as f:
    rot_problems = [json.loads(l) for l in f]

rot_true = [p for p in rot_problems if p['answer']]
rot_false = [p for p in rot_problems if not p['answer']]

rot_sep = 0
rot_sep_tests = {}
for p in rot_false:
    seps = find_separators(p['equation1'], p['equation2'])
    if seps:
        rot_sep += 1
        for s in seps:
            rot_sep_tests[s] = rot_sep_tests.get(s, 0) + 1

rot_fp = 0
for p in rot_true:
    seps = find_separators(p['equation1'], p['equation2'])
    if seps: rot_fp += 1

print(f"  FALSE separable: {rot_sep}/{len(rot_false)} ({100*rot_sep/len(rot_false):.1f}%)")
print(f"  TRUE wrongly separated: {rot_fp}/{len(rot_true)}")
print(f"  Separators: {rot_sep_tests}")
print(f"  Best possible: {len(rot_true)-rot_fp+rot_sep}/{len(rot_problems)} = {100*(len(rot_true)-rot_fp+rot_sep)/len(rot_problems):.1f}%")
