"""model 20 for 12073  --  THE derived-identity model.

THEOREM (derived from 12073 by hand, checked below by exhaustive test):
  12073  =>  a*a = e  for a single constant e (all squares are equal and idempotent),
  so the law is equivalent to  a*a = e  together with the 2-variable law
      x = y * ((((y*x)*x)) * e).

Carrier  M = E | g n | P a b | C m   (C UNARY, E the unique square).

  op u u        = E                                          (a*a = e)
  op u (C m)    = x            if mid m = (w,x) and op u x = w        [pop]
  op u (C u)    = C (P E u)                                           [ident:  y*(y*e) = E_y]
  op u E        = C u                                                 [push:  m*e = code m]
  op u v        = P u v                                               [free]

  mid m  = (w, x)  --  m = psi_y(x) = op (op y x) x , key u iff op u x = w
    m = P w c , op w c = m  -> (w, c)
    m = C n   , n <> E      -> (n, E)
    m = E                   -> (E, E)
"""
import sys
sys.setrecursionlimit(200000)
EQ = 12073
CT = ('P',)
UN = ('C',)
E = ('E',)
CONST = (E,)

_op = {}


def mid(m):
    if m[0] == 'P':
        return (m[1], m[2]) if op(m[1], m[2]) == m else None
    if m[0] == 'C':
        return (m[1], E) if m[1] != E else None
    if False:
        return (E, E)
    return None


def op(u, v):
    r = _op.get((u, v))
    if r is not None:
        return r
    r = None
    if u == v:
        r = E
    if r is None and v[0] == 'C':
        iv = mid(v[1])
        if iv is not None and op(u, iv[1]) == iv[0]:
            r = iv[1]
    if r is None and v[0] == 'C' and v[1] == u:
        r = ('C', ('P', E, u))
    if r is None and v == E:
        r = ('C', u)
    if r is None:
        r = ('P', u, v)
    _op[(u, v)] = r
    return r
