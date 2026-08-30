"""model 7 for 12073: G n | P a b | C x k   (C = code carrying payload x and key k).

pop   : op(k, C x k) = x
ident : op(u, P u (P z z)) = C u u          (the derived identity y*(y*(z*z)) = K y)
push  : op(P w c, P z z) = C c (key w c)    where key inverts step 1:
          w = P k c  -> k        (step 1 was free)
          c = C w k  -> k        (step 1 was a pop)
free  : P u v
"""
EQ = 12073
CT = ('P', 'C')
UN = ()


def sq(t):
    return t[0] == 'P' and t[1] == t[2]


def key(w, c):
    if w[0] == 'P' and w[2] == c:
        return w[1]
    if c[0] == 'C' and c[1] == w:
        return c[2]
    return None


def op(u, v):
    if v[0] == 'C' and v[2] == u:                     # pop
        return v[1]
    if v[0] == 'P' and v[1] == u and sq(v[2]):        # ident
        return ('C', u, u)
    if u[0] == 'P' and sq(v):                         # push
        k = key(u[1], u[2])
        if k is not None:
            return ('C', u[2], k)
    return ('P', u, v)
