"""_y6912_qfix.py : least-fixed-point prober for the E-quotient carrier of law 6912.

Law 6912 (L-form, normalised):  x = y * (y * ((z*z) * (x*y)))
With every square collapsed to a single 0-ary constant E, that is the two-variable law

    LE :   x = op(y, op(y, op(E, op(x, y))))        together with   op(u,u) = E

Chain (bottom-up):  A = op(x,y),  B = op(E,A),  C = op(y,B),  forced  op(y,C) = x.

Every (x,y) pair FORCES one entry op(y,C) = x.  We saturate the table over a term pool and report
  * COLLISIONS (two different payloads forced onto the same pair) -> the E-carrier is REFUTED
  * degenerate cells (C == y, so op(y,C) = E by the square rule -> forces x = E)
  * the SHAPES of the forced entries, so a finite rule set can be read off.

Usage: python -u gen/_y6912_qfix.py [maxsize] [gens] [rounds]
"""
import sys, os, collections, itertools

E = ('E',)


def sz(t):
    if t[0] in ('g', 'E'):
        return 1
    return 1 + sz(t[1]) + sz(t[2])


def show(t):
    if t[0] == 'E':
        return 'E'
    if t[0] == 'g':
        return 'g%d' % t[1]
    return '(%s*%s)' % (show(t[1]), show(t[2]))


def terms_upto(maxsize, gens):
    by = {1: [('g', i) for i in range(gens)] + [E]}
    allt = list(by[1])
    for n in range(2, maxsize + 1):
        cur = []
        for a in range(1, n - 1):
            b = n - 1 - a
            for s in by.get(a, []):
                for t in by.get(b, []):
                    cur.append(('J', s, t))
        by[n] = cur
        allt += cur
    return allt


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

    def force(self, x, y):
        A = self.op(x, y)
        B = self.op(E, A)
        C = self.op(y, B)
        if C == y:                      # op(y,C) = E by the square rule
            if x != E:
                self.bad.append(('C=y', x, y))
            return False
        old = self.dec.get((y, C))
        if old is None:
            self.dec[(y, C)] = x
            return True
        if old != x:
            self.collisions.append((y, C, old, x))
        return False


def shape(u, v, x):
    """classify a forced entry op(u,v) = x by the structural pattern of v."""
    if v[0] != 'J':
        return 'v-not-J'
    tags = []
    tags.append('v1=u' if v[1] == u else ('v1=E' if v[1] == E else 'v1=?'))
    w = v[2]
    if w[0] != 'J':
        tags.append('v2-not-J:' + ('E' if w == E else '?'))
        return ' '.join(tags)
    tags.append('v21=E' if w[1] == E else ('v21=u' if w[1] == u else 'v21=?'))
    q = w[2]
    if q[0] != 'J':
        tags.append('v22-not-J:' + ('E' if q == E else '?'))
        return ' '.join(tags)
    tags.append('v221=x' if q[1] == x else ('v221=E' if q[1] == E else 'v221=?'))
    tags.append('v222=u' if q[2] == u else ('v222=E' if q[2] == E else 'v222=?'))
    return ' '.join(tags)


def saturate(pool, rounds=12, verbose=True):
    F = Fix()
    for it in range(rounds):
        added = 0
        for x in pool:
            for y in pool:
                if F.force(x, y):
                    added += 1
        if verbose:
            print('round %d: dec=%d added=%d collisions=%d bad=%d'
                  % (it, len(F.dec), added, len(F.collisions), len(F.bad)), flush=True)
        if added == 0:
            break
    return F


if __name__ == '__main__':
    ms = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    gens = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    rounds = int(sys.argv[3]) if len(sys.argv) > 3 else 12
    pool = terms_upto(ms, gens)
    print('pool %d terms (size<=%d, %d gens)' % (len(pool), ms, gens))
    F = saturate(pool, rounds)
    print()
    print('collisions %d, bad %d, dec %d' % (len(F.collisions), len(F.bad), len(F.dec)))
    for u, v, a, b in F.collisions[:8]:
        print('  COLLISION op(%s, %s) = %s   AND   %s' % (show(u), show(v), show(a), show(b)))
    for b in F.bad[:8]:
        print('  BAD %s x=%s y=%s' % (b[0], show(b[1]), show(b[2])))
    cnt = collections.Counter()
    ex = {}
    for (u, v), x in F.dec.items():
        k = shape(u, v, x)
        cnt[k] += 1
        ex.setdefault(k, (u, v, x))
    print()
    for k, n in cnt.most_common():
        u, v, x = ex[k]
        print('  %6d  %-55s  e.g. op(%s, %s) = %s' % (n, k, show(u), show(v), show(x)))
