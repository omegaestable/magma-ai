"""Law 13764 / 32294 model laboratory.

Law (normalised, L-form):   x = y * ((x * ((z * y) * y)) * y)
Chain:  A = z*y ;  B = A*y ;  C = x*B ;  D = C*y ;  goal  y*D = x.

The generated free-model package needs 67 rules (54,402 B of Lean definitions,
2.7x the 20,000 B certificate cap), so the free model is unshippable.  This file
searches for a SMALL, NON-RECURSIVE model over a multi-constructor term algebra:
every rule is a pure shape test on (u, v) and every result is a subterm or a
constructor application, so the Lean `op` needs no well-founded recursion, no
msr gate and no per-rule Decidable instance.

Terms:  ('g', n) | (C, a, b) for each binary constructor C in CONS.
Accessors are TOTAL, exactly as in Lean: a1/a2 of a generator is itself.
"""
import itertools, random, sys

CONS = ('J', 'E')          # binary constructors, in tag order
TAG = {'g': 1}
for i, c in enumerate(CONS):
    TAG[c] = i + 2


def tg(t):
    return TAG[t[0]]


def a1(t):
    return t[1] if t[0] != 'g' else t


def a2(t):
    return t[2] if t[0] != 'g' else t


def sz(t):
    return 1 if t[0] == 'g' else sz(t[1]) + sz(t[2]) + 1


def show(t, depth=0):
    if t[0] == 'g':
        return 'g%d' % t[1]
    if depth > 6:
        return '<%d>' % sz(t)
    return '%s(%s,%s)' % (t[0], show(t[1], depth + 1), show(t[2], depth + 1))


# ---------------------------------------------------------------- rule sets

def mk_op(rules):
    """rules: list of (name, fn(u,v)->result or None).  First match wins."""
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
                return (r, nm)
        return (('J', u, v), 'free')
    return op, opr


def chain(op, x, y, z):
    A = op(z, y)
    B = op(A, y)
    C = op(x, B)
    D = op(C, y)
    return op(y, D), (A, B, C, D)


def chain_r(opr, x, y, z):
    steps = []
    A, n1 = opr(z, y); steps.append(('A=z*y', A, n1))
    B, n2 = opr(A, y); steps.append(('B=A*y', B, n2))
    C, n3 = opr(x, B); steps.append(('C=x*B', C, n3))
    D, n4 = opr(C, y); steps.append(('D=C*y', D, n4))
    R, n5 = opr(y, D); steps.append(('R=y*D', R, n5))
    return R, steps


# ---------------------------------------------------------------- test suite

def gen_terms(maxsize, ngen=2):
    """all terms of size <= maxsize over ngen generators and CONS."""
    by = {1: [('g', i) for i in range(ngen)]}
    for n in range(2, maxsize + 1):
        out = []
        for i in range(1, n):
            j = n - 1 - i
            if j < 1:
                continue
            for a in by[i]:
                for b in by[j]:
                    for c in CONS:
                        out.append((c, a, b))
        by[n] = out
    return [t for n in range(1, maxsize + 1) for t in by[n]]


def rand_term(rng, depth, ngen=3):
    if depth <= 0 or rng.random() < 0.35:
        return ('g', rng.randrange(ngen))
    c = CONS[rng.randrange(len(CONS))]
    return (c, rand_term(rng, depth - 1, ngen), rand_term(rng, depth - 1, ngen))


def exhaustive(op, maxsize=3, ngen=2, limit=8):
    ts = gen_terms(maxsize, ngen)
    fails = []
    for y in ts:
        for x in ts:
            for z in ts:
                try:
                    r, _ = chain(op, x, y, z)
                except RecursionError:
                    continue
                if r != x:
                    fails.append((x, y, z))
                    if len(fails) >= limit:
                        return fails, len(ts)
    return fails, len(ts)


def deep(op, n, seed, depth=4, ngen=3, limit=8):
    rng = random.Random(seed)
    fails = []
    for _ in range(n):
        x = rand_term(rng, rng.randrange(depth + 1), ngen)
        y = rand_term(rng, rng.randrange(depth + 1), ngen)
        z = rand_term(rng, rng.randrange(depth + 1), ngen)
        try:
            r, _ = chain(op, x, y, z)
        except RecursionError:
            continue
        if r != x:
            fails.append((x, y, z))
            if len(fails) >= limit:
                break
    return fails


def coincidence(op, n, seed, limit=8):
    """targeted: build y/z/x out of the model's own chain values."""
    rng = random.Random(seed)
    fails = []
    pool = gen_terms(2, 3) + [rand_term(rng, 2, 3) for _ in range(30)]
    for _ in range(n):
        x0 = rng.choice(pool); y0 = rng.choice(pool); z0 = rng.choice(pool)
        _, (A, B, C, D) = chain(op, x0, y0, z0)
        cands = [x0, y0, z0, A, B, C, D, ('J', x0, y0), ('E', x0, y0),
                 op(y0, D), op(z0, y0), op(y0, y0)]
        x = rng.choice(cands); y = rng.choice(cands); z = rng.choice(cands)
        try:
            r, _ = chain(op, x, y, z)
        except RecursionError:
            continue
        if r != x:
            fails.append((x, y, z))
            if len(fails) >= limit:
                break
    return fails


def validate(rules, quiet=False, exh=3, ngen=2):
    op, opr = mk_op(rules)
    f1, nts = exhaustive(op, exh, ngen)
    f2 = deep(op, 4000, 11) + deep(op, 4000, 12) + deep(op, 4000, 13)
    f3 = coincidence(op, 4000, 21) + coincidence(op, 4000, 22)
    if not quiet:
        print('rules=%d  exhaustive(size<=%d,%dgen: %d terms) fails=%d  deep fails=%d  coincidence fails=%d'
              % (len(rules), exh, ngen, nts, len(f1), len(f2), len(f3)))
    return f1, f2, f3


def explain(rules, x, y, z):
    op, opr = mk_op(rules)
    R, steps = chain_r(opr, x, y, z)
    print('  x =', show(x))
    print('  y =', show(y))
    print('  z =', show(z))
    for nm, val, rule in steps:
        print('   %-8s = %-60s [%s]' % (nm, show(val), rule))
    print('  RESULT', show(R), ' expected', show(x))
