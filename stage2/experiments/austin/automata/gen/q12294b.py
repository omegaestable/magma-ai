"""Law 12294:  x = y * (((z*y)*x) * (x*y))   -- ONE rule.

code of x w.r.t. u:  C = J D P,  D = op (op z u) x,  P = op x u.
The witness x sits in the D slot (D = J A x), which is INDEPENDENT of P, so it stays readable even
when P decodes.  Guard is semantic: op x u = P.
  inimg A u := (A = J _ u) or (A = a2 (a1 u))       -- a decode of op(z,u) returns a2 (a1 u)
Gate: op x u with x = a2 (a1 v) a proper subterm of v, so sz x + sz u < sz u + sz v UNCONDITIONALLY.
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

def inimg(A, u):
    if A[0] == 'J' and A[2] == u: return True
    return u[0] == 'J' and u[1][0] == 'J' and A == u[1][2]

def _op(u, v):
    if v[0] == 'J':
        D, P = v[1], v[2]
        if D[0] == 'J' and inimg(D[1], u) and op(D[2], u) == P:
            return D[2]
    return J(u, v)
