"""Census v2 for 10222: firing counts under EXACTLY the run_tests suite (exh9/1, exh5/2, deep,
fuzz, closure_fuzz, critical_fuzz), then bulk-drop of never-fired rules + validation.
"""
import sys, os, time, json, pickle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import closedform as cf, leangen, fuzz as fz, smallcheck as sc, revalidate as rv
from freemodel import normalise, catalog
from laws import parse_eq

EQ = 10222
cat = catalog(); law = normalise(parse_eq(cat[EQ]))
X = cf.Extractor(law)
rules = X.rules(exist=False, level2=False)
print('nrules', len(rules), flush=True)

fired = {}
def census(C):
    for k, v in C.fired.items():
        fired[k] = fired.get(k, 0) + v

t0 = time.time()
for ms, g in ((9, 1), (5, 2)):
    C = cf.Closed(law, rules); sc.exhaustive(C, law, ms, g, limit=25); census(C)
    print('  exh%d/%d done %.1fs' % (ms, g, time.time() - t0), flush=True)
for sd in (3, 4, 5):
    C = cf.Closed(law, rules); cf.deep_tests(C, law, 3000, 240, sd); census(C)
    C = cf.Closed(law, rules); fz.fuzz(C, law, rules, 6000, seed=sd + 100); census(C)
    C = cf.Closed(law, rules); fz.closure_fuzz(C, law, 6000, seed=sd + 200); census(C)
    C = cf.Closed(law, rules); fz.critical_fuzz(C, law, 6000, seed=sd + 300); census(C)
    print('  seed %d done %.1fs' % (sd, time.time() - t0), flush=True)
print('census %.1fs' % (time.time() - t0), flush=True)
for i, c in sorted(fired.items(), key=lambda kv: -kv[1]):
    print('  R%-3d %-40s fired %d' % (i, rules[i][2], c), flush=True)
print('live rules: %d of %d' % (len(fired), len(rules)), flush=True)

keep = [rules[i] for i in sorted(fired)]
print('trial keep = %d rules: %s' % (len(keep), [r[2] for r in keep]), flush=True)
t0 = time.time()
f = rv.run_tests(law, keep, [3, 4, 5], 3000, 12000)
real = [x for x in f if x[1] != 'recursion']
print('run_tests(keep) fails=%d real=%d  %.1fs' % (len(f), len(real), time.time() - t0), flush=True)
kinds = {}
for s, r, kind, sd in real:
    kinds[kind] = kinds.get(kind, 0) + 1
print('kinds', kinds, flush=True)
for s, r, kind, sd in real[:3]:
    print('  FAIL', kind, {k: str(v)[:90] for k, v in s.items()}, flush=True)
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '_x10222_keep2.pkl'), 'wb') as fh:
    pickle.dump(keep, fh)
