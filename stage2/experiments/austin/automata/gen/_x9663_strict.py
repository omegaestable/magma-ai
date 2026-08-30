"""9663: the STRICTLY STRUCTURAL decode rule -- no recursive call anywhere.

op u v = x   when  v = J A (J x (J x u))  and  inimg A u
       = J u v otherwise
inimg A u := (A = J _ u)  or  (u = J _ (J A _))
"""
import sys, os, random, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _idc_lib import G, J, sz, show, terms, check, ev

LAW = ('y', (('z', 'y'), ('x', ('x', 'y'))))

def inimg(A, u):
    if A[0] == 'J' and A[2] == u: return True
    return u[0] == 'J' and u[2][0] == 'J' and A == u[2][1]

def op(u, v):
    if v[0] == 'J':
        A, Q = v[1], v[2]
        if Q[0] == 'J':
            x, P = Q[1], Q[2]
            if P[0] == 'J' and P[1] == x and P[2] == u and inimg(A, u):
                return x
    return J(u, v)

def enc(a, w, j): return J(J(j, a), J(w, J(w, a)))

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'exh'
    if mode == 'exh':
        ms, gens, zs = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
        pool = terms(ms, gens); zp = terms(zs, gens)
        t0 = time.time()
        n, f = check(op, LAW, pool, pools={'x': pool, 'y': pool, 'z': zp}, limit=3)
        print('strict exh size<=%d gens=%d z<=%d: pool=%d tested=%d FAILS=%d (%.1fs)'
              % (ms, gens, zs, len(pool), n, len(f), time.time()-t0))
        for s, r in f[:3]:
            print('   x=%s y=%s z=%s -> %s' % (show(s['x']), show(s['y']), show(s['z']), show(r)))
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
                        pool.append(J(a[2][1], J(w, J(w, a))))
        for a in base[:4]:
            for w in base[:3]:
                e = enc(a, w, g0)
                pool.append(enc(e, w, g0)); pool.append(enc(a, e, g0))
        pool = list(dict.fromkeys(pool))
        print('pool = %d (max size %d)' % (len(pool), max(sz(t) for t in pool)))
        seen = {}; fails = []
        for _ in range(int(sys.argv[2]) if len(sys.argv) > 2 else 400000):
            x = rng.choice(pool); y = rng.choice(pool); z = rng.choice(pool)
            P = op(x, y); Q = op(x, P); A = op(z, y); Cc = op(A, Q); R = op(y, Cc)
            d = (P != J(x, y), Q != J(x, P), A != J(z, y), Cc != J(A, Q))
            st = seen.setdefault(d, [0, 0]); st[0] += 1
            if R != x:
                st[1] += 1
                if len(fails) < 3: fails.append((x, y, z, R))
        for d in sorted(seen, key=lambda t: (sum(t), t)):
            n, bad = seen[d]
            print('  cell P%d Q%d A%d C%d : %8d instances, %d FAIL' % (d[0], d[1], d[2], d[3], n, bad))
        print('cells reached: %d' % len(seen))
        for x, y, z, R in fails:
            print('  FAIL x=%s' % show(x)[:80]); print('       y=%s' % show(y)[:80])
            print('       z=%s' % show(z)[:80]); print('       -> %s' % show(R)[:80])
