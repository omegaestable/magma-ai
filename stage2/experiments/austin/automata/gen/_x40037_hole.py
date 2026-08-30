"""Derived cell (F,F,F,D,?) for 40037: s4 = op(x, J z s2) DECODES to z via R3.

Construction (see NOTES_40037.md).  Free parameters x, y, D, F.
  s1 = J y x ; s2 = J s1 y ; W = J x (J (J D s2) D) ; z = J s2 (J W (J (J F s2) F))
R3 on (x, J z s2) needs E3 z (true by construction, with a1(a2 z) = W) and the guard
  s2 = op x (op (op W z) W) = op x (op (a1 z) W) = op x (op s2 W) = op x (J s2 W) = a1 (J s2 W) = s2
where op x (J s2 W) fires R1 because x = a1 W and E3 (J s2 W).
"""
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
pool = [g(0), g(1), g(2), J(g(1), g(2)), J(g(0), J(g(1), g(2)))]
tab = collections.Counter(); bad = []; n = 0
for x, y, D, F in itertools.product(pool, repeat=4):
    s1 = J(y, x); s2 = J(s1, y)
    W = J(x, J(J(D, s2), D))
    z = J(s2, J(W, J(J(F, s2), F)))
    try:
        t1 = C.op(y, x); t2 = C.op(t1, y); t3 = C.op(z, t2); t4 = C.op(x, t3); t5 = C.op(z, t4)
    except RecursionError:
        continue
    n += 1
    m = ('F' if t1 == J(y, x) else 'D', 'F' if t2 == J(t1, y) else 'D',
         'F' if t3 == J(z, t2) else 'D', 'F' if t4 == J(x, t3) else 'D',
         'F' if t5 == J(z, t4) else 'D')
    tab[m] += 1
    if t5 != x: bad.append(((x, y, z), m, t5))
print('assignments', n)
for k, c in sorted(tab.items(), key=lambda kv: -kv[1]): print('  %-24s %d' % (str(k), c))
print('LAW FAILURES', len(bad))
for (x, y, z), m, r in bad[:2]:
    print('  modes', m)
    print('    x =', show(x)); print('    y =', show(y)); print('    z =', show(z))
    print('    got =', show(r)[:400])
