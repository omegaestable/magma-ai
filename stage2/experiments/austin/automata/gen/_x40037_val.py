"""Validate the current gen/chk40037.py rule set to the §7 standard. Prints failing instances."""
import sys, os, json, time
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE)
import closedform as cf, revalidate as rv, leangen
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 40037
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig
print('orig     ', orig)
print('dualized ', dualized)
print('law      ', law)


def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))


def load_rules(path):
    src = open(path, encoding='utf-8').read().split('C = cf.Closed')[0]
    ns = {}
    exec(src, ns)
    return ns['rules']


rules = load_rules(os.path.join(HERE, 'gen', 'chk%d.py' % EQ))
print('nrules', len(rules))
for i, r in enumerate(rules):
    print(' R%d' % (i + 1), cf.show_rule(r) if hasattr(cf, 'show_rule') else r[2])

t0 = time.time()
fails = rv.run_tests(law, rules, [3, 4, 5], 3000, 12000)
print('run_tests fails', len(fails), 'in %.1fs' % (time.time() - t0))
for s, r, kind, sd in fails[:6]:
    print('  FAIL[%s seed %s]' % (kind, sd), {k: show(v) for k, v in s.items()})
    print('     got', 'recursion' if r == 'recursion' else show(r))
import pickle
with open(os.path.join(HERE, 'gen', '_x40037_fails.pkl'), 'wb') as f:
    pickle.dump(fails, f)
