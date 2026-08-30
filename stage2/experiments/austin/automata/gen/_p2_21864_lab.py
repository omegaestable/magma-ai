# -*- coding: utf-8 -*-
"""Law 21864 carrier laboratory -- the SEARCH DECODER (the 17286 move).

Law (L-form):  x = (y * (z * x)) * (x * (x * y))
Chain:  P = z*x ; U = y*P ; Q = x*y ; V = x*Q ; goal  U*V = x.

  decoder side (A-term) of t with key y, junk z :  AT(y,z,t) = op(y, op(z,t))
  encoding side (B-term) of t with key y        :  BT(t,y)   = op(t, op(t,y))
  the law is exactly                               op( AT(y,z,t), BT(t,y) ) = t

The free rule model is FALSE (gen/P2_MECHANISM.md 6): every finite rule list reads the A-side inner
product at a FIXED accessor depth, and the tower needs |l1,|l2,|l3,...  The fix, following
gen/NOTES_17286.md: keep the free carrier `M ::= g n | J a b` and SEARCH for the certificate.

The payload itself is easy here: BT(t,y) = op(t, ...) is free-outer in every reachable case, so the
candidate payload is `a1 v`.  What needs the search is the A-SIDE certificate: op(z,t) = a2 u for
SOME z, whose witness sits at an unbounded depth inside t.

usage: python gen/_p2_21864_lab.py [version] [--full]
"""
import itertools, random, sys, collections, time
sys.setrecursionlimit(100000)

VER = 'v1'
MAXD = 60


def tg(t):
    return 1 if t[0] == 'g' else 2


def a1(t):
    return t[1] if t[0] != 'g' else t


def a2(t):
    return t[2] if t[0] != 'g' else t


def sz(t):
    return 1 if t[0] == 'g' else sz(t[1]) + sz(t[2]) + 1


def J(a, b):
    return ('J', a, b)


def show(t, d=0):
    if t[0] == 'g':
        return 'g%d' % t[1]
    if d > 8:
        return '<%d>' % sz(t)
    return '(%s*%s)' % (show(t[1], d + 1), show(t[2], d + 1))


MEMO = {}
BR = collections.Counter()


def unwraps(t, k=8):
    """proper-subterm chain of candidate A-side targets: a1 t, a1 (a1 t), ..."""
    out = []
    c = t
    for _ in range(k):
        if tg(c) == 1:
            break
        c = a1(c)
        out.append(c)
    return out


def codesB(t, w):
    """t is a legal B-term for payload w:  t = BT(w, y') = op(w, op(w,y')) with the inner free.
    The free-inner shape pins y' = a2 (a2 t) and is a real certificate; a bare `a1 t = w` is NOT
    (17286's lesson: the certificate must re-run/shape-match the WHOLE encoding, not its head)."""
    return tg(t) != 1 and a1(t) == w and tg(a2(t)) != 1 and a1(a2(t)) == w


def codes(t, w, depth):
    """v5: t = BT(w,y') = op(w, op(w,y')) for SOME key y' -- the certificate must be RECURSIVE.
    y' is not determined by the pair, so search it over proper subterms of a2 t (17286's rule:
    candidates are projections and unwraps, and there is NO size cutoff on a candidate)."""
    if tg(t) == 1 or a1(t) != w:
        return False
    P = a2(t)
    cands = []
    if tg(P) != 1:
        cands.append(a2(P))
    c = P
    for _ in range(6):
        if tg(c) == 1:
            break
        c = a1(c)
        cands.append(c)
    for cc in cands:
        if op(w, cc, depth + 1) == P:
            BR['codes'] += 1
            return True
    return False


