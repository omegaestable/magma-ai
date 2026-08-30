"""Wave-3 validation of the 11081 E-carrier model: bigger exhaustive levels, the LEVEL-K DESCENT
(the key of the encoding is itself an encoding, k levels deep), large junk, and every rule forced at
every chain product.  usage: python gen/_x11081_val.py <ver>"""
import sys, random, collections, time
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen')
from _x11081_lab import (Model, chain, prof, terms, sz, show, g, J, E, tg, a1, a2)

VER = sys.argv[1] if len(sys.argv) > 1 else 'v1'
t0 = time.time()
tot = 0
fails = []
profs = collections.Counter()


def test(x, y, z, tag):
    global tot
    M = Model(VER)
    try:
        A, B, C, D, R = chain(M, x, y, z)
    except RecursionError:
        return
    tot += 1
    profs[prof(M, x, y, z)] += 1
    if R != x:
        fails.append((tag, x, y, z, R))


T7 = terms(7, 2)
T5 = terms(5, 2)
T3 = terms(3, 2)
print('pools: |T3|=%d |T5|=%d |T7|=%d' % (len(T3), len(T5), len(T7)), flush=True)

# L1 exhaustive over all terms of size <= 5, 2 generators
for x in T5:
    for y in T5:
        for z in T5:
            test(x, y, z, 'L1')
print('L1 %d chains %d fails %.0fs' % (tot, len(fails), time.time() - t0), flush=True)

# L2: one slot ranges over size <= 7
for y in T7:
    for x in T3:
        for z in T3:
            test(x, y, z, 'L2y')
for z in T7:
    for x in T3:
        for y in T3:
            test(x, y, z, 'L2z')
for x in T7:
    for y in T3:
        for z in T3:
            test(x, y, z, 'L2x')
print('L2 %d chains %d fails %.0fs' % (tot, len(fails), time.time() - t0), flush=True)

# ---- the LEVEL-K DESCENT ----
M0 = Model(VER)
enc = lambda p, u, w: E(E(p, M0.op(u, p)), E(w, u))     # op u (enc p u w) = p by R1
random.seed(20260829)


def rnd(d):
    if d == 0:
        return g(random.randrange(3))
    return random.choice([J, E, E])(rnd(d - 1), rnd(d - 1))


BIG = [rnd(3) for _ in range(5)] + [rnd(4) for _ in range(3)]
SM = T3
print('junk sizes:', sorted(sz(t) for t in BIG), flush=True)

# level k: key_0 = a small term; key_{i+1} = enc(p_i, key_i, w_i); test with y = key_k
keys = [SM[:4]]
for lvl in range(4):
    nxt = []
    for k in keys[-1]:
        for p in SM[:2]:
            for w in (SM[:2] + BIG[:1]):
                v = enc(p, k, w)
                if sz(v) <= 3000:
                    nxt.append((v, k))
    random.shuffle(nxt)
    nxt = nxt[:24]
    keys.append([v for v, _ in nxt])
    for (v, k) in nxt:
        for o in SM[:3] + BIG[:2]:
            test(o, v, k, 'lvl%d-y' % (lvl + 1))     # C = op(k,v) decodes; y is a level-(lvl+1) encoding
            test(o, k, v, 'lvl%d-z' % (lvl + 1))
            test(v, k, o, 'lvl%d-x' % (lvl + 1))
            test(v, o, k, 'lvl%d-x2' % (lvl + 1))
    print('  level %d: %d encodings, sizes %s ; %d chains %d fails %.0fs'
          % (lvl + 1, len(nxt), sorted(set(sz(v) for v, _ in nxt))[:5], tot, len(fails),
             time.time() - t0), flush=True)

# every chain product forced to decode in turn, with large junk everywhere
for p in SM[:3]:
    for u in SM[:3] + BIG[:2]:
        for w in SM[:2] + BIG[:3]:
            v = enc(p, u, w)
            if sz(v) > 600:
                continue
            for o in SM[:3] + BIG[:2]:
                test(o, v, u, 'F-y'); test(v, u, o, 'F-x'); test(o, u, v, 'F-z')
                test(v, o, u, 'F-x2'); test(u, v, o, 'F-u')
print('chain-forcing %d chains %d fails %.0fs' % (tot, len(fails), time.time() - t0), flush=True)

# deep random with both constructors
for seed in (3, 5, 7, 11, 13, 17):
    random.seed(seed)
    for _ in range(20000):
        test(rnd(random.choice([1, 2, 3])), rnd(random.choice([2, 3, 3])), rnd(random.choice([1, 2, 3])), 'deep')
print('TOTAL %d chains, %d FAILS  %.0fs' % (tot, len(fails), time.time() - t0))
print('profiles reached (%d):' % len(profs))
for k, n in profs.most_common(20):
    print('   ', k, n)
fails.sort(key=lambda f: sz(f[1]) + sz(f[2]) + sz(f[3]))
for (tag, x, y, z, R) in fails[:2]:
    M = Model(VER)
    A, B, C, D, Rr = chain(M, x, y, z)
    print('\nFAIL %s profile %s' % (tag, str(prof(M, x, y, z))))
    for nm, t in (('x', x), ('y', y), ('z', z), ('A', A), ('B', B), ('C', C), ('D', D), ('R', R)):
        print('  %s (sz %d) = %s' % (nm, sz(t), show(t)[:220]))
