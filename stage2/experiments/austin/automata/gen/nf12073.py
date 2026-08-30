"""nf12073.py -- a NORMAL-FORM model for law 12073   x = y * (((y*x)*x) * (z*z))

No quotient type.  The carrier is a plain inductive term type; `op` computes directly into the
normal form of the product, so the identities the law derives ("the value does not depend on which
square z*z is") hold on the nose between distinct constructors rather than up to a congruence.

    M ::= g n | S | E t | J a b            sz(g)=sz(S)=1, sz(E t)=1+sz t, sz(J a b)=1+sz a+sz b

`S` is the normal form of every square (rule R1), `E u` is the normal form of `u * S` (rule R2),
`J u v` is the free/inert product.  The law's right-hand side evaluates to

    op y (op (op (op y x) x) S)  =  op y (E (J (op y x) x))

and the decoder R3 turns that back into `x` with the guard `op u q = p`, which is true *by
definition* of the middle product.  R5..R8 are the completion of the rule system: the finitely many
overlaps where one of the two inner products is itself a redex.

RULES (ordered; `op` returns the first that applies)
  R1  u = v                                                        -> S
  R2  v = S                                                        -> E u
  R5  u != S,  v = E (E (E u))                                     -> S
  R3  v = E (J p q),  q != S,  op u q = p,  op p q = J p q         -> q          (the decoder)
  R7  v = E w,  w != S,  u = E (J p w),  op S w = p                -> u
  R8  v = E u,  u = E (J p q),  q != S,  op S q = p                -> E q
  R6  v = E w,  w != S,  op u w = S,  op S w = J S w               -> E (J S w)
  R4  otherwise                                                    -> J u v

Every recursive call is `op _ t` with `t` a proper subterm of `v`, so `op` is structurally
recursive on its second argument (Lean: `termination_by v` / `decreasing_by` on `sz v`).
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nfcore import S

def E(t): return ('E', t)
def J(a, b): return ('J', a, b)

_memo = {}

def op(u, v):
    k = (u, v)
    r = _memo.get(k)
    if r is not None: return r
    r = None
    if u == v:
        r = S                                                                     # R1
    elif v == S:
        r = E(u)                                                                  # R2
    elif u != S and v[0] == 'E' and v[1][0] == 'E' and v[1][1][0] == 'E' and v[1][1][1] == u:
        r = S                                                                     # R5
    if r is None and v[0] == 'E' and v[1][0] == 'J':
        p, q = v[1][1], v[1][2]
        if q != S and op(u, q) == p and op(p, q) == J(p, q):
            r = q                                                                 # R3
    if r is None and v[0] == 'E' and v[1] != S and u[0] == 'E' and u[1][0] == 'J' \
            and u[1][2] == v[1] and op(S, v[1]) == u[1][1]:
        r = u                                                                     # R7
    if r is None and v[0] == 'E' and v[1] == u and u[0] == 'E' and u[1][0] == 'J' \
            and u[1][2] != S and op(S, u[1][2]) == u[1][1]:
        r = E(u[1][2])                                                            # R8
    if r is None and v[0] == 'E' and v[1] != S and op(u, v[1]) == S and op(S, v[1]) == J(S, v[1]):
        r = E(J(S, v[1]))                                                         # R6
    if r is None:
        r = J(u, v)                                                               # R4
    _memo[k] = r
    return r
