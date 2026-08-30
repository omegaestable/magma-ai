"""Quotient-carrier models for the five 'identity laws' (12073, 27859, 21865, 21866, 22591).

Carrier: an inductive term algebra with an extra constant constructor E ('the square tag').
The point: every one of these five laws contains a subpattern in which a variable occurs ONLY as
a square (z*z) or as a doubled occurrence, and the law forces the value of the whole expression to
be independent of that variable.  On the free magma that is a derived identity between distinct
free terms, so no free-magma model exists.  Making op(u,u) = E by fiat kills the family at the
root: every square is literally the same element, so the "independent of z" requirement is
discharged definitionally and what is left is a 2-variable functional equation.

Terms: ('g',i) generator | ('E',) | ('J',u,v).
A model is a list of rules; rules are python closures (u, v, op) -> value or None, tried in order.
"""
import sys, os, itertools, random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.setrecursionlimit(20000)

E = ('E',)


UNARY = []          # names of unary constructors present in the carrier (e.g. ['Q'])


def sz(t):
    if t[0] == 'J':
        return 1 + sz(t[1]) + sz(t[2])
    if len(t) == 2 and t[0] in UNARY:
        return 1 + sz(t[1])
    return 1


def show(t):
    if t[0] == 'g':
        return 'g%d' % t[1]
    if t[0] == 'E':
        return 'E'
    if t[0] == 'J':
        return '(%s*%s)' % (show(t[1]), show(t[2]))
    return '%s[%s]' % (t[0], show(t[1]))


class Model:
    """op built from an ordered rule list.  Each rule is f(u, v, op) -> term or None."""

    def __init__(self, rules):
        self.rules = rules
        self.memo = {}

    def op(self, u, v):
        key = (u, v)
        r = self.memo.get(key)
        if r is not None:
            return r
        for f in self.rules:
            r = f(u, v, self.op)
            if r is not None:
                break
        else:
            r = ('J', u, v)
        self.memo[key] = r
        return r

    def ev(self, p, s):
        if isinstance(p, str):
            return s[p]
        return self.op(self.ev(p[0], s), self.ev(p[1], s))


# ---------------------------------------------------------------- test harness
def terms_upto(maxsize, gens, with_e=True):
    atoms = [('g', i) for i in range(gens)] + ([E] if with_e else [])
    by = {n: [] for n in range(1, maxsize + 1)}
    by[1] = list(atoms)
    for n in range(2, maxsize + 1):
        for c in UNARY:
            for s in by[n - 1]:
                by[n].append((c, s))
        for a in range(1, n - 1):
            b = n - 1 - a
            for s in by[a]:
                for t in by[b]:
                    by[n].append(('J', s, t))
    out = []
    for n in sorted(by):
        out += by[n]
    return out


def rand_term(d, ng=3, pe=0.2):
    if d <= 0 or random.random() < 0.35:
        return E if random.random() < pe else ('g', random.randrange(ng))
    if UNARY and random.random() < 0.3:
        return (random.choice(UNARY), rand_term(d - 1, ng, pe))
    return ('J', rand_term(d - 1, ng, pe), rand_term(d - 1, ng, pe))


def pvars(p, acc=None):
    if acc is None:
        acc = []
    if isinstance(p, str):
        if p not in acc:
            acc.append(p)
    else:
        pvars(p[0], acc)
        pvars(p[1], acc)
    return acc


def exhaustive(M, law, maxsize, gens, limit=30):
    vs = pvars(law[1])
    pool = terms_upto(maxsize, gens)
    fails = []
    n = 0
    for vals in itertools.product(pool, repeat=len(vs)):
        s = dict(zip(vs, vals))
        n += 1
        try:
            r = M.ev(law[1], s)
        except RecursionError:
            fails.append((s, 'recursion'))
            continue
        if r != s['x']:
            fails.append((s, r))
            if len(fails) >= limit:
                break
    return n, fails


