"""Full-standard revalidation of the repaired 10-rule model for law 38316 (dualized L-form)."""
import sys, os, time, json
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, revalidate as rv, leangen
from freemodel import normalise, catalog
from laws import parse_eq

EQ = 38316
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig
print('dualized', dualized, 'law', law)

src = open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chkrep38316.py',
           encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}
exec(src, ns)
rules = ns['rules']
print('nrules', len(rules))
for r in rules:
    print('  ', r[2], cf.show_rule(r))

t0 = time.time()
fails = rv.run_tests(law, rules, [3, 4, 5], 3000, 12000)
print('run_tests fails', len(fails), '%.1fs' % (time.time() - t0))
from collections import Counter
print(Counter([f[2] for f in fails]))
for f in fails[:6]:
    print(' FAIL', f)

if not fails:
    for seed in (777, 4242):
        t0 = time.time()
        C = cf.Closed(law, rules)
        tested, df = cf.deep_tests(C, law, 20000, 300, seed)
        print('deep seed %d: tested %d fails %d  %.1fs' % (seed, tested, len(df), time.time() - t0))
        for f in df[:4]:
            print('   ', f)
