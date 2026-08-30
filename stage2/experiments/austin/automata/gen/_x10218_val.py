import sys, os, time, json
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
os.chdir('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, revalidate as rv, leangen
from freemodel import normalise, catalog
from laws import parse_eq

EQ = 10218
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig
print('orig', orig)
print('dualized', dualized)
print('law', law)

src = open('gen/chk%d.py' % EQ, encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}
exec(src, ns)
rules = ns['rules']
print('nrules', len(rules))

t = time.time()
fails = rv.run_tests(law, rules, [3, 4, 5], 3000, 12000)
val = [f for f in fails if f[2].split(':')[0] != 'recursion']
print('run_tests fails', len(fails), 'value fails', len(val), '%.1fs' % (time.time() - t))
from collections import Counter
print(Counter(f[2] for f in fails))
for f in val[:5]:
    print('FAIL', f[0], '->', str(f[1])[:200], f[2], f[3])
