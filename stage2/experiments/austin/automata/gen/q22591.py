"""Law 22591:  x = (y*(y*x)) * ((x*x)*z)      -- E-quotient carrier (all squares = E).

With every square equal to E the right argument is  op E z, which is  J E z  (z != E) or E (z = E);
so op (..) must ignore the whole right argument as long as it has one of those two shapes.
Carrier M ::= g i | E | J u v ;  msr u v = max(sz u, sz v)^2 + sz u + sz v.
op u v =
  R1 SQ    u = v                                                    -> E
  R2 DEC   (v = E or v = (E*t)),  u = (a*c),  <a,<a,b>> = c ...      -> b
  R3                                                                -> u*v
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qmod
qmod.UNARY = []
from qmod import E, sz, show

LAW = ('x', (('y', ('y', 'x')), (('x', 'x'), 'z')))


def J(a, b):
    return ('J', a, b)


def msr(a, b):
    sa, sb = sz(a), sz(b)
    return max(sa, sb) ** 2 + sa + sb


class Mod:
    def __init__(self):
        self.memo = {}

    def op(self, u, v):
        key = (u, v)
        r = self.memo.get(key)
        if r is not None:
            return r
        r = self._op(u, v)
        self.memo[key] = r
        return r

    def g(self, a, b, m):
        return self.op(a, b) if msr(a, b) < m else J(a, b)

    def _op(self, u, v):
        if u == v:
            return E
        m = msr(u, v)
        if (v == E or (v[0] == 'J' and v[1] == E)) and u[0] == 'J':
            a, c = u[1], u[2]
            if c[0] == 'J' and c[1] == a:
                return c[2]
            if c == E:                    # SELF: y = x, so the inner product op(y,x) is E
                return a
        return J(u, v)

    def ev(self, p, s):
        if isinstance(p, str):
            return s[p]
        return self.op(self.ev(p[0], s), self.ev(p[1], s))


def M():
    return Mod()


if __name__ == '__main__':
    import qcheck
    qcheck.check(M, LAW, ['x', 'y', 'z'], [], sizes=((7, 1), (5, 2)), big=(9, 1, 3))
