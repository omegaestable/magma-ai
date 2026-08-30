"""model 9 for 12073: G n | P a b | C m   (C UNARY: the code records the whole chain-middle,
so nothing is lost -- that is what makes  x |-> psi_y(x) = op(op(y,x),x)  injective).

push : op(m, P z z) = C m          when m = P w c and key(w,c) is defined   (S-independent: the
                                    derived identity ((y*y)*y)*(w*w) = K y needs exactly this)
pop  : op(u, C (P w c)) = c        when key(w,c) = u
key(w,c) = the y with op(y,c) = w  -- one case per rule of op.
"""
EQ = 12073
CT = ('P',)
UN = ('C',)


def sq(t):
    return t[0] == 'P' and t[1] == t[2]


def key(w, c):
    if w[0] == 'P' and w[2] == c:                       # op(y,c) was the free product
        return w[1]
    if (c[0] == 'C' and c[1][0] == 'P' and c[1][2] == w
            and c[1][1][0] == 'P' and c[1][1][2] == w):  # op(y, C(P (P y w) w)) = w was a pop
        return c[1][1][1]
    if w[0] == 'C' and sq(c):                            # op(y,c) was a push, y = w's payload
        return w[1]
    return None


def op(u, v):
    if v[0] == 'C':                                      # pop
        m = v[1]
        if m[0] == 'P' and key(m[1], m[2]) == u:
            return m[2]
    if u[0] == 'P' and sq(v) and u != v and key(u[1], u[2]) is not None:   # push
        return ('C', u)
    return ('P', u, v)
