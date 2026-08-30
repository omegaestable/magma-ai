"""EXACT python mirror of the Lean `op` in gen/q34889_a.lean: the gate is an explicit conjunct of
each rule's condition (in q34889.py a failed gate falls back to J a b and is then compared), so this
file is what the certificate actually defines.  Validated to the same standard."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qmod
qmod.UNARY = []
from qmod import E, sz, show

LAW = ('x', ('z', (('x', ('z', 'x')), ('y', 'y'))))


def J(a, b):
    return ('J', a, b)


def tg(t):
    return 1 if t[0] == 'g' else (3 if t[0] == 'E' else 2)


def a1(t):
    return t[1] if t[0] == 'J' else t


def a2(t):
    return t[2] if t[0] == 'J' else t


def msr(a, b):
    sa, sb = sz(a), sz(b)
    return max(sa, sb) ** 2 + sa + sb


class QL:
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

    def _op(self, u, v):
        m = msr(u, v)
        g1 = msr(u, a1(a1(v))) < m
        g2 = msr(E, a1(v)) < m
        p1 = self.op(u, a1(a1(v))) if g1 else J(u, v)
        p2 = self.op(E, a1(v)) if g2 else J(u, v)
        P1 = tg(v) == 2 and a2(v) == E and tg(a1(v)) == 2 and not (a1(a1(v)) == E and a2(a1(v)) == E)
        P2 = tg(v) == 2 and a2(v) == E and tg(u) == 2 and a1(u) == a1(v)
        if u == v:
            return E
        if P1 and g1 and a2(a1(v)) == p1:
            return a1(a1(v))
        if P2 and g2 and a2(u) == p2:
            return E
        return J(u, v)

    def ev(self, p, s):
        if isinstance(p, str):
            return s[p]
        return self.op(self.ev(p[0], s), self.ev(p[1], s))


def M():
    return QL()


if __name__ == '__main__':
    import qcheck, itertools, time
    # 1. the Lean mirror agrees with gen/q34889.py everywhere
    import q34889
    A, B = QL(), q34889.M()
    pool = qmod.terms_upto(7, 2)
    n = d = 0
    for u in pool:
        for v in pool:
            n += 1
            if A.op(u, v) != B.op(u, v):
                d += 1
                if d <= 3:
                    print('DIFF u=%s v=%s lean=%s py=%s' % (show(u), show(v), show(A.op(u, v)), show(B.op(u, v))))
    print('op-diff vs q34889.py over %d pairs: %d' % (n, d))
    qcheck.check(M, LAW, ['x', 'z'], ['y'], sizes=((9, 1), (7, 2), (5, 3)), big=(11, 1, 5),
                 deepN=20000, seeds=(3, 4, 5, 6, 7), fuzzN=12000)
