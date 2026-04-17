"""
Simulate v26c's full pipeline (structural + gated rescues) and test
adding T5B with ≤3-var gate. Shows exact FN/catch delta.
"""
import json

T3R = [[1,2,0],[1,2,0],[1,2,0]]
T3L = [[1,1,1],[2,2,2],[0,0,0]]
T4A = [[0,1,2],[2,0,1],[1,2,0]]
T5B = [[0,2,1],[1,0,2],[2,1,0]]

def parse_expr(s):
    s = s.strip()
    while s[0] == '(' and _m(s,0) == len(s)-1: s = s[1:-1].strip()
    d = 0
    for i,c in enumerate(s):
        if c == '(': d+=1
        elif c == ')': d-=1
        elif c == '*' and d==0:
            return ('*', parse_expr(s[:i]), parse_expr(s[i+1:]))
    return s.strip()

def _m(s,p):
    d=1
    for i in range(p+1,len(s)):
        if s[i]=='(': d+=1
        elif s[i]==')':
            d-=1
            if d==0: return i
    return -1

def first_letter(s):
    for c in s:
        if c.isalpha(): return c
    return None

def last_letter(s):
    for c in reversed(s):
        if c.isalpha(): return c
    return None

def has_star(s):
    return '*' in s

def get_vars_set(s):
    return set(c for c in s if c.isalpha())

def count_vars(s):
    d = {}
    for c in s:
        if c.isalpha():
            d[c] = d.get(c, 0) + 1
    return d

def ldepth(s):
    """Count * nodes from root to leftmost letter, going left."""
    s = s.strip()
    depth = 0
    while True:
        s = s.strip()
        if not s or s[0].isalpha():
            return depth
        if s[0] == '(':
            # find the main * at top level
            d = 0; found = -1
            for i,c in enumerate(s):
                if c == '(': d += 1
                elif c == ')': d -= 1
                elif c == '*' and d == 1:
                    found = i; break
            if found == -1:
                # no * found, peel parens
                if s[0] == '(' and _m(s,0) == len(s)-1:
                    s = s[1:-1]
                    continue
                return depth
            # go left
            depth += 1
            s = s[1:found]
        else:
            return depth

def get_vars_ordered(e1, e2):
    seen = []
    for c in e1 + ' ' + e2:
        if c.isalpha() and c not in seen:
            seen.append(c)
    return seen

def default_assign(vo):
    return {v: i%3 for i,v in enumerate(vo)}

def ev(t, a, table):
    if isinstance(t, str): return a[t]
    return table[ev(t[1],a,table)][ev(t[2],a,table)]

def magma_check(e1, e2, table, var_order):
    """Returns 'SEP', 'E1F', or 'HOLD'."""
    e1l,e1r = e1.split('=',1)
    e2l,e2r = e2.split('=',1)
    a = default_assign(var_order)
    if ev(parse_expr(e1l),a,table) != ev(parse_expr(e1r),a,table):
        return 'E1F'
    if ev(parse_expr(e2l),a,table) != ev(parse_expr(e2r),a,table):
        return 'SEP'
    return 'HOLD'

def structural_test(name, e1l, e1r, e2l, e2r):
    """Returns (e1_result, e2_result) as 'HOLD'/'FAIL'."""
    if name == 'LP':
        r1 = 'HOLD' if first_letter(e1l) == first_letter(e1r) else 'FAIL'
        r2 = 'HOLD' if first_letter(e2l) == first_letter(e2r) else 'FAIL'
    elif name == 'RP':
        r1 = 'HOLD' if last_letter(e1l) == last_letter(e1r) else 'FAIL'
        r2 = 'HOLD' if last_letter(e2l) == last_letter(e2r) else 'FAIL'
    elif name == 'C0':
        s1l, s1r = has_star(e1l), has_star(e1r)
        s2l, s2r = has_star(e2l), has_star(e2r)
        if s1l and s1r: r1 = 'HOLD'
        elif not s1l and not s1r and get_vars_set(e1l) == get_vars_set(e1r): r1 = 'HOLD'
        else: r1 = 'FAIL'
        if s2l and s2r: r2 = 'HOLD'
        elif not s2l and not s2r and get_vars_set(e2l) == get_vars_set(e2r): r2 = 'HOLD'
        else: r2 = 'FAIL'
    elif name == 'VARS':
        vs1l, vs1r = get_vars_set(e1l), get_vars_set(e1r)
        s1l, s1r = has_star(e1l), has_star(e1r)
        if s1l and s1r: r1 = 'HOLD' if vs1l == vs1r else 'FAIL'
        elif not s1l and not s1r: r1 = 'HOLD' if vs1l == vs1r else 'FAIL'
        else:
            bare = vs1l if not s1l else vs1r
            star = vs1r if not s1l else vs1l
            r1 = 'HOLD' if star == bare else 'FAIL'
        vs2l, vs2r = get_vars_set(e2l), get_vars_set(e2r)
        s2l, s2r = has_star(e2l), has_star(e2r)
        if s2l and s2r: r2 = 'HOLD' if vs2l == vs2r else 'FAIL'
        elif not s2l and not s2r: r2 = 'HOLD' if vs2l == vs2r else 'FAIL'
        else:
            bare = vs2l if not s2l else vs2r
            star = vs2r if not s2l else vs2l
            r2 = 'HOLD' if star == bare else 'FAIL'
    elif name == 'COUNT2':
        c1l, c1r = count_vars(e1l), count_vars(e1r)
        allv = set(list(c1l.keys()) + list(c1r.keys()))
        r1 = 'HOLD'
        for v in allv:
            if c1l.get(v,0) % 2 != c1r.get(v,0) % 2:
                r1 = 'FAIL'; break
        c2l, c2r = count_vars(e2l), count_vars(e2r)
        allv = set(list(c2l.keys()) + list(c2r.keys()))
        r2 = 'HOLD'
        for v in allv:
            if c2l.get(v,0) % 2 != c2r.get(v,0) % 2:
                r2 = 'FAIL'; break
    elif name == 'LDEPTH':
        # LDEPTH: HOLD iff LP=HOLD AND ldepth(L) ≡ ldepth(R) mod 2
        lp1 = 'HOLD' if first_letter(e1l) == first_letter(e1r) else 'FAIL'
        lp2 = 'HOLD' if first_letter(e2l) == first_letter(e2r) else 'FAIL'
        if lp1 == 'FAIL': r1 = 'FAIL'
        else: r1 = 'HOLD' if ldepth(e1l) % 2 == ldepth(e1r) % 2 else 'FAIL'
        if lp2 == 'FAIL': r2 = 'FAIL'
        else: r2 = 'HOLD' if ldepth(e2l) % 2 == ldepth(e2r) % 2 else 'FAIL'
    return r1, r2

