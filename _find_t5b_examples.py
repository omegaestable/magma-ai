"""Find T5B-only catches for worked example."""
import json

T3R = [[1,2,0],[1,2,0],[1,2,0]]
T3L = [[1,1,1],[2,2,2],[0,0,0]]
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

def last_letter(s):
    for c in reversed(s):
        if c.isalpha(): return c

def get_vars_ordered(e1, e2):
    seen = []
    for c in e1 + ' ' + e2:
        if c.isalpha() and c not in seen: seen.append(c)
    return seen

def default_assign(vo): return {v:i%3 for i,v in enumerate(vo)}

def ev(t, a, tb):
    if isinstance(t, str): return a[t]
    return tb[ev(t[1],a,tb)][ev(t[2],a,tb)]

def mc(e1, e2, table, vo):
    e1l,e1r = e1.split('=',1)
    e2l,e2r = e2.split('=',1)
    a = default_assign(vo)
    v1l = ev(parse_expr(e1l), a, table)
    v1r = ev(parse_expr(e1r), a, table)
    if v1l != v1r: return 'E1F', v1l, v1r, None, None
    v2l = ev(parse_expr(e2l), a, table)
    v2r = ev(parse_expr(e2r), a, table)
    return ('SEP' if v2l!=v2r else 'HOLD'), v1l, v1r, v2l, v2r

with open('data/benchmark/hard3_balanced50_true10_false40_rotation0020_20260417_002534.jsonl') as f:
    for line in f:
        p = json.loads(line)
        if p['answer']: continue  # skip TRUE
        e1, e2 = p['equation1'], p['equation2']
        el, er = e1.split('=', 1)
        e2l_str, e2r_str = e2.split('=', 1)
        vo = get_vars_ordered(e1, e2)
        nv = len(vo)
        if nv > 3: continue

        lp1 = 'HOLD' if first_letter(el) == first_letter(er) else 'FAIL'
        rp1 = 'HOLD' if last_letter(el) == last_letter(er) else 'FAIL'

        # Skip if T3R or T3L separate
        if rp1 == 'HOLD':
            r = mc(e1, e2, T3R, vo)
            if r[0] == 'SEP': continue
        if lp1 == 'HOLD':
            r = mc(e1, e2, T3L, vo)
            if r[0] == 'SEP': continue

        # Check T5B
        r = mc(e1, e2, T5B, vo)
        if r[0] == 'SEP':
            a = default_assign(vo)
            asgn = {v: a[v] for v in vo}
            print(f"  {p['id']} ({nv}v): LP_E1={lp1} RP_E1={rp1}")
            print(f"    E1: {e1}")
            print(f"    E2: {e2}")
            print(f"    assign: {asgn}")
            print(f"    T5B: E1={r[1]}={r[2]}, E2={r[3]}!={r[4]}")
            print()
