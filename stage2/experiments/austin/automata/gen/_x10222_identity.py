"""10222 is a QUOTIENT law: it derives an identity between two distinct free terms.

Law L (eq 10222, L-form):   x = y * ((x*y) * ((z*y)*y))

Derivation (each step is an instance of L, plus substitution of an already-derived equation;
this script checks every *structural* claim, i.e. that the term L produces really is the term named):

  F1  R_y is injective:  x1*y = x2*y  =>  B(x1,y,z) = B(x2,y,z)  =>  x1 = y*B(x1,y,z) = y*B(x2,y,z) = x2.
  (2) L(a,a,a):  a = a * T          where  T := (a*a)*((a*a)*a)
  (3) L(a,a,b):  a = a * S          where  S := (a*a)*((b*a)*a)
  (4) L(a,T,a):  a = T * ((a*T)*((a*T)*T))  --[(2): a*T = a]-->  a = T * (a*a)
  (5) L(a,S,a):  a = S * ((a*S)*((a*S)*S))  --[(3): a*S = a]-->  a = S * (a*a)
  (6) F1 at y = a*a on (4),(5):  T = S.

  ==>  every magma satisfying 10222 satisfies   (a*a)*((a*a)*a) = (a*a)*((b*a)*a)   for all a,b.

T and S are DISTINCT terms of the free magma (b != a), so the free magma on generators is not a model,
and no rule set over the g/J carrier can be one.  The dual statement, for eq 35836 (= dual of 10222):

       (a*(a*a))*(a*a) = (a*(a*b))*(a*a)

Run: python gen/_x10222_identity.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from freemodel import normalise, catalog
from laws import parse_eq

def show(t):
    return t if isinstance(t, str) else '(%s*%s)' % (show(t[0]), show(t[1]))

def J(a, b): return (a, b)

law = normalise(parse_eq(catalog()[10222]))
LHS, RHS = law
print('law 10222 :', catalog()[10222])
print('normalised:', LHS, '=', show(RHS))

def inst(pat, s):
    if isinstance(pat, str): return s[pat]
    return (inst(pat[0], s), inst(pat[1], s))

def rhs(x, y, z):
    return inst(RHS, {'x': x, 'y': y, 'z': z})

a, b = 'a', 'b'
T = J(J(a, a), J(J(a, a), a))          # (a*a)*((a*a)*a)
S = J(J(a, a), J(J(b, a), a))          # (a*a)*((b*a)*a)

ok = True
# (2)
e2 = rhs(a, a, a)
print('(2) L(a,a,a) RHS =', show(e2), '   expected a*T =', show(J(a, T)))
ok &= (e2 == J(a, T))
# (3)
e3 = rhs(a, a, b)
print('(3) L(a,a,b) RHS =', show(e3), '   expected a*S =', show(J(a, S)))
ok &= (e3 == J(a, S))
# (4) before the rewrite
e4 = rhs(a, T, a)
want4 = J(T, J(J(a, T), J(J(a, T), T)))
print('(4) L(a,T,a) RHS =', show(e4))
print('    expected     =', show(want4), '  -- rewrite a*T -> a gives  T*(a*a)')
ok &= (e4 == want4)
# (5)
e5 = rhs(a, S, a)
want5 = J(S, J(J(a, S), J(J(a, S), S)))
print('(5) L(a,S,a) RHS =', show(e5))
print('    expected     =', show(want5), '  -- rewrite a*S -> a gives  S*(a*a)')
ok &= (e5 == want5)

print()
print('all structural claims check:', ok)
print('DERIVED IDENTITY:  %s  =  %s' % (show(T), show(S)))
print('T == S as free terms?', T == S, '(so the free magma cannot be a model)')

# the dual, for eq 35836
def dual(t):
    return t if isinstance(t, str) else (dual(t[1]), dual(t[0]))
print()
print('dual law 35836 :', catalog()[35836])
print('DUAL IDENTITY  :  %s  =  %s' % (show(dual(T)), show(dual(S))))
