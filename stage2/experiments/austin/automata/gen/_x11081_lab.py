"""Carrier lab for law 11081:  x = y * ((x * (y*x)) * (z*y))
chain:  A = y*x ;  B = x*A ;  C = z*y ;  D = B*C ;  R = y*D = x

Carrier  M ::= g n | J a b | E a b ,  tg = 1/2/3, a1/a2 total (identity on g), sz as in Lean.
The free product is the TAGGED node `E u v`, which is what makes the C-condition of the root
EXACT -- `a2 v` is a product with right argument u iff `tg (a2 v) = 3 and a2 (a2 v) = u`.
That is the conjunct w123's K2a/K2b could not state, and it is what stores the key at a FIXED path.

usage: python gen/_x11081_lab.py <version> [what]
"""
import sys, itertools, random, collections

G, JJ, EE = 'g', 'J', 'E'
g = lambda n: (G, n)
J = lambda a, b: (JJ, a, b)
E = lambda a, b: (EE, a, b)
tg = lambda t: 1 if t[0] == G else (2 if t[0] == JJ else 3)
a1 = lambda t: t[1] if t[0] != G else t
a2 = lambda t: t[2] if t[0] != G else t


def sz(t):
    return 1 if t[0] == G else sz(t[1]) + sz(t[2]) + 1


def show(t):
    return 'g%d' % t[1] if t[0] == G else '%s(%s,%s)' % (t[0], show(t[1]), show(t[2]))


class Model:
    """version v1:
         R1 (free C):   tg v=3, tg(a1 v)=3, a2(a1 v) = op u (a1(a1 v)), tg(a2 v)!=1, a2(a2 v) = u
         R2 (dec  C):   tg v=3, tg(a1 v)=3, a2(a1 v) = op u (a1(a1 v)), a2 v = op (a2(a2 u)) u
         else           E u v
    """
    def __init__(self, ver='v1', depth=400):
        self.ver = ver
        self.memo = {}
        self.inprog = set()
        self.depth = depth
        self.fired = collections.Counter()

    def op(self, u, v, d=0):
        k = (u, v)
        if k in self.memo:
            return self.memo[k]
        if k in self.inprog or d > self.depth:
            return E(u, v)
        self.inprog.add(k)
        r = self._op(u, v, d)
        self.inprog.discard(k)
        self.memo[k] = r
        return r

    def _op(self, u, v, d):
        b = self.branch(u, v, d)
        if b == 1 or b == 2:
            self.fired[b] += 1
            return a1(a1(v))
        return E(u, v)

    def core(self, u, v, d):
        return (tg(v) != 1 and tg(a1(v)) != 1
                and a2(a1(v)) == self.op(u, a1(a1(v)), d + 1))

    def Fslot(self, u, v):
        """v's A-slot is literally the free product E u (a1 (a1 v)) -- this is what STORES the key:
        if the rule fires at (z,y) then a1 (a2 (a1 y)) = z, a fixed path."""
        w = a2(a1(v))
        return tg(w) == 3 and a1(w) == u and a2(w) == a1(a1(v))

    def key(self, v, d=0):
        """the key that decodes v, extracted RECURSIVELY (rail: the decoder must recurse).
        A-slot free  -> the key is a1 (a2 (a1 v)) ;  A-slot decoded -> descend into a1 (a1 v)."""
        for _ in range(60):
            if tg(v) == 1 or tg(a1(v)) == 1:
                return v
            w = a2(a1(v))
            if tg(w) == 3 and a2(w) == a1(a1(v)):
                return a1(w)
            v = a1(a1(v))
        return v

    def R1dec(self, u, d):
        """u is R1-decodable, UNFOLDED: both recursive arguments are proper subterms of u,
        so the Lean gate sz(a2(a2 u)) + sz(a1(a1 u)) < sz u + sz v is UNCONDITIONAL (rail 3)."""
        return (tg(u) != 1 and tg(a1(u)) != 1 and tg(a2(u)) == 3
                and a2(a1(u)) == self.op(a2(a2(u)), a1(a1(u)), d + 1))

    def Kdec(self, u, d):
        """u decodes with the RECURSIVELY EXTRACTED key, unfolded the same way."""
        if tg(u) == 1 or tg(a1(u)) == 1:
            return False
        return a2(a1(u)) == self.op(self.key(u), a1(a1(u)), d + 1)

    def branch(self, u, v, d=0):
        if not self.core(u, v, d):
            return 0
        if tg(a2(v)) == 3 and a2(a2(v)) == u:
            return 1
        if self.ver == 'v1':
            if a2(v) == self.op(a2(a2(u)), u, d + 1):
                return 2
            return 0
        # v2 / v3: R2 and R3 additionally require Fslot, which stores their own key
        if self.ver in ('v4', 'v5'):
            if a2(v) != a1(a1(u)):
                return 0
            if self.R1dec(u, d):
                return 2
            if self.ver == 'v5' and self.Kdec(u, d):
                return 3
            return 0
        if self.ver in ('v2', 'v3') and self.Fslot(u, v):
            if a2(v) == self.op(a2(a2(u)), u, d + 1):
                return 2
            if a2(v) == self.op(a1(a2(a1(u))), u, d + 1):
                return 3
        return 0


