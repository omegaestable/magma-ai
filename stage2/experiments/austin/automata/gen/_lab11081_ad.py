# -*- coding: utf-8 -*-
"""sepfind adapter for law 11081 (_x11081_lab4, default v20).

Law: x = y * ((x*(y*x)) * (z*y))
Chain: A = y*x ; B = x*A ; C = z*y ; D = B*C ; root = y*D  must equal x.
Branch codes from Model.branch: 0 = no reading, 1 = beta (bare payload), 2 = alpha (marked decode).
Set VER via env X11081_VER.
"""
import os, sys
sys.path.insert(0, '.')
sys.setrecursionlimit(100000)
import _x11081_lab4 as L

VER = os.environ.get('X11081_VER', 'v20')
_M = L.Model(VER, fuel=10 ** 9)

tg, a1, a2, sz, show = L.tg, L.a1, L.a2, L.sz, L.show
G = L.g
CTORS = ('J', 'E', 'F', 'K', 'D')


def op(u, v):
    return _M.op(u, v)


def chain(x, y, z):
    return L.chain(_M, x, y, z)


def prof(x, y, z):
    return L.prof(_M, x, y, z)


def pairs(x, y, z):
    A = op(y, x); B = op(x, A); C = op(z, y); D = op(B, C)
    return [(y, x), (x, A), (z, y), (B, C), (y, D)]


def terms(maxsz, gens):
    return L.terms(maxsz, gens)
