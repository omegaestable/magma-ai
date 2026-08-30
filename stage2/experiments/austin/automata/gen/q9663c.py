"""Law 9663:  x = y * ((z*y) * (x*(x*y)))  --- decoder with three witness positions.

Uniform rule:  op(u, J A Q) = x   when  inimg A u  and  op x (op x u) = Q.
The witness x is read from one of three positions; each rule states the two-level structure
explicitly so that EVERY nested call has both arguments proper subterms of u or of v, hence the
gate  sz(args) < sz u + sz v  holds UNCONDITIONALLY (the 27859 property).

  W1  x := a1 Q                  Q = J x P,   op x u = P
  W2  x := a2 (a1 u)             u = J (J j x) (J w P1),  op w x = P1,
                                 w = J A2 (J Q P2),  op Q x = P2,  inimg A2 x
  W3  x := a2 (a2 (a2 u))        u = J A1 (J w (J w x)),   (P1 free) ... same second level
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


def _lvl2(u, Q, x):
    """u is the code of w w.r.t. x, and w is the code of Q w.r.t. x."""
    if u[0] != 'J' or u[2][0] != 'J': return False
    w, P1 = u[2][1], u[2][2]
    if op(w, x) != P1: return False
    if w[0] != 'J' or w[2][0] != 'J': return False
    if w[2][1] != Q: return False
    if op(Q, x) != w[2][2]: return False
    return inimg(w[1], x)


def _op(u, v):
    if v[0] == 'J':
        A, Q = v[1], v[2]
        if inimg(A, u):
            if Q[0] == 'J' and op(Q[1], u) == Q[2]:
                return Q[1]                                     # W1
            if u[0] == 'J' and u[1][0] == 'J':
                x = u[1][2]
                if _lvl2(u, Q, x): return x                      # W2
            if u[0] == 'J' and u[2][0] == 'J' and u[2][2][0] == 'J':
                x = u[2][2][2]
                if _lvl2(u, Q, x): return x                      # W3
    return J(u, v)
