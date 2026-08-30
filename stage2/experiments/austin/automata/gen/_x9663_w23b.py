"""Do W2/W3 ever fire?  Build the level-3 pool (inimg via disjunct 2) and census."""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _idc_lib import G, J, sz, show
import q9663c as M
inimg, _lvl2, op = M.inimg, M._lvl2, M.op

def which(u, v):
    if v[0] == 'J':
        A, Q = v[1], v[2]
        if inimg(A, u):
            if Q[0] == 'J' and op(Q[1], u) == Q[2]: return 'W1'
            if u[0] == 'J' and u[1][0] == 'J' and _lvl2(u, Q, u[1][2]): return 'W2'
            if u[0] == 'J' and u[2][0] == 'J' and u[2][2][0] == 'J' and _lvl2(u, Q, u[2][2][2]): return 'W3'
    return 'free'

g0, g1 = G(0), G(1)
base = [g0, g1, J(g0, g0), J(g0, g1), J(g1, g0), J(g0, J(g0, g0)), J(J(g0, g0), g0)]
pool = set(base)
# level-3 shapes: x = J s (J A1 t) so inimg A1 x holds by disjunct 2
for A1 in base:
    for s in base[:4]:
        for t in base[:4]:
            x = J(s, J(A1, t)); pool.add(x)
            for w in base[:5]:
                y = J(A1, J(w, op(w, x))); pool.add(y)
                for w2 in base[:3]:
                    for A2 in base[:3]:
                        if not inimg(A2, x): continue
                        wc = J(A2, J(w2, op(w2, x))); pool.add(wc)
                        pool.add(J(A1, J(wc, op(wc, x))))
pool = list(pool)
st = collections.Counter(); ex = {}; imgbad = []
for u in pool:
    for v in pool:
        k = which(u, v); st[k] += 1
        if k in ('W2', 'W3'):
            if k not in ex: ex[k] = (u, v)
            st[(k, 'tgQ2' if v[2][0] == 'J' else 'tgQnot2')] += 1
        if not inimg(op(u, v), v): imgbad.append((u, v, k))
print('pool=%d pairs=%d  %s' % (len(pool), len(pool)**2, dict(st)))
print('IMG counterexamples:', len(imgbad))
for k, (u, v) in ex.items():
    print('%s fires: u=%s' % (k, show(u)[:80])); print('          v=%s' % show(v)[:80])
    print('          tg(a2 v)=%d   a2 v = %s' % (2 if v[2][0] == 'J' else 0, show(v[2])[:60]))
for u, v, k in imgbad[:2]:
    print('IMG FAIL rule=%s u=%s v=%s' % (k, show(u)[:70], show(v)[:70]))
