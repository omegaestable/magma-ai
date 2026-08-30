"""Where does `revalidate.py 10222` spend its 2,400 s?  Phase timings at reduced budgets."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import closedform as cf, fuzz as fz, smallcheck as sc
from freemodel import normalise, catalog
from laws import parse_eq

law = normalise(parse_eq(catalog()[10222]))
X = cf.Extractor(law)
for label, kw in (('noexist', dict(exist=False)), ('exist', dict(exist=True))):
    t0 = time.time(); rules = X.rules(**kw); te = time.time() - t0
    print('%s: extract %.2fs -> %d rules' % (label, te, len(rules)), flush=True)
    for name, fn, N in (('exh9/1', lambda C, n: sc.exhaustive(C, law, 9, 1, limit=25), 1),
                        ('exh5/2', lambda C, n: sc.exhaustive(C, law, 5, 2, limit=25), 1),
                        ('deep', lambda C, n: cf.deep_tests(C, law, n, 240, 3), 300),
                        ('fuzz', lambda C, n: fz.fuzz(C, law, rules, n, seed=103), 600),
                        ('closure', lambda C, n: fz.closure_fuzz(C, law, n, seed=203), 600),
                        ('critical', lambda C, n: fz.critical_fuzz(C, law, n, seed=303), 600)):
        C = cf.Closed(law, rules)
        t0 = time.time(); fn(C, N); dt = time.time() - t0
        scale = {'deep': 3000 / N, 'fuzz': 12000 / N, 'closure': 12000 / N, 'critical': 12000 / N}.get(name, 1)
        print('   %-9s N=%-5d %6.1fs   -> at full budget ~%.0fs' % (name, N, dt, dt * scale), flush=True)
