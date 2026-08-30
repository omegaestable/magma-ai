"""law 27859:  x = ((y * (y * x)) * x) * (z * z).   z occurs only as the square z*z, so
op(A(y,x), S) = x must be S-independent -- exactly the shape that kills the free model.
Here the carrier is the plain P-term algebra and op DECODES the A-shape against any square."""
EQ = 27859
CT = ('P',)
UN = ()


def sq(t):
    return t[0] == 'P' and t[1] == t[2]


def A(u):
    # u = P (P y (P y x)) x
    return (u[0] == 'P' and u[1][0] == 'P' and u[1][2][0] == 'P'
            and u[1][1] == u[1][2][1] and u[1][2][2] == u[2])


def op(u, v):
    if sq(v) and A(u):
        return u[2]
    return ('P', u, v)
