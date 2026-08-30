"""Force rule R2 to fire at EVERY chain product of law 11081's chain (the coordinator's requirement 2),
and iterate the R2-encoding to level k (the level-k descent through the rule that does NOT store the key).

encR1(p,u,w) = E (E p (op u p)) (E w u)                 -- op u . = p by R1 ; key stored at a2(a2 v)
encR2(p,u)   = E (E p (op u p)) (op (a2(a2 u)) u)       -- op u . = p by R2 ; key NOT stored
   (encR2 needs u itself R1-decodable, i.e. u = encR1(...))
"""
import sys, random, collections, time
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen')
from _x11081_lab import Model, chain, prof, terms, sz, show, g, J, E, tg, a1, a2

VER = sys.argv[1] if len(sys.argv) > 1 else 'v1'
M0 = Model(VER)
encR1 = lambda p, u, w: E(E(p, M0.op(u, p)), E(w, u))
encR2 = lambda p, u: E(E(p, M0.op(u, p)), M0.op(a2(a2(u)), u))
T3 = terms(3, 2)
random.seed(20260829)


def rnd(d):
    if d == 0:
        return g(random.randrange(3))
    return random.choice([J, E, E])(rnd(d - 1), rnd(d - 1))


BIG = [rnd(3) for _ in range(4)]
tot = 0; fails = []; profs = collections.Counter()


def test(x, y, z, tag):
    global tot
    M = Model(VER)
    try:
        A, B, C, D, R = chain(M, x, y, z)
    except RecursionError:
        return
    tot += 1
    p = prof(M, x, y, z)
    profs[p] += 1
    if R != x:
        fails.append((tag, x, y, z, R, p))


# build R1-decodable keys, then R2-encodings on top of them, level by level
lvl_keys = [[encR1(p, u, w) for p in T3[:3] for u in T3[:3] for w in T3[:2] + BIG[:1]]]
print('level-1 R1 keys:', len(lvl_keys[0]), flush=True)
for lvl in range(4):
    r2s = []
    for k in lvl_keys[-1][:40]:
        M = Model(VER)
        if M.branch(a2(a2(k)), k) != 1:      # k must be R1-decodable
            continue
        for p in T3[:2]:
            v = encR2(p, k)
            if sz(v) > 4000:
                continue
            M2 = Model(VER)
            b = M2.branch(k, v)
            r2s.append((v, k, b))
    nfire = sum(1 for _, _, b in r2s if b == 2)
    print('level %d: %d R2-encodings built, %d actually fire R2, sizes %s'
          % (lvl + 1, len(r2s), nfire, sorted(set(sz(v) for v, _, _ in r2s))[:4]), flush=True)
    for (v, k, b) in r2s[:60]:
        for o in T3[:3] + BIG[:2]:
            test(o, v, k, 'R2-at-C-lvl%d' % (lvl + 1))    # C = op(k,v) fires R2
            test(v, k, o, 'R2-at-A-lvl%d' % (lvl + 1))    # A = op(y,x) fires R2
            test(o, k, v, 'R2-at-z-lvl%d' % (lvl + 1))
            test(v, o, k, 'R2-at-x-lvl%d' % (lvl + 1))
            test(k, v, o, 'R2-key-y-lvl%d' % (lvl + 1))
    print('   after level %d: %d chains, %d fails' % (lvl + 1, tot, len(fails)), flush=True)
    lvl_keys.append([v for v, _, b in r2s if b == 2][:40] or [v for v, _, _ in r2s][:40])

# also: R1-encodings whose key is an R2-encoding (mixed spine)
for k in lvl_keys[1][:20]:
    for p in T3[:2]:
        for w in T3[:2] + BIG[:1]:
            v = encR1(p, k, w)
            if sz(v) > 4000:
                continue
            for o in T3[:3]:
                test(o, v, k, 'mix-y'); test(v, k, o, 'mix-x'); test(o, k, v, 'mix-z')
print('TOTAL %d chains, %d FAILS' % (tot, len(fails)))
print('profiles reached (%d):' % len(profs))
for k, n in profs.most_common(15):
    print('   ', k, n)
fails.sort(key=lambda f: sz(f[1]) + sz(f[2]) + sz(f[3]))
for (tag, x, y, z, R, p) in fails[:2]:
    print('\nFAIL %s profile %s' % (tag, str(p)))
    for nm, t in (('x', x), ('y', y), ('z', z), ('R', R)):
        print('  %s (sz %d) = %s' % (nm, sz(t), show(t)[:200]))
