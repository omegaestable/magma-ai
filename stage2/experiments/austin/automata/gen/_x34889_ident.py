"""Law 34889 derives  (g*g)*(g*g) = g*g  -- mechanical check of the 3-step derivation.

Modelled (dual, L-form) law  L :   x = z * ((x * (z * x)) * (y * y))
(34889 itself is  x = ((y*y) * ((x*z)*x)) * z ; the derivation below is stated for the L-form,
and dualises verbatim because the identity  s*s = s  with  s = g*g  is self-dual.)

    c  := g*g
    z1 := c * (c*c)
 (1) L[x:=c, z:=c, y:=g]   is literally   c = c * (z1 * c)
 (2) L[x:=c, z:=z1, y:=g]  is literally   c = z1 * ((c * (z1*c)) * c) ;  rewrite by (1)  ->  c = z1 * (c*c)
 (3) L[x:=c, z:=c, y:=c]   is literally   c = c * (z1 * (c*c))        ;  rewrite by (2)  ->  c = c*c
Every step is a substitution instance of L plus replacement of a subterm by an already-derived equal.
"""
import sys

sys.setrecursionlimit(10000)


def M(a, b):
    return ('*', a, b)


def show(t):
    return t if isinstance(t, str) else '(%s*%s)' % (show(t[1]), show(t[2]))


def subst(t, s):
    if isinstance(t, str):
        return s.get(t, t)
    return ('*', subst(t[1], s), subst(t[2], s))


def rewrite(t, a, b):
    """replace every occurrence of subterm a by b"""
    if t == a:
        return b
    if isinstance(t, str):
        return t
    return ('*', rewrite(t[1], a, b), rewrite(t[2], a, b))


# L :  x = z * ((x * (z*x)) * (y*y))
LHS = 'x'
RHS = M('z', M(M('x', M('z', 'x')), M('y', 'y')))

g = 'g'
c = M(g, g)
z1 = M(c, M(c, c))

# (1)
i1 = subst(RHS, {'x': c, 'z': c, 'y': g})
want1 = M(c, M(z1, c))
assert i1 == want1, (show(i1), show(want1))
print('(1)  %s = %s      [L with x:=c, z:=c, y:=g, literally]' % (show(c), show(i1)))

# (2)
i2 = subst(RHS, {'x': c, 'z': z1, 'y': g})
print('(2)  %s = %s      [L with x:=c, z:=z1, y:=g, literally]' % (show(c), show(i2)))
# the subterm  c*(z1*c)  equals c by (1)
i2r = rewrite(i2, M(c, M(z1, c)), c)
want2 = M(z1, M(c, c))
assert i2r == want2, (show(i2r), show(want2))
print('     rewrite by (1):  %s = %s' % (show(c), show(i2r)))

# (3)
i3 = subst(RHS, {'x': c, 'z': c, 'y': c})
print('(3)  %s = %s      [L with x:=c, z:=c, y:=c, literally]' % (show(c), show(i3)))
i3r = rewrite(i3, M(z1, M(c, c)), c)
want3 = M(c, c)
assert i3r == want3, (show(i3r), show(want3))
print('     rewrite by (2):  %s = %s' % (show(c), show(i3r)))
print()
print('THEOREM  34889 (L-form)  |-  (g*g)*(g*g) = g*g   for every g.')
print('So the free magma is NOT a model: it must be quotiented (squares are idempotent).')
