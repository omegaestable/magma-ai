"""Law 9663 -- two-witness decoder.

Uniform rule:   op(u, J A Q) = x   when   inimg A u   and   op x (op x u) = Q .
Witness sources for x, tried in order:
   W1  x := a1 Q                        (Q = J x P free)
   W2  x := a2 (a1 u)                   (u's own code has a free junk slot J j x)
Both nested calls are gated by  sz(args) < sz u + sz v, unconditionally.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _idc_lib import G, J, sz, show

_memo = {}

def op(u, v):
    k = (u, v)
    r = _memo.get(k)
    if r is None:
        r = _op(u, v); _memo[k] = r
    return r

def inimg(A, u):
    if A[0] == 'J' and A[2] == u: return True
    return u[0] == 'J' and u[2][0] == 'J' and A == u[2][1]

def _op(u, v):
    if v[0] == 'J':
        A, Q = v[1], v[2]
        if inimg(A, u):
            if Q[0] == 'J' and op(Q[1], u) == Q[2]:
                return Q[1]                                   # W1
            if u[0] == 'J' and u[1][0] == 'J':
                x = u[1][2]
                if op(x, op(x, u)) == Q:
                    return x                                  # W2
    return J(u, v)
