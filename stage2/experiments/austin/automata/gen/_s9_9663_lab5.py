# -*- coding: utf-8 -*-
"""Law 9663 -- FOUR-constructor carrier, SESSION 9 variant lab.  x = y * ((z*y) * (x*(x*y)))
Chain: P = x*y ; Q = x*P ; A = z*y ; C = A*Q ; root y*C = x.

  M ::= g n | J a b | E a b | F a b        tg: g->1, J->2, E->3, F->4;  a1/a2 total.
  E = the (x,P) pair marker;  F = the CODE CONTAINER that the root reads.

Baseline (v0 == gen/_x9663_lab4.py, session 8's final):

  DEC   tg v != 1, tg (a2 v) = 4, op (a1 (a2 v)) u = a2 (a2 v)      ->  a1 (a2 v)
  R2    tg u != 1, ... payload out of u certified by re-running     ->  x
  TAGF  tg v != 1, a1 v = u, op u (a2 v) = v                        ->  F u v
  TAGE  tg v != 1                                                   ->  E u v
  else                                                              ->  J u v

v0's residual, measured session 9 (gen/_s9_9663_diag.py): 632 L1 fails at size<=5/2gen out of
3,944,312, from exactly FOUR (x,y) pairs -- x = g_b a generator and y = F(g_a, J(g_a, g_b)).
DEC misfires at the *Q* slot: v = P = op(x,y) so a2 v = y, and y being an F node with
op(a1 y, x) = a2 y makes the root's reading true one position too early.

VARIANTS (the separator candidates):
  v1  DEC also requires  tg (a1 v) != 1
  v2  v1 and also        a2 (a1 v) = u
  v3  DEC also requires  a1 v != u
  v4  DEC also requires  tg (a1 v) != 1  AND  tg (a2 (a2 v)) != 1
"""
import sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.setrecursionlimit(100000)
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
VAR = 'v0'


def R2(u, v, d):
    """payload out of u, certified by re-running the encoding (13764 W6); both args subterms of u."""
    if not R2ON or tg(u) == 1: return None
    if 'nur' in FEAT and (tg(v) == 1 or a1(v) == u): return None
    if 'v34r' in FEAT and tg(v) == 2: return None
    Q = a2(u)
    if tg(Q) == 1: return None
    P = a2(Q)
    if tg(P) == 1: return None
    p, x = a1(Q), a2(P)
    if 'rnv' in FEAT and x == v: return None
    if op(p, x, d + 1) != P: return None
    if op(x, p, d + 1) != a2(v): return None
    return x


FEAT = set()


def op(u, v, d=0):
    if d > 60: return J(u, v)
    if tg(v) != 1:
        Q = a2(v)
        # DEC.
        ok = tg(Q) == 4
        if ok and 'tg1' in FEAT and tg(a1(v)) == 1: ok = False
        if ok and 'a2u' in FEAT and a2(a1(v)) != u: ok = False
        if ok and 'nu' in FEAT and a1(v) == u: ok = False
        if ok and 'v34' in FEAT and tg(v) == 2: ok = False
        if ok and 'wf' in FEAT and not wf(v): ok = False
        if ok and op(a1(Q), u, d + 1) == a2(Q):
            PROF[(u, v)] = 'D'; return a1(Q)
    x = R2(u, v, d)
    if x is not None:
        PROF[(u, v)] = 'R'; return x
    if tg(v) != 1 and a1(v) == u and op(u, a2(v), d + 1) == v:
        PROF[(u, v)] = 'F'; return F(u, v)
    if 'noJ' in FEAT or tg(v) != 1:
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


def cons_set():
    return ('E', 'F') if 'noJ' in FEAT else ('J', 'E', 'F')


def terms(maxsize, gens, cons=None):
    cons = cons or cons_set()
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


def sweep(name, gen, N, quiet=False):
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
    if not quiet:
        for k in sorted(cells, key=lambda k: -cells[k][1])[:5]:
            if cells[k][1] or len(cells) <= 5:
                print('       %-18s %8d  %d bad' % (','.join(k), cells[k][0], cells[k][1]), flush=True)
        for x, y, z in sorted(bad, key=lambda t: sum(sz(q) for q in t))[:1]:
            print('     BAD prof=%s' % ','.join(prof(x, y, z)), flush=True)
            print('       x=%s' % show(x)[:100], flush=True); print('       y=%s' % show(y)[:100], flush=True)
            print('       z=%s -> %s' % (show(z)[:80], show(chain(x, y, z)[4])[:80]), flush=True)
    return len(bad), cells


def g_L1(ms, gens):
    pool = terms(ms, gens)
    for x in pool:
        for y in pool:
            for z in pool: yield x, y, z


def rt(rng, dd, gens):
    if dd <= 0 or rng.random() < 0.3: return G(rng.randrange(gens))
    return (rng.choice(cons_set()), rt(rng, dd - 1, gens), rt(rng, dd - 1, gens))


def g_deep(seed, maxd, gens):
    rng = random.Random(seed)
    while True: yield rt(rng, maxd, gens), rt(rng, maxd, gens), rt(rng, maxd, gens)


def g_H3(seed, gens):
    """H3: y is a GENUINE encoding by x -- y = enc(j, w, x), so x sits in the junk slot."""
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


def battery(full=False):
    tot = 0
    tot += sweep('L1 exh size<=%d 2gen' % (5 if full else 3), g_L1(5 if full else 3, 2), 10 ** 9)[0]
    for sd in (5, 19):
        tot += sweep('H3 seed=%d' % sd, g_H3(sd, 3), 20000 if full else 8000)[0]
    for sd in (5, 19, 23):
        tot += sweep('deep seed=%d' % sd, g_deep(sd, 5, 3), 20000 if full else 8000)[0]
    for lv in (0, 1, 2, 3):
        for bj in (False, True):
            tot += sweep('descent lv=%d bj=%s' % (lv, bj), g_desc(lv, 7, bj, 3), 400 if full else 300)[0]
    print('TOTAL BAD %d' % tot, flush=True)
    return tot


def wf(t):
    """structural under-approximation of 'op could have produced t'."""
    if t[0] == 'g': return True
    if t[0] == 'J': return tg(t[2]) == 1 and wf(t[1]) and wf(t[2])
    return wf(t[1]) and wf(t[2])


if __name__ == '__main__':
    for a in sys.argv[1:]:
        if a.startswith('f:'): FEAT = set(a[2:].split(','))
    VAR = ','.join(sorted(FEAT)) or 'v0'
    R2ON = 'noR2' not in sys.argv
    print('=== 9663 four-constructor carrier FEAT={%s} R2=%s ===' % (VAR, R2ON))
    battery('full' in sys.argv)
