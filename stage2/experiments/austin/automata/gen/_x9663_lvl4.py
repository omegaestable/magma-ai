"""Level-4 probe: make BOTH witness positions of u's code decoded, so x is unreadable from u.

Need:  u = J A1 (J w P1)  with  P1 = op(w,x) = a1(a2 x)  (so P1 is decoded, not J w x)
       and A1 = a1 (a2 x) too (so inimg A1 x holds by disjunct 2 rather than A1 = J j x).
That forces A1 = P1 = p := a1 (a2 x), and x must be the code of p w.r.t. w:
       x = J A2 (J p (op p w)),  inimg A2 w.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _idc_lib import G, J, sz, show
M = __import__(sys.argv[1] if len(sys.argv) > 1 else 'q9663c')
op, inimg = M.op, M.inimg
g0, g1 = G(0), G(1)
base = [g0, g1, J(g0, g0), J(g0, g1), J(g1, g0), J(g0, J(g0, g0)), J(J(g0, g0), g0)]

n = bad = 0; shown = 0; cells = {}
for w in base:
    for p in base:
        for A2 in base + [J(g0, w), J(g1, w)]:
            if not inimg(A2, w): continue
            P2 = op(p, w)
            x = J(A2, J(p, P2))
            if op(w, x) != p:  continue        # P1 must really decode to p
            if not inimg(p, x): continue
            for wtop in base:
                P1 = op(wtop, x)
                if P1 != p: continue           # need op(wtop,x) decoded to p as well
                y = J(p, J(wtop, P1))
                if op(x, y) != wtop: continue
                for z in base[:4] + [x, y]:
                    n += 1
                    P = op(x, y); Q = op(x, P); A = op(z, y); C = op(A, Q); r = op(y, C)
                    d = (P != J(x, y), Q != J(x, P), A != J(z, y), C != J(A, Q))
                    c = cells.setdefault(d, [0, 0]); c[0] += 1
                    if r != x:
                        bad += 1; c[1] += 1
                        if shown < 2:
                            shown += 1
                            print('FAIL x=%s' % show(x)[:110]); print('     y=%s' % show(y)[:110])
                            print('     z=%s -> %s' % (show(z)[:60], show(r)[:110]))
print('level-4 constructed: tested=%d FAILS=%d' % (n, bad))
for d in sorted(cells, key=lambda t: (sum(t), t)):
    print('  cell P%d Q%d A%d C%d : %6d, %d FAIL' % (d[0], d[1], d[2], d[3], cells[d][0], cells[d][1]))
