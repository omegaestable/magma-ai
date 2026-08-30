"""_s9_17286_uattack.py -- targeted probe: can branch U fire at the TOP product with a2 A != x?

Construction (hand-derived, session 9):
    wx = g20, wz = g30, q = g50, junk = g51, jy = g9
    A  = J q c              where c = J junk P
    P  = J wx (J A wx)      (so P = a2 x)
    x  = J wx P             = encB-like:  x = J wx (J wx (J A wx))
    z  = J wz (J wz (J P wz))
    y  = J jy A
Then  op y x = a2 y = A (branch U),  op x z = a2 x = P (branch U),
      op (a2 A) z = op c z = a2 c = P (branch U), so branch U fires at the top and
      returns a2 A = c != x.

P is defined in terms of A and A in terms of c and c in terms of P -> the definition is
circular, so build it as a fixed point over a formal placeholder instead: note P only ever
appears inside c as a2 c, and c inside A as a2 A, and A inside P as a1 (a2 P).  Solve by
choosing the nesting explicitly with a "knot" term.
"""
import os, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('lab', os.path.join(HERE, '_x17286_lab.py'))
lab = importlib.util.module_from_spec(spec); spec.loader.exec_module(lab)
g, J, tg, a1, a2, sz, show = lab.g, lab.J, lab.tg, lab.a1, lab.a2, lab.sz, lab.show

spec2 = importlib.util.spec_from_file_location('pr', os.path.join(HERE, '_s9_17286_probe.py'))
pr = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(pr)
Mod = pr.Mod


def report(name, x, y, z):
    M = Mod()
    A = M.op(y, x); P = M.op(x, z); Q = M.op(z, P); B = M.op(z, Q); top = M.op(A, B)
    print('--- %s' % name)
    print('   x   =', show(x), 'sz', sz(x))
    print('   A   =', show(A), ' free?', A == J(y, x))
    print('   P   =', show(P), ' free?', P == J(x, z))
    print('   Q   =', show(Q), ' free?', Q == J(z, P))
    print('   B   =', show(B), ' free?', B == J(z, Q))
    print('   top =', show(top))
    print('   LAW', 'OK' if top == x else '*** FAIL ***')
    return top == x


# The circularity is only apparent: A occurs inside P, and P occurs inside c = a2 A.
# So take A to be any term whose second component c has a2 c = P for the P built from A.
# Break it by using a DIFFERENT witness for the second branch-U check: what op c z needs is
# op (a2 c) (a1 z) = a2 (a2 z), and a2 (a2 z) is ours to choose.  So set c = J junk D for an
# ARBITRARY D, and choose z = J wz (J wz (J D wz)) so that op D wz = J D wz = a2 (a2 z).
# Then op c z = a2 c = D, and branch U at the top needs D = a2 (a2 B) = P = op x z.
# So we need op x z = D with D chosen freely -> pick D = a2 x and x = J wx (J wx (J A wx))
# with A = J q (J junk D).  Now D = a2 x = J wx (J A wx) mentions A which mentions D: build
# the knot by *unrolling once* -- give D a placeholder shape and check what op actually does.
def build():
    wx, wz, q, junk, jy = g(20), g(30), g(50), g(51), g(9)
    # unrolled: choose A first with an arbitrary c, then define x from A, then D := a2 x.
    # For op c z = a2 c = P we need a2 c = P, i.e. c = J junk P.  P = a2 x = J wx (J A wx).
    # A = J q c = J q (J junk (J wx (J A wx))) -- genuinely circular.  Use a two-step tower:
    # take A0 arbitrary, x = J wx (J wx (J A0 wx)), P = a2 x, c = J junk P, A = J q c.
    # Then op y x = A requires op (a2 y) (a1 x) = a2 (a2 x) with a2 y = A: op A wx = J A wx
    # (free, since wx is a generator) and a2 (a2 x) = J A0 wx.  So we need A = A0.
    # => the knot is real.  Instead drop the requirement op y x = A via branch U and get A
    # from the FREE product: y such that J y x has a2 = x -- that is the A-FREE case.
    # So test the A-decoded case with A obtained from branch V/R instead.
    return wx, wz, q, junk, jy


def attack1():
    """A-free control: top must be x via branch U."""
    wx, wz = g(20), g(30)
    A0 = J(g(1), g(2))
    x = J(wx, J(wx, J(A0, wx)))
    z = J(wz, J(wz, J(J(wx, J(A0, wx)), wz)))
    y = g(7)
    return report('control A-free', x, y, z)


def attack2():
    """A decoded through branch U at (y,x), a2 A a WRAPPER of P."""
    wx, wz, junk, jy = g(20), g(30), g(51), g(9)
    # A must satisfy: op A wx = a2 (a2 x)  (so that op y x = a2 y = A with y = J jy A)
    # take x = J wx (J wx (J A wx)) -> a2 (a2 x) = J A wx, and op A wx = J A wx free. OK for ANY A.
    # want a2 A = c with op c z = P = a2 x = J wx (J A wx).
    # op c z via branch U: a2 c must satisfy op (a2 c) wz = a2 (a2 z); pick z = J wz (J wz (J (a2 c) wz)).
    # and then op c z = a2 c, which must equal P = J wx (J A wx).   So a2 c = J wx (J A wx),
    # i.e. c = J junk (J wx (J A wx)) and A = J q c -- circular again in A.
    # Break the knot: let A be the FIXED POINT of A |-> J q (J junk (J wx (J A wx))) unrolled
    # k times with a generator at the bottom; the branch-U checks only look one level deep.
    for k in range(0, 5):
        A = g(60)
        for _ in range(k):
            A = J(g(50), J(junk, J(wx, J(A, wx))))
        x = J(wx, J(wx, J(A, wx)))
        P = a2(x)                       # J wx (J A wx)
        c = a2(A) if tg(A) == 2 else None
        if c is None:
            continue
        z = J(wz, J(wz, J(a2(c), wz)))
        y = J(jy, A)
        ok = report('attack2 k=%d' % k, x, y, z)
        if not ok:
            print('   >>> a2 A =', show(c), '  x =', show(x))
    return True


if __name__ == '__main__':
    attack1()
    attack2()
