"""Firing-count census for 10222, then bulk-drop of never-fired rules + validation.

python gen/_x10222_fire.py <cap2|none>
"""
import sys, os, time, json, pickle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import closedform as cf, leangen, fuzz as fz, smallcheck as sc, revalidate as rv
from freemodel import normalise, catalog
from laws import parse_eq

EQ = 10222
cat = catalog(); law = normalise(parse_eq(cat[EQ]))
X = cf.Extractor(law)
arg = sys.argv[1] if len(sys.argv) > 1 else 'none'
rules = X.rules(exist=False, level2=False) if arg == 'none' else X.rules(exist=False, level2=True, cap2=int(arg))
print('nrules', len(rules), flush=True)

fired = {}
t0 = time.time()
for sd in (3, 4, 5, 11, 12):
    C = cf.Closed(law, rules)
    sc.exhaustive(C, law, 8, 1, limit=5)
    cf.deep_tests(C, law, 800, 300, sd)
    for k, v in C.fired.items():
        fired[k] = fired.get(k, 0) + v
    C2 = cf.Closed(law, rules)
    fz.fuzz(C2, law, rules, 1500, seed=sd + 100)
    for k, v in C2.fired.items():
        fired[k] = fired.get(k, 0) + v
    C3 = cf.Closed(law, rules)
    fz.closure_fuzz(C3, law, 1500, seed=sd + 200)
    for k, v in C3.fired.items():
        fired[k] = fired.get(k, 0) + v
    C4 = cf.Closed(law, rules)
    fz.critical_fuzz(C4, law, 1500, seed=sd + 300)
    for k, v in C4.fired.items():
        fired[k] = fired.get(k, 0) + v
print('census %.1fs' % (time.time() - t0), flush=True)
live = sorted(fired.items(), key=lambda kv: -kv[1])
for i, c in live:
    print('  R%-3d %-40s fired %d' % (i, rules[i][2], c), flush=True)
print('live rules: %d of %d' % (len(live), len(rules)), flush=True)

keep = [rules[i] for i in sorted(fired)]
if rules[0] not in keep:
    keep = [rules[0]] + keep
print('trial keep = %d rules' % len(keep), flush=True)
t0 = time.time()
f = rv.run_tests(law, keep, [3, 4], 1500, 4000)
real = [x for x in f if x[1] != 'recursion']
print('run_tests(keep) fails=%d real=%d  %.1fs' % (len(f), len(real), time.time() - t0), flush=True)
for s, r, kind, sd in real[:3]:
    print('  FAIL', kind, {k: str(v)[:70] for k, v in s.items()}, flush=True)
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '_x10222_keep_%s.pkl' % arg), 'wb') as fh:
    pickle.dump(keep, fh)
