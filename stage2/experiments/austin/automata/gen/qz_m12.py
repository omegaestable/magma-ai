"""model 12 for 12073:  G n | P a b | C m   (C UNARY).

op, mid, key by mutual well-founded recursion (lexicographic on the term-size measure):

  op(u, C m)   = c        if mid m = (u, c)                       [pop]
  op(u, P z z) = C u      if u <> P z z and mid u defined         [push]
  op(u, v)     = P u v    otherwise                               [free]

  mid m   -- the (y,x) with op(op(y,x),x) = m  (psi_y(x) = m)
     m = P w c :  y = key w c,  provided op(w,c) = m              [step 2 was free]
     m = C n   :  n = P a b, sq b, b <> n, op(a,b) = n, mid n defined  -> (a, b)
                                                                  [step 2 was a push]
  key w c -- the y with op(y,c) = w; candidates from each rule, each VERIFIED by calling op.
"""
import sys
sys.setrecursionlimit(200000)
EQ = 12073
CT = ('P',)
UN = ('C',)

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
        n = m[1]
        if n[0] == 'P' and sq(n[2]) and n[2] != n and op(n[1], n[2]) == n and mid(n) is not None:
            r = (n[1], n[2])
    _mid[m] = r
    return r


def key(w, c):
    r = _key.get((w, c), 0)
    if r != 0:
        return r
    cands = []
    if w[0] == 'P' and w[2] == c:
        cands.append(w[1])
    if (w[0] == 'C' and w[1][0] == 'P' and w[1][1][0] == 'P' and c[0] == 'P'
            and c[1] == w[1][1][1] and c[1] == w[1][1][2] and c[1] == w[1][2] and sq(c[2])):
        if w[1][1][1] not in cands:
            cands.append(w[1][1][1])          # op(y, P y (P z z)) = C (P (P y y) y)   [ident]
    if c[0] == 'C':
        md = mid(c[1])
        if md is not None and md[0] not in cands:
            cands.append(md[0])
    if w[0] == 'C' and w[1] not in cands:
        cands.append(w[1])
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
        if md is not None and md[0] == u:
            r = md[1]
    if r is None and v[0] == 'P' and v[1] == u and sq(v[2]):        # ident
        r = ('C', ('P', ('P', u, u), u))
    if r is None and sq(v) and u != v and mid(u) is not None:
        r = ('C', u)
    if r is None:
        r = ('P', u, v)
    _op[(u, v)] = r
    return r
