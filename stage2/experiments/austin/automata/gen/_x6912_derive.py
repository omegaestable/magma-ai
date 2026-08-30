"""Mechanically verify that law 6912   x = y*(y*((z*z)*(x*y)))   derives

        (a*a) = (a*a)*(a*a)          [every square is idempotent]

Each step is either a literal INSTANCE of the law (checked by substituting into the pattern and
comparing terms) or a REWRITE of one subterm by an equation already derived (checked by locating
the subterm and replacing it).  Nothing else is used.
"""
import sys
sys.setrecursionlimit(10000)

def J(a, b): return ('J', a, b)
A = ('g', 0)

def show(t):
    return 'a' if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))

# law 6912 pattern:  x = y * (y * ((z*z) * (x*y)))
def rhs(x, y, z):
    return J(y, J(y, J(J(z, z), J(x, y))))

def instance(x, y, z):
    """the equation (x , rhs) which the law asserts"""
    return (x, rhs(x, y, z))

def subst(t, old, new):
    """replace every occurrence of `old` in `t` by `new` (rewriting by a derived equation)"""
    if t == old: return new
    if t[0] == 'g': return t
    return J(subst(t[1], old, new), subst(t[2], old, new))

def occurs(t, sub):
    if t == sub: return True
    if t[0] == 'g': return False
    return occurs(t[1], sub) or occurs(t[2], sub)

u = J(A, A)          # a*a
v = J(u, u)          # (a*a)*(a*a)
S = J(v, v)

steps = []

# F1: instance x=u, y=u, z=u
l, r = instance(u, u, u)
assert r == J(u, J(u, J(J(u, u), J(u, u))))
assert J(J(u, u), J(u, u)) == S, show(J(J(u,u),J(u,u)))
F1 = (u, J(u, J(u, S)))          # u = u * (u * S)
assert r == F1[1], (show(r), show(F1[1]))
steps.append(('F1  instance x=u,y=u,z=u', F1))

# F2: instance x=u, y=S, z=a, then rewrite the subterm  u*(u*S)  ->  u   using F1
l, r = instance(u, S, A)
assert r == J(S, J(S, J(J(A, A), J(u, S))))
assert J(A, A) == u
r2 = J(S, J(S, J(u, J(u, S))))
assert r == r2, (show(r), show(r2))
assert occurs(r2, F1[1])
F2 = (u, subst(r2, F1[1], F1[0]))      # u = S * (S * u)
assert F2[1] == J(S, J(S, u)), show(F2[1])
steps.append(('F2  instance x=u,y=S,z=a + rewrite by F1', F2))

# F3: instance x=S, y=u, z=v, then rewrite  S*(S*u) -> u  using F2
l, r = instance(S, u, v)
assert r == J(u, J(u, J(J(v, v), J(S, u))))
assert J(v, v) == S
r2 = J(u, J(u, J(S, J(S, u))))
assert r == r2, (show(r), show(r2))
assert occurs(r2, F2[1])
F3 = (S, subst(r2, F2[1], F2[0]))      # S = u * (u * u) = u * v
assert F3[1] == J(u, J(u, u)) == J(u, v), show(F3[1])
steps.append(('F3  instance x=S,y=u,z=v + rewrite by F2', F3))

# F4: instance x=u, y=v, z=a, then rewrite u*v -> S using F3 (F3 read right-to-left: u*v = S)
l, r = instance(u, v, A)
assert r == J(v, J(v, J(J(A, A), J(u, v))))
r2 = J(v, J(v, J(u, J(u, v))))
assert r == r2
assert occurs(r2, J(u, v))
F4 = (u, subst(r2, J(u, v), S))        # u = v * (v * (u * S))
assert F4[1] == J(v, J(v, J(u, S))), show(F4[1])
steps.append(('F4  instance x=u,y=v,z=a + rewrite u*v = S (F3)', F4))

# F5: instance x=v, y=v, z=a   (v*v = S literally)
l, r = instance(v, v, A)
assert r == J(v, J(v, J(J(A, A), J(v, v))))
r2 = J(v, J(v, J(u, S)))
assert r == r2, (show(r), show(r2))
F5 = (v, r2)                           # v = v * (v * (u * S))
steps.append(('F5  instance x=v,y=v,z=a', F5))

assert F4[1] == F5[1]
print('DERIVED:  %s  =  %s' % (show(F4[0]), show(F5[0])))
print('     i.e.  a*a = (a*a)*(a*a)   -- every square is idempotent\n')
for name, (a, b) in steps:
    print('  %-46s  %s  =  %s' % (name, show(a), show(b)))
print('\nF4 and F5 share the right-hand side %s, so %s = %s.' % (show(F4[1]), show(F4[0]), show(F5[0])))
