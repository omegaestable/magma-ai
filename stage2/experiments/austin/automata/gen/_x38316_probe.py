"""Targeted probe: can the chain products b = op y a, c = op b y, d = op x c ever decode for law 38316?

Builds the analytically-derived candidate instances and also brute-forces small (x,y,z) triples.
"""
import sys, os, itertools, random
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, leangen
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 38316
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = ('x', leangen.dual_pat(orig[1]))
src = open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chkrep38316.py',
           encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); rules = ns['rules']
TAGS = [r[2] for r in rules]
C = cf.Closed(law, rules)

def J(a, b): return ('J', a, b)
def g(n): return ('g', n)
def sh(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (sh(t[1]), sh(t[2]))

def which(u, v):
    for i, (conds, xx, tag) in enumerate(C.rules):
        if C.check(conds, u, v):
            r = C.ev(xx, u, v)
            if r is not None:
                return i
    return -1

def chain(x, y, z):
    a = C.op(z, x); b = C.op(y, a); c = C.op(b, y); d = C.op(x, c); top = C.op(y, d)
    return (which(z, x), which(y, a), which(b, y), which(x, c), which(y, d)), top, (a, b, c, d)

# --- analytic candidate: x = J (J y q) y with q = J w z and op w z free ---
print('--- analytic candidates ---')
for yi, wi, zi in itertools.product(range(3), repeat=3):
    y, w, z = g(yi), g(wi), g(zi)
    q = J(w, z)
    x = J(J(y, q), y)
    try:
        pat, top, inner = chain(x, y, z)
    except RecursionError:
        continue
    if pat[1:4] != (-1, -1, -1) or top != x:
        print('  y=%s w=%s z=%s x=%s  pat=%s top_ok=%s' % (sh(y), sh(w), sh(z), sh(x), pat, top == x))

# --- brute force over small terms ---
print('--- brute force ---')
terms = [g(0), g(1), g(2)]
for _ in range(3):
    new = list(terms)
    for a in terms:
        for b in terms:
            t = J(a, b)
            if size(t) <= 5 and t not in new:
                new.append(t)
    terms = new
terms = [t for t in terms if size(t) <= 5]
print('  %d terms of size <= 5' % len(terms))
found = {}
random.seed(0)
cnt = 0
for x in terms:
    for y in terms:
        for z in terms:
            if size(x) + size(y) + size(z) > 11:
                continue
            cnt += 1
            try:
                pat, top, inner = chain(x, y, z)
            except RecursionError:
                continue
            key = pat
            if key not in found:
                found[key] = (x, y, z, top == x)
print('  tried %d triples, %d distinct patterns' % (cnt, len(found)))
for k, v in sorted(found.items()):
    print('   ', k, [TAGS[i] if i >= 0 else 'free' for i in k], 'x=%s y=%s z=%s ok=%s' % (sh(v[0]), sh(v[1]), sh(v[2]), v[3]))
