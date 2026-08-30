"""Law 13764 model v15 = v14 with the Q branch BEFORE the W6 branch (makes Q disjoint from W).

    op u v =
      let r := if sz (a2 (a2 u)) + sz (a2 u) < sz u + sz v then op (a2 (a2 u)) (a2 u) else u
      if D u v            then a1 (a1 v)
      else if W u v ∧ r = a1 v then a2 (a2 u)
      else if Q v         then E u v
      else J u v
    D = W1 ∨ W4 ∨ W3 ∨ W5,  W = tg u ≠ 1 ∧ a1 (a1 u) = a2 u ∧ tg v = 2 ∧ a2 v = u

v11 (W6 total)                       FALSE (CE1)
v12 (W6 deleted)                     FALSE (CE2)
v13 (W6 guarded a1 v = a1(a1(a2 u))) FALSE (CE3 — the inner product itself decoded by W6)
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


def W(u, v):
    return tg(u) != 1 and a1(a1(u)) == a2(u) and tg(v) == 2 and a2(v) == u


def Q(v):
    return tg(v) == 2 and tg(a1(v)) == 2 and a2(a1(v)) == a2(v)


def opL(u, v):
    if sz(a2(a2(u))) + sz(a2(u)) < sz(u) + sz(v):
        r = op(a2(a2(u)), a2(u))
    else:
        r = u
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
    if W(u, v) and r == a1(v):
        return a2(a2(u)), 'W6'
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


def gate_audit(terms):
    """the W6 gate must follow from W's own guards (tg u != 1, tg v = 2, a2 v = u)."""
    bad = []
    for u in terms:
        for v in terms:
            if W(u, v) and not (sz(a2(a2(u))) + sz(a2(u)) < sz(u) + sz(v)):
                bad.append((u, v))
    return bad


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


# ---------------------------------------------------------- the three known holes

def CE1():
    g0, g1 = ('g', 0), ('g', 1)
    z = ('J', ('J', g0, g1), g0)
    y = ('J', ('J', z, g1), z)
    return (y, y, z)


def CE2():
    g0, g1, g2 = ('g', 0), ('g', 1), ('g', 2)
    z = ('J', ('E', g0, ('J', g1, g2)), g2)
    y = ('J', ('E', z, ('J', g0, z)), z)
    return (g2, y, z)


def CE3():
    g0, g1 = ('g', 0), ('g', 1)
    Wt = ('J', g0, g1)
    x = ('J', ('J', Wt, g1), Wt)
    z = ('J', g0, x)
    y = ('J', ('E', z, ('J', g1, z)), z)
    return (x, y, z)


def selfdec(pool):
    return [t for t in pool if tg(t) != 1 and a1(a1(t)) == a2(t)]


def fam_ce1(pool, wpool):
    n = 0
    for z in selfdec(pool):
        for c in ('J', 'E'):
            for Wt in wpool:
                y = ('J', (c, z, Wt), z)
                for x in (y, z, Wt, ('g', 0), ('J', z, Wt), ('E', z, Wt), a2(z), a1(z)):
                    run(x, y, z); n += 1
    return n


def fam_ce2(pool, wpool):
    n = 0
    for z in pool:
        for c in ('J', 'E'):
            for Wt in wpool:
                y = ('J', (c, z, Wt), z)
                for x in (a2(z), a1(a1(z)), a2(a2(z)), z, y, ('g', 0)):
                    run(x, y, z); n += 1
    return n


def fam_ce3(pool, wpool):
    """x a self-decoder, z = J (a1 (a1 (a2 x))) x so W6 can fire on (x,z); y encodes z."""
    n = 0
    for x in selfdec(pool):
        z = ('J', a1(a1(a2(x))), x)
        for c in ('J', 'E'):
            for Wt in wpool:
                y = ('J', (c, z, ('J', Wt, z)), z)
                run(x, y, z); n += 1
                y2 = ('J', (c, z, Wt), z)
                run(x, y2, z); n += 1
    return n


def fam_chainenc(pool, wpool):
    n = 0
    for y in pool:
        for w in wpool:
            for z in (a2(y), a1(a1(y)), w, a2(a2(y))):
                for x in (y, a2(z), a1(a1(z)), w, ('g', 0)):
                    run(x, y, z); n += 1
    return n


if __name__ == '__main__':
    ts5 = gen_terms(5, 2)
    ts7 = gen_terms(7, 2)
    print('W6 gate implied by W guards? violations over %d^2: %d' % (len(ts7), len(gate_audit(ts7))))
    for nm, t in (('CE1', CE1()), ('CE2', CE2()), ('CE3', CE3())):
        R, prof, _ = chain(*t)
        print('%s under v14: profile %-22s R == x ? %s' % (nm, ','.join(prof), R == t[0]))

    n = 0
    for y in ts5:
        for x in ts5:
            for z in ts5:
                run(x, y, z); n += 1
    print('L1 exhaustive size<=5 2gen: %d chains, %d fails' % (n, len(FAILS)))
    print('CE1 family: %d chains, %d fails' % (fam_ce1(ts7, ts5), len(FAILS)))
    print('CE2 family: %d chains, %d fails' % (fam_ce2(ts7, ts5), len(FAILS)))
    print('CE3 family: %d chains, %d fails' % (fam_ce3(ts7, ts5), len(FAILS)))
    print('chain-enc family: %d chains, %d fails' % (fam_chainenc(ts7, ts5), len(FAILS)))

    tot = 0
    for seed in (101, 202, 303, 404, 505, 606):
        rng = random.Random(seed)
        for _ in range(20000):
            run(rand_term(rng, rng.randrange(6), 3), rand_term(rng, rng.randrange(6), 3),
                rand_term(rng, rng.randrange(6), 3))
            tot += 1
    print('deep 6x20,000: %d chains, %d fails' % (tot, len(FAILS)))

    print('\nprofiles:')
    for p, c in sorted(PROFILES.items(), key=lambda kv: -kv[1]):
        print('  %-24s %d' % (','.join(p), c))
    if FAILS:
        print('\n!!! %d FAILURES' % len(FAILS))
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
            if len(seen) > 5:
                break
    else:
        print('\nCLEAN')
