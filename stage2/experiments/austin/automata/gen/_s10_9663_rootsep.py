# -*- coding: utf-8 -*-
"""Targeted controls for the proved 9663 root separator.

This is deliberately not a random sweep.  It checks the constructed A=y
counterfamily and the older Q-slot counterfamily, including the deletion
control showing that the two independent guards are both necessary.
"""
import _s9_9663_lab5 as L


def d3(t):
    return L.a2(L.a2(L.a2(t)))


def rule(u, v):
    L.PROF.clear()
    L.op(u, v)
    return L.PROF.get((u, v)) or '.'


def profile(x, y, z):
    L.PROF.clear()
    values = L.chain(x, y, z)
    P, Q, A, C, _ = values
    pairs = ((x, y), (x, P), (z, y), (A, Q), (y, C))
    return values, tuple(L.PROF.get(pair) or '.' for pair in pairs)


# `rnv` is the existing lab switch for S(u,v): d3(u) != v.
L.FEAT = {'nu', 'v34', 'nur', 'rnv'}

# Exact A=y family from REMAINING_40_PROMPT.md.
g, c, b, d, x = (L.G(i) for i in range(5))
y = L.E(c, g)
V = L.E(g, y)
p = L.E(b, L.F(g, V))
H = L.E(p, y)
z = L.J(d, L.J(p, H))

assert L.op(g, y) == V
assert L.op(y, p) == g
assert L.op(p, y) == H
assert d3(z) == y
assert rule(z, y) != 'R'
(P, Q, A, C, root), pr = profile(x, y, z)
assert A != y
assert L.a1(C) != y
assert d3(y) != C
assert root == x
print('A=y control repaired:', pr, 'root_ok=', root == x,
      'bad_R2_blocked=', rule(z, y) != 'R')

L.FEAT = {'nu', 'v34', 'nur'}
(_, _, A0, _, root0), pr0 = profile(x, y, z)
assert A0 == y
assert rule(z, y) == 'R'
assert root0 != x
print('A=y without S:', pr0, 'root_ok=', root0 == x,
      'bad_R2_fires=', rule(z, y) == 'R')

# Exact old Q-slot family.  S is true here, so only N can block DEC.
L.FEAT = {'nu', 'v34', 'nur', 'rnv'}
xq = L.G(10)
yq = L.F(xq, L.J(xq, xq))
Pq = L.op(xq, yq)
assert L.a1(Pq) == xq
assert d3(xq) != Pq
assert rule(xq, Pq) == 'F'
print('Q-slot with N:', 'S=', d3(xq) != Pq, 'N=', L.a1(Pq) != xq,
      'rule=', rule(xq, Pq))

L.FEAT = {'v34', 'nur', 'rnv'}
assert rule(xq, Pq) == 'D'
print('Q-slot without N:', 'S=', d3(xq) != Pq, 'N=', L.a1(Pq) != xq,
      'rule=', rule(xq, Pq))
