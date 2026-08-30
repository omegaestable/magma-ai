"""Case profile for the qz carrier (c) of law 12073: which rule fires at each chain product."""
import sys, os, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.setrecursionlimit(200000)
E = ('E',)
_op = {}
def rule(u, v):
    """return (rule name, result)"""
    if u == v: return ('R1', E)
    if v[0] == 'C':
        m = v[1]
        if u != E and m[0] == 'C' and m[1] == ('C', u): return ('R2', E)
        if m[0] == 'P' and op(m[1], m[2]) == m and op(u, m[2]) == m[1]: return ('R3', m[2])
        if u != E and op(E, u) == m: return ('R4', u)
        if m != E and op(u, m) == E: return ('R5', ('C', op(E, m)))
    if v == E: return ('R6', ('C', u))
    return ('R7', ('P', u, v))
def op(u, v):
    r = _op.get((u, v))
    if r is None:
        r = rule(u, v)[1]
        _op[(u, v)] = r
    return r

def terms(maxsz):
    by = {1: [E, ('g', 0)]}
    for n in range(2, maxsz + 1):
        cur = []
        for t in by[n-1]:
            cur.append(('C', t))
        for i in range(1, n):
            j = n - 1 - i
            if j >= 1:
                for a in by[i]:
                    for b in by[j]:
                        cur.append(('P', a, b))
        by[n] = cur
    out = []
    for n in range(1, maxsz+1): out.extend(by[n])
    return out

MS = int(sys.argv[1]) if len(sys.argv) > 1 else 7
T = terms(MS)
print("terms", len(T))
from collections import Counter
prof = Counter()
ex = {}
fails = 0
for y in T:
    for x in T:
        q = op(y, x)
        rw, w = rule(q, x)
        ro, o = rule(w, E)
        rt, t = rule(y, o)
        key = (rw, ro, rt)
        prof[key] += 1
        if key not in ex: ex[key] = (y, x, q, w, o, t)
        if t != x:
            fails += 1
            if fails < 4: print("FAIL", y, x, "->", t)
print("fails", fails)
for k, c in prof.most_common():
    y,x,q,w,o,t = ex[k]
    print(f"{k}  n={c:8d}  ex y={y} x={x}")
