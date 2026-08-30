"""Law 12234 model laboratory — the 13764 recipe applied to `x = y*(((z*x)*y)*(x*y))`.

WHY THIS FILE EXISTS.  `gen/rec12234.lean` is the extractor's free model: 6 rules, a 5,167 B
definition block with `msr` + `oc` + well-founded recursion, 8 sorries left, and a byte deficit of
~6-9 KB even when finished (see `gen/NOTES_12234.md`).  On law 13764 the same wall (67 rules,
54,402 B) was cleared not by minimising but by REPLACING THE CARRIER: a small term algebra with
extra constructors, total accessors, and pure shape tests.  That took 13764 to 13,949 B and three
accepted certificates.  This file is that lab for 12234.

Chain:  A = z*x ;  B = A*y ;  C = x*y ;  D = B*C ;  goal  y*D = x.

Note the shape difference from 13764: 12234 has TWO products with `y` on the right (`B = A*y` and
`C = x*y`) and combines them (`D = B*C`), where 13764 had a single left spine.  So the root reads
the payload through `a1` twice and then `a2`:  in the all-free case
    D = J (J (J z x) y) (J x y)      and      x = a2 (a1 (a1 D)) = a1 (a2 D).
It is readable through TWO independent paths, which is a genuine advantage over 13764 — a rule may
demand both and is then far harder to trigger accidentally.

Usage:  python gen/_x12234_lab.py            -- validate the current RULES
        python gen/_x12234_lab.py explain    -- print the chain of the first few failures
"""
import random, sys

sys.setrecursionlimit(100000)

CONS = ('J', 'E')                      # add more constructors here if a marking is needed
TAG = {'g': 1, 'J': 2, 'E': 3}


def tg(t):
    return TAG[t[0]]


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


# ------------------------------------------------------------------ rules
# Each rule is (name, fn(u, v) -> result or None).  First match wins; fall through to J u v.
# Keep every guard a PURE SHAPE TEST and every result a subterm or a constructor application:
# that is what keeps `op` non-recursive and the Lean definition block ~2 KB.

def R1(u, v):
    """the root read, all four chain products free:
       v = J (J (J z x) y) (J x y),  u = y   ->   x, confirmed on both paths."""
    if (tg(v) == 2 and tg(a1(v)) == 2 and tg(a1(a1(v))) == 2 and tg(a2(v)) == 2
            and a2(a1(v)) == u and a2(a2(v)) == u
            and a1(a2(v)) == a2(a1(a1(v)))):
        return a2(a1(a1(v)))
    return None


RULES = [('R1', R1)]


def mk_op(rules):
    def op(u, v):
        for nm, fn in rules:
            r = fn(u, v)
            if r is not None:
                return r
        return ('J', u, v)

    def opr(u, v):
        for nm, fn in rules:
            r = fn(u, v)
            if r is not None:
                return r, nm
        return ('J', u, v), 'F'
    return op, opr


def chain(opr, x, y, z):
    A, r1 = opr(z, x)
    B, r2 = opr(A, y)
    C, r3 = opr(x, y)
    D, r4 = opr(B, C)
    R, r5 = opr(y, D)
    return R, (r1, r2, r3, r4, r5), (A, B, C, D)


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
                    for c in CONS:
                        out.append((c, a, b))
        by[n] = out
    return [t for n in range(1, maxsize + 1) for t in by.get(n, ())]


def rand_term(rng, depth, ngen=3):
    if depth <= 0 or rng.random() < 0.32:
        return ('g', rng.randrange(ngen))
    return (CONS[rng.randrange(len(CONS))],
            rand_term(rng, depth - 1, ngen), rand_term(rng, depth - 1, ngen))


def validate(rules, explain_n=0):
    op, opr = mk_op(rules)
    profiles, fails = {}, []
    ts = gen_terms(5, 2)
    n = 0
    for y in ts:
        for x in ts:
            for z in ts:
                R, prof, mid = chain(opr, x, y, z)
                profiles[prof] = profiles.get(prof, 0) + 1
                if R != x:
                    fails.append((x, y, z, prof, mid, R))
                n += 1
    print('exhaustive size<=5 2gen (%d terms): %d chains, %d fails' % (len(ts), n, len(fails)))
    tot = 0
    for seed in (101, 202, 303):
        rng = random.Random(seed)
        for _ in range(20000):
            x = rand_term(rng, rng.randrange(6), 3)
            y = rand_term(rng, rng.randrange(6), 3)
            z = rand_term(rng, rng.randrange(6), 3)
            R, prof, mid = chain(opr, x, y, z)
            profiles[prof] = profiles.get(prof, 0) + 1
            if R != x:
                fails.append((x, y, z, prof, mid, R))
            tot += 1
    print('deep 3x20,000: %d chains, %d fails total' % (tot, len(fails)))
    print('profiles (top 15):')
    for p, c in sorted(profiles.items(), key=lambda kv: -kv[1])[:15]:
        print('  %-24s %d' % (','.join(p), c))
    seen = set()
    for (x, y, z, prof, mid, R) in fails:
        if prof in seen or len(seen) >= explain_n:
            continue
        seen.add(prof)
        print('--- FAIL profile', ','.join(prof))
        print('  x =', show(x)); print('  y =', show(y)); print('  z =', show(z))
        for nm, val in zip(('A=z*x', 'B=A*y', 'C=x*y', 'D=B*C'), mid):
            print('   %-6s = %s' % (nm, show(val)))
        print('  RESULT', show(R), 'expected', show(x))
    return fails


# ------------------------------------------------------------------ known holes (regressions)

def CE1():
    """R1 fires at A = op z x and destroys the payload.  sz x = 9, so no sweep of terms of
    size <= 5 can see it, and its guards are three simultaneous equalities, so no sampler can
    hit it either.  Found by construction (the case tree), 2026-08-29."""
    g0, g1, g2, g3 = [('g', i) for i in range(4)]
    z = g2
    x = ('J', ('J', ('J', g0, g1), z), ('J', g1, z))
    return (x, g3, z)


def regressions(rules):
    op, opr = mk_op(rules)
    out = []
    for nm, t in (('CE1', CE1()),):
        R, prof, mid = chain(opr, *t)
        out.append((nm, ','.join(prof), R == t[0]))
    return out


if __name__ == '__main__':
    for nm, prof, ok in regressions(RULES):
        print('%s: profile %-18s R == x ? %s' % (nm, prof, ok))
    validate(RULES, explain_n=6 if 'explain' in sys.argv else 0)
