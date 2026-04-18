"""Investigate hard2 FNs: TRUE problems predicted as FALSE"""
import re

def assign_vars(e1, e2):
    full = e1 + ' ' + e2
    seen = []
    for c in full:
        if c.isalpha() and c not in seen:
            seen.append(c)
    return {v: i % 3 for i, v in enumerate(seen)}

def rewrite(expr, mapping):
    return ''.join(str(mapping[c]) if c.isalpha() else c for c in expr)

def eval_m(expr, fn):
    s = expr.replace(' ', '')
    while '*' in s:
        m = re.search(r'\((\d)\*(\d)\)', s)
        if not m:
            m = re.search(r'(\d)\*(\d)', s)
        if not m:
            break
        a, b = int(m.group(1)), int(m.group(2))
        s = s[:m.start()] + str(fn(a, b)) + s[m.end():]
    s = s.replace('(', '').replace(')', '')
    return int(s) if s.isdigit() else -1

t3r = lambda a, b: (b + 1) % 3
t3l = lambda a, b: (a + 1) % 3
t5b = lambda a, b: (a + 2*b) % 3
nl1_t = {(0,0):0,(0,1):0,(0,2):0,(1,0):1,(1,1):1,(1,2):0,(2,0):1,(2,1):2,(2,2):2}
nl1 = lambda a, b: nl1_t[(a,b)]

pairs = [
    ('hard2_0198', 'x * y = z * (y * (x * x))', 'x * y = (z * w) * (z * x)'),
    ('hard2_0023', 'x = x * (y * (x * z))', 'x = (x * ((y * z) * w)) * x'),
]

for pid, e1, e2 in pairs:
    print(f'=== {pid}: E1: {e1}    E2: {e2} ===')
    lhs1, rhs1 = e1.split(' = ', 1)
    lhs2, rhs2 = e2.split(' = ', 1)
    m = assign_vars(e1, e2)
    nvars = len(m)
    zm = {v: 0 for v in m}
    print(f'  Vars: {m} (nvars={nvars})')
    
    for name, fn in [('T3R', t3r), ('T3L', t3l), ('T5B', t5b), ('NL1', nl1)]:
        skip = name in ('T5B','NL1') and nvars >= 4
        l1 = eval_m(rewrite(lhs1, m), fn)
        r1 = eval_m(rewrite(rhs1, m), fn)
        l1z = eval_m(rewrite(lhs1, zm), fn)
        r1z = eval_m(rewrite(rhs1, zm), fn)
        l2 = eval_m(rewrite(lhs2, m), fn)
        r2 = eval_m(rewrite(rhs2, m), fn)
        
        e1d = 'match' if l1 == r1 else 'MISS'
        e1z = 'match' if l1z == r1z else 'MISS'
        e2d = 'match' if l2 == r2 else 'MISS'
        
        spur = ''
        if l1 == r1 and l1z == r1z and l2 != r2:
            spur = ' >>> SPURIOUS SEPARATION <<<'
        
        sk = ' [SKIP:4+vars]' if skip else ''
        print(f'  {name}: E1_def {l1}v{r1} {e1d}, E1_zero {l1z}v{r1z} {e1z}, E2_def {l2}v{r2} {e2d}{spur}{sk}')
    
    # Structural: LP, RP, C0
    def first_let(s):
        for c in s:
            if c.isalpha(): return c
        return None
    def last_let(s):
        for c in reversed(s):
            if c.isalpha(): return c
        return None
    
    e1_lp = first_let(lhs1) == first_let(rhs1)
    e2_lp = first_let(lhs2) == first_let(rhs2)
    e1_rp = last_let(lhs1) == last_let(rhs1)
    e2_rp = last_let(lhs2) == last_let(rhs2)
    e1_c0 = ('*' in lhs1) == ('*' in rhs1)
    e2_c0 = ('*' in lhs2) == ('*' in rhs2)
    
    def hf(b): return 'HOLD' if b else 'FAIL'
    
    print(f'  LP: E1={hf(e1_lp)} E2={hf(e2_lp)}' + (' >>> STRUCT SEP' if e1_lp and not e2_lp else ''))
    print(f'  RP: E1={hf(e1_rp)} E2={hf(e2_rp)}' + (' >>> STRUCT SEP' if e1_rp and not e2_rp else ''))
    print(f'  C0: E1={hf(e1_c0)} E2={hf(e2_c0)}' + (' >>> STRUCT SEP' if e1_c0 and not e2_c0 else ''))
    print()
