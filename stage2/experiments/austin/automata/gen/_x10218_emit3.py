"""Emit + validate the 3-rule minimised 10218 model from gen/_orch_min10218.json."""
import sys, os, json, time, itertools
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'gen'))
import closedform as cf, leangen, revalidate as rv, smallcheck as sc
from freemodel import normalise, catalog, size
from laws import parse_eq
EQ = 10218
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig
print('law', law, 'dualized', dualized)
def conv(e):
    return tuple(conv(x) if isinstance(x, list) else x for x in e)
d = json.load(open(os.path.join(HERE, 'gen', '_orch_min10218.json'), encoding='utf-8'))
rules = [(tuple(conv(c) for c in r[0]), conv(r[1]), r[2]) for r in d['rules']]
print('rules', len(rules))
for r in rules: print('  ', r[2])
t0 = time.time()
fails = rv.run_tests(law, rules, [3, 4, 5], 3000, 12000)
print('run_tests: %d fails in %.0fs' % (len(fails), time.time() - t0), flush=True)
for s, r in fails[:5]: print('   FAIL', s)
C = cf.Closed(law, rules)
for sd in (10218, 987654, 555):
    t0 = time.time(); n, f = cf.deep_tests(C, law, 20000, 300, sd)
    print('  deep seed %d: %d tested, %d fails, %.0fs' % (sd, n, len(f), time.time() - t0), flush=True)
if not fails:
    leangen.emit(EQ, os.path.join(HERE, 'gen', 'rep10218'), rules_override=rules)
    print('emitted gen/rep10218/')
