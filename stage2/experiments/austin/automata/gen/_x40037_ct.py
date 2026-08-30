"""Case-tree validation (W3-6) for the 4-rule 40037 model, plus an exhaustive small-term sweep.

The law's chain (L-form, dual of 40037):
    s1 = op(y,x)   s2 = op(s1,y)   s3 = op(z,s2)   s4 = op(x,s3)   s5 = op(z,s4) == x

`enc(x,y,z) = J x (J z (J (J y x) y))` is exactly the R1 (free-mode) encoding: op(z, enc(x,y,z)) = x.
Chained encoding builds instances that force a chosen product to DECODE, which random sampling
cannot reach (rail 50).

usage: _x40037_ct.py [rule idx csv, default 1,2,14,10] [N random combos]
"""
import sys, os, itertools, random, collections
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'gen'))
import closedform as cf, leangen, smallcheck as sc
from freemodel import normalise, catalog, size
from laws import parse_eq
import _x40037_rules as R

EQ = 40037
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = ('x', leangen.dual_pat(orig[1]))
idx = [int(i) for i in (sys.argv[1] if len(sys.argv) > 1 else '1,2,14,10').split(',')]
rules = [R.ALL[i - 1] for i in idx]
N = int(sys.argv[2]) if len(sys.argv) > 2 else 4000

C = cf.Closed(law, rules)


def J(a, b):
    return ('J', a, b)


def enc(x, y, z):
    """op(z, enc(x,y,z)) = x by rule R1 when everything is free"""
    return J(x, J(z, J(J(y, x), y)))


def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))


tab = collections.Counter()
bad = []
first = {}


def run(x, y, z):
    s1 = C.op(y, x)
    s2 = C.op(s1, y)
    s3 = C.op(z, s2)
    s4 = C.op(x, s3)
    s5 = C.op(z, s4)
    k = ('F' if s1 == J(y, x) else 'D', 'F' if s2 == J(s1, y) else 'D',
         'F' if s3 == J(z, s2) else 'D', 'F' if s4 == J(x, s3) else 'D',
         'F' if s5 == J(z, s4) else 'D')
    tab[k] += 1
    first.setdefault(k, (x, y, z))
    if s5 != x:
        bad.append(((x, y, z), k))
    return k


# ---- 1. exhaustive small terms -------------------------------------------------
pool = sc.terms_upto(9, 1) + sc.terms_upto(7, 2)
pool = list(dict.fromkeys(pool))
n = 0
for x, y, z in itertools.product(pool, repeat=3):
    try:
        run(x, y, z); n += 1
    except RecursionError:
        pass
print('exhaustive assignments', n, 'fails', len(bad), flush=True)

# ---- 2. chained encodings ------------------------------------------------------
base = [('g', 0), ('g', 1), ('g', 2), J(('g', 0), ('g', 1)), J(('g', 1), ('g', 0)),
        J(('g', 0), ('g', 0)), J(J(('g', 0), ('g', 1)), ('g', 2))]
lvl1 = []
for a, b, c in itertools.product(base, repeat=3):
    lvl1.append(enc(a, b, c))
lvl1 = list(dict.fromkeys(lvl1))
rng = random.Random(40037)
lvl2 = []
for _ in range(300):
    a = rng.choice(base + lvl1); b = rng.choice(base + lvl1); c = rng.choice(base + lvl1)
    t = enc(a, b, c)
    if size(t) <= 200:
        lvl2.append(t)

big = base + lvl1 + lvl2
print('pool sizes: base %d lvl1 %d lvl2 %d' % (len(base), len(lvl1), len(lvl2)), flush=True)

# 2a. targeted: x an encoding (forces s1 = op(y,x) to decode when y is x's z-role)
cnt = 0
for xe in lvl1:
    # xe = enc(a,b,c): op(c, xe) = a, so take y := c to decode s1
    a, rest = xe[1], xe[2]
    c = rest[1]
    b = rest[2][2]
    for z in base:
        try:
            run(xe, c, z); cnt += 1
        except RecursionError:
            pass
    for z in lvl1[:40]:
        try:
            run(xe, c, z); cnt += 1
        except RecursionError:
            pass
print('targeted s1-decode assignments', cnt, 'fails', len(bad), flush=True)

# 2b. targeted: y an encoding whose z-role is s1 (forces s2 to decode).  s1 = op(y,x);
#     when s1 is free s1 = J y x, so y must contain J y x -- impossible.  So try s1 decoded:
#     x = enc(a,b,y) gives s1 = a; then y = enc(p,q,a) gives s2 = op(a, y) = p.
cnt = 0
for a, b, p, q in itertools.product(base[:5], repeat=4):
    y = enc(p, q, a)
    x = enc(a, b, y)
    for z in base[:5]:
        try:
            run(x, y, z); cnt += 1
        except RecursionError:
            pass
print('targeted s2-decode assignments', cnt, 'fails', len(bad), flush=True)

# 2c. targeted: s3 = op(z, s2) decodes.  s2 = op(s1,y); free s2 = J s1 y, need
#     y = J z (J (J T s1) T) with s1 = op(y,x).  Use s1 decoded: x = enc(a,b,y) so s1 = a,
#     then y must be J z (J (J T a) T) -- but a is free of y, so pick a first.
cnt = 0
for a, T, z in itertools.product(base[:6], repeat=3):
    y = J(z, J(J(T, a), T))
    x = enc(a, ('g', 7), y)     # op(y, x) = a
    try:
        run(x, y, z); cnt += 1
    except RecursionError:
        pass
    # also with s1 free
    for b in base[:4]:
        try:
            run(b, y, z); cnt += 1
        except RecursionError:
            pass
print('targeted s3-decode assignments', cnt, 'fails', len(bad), flush=True)

# 2d. targeted: s4 = op(x, s3) decodes.  s3 free = J z s2, need s3 = J X (J x (J (J T X) T)),
#     i.e. z = X payload and s2 = J (J T z) T.  s2 = op(s1,y) free = J s1 y => s1 = J T z, y = T.
#     s1 = op(y,x) free = J y x => T = y and z = x.  So x = z, y arbitrary, T = y.
cnt = 0
for y, z in itertools.product(base, repeat=2):
    try:
        run(z, y, z); cnt += 1
    except RecursionError:
        pass
for y, z in itertools.product(lvl1[:30], base):
    try:
        run(z, y, z); cnt += 1
    except RecursionError:
        pass
print('targeted s4-decode assignments', cnt, 'fails', len(bad), flush=True)

# ---- 3. random over the encoding pool -----------------------------------------
cnt = 0
for _ in range(N):
    x = rng.choice(big); y = rng.choice(big); z = rng.choice(big)
    if size(x) + size(y) + size(z) > 400:
        continue
    try:
        run(x, y, z); cnt += 1
    except RecursionError:
        pass
print('random-encoding assignments', cnt, flush=True)

print()
print('%-24s %s' % ('(s1,s2,s3,s4,s5)', 'count'))
for k, c in sorted(tab.items(), key=lambda kv: -kv[1]):
    x, y, z = first[k]
    print('%-24s %-9d  x=%s' % (str(k), c, show(x)[:60]))
print('LAW FAILURES', len(bad))
for (x, y, z), k in bad[:5]:
    print('  ', k)
    print('    x =', show(x)[:200])
    print('    y =', show(y)[:200])
    print('    z =', show(z)[:200])
