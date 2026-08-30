# -*- coding: utf-8 -*-
"""Law 9663, DEC-guard SEPARATOR experiment (session 9).

lab4's residual cell is `*,D,*,.,E`: DEC fires at the Q slot (op(x,P)) where TAGF/TAGE is wanted,
and then the root has nothing to read.  lab4's NOTES say "the root and Q present the same pair, so
no guard can separate them".  THEY DO NOT:

    root : u = y,  v = C = op(A,Q)      -> needs a1(v) = A = op(z,y),  a2(v) = Q
    bad Q: u = x,  v = P = op(x,y)      -> a1(v) = x = u

So `a1 v != u` is a candidate separator, expressible as a predicate on (u,v).
SEP=0 : lab4 verbatim (control)     SEP=1 : DEC gains `a1 v != u`
SEP=2 : DEC gains `tg v != 4`       SEP=3 : DEC gains both
"""
import sys, os, random
sys.setrecursionlimit(100000)
SEP = int(os.environ.get('SEP9663', '0'))
TAG = {'g': 1, 'J': 2, 'E': 3, 'F': 4}
def tg(t): return TAG[t[0]]
def a1(t): return t[1] if t[0] != 'g' else t
def a2(t): return t[2] if t[0] != 'g' else t
def sz(t): return 1 if t[0] == 'g' else sz(t[1]) + sz(t[2]) + 1
def G(n): return ('g', n)
def J(a, b): return ('J', a, b)
def E(a, b): return ('E', a, b)
def F(a, b): return ('F', a, b)
def show(t, d=0):
    if t[0] == 'g': return 'g%d' % t[1]
    if d > 7: return '<%d>' % sz(t)
    return '%s(%s,%s)' % (t[0], show(t[1], d + 1), show(t[2], d + 1))

PROF = {}
R2ON = True

def R2(u, v, d):
    if not R2ON or tg(u) == 1: return None
    Q = a2(u)
    if tg(Q) == 1: return None
    P = a2(Q)
    if tg(P) == 1: return None
    p, x = a1(Q), a2(P)
    if op(p, x, d + 1) != P: return None
    if op(x, p, d + 1) != a2(v): return None
    return x

def op(u, v, d=0):
    if d > 60: return J(u, v)
    if tg(v) != 1:
        Q = a2(v)
        sep = True
        if SEP in (1, 3, 4, 5) and a1(v) == u: sep = False
        if SEP in (2, 3) and tg(v) == 4: sep = False
        if sep and SEP == 4 and tg(Q) == 4 and op(a1(Q), a2(Q), d + 1) != Q: sep = False
        if sep and SEP == 5 and tg(Q) == 4 and tg(a2(Q)) == 1: sep = False
        if sep and tg(Q) == 4 and op(a1(Q), u, d + 1) == a2(Q):
            PROF[(u, v)] = 'D'; return a1(Q)
    x = R2(u, v, d)
    if x is not None:
        PROF[(u, v)] = 'R'; return x
    if tg(v) != 1 and a1(v) == u and op(u, a2(v), d + 1) == v:
        PROF[(u, v)] = 'F'; return F(u, v)
    if tg(v) != 1:
        PROF[(u, v)] = 'E'; return E(u, v)
    PROF[(u, v)] = None
    return J(u, v)

def chain(x, y, z):
    P = op(x, y); Q = op(x, P); A = op(z, y); C = op(A, Q); R = op(y, C)
    return P, Q, A, C, R
def prof(x, y, z):
    P, Q, A, C, R = chain(x, y, z)
    g = lambda a, b: PROF.get((a, b)) or '.'
    return (g(x, y), g(x, P), g(z, y), g(A, Q), g(y, C))
def enc(y, x, z):
    return op(op(z, y), op(x, op(x, y)))


CTORS = ('J', 'E', 'F')
def pairs(x, y, z):
    P = op(x, y); Q = op(x, P); A = op(z, y); C = op(A, Q)
    return [(x, y), (x, P), (z, y), (A, Q), (y, C)]

