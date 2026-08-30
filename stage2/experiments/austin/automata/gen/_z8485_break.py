"""_z8485_break.py -- targeted attack on the one cell session 2 could not prove.

NOTES_8485 "THE BLOCKER":  cell (R2, free, free, free, R2) -- P = op z x decoded by rule R2 instead
of R1.  Then no conjunct hands over  z = a2 (a2 x), and the top pair's R2 guard needs
`op (a2 (a2 x)) x = op z x` for a reason that is not syntactic.  Session 2 only ever saw that cell
via the level-k descent, where `x` happens to be a FREE encoding, so `a2 (a2 x) = z` literally.

Construction that breaks it.  Make the LAST step of the chain that R2 verifies at (z,x) DECODE, so
that a2 x is not `J _ z` and the locator is destroyed:

    z0, A, Cc  free generators
    X1 := J A (J Cc z0)              -- so a2 (a2 X1) = z0, i.e. R2 can read z0 off  a1 x
    c  := J z0 X1                    -- = op z0 X1 (free)
    z  := J c (J (J (J zz c) c) c)   -- so P1 c z holds, hence op c z = c
    x  := J X1 c

Then at (z, x):  p1 = op z0 X1 = c, p2 = op c z = c, p3 = op c z = c = a2 x, and P2 z x holds,
so **R2 fires and op z x = X1**.  But a2 (a2 x) = a2 c = X1, and op X1 x is free, so the top pair's
R2 guard is `op (op (op X1 x) y) y = R`, which is false.  With y a GENERATOR, P3/P4 cannot fire at
the top pair either (they need tg u = 2), and P1 fails, so the top pair stays free.
"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.setrecursionlimit(100000)
from _z8485_lean import LeanOp, show, sz, tg, a1, a2, msr, P1, P2, P3, P4

G = lambda i: ('g', i)
J = lambda a, b: ('J', a, b)

def instance(z0, A, Cc, zz, y):
    X1 = J(A, J(Cc, z0))
    c = J(z0, X1)
    z = J(c, J(J(J(zz, c), c), c))
    x = J(X1, c)
    return x, y, z, X1, c

def run(z0, A, Cc, zz, y, verbose=True):
    C = LeanOp()
    x, y, z, X1, c = instance(z0, A, Cc, zz, y)
    P = C.op(z, x); Q = C.op(P, y); R = C.op(Q, y); S = C.op(x, R); T = C.op(y, S)
    if verbose:
        print('x  =', show(x))
        print('y  =', show(y))
        print('z  =', show(z))
        print('  op z0 X1        =', show(C.op(z0, X1)), ' (want c =', show(c) + ')  branch', C.fired[(z0, X1)])
        print('  op c z          =', show(C.op(c, z)), ' (want c)                branch', C.fired[(c, z)])
        print('  P = op z x      =', show(P), ' branch', C.fired[(z, x)], ' (want branch 2)')
        print('  a2 (a2 x)       =', show(a2(a2(x))), '   z =', show(z), '   equal?', a2(a2(x)) == z)
        print('  op (a2(a2 x)) x =', show(C.op(a2(a2(x)), x)), ' branch', C.fired[(a2(a2(x)), x)])
        print('  Q = op P y      =', show(Q), ' branch', C.fired[(P, y)])
        print('  R = op Q y      =', show(R), ' branch', C.fired[(Q, y)])
        print('  S = op x R      =', show(S), ' branch', C.fired[(x, R)])
        print('  T = op y S      =', show(T), ' branch', C.fired[(y, S)])
        print('  LAW  op y (op x (op (op (op z x) y) y)) = x  ?  ', T == x)
    return T == x, (x, y, z)

if __name__ == '__main__':
    print('=' * 78)
    print('canonical instance: z0=g0 A=g1 Cc=g2 zz=g3 y=g5')
    print('=' * 78)
    ok, s = run(G(0), G(1), G(2), G(3), G(5))
    print()
    print('=' * 78)
    print('sweep over generator choices and small y')
    print('=' * 78)
    import itertools
    pool = [G(i) for i in range(4)] + [J(G(0), G(1)), J(G(1), G(0)), J(G(2), G(2))]
    bad = 0; tot = 0
    for z0, A, Cc, zz, y in itertools.product(pool[:5], pool[:4], pool[:4], pool[:3], pool):
        tot += 1
        o, s = run(z0, A, Cc, zz, y, verbose=False)
        if not o:
            bad += 1
            if bad <= 6:
                print('LAW FAILS: x=%s  y=%s  z=%s' % (show(s[0]), show(s[1]), show(s[2])))
    print('\nsweep: %d instances, %d LAW FAILURES' % (tot, bad))
