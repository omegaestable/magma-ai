"""How deep is the all-decoded spine in the w123 counterexample, and where is the key stored?"""
import sys, itertools, pickle
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE); sys.path.insert(0, HERE + '/gen')
import closedform as cf
from freemodel import normalise, catalog, size
from laws import parse_eq
from _v11081_rs import SETS
law = normalise(parse_eq(catalog()[11081]))
rules = SETS[sys.argv[1] if len(sys.argv) > 1 else 'w123']
S = pickle.load(open(HERE + '/gen/_v11081_fail.pkl', 'rb'))
x, y, z = S[0]['x'], S[0]['y'], S[0]['z']
a1 = lambda t: t[1] if t[0] == 'J' else t
a2 = lambda t: t[2] if t[0] == 'J' else t
C = cf.Closed(law, rules)


def br(u, v):
    for i, (conds, xx, tag) in enumerate(C.rules):
        if C.check(conds, u, v) and C.ev(xx, u, v) is not None:
            return i + 1
    return 0


print('THE SPINE: op z <descend a1.a1 from y>')
t = y
for k in range(6):
    b = br(z, t)
    print('  level %d: sz %-3d  op z (.) branch %s  result %s' %
          (k, size(t), b, 'decoded' if b else 'FREE'))
    if b == 0 or t[0] != 'J' or a1(t)[0] != 'J':
        break
    t = a1(a1(t))
print()
print('THE KEY: where does z sit inside y?')
for L in range(1, 8):
    for p in itertools.product('12', repeat=L):
        s = ''.join(p)
        u = y
        ok = True
        for ch in s:
            if u[0] != 'J':
                ok = False; break
            u = u[1] if ch == '1' else u[2]
        if ok and u == z:
            print('  y.%s  (depth %d)   model canonical keys are y.22 (a2 a2) and y.121 (a1 a2 a1)' % (s, L))
print()
print('CK z (a2 y) — which disjunct held at (z,y)?')
print('  K1  a2(a2 y) == z :', a2(a2(y)) == z)
print('  K2a op (a1(a2(a1 z))) z == a2 y :', C.op(a1(a2(a1(z))), z) == a2(y),
      ' [that op decoded:', br(a1(a2(a1(z))), z) != 0, ']')
print('  K2b op (a2(a2 z)) z == a2 y :', C.op(a2(a2(z)), z) == a2(y),
      ' [that op decoded:', br(a2(a2(z)), z) != 0, ']')
