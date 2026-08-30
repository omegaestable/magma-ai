"""exh9/1 + exh5/2 failure counts as a function of cap2 (and level2 off), for 10222."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import closedform as cf, smallcheck as sc
from freemodel import normalise, catalog
from laws import parse_eq

law = normalise(parse_eq(catalog()[10222]))
X = cf.Extractor(law)
cfgs = [('none', dict(level2=False))]
for c in (2, 8, 32, 64, 128, 256, 1024):
    cfgs.append((str(c), dict(level2=True, cap2=c)))
for name, kw in cfgs:
    t0 = time.time()
    rules = X.rules(exist=False, **kw)
    text = time.time() - t0
    t0 = time.time()
    tot = 0
    for ms, g in ((9, 1), (5, 2)):
        C = cf.Closed(law, rules)
        n, f = sc.exhaustive(C, law, ms, g, limit=25)
        tot += len(f)
        print('  cap2=%-5s nrules=%-4d exh%d/%d tested=%d fails=%d' % (name, len(rules), ms, g, n, len(f)), flush=True)
    print('cap2=%-5s nrules=%-4d extract=%.1fs check=%.1fs totalfails=%d' % (name, len(rules), text, time.time() - t0, tot), flush=True)
