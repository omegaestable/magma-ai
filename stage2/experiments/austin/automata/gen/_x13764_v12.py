"""Law 13764 model v12 = v11 with the W6 half of W56 DELETED, in the final Lean shape.

    op u v = if D u v then a1 (a1 v) else if Q v then E u v else J u v

D = W1 v W4 v W3 v W5 (all four return a1 (a1 v)); each is provably disjoint from Q,
so the branch order is irrelevant.

Includes the v11 counterexample as a regression control and a *generator* for its whole
family (the cell the samplers cannot reach).
"""
import random, sys

sys.setrecursionlimit(100000)


def tg(t):
    return 1 if t[0] == 'g' else (2 if t[0] == 'J' else 3)


def a1(t):
    return t[1] if t[0] != 'g' else t


def a2(t):
    return t[2] if t[0] != 'g' else t


def sz(t):
    return 1 if t[0] == 'g' else sz(t[1]) + sz(t[2]) + 1


def show(t, d=0):
    if t[0] == 'g':
        return 'g%d' % t[1]
    if d > 7:
        return '<%d>' % sz(t)
    return '%s(%s,%s)' % (t[0], show(t[1], d + 1), show(t[2], d + 1))


# ------------------------------------------------------------------ the model

def W1(u, v):
    return tg(v) == 2 and a2(v) == u and tg(a1(v)) == 3 and a2(a2(a1(v))) == u


def W4(u, v):
    return (tg(v) == 2 and a2(v) == u and tg(a1(v)) == 2
            and tg(a2(a1(v))) == 2 and a2(a2(a1(v))) == u)


def W3(u, v):
    return tg(v) == 3 and a2(v) == u and tg(a1(v)) == 2


def W5(u, v):
    return (tg(u) != 1 and a1(a1(u)) == a2(u) and tg(v) == 2
            and a2(v) == u and a2(a1(v)) == a2(u))


def D(u, v):
    return W1(u, v) or W4(u, v) or W3(u, v) or W5(u, v)


def Q(v):
    return tg(v) == 2 and tg(a1(v)) == 2 and a2(a1(v)) == a2(v)


def opL(u, v):
    if W1(u, v):
        return a1(a1(v)), 'W1'
    if W4(u, v):
        return a1(a1(v)), 'W4'
    if W3(u, v):
        return a1(a1(v)), 'W3'
    if W5(u, v):
        return a1(a1(v)), 'W5'
    if Q(v):
        return ('E', u, v), 'W2'
    return ('J', u, v), 'F'


def op(u, v):
    return opL(u, v)[0]


def chain(x, y, z):
    A, r1 = opL(z, y)
    B, r2 = opL(A, y)
    C, r3 = opL(x, B)
    Dd, r4 = opL(C, y)
    R, r5 = opL(y, Dd)
    return R, (r1, r2, r3, r4, r5), (A, B, C, Dd)


# ------------------------------------------------------------------ disjointness audit

def audit_disjoint(terms):
    bad = []
    for u in terms:
        for v in terms:
            if Q(v) and D(u, v):
                bad.append((u, v))
    return bad


# ------------------------------------------------------------------ pools

def gen_terms(maxsize, ngen):
    by = {1: [('g', i) for i in range(ngen)]}
    for n in range(2, maxsize + 1):
        out = []
        for i in range(1, n):
            j = n - 1 - i
            if j < 1:
                continue
            for a in by.get(i, ()):
                for b in by.get(j, ()):
                    out.append(('J', a, b))
                    out.append(('E', a, b))
        by[n] = out
    return [t for n in range(1, maxsize + 1) for t in by.get(n, ())]


def rand_term(rng, depth, ngen=3):
    if depth <= 0 or rng.random() < 0.32:
        return ('g', rng.randrange(ngen))
    c = 'J' if rng.random() < 0.6 else 'E'
    return (c, rand_term(rng, depth - 1, ngen), rand_term(rng, depth - 1, ngen))


