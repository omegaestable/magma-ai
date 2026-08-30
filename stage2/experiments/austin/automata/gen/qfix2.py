"""Least-fixed-point prober, variant 2: NO extra tag constructor.

Carrier: g i | E | J u v.       op(u,u) = E  (one square, kills the z-dependence);
everything else is the free product J u v unless the law FORCES a value.
The law  x = y*(((y*x)*x)*(z*z))  forces   op(u, C_u(x)) = x   with C_u(x) = op(op(op(u,x),x), E).
Saturate over a term pool, report collisions and the shapes of the forced entries.
"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qmod
qmod.UNARY = []
from qmod import E, sz, show, terms_upto


class Fix:
    def __init__(self):
        self.dec = {}
        self.collisions = []
        self.bad = []

    def op(self, u, v):
        if u == v:
            return E
        r = self.dec.get((u, v))
        if r is not None:
            return r
        return ('J', u, v)

    def code(self, u, x):
        return self.op(self.op(self.op(u, x), x), E)

    def force(self, u, x):
        C = self.code(u, x)
        if C == u:                       # op(u,C) = E is forced by the square rule
            if x != E:
                self.bad.append(('C=u', u, x))
            return False
        old = self.dec.get((u, C))
        if old is None:
            self.dec[(u, C)] = x
            return True
        if old != x:
            self.collisions.append((u, C, old, x))
        return False


def saturate(pool, rounds=15, verbose=True):
    F = Fix()
    for it in range(rounds):
        added = 0
        for u in pool:
            for x in pool:
                if F.force(u, x):
                    added += 1
        if verbose:
            print('round %d: dec=%d added=%d collisions=%d bad=%d'
                  % (it, len(F.dec), added, len(F.collisions), len(F.bad)), flush=True)
        if added == 0:
            break
    return F


def sh(t, u, x):
    if t == u:
        return 'u'
    if t == x:
        return 'X'
    if t == E:
        return 'E'
    if t[0] == 'J':
        return '(%s*%s)' % (sh(t[1], u, x), sh(t[2], u, x))
    return 'a'


if __name__ == '__main__':
    ms = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    g = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    pool = terms_upto(ms, g)
    print('pool', len(pool))
    F = saturate(pool)
    print('collisions', len(F.collisions))
    for u, v, a, b in F.collisions[:10]:
        print('   COLL u=%s v=%s  -> %s  AND  %s' % (show(u), show(v), show(a), show(b)))
    print('bad', len(F.bad))
    for b in F.bad[:6]:
        print('   BAD', b[0], show(b[1]), show(b[2]))
    holes = collections.Counter()
    ex = {}
    for (u, v), x in F.dec.items():
        k = 'v=%s' % sh(v, u, x)
        holes[k] += 1
        ex.setdefault(k, (u, v, x))
    print('distinct entry shapes', len(holes))
    for k, c in holes.most_common(25):
        u, v, x = ex[k]
        print('   %-46s x%-7d e.g. u=%s v=%s x=%s' % (k, c, show(u), show(v), show(x)))
