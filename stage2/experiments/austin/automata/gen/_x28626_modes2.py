"""FAST joint-freeness probe for law 28626's chain.

a = op y x ; b = op a y ; c = op b y (= u) ; d = op x z (= v) ; final = op c d.
One shared Closed (memo shared across instances -- much faster than a fresh one per instance).
Reports how often each of a,b,c,d is non-free, the joint pattern, and any law failure.
"""
import sys, os, time, random, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import closedform as cf, leangen
from closedform import Extractor
from freemodel import normalise, catalog, size, pvars
from laws import parse_eq
import freetest2 as ft

EQ = 28626
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig
rules = Extractor(law).rules(exist=False)
A, B = law[1]

C = cf.Closed(law, rules)
counts = collections.Counter()
ex = {}
bad = []

def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))

def record(s):
    x, y, z = s['x'], s['y'], s['z']
    try:
        a = C.op(y, x); b = C.op(a, y); c = C.op(b, y); d = C.op(x, z); f = C.op(c, d)
    except RecursionError:
        return
    key = ''.join('F' if t == ('J', p, q) else 'D'
                  for t, p, q in ((a, y, x), (b, a, y), (c, b, y), (d, x, z)))
    counts[key] += 1
    if key not in ex:
        ex[key] = {k: show(v) for k, v in s.items()} if max(size(v) for v in s.values()) < 40 else {k: size(v) for k, v in s.items()}
    if f != x:
        bad.append((s, key))

class Shim: pass
F = Shim(); F.vars = pvars(law[1]); F.rhs = law[1]; F.ev = lambda p, s: C.evp(p, s)
t0 = time.time()
for sd in (21, 3, 77, 101, 5, 9):
    random.seed(sd); pool = []
    n = 0
    while n < 6000 and time.time() - t0 < 900:
        s = ft.nested_triple(F, pool)
        if max(size(t) for t in s.values()) > 120: continue
        n += 1
        for t in s.values():
            if size(t) <= 40 and len(pool) < 400: pool.append(t)
        record(s)
    print('seed', sd, 'done', dict(counts), flush=True)

# fuzz-shaped pool instances
for sd in (11, 13, 17):
    random.seed(sd)
    pool = [('g', 0), ('g', 1), ('g', 2)]
    for _ in range(5):
        pool = pool + [('J', random.choice(pool), random.choice(pool)) for _ in range(25)]
        pool = [t for t in pool if size(t) <= 40]
    for _ in range(15000):
        s = {v: random.choice(pool) for v in ('x', 'y', 'z')}
        record(s)
print('after pool fuzz', dict(counts), flush=True)

# coincidence-targeted: terms built from the model's own A-shape encodings
random.seed(5)
base = [('g', 0), ('g', 1), ('g', 2), ('J', ('g', 0), ('g', 1)), ('J', ('g', 1), ('g', 0))]
for _ in range(30000):
    w = random.choice(base); pay = random.choice(base)
    enc = ('J', ('J', ('J', w, pay), w), w)        # A-shape with payload pay, tag w
    enc2 = ('J', ('J', ('J', enc, pay), enc), enc)
    cand = base + [enc, enc2, ('J', enc, w), ('J', pay, enc), ('J', ('J', w, enc), w)]
    s = {k: random.choice(cand) for k in ('x', 'y', 'z')}
    if max(size(t) for t in s.values()) > 120: continue
    record(s)

print()
print('JOINT (a,b,c,d) F=free D=decoded:')
for k, v in counts.most_common():
    print('  %-6s %8d   %s' % (k, v, ex[k]))
print('law failures:', len(bad))
for s, k in bad[:5]:
    print('  BAD', k, {kk: show(vv) for kk, vv in s.items()})
