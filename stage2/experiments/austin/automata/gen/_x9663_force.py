"""LEMMA_LIBRARY / law-40037 oracle: force W2 and W3 to fire at the op(z,y) product, where they
have never been observed, and check IMG and the law there."""
import sys, os, itertools, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _idc_lib import G, J, sz, show
import q9663c as M
inimg, _lvl2, op = M.inimg, M._lvl2, M.op
g0, g1 = G(0), G(1)
base = [g0, g1, J(g0, g0), J(g0, g1), J(g1, g0), J(g0, J(g0, g0)), J(J(g0, g0), g0)]

def which(u, v):
    if v[0] == 'J':
        A, Q = v[1], v[2]
        if inimg(A, u):
            if Q[0] == 'J' and op(Q[1], u) == Q[2]: return 'W1'
            if u[0] == 'J' and u[1][0] == 'J' and _lvl2(u, Q, u[1][2]): return 'W2'
            if u[0] == 'J' and u[2][0] == 'J' and u[2][2][0] == 'J' and _lvl2(u, Q, u[2][2][2]): return 'W3'
    return 'free'

# build z with the _lvl2 shape: z = J A1 (J w P1),  w = J A2 (J Q P2),  op w x = P1, op Q x = P2
# with x = a2 A1 (W2) or x = a2 P1 (W3); then m must satisfy a2 m = Q and inimg (a1 m) z.
made = collections.Counter(); imgbad = []; lawbad = []
n = 0
for x in base:
    for Q in base[:5]:
        for A2 in base[:4]:
            if not inimg(A2, x): continue
            P2 = op(Q, x)
            w = J(A2, J(Q, P2))
            if not _lvl2.__module__: pass
            P1 = op(w, x)
            for A1 in [J(g0, x), J(g1, x)]:              # so a2 A1 = x  -> W2 witness
                z = J(A1, J(w, P1))
                if not _lvl2(z, Q, x): continue
                # m must have a2 m = Q and inimg (a1 m) z
                for jm in base[:4]:
                    m = J(J(jm, z), Q)                    # a1 m = J jm z -> inimg by disjunct 1
                    n += 1
                    k = which(z, m)
                    made[k] += 1
                    A = op(z, m)
                    if not inimg(A, m): imgbad.append((z, m, k, A))
                    # and the law at (x', y:=m, z:=z) for a few x'
                    for xp in base[:4]:
                        P = op(xp, m); QQ = op(xp, P); AA = op(z, m); C = op(AA, QQ)
                        if op(m, C) != xp:
                            lawbad.append((xp, m, z, op(m, C)))
print('forced pairs n=%d  rule at op(z,m): %s' % (n, dict(made)))
print('IMG counterexamples:', len(imgbad), '   law failures:', len(lawbad))
for z, m, k, A in imgbad[:2]:
    print('  IMG FAIL rule=%s' % k); print('    z=%s' % show(z)[:110]); print('    m=%s' % show(m)[:110]); print('    op z m=%s' % show(A)[:110])
for xp, y, z, r in lawbad[:2]:
    print('  LAW FAIL x=%s' % show(xp)[:90]); print('    y=%s' % show(y)[:110]); print('    z=%s' % show(z)[:110]); print('    -> %s' % show(r)[:110])
