"""KEY/SZU/SZR over EVERY pair the adversarial workloads actually evaluated (the memo table)."""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _x32281_lib import *
from _x32281_try1 import R1
from _x32281_try2 import R3
import closedform as cf, fuzz as fz, smallcheck as sc
from freemodel import size

RULES = [R1, R3]

def sh(t): return 'g%d' % t[1] if t[0] == 'g' else '(' + sh(t[1]) + '*' + sh(t[2]) + ')'

def scan(C, tag):
    st = collections.Counter(); bad = []
    for (u, v), w in C.memo.items():
        if w[0] == 'J' and w[1] == u and w[2] == v:
            st['free'] += 1; continue
        st['fired'] += 1
        if not size(w) < size(v):
            st['!SZR'] += 1; bad.append(('SZR', u, v, w))
        if not size(u) < size(v):
            st['!SZU'] += 1; bad.append(('SZU', u, v, w))
        b = v[1][1] if (v[0] == 'J' and v[1][0] == 'J') else None
        if b != u:
            st['!KEY'] += 1; bad.append(('KEY', u, v, w))
        # R1 structural?
        r1 = (v[0] == 'J' and v[1][0] == 'J' and v[1][1] == u and v[1][2][0] == 'J'
              and v[1][2][1][0] == 'J' and v[1][2][1][2] == v[1][2][2] and v[1][2][1][2] == v[2])
        st['R1' if r1 else 'R3'] += 1
    print(tag, dict(st), flush=True)
    return bad

allbad = []
for sd in (3, 4, 5, 101, 202):
    C = cf.Closed(LAW, RULES)
    cf.deep_tests(C, LAW, 8000, 240, sd)
    fz.fuzz(C, LAW, RULES, 12000, seed=sd + 100)
    fz.closure_fuzz(C, LAW, 12000, seed=sd + 200)
    fz.critical_fuzz(C, LAW, 12000, seed=sd + 300)
    allbad += scan(C, 'seed%d' % sd)

C = cf.Closed(LAW, RULES)
sc.exhaustive(C, LAW, 10, 1, limit=25)
sc.exhaustive(C, LAW, 6, 2, limit=25)
allbad += scan(C, 'exh')

print('violations', len(allbad))
for e in allbad[:5]:
    print(e[0], 'u=', sh(e[1])[:100], '  v=', sh(e[2])[:160], '  w=', sh(e[3])[:100])
