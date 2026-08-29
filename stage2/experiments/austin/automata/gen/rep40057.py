"""rep40057.py [N] : validate the repaired rule set for 40057 (L-form dual law x = y*(y*(x*((z*x)*y)))).

Hole: the generated rules R1-R4 assume the third product E = op x P1 of the evaluation is free; when
P1 = op P0 y is itself a decoded payload of the shape J x (...), E is decoded again and the payload x is
no longer at a1 (a2 v).  Repair: two rules that read v = J u E, u = J P0 (J P1 u3), P1 = J x _, and check
recursively  op x P1 = E,  op P0 u = P1,  and  P0 = op z x  (P0 = J z x, or P0 = op (a1 x) x).
"""
import sys, os, random, time
sys.path.insert(0, 'C:\\Users\\nacho\\Documents\\GitHub\\magma-ai\\stage2\\experiments\\austin\\automata')
import closedform as cf
from freemodel import normalise, catalog, size
from laws import parse_eq
from chk40057 import rules as rules4

def dual_pat(p):
    return p if isinstance(p, str) else (dual_pat(p[1]), dual_pat(p[0]))
orig = normalise(parse_eq(catalog()[40057]))
law = ('x', dual_pat(orig[1]))

sys.path.insert(0, 'C:\\Users\\nacho\\Documents\\GitHub\\magma-ai\\stage2\\experiments\\austin\\automata\\gen')
from rules6_40057 import rules6

def J(a, b): return ('J', a, b)
def g(n): return ('g', n)
def pp(t):
    if t[0] == 'g': return 'g%d' % t[1]
    return '(' + pp(t[1]) + ' ' + pp(t[2]) + ')'

def T(C, x, y, z):
    """the encoding of x by y via z: y * (x * ((z * x) * y)); the law says y * T = x"""
    return C.op(y, C.op(x, C.op(C.op(z, x), y)))

def lawval(C, x, y, z):
    return C.op(y, T(C, x, y, z))

def targeted(C, N, seed, maxsize=160):
    random.seed(seed)
    pool = [g(i) for i in range(5)]
    fails = []; tested = 0
    def add(t):
        if size(t) <= 80 and t not in pool: pool.append(t)
    for _ in range(N):
        a, b, c = (random.choice(pool) for _ in range(3))
        r = random.random()
        if r < 0.25:
            add(C.op(a, b))
        elif r < 0.6:
            add(T(C, a, b, c))
        elif r < 0.8:
            # the hole shape: y encodes P1 by P0 = op z x, P1 encodes w by x
            x, z, w, z1, z2 = (random.choice(pool) for _ in range(5))
            p0 = C.op(z, x); p1 = T(C, w, x, z2); y = T(C, p1, p0, z1)
            add(p1); add(y)
            if max(size(x), size(y), size(z)) <= maxsize:
                tested += 1
                v = lawval(C, x, y, z)
                if v != x: fails.append(((x, y, z), v))
        elif r < 0.9:
            # the R6 shape: additionally P0 = op z x is decoded (x encodes w0 by z)
            z, w0, w, z1, z2, z3 = (random.choice(pool) for _ in range(6))
            x = T(C, w0, z, z3); p0 = C.op(z, x); p1 = T(C, w, x, z2); y = T(C, p1, p0, z1)
            add(x); add(p1); add(y)
            if max(size(x), size(y), size(z)) <= maxsize:
                tested += 1
                v = lawval(C, x, y, z)
                if v != x: fails.append(((x, y, z), v))
        else:
            # deeper: x or z themselves encodings / products
            x, z = random.choice(pool), random.choice(pool)
            y = random.choice(pool)
            if random.random() < 0.5:
                p0 = C.op(z, x); y = T(C, random.choice(pool), p0, random.choice(pool)); add(y)
        if len(pool) > 4000: del pool[5:1000]
        # random law tests from the enriched pool
        x, y, z = (random.choice(pool) for _ in range(3))
        if random.random() < 0.2: y = x
        if random.random() < 0.1: z = x
        if max(size(x), size(y), size(z)) <= maxsize:
            tested += 1
            v = lawval(C, x, y, z)
            if v != x: fails.append(((x, y, z), v))
    return tested, fails

def report(name, C, tested, fails):
    print('%s: tested %d fails %d fired %s cycles %d' % (name, tested, len(fails), sorted(C.fired.items()), C.cycles))
    for (s, r) in fails[:3]:
        if isinstance(s, dict): x, y, z = s['x'], s['y'], s['z']
        else: x, y, z = s
        print('   FAIL x =', pp(x), ' y =', pp(y), ' z =', pp(z), ' ->', pp(r) if isinstance(r, tuple) else r)

N = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
sets = (('ORIGINAL R1-R4', rules4), ('REPAIRED R1-R6', rules6))
if len(sys.argv) > 2 and sys.argv[2] == 'rep': sets = sets[1:]
for name, rules in sets:
    print('=====', name, '=====')
    C = cf.Closed(law, rules)
    # the hand instance
    x = g(0); z = g(1); w = g(2)
    P1c = J(x, J(w, J(J(g(3), w), x))); P0c = J(z, x); y = J(P0c, J(P1c, J(J(g(4), P1c), P0c)))
    print('hand instance 1 (E decoded):', pp(lawval(C, x, y, z)), '== x', lawval(C, x, y, z) == x)
    # instance 2: y = P0 = J z xbig with u = J P0 g7 (R5 must fire on (P0, u))
    Eq = J(g(7), J(J(g(8), g(7)), g(5))); P1q = J(g(5), Eq); zq = J(g(6), g(5))
    xq = J(P1q, J(J(g(9), P1q), zq)); P0q = J(zq, xq)
    print('hand instance 2 (x=g5, y=P0, z=g6):', pp(lawval(C, g(5), P0q, g(6))), '== g5', lawval(C, g(5), P0q, g(6)) == g(5))
    t0 = time.time()
    for seed in (11, 12, 13):
        tested, fails = cf.deep_tests(C, law, N, 300, seed)
        report('deep_tests seed %d' % seed, C, tested, fails)
    import fuzz as fz
    for seed in (5, 6):
        t2, f2 = fz.fuzz(C, law, rules, 4 * N, seed=seed)
        report('fuzz seed %d' % seed, C, t2, f2)
    for seed in (1, 2, 3, 4):
        t3, f3 = targeted(C, 3 * N, seed)
        report('targeted seed %d' % seed, C, t3, f3)
    print('   time %.1fs' % (time.time() - t0))

print()
print('REPAIRED RULES:')
for i, r in enumerate(rules6):
    print('R%d %s' % (i + 1, cf.show_rule(r)))
print()
print('rules6 =', repr(rules6))
