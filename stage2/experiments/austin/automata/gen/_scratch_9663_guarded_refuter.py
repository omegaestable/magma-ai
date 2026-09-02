# -*- coding: utf-8 -*-
"""Exact nested-DEC refuter for the guarded session-10 9663 model.

This is a symbolic positive control, not a sweep.  It reaches the branch that
the proposed chain dichotomy omitted: DEC may certify another DEC output,
rather than a container whose second child is the original first argument.
"""
import _s9_9663_lab5 as L


L.FEAT = {"nu", "v34", "nur", "rnv"}

# All six generators are distinct.
p, h, k, a, b, z = (L.G(i) for i in range(6))
H = L.J(h, k)
K = L.J(H, p)
x = L.E(a, L.F(H, K))
y = L.E(b, L.F(p, H))

# Inner DEC certificate, then the chain's first DEC.
assert L.op(H, p) == K
assert L.op(p, x) == H
assert L.op(x, y) == p

P, Q, A, C, root = L.chain(x, y, z)
assert P == p
assert Q == L.J(x, p)
assert A == L.E(z, y)
assert C == L.E(A, Q)
assert root == L.E(y, C)
assert root != x
assert L.prof(x, y, z) == ("D", ".", "E", "E", "E")

print("guarded 9663 refuted:", L.prof(x, y, z), "root_ok=", root == x)
