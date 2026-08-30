"""When W2/W3 fire, what is true of v?  (Deciding whether IMG is locally provable.)"""
import sys, os, random, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _idc_lib import G, J, sz, show
import q9663c as M
import _x9663_which as W

def enc(u, w, j):
    return J(J(j, u), J(w, M.op(w, u)))

rng = random.Random(11)
g0, g1 = G(0), G(1)
base = [g0, g1, J(g0, g0), J(g0, g1), J(g1, g0), J(g0, J(g0, g0)), J(J(g0, g0), g0)]
pool = list(base)
for a in base:
    for w in base:
        for j in base[:3]:
            e = enc(a, w, j); pool.append(e)
            pool.append(enc(a, e, j)); pool.append(enc(e, w, j))
            pool.append(enc(a, enc(a, w, j), j))
pool = list(dict.fromkeys(pool))
stats = collections.Counter(); ex = {}
for u in pool:
    for v in pool:
        k = W.which(u, v)
        stats[k] += 1
        if k in ('W2', 'W3') and k not in ex:
            ex[k] = (u, v)
        if k in ('W2', 'W3'):
            stats[(k, 'tgQ=2' if v[2][0] == 'J' else 'tgQ!=2')] += 1
            stats[(k, 'IMGok' if M.inimg(M.op(u, v), v) else 'IMGBAD')] += 1
print('pool', len(pool), dict(stats))
for k, (u, v) in ex.items():
    print('%s example: u=%s' % (k, show(u)[:90])); print('            v=%s' % show(v)[:90])
