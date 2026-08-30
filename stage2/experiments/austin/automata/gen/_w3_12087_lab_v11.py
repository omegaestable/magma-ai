# -*- coding: utf-8 -*-
"""Law 12087 carrier laboratory (the 13764 move).

Law (L-form):  x = y * (((y*x)*z) * (x*z))
Chain:  N1 = y*x ; N2 = N1*z ; N3 = x*z ; V = N2*N3 ; goal  y*V = x.

Free-model verdict (this session): EVERY finite extractor rule set is FALSE -- the decoder must descend
an unbounded number of x-encoding levels inside z.  Fix, following gen/NOTES_13764.md: a second
constructor `E` that TAGS the encoding and CARRIES THE DECODER, so a decode is `tg v = 3 & a2 v = u -> a1 v`
(depth 1, no descent) and a decoded inner product loses nothing (x is recoverable from the tag).
"""
import itertools, random, sys
sys.setrecursionlimit(100000)

TAG = {'g': 1, 'J': 2, 'E': 3}
def tg(t): return TAG[t[0]]
def a1(t): return t[1] if t[0] != 'g' else t
def a2(t): return t[2] if t[0] != 'g' else t
def sz(t): return 1 if t[0] == 'g' else sz(t[1]) + sz(t[2]) + 1
def show(t, d=0):
    if t[0] == 'g': return 'g%d' % t[1]
    if d > 7: return '<%d>' % sz(t)
    return '%s(%s,%s)' % (t[0], show(t[1], d+1), show(t[2], d+1))

PROF = {}

def xc(w):
    out = []
    if tg(a2(w)) != 1: out.append(a1(a2(w)))
    z = a2(a1(w))
    if tg(z) == 3: out.append(a1(a1(a1(z))))
    return out

def Dec(u, v, depth=0):
    """anchored by tg v = 3: only a node this model tagged can match."""
    if tg(v) != 3: return None
    z = a2(a1(v))
    for X in xc(v):
        if op(u, X, depth + 1) == a1(a1(v)) and op(X, z, depth + 1) == a2(v):
            return X
    # reading 3: N2 was decoded, so a1 v is opaque -- B0's two-step relation, now ANCHORED by tg v = 3
    if tg(a2(v)) != 1:
        X = a1(a2(v)); zz = a2(a2(v))
        if op(X, zz, depth + 1) == a2(v) and op(op(u, X, depth + 1), zz, depth + 1) == a1(v):
            return X
    return None

def P(u, v, depth=0):
    if tg(u) == 1: return False
    z = a2(u)
    if tg(a1(u)) != 1 and op(a2(a1(u)), z, depth + 1) == v: return True
    if tg(z) == 3 and op(a1(a1(a1(z))), z, depth + 1) == v: return True
    # mark for the opaque-N2 case: shape only.  A mark commits to nothing, so a spurious firing is
    # harmless; it exists purely to give the root the tg v = 3 anchor.
    if tg(v) == 2 and tg(a2(v)) != 1 and op(a1(v), a2(v), depth + 1) == v: return True
    return False

def op(u, v, depth=0):
    if depth > 60: return ('J', u, v)
    X = Dec(u, v, depth)
    if X is not None:
        PROF[(u, v)] = 'D'; return X
    if P(u, v, depth):
        PROF[(u, v)] = 'T'; return ('E', u, v)
    PROF[(u, v)] = None
    return ('J', u, v)

def chain(x, y, z):
    N1 = op(y, x); N2 = op(N1, z); N3 = op(x, z); V = op(N2, N3); R = op(y, V)
    return N1, N2, N3, V, R

def prof(x, y, z):
    N1, N2, N3, V, R = chain(x, y, z)
    g = lambda u, v: PROF.get((u, v)) or 'F'
    return (g(y, x), g(N1, z), g(x, z), g(N2, N3), g(y, V))

