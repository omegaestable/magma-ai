"""model 23 for 12073, built on the derived theorem.

THEOREM (hand derivation, see qz_theorem.py for the machine check of each step)
  L : x = y * (((y*x)*x) * (z*z))
  (a) L[x:=y]            : y = y * E(y,z),  E(y,z) := ((y*y)*y) * (z*z)
  (b) L[x:=E(y,z')]      : psi_y(E) = (y*E)*E = y*E = y, so E(y,z') = y * (y * (z*z))
                           -- E is independent of z' and y*(y*S) is independent of S
  (c) y := a*a (a square): with z:=a, E_y = y*(y*y); with z:=y, E_y = y*(y*(y*y)) = y*E_y = y
  (d) so E_y = y and (a) gives y*y = y ; then y*S = E_y = y for every square S
  (e) L[y:=a*a, x:=b*b]  : psi = (y*x)*x = y, so b*b = y*(y*S) = y = a*a
  => ALL SQUARES ARE EQUAL AND IDEMPOTENT.  Write e for the unique square:  a*a = e for all a,
     and the law is equivalent to  a*a = e  &&  x = y * (((y*x)*x) * e).

Carrier  M = E | g n | P a b | C m   (C unary; E is the unique square e).

  D  diagonal : op u u = E
  P2 pop(x=E) : op u (C (C (C u))) = E
  P1 pop      : op u (C (P w c))   = c          if op u c = w
  P3 pop(id)  : op u (C c)         = C (op E c) if op u c = E
  R  push     : op u E             = C u        (u <> E)
  F  free     : op u v             = P u v
"""
import sys
sys.setrecursionlimit(200000)
EQ = 12073
CT = ('P',)
UN = ('C',)
E = ('E',)
CONST = (E,)

_op = {}


def op(u, v):
    r = _op.get((u, v))
    if r is not None:
        return r
    r = None
    if u == v:
        r = E
    if r is None and v[0] == 'C':
        m = v[1]
        if u != E and m[0] == 'C' and m[1] == ('C', u):
            r = E                                            # P2
        elif m[0] == 'P' and op(m[1], m[2]) == m and op(u, m[2]) == m[1]:
            r = m[2]                                         # P1
        elif m != E and op(u, m) == E:
            r = ('C', op(E, m))                              # P3
    if r is None and v == E:
        r = ('C', u)
    if r is None:
        r = ('P', u, v)
    _op[(u, v)] = r
    return r
