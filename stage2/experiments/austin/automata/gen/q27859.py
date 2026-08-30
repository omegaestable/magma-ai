"""Law 27859:  x = ((y*(y*x))*x) * (z*z)      -- E-quotient carrier (all squares = E).

Carrier M ::= g i | E | J u v ;  msr u v = max(sz u, sz v)^2 + sz u + sz v.
With every square equal to E the law is the 2-variable statement
        op (op (op y (op y x)) x) E = x .
op u v =
  R1 SQ    u = v                                                   -> E
  R2 DEC   v = E, u = ((a*q)*b), <a, <a,b>> = (a*q)                 -> b
  R3                                                               -> u*v
(repairs appended below as they are found by gen/qcheck.py)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qmod
qmod.UNARY = []
from qmod import E, sz, show

LAW = ('x', ((('y', ('y', 'x')), 'x'), ('z', 'z')))


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
        if v == E and u[0] == 'J':
            c, b = u[1], u[2]
            if c[0] == 'J' and self.g(c[1], self.g(c[1], b, m), m) == c:
                return b
            if self.g(b, E, m) == c:          # SELF: the x=y chain, whose first product is E
                return b
        return J(u, v)

    def ev(self, p, s):
        if isinstance(p, str):
            return s[p]
        return self.op(self.ev(p[0], s), self.ev(p[1], s))


def M():
    return Mod()


if __name__ == '__main__':
    import qcheck
    qcheck.check(M, LAW, ['x', 'y'], ['z'], sizes=((9, 1), (5, 2), (5, 3)), big=(11, 1, 5))
