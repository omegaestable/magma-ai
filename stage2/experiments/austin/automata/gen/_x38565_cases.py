"""_x38565_cases.py -- which (s1,s2,s3,s4) free/decoded patterns actually occur, and which rule
fires at the top, over many random instances of law 38565's chain."""
import sys, os, random, pickle, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import closedform as cf, leangen
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 38565
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = ('x', leangen.dual_pat(orig[1]))
with open(os.path.join(HERE, '_x38565_full.pkl'), 'rb') as f:
    full = pickle.load(f)
rules = [full[i] for i in (0, 1, 6)]
C = cf.Closed(law, rules)
J = lambda a, b: ('J', a, b)
g = lambda n: ('g', n)


def which(u, v):
    """index of the rule that fires at (u,v), or None"""
    for i, (conds, x, tag) in enumerate(C.rules):
        if C.check(conds, u, v) and C.ev(x, u, v) is not None:
            return i
    return None


def chain(x, y, z):
    s1 = C.op(x, z); s2 = C.op(z, s1); s3 = C.op(s2, y); s4 = C.op(y, s3)
    top = C.op(y, s4)
    pat = tuple('D' if C.op(a, b) != J(a, b) else 'F'
                for (a, b) in ((x, z), (z, s1), (s2, y), (y, s3)))
    return pat, which(y, s4), top == x, (s1, s2, s3, s4, top)


def rnd(depth, rng):
    if depth <= 0 or rng.random() < 0.35:
        return g(rng.randrange(3))
    return J(rnd(depth - 1, rng), rnd(depth - 1, rng))


def enc(x, y, z):
    return C.op(y, C.op(y, C.op(C.op(z, C.op(x, z)), y)))


cnt = collections.Counter()
bad = []
rng = random.Random(20260829)
pool = [g(0), g(1), g(2)]
for _ in range(30000):
    if rng.random() < 0.5 and len(pool) > 3:
        x, y, z = (rng.choice(pool) for _ in range(3))
    else:
        x, y, z = (rnd(3, rng) for _ in range(3))
    try:
        pat, w, ok, vals = chain(x, y, z)
    except RecursionError:
        continue
    cnt[(pat, w, ok)] += 1
    if not ok and len(bad) < 5:
        bad.append((x, y, z, pat, w))
    if rng.random() < 0.25 and len(pool) < 400:
        pool.append(enc(x, y, z))
    if rng.random() < 0.15 and len(pool) < 400:
        pool.append(C.op(z, C.op(x, z)))
        pool.append(C.op(C.op(z, C.op(x, z)), y))
for k in sorted(cnt, key=lambda k: -cnt[k]):
    pat, w, ok = k
    print('s1s2s3s4=%s  toprule=%s  ok=%s   n=%d' % (''.join(pat), 'R%d' % (w + 1) if w is not None else 'free', ok, cnt[k]))
print('bad', len(bad))
for b in bad:
    print('  ', [size(t) for t in b[:3]], b[3], b[4])