# ------------------------------------------------------------------ validators
def terms(maxsize, gens, cons=('J', 'E')):
    by = {1: [('g', i) for i in range(gens)]}
    for n in range(3, maxsize + 1, 2):
        by[n] = []
        for a in range(1, n - 1, 2):
            b = n - 1 - a
            if b in by:
                for s in by[a]:
                    for t in by[b]:
                        for c in cons: by[n].append((c, s, t))
    out = []
    for n in sorted(by): out += by[n]
    return out

def L1(maxsize=5, gens=2, limit=6):
    pool = terms(maxsize, gens); n = 0; bad = []
    for x in pool:
        for y in pool:
            for z in pool:
                n += 1
                try:
                    if chain(x, y, z)[4] != x:
                        bad.append((x, y, z))
                        if len(bad) >= limit: return n, bad, pool
                except RecursionError: bad.append((x, y, z))
    return n, bad, pool

def deep(seed, N, maxd=5, gens=3):
    random.seed(seed); bad = []
    def rt(d):
        if d <= 0 or random.random() < 0.3: return ('g', random.randrange(gens))
        return (random.choice(('J', 'E')), rt(d-1), rt(d-1))
    for _ in range(N):
        x, y, z = rt(maxd), rt(maxd), rt(maxd)
        try:
            if chain(x, y, z)[4] != x: bad.append((x, y, z))
        except RecursionError: bad.append((x, y, z))
    return bad

def enc(a, b, c):
    """the law's RHS for y=a, x=b, z=c -- must decode to b under a"""
    return op(op(op(a, b), c), op(b, c))

def descent(levels, seed, N, bigjunk=False, gens=3):
    """THE level-k descent oracle (this session's finding), on the new carrier"""
    random.seed(seed)
    small = [('g', i) for i in range(gens)] + [(c, ('g', i), ('g', j))
             for c in ('J', 'E') for i in range(gens) for j in range(gens)]
    def rt(d):
        if d <= 0 or random.random() < 0.35: return ('g', random.randrange(gens))
        return (random.choice(('J', 'E')), rt(d-1), rt(d-1))
    big = [rt(4) for _ in range(60)]
    junk = big if bigjunk else small
    bad = []; hits = 0
    for _ in range(N):
        try:
            y = random.choice(small)
            x = enc(y, random.choice(small), random.choice(junk))
            if op(y, x) == ('J', y, x): continue
            p = random.choice(small)
            for _ in range(levels): p = enc(x, p, random.choice(junk))
            z = enc(x, p, random.choice(junk))
            if op(x, z) == ('J', x, z): continue
            hits += 1
            if chain(x, y, z)[4] != x: bad.append((x, y, z))
        except RecursionError:
            continue
    return hits, bad

if __name__ == '__main__':
    import time
    t0 = time.time()
    n, bad, pool = L1(5, 2)
    print('L1 exhaustive size<=5 gens=2 (%d terms): %d chains, %d fails (%.0fs)' % (len(pool), n, len(bad), time.time()-t0), flush=True)
    for (x, y, z) in bad[:3]:
        print('   x=%s\n   y=%s\n   z=%s\n   profile %s got %s' % (show(x), show(y), show(z), prof(x, y, z), show(chain(x, y, z)[4])), flush=True)
    if not bad:
        for sd in (1, 2, 3):
            b = deep(sd, 4000)
            print('deep seed %d: %d fails' % (sd, len(b)), flush=True)
            for (x, y, z) in b[:2]:
                print('   x=%s\n   y=%s\n   z=%s\n   profile %s' % (show(x), show(y), show(z), prof(x, y, z)), flush=True)
            if b: break
        for lv in (0, 1, 2, 3):
            for bj in (False, True):
                h, b = descent(lv, 5, 250, bj)
                print('descent levels=%d bigjunk=%-5s hits=%-4d fails=%d' % (lv, bj, h, len(b)), flush=True)
                for (x, y, z) in b[:1]:
                    print('   profile %s sizes x=%d y=%d z=%d' % (prof(x, y, z), sz(x), sz(y), sz(z)), flush=True)
    print('total %.0fs' % (time.time()-t0))
