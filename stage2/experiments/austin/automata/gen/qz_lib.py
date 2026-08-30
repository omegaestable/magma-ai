"""qz_lib.py -- a NON-free-magma carrier framework for the five 'identity laws'.

Carrier: an inductive type with several binary constructors (not just the free product).
`op` is defined by an ORDERED list of purely STRUCTURAL pattern rules (no nested `op` calls in
any guard), so `op` is a non-recursive function -- pattern matching + decidable equality.
That makes the Lean definition trivially terminating and the law provable by case analysis.

Terms: ('G', n) | (K, a, b) for K in the constructor alphabet.
"""
import sys, os, itertools, random, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.setrecursionlimit(100000)
from laws import parse_eq
from freemodel import catalog, normalise, pvars


def size(t):
    if len(t) == 1 or t[0] == 'G':
        return 1
    if len(t) == 2:
        return 1 + size(t[1])
    return 1 + size(t[1]) + size(t[2])


def show(t):
    if len(t) == 1:
        return t[0]
    if t[0] == 'G':
        return 'g%d' % t[1]
    if len(t) == 2:
        return '%s[%s]' % (t[0], show(t[1]))
    return '%s(%s,%s)' % (t[0], show(t[1]), show(t[2]))


CONST = []


def terms_upto(maxsize, gens, ctors, un=()):
    """all constructor terms of size <= maxsize over `gens` generators (binary `ctors`, unary `un`)."""
    by = {1: [('G', i) for i in range(gens)] + list(CONST)}
    for n in range(2, maxsize + 1):
        by.setdefault(n, [])
        for K in un:
            for s in by.get(n - 1, []):
                by[n].append((K, s))
        for a in range(1, n - 1):
            b = n - 1 - a
            for s in by.get(a, []):
                for t in by.get(b, []):
                    for K in ctors:
                        by[n].append((K, s, t))
    out = []
    for n in sorted(by):
        out += by[n]
    return out


def make_ev(op):
    def ev(p, s):
        if isinstance(p, str):
            return s[p]
        return op(ev(p[0], s), ev(p[1], s))
    return ev


def exhaustive(op, law, maxsize, gens, ctors, limit=20, un=()):
    vs = pvars(law[1])
    pool = terms_upto(maxsize, gens, ctors, un)
    ev = make_ev(op)
    fails = []
    n = 0
    for vals in itertools.product(pool, repeat=len(vs)):
        s = dict(zip(vs, vals))
        n += 1
        r = ev(law[1], s)
        if r != s[law[0]]:
            fails.append((s, r))
            if len(fails) >= limit:
                break
    return n, pool, fails


UN = []


def rand_term(depth, gens, ctors, rng):
    if depth <= 0 or rng.random() < 0.32:
        if CONST and rng.random() < 0.25:
            return rng.choice(CONST)
        return ('G', rng.randrange(gens))
    if UN and rng.random() < 0.2:
        return (rng.choice(UN), rand_term(depth - 1, gens, ctors, rng))
    K = rng.choice(ctors)
    return (K, rand_term(depth - 1, gens, ctors, rng), rand_term(depth - 1, gens, ctors, rng))


def subterms(t, acc=None):
    if acc is None:
        acc = []
    acc.append(t)
    if len(t) > 1 and t[0] != 'G':
        subterms(t[1], acc)
        if len(t) == 3:
            subterms(t[2], acc)
    return acc


def all_subpatterns(p, acc):
    if not isinstance(p, str):
        acc.append(p)
        all_subpatterns(p[0], acc)
        all_subpatterns(p[1], acc)
    return acc


def deep_tests(op, law, N, seed, gens=3, ctors=('P',), depth=3, verbose=False):
    """biased deep random tests: variables drawn from a growing pool that includes evaluations of
    the law's own subpatterns (critical-pair bait) and the model's own encodings."""
    rng = random.Random(seed)
    vs = pvars(law[1])
    ev = make_ev(op)
    subs = all_subpatterns(law[1], [])
    pool = []
    fails = []
    for i in range(N):
        s = {v: (rng.choice(pool) if pool and rng.random() < 0.55 else rand_term(depth, gens, ctors, rng)) for v in vs}
        r = rng.random()
        if r < 0.45:
            # make one variable be the evaluation of a law subpattern (the encodings)
            p = rng.choice(subs)
            s0 = {v: (rng.choice(pool) if pool and rng.random() < 0.5 else rand_term(depth, gens, ctors, rng)) for v in vs}
            for v in vs:
                if rng.random() < 0.4:
                    s0[v] = s[rng.choice(vs)]
            s[rng.choice(vs)] = ev(p, s0)
        elif r < 0.6 and len(vs) > 1:
            a, b = rng.sample(vs, 2)
            s[a] = s[b]
        elif r < 0.72 and pool:
            # a variable equal to a random subterm of another variable's value
            a, b = rng.sample(vs, 2)
            s[a] = rng.choice(subterms(s[b]))
        got = ev(law[1], s)
        if got != s[law[0]]:
            fails.append((s, got))
            if len(fails) >= 6:
                break
        for v in vs:
            if len(pool) < 400 and size(s[v]) <= 40:
                pool.append(s[v])
    return i + 1, fails


