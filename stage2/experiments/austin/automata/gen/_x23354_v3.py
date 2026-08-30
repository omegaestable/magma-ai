"""Wave-3 validation of the 23354 rule sets: rv.run_tests on 3 seeds + deep 20k on 3 seeds.
usage: _x23354_v3.py [rec|rep] """
import sys, os, time
from collections import Counter
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, revalidate as rv, leangen
from freemodel import normalise, catalog, size
from laws import parse_eq
EQ = 23354
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig
GEN = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/'
which = sys.argv[1] if len(sys.argv) > 1 else 'rec'
path = GEN + ('chk23354.py' if which == 'rec' else 'rep23354/chk23354.py')
src = open(path, encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); RULES = ns['rules']
print('%s: %d rules %s' % (which, len(RULES), [r[2] for r in RULES]), flush=True)
t0 = time.time()
f = rv.run_tests(law, RULES, [3, 4, 5], 3000, 12000)
print('rv.run_tests fails %d (%.0fs) %s' % (len(f), time.time() - t0, Counter([q[2] for q in f])), flush=True)
for q in f[:3]: print('   ', q[2], q[0])
if not f:
    for sd in (777, 4242, 90210):
        t, df = cf.deep_tests(cf.Closed(law, RULES), law, 20000, 300, sd)
        print('deep seed %d: %d tested, %d fails' % (sd, t, len(df)), flush=True)
