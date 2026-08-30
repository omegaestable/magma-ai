import sys, time
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, revalidate as rv, leangen
from freemodel import normalise, catalog
from laws import parse_eq

EQ = 38565
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig
print('law', law, 'dualized', dualized)

src = open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chk38565.py',
           encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}
exec(src, ns)
rules = ns['rules']
print('nrules', len(rules))
for r in rules:
    print(' ', cf.show_rule(r))

t0 = time.time()
fails = rv.run_tests(law, rules, [3, 4, 5], 3000, 12000)
print('run_tests fails', len(fails), 'in %.1fs' % (time.time() - t0))
for f in fails[:5]:
    print('  FAIL', f)

C = cf.Closed(law, rules)
for seed in (777, 991):
    t0 = time.time()
    tested, fl = cf.deep_tests(C, law, 20000, 300, seed)
    print('deep seed', seed, 'tested', tested, 'fails', len(fl), '%.1fs' % (time.time() - t0))
    for f in fl[:3]:
        print('   ', f)