def closure_tests(op, law, N, seed, gens=3, ctors=('P',), depth=2):
    """closure fuzz: build the pool by repeatedly applying op to pool elements, then test."""
    rng = random.Random(seed)
    vs = pvars(law[1])
    ev = make_ev(op)
    pool = [('G', i) for i in range(gens)] + list(CONST)
    for _ in range(60):
        a, b = rng.choice(pool), rng.choice(pool)
        t = op(a, b)
        if size(t) <= 60:
            pool.append(t)
    fails = []
    for i in range(N):
        s = {v: rng.choice(pool) for v in vs}
        if rng.random() < 0.3:
            s[rng.choice(vs)] = rand_term(depth, gens, ctors, rng)
        got = ev(law[1], s)
        if got != s[law[0]]:
            fails.append((s, got))
            if len(fails) >= 6:
                break
    return i + 1, fails


def critical_tests(op, law, N, seed, gens=3, ctors=('P',), depth=2):
    """critical-pair fuzz: instantiate a variable with the value of the law's root pattern under a
    second, independent assignment sharing variables with the first."""
    rng = random.Random(seed)
    vs = pvars(law[1])
    ev = make_ev(op)
    fails = []
    for i in range(N):
        s0 = {v: rand_term(depth, gens, ctors, rng) for v in vs}
        s = {v: rand_term(depth, gens, ctors, rng) for v in vs}
        for v in vs:
            if rng.random() < 0.5:
                s0[v] = s[rng.choice(vs)]
        tgt = rng.choice(vs)
        s[tgt] = ev(law[1], s0)
        if rng.random() < 0.4:
            tgt2 = rng.choice(vs)
            s[tgt2] = ev(rng.choice(all_subpatterns(law[1], [])), s0)
        got = ev(law[1], s)
        if got != s[law[0]]:
            fails.append((s, got))
            if len(fails) >= 6:
                break
    return i + 1, fails


def law_of(eq):
    cat = catalog()
    return normalise(parse_eq(cat[eq])), cat[eq]


def refute_goal(op, goal, gens=3, ctors=('P',), tries=4000, seed=1, depth=2):
    """find an assignment where the goal equation FAILS."""
    rng = random.Random(seed)
    ev = make_ev(op)
    vs = pvars(goal[1]) + ([goal[0]] if isinstance(goal[0], str) and goal[0] not in pvars(goal[1]) else [])
    pool = terms_upto(3, gens, ctors, tuple(UN))
    for i in range(tries):
        if i < len(pool) ** 1:
            pass
        s = {v: rng.choice(pool) if rng.random() < 0.6 else rand_term(depth, gens, ctors, rng) for v in vs}
        lhs = ev(goal[0], s) if not isinstance(goal[0], str) else s[goal[0]]
        rhs = ev(goal[1], s)
        if lhs != rhs:
            return s, lhs, rhs
    return None


def identity_probe(op, law, gens=3, ctors=('P',), depth=3, seeds=(1, 2, 3), rounds=400):
    """The instances that killed models 15-18: x set to a CODE built by the model itself.

    For 12073-shaped laws (x = A * B) the dangerous x are the values of the law's own
    subpatterns under a second assignment, iterated: E_y = psi_y(y)*Sq(z), then x := E_y,
    x := psi_y(E_y)*Sq(z), and one more level.  A plain deep/critical fuzz never reaches
    them (they are size 20-60 terms with an exact internal shape).
    """
    ev = make_ev(op)
    vs = pvars(law[1])
    subs = all_subpatterns(law[1], [])
    fails = []
    n = 0
    for sd in seeds:
        rng = random.Random(sd)
        pool = [rand_term(depth, gens, ctors, rng) for _ in range(24)]
        pool += [('G', i) for i in range(gens)] + list(CONST)
        for _ in range(rounds):
            base = {v: rng.choice(pool) for v in vs}
            if rng.random() < 0.5:
                a, b = rng.sample(vs, 2)
                base[a] = base[b]
            cur = dict(base)
            for _lvl in range(3):
                p = rng.choice(subs)
                val = ev(p, cur)
                if size(val) > 4000:
                    break
                s = dict(base)
                s[rng.choice(vs)] = val
                if rng.random() < 0.5:
                    s[law[0]] = val
                n += 1
                got = ev(law[1], s)
                if got != s[law[0]]:
                    fails.append((s, got))
                    if len(fails) >= 5:
                        return n, fails
                cur = s
    return n, fails
