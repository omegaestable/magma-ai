"""Force the RECOMPUTATION branch (branch 2) to fire at an INNER chain product, for lab3 v17.

v17's branch 2 is complete only if every decode stores its key at a2 (a2 v) -- which the Cfree branch
does and branch 2 itself does NOT.  The general sweeps never fire branch 2 anywhere but the root
(profiles: only (0,0,1,0,2)), so they cannot see this.  Build it:

  z  = M (M pz (op kz pz)) (M wz kz)      -- z is Cfree-decodable by kz = a2 (a2 z), payload pz
  y  = M (M P  (op z  P )) pz             -- op z y then fires BRANCH 2 (a2 y = a1 (a1 z) = pz)
then run the law on (x, y, z') for many x and z'.
usage: python gen/_x11081_forceB2.py <ver>"""
import sys, collections
H = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen'
sys.path.insert(0, H)
from _x11081_lab4 import Model, chain, prof, terms, sz, show, g, J, E, F, K, tg, a1, a2

VER = sys.argv[1] if len(sys.argv) > 1 else 'v17'
T3 = terms(3, 2)
tot = 0
fails = []
profs = collections.Counter()
built = collections.Counter()


def test(x, y, z, tag):
    global tot
    M = Model(VER)
    try:
        A, B, C, D, R = chain(M, x, y, z)
        p = prof(M, x, y, z)
    except RecursionError:
        return
    tot += 1
    profs[p] += 1
    if R != x:
        fails.append((tag, x, y, z, R, p))


CT = (E, F, K, J)
pairs = []
for c1 in CT:
    for c2 in CT:
        for pz in T3[:6]:
            for kz in T3[:4]:
                for wz in T3[:3]:
                    M = Model(VER)
                    try:
                        z = c1(c2(pz, M.op(kz, pz)), c1(wz, kz))
                    except RecursionError:
                        continue
                    if sz(z) > 200:
                        continue
                    M2 = Model(VER)
                    try:
                        if M2.branch(kz, z) != 1:      # z must be Cfree-decodable
                            continue
                    except RecursionError:
                        continue
                    pairs.append((z, kz, pz))
print('Cfree-decodable z built:', len(pairs), flush=True)

ys = []
for (z, kz, pz) in pairs[:200]:
    for c3 in CT:
        for c4 in CT:
            for P in T3[:3]:
                M = Model(VER)
                try:
                    y = c3(c4(P, M.op(z, P)), pz)
                except RecursionError:
                    continue
                if sz(y) > 400:
                    continue
                M2 = Model(VER)
                try:
                    b = M2.branch(z, y)
                except RecursionError:
                    continue
                built[b] += 1
                if b == 2:
                    ys.append((y, z, P))
print('y built, branch fired at (z,y):', dict(built), '-> branch-2 cases:', len(ys), flush=True)

for (y, z, P) in ys[:400]:
    for x in T3[:6]:
        test(x, y, z, 'B2-at-C')
        test(x, y, P, 'B2-at-C2')
        test(y, z, x, 'B2-at-A')
        test(x, z, y, 'B2-at-z')
print('%s: %d chains, %d FAILS' % (VER, tot, len(fails)))
print('profiles:', dict(profs.most_common(8)))
fails.sort(key=lambda f: sz(f[1]) + sz(f[2]) + sz(f[3]))
for (tag, x, y, z, R, p) in fails[:2]:
    print('FAIL %s profile %s' % (tag, str(p)))
    for nm, t in (('x', x), ('y', y), ('z', z), ('R', R)):
        print('  %s (sz %d) = %s' % (nm, sz(t), show(t)[:200]))
