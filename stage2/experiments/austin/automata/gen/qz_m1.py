"""model 1 for 12073: constructors G|P|D|C, non-recursive structural op."""
EQ = 12073
CT = ('P', 'D', 'C')


def op(u, v):
    if v[0] == 'C' and v[2] == u:          # D1 decode
        return v[1]
    if u[0] == 'D':                        # D3 encode (independent of v)
        return ('C', u[1], u[2])
    if u[0] == 'P' and u[2] == v:          # D2 double
        return ('D', v, u[1])
    return ('P', u, v)
