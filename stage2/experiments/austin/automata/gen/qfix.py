"""Least-fixed-point prober for the E-quotient carrier of 12073.

Carrier: g i | E | Q u | J u v.
Base rules   op(u,u) = E,  op(u,E) = Q u,  otherwise J u v,
plus a DECODE TABLE  dec[(u,w)] = x  meaning  op(u, Q w) = x.
The law  x = y * (((y*x)*x)*(z*z))  with all squares = E is exactly
        op(u, op(B_u(x), E)) = x   where B_u(x) = op(op(u,x),x).
So every pair (u,x) FORCES one decode entry.  We saturate the table over a pool of terms and report
  * COLLISIONS   (two different payloads forced onto the same (u,w))  -> the construction is refuted
  * BAD-SHAPE    (B_u(x) = E, so the third product is E, not Q _)     -> a separate forced identity
  * the SHAPES of the forced entries, so we can see whether finitely many rules generate them.
"""
import sys, os, itertools, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qmod
qmod.UNARY = ['Q']
from qmod import E, sz, show, terms_upto


def Q(u):
    return ('Q', u)


class Fix:
    def __init__(self):
        self.dec = {}
        self.collisions = []
        self.bad = []

    def op(self, u, v):
        if u == v:
            return E
        if v == E:
            return Q(u)
        if v[0] == 'Q':
            r = self.dec.get((u, v[1]))
            if r is not None:
                return r
        return ('J', u, v)

    def force(self, u, x):
        A = self.op(u, x)
        B = self.op(A, x)
        C = self.op(B, E)
        if C == E:          # B == E : the third product collapsed; then op(u,E) must equal x
            if self.op(u, E) != x:
                self.bad.append(('B=E', u, x))
            return False
        w = C[1] if C[0] == 'Q' else None
        if w is None:
            self.bad.append(('C-not-Q', u, x, C))
            return False
        old = self.dec.get((u, w))
        if old is None:
            self.dec[(u, w)] = x
            return True
        if old != x:
            self.collisions.append((u, w, old, x))
        return False


def saturate(pool, rounds=12, verbose=True):
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


def classify(F):
    """which forced entries are NOT explained by the structural rule  op(u, Q(J a b)) = b  ?"""
    struct = 0
    holes = collections.Counter()
    examples = {}
    for (u, w), x in F.dec.items():
        if w[0] == 'J' and w[2] == x:
            struct += 1
            continue
        k = shape(u, w, x)
        holes[k] += 1
        examples.setdefault(k, (u, w, x))
    return struct, holes, examples


def shape(u, w, x):
    def sh(t, u):
        if t == u:
            return 'u'
        if t == E:
            return 'E'
        if t[0] == 'Q':
            return 'Q(%s)' % sh(t[1], u)
        if t[0] == 'J':
            return '(%s*%s)' % (sh(t[1], u), sh(t[2], u))
        return 'a'
    return 'w=%s  x=%s' % (sh(w, u), sh(x, u))


if __name__ == '__main__':
    ms = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    g = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    pool = terms_upto(ms, g)
    print('pool', len(pool))
    F = saturate(pool)
    print('collisions', len(F.collisions))
    for u, w, a, b in F.collisions[:10]:
        print('   COLL u=%s w=%s  -> %s  AND  %s' % (show(u), show(w), show(a), show(b)))
    print('bad', len(F.bad))
    for b in F.bad[:10]:
        print('   BAD', b[0], ' '.join(show(t) for t in b[1:] if isinstance(t, tuple)))
    st, holes, ex = classify(F)
    print('structural entries', st, ' holes', sum(holes.values()))
    for k, c in holes.most_common(20):
        u, w, x = ex[k]
        print('   %-40s x%-6d  e.g. u=%s w=%s x=%s' % (k, c, show(u), show(w), show(x)))