PROFILES = {}
FAILS = []


def run(x, y, z):
    R, prof, mid = chain(x, y, z)
    PROFILES[prof] = PROFILES.get(prof, 0) + 1
    if R != x:
        FAILS.append((x, y, z, prof))


# ------------------------------------------------------------------ the case-tree family
# The v11 counterexample generalised: z a "self-decoder" (a1 (a1 z) = a2 z),
# y = J (c z W) z so that a2 y = z and a1 (a1 y) = z, x anything (esp. x = y).

def selfdecoders(pool):
    return [z for z in pool if tg(z) != 1 and a1(a1(z)) == a2(z)]


def case_tree_family(pool, wpool):
    """every (x,y,z) with a2 y = z, a1 (a1 y) = z, z a self-decoder — the v11 hole."""
    n = 0
    for z in selfdecoders(pool):
        for c in ('J', 'E'):
            for W in wpool:
                y = ('J', (c, z, W), z)
                for x in (y, z, W, ('g', 0), ('J', z, W), ('E', z, W), a2(z), a1(z)):
                    run(x, y, z)
                    n += 1
    return n


def encoded_family(pool, wpool):
    """x/y/z built so that each chain product in turn is forced to decode."""
    n = 0
    for y in pool:
        for zz in wpool:
            for x in (y, zz, a2(y), a1(a1(y)), ('g', 0)):
                run(x, y, a2(y))
                run(x, y, a1(a1(y)))
                run(x, y, zz)
                n += 3
    return n


if __name__ == '__main__':
    ts5 = gen_terms(5, 2)
    print('disjointness D vs Q over %d x %d pairs: %d violations'
          % (len(ts5), len(ts5), len(audit_disjoint(ts5))))

    # regression: the v11 counterexample
    g0, g1 = ('g', 0), ('g', 1)
    zc = ('J', ('J', g0, g1), g0)
    yc = ('J', ('J', zc, g1), zc)
    R, prof, mid = chain(yc, yc, zc)
    print('v11 counterexample under v12: profile %s  R == x ? %s' % (','.join(prof), R == yc))

    n = 0
    for y in ts5:
        for x in ts5:
            for z in ts5:
                run(x, y, z)
                n += 1
    print('L1 exhaustive size<=5 2gen: %d chains, %d fails' % (n, len(FAILS)))

    ts7 = gen_terms(7, 2)
    print('case-tree family over %d self-decoders x 2 x %d W x 8 x: %d chains, %d fails'
          % (len(selfdecoders(ts7)), len(ts5), case_tree_family(ts7, ts5), len(FAILS)))
    print('encoded family: %d chains, %d fails' % (encoded_family(ts7, ts5), len(FAILS)))

    tot = 0
    for seed in (101, 202, 303, 404, 505, 606):
        rng = random.Random(seed)
        for _ in range(20000):
            run(rand_term(rng, rng.randrange(6), 3), rand_term(rng, rng.randrange(6), 3),
                rand_term(rng, rng.randrange(6), 3))
            tot += 1
    print('L3 deep 6x20,000 depth<=5: %d chains, %d fails' % (tot, len(FAILS)))

    print('\nprofiles:')
    for p, c in sorted(PROFILES.items(), key=lambda kv: -kv[1]):
        print('  %-24s %d' % (','.join(p), c))
    if FAILS:
        print('\n!!! %d FAILURES' % len(FAILS))
        for (x, y, z, prof) in FAILS[:6]:
            R, _, (A, B, C, Dd) = chain(x, y, z)
            print('--- profile', ','.join(prof))
            print('  x =', show(x)); print('  y =', show(y)); print('  z =', show(z))
            for nm, val in (('A', A), ('B', B), ('C', C), ('D', Dd)):
                print('   %-3s = %s' % (nm, show(val)))
            print('  RESULT', show(R), 'expected', show(x))
    else:
        print('\nCLEAN')
