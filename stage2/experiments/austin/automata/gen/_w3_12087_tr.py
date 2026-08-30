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
    if r == ('J', u, v): return 'F'
    if r == ('E', u, v): return 'T'
    if lab.B0(u, v) is not None and lab.Dec(u, v) is None and not lab.P(u, v): return 'B'
    return 'D'
random.seed(5)
small = [('g', i) for i in range(3)] + [(c, ('g', i), ('g', j)) for c in ('J', 'E') for i in range(3) for j in range(3)]
best = None
for _ in range(4000):
    try:
        x = random.choice(small)
        y = random.choice([random.choice(small), enc(x, random.choice(small), random.choice(small))])
        p = random.choice(small)
        for _ in range(random.randrange(3)): p = enc(x, p, random.choice(small))
        z = random.choice([random.choice(small), enc(x, p, random.choice(small)),
                           enc(op(y, x), p, random.choice(small))])
        N1 = op(y, x); N2 = op(N1, z); N3 = op(x, z); V = op(N2, N3); R = op(y, V)
        if R != x:
            t = sz(x) + sz(y) + sz(z)
            if best is None or t < best[0]: best = (t, x, y, z, N1, N2, N3, V, R)
    except RecursionError: pass
t, x, y, z, N1, N2, N3, V, R = best
print('smallest fail total=%d' % t)
for nm, (u, v) in (('N1 op(y,x)', (y, x)), ('N2 op(N1,z)', (N1, z)), ('N3 op(x,z)', (x, z)),
                   ('V  op(N2,N3)', (N2, N3)), ('R  op(y,V)', (y, V))):
    print('  %-14s kind=%s  Dec=%s P=%s B0=%s' % (nm, kind(u, v),
          lab.Dec(u, v) is not None, lab.P(u, v), lab.B0(u, v) is not None))
print('  x =', show(x)); print('  y =', show(y)); print('  z =', show(z))
print('  N3=', show(N3)); print('  V =', show(V)); print('  got', show(R))
