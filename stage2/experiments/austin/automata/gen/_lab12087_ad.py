# -*- coding: utf-8 -*-
"""sepfind adapter for law 12087 (_w3_12087_lab_v11).
Law: x = y * (((y*x)*z) * (x*z));  chain N1=y*x, N2=N1*z, N3=x*z, V=N2*N3, root=y*V.
Branches: 'D' decode, 'T' tag/mark, 'F' free."""
import sys
sys.path.insert(0, '.')
sys.setrecursionlimit(100000)
import _w3_12087_lab_v11 as L
op, chain, prof, tg, a1, a2, sz, show, terms = L.op, L.chain, L.prof, L.tg, L.a1, L.a2, L.sz, L.show, L.terms
CTORS = ('J', 'E')
def G(n): return ('g', n)
def pairs(x, y, z):
    N1 = op(y, x); N2 = op(N1, z); N3 = op(x, z); V = op(N2, N3)
    return [(y, x), (N1, z), (x, z), (N2, N3), (y, V)]
