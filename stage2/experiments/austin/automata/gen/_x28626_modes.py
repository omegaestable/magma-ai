"""Joint mode distribution of the four chain products of law 28626.

chain (inside out):  a = op y x ;  b = op a y ;  c = op b y  (= u) ;  d = op x z  (= v) ;  final = op c d.
Prints, over deep + fuzz + closure + critical instances, how often each of a,b,c,d was non-free and
which rule fired at the final product.  The question the proof needs answered:
  * can `c = op b y` ever decode?  (no rule of the 10 handles a decoded A-top)
  * which (a-mode, b-mode, d-mode) combinations really occur?
"""
import sys, os, time, random, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import closedform as cf, fuzz as fz, leangen
import trace as tr
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

counts = collections.Counter()
finalr = collections.Counter()
bad = []
examples = {}

def chain(s):
    T = tr.Tracing(law, rules)
    T.trace_on = True
    modes = []
    def prod(p, q):
        T.log = []
        r = T.op(p, q)
        w = T.log[-1][2] if T.log else None
        modes.append(w)
        return r
    a = prod(s['y'], s['x'])
    b = prod(a, s['y'])
    c = prod(b, s['y'])
    d = prod(s['x'], s['z'])
    f = prod(c, d)
    return modes, f

def record(s):
    try:
        modes, f = chain(s)
    except RecursionError:
        return
    key = tuple('F' if m is None else 'R%d' % (m + 1) for m in modes[:4])
    counts[key] += 1
    finalr['F' if modes[4] is None else 'R%d' % (modes[4] + 1)] += 1
    if key not in examples:
        examples[key] = {k: size(v) for k, v in s.items()}
    if f != s['x']:
        bad.append((s, key))

# --- deep instances (same generator deep_tests uses) ---
class Shim: pass
C0 = cf.Closed(law, rules)
F = Shim(); F.vars = pvars(law[1]); F.rhs = law[1]; F.ev = lambda p, s: C0.evp(p, s)
for sd in (21, 3, 77, 101):
    random.seed(sd); pool = []
    t0 = time.time(); n = 0
    while n < 8000 and time.time() - t0 < 240:
        s = ft.nested_triple(F, pool)
        if max(size(t) for t in s.values()) > 120: continue
        n += 1
        for t in s.values():
            if size(t) <= 40 and len(pool) < 400: pool.append(t)
        record(s)
print('after deep:', dict(counts))

# --- fuzz-shaped instances ---
for sd in (11, 13, 17):
    random.seed(sd)
    pool = [('g', 0), ('g', 1), ('g', 2)]
    for _ in range(6):
        pool = pool + [('J', random.choice(pool), random.choice(pool)) for _ in range(30)]
        pool = [t for t in pool if size(t) <= 60]
    vs = pvars(law[1])
    for _ in range(20000):
        s = {v: random.choice(pool) for v in vs}
        record(s)
print('after fuzz-pool:', dict(counts))

# --- critical: x/y/z built as encodings of each other ---
def enc(p, q):
    # the A-shape encoding: J(J(J(p, payload), p), p) encodes payload with tag p
    return p, q
random.seed(5)
base = [('g', 0), ('g', 1), ('g', 2), ('J', ('g', 0), ('g', 1))]
for _ in range(40000):
    w = random.choice(base)
    pay = random.choice(base + [('J', ('g', 1), ('g', 2))])
    y = ('J', ('J', ('J', w, pay), w), w)
    cand = [y, w, pay, ('J', ('J', ('J', y, pay), y), y), ('J', pay, w)]
    s = {'x': random.choice(cand), 'y': random.choice(cand), 'z': random.choice(cand)}
    if max(size(t) for t in s.values()) > 120: continue
    record(s)

print()
print('JOINT MODES (a=op y x, b=op a y, c=op b y, d=op x z):')
for k, v in counts.most_common():
    print('  %-24s %8d   sizes %s' % (str(k), v, examples[k]))
print('FINAL rule:', dict(finalr))
print('law failures:', len(bad))
for s, k in bad[:5]:
    print('  BAD', k, {kk: size(vv) for kk, vv in s.items()})
