# -*- coding: utf-8 -*-
"""Law 9663 carrier laboratory -- the 13764/12087 move (E-tag carrier).

Law (L-form):  x = y * ((z*y) * (x*(x*y)))
Chain:  P = x*y ; Q = x*P ; A = z*y ; C = A*Q ; goal  y*C = x.

Why the tag: the free-term models (gen/q9663*.py) all died on `inimg A u`, a structural
under-approximation of im(R_u) that every new witness rule enlarges (see NOTES_IDENTITY CORRECTION).
With a tag the junk slot A needs NO guard at all -- `E` is produced only by the model, so the root
recognises the code by its constructor instead of guessing membership of im(R_y).

  M ::= g n | J a b | E a b        tg: g->1, J->2, E->3;  a1/a2 total (identity on g).
  TAG  (u,v) is an (x,P) pair -- v = op u y for some y   ->  E u v         [certified by re-running]
  DEC  v = <J|E> A Q with tg Q = 3 and Q the code of a1 Q w.r.t. u  ->  a1 Q

Every recursive argument is a proper subterm of u or of v, so the Lean gate on sz u + sz v is
UNCONDITIONAL (the 27859 shape).

python gen/_x9663_lab.py [variant]
"""
import itertools, random, sys
sys.setrecursionlimit(100000)

TAG = {'g': 1, 'J': 2, 'E': 3}
def tg(t): return TAG[t[0]]
def a1(t): return t[1] if t[0] != 'g' else t
def a2(t): return t[2] if t[0] != 'g' else t
def sz(t): return 1 if t[0] == 'g' else sz(t[1]) + sz(t[2]) + 1
def J(a, b): return ('J', a, b)
def E(a, b): return ('E', a, b)
def G(n): return ('g', n)
def show(t, d=0):
    if t[0] == 'g': return 'g%d' % t[1]
    if d > 7: return '<%d>' % sz(t)
    return '%s(%s,%s)' % (t[0], show(t[1], d + 1), show(t[2], d + 1))

PROF = {}
VARIANT = 'v1'

def yc(v):
    """fixed-depth readings of the y that produced v = op u y."""
    out = []
    if tg(v) != 1: out.append(a2(v))
    return out

TAGV, DECV = 'T1', 'D1'

def TAGp(u, v, d):
    """(u,v) is an (x,P) pair of a law instance: v = op u y for some y."""
    if tg(v) == 1: return False
    if TAGV == 'T2': return True
    if TAGV == 'T3': return a1(v) == u
    if a1(v) != u: return False
    for y in yc(v):
        if op(u, y, d + 1) == v: return True
    return False

def xc(v):
    """fixed-depth readings of the payload x out of the code node Q (= a2 v)."""
    Q = a2(v)
    out = []
    if tg(Q) == 3: out.append(a1(Q))
    if DECV == 'D2' and tg(Q) == 2: out.append(a1(Q))
    if VARIANT == 'v2' and tg(Q) != 1 and tg(a1(Q)) == 3:
        out.append(a1(a1(Q)))          # second reading: Q's own first component is a tag
    return out

def DECv(u, v, d):
    """v = <J|E> A Q, Q the tagged code of x w.r.t. u: op x u = a2 Q."""
    if tg(v) == 1: return None
    Q = a2(v)
    if DECV == 'D1' and tg(Q) != 3: return None
    if DECV == 'D2' and tg(Q) == 1: return None
    for x in xc(v):
        if op(x, u, d + 1) == a2(Q):
            return x
    return None

R2ON = True

def R2(u, v, d):
    """the payload is not in v, it is inside u's own code -- READ IT OUT OF u, and certify by
    RE-RUNNING the encoding (the 13764 W6 lesson).  Every argument is a proper subterm of u, so the
    gate sz(arg1)+sz(arg2) < sz u <= sz u + sz v is UNCONDITIONAL."""
    if not R2ON: return None
    if tg(u) == 1: return None
    Q = a2(u)
    if tg(Q) != 3: return None
    P = a2(Q)
    if tg(P) != 3: return None
    p, x = a1(Q), a2(P)
    if op(p, x, d + 1) != P: return None          # certify P = op p x
    if op(x, p, d + 1) != a2(v): return None      # certify v's code component = op x p
    return x


def R3(u, v, d):
    """the shallower payload position: u = E p P' with P' = op p x, and v's code component is p.
    Both certification arguments are proper subterms of u -> unconditional gate."""
    if not R2ON: return None
    if tg(u) != 3: return None
    P = a2(u)
    if tg(P) != 3: return None
    p, x = a1(u), a2(P)
    if a2(v) != p: return None
    if op(p, x, d + 1) != P: return None
    return x


def op(u, v, d=0):
    if d > 60: return J(u, v)
    x = DECv(u, v, d)
    if x is not None:
        PROF[(u, v)] = 'D'; return x
    x = R2(u, v, d)
    if x is not None:
        PROF[(u, v)] = 'R'; return x
    x = R3(u, v, d)
    if x is not None:
        PROF[(u, v)] = 'S'; return x
    if TAGp(u, v, d):
        PROF[(u, v)] = 'T'; return E(u, v)
    PROF[(u, v)] = None
    return J(u, v)

