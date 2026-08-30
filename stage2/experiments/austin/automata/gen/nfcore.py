"""nfcore.py -- normal-form (confluent-rewrite) models for the five 'identity laws'.

Carrier: an inductive term type with EXTRA constructors beyond the free pair J, so that the
identities the law derives are already true on the nose between normal forms.  No quotient.

Terms are tuples:
    ('g', i)      generator i          sz = 1
    ('S',)        the square constant  sz = 1
    ('E', t)      unary tag            sz = 1 + sz t
    ('J', a, b)   free pair            sz = 1 + sz a + sz b

A model is a Python function op(u, v) -> term with memoisation.  Every recursive call inside op
is on a pair strictly smaller in `sz v` (structural on the second argument), so the Lean
definition is structurally recursive on v.

This module only holds the shared machinery (terms, enumerators, testers, goal refutation);
each law's op lives in nf<eq>.py.
"""
import sys, os, json, random, itertools, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.setrecursionlimit(100000)
from laws import parse_eq
from freemodel import catalog, pvars, normalise
import laws as _laws

S = ('S',)

_SZ = {}
def sz(t):
    r = _SZ.get(t)
    if r is None:
        k = t[0]
        if k == 'g' or k == 'S': r = 1
        elif k == 'E': r = 1 + sz(t[1])
        else: r = 1 + sz(t[1]) + sz(t[2])
        _SZ[t] = r
    return r

def show(t):
    k = t[0]
    if k == 'g': return 'g%d' % t[1]
    if k == 'S': return 'S'
    if k == 'E': return 'E(%s)' % show(t[1])
    return '(%s.%s)' % (show(t[1]), show(t[2]))

# ---------------------------------------------------------------- enumerators
def carrier_upto(maxsize, gens, use_S=True, use_E=True):
    """every term of the inductive type with sz <= maxsize."""
    by = {1: [('g', i) for i in range(gens)] + ([S] if use_S else [])}
    for n in range(2, maxsize + 1):
        cur = []
        if use_E:
            for t in by.get(n - 1, []): cur.append(('E', t))
        for a in range(1, n - 1):
            b = n - 1 - a
            for s in by.get(a, []):
                for t in by.get(b, []):
                    cur.append(('J', s, t))
        by[n] = cur
    out = []
    for n in sorted(by): out += by[n]
    return out

def jterms_upto(maxsize, gens):
    """the validator's classic pool: J-terms over generators only (no S, no E)."""
    return carrier_upto(maxsize, gens, use_S=False, use_E=False)

ALLOW_E = True

def rand_term(depth, gens=2, pS=0.12, pE=0.15):
    if not ALLOW_E: pE = 0.0
    r = random.random()
    if depth <= 0 or r < 0.30:
        if random.random() < pS: return S
        return ('g', random.randrange(gens))
    if r < 0.30 + pE: return ('E', rand_term(depth - 1, gens, pS, pE))
    return ('J', rand_term(depth - 1, gens, pS, pE), rand_term(depth - 1, gens, pS, pE))

# ---------------------------------------------------------------- law evaluation
def get_law(eq):
    """normalised L-form law ('x', pattern) for catalog id eq."""
    return normalise(parse_eq(catalog()[eq]))

def evaluator(op):
    def ev(p, s):
        if isinstance(p, str): return s[p]
        return op(ev(p[0], s), ev(p[1], s))
    return ev

# ---------------------------------------------------------------- tests
def exhaustive(op, law, pool, limit=40):
    ev = evaluator(op)
    vs = pvars(law[1]); fails = []; n = 0
    for vals in itertools.product(pool, repeat=len(vs)):
        s = dict(zip(vs, vals)); n += 1
        try:
            r = ev(law[1], s)
        except RecursionError:
            fails.append((dict(s), 'recursion')); continue
        if r != s['x']:
            fails.append((dict(s), r))
            if len(fails) >= limit: break
    return n, fails

