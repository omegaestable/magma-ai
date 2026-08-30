"""Find and dump the deep-test failures of a subset. usage: _x40037_deep.py 1,2,3,4,5,6,13 [seed] [N]"""
import sys, os, pickle
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'gen'))
import closedform as cf, leangen
from freemodel import normalise, catalog, size
from laws import parse_eq
import _x40037_rules as R

EQ = 40037
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = ('x', leangen.dual_pat(orig[1]))
idx = [int(i) for i in sys.argv[1].split(',')]
seed = int(sys.argv[2]) if len(sys.argv) > 2 else 40037
N = int(sys.argv[3]) if len(sys.argv) > 3 else 20000
rules = [R.ALL[i - 1] for i in idx]


def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))


C = cf.Closed(law, rules)
tested, fails = cf.deep_tests(C, law, N, 900, seed)
fails = [f for f in fails if f[1] != 'recursion']
print('subset', idx, 'tested', tested, 'real fails', len(fails))
fails.sort(key=lambda f: sum(size(t) for t in f[0].values()))
for s, got in fails[:5]:
    print('FAIL sizes', {k: size(v) for k, v in s.items()})
    for k in ('x', 'y', 'z'):
        print('   %s = %s' % (k, show(s[k])))
with open(os.path.join(HERE, 'gen', '_x40037_deepfails.pkl'), 'wb') as f:
    pickle.dump([(s, g, 'deep', seed) for s, g in fails], f)
