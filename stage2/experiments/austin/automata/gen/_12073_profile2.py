import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.setrecursionlimit(200000)
E = ('E',)
_op = {}
def rule(u, v):
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
        r = rule(u, v)[1]; _op[(u, v)] = r
    return r
def terms(maxsz, ngen):
    by = {1: [E] + [('g', i) for i in range(ngen)]}
    for n in range(2, maxsz + 1):
        cur = [('C', t) for t in by[n-1]]
        for i in range(1, n):
            j = n - 1 - i
            if j >= 1:
                for a in by[i]:
                    for b in by[j]: cur.append(('P', a, b))
        by[n] = cur
    out = []
    for n in range(1, maxsz+1): out.extend(by[n])
    return out
from collections import Counter
def run(tag, YS, XS):
    prof = Counter(); ex = {}; fails = 0
    for y in YS:
        for x in XS:
            q = op(y, x); rw, w = rule(q, x); ro, o = rule(w, E); rt, t = rule(y, o)
            k = (rw, ro, rt); prof[k] += 1
            if k not in ex: ex[k] = (y, x)
            if t != x:
                fails += 1
                if fails < 3: print("FAIL", y, x, "->", t)
    print(f"== {tag}  pairs={len(YS)*len(XS)} fails={fails}")
    for k, c in prof.most_common():
        print(f"   {k}  n={c:9d}  ex y={ex[k][0]} x={ex[k][1]}")
T2 = terms(5, 2); run("<=5 / 2 gens", T2, T2)
T1 = terms(9, 1)
Csm = [t for t in T1 if t[0] == 'C']
Ysm = [t for t in T1 if len(repr(t)) < 60]
print("Csm", len(Csm), "Ysm", len(Ysm))
run("x C-term<=9, y<=9-small", Ysm, Csm)
