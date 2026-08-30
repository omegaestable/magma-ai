"""model 16 for 12073 -- the Lean-shaped one.  Carrier  M = G n | P a b | C m s | K m.

`op` is ONE well-founded recursion on  sz u + sz v  (every recursive call is on a pair of proper
subterms of v), five ordered cases:

  Kc m   := m = P (P c c) c  or  m = C (P s s) s          -- "m = psi_y(y) for its own payload"
  inv m  := (w, x)  -- x is the payload of m as a psi-value, and u is a key of m iff op u x = w
            m = P w c , op w c = m           -> (w, c)
            m = C n s , sq s, n <> s, ~Kc n  -> (n, s)
            m = K n   , Kc n, sq n.2         -> (n, n.2)

  R1 pop  : op u (C m s) = x     if ~Kc m, inv m = (w,x), op u x = w
  R2 popK : op u (K m)   = x     if  Kc m, inv m = (w,x), op u x = w
  R3 ident: op u (C u (P z z)) = K (if sq u then C (P u u) u else P (P u u) u)
  R4 push : op u (P z z) = (K u if Kc u else C u (P z z))          when u <> P z z
  R5 free : op u v = P u v
"""
import sys
sys.setrecursionlimit(200000)
EQ = 12073
CT = ('P', 'C')
UN = ('K',)

_op = {}


def sq(t):
    return t[0] == 'P' and t[1] == t[2]


def Kc(m):
    if m[0] == 'P':
        return m[1][0] == 'P' and m[1][1] == m[1][2] and m[1][1] == m[2]
    if m[0] == 'C':
        return m[1][0] == 'P' and m[1][1] == m[1][2] and m[1][1] == m[2]
    return False


def inv(m):
    if m[0] == 'P':
        return (m[1], m[2]) if op(m[1], m[2]) == m else None
    if m[0] == 'C':
        return (m[1], m[2]) if (sq(m[2]) and m[1] != m[2] and not Kc(m[1])) else None
    if m[0] == 'K':
        return (m[1], m[1][2]) if (Kc(m[1]) and sq(m[1][2])) else None
    return None


def op(u, v):
    r = _op.get((u, v))
    if r is not None:
        return r
    r = None
    if v[0] == 'C' and not Kc(v[1]):
        iv = inv(v[1])
        if iv is not None and op(u, iv[1]) == iv[0]:
            r = iv[1]
    elif v[0] == 'K' and Kc(v[1]):
        iv = inv(v[1])
        if iv is not None and op(u, iv[1]) == iv[0]:
            r = iv[1]
    if r is None and v[0] == 'C' and v[1] == u and sq(v[2]):
        r = ('K', ('C', ('P', u, u), u) if sq(u) else ('P', ('P', u, u), u))
    if r is None and sq(v) and u != v:
        r = ('K', u) if Kc(u) else ('C', u, v)
    if r is None:
        r = ('P', u, v)
    _op[(u, v)] = r
    return r