def terms(maxsize, gens, cons=('J', 'E', 'F')):
    by = {1: [G(i) for i in range(gens)]}
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

def sweep(name, gen, N):
    bad = []; cells = {}; n = 0
    for x, y, z in gen:
        n += 1
        try:
            pr = prof(x, y, z); r = chain(x, y, z)[4]
        except RecursionError:
            bad.append((x, y, z)); continue
        c = cells.setdefault(pr, [0, 0]); c[0] += 1
        if r != x: c[1] += 1; bad.append((x, y, z))
        if n >= N: break
    print('  %-30s n=%-8d BAD=%-6d cells=%d' % (name, n, len(bad), len(cells)), flush=True)
    for k in sorted(cells, key=lambda k: -cells[k][1])[:5]:
        if cells[k][1]:
            print('       %-18s %8d  %d bad' % (','.join(k), cells[k][0], cells[k][1]), flush=True)
    for x, y, z in sorted(bad, key=lambda t: sum(sz(q) for q in t))[:1]:
        print('     BAD prof=%s' % ','.join(prof(x, y, z)), flush=True)
        print('       x=%s' % show(x)[:100], flush=True); print('       y=%s' % show(y)[:100], flush=True)
        print('       z=%s -> %s' % (show(z)[:80], show(chain(x, y, z)[4])[:80]), flush=True)
    return len(bad)

def g_L1(ms, gens):
    pool = terms(ms, gens)
    for x in pool:
        for y in pool:
            for z in pool: yield x, y, z

def rt(rng, dd, gens):
    if dd <= 0 or rng.random() < 0.3: return G(rng.randrange(gens))
    return (rng.choice(('J', 'E', 'F')), rt(rng, dd - 1, gens), rt(rng, dd - 1, gens))

def g_deep(seed, maxd, gens):
    rng = random.Random(seed)
    while True: yield rt(rng, maxd, gens), rt(rng, maxd, gens), rt(rng, maxd, gens)

def g_H3(seed, gens):
    rng = random.Random(seed)
    while True:
        x = rt(rng, 2, gens); j = rt(rng, 2, gens); w = rt(rng, 2, gens)
        try: y = enc(j, w, x)
        except RecursionError: continue
        yield x, y, rt(rng, 2, gens)

def g_desc(levels, seed, bigjunk, gens):
    rng = random.Random(seed)
    small = [rt(rng, 2, gens) for _ in range(80)]
    big = [rt(rng, 6, gens) for _ in range(80)]
    junk = big if bigjunk else small
    while True:
        x = rng.choice(small); p = rng.choice(small)
        try:
            for _ in range(levels): p = enc(x, p, rng.choice(junk))
            y = enc(x, p, rng.choice(junk))
            if op(x, y) != p: continue
        except RecursionError: continue
        yield x, y, rng.choice(small + junk)

if __name__ == '__main__':
    SEP = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    L1 = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    print('=== 9663 SEP=%d (0=lab4, 1=a1 v!=u, 2=tg v!=4, 3=1+2, 4=1+F-anchor, 5=1+tg a2 Q!=1) ===' % SEP)
    tot = 0
    tot += sweep('L1 exh size<=%d 2gen' % L1, g_L1(L1, 2), 10 ** 9)
    for sd in (5, 19, 23):
        tot += sweep('deep seed=%d' % sd, g_deep(sd, 5, 3), 20000)
    for sd in (5, 19):
        tot += sweep('H3 (y = enc by x) seed=%d' % sd, g_H3(sd, 3), 20000)
    for lv in (0, 1, 2, 3):
        for bj in (False, True):
            tot += sweep('descent lv=%d bigjunk=%s' % (lv, bj), g_desc(lv, 7, bj, 3), 400)
    print('TOTAL BAD %d' % tot)
