"""model 15 for 12073:  G n | P a b | C m s | K m.   Keys are a SET (op(y,x) need not be injective
in y, and when two keys share a psi-value they also share the payload, so the pop may fire for all
of them).

  pop   : op(u, C m s) = x   if u in keys(m), mid m = (keys, x), x not in keys
          op(u, K m)   = x   if u in keys(m), mid m = (keys, x), x in keys
  ident : op(u, P u (P z z)) = K (P (P u u) u)
  push  : op(u, P z z) = K u        if u <> P z z, mid u = (ks, p), p in ks   (S-INDEPENDENT: forced)
          op(u, P z z) = C u (P z z) if u <> P z z, mid u = (ks, p), p not in ks
  free  : op(u,v) = P u v
"""
import sys
sys.setrecursionlimit(200000)
EQ = 12073
CT = ('P', 'C')
UN = ('K',)

_op, _mid, _keys = {}, {}, {}


def sq(t):
    return t[0] == 'P' and t[1] == t[2]


def keys(w, c):
    r = _keys.get((w, c))
    if r is not None:
        return r
    cands = []

    def add(t):
        if t not in cands:
            cands.append(t)
    if w[0] == 'P' and w[2] == c:
        add(w[1])                                        # free
    if c[0] in ('C', 'K'):
        md = mid(c[1])
        if md is not None and md[1] == w:
            for k in md[0]:
                add(k)                                   # pop
    if w[0] == 'C':
        add(w[1])                                        # push C
    if w[0] == 'K':
        add(w[1])                                        # push K
        n = w[1]
        if (n[0] == 'P' and n[1][0] == 'P' and n[1][1] == n[1][2] and n[1][1] == n[2]):
            add(n[2])                                    # ident
    r = [k for k in cands if op(k, c) == w]
    _keys[(w, c)] = r
    return r


def mid(m):
    r = _mid.get(m, 0)
    if r != 0:
        return r
    r = None
    if m[0] == 'P':
        w, c = m[1], m[2]
        if op(w, c) == m:
            ks = keys(w, c)
            if ks:
                r = (ks, c)
    elif m[0] == 'C':
        n, s = m[1], m[2]
        if sq(s) and n != s:
            md = mid(n)
            if md is not None and md[1] not in md[0]:
                ks = keys(n, s)
                if ks:
                    r = (ks, s)
    elif m[0] == 'K':
        n = m[1]
        md = mid(n)
        if md is not None and md[1] in md[0]:
            x = None
            if n[0] in ('P', 'C') and sq(n[2]) and n[2] != n:
                x = n[2]
            elif (n[0] == 'K' and n[1][0] == 'P' and n[1][1][0] == 'P'
                  and n[1][1][1] == n[1][1][2] and n[1][1][1] == n[1][2] and sq(n[1][2])):
                x = ('P', n[1][2], n[1][2])
            if x is not None:
                ks = keys(n, x)
                if ks:
                    r = (ks, x)
    _mid[m] = r
    return r


def op(u, v):
    r = _op.get((u, v))
    if r is not None:
        return r
    r = None
    if v[0] == 'C':
        md = mid(v[1])
        if md is not None and u in md[0] and md[1] not in md[0]:
            r = md[1]
    elif v[0] == 'K':
        md = mid(v[1])
        if md is not None and u in md[0] and md[1] in md[0]:
            r = md[1]
    if r is None and v[0] == 'P' and v[1] == u and sq(v[2]):
        r = ('K', ('P', ('P', u, u), u))
    if r is None and sq(v) and u != v:
        md = mid(u)
        if md is not None:
            r = ('K', u) if md[1] in md[0] else ('C', u, v)
    if r is None:
        r = ('P', u, v)
    _op[(u, v)] = r
    return r
