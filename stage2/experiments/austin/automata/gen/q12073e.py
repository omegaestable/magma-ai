"""Law 12073:  x = y * (((y*x)*x) * (z*z))     -- the E-quotient carrier, gated exactly as Lean will be.

Carrier   M ::= g i | E | J u v
Measure   msr u v = max (sz u) (sz v) ^ 2 + sz u + sz v          (every nested call is gated by it)

op u v =
  R1 SQ    u = v                                                     -> E
  R2 DEC   v = ((a*b)*E),  p := <u,b>,  <p,b> = (a*b)                -> b
  R3 SELF  v = (d*E),  u != E,  <E,u> = d                            -> u
  R4 GSC   v = (w*E),  not (u = E and w = E),  <u,w> = E             -> ((E*w)*E)
  R5                                                                 -> u*v
where <a,b> = op a b when msr a b < msr u v, else J a b (the gate).

Every square is E, so the law's z disappears and what is left is the 2-variable statement
   op u (op (op (op u x) x) E) = x .
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qmod
qmod.UNARY = []
from qmod import Model, E, sz, show

LAW = ('x', ('y', ((('y', 'x'), 'x'), ('z', 'z'))))


def J(a, b):
    return ('J', a, b)


def msr(a, b):
    sa, sb = sz(a), sz(b)
    return max(sa, sb) ** 2 + sa + sb


class Q12073:
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
        if v[0] == 'J' and v[2] == E:
            w = v[1]
            if w[0] == 'J':
                b = w[2]
                p = self.g(u, b, m)
                if self.g(p, b, m) == w:
                    return b
            if u != E and self.g(E, u, m) == w:
                return u
            if u != E and w == u:
                return J(self.g(E, u, m), E)
            if not (u == E and w == E) and self.g(u, w, m) == E:
                return J(J(E, w), E)
        return J(u, v)

    def ev(self, p, s):
        if isinstance(p, str):
            return s[p]
        return self.op(self.ev(p[0], s), self.ev(p[1], s))


def M():
    return Q12073()


if __name__ == '__main__':
    import qcheck
    qcheck.check(M, LAW, ['x', 'y'], ['z'], sizes=((9, 1), (5, 2), (5, 3)), big=(11, 1, 5))