def deep_random(op, law, N, seed, depth=4, gens=3, pool=None, limit=25):
    random.seed(seed)
    ev = evaluator(op)
    vs = pvars(law[1]); fails = []
    bag = list(pool) if pool else []
    for i in range(N):
        s = {}
        for v in vs:
            if bag and random.random() < 0.45: s[v] = random.choice(bag)
            else: s[v] = rand_term(random.randrange(1, depth + 1), gens)
        # coincidence bait: make a variable equal to another, or to an encoding
        r = random.random()
        if r < 0.25 and len(vs) > 1:
            a, b = random.sample(vs, 2); s[a] = s[b]
        elif r < 0.55:
            # a variable becomes the value of a subterm of the law under a fresh assignment
            s0 = {v: (random.choice(bag) if bag and random.random() < 0.5 else rand_term(random.randrange(1, 3), gens)) for v in vs}
            subs = []
            def coll(p):
                if not isinstance(p, str):
                    subs.append(p); coll(p[0]); coll(p[1])
            coll(law[1])
            try:
                val = ev(random.choice(subs), s0)
                s[random.choice(vs)] = val
            except RecursionError:
                pass
        try:
            got = ev(law[1], s)
        except RecursionError:
            fails.append((dict(s), 'recursion')); continue
        if got != s['x']:
            fails.append((dict(s), got))
            if len(fails) >= limit: break
        if bag is not None and len(bag) < 400:
            for v in s.values():
                if sz(v) <= 30: bag.append(v)
    return N, fails

def closure_random(op, law, N, seed, gens=3, limit=25):
    """closure fuzz: build the pool out of op-values of previous pool elements (the model's own
    reachable elements), then test the law on those."""
    random.seed(seed)
    ev = evaluator(op)
    vs = pvars(law[1])
    pool = [('g', i) for i in range(gens)] + [S]
    for _ in range(120):
        a, b = random.choice(pool), random.choice(pool)
        try: c = op(a, b)
        except RecursionError: continue
        if sz(c) <= 40 and c not in pool: pool.append(c)
    fails = []
    for i in range(N):
        s = {v: random.choice(pool) for v in vs}
        try: got = ev(law[1], s)
        except RecursionError:
            fails.append((dict(s), 'recursion')); continue
        if got != s['x']:
            fails.append((dict(s), got))
            if len(fails) >= limit: break
    return N, fails

def critical_random(op, law, N, seed, gens=3, limit=25):
    """critical-pair-shaped: one variable is set to the model's encoding of another variable's
    value (nested up to 3 deep), which is exactly where every hole found so far lived."""
    random.seed(seed)
    ev = evaluator(op)
    vs = pvars(law[1])
    A, B = law[1]
    fails = []
    for i in range(N):
        s = {v: rand_term(random.randrange(1, 4), gens) for v in vs}
        for _ in range(random.randrange(1, 4)):
            s0 = dict(s)
            for v in vs:
                if random.random() < 0.4: s0[v] = rand_term(random.randrange(1, 3), gens)
            try:
                enc = ev(B, s0)          # the 'encoding' side of the law
                encA = ev(A, s0)
            except RecursionError:
                break
            tgt = random.choice(vs)
            s[tgt] = enc if random.random() < 0.7 else encA
        try: got = ev(law[1], s)
        except RecursionError:
            fails.append((dict(s), 'recursion')); continue
        if got != s['x']:
            fails.append((dict(s), got))
            if len(fails) >= limit: break
    return N, fails

# ---------------------------------------------------------------- goals
def refute_goal(op, goal_eq, tries=40000, gens=3, seed=1):
    """find an assignment refuting the goal equation in this model."""
    random.seed(seed)
    ev = evaluator(op)
    l, r = goal_eq
    vs = sorted(set(pvars(l) if not isinstance(l, str) else [l]) | set(pvars(r) if not isinstance(r, str) else [r]))
    small = [('g', 0), ('g', 1), ('g', 2), S, ('E', ('g', 0)), ('J', ('g', 0), ('g', 1))]
    # first: exhaustive over a tiny pool
    for vals in itertools.product(small, repeat=len(vs)):
        s = dict(zip(vs, vals))
        try:
            a = s[l] if isinstance(l, str) else ev(l, s)
            b = s[r] if isinstance(r, str) else ev(r, s)
        except RecursionError:
            continue
        if a != b: return s, a, b
    for i in range(tries):
        s = {v: rand_term(random.randrange(1, 4), gens) for v in vs}
        try:
            a = s[l] if isinstance(l, str) else ev(l, s)
            b = s[r] if isinstance(r, str) else ev(r, s)
        except RecursionError:
            continue
        if a != b: return s, a, b
    return None
