"""Does the `exist` mode close 10222's exhaustive failures?  Cost + failure counts."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import closedform as cf, smallcheck as sc
from freemodel import normalise, catalog
from laws import parse_eq

law = normalise(parse_eq(catalog()[10222]))
X = cf.Extractor(law)
for name, kw in [('exist,l2=off', dict(exist=True, level2=False)),
                 ('exist,cap2=8', dict(exist=True, level2=True, cap2=8)),
                 ('exist,cap2=64', dict(exist=True, level2=True, cap2=64))]:
    t0 = time.time()
    rules = X.rules(**kw)
    te = time.time() - t0
    print('%s nrules=%d extract=%.1fs' % (name, len(rules), te), flush=True)
    t0 = time.time()
    for ms, g in ((9, 1), (5, 2)):
        C = cf.Closed(law, rules)
        n, f = sc.exhaustive(C, law, ms, g, limit=25)
        print('   exh%d/%d tested=%d fails=%d  (%.1fs)' % (ms, g, n, len(f), time.time() - t0), flush=True)
        if f:
            for s, r in f[:2]:
                print('     FAIL', {k: str(v)[:70] for k, v in s.items()}, flush=True)
