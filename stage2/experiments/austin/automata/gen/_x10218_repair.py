# -*- coding: utf-8 -*-
"""Which dropped rule covers the forced-firing cell the 6-rule 10218 model misses?
Adds each of the 140 extracted rules to the 6 and re-runs the corrected forcing suite."""
import sys, os, itertools, collections, importlib.util
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'gen'))
import closedform as cf
from freemodel import normalise, catalog, size
from laws import parse_eq
law = normalise(parse_eq(catalog()[10218]))
spec = importlib.util.spec_from_file_location('chk', os.path.join(HERE, 'gen', 'rep10218', 'chk10218.py'))
src = open(spec.origin, encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {'__name__': 'chk'}; exec(compile(src, spec.origin, 'exec'), ns); R6 = ns['rules']
FULL = cf.Extractor(law).rules(exist=False)
def J(a, b): return ('J', a, b)
def g(n): return ('g', n)
def enc(P, u, Q): return J(J(P, u), J(J(Q, P), u))
base = [g(0), g(1), g(2), J(g(0), g(1)), J(g(1), g(2))]
def suite(R):
    """the corrected forced-firing cases; returns (n, fails)"""
    C = cf.Closed(law, R); op = C.op
    n = 0; f = 0
    def run(x, y, z):
        nonlocal n, f
        try:
            t1 = op(x, y); t2 = op(z, x); t3 = op(t2, y); t4 = op(t1, t3); t5 = op(y, t4)
        except RecursionError: return
        n += 1
        if t5 != x: f += 1
    for Pp, B, Q, u in itertools.product(base[:4], base[:3], base[:3], base[:3]):
        P = enc(Pp, B, Q); v = J(J(P, u), J(Pp, u))
        run(u, v, Q); run(v, base[0], u)
    for A2, P, Wt, Q in itertools.product(base[:3], base[:4], base[:3], base[:3]):
        m = J(A2, P); u = enc(Wt, m, Q); v = J(J(P, u), Wt)
        run(u, v, Q); run(v, base[0], u)
    for P, Q, u, D in itertools.product(base[:4], base[:3], base[:3], base[:3]):
        uu = enc(D, P, Q); v = J(op(P, uu), J(J(Q, P), uu))
        run(uu, v, Q); run(v, base[0], uu)
    for A1, Rp, Bq, Qq, A3 in itertools.product(base[:3], repeat=5):
        R_ = enc(Rp, Bq, Qq); u = J(J(A1, R_), A3); v = J(op(R_, u), J(Rp, u))
        run(u, v, Qq); run(v, base[0], u)
    for A, B, Cc, A1, A3 in itertools.product(base[:3], repeat=5):
        P = enc(A, B, Cc); Wv = op(B, P); u = J(J(A1, Wv), A3); v = J(J(P, u), op(Wv, u))
        run(u, v, Cc); run(v, base[0], u)
    return n, f
n0, f0 = suite(R6)
print('6-rule model: %d assignments, %d fails' % (n0, f0), flush=True)
tags6 = {r[2] for r in R6}
best = []
for i, r in enumerate(FULL):
    if r[2] in tags6: continue
    for pos in (1, len(R6)):          # try inserting early and late (rule order matters)
        R = R6[:pos] + [r] + R6[pos:]
        try: n, f = suite(R)
        except RecursionError: continue
        if f < f0:
            best.append((f, i + 1, r[2], pos, n))
best.sort()
print('rules that reduce the failures (fails, rule#, tag, insert-pos, n):')
for b in best[:12]: print('  ', b)
if not best: print('  NONE of the 134 dropped rules fixes it at either insertion point')
