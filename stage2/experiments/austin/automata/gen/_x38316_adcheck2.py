# -*- coding: utf-8 -*-
"""Widened Adig-branch census: pool = all terms up to size 13 on 2 gens, PLUS encoding towers
(enc nested up to 3 deep) and their subterms.  Reports, over every decoding pair, whether
Adig-LEFT (tg (a2 v) = 2 & a2 (a2 v) = u) or only Adig-RIGHT (a2 v = a1 u) holds."""
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
a1 = lambda t: t[1] if t[0] == 'J' else t
a2 = lambda t: t[2] if t[0] == 'J' else t
tg2 = lambda t: t[0] == 'J'
def enc(u, P, Z):
    a = C.op(Z, P); b = C.op(u, a); c = C.op(b, u); return J(P, c)
MAX = int(sys.argv[1]) if len(sys.argv) > 1 else 13
by = {1: [g(0), g(1)]}
for n in range(3, MAX + 1, 2):
    by[n] = [J(s, t) for a in range(1, n - 1, 2) for s in by[a] for t in by.get(n - 1 - a, [])]
pool = [t for n in sorted(by) for t in by[n]]
base = [g(0), g(1), g(2), J(g(0), g(1)), J(g(1), g(2))]
tow = []
for u, P, Z in itertools.product(base[:4], base[:4], base[:3]):
    t = enc(u, P, Z)
    if size(t) <= 400: tow.append(t)
    t2 = enc(u, t, Z)
    if size(t2) <= 2000: tow.append(t2)
    t3 = enc(u, t2, Z)
    if size(t3) <= 8000: tow.append(t3)
sub = set()
def subs(t):
    sub.add(t)
    if t[0] == 'J': subs(t[1]); subs(t[2])
for t in tow: subs(t)
extra = [t for t in sub if size(t) <= 4000]
print('grid pool %d, towers %d, tower subterms %d' % (len(pool), len(tow), len(extra)), flush=True)
cnt = Counter(); rightonly = []
def scan(P, Q, cap):
    for u in P:
        for v in Q:
            if size(u) + size(v) > cap: continue
            try:
                if C.op(u, v) == J(u, v): continue
            except RecursionError:
                continue
            L = tg2(a2(v)) and a2(a2(v)) == u
            R = a2(v) == a1(u)
            cnt[(L, R)] += 1
            if not L: rightonly.append((u, v))
scan(pool, pool, MAX + 8)
scan(extra, extra, 9000)
scan(pool, extra, 9000)
scan(extra, pool, 9000)
print('Adig branch census over decoding pairs (left, right):')
for k, c in sorted(cnt.items()):
    print('  left=%-5s right=%-5s  x%d' % (k[0], k[1], c))
print('TOTAL decoding pairs:', sum(cnt.values()))
print('NOT-LEFT instances:', len(rightonly))
for u, v in rightonly[:3]:
    print('   u sz%d  v sz%d' % (size(u), size(v)))
