"""cx40057.py : coincidence check for the 40057 skeleton (rules are for the DUAL L-form law).

1. reproduces the generator's deep test on the L-form law (chk40057.py tests the R-form text unflipped: bogus)
2. evaluates the hand-derived level-2 instance (P2 = op x P1 decoded when P1 = op P0 y is itself decoded)
3. cross-checks the instance against the reference semantic free model (freemodel.Free)
4. structured fuzz (fuzz.fuzz) on the L-form law
"""
import sys, os, random
sys.path.insert(0, 'C:\\Users\\nacho\\Documents\\GitHub\\magma-ai\\stage2\\experiments\\austin\\automata')
import closedform as cf
import freemodel as fm
from freemodel import normalise, catalog, size
from laws import parse_eq, show
from chk40057 import rules

def dual_pat(p):
    return p if isinstance(p, str) else (dual_pat(p[1]), dual_pat(p[0]))

orig = normalise(parse_eq(catalog()[40057]))
law = ('x', dual_pat(orig[1]))
print('R-form law :', orig)
print('L-form law :', law)

C = cf.Closed(law, rules)
N = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
tested, fails = cf.deep_tests(C, law, N, 300, 11)
print('deep tests on L-form law: tested', tested, 'fails', len(fails), 'fired', sorted(C.fired.items()))

def J(a, b): return ('J', a, b)
def g(n): return ('g', n)
def pp(t):
    if t[0] == 'g': return 'g%d' % t[1]
    return '(' + pp(t[1]) + ' ' + pp(t[2]) + ')'

# ---- the hand-derived instance ----
x = g(0); z = g(1)
w = g(2); z2 = g(3); z1 = g(4)
P1 = J(x, J(w, J(J(z2, w), x)))          # op x P1 = w by R1
P0 = J(z, x)                              # op z x free
y = J(P0, J(P1, J(J(z1, P1), P0)))        # op P0 y = P1 by R1
s = {'x': x, 'y': y, 'z': z}
A, B = law[1]
p0 = C.op(z, x); p1 = C.op(p0, y); p2 = C.op(x, p1); p3 = C.op(y, p2); p4 = C.op(y, p3)
print('P0 = op z x      =', pp(p0))
print('P1 = op P0 y     =', pp(p1), '  (expected P1 =', pp(P1), ')', p1 == P1)
print('P2 = op x P1     =', pp(p2), '  (expected w = g2)', p2 == w)
print('P3 = op y P2     =', pp(p3))
print('P4 = op y P3     =', pp(p4), '  law wants x = g0 :', p4 == x)
lhs = C.op(C.evp(A, s), C.evp(B, s))
print('C.evp law value  =', pp(lhs), ' == x ?', lhs == x)
print('instance sizes: x', size(x), 'y', size(y), 'z', size(z))
print('INSTANCE (L-form, x y z):')
print('  x =', pp(x)); print('  y =', pp(y)); print('  z =', pp(z))

# ---- reference semantic free model ----
F = fm.Free(law)
try:
    ref = F.op(F.ev(F.A, s), F.ev(F.B, s))
    print('freemodel.Free law value =', pp(ref), ' == x ?', ref == x, ' conflicts', len(F.conflicts), 'bail', F.bail, 'tainted', F.tainted)
    print('Free: op y P3 =', pp(F.op(y, p3)), ' Free: op x P1 =', pp(F.op(x, p1)))
except Exception as e:
    print('freemodel.Free raised', repr(e))

# ---- structured fuzz ----
try:
    import fuzz as fz
    t2, f2 = fz.fuzz(C, law, rules, int(sys.argv[2]) if len(sys.argv) > 2 else 8000, seed=5)
    print('fuzz: tested', t2, 'fails', len(f2))
    for (ss, r) in f2[:3]:
        print('  fuzz fail: x =', pp(ss['x']), ' y =', pp(ss['y']), ' z =', pp(ss['z']), ' ->', pp(r) if isinstance(r, tuple) else r)
except Exception as e:
    print('fuzz raised', repr(e))