def deep(M, law, N, seed, depth=3, ng=3, pool_extra=None):
    """random assignments, biased: values drawn from a growing pool of previously produced values
    and of law-subterm evaluations (critical-pair bait)."""
    random.seed(seed)
    vs = pvars(law[1])
    subs = []

    def collect(p):
        if not isinstance(p, str):
            subs.append(p)
            collect(p[0])
            collect(p[1])
    collect(law[1])
    pool = list(pool_extra or [])
    fails = []
    for i in range(N):
        s = {}
        for v in vs:
            if pool and random.random() < 0.45:
                s[v] = random.choice(pool)
            else:
                s[v] = rand_term(depth, ng)
        r = random.random()
        if r < 0.45:
            # set one variable to the evaluation of a law subterm under a random assignment
            p = random.choice(subs)
            s0 = {}
            for v in vs:
                s0[v] = s[random.choice(vs)] if random.random() < 0.5 else rand_term(depth, ng)
            try:
                s[random.choice(vs)] = M.ev(p, s0)
            except RecursionError:
                continue
        elif r < 0.65 and len(vs) > 1:
            a, b = random.sample(vs, 2)
            s[a] = s[b]
        try:
            got = M.ev(law[1], s)
        except RecursionError:
            fails.append((s, 'recursion'))
            continue
        if got != s['x']:
            fails.append((s, got))
            if len(fails) > 8:
                break
        if len(pool) < 400:
            for v in s.values():
                if sz(v) <= 40:
                    pool.append(v)
            if sz(got) <= 40:
                pool.append(got)
    return N, fails


def closure_fuzz(M, law, N, seed):
    """products of model values with model values: every value the model ever produces is fed back in."""
    random.seed(seed)
    vs = pvars(law[1])
    pool = [('g', 0), ('g', 1), ('g', 2), E]
    fails = []
    for i in range(N):
        s = {v: random.choice(pool) for v in vs}
        try:
            got = M.ev(law[1], s)
        except RecursionError:
            fails.append((s, 'recursion'))
            continue
        if got != s['x']:
            fails.append((s, got))
            if len(fails) > 8:
                break
        if len(pool) < 500:
            a, b = random.choice(pool), random.choice(pool)
            c = M.op(a, b)
            if sz(c) <= 60:
                pool.append(c)
            if sz(got) <= 60:
                pool.append(got)
    return N, fails


def critical_fuzz(M, law, N, seed):
    """x set to a full evaluation of the law's rhs on other values (rule/rule overlaps)."""
    random.seed(seed)
    vs = pvars(law[1])
    fails = []
    for i in range(N):
        s0 = {v: rand_term(2, 3) for v in vs}
        try:
            enc = M.ev(law[1], s0)
        except RecursionError:
            continue
        s = {v: rand_term(2, 3) for v in vs}
        tgt = random.choice(vs)
        s[tgt] = enc
        if random.random() < 0.5:
            s['x'] = enc
        try:
            got = M.ev(law[1], s)
        except RecursionError:
            fails.append((s, 'recursion'))
            continue
        if got != s['x']:
            fails.append((s, got))
            if len(fails) > 8:
                break
    return N, fails


def run_tests(M_factory, law, seeds=(3, 4, 5), Ndeep=20000, Nfuzz=12000, small=((9, 1), (5, 2))):
    out = []
    for ms, g in small:
        n, f = exhaustive(M_factory(), law, ms, g)
        out += [(s, r, 'exh%d/%d' % (ms, g), 0) for s, r in f]
    for sd in seeds:
        n, f = deep(M_factory(), law, Ndeep, sd)
        out += [(s, r, 'deep', sd) for s, r in f]
        n, f = closure_fuzz(M_factory(), law, Nfuzz, sd + 100)
        out += [(s, r, 'closure', sd) for s, r in f]
        n, f = critical_fuzz(M_factory(), law, Nfuzz, sd + 200)
        out += [(s, r, 'critical', sd) for s, r in f]
    return out
