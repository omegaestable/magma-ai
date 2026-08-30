"""STATUS: NOT A MODEL -- refuted 2026-08-29 by the x<=9 sweep (gen/qbig2.out):
    x = ((g0*g0)*((g0*g0)*g0)),  y = (g0*(g0*g0)),  any z
  op(y,x) decodes to g0 AND op(x,x) decodes to g0 (both are forced readings), so the third
  product loses the payload on BOTH sides at once and neither reading rule can recover it.
  A repair needs the existential decoder  "exists a,b : op(a, op(a,t)) = u"  -- see the report.
  Separately PROVED: no model of 22591 can have all squares equal (see the note below), so the
  E-quotient that works for 12073/27859 is impossible here.
      all squares = e  =>  (x=y=e)  e = (e*(e*e))*((e*e)*z) = e*(e*z),  so e*(e*z) = e for all z;
      then (y=e, any x)  x = (e*(e*x))*((x*x)*z) = e*(e*z) = e.   The magma is trivial.

Law 22591:  x = (y*(y*x)) * ((x*x)*z)   -- plain free magma, semantic reading rule.

An E-collapse is REFUTED for this law: if every square s satisfies "s*z independent of z" then for
y := s the left factor y*(y*x) is s*(...) = sigma(s), which is again a square, so x = sigma^2(s) for
every x -- the one-element magma.  So the square must stay a real term and the rule reads it.
Carrier M ::= g i | J u v.
op u v =
  R1a v = (s*t),      u = (a*(a*b)),  <b,b> = s   -> b
  R1b v = ((b*b)*t),  u = (a*c),      <a,b> = c   -> b
  R2                                          -> u*v
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
        m = msr(u, v)
        if v[0] == 'J' and u[0] == 'J':
            a, c = u[1], u[2]
            # (a) read the payload out of u = (a*(a*b)) and check the square against v.1
            if c[0] == 'J' and c[1] == a and self.g(c[2], c[2], m) == v[1]:
                return c[2]
            # (b) read the payload out of v.1 = (b*b) and check u = (a * op a b)
            if v[1][0] == 'J' and v[1][1] == v[1][2] and self.g(a, v[1][1], m) == c:
                return v[1][1]
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
