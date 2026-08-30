"""Law 9663:  x = y * ((z*y) * (x*(x*y)))   --- FREE-TERM carrier, ONE decode rule.

There is NO forced identity (gen/_id_query.py: 0 junk-forgetting merges over 689,386 congruence
nodes), so the carrier stays M ::= g n | J u v.  The code of x relative to u is
    C = J A (J x P)     with   P = op(x,u)   and   A in im(R_u).
im(R_u) = { J z u : z }  u  { a1 (a2 u) }: a decode of any product with right argument u returns
u's own payload slot, whatever z was.  So the existential "A = op(z,u) for some z" is decidable by
projection -- that is `inimg` below.

Gate: the nested call is op(x,u) with sz x < sz v, so msr u v = sz u + sz v strictly decreases
UNCONDITIONALLY (the 27859 property, LEMMA_LIBRARY.md sec.4).

python gen/q9663.py [maxsize] [gens]
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _idc_lib import G, J, sz, show, report

LAW_RHS = ('y', (('z', 'y'), ('x', ('x', 'y'))))
_memo = {}


def op(u, v):
    k = (u, v)
    r = _memo.get(k)
    if r is None:
        r = _op(u, v); _memo[k] = r
    return r


def inimg(A, u):
    """A = op(z,u) for some z."""
    if A[0] == 'J' and A[2] == u:
        return True                                        # free reading, z := a1 A
    return u[0] == 'J' and u[2][0] == 'J' and A == u[2][1]  # A = a1 (a2 u), u decoded


def _op(u, v):
    if v[0] == 'J':
        A, Q = v[1], v[2]
        if Q[0] == 'J':
            x, P = Q[1], Q[2]
            if op(x, u) == P and inimg(A, u):
                return x
    return J(u, v)


if __name__ == '__main__':
    ms = int(sys.argv[1]) if len(sys.argv) > 1 else 11
    gens = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    report('q9663 size<=%d gens=%d' % (ms, gens), op, LAW_RHS, ms, gens)
