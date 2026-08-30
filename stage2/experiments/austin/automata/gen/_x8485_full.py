"""_x8485_full.py : extract the FULL rule set for law 8485 and validate it (no minimisation)."""
import sys, os, time, json
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
os.chdir('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, revalidate as rv, leangen
from freemodel import normalise, catalog, size
from laws import parse_eq
from collections import Counter

EQ = 8485
cat = catalog(); law = normalise(parse_eq(cat[EQ]))
X = cf.Extractor(law)
print('lform', X.lform, 'rform', X.rform)
t0 = time.time()
rules = X.rules(exist=False)
print('full nrules', len(rules), round(time.time() - t0, 1), 's')
for i, r in enumerate(rules):
    print('  R%-3d %s' % (i + 1, cf.show_rule(r)))
t0 = time.time()
fails = rv.run_tests(law, rules, [3, 4, 5], 3000, 12000)
print('run_tests fails', len(fails), round(time.time() - t0, 1), 's')
print(Counter((('recursion' if f[1] == 'recursion' else 'value') + ':' + f[2]) for f in fails))
