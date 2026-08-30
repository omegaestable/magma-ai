"""_pb_minemit9667.py -- check the playbook's copy-pasteable validated-removal loop and emit snippet on 9667."""
import sys, os, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import closedform as cf, revalidate as rv, leangen
from freemodel import normalise, catalog
from laws import parse_eq

EQ = 9667
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig
src = open(os.path.join(HERE, 'chk%d.py' % EQ), encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); rules = ns['rules']

# ---- validated removal (the playbook loop) ----
C = cf.Closed(law, rules)
cf.deep_tests(C, law, 1500, 120, 991)
order = sorted(range(len(rules)), key=lambda i: C.fired.get(i, 0))
keep = list(rules); dropped = []
for i in order:
    r = rules[i]
    if r[2] == 'free':
        continue
    trial = [q for q in keep if q is not r]
    if not trial:
        continue
    if rv.run_tests(law, trial, [3, 4, 5], 3000, 12000):
        print('  KEEP  %-6s (fired %d) - removal breaks the validator' % (r[2], C.fired.get(i, 0)))
        continue
    keep = trial; dropped.append(r[2])
    print('  DROP  %-6s (fired %d) -> %d rules' % (r[2], C.fired.get(i, 0), len(keep)))
print('minimised: %d -> %d rules, dropped %s' % (len(rules), len(keep), dropped))
assert not rv.run_tests(law, keep, [77, 78], 3000, 12000), 'final validation failed'
print('final validation on fresh seeds: 0 fails')

# ---- emit snippet ----
out = os.path.join(HERE, '_pbrep%d' % EQ)
res = leangen.emit(EQ, out, rules_override=keep)
print('emit ->', out, sorted(os.listdir(out)), res)