def okA(u, t, depth):
    """u = op(y, op(z,t)) for some z: certify the A-side inner product."""
    # (A0) the inner product is FREE:  a2 u = J z t
    if tg(a2(u)) != 1 and a2(a2(u)) == t:
        BR['A0'] += 1
        return True
    # (A1) the inner product DECODED to a2 u: then t must CODE a2 u, i.e. t = op(a2 u, ...)
    if VER in ('v1', 'v2') and tg(t) != 1 and a1(t) == a2(u):
        BR['A1'] += 1
        return True
    if VER in ('v3', 'v4') and codesB(t, a2(u)):
        BR['A1'] += 1
        return True
    if VER == 'v5' and codes(t, a2(u), depth):
        BR['A1'] += 1
        return True
    # (A2) unwraps: the decode of op(z,t) may itself have decoded, k levels deep
    if VER == 'v2':
        for c in unwraps(t):
            if c == a2(u):
                BR['A2'] += 1
                return True
    if VER in ('v3', 'v4', 'v5'):
        c = t
        for _ in range(8):
            if not codesB(c, a1(c)):
                break
            c = a1(c)
            if c == a2(u):
                BR['A2'] += 1
                return True
    return False


def op(u, v, depth=0):
    k = (u, v)
    r = MEMO.get(k)
    if r is not None:
        return r
    if depth > MAXD:
        return J(u, v)
    r = J(u, v)
    if tg(v) != 1:
        t = a1(v)
        X = a2(v)
        # ---- branch U : u is the FREE A-term  op(y, op(z,t)) with y = a1 u -------------------
        if tg(u) != 1 and op(t, a1(u), depth + 1) == X and okA(u, t, depth):
            BR['U'] += 1
            r = t
        # ---- branch A : the A-side product itself DECODED to u.  Then v must be the free
        #      B-term  J t (J t y), and the decode of op(y, op(z,t)) = u forces t to CODE u,
        #      i.e. a1 t = u -- or, k levels down, a1^k t = u.  (This is the As family:
        #      P7..P11 have NO tg u condition, which is what v1 was missing.)
        elif VER in ('v2', 'v4') and tg(X) != 1 and a1(X) == t and u in unwraps(t):
            BR['A'] += 1
            r = t
        elif VER in ('v3', 'v4') and tg(X) != 1 and a1(X) == t and codesB(t, u):
            BR['A'] += 1
            r = t
        elif VER == 'v5' and tg(X) != 1 and a1(X) == t and codes(t, u, depth):
            BR['A'] += 1
            r = t
    MEMO[k] = r
    return r


def ev(x, y, z):
    P = op(z, x)
    U = op(y, P)
    Q = op(x, y)
    V = op(x, Q)
    return op(U, V), (P, U, Q, V)


def rand_term(d, ng=3, rng=random):
    if d <= 0 or rng.random() < 0.35:
        return ('g', rng.randrange(ng))
    return J(rand_term(d - 1, ng, rng), rand_term(d - 1, ng, rng))


def terms_upto(ms, gens):
    by = {1: [('g', i) for i in range(gens)]}
    for n in range(3, ms + 1, 2):
        by[n] = []
        for a in range(1, n - 1, 2):
            b = n - 1 - a
            if b in by:
                for s in by[a]:
                    for t in by[b]:
                        by[n].append(J(s, t))
    out = []
    for n in sorted(by):
        out += by[n]
    return out


# ---------------------------------------------------------------- oracles
def descent(levels, variant, seed, bigjunk, N):
    """the level-k tower, both variants (gen/P2_MECHANISM.md 6.1)."""
    rng = random.Random(seed)
    small = [rand_term(rng.randint(1, 3), 2, rng) for _ in range(60)]
    big = [rand_term(rng.randint(5, 8), 3, rng) for _ in range(60)]
    junk = big if bigjunk else small
    cells = collections.Counter()
    bad = 0
    worst = None
    for _ in range(N):
        t = rng.choice(small)
        y = rng.choice(small)
        for _ in range(levels):
            t, y = op(y, op(rng.choice(junk), t)), op(t, op(t, y))
        if variant == 'A':
            x, yy, zz = t, y, rng.choice(junk)
        else:
            x, yy, zz = y, rng.choice(small), t
        r, (P, U, Q, V) = ev(x, yy, zz)
        cells[tuple('D' if a != b else 'F' for a, b in
                    ((P, J(zz, x)), (U, J(yy, P)), (Q, J(x, yy)), (V, J(x, Q))))] += 1
        if r != x:
            bad += 1
            tot = sz(x) + sz(yy) + sz(zz)
            if worst is None or tot < worst[0]:
                worst = (tot, x, yy, zz, r)
    return bad, cells, worst


