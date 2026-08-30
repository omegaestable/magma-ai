"""Is the 22591 repair hierarchy CONSISTENT?  Check whether two instances of the law force the
same product to two different values, using only FREE evaluation of the side products.

Level-n family (w a generator):
  I0 = w,  I(k+1) = invsq(Ik) = J (op(Ik,Ik)) (J (op(Ik,Ik)) Ik)   with op(I(k+1), I(k+1)) = Ik
The FTT cell forces      op( J p (J p I2), I0 ) = I2         for EVERY p           (*)
and the TTT cell forces  op( J p (J p I2), I1 ) = I3         for the same p        (**)
With p := g3 the two readings of the law meet at the same top pair.

usage: python gen/_p2_conflict.py
"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
_ARGV = list(sys.argv)
sys.argv = [sys.argv[0], '6']
import _p2_q22591 as Q
import freemodel as fm
from freemodel import normalise, catalog
from laws import parse_eq

J = Q.J
g = lambda n: ('g', n)


def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))


def sh(t, k=60):
    s = show(t)
    return s if len(s) <= k else s[:k] + '..'


M = Q.Mod(6)


def invsq(s):
    T = M.op(s, s)
    return J(T, J(T, s))


w = g(0)
I = [w]
for k in range(4):
    I.append(invsq(I[-1]))
print('the tower  I0=w,  I(k+1) = invsq(Ik):')
for k, t in enumerate(I):
    print('  I%d = %-62s  op(I%d,I%d) = %s' % (k, sh(t), k, k, sh(M.op(t, t), 40)))

p = g(3)
Y = J(p, J(p, I[2]))                     # a decoder whose payload is I2
print('\nY = J p (J p I2) = %s' % sh(Y, 70))

# --- reading C : x = I2, y = p, z = J (op(I1,I1)) g7    forces op(Y, I0) = I2 ---------------
zC = J(M.op(I[1], I[1]), g(7))
print('\nreading C   x=I2  y=p  z=%s' % sh(zC, 40))
PC = M.op(p, I[2]); uC = M.op(p, PC); SC = M.op(I[2], I[2]); vC = M.op(SC, zC)
print('   u = op(p, op(p,I2)) = %-60s  (= Y? %s)' % (sh(uC), uC == Y))
print('   S = op(I2,I2) = %s ;  v = op(S,z) = %s' % (sh(SC, 30), sh(vC, 30)))
print('   => the law demands  op(%s, %s) = I2' % ('Y', sh(vC, 20)))

# --- reading A : x = I0, y = Y, z = J (op(I0,I0)) I0 --------------------------------------
zA = J(M.op(I[0], I[0]), I[0])
PA = M.op(Y, I[0]); uA = M.op(Y, PA); SA = M.op(I[0], I[0]); vA = M.op(SA, zA)
print('\nreading A   x=I0  y=Y  z=%s' % sh(zA, 40))
print('   P = op(Y,I0) = %s        [= I2 by reading C]' % sh(PA, 40))
print('   u = op(Y,P)  = %s' % sh(uA))
print('   S = op(I0,I0) = %s ;  v = op(S,z) = %s' % (sh(SA, 30), sh(vA, 40)))
print('   => the law demands  op(u,v) = I0 = %s' % show(I[0]))

# --- reading B : x = I3, y = Y, z = J (op(I1,I1)) g7 --------------------------------------
zB = J(M.op(I[1], I[1]), g(7))
PB = M.op(Y, I[3]); uB = M.op(Y, PB); SB = M.op(I[3], I[3]); vB = M.op(SB, zB)
print('\nreading B   x=I3  y=Y  z=%s' % sh(zB, 40))
print('   P = op(Y,I3) = %s' % sh(PB, 40))
print('   u = op(Y,P)  = %s' % sh(uB))
print('   S = op(I3,I3) = %s ;  v = op(S,z) = %s' % (sh(SB, 30), sh(vB, 40)))
print('   => the law demands  op(u,v) = I3')

print('\n=== VERDICT ===')
print('  u_A == u_B : %s' % (uA == uB))
print('  v_A == v_B : %s' % (vA == vB))
print('  demands    : I0 = %s   vs   I3 = %s' % (sh(I[0], 20), sh(I[3], 40)))
if uA == uB and vA == vB and I[0] != I[3]:
    print('  CONFLICT: the same pair (u,v) is forced to two different values.')
    print('  u = %s' % show(uA))
    print('  v = %s' % show(vA))

# --- and the semantic free model's own opinion --------------------------------------------
cat = catalog()
law = normalise(parse_eq(cat[22591]))
F = fm.Free(law)
try:
    r = F.ev(law[1], {'x': I[0], 'y': Y, 'z': zA})
    print('\nsemantic Free: reading A ->', sh(r, 40), 'want', show(I[0]))
except Exception as e:
    print('\nsemantic Free reading A raised', type(e).__name__, e)
try:
    r = F.ev(law[1], {'x': I[3], 'y': Y, 'z': zB})
    print('semantic Free: reading B ->', sh(r, 40), 'want I3')
except Exception as e:
    print('semantic Free reading B raised', type(e).__name__, e)
print('semantic conflicts recorded:', len(getattr(F, 'conflicts', [])))
