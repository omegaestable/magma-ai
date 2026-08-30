"""_x33020_cases2.py : firing pattern of the hand instances I1..I5 plus fuzz-generated instances
(hooking fuzz.fuzz's own instance stream via its internals is fragile, so we replicate the rule-shaped
construction by reusing fuzz.fuzz and instead sampling from closure_fuzz/critical_fuzz pools).
"""
import sys, os, collections, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import closedform as cf, fuzz as fz, leangen
from freemodel import normalise, catalog, size
from laws import parse_eq

cat = catalog(); orig = normalise(parse_eq(cat[33020]))
law = ('x', leangen.dual_pat(orig[1]))
src = open(os.path.join(HERE, 'repair33020', 'chk33020.py'), encoding='utf-8').read()
ns = {}
exec(src[src.index('rules = '):src.index('C = cf.Closed')], {'cf': cf}, ns)
rules = ns['rules']

def which(C, u, v):
    for i, (conds, e, tag) in enumerate(rules):
        if C.check(conds, u, v) and C.ev(e, u, v) is not None:
            return 'R%d' % (i + 1)
    return '.'

def pat(C, s):
    x, y, z = s['x'], s['y'], s['z']
    s1 = C.op(y, x); s2 = C.op(z, s1); s3 = C.op(x, s2); s4 = C.op(s3, y); T = C.op(y, s4)
    return (which(C, y, x), which(C, z, s1), which(C, x, s2), which(C, s3, y), which(C, y, s4)), T == x

def g(n): return ('g', n)
def J(a, b): return ('J', a, b)
y1 = J(J(g(0), J(g(2), J(g(1), g(0)))), g(1)); cy = J(y1, J(g(2), g(0)))
x3 = J(g(1), J(g(1), J(g(0), g(1)))); xb = J(g(1), g(1)); s2b = J(J(g(0), J(g(2), J(xb, g(0)))), xb)
INST = {'I1': {'x': g(1), 'y': J(y1, J(g(2), J(g(1), y1))), 'z': g(1)}, 'I2': {'x': g(1), 'y': cy, 'z': g(1)},
        'I3': {'x': x3, 'y': J(g(0), g(1)), 'z': x3}, 'I4': {'x': xb, 'y': J(s2b, J(g(2), g(0))), 'z': xb},
        'I5': {'x': cy, 'y': J(J(g(0), cy), J(g(2), g(1))), 'z': cy}}
C = cf.Closed(law, rules)
for k, s in INST.items():
    print(k, pat(C, s))

# fuzz-shaped: use fuzz's own machinery by monkey-hooking Closed.op? simpler: sample from its pools
hist = collections.Counter(); wit = {}
orig_fuzz = fz.fuzz
seen = []
class Spy(cf.Closed):
    pass
for seed in (7, 8, 9, 10, 11, 12):
    C = cf.Closed(law, rules)
    # re-implement: fuzz builds instances then calls C.evp; we just intercept by wrapping evp
    A, B = law[1]
    real_evp = C.evp
    def evp(expr, s, _r=real_evp, _seen=seen):
        if expr is B and isinstance(s, dict) and set(s) >= {'x', 'y', 'z'}:
            _seen.append(dict(s))
        return _r(expr, s)
    C.evp = evp
    try:
        fz.fuzz(C, law, rules, 4000, seed=seed)
    except Exception as e:
        print('fuzz err', type(e).__name__, e)
print('captured', len(seen), 'fuzz assignments')
C = cf.Closed(law, rules)
for s in seen:
    try:
        p, ok = pat(C, s)
    except RecursionError:
        continue
    hist[(p, ok)] += 1
    wit.setdefault(p, s)
for (p, ok), n in sorted(hist.items(), key=lambda kv: -kv[1]):
    print('%-30s ok=%-5s %6d' % ('/'.join(p), ok, n))
for p, s in sorted(wit.items()):
    print('/'.join(p), 'sizes', {k: size(v) for k, v in s.items()})
