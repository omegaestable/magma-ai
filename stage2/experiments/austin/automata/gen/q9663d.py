"""9663 with W3 only (W2 dropped) -- does dropping the offending rule keep the model correct?"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _idc_lib import G, J, sz, show
import q9663c as C
_memo = {}
def op(u, v):
    k = (u, v)
    r = _memo.get(k)
    if r is None:
        r = _op(u, v); _memo[k] = r
    return r
inimg = C.inimg
def _lvl2(u, Q, x):
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
                return Q[1]
            if u[0] == 'J' and u[2][0] == 'J' and u[2][2][0] == 'J':
                x = u[2][2][2]
                if _lvl2(u, Q, x): return x
    return J(u, v)