def chain(x, y, z):
    P = op(x, y); Q = op(x, P); A = op(z, y); C = op(A, Q); R = op(y, C)
    return P, Q, A, C, R

def prof(x, y, z):
    P, Q, A, C, R = chain(x, y, z)
    g = lambda a, b: PROF.get((a, b)) or 'F'
    return (g(x, y), g(x, P), g(z, y), g(A, Q), g(y, C))

# ------------------------------------------------------------------ validators
def terms(maxsize, gens, cons=('J', 'E')):
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

def L1(maxsize=5, gens=2, limit=4):
    pool = terms(maxsize, gens); n = 0; bad = []; cells = {}
    for x in pool:
        for y in pool:
            for z in pool:
                n += 1
                try:
                    pr = prof(x, y, z); r = chain(x, y, z)[4]
                except RecursionError:
                    bad.append((x, y, z)); continue
                c = cells.setdefault(pr, [0, 0]); c[0] += 1
                if r != x:
                    c[1] += 1; bad.append((x, y, z))
    return n, bad, cells, pool

def deep(seed, N, maxd=5, gens=3):
    random.seed(seed); bad = []; cells = {}
    def rt(dd):
        if dd <= 0 or random.random() < 0.3: return G(random.randrange(gens))
        return (random.choice(('J', 'E')), rt(dd - 1), rt(dd - 1))
    for _ in range(N):
        x, y, z = rt(maxd), rt(maxd), rt(maxd)
        try:
            pr = prof(x, y, z); r = chain(x, y, z)[4]
        except RecursionError:
            bad.append((x, y, z)); continue
        c = cells.setdefault(pr, [0, 0]); c[0] += 1
        if r != x: c[1] += 1; bad.append((x, y, z))
    return bad, cells

def enc(y, x, z):
    """the law's RHS for this (x,y,z) -- must decode to x under y."""
    return op(op(z, y), op(x, op(x, y)))

def descent(levels, seed, N, bigjunk=False, gens=3):
    """level-k descent: nest x-encodings so the SAME rule descends k levels in one argument."""
    random.seed(seed)
    def rt(dd):
        if dd <= 0 or random.random() < 0.3: return G(random.randrange(gens))
        return (random.choice(('J', 'E')), rt(dd - 1), rt(dd - 1))
    small = [rt(2) for _ in range(80)]
    big = [rt(6) for _ in range(80)]
    junk = big if bigjunk else small
    bad = []; cells = {}; hits = 0
    for _ in range(N):
        x = random.choice(small)
        p = random.choice(small)
        try:
            for _ in range(levels):
                p = enc(x, p, random.choice(junk))
            y = enc(x, p, random.choice(junk))
            if op(x, y) != p: continue
            z = random.choice(small + junk)
            pr = prof(x, y, z); r = chain(x, y, z)[4]
        except RecursionError:
            continue
        hits += 1
        c = cells.setdefault(pr, [0, 0]); c[0] += 1
        if r != x: c[1] += 1; bad.append((x, y, z))
    return hits, bad, cells

def report(name, n, bad, cells):
    print('  %-34s n=%-8d BAD=%d   cells=%d' % (name, n, len(bad), len(cells)), flush=True)
    for k in sorted(cells, key=lambda k: -cells[k][0])[:6]:
        print('       %-24s %8d  %d bad' % (','.join(k), cells[k][0], cells[k][1]), flush=True)
    for x, y, z in bad[:2]:
        print('     BAD x=%s' % show(x)[:110], flush=True)
        print('         y=%s' % show(y)[:110], flush=True)
        print('         z=%s  -> %s' % (show(z)[:80], show(chain(x, y, z)[4])[:80]), flush=True)

if __name__ == '__main__':
    TAGV = sys.argv[1] if len(sys.argv) > 1 else 'T1'
    DECV = sys.argv[2] if len(sys.argv) > 2 else 'D1'
    R2ON = (len(sys.argv) < 4 or sys.argv[3] != 'noR2')
    print('=== 9663 E-carrier lab, TAG=%s DEC=%s R2=%s ===' % (TAGV, DECV, R2ON))
    n, bad, cells, pool = L1(5, 2)
    report('L1 exh size<=5 2gen (%d terms)' % len(pool), n, bad, cells)
    tot = len(bad)
    for sd in (5, 19, 23):
        b, c = deep(sd, 20000)
        report('deep seed=%d' % sd, 20000, b, c); tot += len(b)
    for lv in (0, 1, 2, 3):
        for bj in (False, True):
            h, b, c = descent(lv, 7, 300, bj)
            report('descent lv=%d bigjunk=%s' % (lv, bj), h, b, c); tot += len(b)
    print('TOTAL BAD %d' % tot)
