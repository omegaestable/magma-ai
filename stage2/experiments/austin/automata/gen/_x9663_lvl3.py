"""Level-3 probe for the 9663 two-witness decoder.

W2 reads the witness x off a2 (a1 u), which needs u's junk slot A1 to be a FREE product J j x.
Construct instances where A1 is instead the DECODED kind (inimg via  x = J _ (J A1 _) ), so x is
not readable there, and both chain products decode.
"""
import sys, os, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _idc_lib import G, J, sz, show
M = __import__(sys.argv[1] if len(sys.argv) > 1 else 'q9663b')
op = M.op
inimg = M.inimg
g0, g1, g2 = G(0), G(1), G(2)

def law(x, y, z):
    P = op(x, y); Q = op(x, P); A = op(z, y); C = op(A, Q)
    return op(y, C), (P != J(x, y), Q != J(x, P), A != J(z, y), C != J(A, Q))

base = [g0, g1, J(g0, g0), J(g0, g1), J(g1, g0), J(g0, J(g0, g0)), J(J(g0, g0), g0)]
bad = 0; n = 0; cells = {}
shown = 0
for A1 in base:
    for s in base[:4]:
        for t in base[:4]:
            x = J(s, J(A1, t))                 # so inimg(A1,x) holds via disjunct 2
            assert inimg(A1, x)
            for w in base[:5]:
                P1 = op(w, x)
                y = J(A1, J(w, P1))            # y = code of w w.r.t. x, junk slot NOT free
                if op(x, y) != w: continue     # DEC must fire
                for w2 in base[:4]:
                    for A2 in base[:4]:
                        if not inimg(A2, x): continue
                        P2 = op(w2, x)
                        w_ = J(A2, J(w2, P2))
                        # rebuild y so that op(x,y) = w_ and op(x,w_) = w2
                        P1_ = op(w_, x)
                        y2 = J(A1, J(w_, P1_))
                        if op(x, y2) != w_: continue
                        if op(x, w_) != w2: continue
                        for z in base[:4] + [x, y2]:
                            n += 1
                            r, d = law(x, y2, z)
                            cells.setdefault(d, [0, 0])
                            cells[d][0] += 1
                            if r != x:
                                cells[d][1] += 1; bad += 1
                                if shown < 3:
                                    shown += 1
                                    print('FAIL x=%s' % show(x)[:100])
                                    print('     y=%s' % show(y2)[:100])
                                    print('     z=%s' % show(z)[:100])
                                    print('     -> %s' % show(r)[:100])
print('level-3 constructed: tested=%d FAILS=%d' % (n, bad))
for d in sorted(cells, key=lambda t: (sum(t), t)):
    print('  cell P%d Q%d A%d C%d : %6d, %d FAIL' % (d[0], d[1], d[2], d[3], cells[d][0], cells[d][1]))
