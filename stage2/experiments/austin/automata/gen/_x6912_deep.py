"""Deep validation of a 6912 rule-set variant: run_tests on fresh seeds + 20k deep on 3 seeds."""
import sys, os, time, pickle
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen')
import closedform as cf, revalidate as rv
from freemodel import size
import _x6912_rep as R

law = R.law
which = sys.argv[1] if len(sys.argv) > 1 else 'bare'
if which.endswith('.pkl'):
    rules = pickle.load(open(which, 'rb'))
else:
    rules = R.VARIANTS[which]
print('rules(%d):' % len(rules), [r[2] for r in rules], flush=True)
tot = 0
for seeds in ([3, 4, 5], [77, 78], [911, 1012]):
    f = rv.run_tests(law, rules, seeds, 3000, 12000)
    f = [x for x in f if x[1] != 'recursion']
    tot += len(f)
    print('run_tests %s fails=%d' % (seeds, len(f)), flush=True)
    for s, r, kind, sd in f[:3]:
        print('   FAIL', kind, sd, {k: size(v) for k, v in s.items()}, flush=True)
for sd in (1234, 4321, 20260829, 55555):
    C = cf.Closed(law, rules)
    t, fl = cf.deep_tests(C, law, 20000, 900, sd)
    fl = [x for x in fl if x[1] != 'recursion']
    tot += len(fl)
    print('deep 20000 seed %d: tested %d fails %d' % (sd, t, len(fl)), flush=True)
    for s, r in fl[:3]:
        print('   FAIL', {k: size(v) for k, v in s.items()}, flush=True)
print('TOTAL real fails:', tot)
