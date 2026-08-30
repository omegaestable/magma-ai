# -*- coding: utf-8 -*-
"""LEVEL-k DESCENT for 38316 (dualized L-form x = y*(x*((y*(z*x))*y))).
chain: a=op z x ; b=op y a ; c=op b y ; d=op x c ; top=op y d.
enc(u,P,Z) is the reading with op(u, enc(u,P,Z)) = P when every inner product is free:
    enc(u,P,Z) = J P (op (op u (op Z P)) u)
The shapes G1..G3 never build a chain whose decoder must descend THREE levels in the SAME
argument.  Here: nest enc inside its own payload k times, nest it inside its own u slot k times,
and combine, so that op(y,d), the b/c products, AND the products inside them all decode.
usage: _x38316_deep3.py [setname] [N]"""
import sys, os, random, itertools
sys.setrecursionlimit(100000)
from collections import Counter
D = r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, D)
import closedform as cf, leangen
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 38316
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = ('x', leangen.dual_pat(orig[1]))
GEN = D + '/gen/'
name = sys.argv[1] if len(sys.argv) > 1 else 'cand4'
src = open(GEN + 'chkrep38316.py', encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); ALL = ns['rules']
if name == 'all': RULES = ALL
elif name == 'v0': RULES = [r for r in ALL if r[2].startswith('V0')]
else:
    ns2 = {}; exec(open(GEN + '_x38316_rules_%s.py' % name, encoding='utf-8').read(), ns2); RULES = ns2['rules']
TAGS = [r[2] for r in RULES]
C = cf.Closed(law, RULES)
FIRED = {}
_oldop = cf.Closed.op
def _op(self, u, v):
    key = (u, v)
    if key in self.memo: return self.memo[key]
    r = _oldop(self, u, v)
    if key not in FIRED:
        w = -1
        for i, (co, xx, tg) in enumerate(self.rules):
            if self.check(co, u, v) and self.ev(xx, u, v) is not None:
                w = i; break
        FIRED[key] = w
    return r
cf.Closed.op = _op

print('set %s: %d rules' % (name, len(RULES)), flush=True)
J = lambda a, b: ('J', a, b)
g = lambda n: ('g', n)
def sh(t): return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (sh(t[1]), sh(t[2]))
def which(u, v):
    C.op(u, v)
    return FIRED.get((u, v), -1) if C.op(u, v) != J(u, v) else -1
def enc(u, P, Z):
    a = C.op(Z, P); b = C.op(u, a); c = C.op(b, u); return J(P, c)
def dec(u, v): return C.op(u, v) != J(u, v)

bad = []; cnt = Counter(); depths = Counter(); WIT = {}
def rec(x, y, z, fam):
    try:
        a = C.op(z, x); b = C.op(y, a); c = C.op(b, y); d = C.op(x, c); top = C.op(y, d)
    except RecursionError:
        return
    lv = sum(1 for (u, v) in ((z, x), (y, a), (b, y), (x, c), (y, d)) if dec(u, v))
    depths[lv] += 1
    pat = (which(z, x), which(y, a), which(b, y), which(x, c), which(y, d))
    cnt[pat] += 1
    WIT.setdefault(pat, (x, y, z, fam))
    if top != x: bad.append((x, y, z, fam, top))

G = [g(i) for i in range(5)]
small = G[:3] + [J(g(0), g(1)), J(g(1), g(2)), J(g(2), g(0))]

# ---- D1: payload nested k deep (the decoder must unwrap enc(enc(enc(...)))) ----
n = 0
for k in (1, 2, 3, 4):
    for y, Z in itertools.product(small, small):
        P = g(4)
        for _ in range(k):
            P = enc(y, P, Z)
            if size(P) > 3000: break
        else:
            if size(P) <= 3000:
                for zz in small:
                    rec(P, y, zz, 'D1k%d' % k); n += 1
print('D1 done (%d), failures %d' % (n, len(bad)), flush=True)

