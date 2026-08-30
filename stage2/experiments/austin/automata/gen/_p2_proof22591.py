"""PROOF that 22591 derives an identity between two distinct free terms (so it is a Track-C
"identity law" and NO rule set on the free carrier M ::= g i | J u v can model it).

Method: a FORCED-VALUE table.  Start from the free magma (op = J).  Each step is one instance of
the law  x = (y*(y*x)) * ((x*x)*z) ; every side product of the instance is evaluated in the table
(free unless an earlier step already forced it), and the instance then FORCES the value of the
final product.  A step is legal only if every side product it needs is already determined.

The chain builds the square-root tower  I0 = g0,  I(k+1) = the element whose square is I(k),
and ends with two instances that force the same product to I0 and to I3.

usage: python gen/_p2_proof22591.py
"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)

g = lambda n: ('g', n)


def J(a, b):
    return ('J', a, b)


def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))


def sz(t):
    return 1 if t[0] == 'g' else 1 + sz(t[1]) + sz(t[2])


FORCED = {}          # (u,v) -> value forced by an earlier law instance
STEPS = []


def op(u, v):
    """the value of u*v in the partial model: forced if an earlier instance pinned it, else free."""
    return FORCED.get((u, v), J(u, v))


def instance(x, y, z, tag):
    """apply the law at (x,y,z).  Returns the pair it constrains and forces its value to x."""
    P = op(y, x)
    u = op(y, P)
    S = op(x, x)
    v = op(S, z)
    old = FORCED.get((u, v))
    if old is not None and old != x:
        print('  *** CONTRADICTION at %s' % tag)
        print('      pair  u = %s' % show(u))
        print('            v = %s' % show(v))
        print('      already forced to %s  (size %d)' % (show(old), sz(old)))
        print('      now forced to     %s  (size %d)' % (show(x), sz(x)))
        return (u, v), old, x
    FORCED[(u, v)] = x
    STEPS.append((tag, x, y, z, u, v))
    print('  %-34s x=%-22s  forces  op(u,v) = x  with' % (tag, show(x)[:22]))
    print('      u = %s' % (show(u) if sz(u) < 40 else show(u)[:70] + '..'))
    print('      v = %s' % (show(v) if sz(v) < 40 else show(v)[:70] + '..'))
    return (u, v), None, x


print('law 22591:  x = (y*(y*x)) * ((x*x)*z)\n')
I0 = g(0)
T = J(I0, I0)                      # op(I0,I0) is free = J g0 g0
print('STEP 1  build op(I1,I1) = I0,  I1 := (g0*g0)*((g0*g0)*g0)')
# I1 must satisfy op(I1,I1) = I0.  I1 = op(T, op(T,I0)) = J T (J T I0) is in A(I0);
# and op(op(I0,I0), t) = op(T,t) = J T t is in E(I0).  Choose t = J T I0 so E-side = I1 too.
I1 = J(T, J(T, I0))
instance(I0, T, J(T, I0), 'L[x=I0, y=T, z=(T*I0)]')
print('     -> op(I1, I1) = I0   (both factors are I1)\n')

print('STEP 2  build op(I2,I2) = I1,  I2 := g0*(g0*I1)')
I2 = J(I0, J(I0, I1))
instance(I1, I0, J(I0, I1), 'L[x=I1, y=I0, z=(I0*I1)]')
print('     -> op(I2, I2) = I1\n')

print('STEP 3  build op(I3,I3) = I2,  I3 := I1*(I1*I2)')
I3 = J(I1, J(I1, I2))
instance(I2, I1, J(I1, I2), 'L[x=I2, y=I1, z=(I1*I2)]')
print('     -> op(I3, I3) = I2\n')

p = g(3)
Y = J(p, J(p, I2))                 # a decoder for I2 built on a fresh generator
print('STEP 4  Y := g3*(g3*I2).   Force op(I1, (T*g7)) = I0, then op(Y, I0) = I2')
instance(I0, T, J(T, g(7)), 'L[x=I0, y=T, z=(T*g7)]')
print('     -> op(I1, (T*g7)) = I0')
instance(I2, p, J(T, g(7)), 'L[x=I2, y=g3, z=(T*g7)]')
print('     -> op(Y, I0) = I2\n')

print('STEP 5  force op(Y, I3) = I2   (I3 is in E(I2) with z = I1*I2)')
instance(I2, p, J(I1, I2), 'L[x=I2, y=g3, z=(I1*I2)]')
print('     -> op(Y, I3) = I2\n')

print('STEP 6  the two instances that meet')
pair1, clash1, _ = instance(I0, Y, J(T, I0), 'L[x=I0, y=Y, z=(T*I0)]')
pair2, clash2, _ = instance(I3, Y, J(I0, g(7)), 'L[x=I3, y=Y, z=(g0*g7)]')

print('\n=== VERDICT ===')
if clash2 is not None:
    print('  22591 forces   %s  =  %s' % (show(clash2), show(pair2 and I3)))
    print('  i.e.  I0 = I3  in the free magma modulo the law.')
    print('  I0 = %s   (size %d)' % (show(I0), sz(I0)))
    print('  I3 = %s   (size %d)' % (show(I3), sz(I3)))
    print('  These are DISTINCT free terms, so 22591 has no model on the free term algebra.')
elif pair1 == pair2:
    print('  the two instances share the pair but no clash was recorded -- check the table')
else:
    print('  pairs differ:')
    print('   A u=%s' % show(pair1[0])); print('   A v=%s' % show(pair1[1]))
    print('   B u=%s' % show(pair2[0])); print('   B v=%s' % show(pair2[1]))

print('\n--- the forced table (%d entries) ---' % len(FORCED))
for (a, b), r in sorted(FORCED.items(), key=lambda kv: sz(kv[0][0]) + sz(kv[0][1])):
    print('  op(%s, %s) = %s' % (show(a)[:34], show(b)[:34], show(r)[:34]))
