"""Timing/validation probe for 10222 rule sets of various sizes.

python gen/_x10222_val.py <cap2|none> <deepN> <fuzzN>
"""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import closedform as cf, leangen, fuzz as fz, smallcheck as sc
from freemodel import normalise, catalog
from laws import parse_eq

EQ = 10222
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = orig  # L-form, not dualized

X = cf.Extractor(law)
arg = sys.argv[1]
if arg == 'none':
    rules = X.rules(exist=False, level2=False)
else:
    rules = X.rules(exist=False, level2=True, cap2=int(arg))
N = int(sys.argv[2]) if len(sys.argv) > 2 else 300
NF = int(sys.argv[3]) if len(sys.argv) > 3 else 1000
print('nrules', len(rules), flush=True)

t0 = time.time()
n, f = sc.exhaustive(cf.Closed(law, rules), law, 7, 1, limit=5)
print('exh7/1 tested=%d fails=%d  %.1fs' % (n, len(f), time.time() - t0), flush=True)

t0 = time.time()
C = cf.Closed(law, rules)
t, f2 = cf.deep_tests(C, law, N, 300, 3)
print('deep tested=%d fails=%d  %.1fs' % (t, len(f2), time.time() - t0), flush=True)
for s, r in f2[:2]:
    print('  FAIL', {k: str(v)[:60] for k, v in s.items()}, flush=True)

t0 = time.time()
t3, f3 = fz.fuzz(cf.Closed(law, rules), law, rules, NF, seed=103)
print('fuzz tested=%d fails=%d  %.1fs' % (t3, len(f3), time.time() - t0), flush=True)
