import sys, os, time, json
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, revalidate as rv, leangen
from freemodel import normalise, catalog
from laws import parse_eq

EQ = 23354
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig
print('law', law, 'dualized', dualized)

src = open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chk%d.py' % EQ, encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}
exec(src, ns)
rules = ns['rules']
print('nrules', len(rules))
for i, r in enumerate(rules):
    print(i, cf.show_rule(r))

t0 = time.time()
fails = rv.run_tests(law, rules, [3, 4, 5], 3000, 12000)
real = [f for f in fails if f[1] != 'recursion']
print('run_tests fails', len(fails), 'real', len(real), 'secs', round(time.time() - t0, 1))
for f in real[:5]:
    print('  FAIL', f[2], f[3], {k: str(v) for k, v in f[0].items()})
for sd in (911, 912):
    C = cf.Closed(law, rules)
    t, f = cf.deep_tests(C, law, 20000, 300, sd)
    rf = [x for x in f if x[1] != 'recursion']
    print('deep20k seed', sd, 'tested', t, 'fails', len(f), 'real', len(rf))
