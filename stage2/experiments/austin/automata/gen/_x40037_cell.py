"""Hand-constructed case-tree cells for 40037 (rail 50: a sampler cannot reach a measure-zero cell).

Cell hunted here: s1 = op(y,x) FREE while s2 = op(s1,y) DECODED (rule R3 on (J y x, y)).
R3 needs P3 (J y x) y  =  tg y = 2  and  E3 (a1 y), and the guard  a2 y = op (J y x) (op X' W')
with X' = a1 (a1 y), W' = a1 (a2 (a1 y)).  Take a1 y = enc(X',T',W') and a2 y = X'.
"""
import sys, os, itertools, collections
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'gen'))
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


def J(a, b):
    return ('J', a, b)


def enc(x, y, z):
    return J(x, J(z, J(J(y, x), y)))


def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))


base = [('g', 0), ('g', 1), ('g', 2), J(('g', 0), ('g', 1)), J(('g', 1), ('g', 2)),
        J(J(('g', 0), ('g', 1)), ('g', 2)), enc(('g', 0), ('g', 1), ('g', 2))]

tab = collections.Counter()
bad = []
hits = []
n = 0
for Xp, Tp, Wp in itertools.product(base, repeat=3):
    A = enc(Xp, Tp, Wp)
    for tail in (Xp, J(Xp, ('g', 5)), ('g', 9)):
        y = J(A, tail)
        for x in base:
            for z in base:
                try:
                    s1 = C.op(y, x); s2 = C.op(s1, y); s3 = C.op(z, s2)
                    s4 = C.op(x, s3); s5 = C.op(z, s4)
                except RecursionError:
                    continue
                n += 1
                m = ('F' if s1 == J(y, x) else 'D', 'F' if s2 == J(s1, y) else 'D',
                     'F' if s3 == J(z, s2) else 'D', 'F' if s4 == J(x, s3) else 'D',
                     'F' if s5 == J(z, s4) else 'D')
                tab[m] += 1
                if m[0] == 'F' and m[1] == 'D':
                    hits.append((x, y, z))
                if s5 != x:
                    bad.append(((x, y, z), m))
print('assignments', n)
for k, c in sorted(tab.items(), key=lambda kv: -kv[1]):
    print('  %-24s %d' % (str(k), c))
print('FD-hits', len(hits))
for x, y, z in hits[:3]:
    print('   x=%s' % show(x)[:120]); print('   y=%s' % show(y)[:120]); print('   z=%s' % show(z)[:120])
print('LAW FAILURES', len(bad))
for (x, y, z), m in bad[:5]:
    print('  ', m)
    print('    x =', show(x)[:300])
    print('    y =', show(y)[:300])
    print('    z =', show(z)[:300])
