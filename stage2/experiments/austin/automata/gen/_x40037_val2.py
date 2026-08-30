"""Validate a candidate rule set for 40037 to the §7 standard."""
import sys, os, time, pickle, importlib
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'gen'))
import closedform as cf, revalidate as rv, leangen
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 40037
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig


def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))


import _x40037_rules as R
rules = R.RULES
print('law', law, 'dualized', dualized)
print('nrules', len(rules))
for i, r in enumerate(rules):
    print(' R%d %s' % (i + 1, cf.show_rule(r)))

# 1. the two known failing instances
with open(os.path.join(HERE, 'gen', '_x40037_fails.pkl'), 'rb') as f:
    old = [f for f in pickle.load(f) if f[1] != 'recursion']
C = cf.Closed(law, rules)
A, B = law[1]
for s, got, kind, sd in old:
    r = C.op(C.evp(A, s), C.evp(B, s))
    print('  regression [%s]: %s' % (kind, 'OK' if r == s['x'] else 'STILL FAILS got ' + show(r)[:60]))

# 2. the full validator on 3 seeds
t0 = time.time()
fails = rv.run_tests(law, rules, [3, 4, 5], 3000, 12000)
real = [f for f in fails if f[1] != 'recursion']
print('run_tests: %d fails (%d real) in %.1fs' % (len(fails), len(real), time.time() - t0))
kinds = {}
for s, r, kind, sd in fails:
    k = ('recursion' if r == 'recursion' else 'value') + ':' + kind
    kinds[k] = kinds.get(k, 0) + 1
print('  kinds', kinds)
for s, r, kind, sd in real[:4]:
    print('  FAIL[%s seed %s]' % (kind, sd), {k: show(v) for k, v in s.items()})
if real:
    with open(os.path.join(HERE, 'gen', '_x40037_fails2.pkl'), 'wb') as f:
        pickle.dump(fails, f)

# 3. 20,000 deep tests on two further seeds
for sd in (40037, 987654):
    C = cf.Closed(law, rules)
    t0 = time.time()
    tested, f = cf.deep_tests(C, law, 20000, 300, sd)
    f = [q for q in f if q[1] != 'recursion']
    print('  deep_tests seed %d: tested %d, %d fails, %.1fs, cycles %d' % (sd, tested, len(f), time.time() - t0, C.cycles))
