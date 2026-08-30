import sys, os, random, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _idc_lib import G, J, sz, show, terms, check, ev
M = __import__(sys.argv[1])
op = M.op
LAW = ('y', (('z', 'y'), ('x', ('x', 'y'))))

def enc(a, w, j):
    return J(J(j, a), J(w, op(w, a)))

mode = sys.argv[2]
if mode == 'exh':
    ms, gens, zs = int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
    pool = terms(ms, gens); zp = terms(zs, gens); t0 = time.time()
    n, f = check(op, LAW, pool, pools={'x': pool, 'y': pool, 'z': zp}, limit=3)
    print('%s exh size<=%d gens=%d z<=%d: tested=%d FAILS=%d (%.1fs)' % (sys.argv[1], ms, gens, zs, n, len(f), time.time()-t0))
    for s, r in f[:3]:
        print('   x=%s y=%s z=%s -> %s' % (show(s['x'])[:60], show(s['y'])[:60], show(s['z'])[:60], show(r)[:60]))
elif mode == 'tree':
    rng = random.Random(20260829)
    g0, g1 = G(0), G(1)
    base = [g0, g1, J(g0, g0), J(g0, g1), J(g1, g0), J(g0, J(g0, g0)), J(J(g0, g0), g0),
            J(J(g0, g0), J(g0, g0)), J(g0, J(g0, J(g0, g0)))]
    pool = list(base)
    for a in base:
        for w in base[:5]:
            for j in base[:3]:
                pool.append(enc(a, w, j))
                if a[0] == 'J' and a[2][0] == 'J':
                    pool.append(J(a[2][1], J(w, op(w, a))))
    for a in base[:4]:
        for w in base[:3]:
            e = enc(a, w, g0)
            pool.append(enc(e, w, g0)); pool.append(enc(a, e, g0))
            pool.append(enc(enc(a, w, g0), enc(a, w, g0), g0))
    pool = list(dict.fromkeys(pool))
    seen = {}; fails = []
    for _ in range(int(sys.argv[3]) if len(sys.argv) > 3 else 400000):
        x = rng.choice(pool); y = rng.choice(pool); z = rng.choice(pool)
        P = op(x, y); Q = op(x, P); A = op(z, y); Cc = op(A, Q); R = op(y, Cc)
        d = (P != J(x, y), Q != J(x, P), A != J(z, y), Cc != J(A, Q))
        st = seen.setdefault(d, [0, 0]); st[0] += 1
        if R != x:
            st[1] += 1
            if len(fails) < 3: fails.append((x, y, z, R))
    print('%s tree pool=%d' % (sys.argv[1], len(pool)))
    for d in sorted(seen, key=lambda t: (sum(t), t)):
        n, bad = seen[d]
        print('  cell P%d Q%d A%d C%d : %8d, %d FAIL' % (d[0], d[1], d[2], d[3], n, bad))
    for x, y, z, R in fails:
        print('  FAIL x=%s' % show(x)[:80]); print('       y=%s' % show(y)[:80])
        print('       z=%s' % show(z)[:80]); print('       -> %s' % show(R)[:80])
