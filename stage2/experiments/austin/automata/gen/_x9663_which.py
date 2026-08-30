"""Which rule fires, and does IMG (inimg (op z u) u) hold in each case?"""
import sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _idc_lib import G, J, sz, show, terms
import q9663c as M
inimg, _lvl2 = M.inimg, M._lvl2

def which(u, v):
    """returns 'free' | 'W1' | 'W2' | 'W3'"""
    if v[0] == 'J':
        A, Q = v[1], v[2]
        if inimg(A, u):
            if Q[0] == 'J' and M.op(Q[1], u) == Q[2]: return 'W1'
            if u[0] == 'J' and u[1][0] == 'J':
                x = u[1][2]
                if _lvl2(u, Q, x): return 'W2'
            if u[0] == 'J' and u[2][0] == 'J' and u[2][2][0] == 'J':
                x = u[2][2][2]
                if _lvl2(u, Q, x): return 'W3'
    return 'free'

def enc(u, w, j):
    P = M.op(w, u); A = J(j, u)
    return J(A, J(w, P))

cnt = {}; badimg = []
pools = [terms(13, 1), terms(7, 2)]
# plus a constructed pool with deep encodings, so W2/W3 actually fire
rng = random.Random(7)
base = [G(0), G(1), J(G(0), G(0)), J(G(0), J(G(0), G(0))), J(J(G(0), G(0)), G(0))]
deep = list(base)
for a in base:
    for w in base:
        e = enc(a, w, G(0)); deep.append(e)
        deep.append(enc(a, e, G(0))); deep.append(enc(e, w, G(0)))
        deep.append(enc(a, enc(a, w, G(0)), G(0)))
pools.append(list(dict.fromkeys(deep)))
for pi, pool in enumerate(pools):
    c = {}
    bad = 0
    for z in pool:
        for u in pool:
            k = which(z, u)
            c[k] = c.get(k, 0) + 1
            if not inimg(M.op(z, u), u):
                bad += 1
                if len(badimg) < 3: badimg.append((z, u, k))
    print('pool %d (%d terms, %d pairs): %s   IMG counterexamples=%d' % (pi, len(pool), len(pool)**2, c, bad), flush=True)
for z, u, k in badimg:
    print('  IMG FAIL rule=%s z=%s u=%s' % (k, show(z)[:70], show(u)[:70]))
