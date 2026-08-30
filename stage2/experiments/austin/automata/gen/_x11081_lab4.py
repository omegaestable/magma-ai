"""Carrier lab 4 -- the ANCHORED decode.  Base is lab3 v16 (D blocked by the C-condition, the a1-mark
relaxed so the Adec cell is already closed).

The idea: a decode at the C position returns a MARKED node that carries its own right argument,
    alpha:  core and not Cfree   ->   D2 (a1 (a1 v)) v          -- payload AND v, tag 6
so that at the root a2 v = D2 P y has tg != 1 and a2 (a2 v) = y = u, i.e. the EXISTING Cfree reading
fires on an anchored a2 v and returns the bare payload.  The root itself uses
    beta:   core and Cfree       ->   a1 (a1 v)                 -- bare, as the law requires
Ordering beta before alpha.  v19 additionally guards alpha with tg u != 4 (u is not the F-marked B),
which is the only conjunct that separates the C position from the D position.
"""
G, JJ, EE, FF, KK, DD = 'g', 'J', 'E', 'F', 'K', 'D'
g = lambda n: (G, n)
J = lambda a, b: (JJ, a, b)
E = lambda a, b: (EE, a, b)
F = lambda a, b: (FF, a, b)
K = lambda a, b: (KK, a, b)
D2 = lambda a, b: (DD, a, b)
TAG = {G: 1, JJ: 2, EE: 3, FF: 4, KK: 5, DD: 6}
tg = lambda t: TAG[t[0]]
a1 = lambda t: t[1] if t[0] != G else t
a2 = lambda t: t[2] if t[0] != G else t


def sz(t):
    return 1 if t[0] == G else sz(t[1]) + sz(t[2]) + 1


def show(t):
    return 'g%d' % t[1] if t[0] == G else '%s(%s,%s)' % (t[0], show(t[1]), show(t[2]))


class Model:
    def __init__(self, ver='v18', fuel=8000):
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
        b = self.branch(u, v)
        if b == 1:
            r = a1(a1(v))
        elif b == 2:
            r = D2(a1(a1(v)), v)
        elif tg(v) != 1 and a2(v) == u:
            r = F(u, v)
        elif tg(u) == 4:
            r = K(u, v)
        else:
            r = E(u, v)
        self.memo[k] = r
        return r

    def branch(self, u, v):
        if tg(v) == 1 or tg(a1(v)) == 1:
            return 0
        if a2(a1(v)) != self.op(u, a1(a1(v))):
            return 0
        if tg(a2(v)) != 1 and a2(a2(v)) == u:
            return 1                                   # beta: anchored reading, bare payload
        if self.ver in ('v19', 'v20') and tg(u) == 4:
            return 0                                   # alpha blocked at D (u = B is F-marked)
        if self.ver == 'v20' and tg(v) != 1 and a2(v) == u:
            return 0                                   # Q-disjointness: alpha blocked at B (a2 A = x = u)
        return 2                                       # alpha: mark the decode, carry v


def chain(M, x, y, z):
    A = M.op(y, x); B = M.op(x, A); C = M.op(z, y); D = M.op(B, C); R = M.op(y, D)
    return A, B, C, D, R


def prof(M, x, y, z):
    A = M.op(y, x); B = M.op(x, A); C = M.op(z, y); D = M.op(B, C)
    return (M.branch(y, x), M.branch(x, A), M.branch(z, y), M.branch(B, C), M.branch(y, D))


def terms(maxsz, gens, ctors=(J, E, F, K, D2)):
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
