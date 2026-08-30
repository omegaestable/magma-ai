"""Hand-built cell (F,F,D,F,D): s3 decodes while s1,s2 are free.  Derived, not sampled."""
import sys, os, itertools, collections
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'gen'))
import closedform as cf, leangen
from freemodel import normalise, catalog, size
from laws import parse_eq
import _x40037_rules as R
EQ = 40037
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = ('x', leangen.dual_pat(orig[1]))
idx = [int(i) for i in (sys.argv[1] if len(sys.argv) > 1 else '1,2,14,10').split(',')]
rules = [R.ALL[i - 1] for i in idx]
C = cf.Closed(law, rules)
def J(a, b): return ('J', a, b)
def g(n): return ('g', n)
def show(t): return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))
tab = collections.Counter(); bad = []; n = 0
pool = [g(0), g(1), g(2), g(3), J(g(0), g(1)), J(g(1), J(g(2), g(0)))]
for y, F, Fp, Cp in itertools.product(pool, repeat=4):
    Cc = J(Cp, J(J(Fp, y), Fp))
    x  = J(Cc, J(J(F, y), F))
    z  = Cp
    try:
        s1 = C.op(y, x); s2 = C.op(s1, y); s3 = C.op(z, s2); s4 = C.op(x, s3); s5 = C.op(z, s4)
    except RecursionError:
        continue
    n += 1
    m = ('F' if s1 == J(y, x) else 'D', 'F' if s2 == J(s1, y) else 'D',
         'F' if s3 == J(z, s2) else 'D', 'F' if s4 == J(x, s3) else 'D',
         'F' if s5 == J(z, s4) else 'D')
    tab[m] += 1
    if s5 != x: bad.append(((x, y, z), m))
print('assignments', n)
for k, c in sorted(tab.items(), key=lambda kv: -kv[1]): print('  %-24s %d' % (str(k), c))
print('LAW FAILURES', len(bad))
for (x, y, z), m in bad[:4]:
    print('  ', m); print('    x =', show(x)[:300]); print('    y =', show(y)[:300]); print('    z =', show(z)[:300])
