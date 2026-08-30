"""Carrier lab 3 -- FIVE constructors, one mark per product the law re-reads.

M ::= g n | J a b | E a b | F a b | K a b        tg = 1/2/3/4/5 ; marks keep BOTH arguments.
11081 re-reads TWO products at the root: a1 v = B (to read x) and v itself / a2 v = C (to certify).
  Qb u v := tg v != 1 and a2 v = u      -> F u v      marks B = x * (y*x)   (a2 (y*x) = x = u)
  Qd u v := tg u = 4                    -> K u v      marks D = B * C       (u = B is F-marked)
else E u v.  Root rule can then demand tg v = 5 and tg (a1 v) = 4.

versions
  v13  R := tg v = 5 and tg (a1 v) = 4 and a2 (a1 v) = op u (a1 (a1 v))                       (no C-cond)
  v14  v13 + a2 v != u                        (Q-disjointness)
  v15  v13 + (tg (a2 v) != 1 and a2 (a2 v) = u)   (the exact C-condition)
"""
G, JJ, EE, FF, KK = 'g', 'J', 'E', 'F', 'K'
g = lambda n: (G, n)
J = lambda a, b: (JJ, a, b)
E = lambda a, b: (EE, a, b)
F = lambda a, b: (FF, a, b)
K = lambda a, b: (KK, a, b)
TAG = {G: 1, JJ: 2, EE: 3, FF: 4, KK: 5}
tg = lambda t: TAG[t[0]]
a1 = lambda t: t[1] if t[0] != G else t
a2 = lambda t: t[2] if t[0] != G else t


def sz(t):
    return 1 if t[0] == G else sz(t[1]) + sz(t[2]) + 1


def show(t):
    return 'g%d' % t[1] if t[0] == G else '%s(%s,%s)' % (t[0], show(t[1]), show(t[2]))


class Model:
    def __init__(self, ver='v13', fuel=8000):
        self.ver = ver
        self.memo = {}
        self.fuel = fuel

    def op(self, u, v):
        k = (u, v)
        if k in self.memo:
            return self.memo[k]
        self.fuel -= 1
        if self.fuel <= 0:
            raise RecursionError('fuel')
        if self.branch(u, v):
            r = a1(a1(v))
        elif tg(v) != 1 and a2(v) == u:
            r = F(u, v)          # B's mark FIRST: the guard that distinguishes the position it marks
        elif tg(u) == 4:
            r = K(u, v)          # D's mark: left argument is B, i.e. F-tagged
        else:
            r = E(u, v)
        self.memo[k] = r
        return r

    def branch(self, u, v):
        # v16/v17: the mark on a1 v is relaxed to "is a product" -- when A decoded, B cannot be
        # F-marked (a2 A != x), and that is what killed v15's 60 Adec chains.  D stays blocked by
        # the C-condition, not by the tag.
        if self.ver in ('v16', 'v17'):
            if tg(v) == 1 or tg(a1(v)) == 1:
                return 0
        elif tg(v) != 5 or tg(a1(v)) != 4:
            return 0
        if self.ver == 'v14' and tg(v) != 1 and a2(v) == u:
            return 0
        if a2(a1(v)) != self.op(u, a1(a1(v))):
            return 0
        Cfree = tg(a2(v)) != 1 and a2(a2(v)) == u
        if self.ver in ('v13', 'v14'):
            return 1
        if Cfree:
            return 1
        # v17: the RECOMPUTATION branch -- u's key is stored at a2 (a2 u) by the Cfree branch,
        # so re-run it instead of reading a path out of a2 v.
        if self.ver == 'v17' and a2(v) == a1(a1(u)):
            try:
                return 2 if self.op(a2(a2(u)), u) == a2(v) else 0
            except RecursionError:
                return 0
        return 0


def chain(M, x, y, z):
    A = M.op(y, x); B = M.op(x, A); C = M.op(z, y); D = M.op(B, C); R = M.op(y, D)
    return A, B, C, D, R


def prof(M, x, y, z):
    A = M.op(y, x); B = M.op(x, A); C = M.op(z, y); D = M.op(B, C)
    return (M.branch(y, x), M.branch(x, A), M.branch(z, y), M.branch(B, C), M.branch(y, D))


def terms(maxsz, gens, ctors=(J, E, F, K)):
    by = {1: [g(i) for i in range(gens)]}
    for s in range(2, maxsz + 1):
        out = []
        for i in range(1, s):
            for a in by.get(i, []):
                for b in by.get(s - 1 - i, []):
                    for c in ctors:
                        out.append(c(a, b))
        by[s] = out
    return [t for s in sorted(by) for t in by[s]]
