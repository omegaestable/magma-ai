# -*- coding: utf-8 -*-
"""Session 9: check the session-9 9663 carrier against all FOUR target rows.

rows: 0018 (9663 -> 22818), 0051 (36487 -> 17522), 0098 (36487 -> 22818), 0093 (12294 -> 41082)
36487 is the DUAL of 9663, so it is checked on the dual magma op'(u,v) = op(v,u).
"""
import sys, os, random, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _s9_9663_lab5 as L

for a in sys.argv[1:]:
    if a.startswith('f:'): L.FEAT = set(x for x in a[2:].split(',') if x)
print('=== FEAT={%s} ===' % ','.join(sorted(L.FEAT)))

ROWS = [
    ('0018', 'x = y * ((z * y) * (x * (x * y)))', 'x = (y * (z * y)) * ((x * x) * y)', False),
    ('0051', 'x = (((y * x) * x) * (y * z)) * y', 'x = (y * z) * (x * (z * (z * z)))', True),
    ('0098', 'x = (((y * x) * x) * (y * z)) * y', 'x = (y * (z * y)) * ((x * x) * y)', True),
    ('0093', 'x = y * (((z * y) * x) * (x * y))', 'x = ((((y * y) * z) * x) * x) * z', False),
]


def parse_term(s):
    s = s.strip(); depth = 0
    for i, c in enumerate(s):
        if c == '(': depth += 1
        elif c == ')': depth -= 1
        elif c in '*' and depth == 0: return (parse_term(s[:i]), parse_term(s[i + 1:]))
    if s[0] == '(' and s[-1] == ')': return parse_term(s[1:-1])
    return s


def parse_eq(s):
    l, r = s.split('=')
    return parse_term(l), parse_term(r)


def ev(t, env, mul):
    if isinstance(t, str): return env[t]
    return mul(ev(t[0], env, mul), ev(t[1], env, mul))


def rt(rng, d, gens=3):
    if d <= 0 or rng.random() < .3: return L.G(rng.randrange(gens))
    return (rng.choice(('J', 'E', 'F')), rt(rng, d - 1, gens), rt(rng, d - 1, gens))


fwd = lambda a, b: L.op(a, b)
dua = lambda a, b: L.op(b, a)

pool5 = L.terms(3, 2) + L.terms(5, 2)[30:60]
rng = random.Random(7)
deeppool = [rt(rng, 5, 3) for _ in range(220)] + [L.G(i) for i in range(3)]

for rid, e1, e2, isdual in ROWS:
    mul = dua if isdual else fwd
    L1, R1 = parse_eq(e1); L2, R2 = parse_eq(e2)
    vs = 'xyz'
    # eq1 must HOLD: exhaustive over the size<=5 2-generator pool
    bad1 = 0; n1 = 0; w1 = None
    for x in pool5:
        for y in pool5:
            for z in pool5:
                env = {'x': x, 'y': y, 'z': z}
                try:
                    a = ev(L1, env, mul); b = ev(R1, env, mul)
                except RecursionError: continue
                n1 += 1
                if a != b:
                    bad1 += 1
                    if w1 is None: w1 = (x, y, z)
    # eq1 deep random
    bad1d = 0; n1d = 0
    for _ in range(20000):
        env = {v: rng.choice(deeppool) for v in vs}
        try:
            a = ev(L1, env, mul); b = ev(R1, env, mul)
        except RecursionError: continue
        n1d += 1
        if a != b: bad1d += 1
    # eq2 must FAIL somewhere: find the smallest witness
    w2 = None
    small = [L.G(0), L.G(1), L.G(2)] + L.terms(3, 2) + L.terms(5, 2)[:40]
    for x in small:
        for y in small:
            for z in small:
                env = {'x': x, 'y': y, 'z': z}
                try:
                    a = ev(L2, env, mul); b = ev(R2, env, mul)
                except RecursionError: continue
                if a != b:
                    w2 = (x, y, z, a, b); break
            if w2: break
        if w2: break
    print('row %s  dual=%-5s  eq1: exh %d/%d bad, deep %d/%d bad   eq2 witness: %s'
          % (rid, isdual, bad1, n1, bad1d, n1d,
             'NONE (eq2 HOLDS -- row is unusable)' if w2 is None else
             'x=%s y=%s z=%s  lhs=%s rhs=%s' % (L.show(w2[0])[:24], L.show(w2[1])[:24],
                                                L.show(w2[2])[:24], L.show(w2[3])[:34], L.show(w2[4])[:34])))
    if w1 is not None:
        print('     eq1 FAILS at x=%s y=%s z=%s' % (L.show(w1[0])[:40], L.show(w1[1])[:40], L.show(w1[2])[:40]))
