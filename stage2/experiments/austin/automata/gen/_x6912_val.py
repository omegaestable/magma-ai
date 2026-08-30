"""Validate the current 6912 rule set and dump the failing instances."""
import sys, os, json
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, revalidate as rv, leangen
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 6912
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig
print('law', law, 'dualized', dualized)

src = open('gen/chk%d.py' % EQ, encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}
exec(src, ns)
rules = ns['rules']
print('nrules', len(rules))
for i, r in enumerate(rules):
    print(' R%d' % (i + 1), r[2])

fails = rv.run_tests(law, rules, [3, 4, 5], 3000, 12000)
print('run_tests fails', len(fails))
out = []
for s, r, kind, sd in fails:
    print(' FAIL', kind, 'seed', sd, {k: size(v) for k, v in s.items()},
          'got', 'recursion' if r == 'recursion' else size(r))
    out.append(dict(kind=kind, seed=sd, s={k: repr(v) for k, v in s.items()}))
open('gen/_x6912_fails.json', 'w', encoding='utf-8').write(json.dumps(out))
