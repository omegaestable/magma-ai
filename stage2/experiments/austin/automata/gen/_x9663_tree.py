"""Case tree (W3-6) for the 9663 model: which of the 2^4 free/decoded cells of the law's own
evaluation chain are reachable, and does the law hold in each?

chain: P = op(x,y),  Q = op(x,P),  A = op(z,y),  C = op(A,Q),  root = op(y,C)
A cell is the 4-tuple of booleans (P decoded, Q decoded, A decoded, C decoded).

Instances are built by CHAINED ENCODING: enc(a,w,j) = J (J j a) (J w (op(w,a))) satisfies
op(a, enc(a,w,j)) = w, so putting an encoding in an argument slot forces that product to decode.
"""
import sys, os, itertools, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _idc_lib import G, J, sz, show
import q9663 as M
op = M.op

def enc(a, w, j):
    """a term E with op(a,E) = w  (free A slot)."""
    return J(J(j, a), J(w, op(w, a)))

def enc2(a, w, j):
    """same but with the DECODED A slot: A = a1 (a2 a), requires a = J _ (J A _)."""
    if a[0] == 'J' and a[2][0] == 'J':
        return J(a[2][1], J(w, op(w, a)))
    return None

def cell(x, y, z):
    P = op(x, y); Q = op(x, P); A = op(z, y); C = op(A, Q); R = op(y, C)
    d = (P != J(x, y), Q != J(x, P), A != J(z, y), C != J(A, Q))
    return d, R

def main():
    g0, g1 = G(0), G(1)
    base = [g0, g1, J(g0, g0), J(g0, g1), J(g1, g0), J(g0, J(g0, g0)), J(J(g0, g0), g0),
            J(J(g0, g0), J(g0, g0)), J(g0, J(g0, J(g0, g0)))]
    pool = list(base)
    # one and two levels of encoding, both A-slot flavours
    for a in base:
        for w in base[:5]:
            for j in base[:3]:
                pool.append(enc(a, w, j))
                e = enc2(a, w, j)
                if e is not None: pool.append(e)
    for a in base[:4]:
        for w in base[:3]:
            e = enc(a, w, g0)
            pool.append(enc(e, w, g0))
            pool.append(enc(a, e, g0))
            e2 = enc2(a, w, g0)
            if e2 is not None:
                pool.append(enc(e2, w, g0)); pool.append(enc(a, e2, g0))
    pool = list(dict.fromkeys(pool))
    print('pool = %d terms (max size %d)' % (len(pool), max(sz(t) for t in pool)))
    seen = {}
    fails = []
    rng = random.Random(20260829)
    N = 0
    NS = int(sys.argv[1]) if len(sys.argv) > 1 else 400000
    for _ in range(NS):
        x = rng.choice(pool); y = rng.choice(pool); z = rng.choice(pool)
        N += 1
        d, R = cell(x, y, z)
        ok = (R == x)
        st = seen.setdefault(d, [0, 0])
        st[0] += 1
        if not ok:
            st[1] += 1
            if len(fails) < 4: fails.append((x, y, z, R))
    print('tested %d assignments' % N)
    for d in sorted(seen, key=lambda t: (sum(t), t)):
        n, bad = seen[d]
        print('  cell P%d Q%d A%d C%d : %8d instances, %d FAIL' %
              (d[0], d[1], d[2], d[3], n, bad))
    print('cells reached: %d of 16' % len(seen))
    for x, y, z, R in fails:
        print('  FAIL x=%s' % show(x)[:70]); print('       y=%s' % show(y)[:70])
        print('       z=%s -> %s' % (show(z)[:70], show(R)[:70]))

main()
