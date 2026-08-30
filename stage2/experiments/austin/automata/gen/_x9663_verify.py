import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _x9663_lab4 as L
from _x9663_lab4 import op, show, sz, G, J, E, F, chain, prof
u  = J(G(2), G(2))
x1 = J(J(F(G(1),G(2)), F(G(0),G(1))), E(G(2), J(G(2),G(2))))
x2 = J(J(G(2),G(1)), J(G(2), J(G(2),G(2))))
for nm, x in (('x1', x1), ('x2', x2)):
    P = op(x, u); Q = op(x, P)
    print('%s: sz=%d  P=%s' % (nm, sz(x), show(P)[:70]))
    print('     Q=%s' % show(Q)[:70])
for z in (G(0), G(1), J(G(2),G(2))):
    A = op(z, u)
    C1 = op(A, op(x1, op(x1, u))); C2 = op(A, op(x2, op(x2, u)))
    r1 = op(u, C1); r2 = op(u, C2)
    print('z=%-14s C equal? %s   law(x1)=%s   law(x2)=%s'
          % (show(z)[:14], C1 == C2, r1 == x1, r2 == x2))
    if C1 == C2:
        print('    C=%s' % show(C1)[:90])
        print('    op(u,C)=%s' % show(r1)[:90])
