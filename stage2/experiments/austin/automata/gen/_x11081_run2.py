"""Fast killer oracle + level-k descent + exhaustive sweep on lab2, WITH THE CELL CENSUS beside
every descent count (an adaptation can be vacuous).  usage: python gen/_x11081_run2.py <ver>"""
import sys, random, collections, time
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen')
from _x11081_lab2 import Model, chain, prof, terms, sz, show, g, J, E, F, tg, a1, a2

VER = sys.argv[1] if len(sys.argv) > 1 else 'v7'
t0 = time.time()
tot = 0
over = 0
fails = []
profs = collections.Counter()
cells = collections.Counter()


def test(x, y, z, tag):
    global tot, over
    M = Model(VER)
    try:
        A, B, C, D, R = chain(M, x, y, z)
        p = prof(M, x, y, z)
    except RecursionError:
        over += 1
        return
    tot += 1
    profs[p] += 1
    cells[(p[2] != 0, p[3] != 0, p[0] != 0)] += 1
    if R != x:
        fails.append((tag, x, y, z, R, p))


T3 = terms(3, 2)
T5 = terms(5, 2)
print('pools |T3|=%d |T5|=%d' % (len(T3), len(T5)), flush=True)
M0 = Model(VER)


def mk(p, u, w):
    try:
        return E(F(p, M0.op(u, p)), w)
    except RecursionError:
        return None


built = []
for p in T3[:4]:
    for u in T3[:4]:
        for w in T3[:3]:
            v = mk(p, u, w)
            if v is None or sz(v) > 200:
                continue
            M = Model(VER)
            try:
                b = M.branch(u, v)
            except RecursionError:
                continue
            built.append((v, u, p, b))
print('builder: branch that fires ->', dict(collections.Counter(b for _, _, _, b in built)),
      'of', len(built), flush=True)
for (v, u, p, b) in built:
    if not b:
        continue
    for o in T3[:4]:
        test(o, v, u, 'dec-at-C')
        test(v, u, o, 'dec-at-A')
        test(o, u, v, 'dec-at-z')
        test(v, o, u, 'dec-at-x')
        test(u, v, o, 'dec-key-y')
print('KILLER: %d chains, %d fails, %d overflow  %.0fs'
      % (tot, len(fails), over, time.time() - t0), flush=True)

keys = [T3[:4]]
for lvl in range(4):
    nxt = []
    for k in keys[-1]:
        for p in T3[:2]:
            for w in T3[:2]:
                v = mk(p, k, w)
                if v is not None and sz(v) <= 3000:
                    nxt.append(v)
    nxt = nxt[:24]
    keys.append(nxt)
    b4 = len(fails)
    c4 = tot
    for v in nxt:
        for k in keys[-2][:4]:
            for o in T3[:3]:
                test(o, v, k, 'lvl-y')
                test(v, k, o, 'lvl-x')
                test(o, k, v, 'lvl-z')
    print('  level %d: %d encs, +%d chains, +%d fails | census(Cdec,Ddec,Adec) %s'
          % (lvl + 1, len(nxt), tot - c4, len(fails) - b4, dict(cells)), flush=True)

for x in T5:
    for y in T3:
        for z in T3:
            test(x, y, z, 'E1')
for y in T5:
    for x in T3:
        for z in T3:
            test(x, y, z, 'E2')
for z in T5:
    for x in T3:
        for y in T3:
            test(x, y, z, 'E3')
print('TOTAL %d chains, %d FAILS, %d overflow  %.0fs'
      % (tot, len(fails), over, time.time() - t0))
print('cell census (Cdec,Ddec,Adec):', dict(cells))
print('profiles (%d):' % len(profs), dict(profs.most_common(8)))
fails.sort(key=lambda f: sz(f[1]) + sz(f[2]) + sz(f[3]))
for (tag, x, y, z, R, p) in fails[:2]:
    print('FAIL %s profile %s' % (tag, str(p)))
    for nm, t in (('x', x), ('y', y), ('z', z), ('R', R)):
        print('  %s (sz %d) = %s' % (nm, sz(t), show(t)[:190]))
