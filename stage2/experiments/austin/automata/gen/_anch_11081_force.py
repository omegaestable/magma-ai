"""PORTED ADVERSARY: every construction from the 11081 oracle suite, with every raw constructor
replaced by `op`, so that every term the adversary builds is IN THE IMAGE (= the anchored carrier).

If a construction still fails here, the anchored carrier does not remove it.
usage: python _anch_11081_force.py [ver] [wsize]"""
import sys, collections, itertools, random
sys.path.insert(0, '.')
sys.setrecursionlimit(100000)
from _x11081_lab4 import Model, chain, prof, terms, sz, show, g, J, E, F, K, D2, tg, a1, a2
from _anch_lib import image

VER   = sys.argv[1] if len(sys.argv) > 1 else 'v20'
WSIZE = int(sys.argv[2]) if len(sys.argv) > 2 else 4
M = Model(VER, fuel=10**9)
by, seen = image(M, ngens=3, wsize=WSIZE, cap=10**6, gmk=g)
pool = [t for s in sorted(by) for t in by[s]]
small = [t for s in sorted(by) if s <= 3 for t in by[s]]
print('VER=%s image total %d (small %d)' % (VER, len(pool), len(small)), flush=True)

tot = 0; fails = []; profs = collections.Counter(); built = collections.Counter()

def test(x, y, z, tag):
    global tot
    try:
        A, B, C, D, R = chain(M, x, y, z); p = prof(M, x, y, z)
    except RecursionError:
        return
    tot += 1; profs[(tag, p)] += 1
    if R != x:
        fails.append((tag, x, y, z, R, p))

def enc(u, p, j):
    """op-built encoding of payload p by decoder u, junk j.  Returns v with op(u,v)=p, or None."""
    try:
        inner = M.op(u, p)
        L = M.op(p, inner)
        Rr = M.op(j, u)
        v = M.op(L, Rr)
    except RecursionError:
        return None
    if a1(v) is not L or a2(v) is not Rr:
        if not (tg(v) != 1 and a1(v) == L and a2(v) == Rr):
            return None
    try:
        if M.op(u, v) != p:
            return None
    except RecursionError:
        return None
    return v

# ---------- P1: forceD ported --  z := op(q, op(B,q))
for x in small:
    for y in small:
        try:
            A = M.op(y, x); B = M.op(x, A)
        except RecursionError:
            continue
        for q in small[:8]:
            try:
                z = M.op(q, M.op(B, q))
            except RecursionError:
                continue
            built['P1'] += 1
            test(x, y, z, 'P1-forceD')

# ---------- P2: forceB2 ported -- z Cfree-decodable, y a branch-2 target
cnt = 0
for pz in small[:6]:
    for kz in small[:5]:
        for wz in small[:4]:
            z = enc(kz, pz, wz)
            if z is None:
                continue
            cnt += 1
            for P in small[:4]:
                try:
                    y = M.op(M.op(P, M.op(z, P)), pz)
                except RecursionError:
                    continue
                built['P2'] += 1
                for x in small[:6]:
                    test(x, y, z, 'P2-B2')
                    test(x, y, P, 'P2-B2b')
                    test(y, z, x, 'P2-B2c')
                    test(x, z, y, 'P2-B2d')
print('  P2: op-built Cfree-decodable z:', cnt, flush=True)

# ---------- P3: H3 ported -- y is a genuine encoding BY x
h3 = 0
for x in small[:8]:
    for p in small[:6]:
        for j in small[:4]:
            y = enc(x, p, j)
            if y is None:
                continue
            h3 += 1
            for z in small[:8]:
                test(x, y, z, 'P3-H3')
                test(p, y, z, 'P3-H3b')
                test(x, z, y, 'P3-H3c')
print('  P3: op-built encodings by x:', h3, flush=True)

# ---------- P4: level-k descent ported (nested encodings, same argument)
d = 0
for x in small[:5]:
    for p in small[:4]:
        for j in small[:3]:
            y1 = enc(x, p, j)
            if y1 is None: continue
            y2 = enc(x, y1, j)
            if y2 is None: continue
            y3 = enc(x, y2, j)
            d += 1
            for z in small[:6]:
                test(x, y2, z, 'P4-L2'); test(x, z, y2, 'P4-L2b')
                if y3 is not None:
                    test(x, y3, z, 'P4-L3'); test(x, z, y3, 'P4-L3b')
print('  P4: towers built:', d, flush=True)

# ---------- P5: random deep image terms
rng = random.Random(7)
deep = list(small)
for _ in range(3000):
    a = rng.choice(deep); b = rng.choice(deep)
    try:
        deep.append(M.op(a, b))
    except RecursionError:
        break
    if len(deep) > 900: deep = deep[-900:] + small
for _ in range(40000):
    test(rng.choice(deep), rng.choice(deep), rng.choice(deep), 'P5-deep')

print('TOTAL %d chains, %d FAILS  (built %s)' % (tot, len(fails), dict(built)))
bytag = collections.Counter(f[0] for f in fails)
print('  fails by construction:', dict(bytag))
firing = collections.Counter()
for (tag, p), n in profs.items():
    for i, b in enumerate(p):
        if b: firing[(tag, i, b)] += n
print('  per-construction branch firings (pos,branch):', dict(sorted(firing.items())))
fails.sort(key=lambda f: sz(f[1]) + sz(f[2]) + sz(f[3]))
for (tag, x, y, z, R, p) in fails[:3]:
    print('FAIL %s profile %s' % (tag, str(p)))
    for nm, t in (('x', x), ('y', y), ('z', z), ('R', R)):
        print('   %s (sz %d) = %s' % (nm, sz(t), show(t)[:220]))
