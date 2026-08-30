"""The measured lead: does law 21866's rule set model 21864?  (21866 => 21864 by w := y.)

Runs the full validator of 21864 against the 21866 rule set, and classifies the failures.
"""
import sys, collections, time
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, leangen, trace as TR, revalidate as rv
from freemodel import normalise, catalog, size
from laws import parse_eq

show = TR.show
SRC = int(sys.argv[1]) if len(sys.argv) > 1 else 21866   # rule set to borrow
TGT = int(sys.argv[2]) if len(sys.argv) > 2 else 21864   # law to test
cat = catalog()
lawS = normalise(parse_eq(cat[SRC]))
lawT = normalise(parse_eq(cat[TGT]))
print('source law', SRC, lawS)
print('target law', TGT, lawT)
src = open('gen/chk%d.py' % SRC, encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}
exec(src, ns)
rules = ns['rules']
print('rules', len(rules))
for i, r in enumerate(rules):
    print('  R%-2d %s' % (i + 1, cf.show_rule(r)))

for name, law in (('source', lawS), ('target', lawT)):
    t0 = time.time()
    fails = rv.run_tests(law, rules, [3, 4], 3000, 8000)
    c = collections.Counter('%s:%s' % (f[2], 'rec' if f[1] == 'recursion' else 'value') for f in fails)
    vf = [f for f in fails if f[1] != 'recursion']
    print('%s law %d: FAILS total %d value %d %s (%.1fs)' % (name, SRC if name == 'source' else TGT,
                                                            len(fails), len(vf), dict(c), time.time() - t0))
    vf.sort(key=lambda q: sum(size(t) for t in q[0].values()))
    for s, got, kind, sd in vf[:5]:
        print('   [%s]' % kind, {k: (show(v) if size(v) < 40 else '<%d>' % size(v)) for k, v in s.items()})
