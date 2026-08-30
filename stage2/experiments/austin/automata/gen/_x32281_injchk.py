"""Is op injective in its FIRST argument?  op u v = op u' v  =>  u = u'."""
import sys, collections
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen')
from _x32281_lib import *
from _x32281_try1 import R1
from _x32281_try2 import R3
from _x32281_try5 import R5
import closedform as cf, fuzz as fz
RULES = [R1, R3, R5]
C = cf.Closed(LAW, RULES); op = C.op
J = lambda a, b: ('J', a, b); g = lambda n: ('g', n)
def enc(xv, zv, yv): return J(J(zv, J(J(xv, yv), yv)), yv)
for sd in (3, 4, 202, 555, 909):
    cf.deep_tests(C, LAW, 6000, 300, sd)
    fz.critical_fuzz(C, LAW, 9000, seed=sd + 300)
    fz.closure_fuzz(C, LAW, 9000, seed=sd + 200)
G = [g(0), g(1), g(2)]
E1 = [enc(a, b, c) for a in G for b in G for c in G]
E2 = ([enc(a, b, c) for a in E1[:9] for b in G for c in G] +
      [enc(a, b, c) for a in G for b in E1[:9] for c in G] +
      [enc(a, b, c) for a in G for b in G for c in E1[:9]])
for x in G + E1:
    for y in G + E1 + E2:
        for z in G + E1[:6]:
            try:
                p = op(x, y); q = op(p, y); a = op(z, q); s = op(a, y); op(z, s)
            except RecursionError: pass
# group memo by v -> {result: [u,...]}
byv = collections.defaultdict(lambda: collections.defaultdict(list))
for (u, v), r in C.memo.items():
    byv[v][r].append(u)
bad = 0; tot = 0
for v, d in byv.items():
    for r, us in d.items():
        tot += 1
        if len(set(us)) > 1:
            bad += 1
            if bad <= 3: print('INJ FAILS: v sz', len(str(v)), 'result', str(r)[:60], 'us', [str(t)[:40] for t in set(us)][:3])
print('memo pairs:', len(C.memo), ' distinct (v,result) groups:', tot, ' groups with >1 u:', bad)
