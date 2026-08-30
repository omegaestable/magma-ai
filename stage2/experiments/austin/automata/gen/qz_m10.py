"""model 10 for 12073:  G n | P a b | C m   (C UNARY).

op is defined by well-founded recursion on  sz u + sz v  :

  pop  : op(u, C m) = c                if mid m = some (u, c)
  push : op(u, P z z) = C u            if u <> P z z and mid u is defined
  free : op(u, v) = P u v

  mid (P w c) = (key w c, c)           -- "P w c is psi_y(c) for y = key w c"
  key w c     = the y with op(y,c) = w -- candidates from each rule of op, VERIFIED by calling op
                  w = P y c            -> y = w.1        (op(y,c) was the free product)
                  c = C m, mid m = (y,_) -> y            (op(y,c) was a pop)
                  w = C y              -> y              (op(y,c) was a push)

Every recursive call is on a pair whose size sum is strictly smaller (the candidates are subterms).
"""
import sys
sys.setrecursionlimit(200000)
EQ = 12073
CT = ('P',)
UN = ('C',)

_op = {}
_mid = {}
_key = {}


def sq(t):
    return t[0] == 'P' and t[1] == t[2]


def mid(m):
    r = _mid.get(m, 0)
    if r != 0:
        return r
    r = None
    if m[0] == 'P':
        k = key(m[1], m[2])
        if k is not None:
            r = (k, m[2])
    _mid[m] = r
    return r


def key(w, c):
    r = _key.get((w, c), 0)
    if r != 0:
        return r
    cands = []
    if w[0] == 'P' and w[2] == c:
        cands.append(w[1])
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
    if r is None and sq(v) and u != v and mid(u) is not None:
        r = ('C', u)
    if r is None:
        r = ('P', u, v)
    _op[(u, v)] = r
    return r
