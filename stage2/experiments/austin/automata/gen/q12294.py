"""Law 12294:  x = y * (((z*y)*x) * (x*y))   -- free-term carrier, same shape as 9663.

code of x w.r.t. u:  C = J D P   with  D = op (op z u) x   (junk in the z slot)  and  P = op x u.
decode reads x off P = J x u.
inimg A u := (A = J _ u) or (A = a1 (a2 (a2 u)))   -- a decode of op(z,u) returns a1 (a2 v) with v=u
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _idc_lib import G, J, sz, show

LAW = ('y', ((('z', 'y'), 'x'), ('x', 'y')))
_memo = {}

def op(u, v):
    k = (u, v)
    r = _memo.get(k)
    if r is None:
        r = _op(u, v); _memo[k] = r
    return r

def decoded_val(u):
    """the value a decode of op(?,u) returns: x = a2 (a1 u)  (the D slot is J A x)."""
    if u[0] == 'J' and u[1][0] == 'J':
        return u[1][2]
    return None

def inimg(A, u):
    if A[0] == 'J' and A[2] == u: return True
    return decoded_val(u) == A

def lvl2(u, x, w):
    """u is the code of w w.r.t. x: u = J (J A1 w) (J w x), op w x = P1, inimg A1 x."""
    if u[0] != 'J' or u[2][0] != 'J': return False
    D1, P1 = u[1], u[2]
    if P1[1] != w or P1[2] != x: return False
    if op(w, x) != P1: return False
    return D1[0] == 'J' and D1[2] == w and inimg(D1[1], x)


def _op(u, v):
    if v[0] == 'J':
        D, P = v[1], v[2]
        if D[0] == 'J' and inimg(D[1], u):
            x = D[2]
            if P[0] == 'J' and P[1] == x and P[2] == u and op(x, u) == P:
                return x                                        # W1
            if u[0] == 'J' and u[2][0] == 'J' and x == u[2][2] and P == u[2][1]                     and lvl2(u, x, P):
                return x                                        # W2
    return J(u, v)
