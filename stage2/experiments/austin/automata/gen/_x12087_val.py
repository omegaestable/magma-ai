"""Mandatory validation of the 3-rule 12087 model to the WAVE2 standard."""
import sys, os, time
sys.path.insert(0, r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, revalidate as rv, leangen, fuzz as fz
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 12087
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig
print('dualized', dualized, 'law', law)

src = open('gen/_x12087out/chk12087.py', encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); rules = ns['rules']
print('nrules', len(rules))
for r in rules: print('  ', cf.show_rule(r))

t0 = time.time()
fails = rv.run_tests(law, rules, [3, 4, 5], 3000, 12000)
real = [f for f in fails if f[1] != 'recursion']
print('run_tests fails', len(fails), 'real', len(real), 'secs', round(time.time() - t0, 1))
for f in fails[:5]:
    print('   ', f[2], f[3], {k: size(v) for k, v in f[0].items()}, 'got', 'recursion' if f[1] == 'recursion' else size(f[1]))

for sd in (101, 202, 303):
    t1 = time.time()
    C = cf.Closed(law, rules)
    t, f = cf.deep_tests(C, law, 20000, 300, sd)
    fr = [q for q in f if q[1] != 'recursion']
    print('deep_tests seed', sd, 'tested', t, 'fails', len(f), 'real', len(fr), 'secs', round(time.time() - t1, 1))
