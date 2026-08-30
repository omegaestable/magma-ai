"""Validate an arbitrary SUBSET of the 40037 rule list.

usage: _x40037_sub.py 1,7,8 [--deep 3000] [--fuzz 12000]
"""
import sys, os, time, pickle
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'gen'))
import closedform as cf, revalidate as rv, leangen
from freemodel import normalise, catalog, size
from laws import parse_eq
import _x40037_rules as R

EQ = 40037
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = ('x', leangen.dual_pat(orig[1]))


def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))


idx = [int(i) for i in sys.argv[1].split(',')]
N = int(sys.argv[sys.argv.index('--deep') + 1]) if '--deep' in sys.argv else 3000
NF = int(sys.argv[sys.argv.index('--fuzz') + 1]) if '--fuzz' in sys.argv else 12000
rules = [R.ALL[i - 1] for i in idx]
print('subset', idx, '->', len(rules), 'rules')
for i, r in zip(idx, rules):
    print('  R%d %s' % (i, cf.show_rule(r)))

with open(os.path.join(HERE, 'gen', '_x40037_fails.pkl'), 'rb') as f:
    old = [q for q in pickle.load(f) if q[1] != 'recursion']
C = cf.Closed(law, rules)
A, B = law[1]
for s, got, kind, sd in old:
    try:
        r = C.op(C.evp(A, s), C.evp(B, s))
    except RecursionError:
        r = 'recursion'
    print('  regression [%s]: %s' % (kind, 'OK' if r == s['x'] else 'FAILS'))

t0 = time.time()
fails = rv.run_tests(law, rules, [3, 4, 5], N, NF)
real = [f for f in fails if f[1] != 'recursion']
kinds = {}
for s, r, kind, sd in fails:
    k = ('recursion' if r == 'recursion' else 'value') + ':' + kind
    kinds[k] = kinds.get(k, 0) + 1
print('run_tests: %d fails (%d real) in %.1fs  %s' % (len(fails), len(real), time.time() - t0, kinds))
for s, r, kind, sd in real[:4]:
    print('  FAIL[%s seed %s]' % (kind, sd), {k: show(v) for k, v in s.items()})
if not real:
    for sd in (40037, 987654, 555):
        C = cf.Closed(law, rules)
        t0 = time.time()
        tested, f = cf.deep_tests(C, law, 20000, 300, sd)
        f = [q for q in f if q[1] != 'recursion']
        print('  deep_tests seed %d: %d tested, %d fails, %.1fs, cycles %d' % (sd, tested, len(f), time.time() - t0, C.cycles))