def exhaustive(ms, gens, zcap=None):
    pool = terms_upto(ms, gens)
    zp = terms_upto(zcap, gens) if zcap else pool
    bad = 0
    n = 0
    worst = None
    for x in pool:
        for y in pool:
            for z in zp:
                n += 1
                r, _ = ev(x, y, z)
                if r != x:
                    bad += 1
                    tot = sz(x) + sz(y) + sz(z)
                    if worst is None or tot < worst[0]:
                        worst = (tot, x, y, z, r)
    return n, bad, worst


def deepco(seed, N):
    """deep random + coincidence: the pool is fed the model's own chain values."""
    rng = random.Random(seed)
    pool = [rand_term(rng.randint(1, 4), 3, rng) for _ in range(60)]
    bad = 0
    worst = None
    for _ in range(N):
        x, y, z = (rng.choice(pool) for _ in range(3))
        if rng.random() < 0.4:
            a, b = rng.sample([0, 1, 2], 2)
            v = [x, y, z]
            v[a] = v[b]
            x, y, z = v
        r, ch = ev(x, y, z)
        if r != x:
            bad += 1
            tot = sz(x) + sz(y) + sz(z)
            if worst is None or tot < worst[0]:
                worst = (tot, x, y, z, r)
        if len(pool) < 300:
            for c in ch + (r,):
                if sz(c) <= 60:
                    pool.append(c)
    return bad, worst


def forced(seed, N):
    """force each chain product to decode by construction, one at a time."""
    rng = random.Random(seed)
    small = [rand_term(rng.randint(1, 3), 2, rng) for _ in range(40)]
    bad = 0
    worst = None
    for _ in range(N):
        t = rng.choice(small)
        y = rng.choice(small)
        zj = rng.choice(small)
        A = op(y, op(zj, t))
        B = op(t, op(t, y))
        for (x, yy, zz) in ((t, y, zj), (B, rng.choice(small), A), (A, B, rng.choice(small)),
                            (t, B, A), (B, A, t)):
            r, _ = ev(x, yy, zz)
            if r != x:
                bad += 1
                tot = sz(x) + sz(yy) + sz(zz)
                if worst is None or tot < worst[0]:
                    worst = (tot, x, yy, zz, r)
    return bad, worst


def report(tag, bad, worst, extra=''):
    print('  %-34s BAD=%-5d %s' % (tag, bad, extra), flush=True)
    if worst:
        tot, x, y, z, r = worst
        print('      smallest: total=%d  x=%s' % (tot, show(x)[:90]), flush=True)
        print('                y=%s' % show(y)[:90], flush=True)
        print('                z=%s' % show(z)[:90], flush=True)
        print('                got=%s' % show(r)[:90], flush=True)


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    VER = args[0] if args else 'v1'
    full = '--full' in sys.argv
    t0 = time.time()
    print('=== 21864 search-decoder lab, %s ===' % VER, flush=True)
    tot = 0
    for va in ('A', 'B'):
        for lv in (0, 1, 2, 3):
            for bj in (False, True):
                b, cells, worst = descent(lv, va, 5 + 7 * lv, bj, 250)
                tot += b
                if b or (lv == 1 and not bj):
                    report('descent %s lv%d junk=%s' % (va, lv, 'big' if bj else 'small'), b, worst,
                           'cells=%s' % dict(list(cells.most_common(3))))
    print('  descent TOTAL BAD %d' % tot, flush=True)
    n, b, w = exhaustive(5, 2)
    report('exhaustive sz<=5 / 2 gen (%d)' % n, b, w)
    n, b, w = exhaustive(7, 1)
    report('exhaustive sz<=7 / 1 gen (%d)' % n, b, w)
    bd = 0
    for sd in (3, 4, 5):
        b, w = deepco(sd, 4000 if not full else 20000)
        bd += b
        if b:
            report('deep+coincidence seed %d' % sd, b, w)
    print('  deep+coincidence BAD %d' % bd, flush=True)
    b, w = forced(11, 400)
    report('forced firing', b, w)
    print('branches: %s' % dict(BR), flush=True)
    print('total %.1fs   memo %d' % (time.time() - t0, len(MEMO)), flush=True)
