"""Law 34889 (L-form dual):  x = z * ((x * (z * x)) * (y * y))   -- the E-quotient carrier.

Carrier   M ::= g i | E | J u v
Measure   msr u v = max (sz u) (sz v) ^ 2 + sz u + sz v          (every nested call is gated by it)

Every square is E, so y disappears and what is left is the 2-variable statement
   op z (op (op x (op z x)) E) = x .
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qmod
qmod.UNARY = []
from qmod import Model, E, sz, show

LAW = ('x', ('z', (('x', ('z', 'x')), ('y', 'y'))))


def J(a, b):
    return ('J', a, b)


def msr(a, b):
    sa, sb = sz(a), sz(b)
    return max(sa, sb) ** 2 + sa + sb


VARIANT = os.environ.get('Q34889', 'A')


class Q34889:
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
                a, b = w[1], w[2]
                if not (a == E and b == E) and self.g(u, a, m) == b:
                    return a                              # R2 DEC
            if u[0] == 'J' and u[1] == w and self.g(E, w, m) == u[2]:
                return E                                  # R3 SELFE   (x = E branch)
        return J(u, v)

    def ev(self, p, s):
        if isinstance(p, str):
            return s[p]
        return self.op(self.ev(p[0], s), self.ev(p[1], s))


def M():
    return Q34889()


if __name__ == '__main__':
    import qcheck
    qcheck.check(M, LAW, ['x', 'z'], ['y'], sizes=((7, 1), (5, 2)), big=None,
                 deepN=3000, seeds=(3,), fuzzN=3000)
