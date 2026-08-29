import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import closedform as cf, revalidate as rv, smallcheck as sc, leangen
from freemodel import normalise, catalog
from laws import parse_eq
from closedform import Extractor

EQ = 28626
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = orig
X = Extractor(law)
rules = X.rules(exist=False)
print('nrules', len(rules))

t0 = time.time()
fails = rv.run_tests(law, rules, [3, 4, 5], 3000, 12000)
print('run_tests(seeds 3,4,5) fails:', len(fails), 'secs', round(time.time()-t0,1))
for f in fails[:5]: print(' FAIL', f[2], f[3])

# targeted: the seed that found the original hole, at higher N
t0 = time.time()
C = cf.Closed(law, rules)
tested, f21 = cf.deep_tests(C, law, 20000, 240, 21)
print('deep_tests seed21 N=20000: tested', tested, 'fails', len(f21), 'secs', round(time.time()-t0,1))

# a few more seeds at N=20000 for extra confidence
for sd in (1,2,6,7,8,9,10):
    C2 = cf.Closed(law, rules)
    t, f = cf.deep_tests(C2, law, 20000, 120, sd)
    if f:
        print(' FAIL seed', sd, 'tested', t, 'fails', len(f))
    else:
        print(' seed', sd, 'OK tested', t)
