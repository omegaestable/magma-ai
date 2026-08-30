"""Validate the 12234 rule set that gen/rec12234.lean was emitted from, to the full standard."""
import sys, os, time, json
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, revalidate as rv, leangen
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 12234
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig
print('law', law, 'dualized', dualized)

src = open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chk12234.py',
           encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}
exec(src, ns)
rules = ns['rules']
print('nrules', len(rules))
for r in rules:
    print('  ', cf.show_rule(r) if hasattr(cf, 'show_rule') else r[2])

t0 = time.time()
fails = rv.run_tests(law, rules, [3, 4, 5], 3000, 12000)
kinds = {}
for s, r, kind, sd in fails:
    k = ('recursion' if r == 'recursion' else 'value') + ':' + kind
    kinds[k] = kinds.get(k, 0) + 1
print('run_tests fails', len(fails), kinds, round(time.time() - t0, 1), 's')
for s, r, kind, sd in fails[:5]:
    print('  FAIL', kind, 'seed', sd, {k: size(v) for k, v in s.items()}, 'got',
          'recursion' if r == 'recursion' else size(r))

for sd in (20260829, 777):
    C = cf.Closed(law, rules)
    t, f = cf.deep_tests(C, law, 20000, 900, sd)
    print('deep_tests seed', sd, 'tested', t, 'fails', len(f))
