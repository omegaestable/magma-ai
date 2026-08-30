"""model 6 for 12073: constructors G n | P a b | C a b.   op(z,z) = P z z always, so a 'square'
is structurally P w w.  Chain: P y x ; P (P y x) x ; C x y ; x."""
EQ = 12073
CT = ('P', 'C')
UN = ()


def op(u, v):
    if v[0] == 'C' and v[2] == u:                                   # pop
        return v[1]
    if (u[0] == 'P' and u[1][0] == 'P' and u[1][2] == u[2]
            and v[0] == 'P' and v[1] == v[2]):                      # push
        return ('C', u[2], u[1][1])
    return ('P', u, v)
