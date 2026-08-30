"""model 18 for 12073 -- model 16 with the K constructor folded into C (K m := C m m), so the
carrier has only THREE constructors:   M = g Nat | P a b | C a b.

  sq v   := v = P z z
  Kc m   := m = P (P c c) c  or  m = C (P s s) s          ("m = psi_c(c)")
  inv m  := (w, x): x is m's payload as a psi-value, u is a key of m iff op u x = w
            m = P w c            , op w c = m                 -> (w, c)
            m = C n n , Kc n     , sq (a2 n)                  -> (n, a2 n)
            m = C n s , s <> n or ~Kc n, sq s, n <> s, ~Kc n  -> (n, s)

  R1 pop  : op u (C m s) = x    if (Kc m -> s = m), inv m = (w,x), op u x = w
  R2 ident: op u (C u (P z z)) = C q q  where q = (C (P u u) u if sq u else P (P u u) u)
  R3 push : op u (P z z) = (C u u if Kc u else C u (P z z))     when u <> P z z
  R4 free : op u v = P u v
"""
import sys
sys.setrecursionlimit(200000)
EQ = 12073
CT = ('P', 'C')
UN = ()

_op = {}


def sq(t):
    return t[0] == 'P' and t[1] == t[2]


def Kc(m):
    return m[0] in ('P', 'C') and m[1][0] == 'P' and m[1][1] == m[1][2] and m[1][1] == m[2]


def inv(m):
    if m[0] == 'P':
        return (m[1], m[2]) if op(m[1], m[2]) == m else None
    if m[0] == 'C':
        n, s = m[1], m[2]
        if s == n and Kc(n):
            return (n, n[2]) if sq(n[2]) else None
        return (n, s) if (sq(s) and n != s and not Kc(n)) else None
    return None


def op(u, v):
    r = _op.get((u, v))
    if r is not None:
        return r
    r = None
    if v[0] == 'C' and not (Kc(v[1]) and v[2] != v[1]):
        iv = inv(v[1])
        if iv is not None and op(u, iv[1]) == iv[0]:
            r = iv[1]
    if r is None and ((v[0] == 'C' and v[1] == u and (sq(v[2]) or (v[2] == u and Kc(u))))
                      or (v[0] == 'P' and v[1] == u and v[2] == u and sq(u))):
        q = ('C', ('P', u, u), u) if sq(u) else ('P', ('P', u, u), u)
        r = ('C', q, q)
    if r is None and sq(v) and u != v:
        r = ('C', u, u) if Kc(u) else ('C', u, v)
    if r is None:
        r = ('P', u, v)
    _op[(u, v)] = r
    return r
