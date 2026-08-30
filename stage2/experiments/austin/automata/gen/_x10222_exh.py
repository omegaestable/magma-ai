"""Which of the 61 rules fire during the exhaustive small-term checks for 10222?"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import closedform as cf, smallcheck as sc
from freemodel import normalise, catalog
from laws import parse_eq

law = normalise(parse_eq(catalog()[10222]))
X = cf.Extractor(law)
rules = X.rules(exist=False, level2=False)
fired = {}
for ms, g in ((9, 1), (5, 2)):
    C = cf.Closed(law, rules)
    n, f = sc.exhaustive(C, law, ms, g, limit=25)
    print('exh%d/%d tested=%d fails=%d' % (ms, g, n, len(f)), flush=True)
    for k, v in C.fired.items():
        fired[k] = fired.get(k, 0) + v
for i, c in sorted(fired.items()):
    print('  R%-3d %-36s fired %d' % (i, rules[i][2], c))
print('live under exhaustive:', sorted(fired))
