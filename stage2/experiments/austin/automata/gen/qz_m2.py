"""model 2 for 12073: constructors G|P|C.  op(P a b, v) = C b a is v-INDEPENDENT (forced: the law
derives ((y*y)*y)*(w*w) = independent of w).  Decode reads the payload out of the code."""
EQ = 12073
CT = ('P', 'C')


def op(u, v):
    # decodes first
    if v[0] == 'C' and v[2] == u:                                     # R1
        return v[1]
    if u[0] == 'P' and v[0] == 'C' and v[2] == ('C', u[2], u[1]):     # R2  (key = kappa u)
        return v[1]
    if v[0] == 'P' and v[1][0] == 'C' and v[1][2] == u:               # R4
        return v[1][1]
    if u[0] == 'P' and v[0] == 'P' and v[1][0] == 'C' and v[1][2] == ('C', u[2], u[1]):  # R5
        return v[1][1]
    if u[0] == 'P':                                                   # R3 encode
        return ('C', u[2], u[1])
    return ('P', u, v)
