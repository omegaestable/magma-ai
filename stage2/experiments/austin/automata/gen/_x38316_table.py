"""Empirical case table for law 38316: for random law instances record which chain products
decoded and which rule fired at the top product."""
import sys, os, random
from collections import Counter
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, leangen
from freemodel import normalise, catalog, rand_term, size
from laws import parse_eq

EQ = 38316
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = ('x', leangen.dual_pat(orig[1]))

src = open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chkrep38316.py',
           encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); rules = ns['rules']
C = cf.Closed(law, rules)

def which(u, v):
    """index of the rule that fires on (u,v), or -1 for free"""
    for i, (conds, x, tag) in enumerate(C.rules):
        if C.check(conds, u, v):
            r = C.ev(x, u, v)
            if r is not None:
                return i
    return -1

def chain(x, y, z):
    s1 = C.op(z, x)
    s2 = C.op(y, s1)
    s3 = C.op(s2, y)
    s4 = C.op(x, s3)
    top = C.op(y, s4)
    pat = tuple(which(a, b) for a, b in ((z, x), (y, s1), (s2, y), (x, s3), (y, s4)))
    return pat, top, (s1, s2, s3, s4)

def J(a, b): return ('J', a, b)
def g(n): return ('g', n)

random.seed(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
N = int(sys.argv[2]) if len(sys.argv) > 2 else 4000
cnt = Counter(); ok = 0; bad = []
pool = [g(0), g(1), g(2), g(3)]
for it in range(N):
    if it % 3 == 0 and len(pool) > 6:
        x, y, z = random.sample(pool, 3)
    else:
        x = rand_term(random.randint(1, 4), 3); y = rand_term(random.randint(1, 4), 3); z = rand_term(random.randint(1, 4), 3)
    try:
        pat, top, inner = chain(x, y, z)
    except RecursionError:
        continue
    cnt[pat] += 1
    if top == x: ok += 1
    else: bad.append((x, y, z, pat))
    for t in inner:
        if size(t) < 40 and len(pool) < 400: pool.append(t)
print('ok', ok, 'of', N, 'bad', len(bad))
for pat, c in sorted(cnt.items(), key=lambda kv: -kv[1]):
    print('  (s1,s2,s3,s4,top) rules', pat, ' x%d' % c)
for b in bad[:5]:
    print(' BAD', b)
