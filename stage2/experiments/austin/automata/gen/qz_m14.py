"""model 14 for 12073:  G n | P a b | C m s | K m.

Only  op(psi_y(y), S)  is forced to be S-independent (that is the derived identity
((y*y)*y)*(w*w) = y*(y*(z*z)) ); every other push may RECORD the square, which is what keeps
x |-> psi_y(x) injective.

  pop   : op(u, C m s) = c        if mid m = (u, c), c <> u
          op(u, K m)   = u        if mid m = (u, u)
  ident : op(u, P u (P z z)) = K (P (P u u) u)
  push  : op(u, P z z) = C u (P z z)   if u <> P z z, mid u = (p,q), p <> q
          op(u, P z z) = K u           if u <> P z z, mid u = (p,p)
  free  : op(u,v) = P u v

  mid m = the (y,x) with op(op(y,x),x) = m ;  key w c = the y with op(y,c) = w.
"""
import sys
sys.setrecursionlimit(200000)
EQ = 12073
CT = ('P', 'C')
UN = ('K',)

_op, _mid, _key = {}, {}, {}


def sq(t):
    return t[0] == 'P' and t[1] == t[2]


def mid(m):
    r = _mid.get(m, 0)
    if r != 0:
        return r
    r = None
    if m[0] == 'P':
        w, c = m[1], m[2]
        if op(w, c) == m:
            k = key(w, c)
            if k is not None:
                r = (k, c)
    elif m[0] == 'C':
        n, s = m[1], m[2]
        if sq(s) and n != s:
            md = mid(n)
            if md is not None and md[0] != md[1]:
                k = key(n, s)
                if k is not None:
                    r = (k, s)
    elif m[0] == 'K':
        n = m[1]
        cand = None
        if n[0] == 'P' and sq(n[2]) and n[2] != n and op(n[1], n[2]) == n:
            cand = (n[1], n[2])
        elif n[0] == 'C' and sq(n[2]) and op(n[1], n[2]) == n:
            cand = (n[1], n[2])
        if cand is not None:
            md = mid(n)
            if md is not None and md[0] == md[1]:
                r = cand
    _mid[m] = r
    return r


def key(w, c):
    r = _key.get((w, c), 0)
    if r != 0:
        return r
    cands = []

    def add(t):
        if t is not None and t not in cands:
            cands.append(t)
    if w[0] == 'P' and w[2] == c:
        add(w[1])                                   # free
    if c[0] == 'C':
        md = mid(c[1])
        if md is not None:
            add(md[0])                              # pop C
    if c[0] == 'K':
        add(w)                                      # pop K  (op(w, K m) = w)
    if w[0] == 'C':
        add(w[1])                                   # push C
    if w[0] == 'K':
        add(w[1])                                   # push K
        if (w[1][0] == 'P' and w[1][1][0] == 'P' and w[1][1][1] == w[1][1][2]
                and w[1][1][1] == w[1][2]):
            add(w[1][2])                            # ident
    r = None
    for k in cands:
        if op(k, c) == w:
            r = k
            break
    _key[(w, c)] = r
    return r


def op(u, v):
    r = _op.get((u, v))
    if r is not None:
        return r
    r = None
    if v[0] == 'C':
        md = mid(v[1])
        if md is not None and md[1] != u:
            r = md[1]
    elif v[0] == 'K':
        md = mid(v[1])
        if md is not None and md[1] == md[0] and md[0] == u:
            r = u
    if r is None and v[0] == 'P' and v[1] == u and sq(v[2]):
        r = ('K', ('P', ('P', u, u), u))
    if r is None and sq(v) and u != v:
        md = mid(u)
        if md is not None:
            r = ('K', u) if md[0] == md[1] else ('C', u, v)
    if r is None:
        r = ('P', u, v)
    _op[(u, v)] = r
    return r
