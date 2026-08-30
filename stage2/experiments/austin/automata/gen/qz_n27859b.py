"""law 27859:  x = ((y * (y * x)) * x) * (z * z)   -- inverted-with-verification model.

  pay m  = the x with  op(op(y,op(y,x)),x) = m  for some y
           m = P w c , op w c = m , key2 w c defined  ->  c
  key2 w c = the y with op(y, op(y,c)) = w :  candidate w.1, verified by calling op

  op u (P z z) = pay u        if pay u is defined and u <> P z z
  op u v       = P u v        otherwise
"""
import sys
sys.setrecursionlimit(200000)
EQ = 27859
CT = ('P',)
UN = ()

_op, _pay = {}, {}
GUARD = [0]


def sq(t):
    return t[0] == 'P' and t[1] == t[2]


def szz(t):
    return 1 if t[0] == 'G' else 1 + szz(t[1]) + szz(t[2])


def key2(w, c, bound):
    if w[0] != 'P':
        return None
    y = w[1]
    t = opb(y, c, bound)
    if t is None:
        return None
    r = opb(y, t, bound)
    return y if r == w else None


def pay(m, bound):
    if m[0] == 'P':
        w, c = m[1], m[2]
        if opb(w, c, bound) == m and key2(w, c, bound) is not None:
            return c
    return None


def opb(u, v, bound):
    """op, but only if sz u + sz v < bound (a gate); None = cut."""
    if szz(u) + szz(v) >= bound:
        GUARD[0] += 1
        return None
    return op(u, v)


def op(u, v):
    r = _op.get((u, v))
    if r is not None:
        return r
    r = None
    if sq(v) and u != v:
        p = pay(u, szz(u) + szz(v))
        if p is not None:
            r = p
    if r is None:
        r = ('P', u, v)
    _op[(u, v)] = r
    return r
