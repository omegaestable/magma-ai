"""Carrier lab 2 for 11081 -- the FOURTH CONSTRUCTOR.

M ::= g n | J a b | E a b | F a b     tg = 1/2/3/4 ; a1/a2 total; the mark KEEPS BOTH ARGUMENTS
(12234 rail 1) so a misfire is transparent: a2 is unchanged and the outer rule still reads through.

Which product does F mark?  The only chain product identifiable by the shape of its RIGHT argument:
    B = x * (y*x)          because  a2 (y*x) = x = the left argument of B.
So  Mark u v := tg v != 1 and a2 v = u   ->  F u v ,  every other free product -> E u v.
At the root a1 v = B is F-tagged, and tag+core is a certificate that never mentions a2 v.

versions
  v6  R := core                                 (no C-condition at all)
  v7  R := core and (Cfree or Cdec)
  v8  v7 + F-mark verified by RECOMPUTATION: op (a1 (a1 v)) (a2 (a1 v)) = a1 v
  v9  v6 + recomputation
"""
import sys, collections

G, JJ, EE, FF = 'g', 'J', 'E', 'F'
g = lambda n: (G, n)
J = lambda a, b: (JJ, a, b)
E = lambda a, b: (EE, a, b)
F = lambda a, b: (FF, a, b)
TAG = {G: 1, JJ: 2, EE: 3, FF: 4}
tg = lambda t: TAG[t[0]]
a1 = lambda t: t[1] if t[0] != G else t
a2 = lambda t: t[2] if t[0] != G else t


def sz(t):
    return 1 if t[0] == G else sz(t[1]) + sz(t[2]) + 1


def show(t):
    return 'g%d' % t[1] if t[0] == G else '%s(%s,%s)' % (t[0], show(t[1]), show(t[2]))


class Model:
    def __init__(self, ver='v7', fuel=8000):
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
        r = a1(a1(v)) if self.branch(u, v) else (F(u, v) if self.mark(u, v) else E(u, v))
        self.memo[k] = r
        return r

    def mark(self, u, v):
        return tg(v) != 1 and a2(v) == u

    def core(self, u, v):
        t = 4 if self.ver not in ('v11', 'v12') else 0
        if tg(v) == 1 or (tg(a1(v)) != t if t else tg(a1(v)) == 1):
            return False
        # v10..v12: the decode rule is DISJOINT from the mark (13764's Q-disjointness).
        # At B the pair is (x, A) with a2 A = x = u, so the mark holds and the decode is blocked.
        if self.ver in ('v10', 'v11', 'v12') and self.mark(u, v):
            return False
        return a2(a1(v)) == self.op(u, a1(a1(v)))

    def recomp(self, v):
        return self.op(a1(a1(v)), a2(a1(v))) == a1(v)

    def branch(self, u, v):
        if not self.core(u, v):
            return 0
        if self.ver in ('v8', 'v9') and not self.recomp(v):
            return 0
        if self.ver in ('v6', 'v9', 'v10', 'v11'):
            return 1
        if tg(a2(v)) == 3 and a2(a2(v)) == u:
            return 1
        if a2(v) == a1(a1(u)):
            return 2
        return 0


def chain(M, x, y, z):
    A = M.op(y, x); B = M.op(x, A); C = M.op(z, y); D = M.op(B, C); R = M.op(y, D)
    return A, B, C, D, R


def prof(M, x, y, z):
    A = M.op(y, x); B = M.op(x, A); C = M.op(z, y); D = M.op(B, C)
    return (M.branch(y, x), M.branch(x, A), M.branch(z, y), M.branch(B, C), M.branch(y, D))


def terms(maxsz, gens, ctors=(J, E, F)):
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