def simulate_v26c(e1_str, e2_str):
    """Simulate v26c pipeline. Returns ('TRUE'/'FALSE', reason)."""
    if e1_str.replace(' ','') == e2_str.replace(' ',''):
        return 'TRUE', 'identical'
    
    e1l, e1r = e1_str.split('=', 1)
    e2l, e2r = e2_str.split('=', 1)
    e1l, e1r, e2l, e2r = e1l.strip(), e1r.strip(), e2l.strip(), e2r.strip()
    
    lp_e1 = rp_e1 = None
    
    for test_name in ['LP', 'RP', 'C0', 'VARS', 'COUNT2', 'LDEPTH']:
        r1, r2 = structural_test(test_name, e1l, e1r, e2l, e2r)
        if test_name == 'LP': lp_e1 = r1
        if test_name == 'RP': rp_e1 = r1
        if r1 == 'HOLD' and r2 == 'FAIL':
            return 'FALSE', test_name
    
    # Spine check (simplified - skip for now, rarely triggers)
    
    var_order = get_vars_ordered(e1_str, e2_str)
    
    # T3R: gate on RP E1=HOLD
    if rp_e1 == 'HOLD':
        r = magma_check(e1_str, e2_str, T3R, var_order)
        if r == 'SEP': return 'FALSE', 'T3R'
    
    # T3L: gate on LP E1=HOLD
    if lp_e1 == 'HOLD':
        r = magma_check(e1_str, e2_str, T3L, var_order)
        if r == 'SEP': return 'FALSE', 'T3L'
    
    return 'TRUE', 'default'

def simulate_v26h(e1_str, e2_str, use_t4a=False, max_vars=3):
    """v26c + T5B (and optionally T4A) with var gate."""
    pred, reason = simulate_v26c(e1_str, e2_str)
    if pred == 'FALSE':
        return pred, reason
    
    var_order = get_vars_ordered(e1_str, e2_str)
    nv = len(var_order)
    
    if nv <= max_vars:
        if use_t4a:
            r = magma_check(e1_str, e2_str, T4A, var_order)
            if r == 'SEP': return 'FALSE', 'T4A'
        
        r = magma_check(e1_str, e2_str, T5B, var_order)
        if r == 'SEP': return 'FALSE', 'T5B'
    
    return 'TRUE', 'default'

benchmarks = [
    ('hard3', 'data/benchmark/hard3_balanced50_true10_false40_rotation0020_20260417_002534.jsonl'),
    ('normal', 'data/benchmark/normal_balanced60_true30_false30_rotation0020_20260417_002534.jsonl'),
]

for bname, bpath in benchmarks:
    print(f"\n{'='*70}")
    print(f"  {bname}")
    print(f"{'='*70}")
    
    problems = []
    with open(bpath) as f:
        for line in f:
            problems.append(json.loads(line))
    
    configs = [
        ("v26c (baseline)", lambda e1,e2: simulate_v26c(e1,e2)),
        ("v26c + T5B(≤3v)", lambda e1,e2: simulate_v26h(e1,e2,use_t4a=False,max_vars=3)),
        ("v26c + T4A+T5B(≤3v)", lambda e1,e2: simulate_v26h(e1,e2,use_t4a=True,max_vars=3)),
        ("v26c + T5B(≤2v)", lambda e1,e2: simulate_v26h(e1,e2,use_t4a=False,max_vars=2)),
    ]
    
    for label, sim_fn in configs:
        true_ok = true_fn = false_ok = false_fp = 0
        fn_details = []
        catch_details = []
        
        for p in problems:
            pred, reason = sim_fn(p['equation1'], p['equation2'])
            gt = p['answer']
            
            if gt:
                if pred == 'TRUE': true_ok += 1
                else: true_fn += 1; fn_details.append((p['id'], reason, len(get_vars_ordered(p['equation1'],p['equation2']))))
            else:
                if pred == 'FALSE': false_ok += 1; catch_details.append((p['id'], reason))
                else: false_fp += 1
        
        total = len(problems)
        acc = (true_ok + false_ok) / total * 100
        true_total = true_ok + true_fn
        false_total = false_ok + false_fp
        
        print(f"\n  {label}:")
        print(f"    TRUE: {true_ok}/{true_total} ({true_ok/true_total*100:.0f}%)  FALSE: {false_ok}/{false_total} ({false_ok/false_total*100:.1f}%)  Acc: {acc:.1f}%")
        
        if fn_details:
            print(f"    FN: {fn_details}")
        
        # At 50/50 mix
        true_rate = true_ok / true_total
        false_rate = false_ok / false_total
        balanced = (true_rate + false_rate) / 2 * 100
        print(f"    Balanced (50/50): {balanced:.1f}%")
