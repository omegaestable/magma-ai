"""Constructed control for the reconstruction candidate R(T) below the root.

The current Lean `find` scans a1(T) and then a2(a2(T)); it never scans
R(T) = J(a1(T), T).  This family makes the intended payload exactly R(T) at
depth one, while every relation used to build the family is forced by a free
or U/V0 cell.
"""
from _x17286_leanmirror import Mod, g, J, show


M = Mod()
a, k, h, q, r = (g(i) for i in range(5))
S = J(a, k)
T = J(k, S)
x = J(k, T)                       # R(T) = C(k,S)
w = J(h, J(h, J(T, h)))           # encB(T,h), so op(x,w)=T by U
P = J(w, J(w, T))                 # cds(x,P)
z = J(q, J(q, J(P, q)))           # encB(P,q), so op(x,z)=P by V0
y = J(r, a)                        # op(y,x)=a by U

A = M.op(y, x)
P0 = M.op(x, z)
Q = M.op(z, P0)
B = M.op(z, Q)
top = M.op(A, B)

print("A_is_a", A == a)
print("inner_U", M.op(x, w) == T)
print("cds_x_P", M.Cd(P) and M.op(x, w) == T)
print("P_chain", P0 == P)
print("F1", Q == J(z, P0))
print("F2", B == J(z, Q))
print("top_is_x", top == x)
print("top_tag", M.fired.get("V", 0), M.fired)
print("x", show(x, 10000))
print("top", show(top, 10000))
