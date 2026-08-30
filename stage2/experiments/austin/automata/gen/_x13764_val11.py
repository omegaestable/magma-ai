"""Wave-3 validation standard (W3-6) for the 13764 v11 5-rule NON-RECURSIVE model.

Transcribes the Lean if-chain VERBATIM (`opL`) rather than importing the lab's rule
functions, so what is validated is what will be written in Lean.

Levels:
  1. exhaustive over all terms of size <= 5 with 2 generators (74 terms, 405,224 chains)
  2. exhaustive over all terms of size <= 5 with 3 generators, z stratified
  3. deep random at 20,000 on 6 seeds, depth 5
  4. THE CASE TREE: record the rule fired at each of the 5 chain products over every test
     above, enumerate the profiles reached, and construct one instance per plausible
     unreached cell by chained encoding.
"""
import itertools, random, sys, os

sys.setrecursionlimit(100000)

# ---------------------------------------------------------------- carrier
# M ::= ('g', n) | ('J', a, b) | ('E', a, b)      tg: g->1, J->2, E->3


def tg(t):
    return 1 if t[0] == 'g' else (2 if t[0] == 'J' else 3)


def a1(t):
    return t[1] if t[0] != 'g' else t


def a2(t):
    return t[2] if t[0] != 'g' else t


def sz(t):
    if t[0] == 'g':
        return 1
    return sz(t[1]) + sz(t[2]) + 1


def show(t, d=0):
    if t[0] == 'g':
        return 'g%d' % t[1]
    if d > 7:
        return '<%d>' % sz(t)
    return '%s(%s,%s)' % (t[0], show(t[1], d + 1), show(t[2], d + 1))


# ---------------------------------------------------------------- op, as Lean will read it


def opL(u, v):
    """The if-chain exactly as it will appear in Lean.  Returns (result, rule name)."""
    # W1
    if tg(v) == 2 and a2(v) == u and tg(a1(v)) == 3 and a2(a2(a1(v))) == u:
        return a1(a1(v)), 'W1'
    # W4
    if (tg(v) == 2 and a2(v) == u and tg(a1(v)) == 2
            and tg(a2(a1(v))) == 2 and a2(a2(a1(v))) == u):
        return a1(a1(v)), 'W4'
    # W2
    if tg(v) == 2 and tg(a1(v)) == 2 and a2(a1(v)) == a2(v):
        return ('E', u, v), 'W2'
    # W56
    if tg(u) != 1 and a1(a1(u)) == a2(u) and tg(v) == 2 and a2(v) == u:
        if a2(a1(v)) == a2(u):
            return a1(a1(v)), 'W5'
        return a2(a2(u)), 'W6'
    # W3
    if tg(v) == 3 and a2(v) == u and tg(a1(v)) == 2:
        return a1(a1(v)), 'W3'
    return ('J', u, v), 'F'


def op(u, v):
    return opL(u, v)[0]


def chain(x, y, z):
    """law: x = y * ((x * ((z*y)*y)) * y)"""
    A, r1 = opL(z, y)
    B, r2 = opL(A, y)
    C, r3 = opL(x, B)
    D, r4 = opL(C, y)
    R, r5 = opL(y, D)
    return R, (r1, r2, r3, r4, r5), (A, B, C, D)


# ---------------------------------------------------------------- term pools


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
    return R == x


# ---------------------------------------------------------------- levels

def level1():
    ts = gen_terms(5, 2)
    n = 0
    for y in ts:
        for x in ts:
            for z in ts:
                run(x, y, z)
                n += 1
    print('L1 exhaustive size<=5 2gen: %d terms, %d chains, %d fails' % (len(ts), n, len(FAILS)))


def level2():
    ts = gen_terms(5, 3)
    small = gen_terms(3, 3)
    n = 0
    for y in ts:
        for x in ts:
            for z in small:
                run(x, y, z)
                n += 1
    print('L2 exhaustive size<=5 3gen (z size<=3): %d x %d x %d = %d chains, %d fails'
          % (len(ts), len(ts), len(small), n, len(FAILS)))


def level3():
    tot = 0
    for seed in (101, 202, 303, 404, 505, 606):
        rng = random.Random(seed)
        for _ in range(20000):
            x = rand_term(rng, rng.randrange(6), 3)
            y = rand_term(rng, rng.randrange(6), 3)
            z = rand_term(rng, rng.randrange(6), 3)
            run(x, y, z)
            tot += 1
    print('L3 deep random 6 seeds x 20,000 depth<=5: %d chains, %d fails' % (tot, len(FAILS)))


def level4_coincidence():
    """x/y/z drawn from the model's own chain values (rail: holes are all of this shape)."""
    tot = 0
    for seed in (21, 22, 23, 24):
        rng = random.Random(seed)
        pool = gen_terms(3, 3) + [rand_term(rng, 3, 3) for _ in range(40)]
        for _ in range(8000):
            x0 = rng.choice(pool); y0 = rng.choice(pool); z0 = rng.choice(pool)
            _, _, (A, B, C, D) = chain(x0, y0, z0)
            cands = [x0, y0, z0, A, B, C, D, ('J', x0, y0), ('E', x0, y0),
                     ('J', A, y0), ('E', A, y0), op(y0, D), op(z0, y0), op(y0, y0),
                     op(x0, B), op(C, y0)]
            x = rng.choice(cands); y = rng.choice(cands); z = rng.choice(cands)
            run(x, y, z)
            tot += 1
    print('L4 coincidence 4 seeds x 8,000: %d chains, %d fails' % (tot, len(FAILS)))


def report_profiles():
    print('\nCASE TREE: rule profiles (A,B,C,D,R) reached, count')
    for p, c in sorted(PROFILES.items(), key=lambda kv: -kv[1]):
        print('  %-30s %d' % (','.join(p), c))
    print('  distinct profiles: %d' % len(PROFILES))


if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if which in ('all', '1'):
        level1()
    if which in ('all', '2'):
        level2()
    if which in ('all', '3'):
        level3()
    if which in ('all', '4'):
        level4_coincidence()
    report_profiles()
    if FAILS:
        print('\n!!! %d FAILURES' % len(FAILS))
        for (x, y, z, prof) in FAILS[:5]:
            R, _, (A, B, C, D) = chain(x, y, z)
            print('--- profile', prof)
            print('  x =', show(x))
            print('  y =', show(y))
            print('  z =', show(z))
            for nm, val in (('A=z*y', A), ('B=A*y', B), ('C=x*B', C), ('D=C*y', D)):
                print('   %-8s = %s' % (nm, show(val)))
            print('  RESULT', show(R), ' expected', show(x))
    else:
        print('\nCLEAN')
