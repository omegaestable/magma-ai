import sys, os, random
D = r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, D); sys.path.insert(0, os.path.join(D, 'gen'))
import importlib.util
spec = importlib.util.spec_from_file_location('lab', os.path.join(D, 'gen', '_w3_12087_lab.py'))
lab = importlib.util.module_from_spec(spec); spec.loader.exec_module(lab)
op, sz, show, tg, a1, a2 = lab.op, lab.sz, lab.show, lab.tg, lab.a1, lab.a2
enc = lab.enc
def kind(u, v):
    r = op(u, v)
    return 'F' if r == ('J', u, v) else ('T' if r == ('E', u, v) else 'D')
# targeted: z = enc(op(y,x), p, q) forces op(N1,z) to decode  -- the mode my E-carrier lab never had
random.seed(11)
small = [('g', i) for i in range(3)] + [(c, ('g', i), ('g', j)) for c in ('J', 'E') for i in range(3) for j in range(3)]
best = None; n = 0; bad = 0
for _ in range(3000):
    try:
        x = random.choice(small); y = random.choice(small)
        z = enc(op(y, x), random.choice(small), random.choice(small))
        N1 = op(y, x); N2 = op(N1, z); N3 = op(x, z); V = op(N2, N3); R = op(y, V)
        n += 1
        if R != x:
            bad += 1
            t = sz(x) + sz(y) + sz(z)
            if best is None or t < best[0]: best = (t, x, y, z, N1, N2, N3, V, R,
                                                   (kind(y,x), kind(N1,z), kind(x,z), kind(N2,N3)))
    except RecursionError: pass
print('N2-decoding construction: %d chains, %d FAILS' % (n, bad))
if best:
    t, x, y, z, N1, N2, N3, V, R, k = best
    print('SMALLEST  total=%d  cell=%s' % (t, str(k)))
    print('  x = %s' % show(x)); print('  y = %s' % show(y)); print('  z = %s' % show(z))
    print('  N1= %s' % show(N1)); print('  N2= %s   (decoded: op N1 z shrank)' % show(N2))
    print('  N3= %s' % show(N3)); print('  V = %s  tg V=%d' % (show(V), tg(V)))
    print('  op y V = %s  != x' % show(R))
