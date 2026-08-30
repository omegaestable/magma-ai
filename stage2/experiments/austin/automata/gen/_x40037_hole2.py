import sys, os, itertools
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'gen'))
import closedform as cf, leangen
from freemodel import normalise, catalog, size
from laws import parse_eq
import _x40037_rules as R
EQ = 40037
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = ('x', leangen.dual_pat(orig[1]))
def J(a, b): return ('J', a, b)
def g(n): return ('g', n)
def show(t): return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))
x = g(0); y = g(0); D = g(0); F = g(1)
s1 = J(y, x); s2 = J(s1, y); W = J(x, J(J(D, s2), D)); z = J(s2, J(W, J(J(F, s2), F)))
print('x =', show(x)); print('y =', show(y)); print('z =', show(z)); print('sz z =', size(z))
SETS = {'4-rule [1,2,14,10]': [1, 2, 14, 10],
        '6-rule GEN (rec40037)': [1, 2, 3, 4, 5, 6],
        '8-rule rep40037a': [1, 2, 3, 4, 5, 6, 14, 10],
        '3-rule rep40037c [15..18]': [15, 17, 18],
        'ALL': list(range(1, len(R.ALL) + 1))}
for name, idx in SETS.items():
    rules = [R.ALL[i - 1] for i in idx]
    C = cf.Closed(law, rules)
    try:
        t1 = C.op(y, x); t2 = C.op(t1, y); t3 = C.op(z, t2); t4 = C.op(x, t3); t5 = C.op(z, t4)
        m = ('F' if t1 == J(y, x) else 'D', 'F' if t2 == J(t1, y) else 'D',
             'F' if t3 == J(z, t2) else 'D', 'F' if t4 == J(x, t3) else 'D',
             'F' if t5 == J(z, t4) else 'D')
        print('%-28s modes %s  law %s' % (name, m, 'OK' if t5 == x else 'FAIL got ' + show(t5)[:60]))
    except RecursionError:
        print('%-28s RecursionError' % name)
