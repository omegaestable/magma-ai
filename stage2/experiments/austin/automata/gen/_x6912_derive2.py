"""Mechanically verify the two consequences of law 6912   x = y*(y*((z*z)*(x*y))) :

  (I)   a*a = (a*a)*(a*a)                     -- every square is idempotent      [gen/_x6912_derive.py]
  (II)  (a*a) = (b*b)   for all a,b           -- ALL squares are equal

so 6912 implies:  there is a constant e with  a*a = e for every a,  e*e = e,  and the law reduces to
      x = y * (y * (e * (x*y))).

Every step is an INSTANCE of the law (checked by substitution) or a REWRITE by an already derived
equation (checked by locating the subterm).  Terms are over two free generators a, b.
"""
import sys
sys.setrecursionlimit(10000)

def J(a, b): return ('J', a, b)
A = ('g', 0); B = ('g', 1)

def show(t):
    return ('a' if t[1] == 0 else 'b') if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))

def rhs(x, y, z): return J(y, J(y, J(J(z, z), J(x, y))))

def subst(t, old, new):
    if t == old: return new
    if t[0] == 'g': return t
    return J(subst(t[1], old, new), subst(t[2], old, new))

def occurs(t, sub):
    if t == sub: return True
    if t[0] == 'g': return False
    return occurs(t[1], sub) or occurs(t[2], sub)

eqs = []          # derived equations (l, r) meaning l = r
def law_inst(x, y, z, name):
    e = (x, rhs(x, y, z))
    eqs.append((name, e)); return e
def rw(eq, old, new, name):
    """rewrite the right-hand side of `eq` by replacing the subterm `old` with `new`"""
    l, r = eq
    assert occurs(r, old), 'subterm %s not in %s' % (show(old), show(r))
    e = (l, subst(r, old, new))
    eqs.append((name, e)); return e

u = J(A, A)                       # a*a
v = J(u, u)
S = J(v, v)

# ---- (I) square idempotence, as in _x6912_derive.py
F1 = law_inst(u, u, u, 'F1  x=u,y=u,z=u')                 # u = u*(u*(v*v)) = u*(u*S)
assert F1[1] == J(u, J(u, S))
F2 = rw(law_inst(u, S, A, 'F2a x=u,y=S,z=a'), F1[1], F1[0], 'F2  rewrite by F1')
assert F2[1] == J(S, J(S, u)), show(F2[1])
F3 = rw(law_inst(S, u, v, 'F3a x=S,y=u,z=v'), F2[1], F2[0], 'F3  rewrite by F2')
assert F3[1] == J(u, v), show(F3[1])                       # S = u*v
F4 = rw(law_inst(u, v, A, 'F4a x=u,y=v,z=a'), J(u, v), S, 'F4  rewrite u*v = S (F3)')
F5 = law_inst(v, v, A, 'F5  x=v,y=v,z=a')
assert F4[1] == F5[1]
IDEM = (u, v)                     # a*a = (a*a)*(a*a)   i.e.  u = u*u
print('(I)  %s = %s' % (show(IDEM[0]), show(IDEM[1])))

# ---- (II) all squares are equal.   w = b*b is a square, so w = w*w by (I) applied at b.
w = J(B, B); ww = J(w, w)
IDEMB = (w, ww)                   # b*b = (b*b)*(b*b), the same derivation with a := b

# (*)  u = u * (u * (w * u))          [law x=u,y=u,z=b, then u*u -> u by (I)]
G1 = law_inst(u, u, B, 'G1a x=u,y=u,z=b')        # u = u*(u*((b*b)*(u*u)))
assert G1[1] == J(u, J(u, J(w, v)))
G1 = rw(G1, v, u, 'G1  rewrite (a*a)*(a*a) = a*a')   # v -> u
assert G1[1] == J(u, J(u, J(w, u))), show(G1[1])

# (**) w = u * (u * (u * (w*u)))      [law x=w,y=u,z=a]
G2 = law_inst(w, u, A, 'G2  x=w,y=u,z=a')        # w = u*(u*((a*a)*(w*u))) = u*(u*(u*(w*u)))
assert G2[1] == J(u, J(u, J(u, J(w, u)))), show(G2[1])

# the inner bracket of G2 is exactly G1's right-hand side, which is u
inner = J(u, J(u, J(w, u)))
assert G2[1] == J(u, inner)
G3 = rw(G2, G1[1], G1[0], 'G3  rewrite by G1')        # w = u * u
assert G3[1] == v, show(G3[1])
G4 = rw(G3, v, u, 'G4  rewrite (a*a)*(a*a) = a*a')
assert G4 == (w, u), (show(G4[0]), show(G4[1]))
print('(II) %s = %s          (all squares are equal)' % (show(G4[0]), show(G4[1])))

print('\nsteps:')
for name, (l, r) in eqs:
    print('  %-26s %s  =  %s' % (name, show(l), show(r)))
