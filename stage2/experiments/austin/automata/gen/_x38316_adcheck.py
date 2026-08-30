# -*- coding: utf-8 -*-
"""For every decoding pair (u,v) in a wide pool of cand6, which Adig branch holds?
Adig: (tg (a2 v) = 2 & a2 (a2 v) = u)  OR  a2 v = a1 u.
If the right branch never holds alone, the `law` cells can always use the left."""
import sys, itertools
from collections import Counter
D = r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, D)
import closedform as cf, leangen
from freemodel import normalise, catalog, size
from laws import parse_eq
law = ('x', leangen.dual_pat(normalise(parse_eq(catalog()[38316]))[1]))
ns = {}; exec(open(D + '/gen/_x38316_rules_cand6.py', encoding='utf-8').read(), ns)
C = cf.Closed(law, ns['rules'])
J = lambda a, b: ('J', a, b); g = lambda n: ('g', n)
def a1(t): return t[1] if t[0] == 'J' else t
def a2(t): return t[2] if t[0] == 'J' else t
def tg2(t): return t[0] == 'J'
MAX, NG = int(sys.argv[1]) if len(sys.argv) > 1 else 11, 2
by = {1: [g(i) for i in range(NG)]}
for n in range(3, MAX + 1, 2):
    by[n] = [J(s, t) for a in range(1, n - 1, 2) for s in by[a] for t in by.get(n - 1 - a, [])]
pool = [t for n in sorted(by) for t in by[n]]
print('pool %d' % len(pool), flush=True)
cnt = Counter(); ex = {}
for u in pool:
    for v in pool:
        if size(u) + size(v) > MAX + 6: continue
        if C.op(u, v) == J(u, v): continue
        L = tg2(a2(v)) and a2(a2(v)) == u
        R = a2(v) == a1(u)
        cnt[(L, R)] += 1
        ex.setdefault((L, R), (u, v))
print('Adig branch census over decoding pairs  (left, right):')
for k, c in sorted(cnt.items()):
    print('  left=%-5s right=%-5s  x%d' % (k[0], k[1], c))
print('RIGHT-ONLY instances:', cnt.get((False, True), 0), ' NEITHER:', cnt.get((False, False), 0))
