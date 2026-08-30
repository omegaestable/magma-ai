"""Force W3 to fire at the op(z,m) product (the law-40037 oracle) for q9663d."""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _idc_lib import G, J, sz, show
M = __import__(sys.argv[1] if len(sys.argv) > 1 else 'q9663d')
inimg, _lvl2, op = M.inimg, M._lvl2, M.op
g0, g1 = G(0), G(1)
base = [g0, g1, J(g0, g0), J(g0, g1), J(g1, g0), J(g0, J(g0, g0)), J(J(g0, g0), g0)]

def which(u, v):
    if v[0] == 'J':
        A, Q = v[1], v[2]
        if inimg(A, u):
            if Q[0] == 'J' and op(Q[1], u) == Q[2]: return 'W1'
            if u[0] == 'J' and u[2][0] == 'J' and u[2][2][0] == 'J' and _lvl2(u, Q, u[2][2][2]): return 'W3'
    return 'free'

made = collections.Counter(); imgbad = []; lawbad = []; n = 0
for x in base:
    for w in base:
        P1 = op(w, x)
        if P1 != J(w, x): continue                 # W3 needs a2 P1 = x, i.e. P1 free
        for Q in base[:5]:
            for A2 in base[:4]:
                if not inimg(A2, x): continue
                P2 = op(Q, x)
                wc = J(A2, J(Q, P2))
                if op(wc, x) != J(wc, x): continue
                # z = J A1 (J wc P1') where P1' = op(wc, x); W3 witness = a2 P1'
                P1c = op(wc, x)
                for A1 in base[:3]:
                    z = J(A1, J(wc, P1c))
                    if not _lvl2(z, Q, x): continue
                    for jm in base[:4]:
                        m = J(J(jm, z), Q)
                        n += 1
                        k = which(z, m); made[k] += 1
                        A = op(z, m)
                        if not inimg(A, m): imgbad.append((z, m, k, A))
                        for xp in base[:4]:
                            P = op(xp, m); QQ = op(xp, P); AA = op(z, m); C = op(AA, QQ)
                            if op(m, C) != xp: lawbad.append((xp, m, z, op(m, C)))
print('%s forced-W3 pairs n=%d  rule at op(z,m): %s' % (sys.argv[1], n, dict(made)))
print('IMG counterexamples:', len(imgbad), '   law failures:', len(lawbad))
for z, m, k, A in imgbad[:1]:
    print('  IMG FAIL rule=%s  op z m = %s' % (k, show(A)[:80]))
for xp, y, z, r in lawbad[:1]:
    print('  LAW FAIL x=%s' % show(xp)[:60]); print('    y=%s' % show(y)[:110]); print('    z=%s' % show(z)[:110])
