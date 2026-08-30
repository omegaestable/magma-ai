"""Validate the EXISTING generated 17-rule package for law 36524 (no re-extraction).

Usage: python gen/_x36524_val.py [seeds...]
"""
import sys, os, time, json
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE)
import closedform as cf, revalidate as rv, leangen
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 36524
cat = catalog()
orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig
print('orig    ', orig)
print('dualized', dualized)
print('law     ', law)

src = open(os.path.join(HERE, 'gen', 'chk%d.py' % EQ), encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}
exec(src, ns)
rules = ns['rules']
print('nrules', len(rules))

t0 = time.time()
fails = rv.run_tests(law, rules, [3, 4, 5], 3000, 12000)
kinds = {}
for s, r, kind, sd in fails:
    k = ('recursion' if r == 'recursion' else 'value') + ':' + kind
    kinds[k] = kinds.get(k, 0) + 1
print('run_tests fails', len(fails), kinds, '%.1fs' % (time.time() - t0))
for s, r, kind, sd in fails[:5]:
    print('  FAIL', kind, 'seed', sd, {k: size(v) for k, v in s.items()},
          'got', 'recursion' if r == 'recursion' else size(r))
real = [f for f in fails if f[1] != 'recursion']
print('REAL value fails:', len(real))
if not real:
    for sd in (777, 778):
        t1 = time.time()
        C = cf.Closed(law, rules)
        t, f = cf.deep_tests(C, law, 20000, 300, sd)
        rf = [x for x in f if x[1] != 'recursion']
        print('deep20k seed', sd, 'tested', t, 'fails', len(f), 'real', len(rf), '%.1fs' % (time.time() - t1))
