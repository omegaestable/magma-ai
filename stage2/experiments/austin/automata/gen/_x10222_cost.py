"""Cost curve of Extractor.rules for law 10222 (L-form, x = y*((x*y)*((z*y)*y))).

Usage: python gen/_x10222_cost.py [cap2 ...]
Times X.rules(exist=False, level2=..., cap2=...) and reports nrules.
"""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import closedform as cf, leangen
from freemodel import normalise, catalog
from laws import parse_eq

EQ = 10222
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig
print('law', law, 'dualized', dualized, flush=True)

X = cf.Extractor(law)
print('lform', X.lform, 'rform', X.rform, flush=True)
from closedform import positions
print('A nodes', [p for p, _ in positions(X.A)] if not isinstance(X.A, str) else 'bare')
print('B nodes', [p for p, _ in positions(X.B)] if not isinstance(X.B, str) else 'bare')

settings = []
args = sys.argv[1:]
if not args:
    settings.append(dict(level2=False, cap2=0))
    for c in (1, 2, 4, 8, 16, 32, 64):
        settings.append(dict(level2=True, cap2=c))
else:
    for a in args:
        if a == 'none':
            settings.append(dict(level2=False, cap2=0))
        else:
            settings.append(dict(level2=True, cap2=int(a)))

for s in settings:
    t0 = time.time()
    try:
        rules = X.rules(exist=False, **s)
        dt = time.time() - t0
        print(json.dumps(dict(cfg=s, nrules=len(rules), secs=round(dt, 1))), flush=True)
    except KeyboardInterrupt:
        raise
    except Exception as e:
        print(json.dumps(dict(cfg=s, error=repr(e), secs=round(time.time() - t0, 1))), flush=True)
