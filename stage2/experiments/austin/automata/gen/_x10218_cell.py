"""10218: force t2 = op z x to decode by rule R5 or R6 (which put z at a2 (a2 x)), not R2's a2 (a1 x).

R5 on (z,x): tg x, tg (a2 x), tg (a1 (a2 x)), z = a2 (a2 x), guard a1 x = op (a2 (a1 (a2 x))) z
             -> result a2 (a1 (a2 x)).
Take x = J (J E z) (J (J D E) z):  a1 x = J E z, a1 (a2 x) = J D E, a2 (a2 x) = z,
a2 (a1 (a2 x)) = E, guard  J E z = op E z  (true when op E z is free).  So t2 = E.
Also try the R1-encoding of 10218:  enc(x,y,z) = J (J x y) (J (J z x) y),  op y (enc x y z) = x.
"""
import sys, os, itertools, collections, importlib.util
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'gen'))
import closedform as cf
from freemodel import normalise, catalog, size
from laws import parse_eq
EQ = 10218
law = normalise(parse_eq(catalog()[EQ]))
spec = importlib.util.spec_from_file_location('chk', os.path.join(HERE, 'gen', 'rep10218', 'chk10218.py'))
src = open(spec.origin, encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {'__name__': 'chk'}; exec(compile(src, spec.origin, 'exec'), ns); rules = ns['rules']
C = cf.Closed(law, rules)
def J(a, b): return ('J', a, b)
def g(n): return ('g', n)
def enc(x, y, z): return J(J(x, y), J(J(z, x), y))
def show(t): return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))
tab = collections.Counter(); bad = []; n = 0
def run(x, y, z, tagset):
    global n
    try:
        t1 = C.op(x, y); t2 = C.op(z, x); t3 = C.op(t2, y); t4 = C.op(t1, t3); t5 = C.op(y, t4)
    except RecursionError:
        return
    n += 1
    m = (tagset, 'F' if t1 == J(x, y) else 'D', 'F' if t2 == J(z, x) else 'D',
         'F' if t3 == J(t2, y) else 'D', 'F' if t4 == J(t1, t3) else 'D',
         'F' if t5 == J(y, t4) else 'D')
    tab[m] += 1
    if t5 != x: bad.append(((x, y, z), m, t5))
pool = [g(0), g(1), g(2), J(g(0), g(1)), J(g(1), g(2)), J(J(g(0), g(1)), g(2)), enc(g(0), g(1), g(2))]
# A. t2 decoded via R5:  x = J (J E z) (J (J D E) z)
for E, D, z, y in itertools.product(pool, repeat=4):
    x = J(J(E, z), J(J(D, E), z))
    run(x, y, z, 'R5-t2')
# B. t2 decoded via R2's own shape (z at a2 (a1 x)) -- the covered case, as a control
for A, z, y, w in itertools.product(pool, repeat=4):
    x = enc(A, z, w)          # op z x = A  by R1  (z is x's y-role)
    run(x, y, z, 'R1-t2')
# C. t1 decoded (x recovered from y)
for A, w, z in itertools.product(pool, repeat=3):
    y = enc(A, w, z)
    run(A, y, z, 'R1-t1'); run(w, y, z, 'R1-t1')
# D. t3 decoded
for A, w, z, x in itertools.product(pool[:5], repeat=4):
    y = enc(A, w, z)
    run(x, y, w, 'R1-t3')
print('assignments', n)
for k, c in sorted(tab.items(), key=lambda kv: -kv[1])[:14]:
    print('  %-34s %d' % (str(k), c))
print('LAW FAILURES', len(bad))
for (x, y, z), m, r in bad[:4]:
    print('  ', m); print('    x =', show(x)[:200]); print('    y =', show(y)[:200])
    print('    z =', show(z)[:200]); print('    got =', show(r)[:200])
