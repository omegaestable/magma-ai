"""Law 13764 model v13.  v11's W6 restored but with a STRUCTURAL guard.

v11 (W6 total, fires whenever `a2 (a1 v) != a2 u`)  -> FALSE, counterexample CE1 below.
v12 (W6 deleted)                                    -> FALSE, counterexample CE2 below.
v13: W6 fires only when `a1 v = a1 (a1 (a2 u))`, i.e. when `a1 v` really is the value the
decoder produced from `a2 u`.  In CE1 that reads `J z g1 = g0` and is false; in CE2 it reads
`g0 = g0` and is true.

    op u v = if D u v then a1 (a1 v)
             else if W6 u v then a2 (a2 u)
             else if Q v   then E u v
             else J u v
    D = W1 v W4 v W3 v W5           (all four return a1 (a1 v))

All five decode guards are provably disjoint from Q, so only W5-before-W6 is order-sensitive.
Non-recursive: no `op` occurs in any guard or result.
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


def W6(u, v):
    return (tg(u) != 1 and a1(a1(u)) == a2(u) and tg(v) == 2
            and a2(v) == u and a1(v) == a1(a1(a2(u))))


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
    if W6(u, v):
        return a2(a2(u)), 'W6'
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


def audit_disjoint(terms):
    """Q must be disjoint from every decode guard, and W5 from W6."""
    bad = []
    for u in terms:
        for v in terms:
            if Q(v) and (D(u, v) or W6(u, v)):
                bad.append(('Q/D', u, v))
            if W5(u, v) and W6(u, v):
                bad.append(('W5/W6', u, v))
    return bad


# ------------------------------------------------------------------ the two known holes

def CE1():
    """v11's hole: z a self-decoder, y = J (J z g1) z, x = y."""
    g0, g1 = ('g', 0), ('g', 1)
    z = ('J', ('J', g0, g1), g0)
    y = ('J', ('J', z, g1), z)
    return (y, y, z)


def CE2():
    """v12's hole: A = B = z, C = op x z decodes, root needs W6."""
    g0, g1, g2 = ('g', 0), ('g', 1), ('g', 2)
    z = ('J', ('E', g0, ('J', g1, g2)), g2)
    y = ('J', ('E', z, ('J', g0, z)), z)
    return (g2, y, z)


def selfdecoders(pool):
    return [z for z in pool if tg(z) != 1 and a1(a1(z)) == a2(z)]


def family_ce1(pool, wpool):
    """all (x,y,z) with z a self-decoder, y = J (c z W) z (so a2 y = z, a1 (a1 y) = z)."""
    n = 0
    for z in selfdecoders(pool):
        for c in ('J', 'E'):
            for W in wpool:
                y = ('J', (c, z, W), z)
                for x in (y, z, W, ('g', 0), ('J', z, W), ('E', z, W), a2(z), a1(z)):
                    run(x, y, z)
                    n += 1
    return n


def family_ce2(pool, wpool):
    """all (x,y,z) with a2 y = z, a1 (a1 y) = z, x = a2 z (so op x z decodes)."""
    n = 0
    for z in pool:
        for c in ('J', 'E'):
            for W in wpool:
                y = ('J', (c, z, W), z)
                for x in (a2(z), a1(a1(z)), a2(a2(z)), z, y, ('g', 0)):
                    run(x, y, z)
                    n += 1
    return n


def family_chainenc(pool, wpool):
    """force each chain product in turn to decode: z = a2 y, z = a1 (a1 y), x = a2 z, x = y."""
    n = 0
    for y in pool:
        for w in wpool:
            for z in (a2(y), a1(a1(y)), w, a2(a2(y))):
                for x in (y, a2(z), a1(a1(z)), w, ('g', 0)):
                    run(x, y, z)
                    n += 1
    return n


if __name__ == '__main__':
    ts5 = gen_terms(5, 2)
    ts7 = gen_terms(7, 2)
    print('disjointness audit over %d^2 pairs: %d violations' % (len(ts5), len(audit_disjoint(ts5))))
    for nm, (x, y, z) in (('CE1', CE1()), ('CE2', CE2())):
        R, prof, _ = chain(x, y, z)
        print('%s under v13: profile %-22s R == x ? %s' % (nm, ','.join(prof), R == x))

    n = 0
    for y in ts5:
        for x in ts5:
            for z in ts5:
                run(x, y, z)
                n += 1
    print('L1 exhaustive size<=5 2gen (%d terms): %d chains, %d fails' % (len(ts5), n, len(FAILS)))

    print('CE1 family (%d self-decoders): %d chains, %d fails'
          % (len(selfdecoders(ts7)), family_ce1(ts7, ts5), len(FAILS)))
    print('CE2 family: %d chains, %d fails' % (family_ce2(ts7, ts5), len(FAILS)))
    print('chain-encoding family: %d chains, %d fails' % (family_chainenc(ts7, ts5), len(FAILS)))

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
        print('\n!!! %d FAILURES, %d distinct' % (len(FAILS), len(set(FAILS))))
        seen = set()
        for (x, y, z, prof) in FAILS:
            if prof in seen:
                continue
            seen.add(prof)
            R, _, (A, B, C, Dd) = chain(x, y, z)
            print('--- profile', ','.join(prof))
            print('  x =', show(x)); print('  y =', show(y)); print('  z =', show(z))
            for nm, val in (('A', A), ('B', B), ('C', C), ('D', Dd)):
                print('   %-3s = %s' % (nm, show(val)))
            print('  RESULT', show(R), 'expected', show(x))
            if len(seen) > 6:
                break
    else:
        print('\nCLEAN')
