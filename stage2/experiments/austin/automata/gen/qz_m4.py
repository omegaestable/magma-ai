"""model 4 for 12073: constructors G n | P a b | C a b | Q a  (Q unary = the 'square' tag).

op(z,z) = Q z always, so 'is a square' is a structural test.
Chain:  op(y,x)=P y x ; op(P y x,x)=C x y ; op(C x y, Q z)=C x y ; op(y, C x y)=x.
"""
EQ = 12073
CT = ('P', 'C')
UN = ('Q',)


def keys(u):
    ks = [u, ('Q', u)]
    if u[0] == 'P':
        ks.append(('C', u[2], u[1]))
    return ks


def op(u, v):
    if u == v:                                   # R0 square tag
        return ('Q', u)
    if v[0] == 'C' and v[2] in keys(u):          # R1 decode
        return v[1]
    if u[0] == 'C' and v[0] == 'Q':              # R2 absorb on a square
        return u
    if u[0] == 'P':                              # R3 encode
        return ('C', u[2], u[1])
    return ('P', u, v)
