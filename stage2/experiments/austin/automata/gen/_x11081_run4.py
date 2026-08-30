"""Driver for lab3 (5 constructors) and, via --lab2, for lab2.
Oracles in kill-power order: forceD, H3, forceDec, exhaustive.  Census printed with every block.
  H3: y is a GENUINE ENCODING BY x  -- y = enc(j, x, w), so op x y decodes.  Orthogonal to the others.
usage: python gen/_x11081_run3.py <ver> [lab2]"""
import sys, collections
H = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen'
sys.path.insert(0, H)
VER = sys.argv[1] if len(sys.argv) > 1 else 'v13'
if len(sys.argv) > 2 and sys.argv[2] == 'lab2':
    from _x11081_lab2 import Model, chain, prof, terms, sz, show, g, J, E, F, tg, a1, a2
    K = F
else:
    from _x11081_lab4 import Model, chain, prof, terms, sz, show, g, J, E, F, K, tg, a1, a2

tot = 0
fails = []
profs = collections.Counter()
cells = collections.Counter()


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
    cells[(p[2] != 0, p[3] != 0, p[0] != 0, p[1] != 0)] += 1
    if R != x:
        fails.append((tag, x, y, z, R, p))


def rep(name, b4):
    print('%-10s +%d chains  +%d fails | census(Cdec,Ddec,Adec,Bdec) %s'
          % (name, tot - b4[0], len(fails) - b4[1], dict(cells)), flush=True)
    return [tot, len(fails)]


T3 = terms(3, 2)
T5 = terms(5, 2)
print('ver %s  |T3|=%d |T5|=%d' % (VER, len(T3), len(T5)), flush=True)
b4 = [0, 0]

# ---- oracle 1: forceD (highest kill power) ----
for x in (T3 + T5[:40])[:36]:
    for y in (T3 + T5[:40])[:36]:
        M = Model(VER)
        try:
            A = M.op(y, x); B = M.op(x, A)
        except RecursionError:
            continue
        for q in T3[:4]:
            try:
                r = M.op(B, q)
            except RecursionError:
                continue
            for ctor in (E, F, K, J):
                z = ctor(q, r)
                if sz(z) <= 400:
                    test(x, y, z, 'forceD')
b4 = rep('forceD', b4)

# ---- oracle 2: H3 -- y is a genuine encoding BY x ----
M0 = Model(VER)


def enc(p, u, w):
    """a v with op u v decoding to p, in whatever shape this version's rule wants"""
    try:
        inner = M0.op(u, p)
    except RecursionError:
        return None
    for outer in (K, E, F, J):
        for mid in (F, E, K, J):
            v = outer(mid(p, inner), w)
            M = Model(VER)
            try:
                if M.branch(u, v):
                    return v
            except RecursionError:
                pass
    return None


made = 0
for j in T3[:4]:
    for x in T3[:6]:
        for w in T3[:4]:
            y = enc(j, x, w)          # H3: y is an encoding BY x
            if y is None or sz(y) > 300:
                continue
            made += 1
            for z in T3[:5]:
                test(x, y, z, 'H3')
                test(j, y, z, 'H3b')
                test(y, x, z, 'H3c')
                test(x, y, x, 'H3d')
print('H3: built %d genuine encodings-by-x' % made, flush=True)
b4 = rep('H3', b4)

# ---- oracle 3: force the decode at every product ----
for p in T3[:4]:
    for u in T3[:5]:
        for w in T3[:3]:
            v = enc(p, u, w)
            if v is None or sz(v) > 300:
                continue
            for o in T3[:4]:
                test(o, v, u, 'dec-C'); test(v, u, o, 'dec-A'); test(o, u, v, 'dec-z')
                test(v, o, u, 'dec-x'); test(u, v, o, 'dec-key')
b4 = rep('forceDec', b4)

# ---- oracle 4: exhaustive ----
for x in T5:
    for y in T3:
        for z in T3:
            test(x, y, z, 'E1')
for y in T5:
    for x in T3:
        for z in T3:
            test(x, y, z, 'E2')
b4 = rep('exhaust', b4)
print('TOTAL %d chains, %d FAILS' % (tot, len(fails)))
print('profiles (%d):' % len(profs), dict(profs.most_common(8)))
fails.sort(key=lambda f: sz(f[1]) + sz(f[2]) + sz(f[3]))
for (tag, x, y, z, R, p) in fails[:2]:
    print('FAIL %s profile %s' % (tag, str(p)))
    for nm, t in (('x', x), ('y', y), ('z', z), ('R', R)):
        print('  %s (sz %d) = %s' % (nm, sz(t), show(t)[:180]))
