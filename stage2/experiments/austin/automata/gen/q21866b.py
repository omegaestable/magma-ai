"""STATUS: NOT A MODEL -- the reading of the A-side is not finitely structural.
  mode 0/1 die on   x=(g0*g0), y=(g0*(g0*g0)), z=g0, any w   (op(z,x)=y and op(y,y)=g0 is FORCED,
  so A is the generator g0 and nothing in the pair (g0, x*(x*w)) reveals the payload);
  mode 2 adds the level-1 existential and dies one level deeper on
        x = w = (g0*(g0*g0)), y = z = g0      (op(x,x)=g0, so B loses the (b*(b*_)) shape).
  The cascade is in DECODER LEVELS, not in tag constructors: no finite set of tags fixes it.

Law 21866:  x = (y*(z*x)) * (x*(x*w))     (21865 is its w:=z instance)

Carrier M ::= g i | J u v.   Both root arguments are read structurally:
  R1  u = (a*(d*b)),  v = (b*(b*e))   -> b
plus repairs.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qmod
qmod.UNARY = []
from qmod import E, sz, show

LAW = ('x', (('y', ('z', 'x')), ('x', ('x', 'w'))))


def J(a, b):
    return ('J', a, b)


def msr(a, b):
    sa, sb = sz(a), sz(b)
    return max(sa, sb) ** 2 + sa + sb


class Mod:
    def __init__(self, mode=0):
        self.memo = {}
        self.mode = mode

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
        if v[0] == 'J' and v[2][0] == 'J' and v[2][1] == v[1]:
            b = v[1]
            # (a) u = (a*(d*b)) : the A-side read structurally
            if u[0] == 'J' and u[2][0] == 'J' and u[2][2] == b:
                return b
            if self.mode >= 1:
                # (b) u = (a*c) with c = op(d,b) for the d that v's own shape supplies
                if u[0] == 'J' and self.g(u[1], b, m) == u[2]:
                    return b
            if self.mode >= 2:
                # (c) u is a DECODED A-value: op(u,b) = (u*(u*_)) makes u = op(y, op(u,b))
                if b[0] == 'J' and b[1] == u:
                    return b
        return J(u, v)

    def ev(self, p, s):
        if isinstance(p, str):
            return s[p]
        return self.op(self.ev(p[0], s), self.ev(p[1], s))


def M0():
    return Mod(0)


def M1():
    return Mod(1)


def M2():
    return Mod(2)


if __name__ == '__main__':
    import qcheck
    mode = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    qcheck.check({0: M0, 1: M1, 2: M2}[mode], LAW, ['x', 'y', 'z', 'w'], [],
                 sizes=((3, 2), (5, 1)), big=(7, 1, 3), deepN=8000, fuzzN=6000)