def chain(M, x, y, z):
    A = M.op(y, x); B = M.op(x, A); C = M.op(z, y); D = M.op(B, C); R = M.op(y, D)
    return A, B, C, D, R


def prof(M, x, y, z):
    A = M.op(y, x); B = M.op(x, A); C = M.op(z, y); D = M.op(B, C)
    return (M.branch(y, x), M.branch(x, A), M.branch(z, y), M.branch(B, C), M.branch(y, D))


def terms(maxsz, gens):
    """every term of size <= maxsz over `gens` generators, with BOTH constructors"""
    by = {1: [g(i) for i in range(gens)]}
    for s in range(2, maxsz + 1):
        out = []
        for i in range(1, s):
            for a in by.get(i, []):
                for b in by.get(s - 1 - i, []):
                    out.append(J(a, b)); out.append(E(a, b))
        by[s] = out
    return [t for s in sorted(by) for t in by[s]]


def run(ver, what):
    print('=== model', ver, '===')
    tot = 0; fails = []
    profs = collections.Counter()

    def test(x, y, z, tag):
        nonlocal tot
        M = Model(ver)
        try:
            A, B, C, D, R = chain(M, x, y, z)
        except RecursionError:
            return
        tot += 1
        profs[prof(M, x, y, z)] += 1
        if R != x:
            fails.append((tag, x, y, z, R))

    if what in ('all', 'L1'):
        T = terms(4, 2)
        print('L1 exhaustive: %d terms' % len(T))
        for x in T:
            for y in T:
                for z in T:
                    test(x, y, z, 'L1')
        print('  after L1: %d chains, %d fails' % (tot, len(fails)), flush=True)
    if what in ('all', 'L2'):
        T5 = terms(5, 2)
        Tsm = terms(3, 2)
        print('L2: %d x %d x %d' % (len(T5), len(Tsm), len(Tsm)))
        for y in T5:
            for x in Tsm:
                for z in Tsm:
                    test(x, y, z, 'L2y')
        for z in T5:
            for x in Tsm:
                for y in Tsm:
                    test(x, y, z, 'L2z')
        print('  after L2: %d chains, %d fails' % (tot, len(fails)), flush=True)
    if what in ('all', 'L3'):
        # constructed: force each product to decode, with LARGE junk
        random.seed(20260829)
        def rnd(d):
            if d == 0:
                return g(random.randrange(3))
            c = random.choice([J, E, E])
            return c(rnd(d - 1), rnd(d - 1))
        SM = terms(3, 2)
        BIG = [rnd(3) for _ in range(6)] + [rnd(4) for _ in range(4)]
        M0 = Model(ver)
        # enc(p,u,w): the term v with op u v = p by R1:  E (E p (op u p)) (E w u)
        enc = lambda p, u, w: E(E(p, M0.op(u, p)), E(w, u))
        POOL = SM + BIG
        for p in SM[:4]:
            for u in SM[:4]:
                for w in POOL:
                    v = enc(p, u, w)
                    if sz(v) > 300:
                        continue
                    for o in SM[:3] + BIG[:2]:
                        test(o, v, u, 'enc-at-y')     # C = op(u,v) decodes
                        test(v, u, o, 'enc-at-x')
                        test(o, u, v, 'enc-at-z')
        # two-level nesting: y an encoding whose key is itself an encoding
        for p in SM[:3]:
            for u in SM[:3]:
                for w in SM[:2] + BIG[:2]:
                    k = enc(p, u, w)
                    for p2 in SM[:2]:
                        for w2 in SM[:2] + BIG[:1]:
                            v2 = enc(p2, k, w2)
                            if sz(v2) > 400:
                                continue
                            for o in SM[:2]:
                                test(o, v2, k, 'enc2-at-y')
                                test(o, k, v2, 'enc2-at-z')
                                test(v2, k, o, 'enc2-at-x')
        print('  after L3: %d chains, %d fails' % (tot, len(fails)), flush=True)
    print('TOTAL %d chains, %d FAILS' % (tot, len(fails)))
    print('profiles reached (%d):' % len(profs), dict(profs.most_common(12)))
    fails.sort(key=lambda f: sz(f[1]) + sz(f[2]) + sz(f[3]))
    for (tag, x, y, z, R) in fails[:2]:
        M = Model(ver)
        A, B, C, D, Rr = chain(M, x, y, z)
        print('\nFAIL %s  profile %s' % (tag, str(prof(M, x, y, z))))
        print('  x =', show(x)); print('  y =', show(y)); print('  z =', show(z))
        print('  A =', show(A)); print('  B =', show(B)); print('  C =', show(C))
        print('  D =', show(D)); print('  R =', show(R))
    return len(fails)


if __name__ == '__main__':
    run(sys.argv[1] if len(sys.argv) > 1 else 'v1', sys.argv[2] if len(sys.argv) > 2 else 'all')
