"""Derived-identity finder: e-graph congruence closure over instances of one law.

For a law  x = RHS(x, y, ...)  every substitution of the variables by concrete free terms is an
equation between two free terms.  Union them all, congruence-close, and report the smallest pair of
DISTINCT free terms that end up in the same class.  Such a pair is a derived identity: the law
identifies two distinct elements of the free term algebra, so it has NO free-term-algebra model
(Track C) -- no rule set can help, the carrier has to change.

usage: python gen/_p2_ident.py <eq> [poolsize=5] [gens=1] [maxsz=40]
"""
import sys, os, itertools, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
from freemodel import normalise, catalog, pvars, size
from laws import parse_eq


def dual_pat(p):
    return p if isinstance(p, str) else (dual_pat(p[1]), dual_pat(p[0]))


def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))


def sz(t):
    return 1 if t[0] == 'g' else 1 + sz(t[1]) + sz(t[2])


def terms_upto(maxsize, gens):
    by = {1: [('g', i) for i in range(gens)]}
    for n in range(3, maxsize + 1, 2):
        by[n] = []
        for a in range(1, n - 1, 2):
            b = n - 1 - a
            if b in by:
                for s in by[a]:
                    for t in by[b]:
                        by[n].append(('J', s, t))
    out = []
    for n in sorted(by):
        out += by[n]
    return out


class EG:
    def __init__(self, maxsz):
        self.par = {}
        self.maxsz = maxsz
        self.kids = {}        # term -> (a,b) for J-terms

    def add(self, t):
        if t in self.par:
            return t
        if sz(t) > self.maxsz:
            return None
        self.par[t] = t
        if t[0] == 'J':
            if self.add(t[1]) is None or self.add(t[2]) is None:
                del self.par[t]
                return None
            self.kids[t] = (t[1], t[2])
        return t

    def find(self, t):
        r = t
        while self.par[r] != r:
            r = self.par[r]
        while self.par[t] != r:
            self.par[t], t = r, self.par[t]
        return r

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        # keep the smaller term as representative
        if sz(rb) < sz(ra):
            ra, rb = rb, ra
        self.par[rb] = ra
        return True

    def congruence(self, rounds=30):
        for _ in range(rounds):
            sigs = {}
            changed = False
            for t, (a, b) in self.kids.items():
                k = (self.find(a), self.find(b))
                if k in sigs:
                    changed |= self.union(sigs[k], t)
                else:
                    sigs[k] = t
            if not changed:
                return
        print('  (congruence did not stabilise in %d rounds)' % rounds)


def run(eq, poolsize, gens, maxsz):
    cat = catalog()
    orig = normalise(parse_eq(cat[eq]))
    dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
    law = ('x', dual_pat(orig[1])) if dualized else orig
    vs = pvars(law[1])
    pool = terms_upto(poolsize, gens)
    print('law %d %s  (dualized=%s)  vars=%s  pool=%d terms<=size %d, %d gens'
          % (eq, show_pat(law[1]), dualized, vs, len(pool), poolsize, gens))

    def build(p, s):
        if isinstance(p, str):
            return s[p]
        return ('J', build(p[0], s), build(p[1], s))

    G = EG(maxsz)
    for t in pool:
        G.add(t)
    n = 0
    skipped = 0
    pairs = []
    for vals in itertools.product(pool, repeat=len(vs)):
        s = dict(zip(vs, vals))
        rhs = build(law[1], s)
        if G.add(rhs) is None:
            skipped += 1
            continue
        n += 1
        pairs.append((s['x'], rhs))
    for a, b in pairs:
        G.union(a, b)
    G.congruence()
    print('  %d instances added (%d skipped for size > %d), %d terms' % (n, skipped, maxsz, len(G.par)))
    cls = collections.defaultdict(list)
    for t in G.par:
        cls[G.find(t)].append(t)
    # the interesting classes: two distinct SMALL terms merged
    found = []
    for r, ms in cls.items():
        small = sorted([t for t in ms if sz(t) <= poolsize], key=sz)
        if len(small) >= 2:
            found.append((sz(small[0]) + sz(small[1]), small[0], small[1], len(ms)))
    found.sort()
    if found:
        print('  DERIVED IDENTITIES between pool terms (smallest first):')
        for _, a, b, k in found[:8]:
            print('    %s  =  %s      (class size %d)' % (show(a), show(b), k))
    else:
        big = sorted(((len(ms), r) for r, ms in cls.items()), reverse=True)[:3]
        print('  no two POOL terms merged.  largest classes: %s' % [k for k, _ in big])
        for k, r in big:
            if k < 2:
                continue
            ms = sorted(cls[r], key=sz)[:3]
            print('    class of size %d: %s' % (k, [show(t)[:44] for t in ms]))
    return found


def show_pat(p):
    return p if isinstance(p, str) else '(%s*%s)' % (show_pat(p[0]), show_pat(p[1]))


if __name__ == '__main__':
    eq = int(sys.argv[1])
    ps = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    gn = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    mz = int(sys.argv[4]) if len(sys.argv) > 4 else 40
    run(eq, ps, gn, mz)
