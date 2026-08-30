"""probe the current 21864 rule set: run_tests, group failures, show the smallest exhaustive ones."""
import sys, os, json, collections
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, revalidate as rv, leangen, smallcheck as sc
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = int(sys.argv[1]) if len(sys.argv) > 1 else 21864
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
    print(' R%d' % (i + 1), cf.show_rule(r) if hasattr(cf, 'show_rule') else r[2])

fails = rv.run_tests(law, rules, [3, 4, 5], 3000, 12000)
c = collections.Counter('%s:%s' % (f[2], f[1] if f[1] == 'recursion' else 'value') for f in fails)
print('FAILS', len(fails), dict(c))


def show(t):
    if isinstance(t, str):
        return t
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))


vf = [f for f in fails if f[1] != 'recursion']
vf.sort(key=lambda f: sum(size(v) for v in f[0].values()))
for s, r, kind, sd in vf[:8]:
    print('FAIL[%s]' % kind, {k: show(v) for k, v in s.items()}, '->', show(r))
