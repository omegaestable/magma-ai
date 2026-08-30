import sys, os, json
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, revalidate as rv, smallcheck as sc, leangen
from freemodel import normalise, catalog
from laws import parse_eq

EQ = 23357
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig
print('law', law, 'dualized', dualized)

src = open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chk%d.py' % EQ, encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}
exec(src, ns)
rules = ns['rules']
for i, r in enumerate(rules):
    print('R%d' % (i + 1), cf.show_rule(r))

if __name__ == '__main__':
    fails = rv.run_tests(law, rules, [3, 4, 5], 3000, 12000)
    print('run_tests fails', len(fails))
    from collections import Counter
    print(Counter(f[2] for f in fails))
    for f in fails[:8]:
        print('  ', f[2], f[0], '->', f[1])
