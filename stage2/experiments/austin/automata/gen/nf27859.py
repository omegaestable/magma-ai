"""nf27859.py -- normal-form model for law 27859:  x = ((y*(y*x))*x)*(z*z)

Same square-collapse idea as 12073, but here the root product is the one that multiplies by the
square, so `* S` must DECODE rather than tag -- and then no tag constructor is needed at all:
`op u S = J u S` (free) is exactly the encoding step.

  M ::= g n | S | J a b
  op u v =
    R1  u = v                                                       -> S
    D   v = S, u = J (J a b) q, op a q = b, op a b = J a b          -> q
    D2  v = S, u = J p (J c p)                                      -> J c p
    R4  otherwise                                                   -> J u v

Main path: t1 = op y x, t2 = op y t1 = J y t1, t3 = op t2 x = J (J y t1) x, and
op t3 S fires D with a = y, b = t1, q = x; its guards `op y x = t1` and `op y t1 = J y t1` hold by
construction.  D2 is the single overlap: y = x and x itself a D-shaped encoding, where t2 decodes
to x's payload q and the root sees J q x with x = J _ q.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nfcore import S

def J(a, b): return ('J', a, b)

_memo = {}

def op(u, v):
    k = (u, v)
    r = _memo.get(k)
    if r is not None: return r
    r = None
    if u == v:
        r = S                                                            # R1
    elif v == S and u[0] == 'J':
        if u[1][0] == 'J':
            a, b, q = u[1][1], u[1][2], u[2]
            if op(a, q) == b and op(a, b) == J(a, b):
                r = q                                                    # D
        if r is None and u[2][0] == 'J' and u[2][2] == u[1]:
            r = u[2]                                                     # D2
    if r is None:
        r = J(u, v)                                                      # R4
    _memo[k] = r
    return r
USE_E = False