# ---- D2: the u-slot nested k deep: y is an encoding whose own u is an encoding, ... ----
n = 0
for k in (1, 2, 3):
    for u0, P0, Z in itertools.product(small[:4], small[:4], small[:3]):
        yy = u0
        for _ in range(k):
            yy = enc(yy, P0, Z)
            if size(yy) > 3000: break
        else:
            if size(yy) <= 3000:
                for zz in small[:3]:
                    for xx in [enc(yy, P0, Z), enc(yy, enc(yy, P0, Z), Z), P0]:
                        if size(xx) <= 6000:
                            rec(xx, yy, zz, 'D2k%d' % k); n += 1
print('D2 done (%d), failures %d' % (n, len(bad)), flush=True)

# ---- D3: THREE levels in the SAME argument: c decodes, its payload decodes, and that decodes ----
n = 0
for W1, W2, Z in itertools.product(G[:3], G[:3], small[:3]):
    for bcand in [g(0), J(g(0), g(1)), enc(g(0), g(1), g(2))]:
        y1 = enc(bcand, W1, Z)                      # c = op(b,y1) decodes to W1
        y2 = enc(bcand, enc(bcand, W1, Z), Z)       # ... and its payload is itself a reading
        y3 = enc(bcand, enc(bcand, enc(bcand, W1, Z), Z), Z)
        for yy in (y1, y2, y3):
            if size(yy) > 4000: continue
            for zz in small[:3]:
                for xx in [enc(yy, W2, zz), enc(yy, enc(yy, W2, zz), zz),
                           enc(yy, enc(yy, enc(yy, W2, zz), zz), zz),
                           J(J(yy, J(W2, zz)), yy)]:
                    if size(xx) <= 12000:
                        rec(xx, yy, zz, 'D3'); n += 1
print('D3 done (%d), failures %d' % (n, len(bad)), flush=True)

# ---- D4: randomized deep mixtures, large junk z, up to 4 nestings anywhere ----
random.seed(383163)
pool = list(small)
for _ in range(40):
    a1 = random.choice(pool); b1 = random.choice(pool); c1 = random.choice(pool)
    t = enc(a1, b1, c1)
    if size(t) <= 2000: pool.append(t)
n = 0
for _ in range(int(sys.argv[2]) if len(sys.argv) > 2 else 4000):
    y = random.choice(pool); z = random.choice(pool); P = random.choice(pool)
    x = enc(y, P, z)
    for _ in range(random.randint(0, 2)):
        x = enc(y, x, z)
        if size(x) > 20000: break
    if size(x) > 20000: continue
    rec(x, y, z, 'D4'); n += 1
print('D4 done (%d)' % n, flush=True)

print('=== instances %d, LAW FAILURES %d ===' % (sum(cnt.values()), len(bad)))
print('decoded-products-per-instance histogram:', dict(sorted(depths.items())))
for b in bad[:4]:
    print('  BAD [%s] x=sz%d y=sz%d z=sz%d top=sz%d' % (b[3], size(b[0]), size(b[1]), size(b[2]), size(b[4])))
    for nm, t in (('x', b[0]), ('y', b[1]), ('z', b[2])):
        print('    %s=%s' % (nm, sh(t) if size(t) < 260 else '<sz %d>' % size(t)))
print('=== patterns (a,b,c,d,top) ===')
for pat, c0 in sorted(cnt.items(), key=lambda kv: -kv[1])[:14]:
    print('  %-26s x%-7d %s' % (str(pat), c0, '|'.join((TAGS[i] if i >= 0 else 'free') for i in pat)))

import pickle
print('=== ALL patterns ===')
for pat, c0 in sorted(cnt.items(), key=lambda kv: -kv[1]):
    print('  %-28s x%-6d %s' % (str(pat), c0, '|'.join((TAGS[i] if i >= 0 else 'free') for i in pat)))
pickle.dump({k: v for k, v in WIT.items()}, open(GEN + '_z_wit.pkl', 'wb'))
print('witnesses dumped', len(WIT))
