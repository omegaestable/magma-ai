import sys, os, random, collections
D = r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, D); sys.path.insert(0, os.path.join(D, 'gen'))
import importlib.util
spec = importlib.util.spec_from_file_location('lab', os.path.join(D, 'gen', '_w3_12087_lab.py'))
lab = importlib.util.module_from_spec(spec); spec.loader.exec_module(lab)
op, sz, show, tg = lab.op, lab.sz, lab.show, lab.tg
enc = lab.enc
def kind(u, v):
    r = op(u, v)
    if r == ('J', u, v): return 'F'
    if r == ('E', u, v): return 'T'
    return 'D'
random.seed(5)
small = [('g', i) for i in range(3)] + [(c, ('g', i), ('g', j)) for c in ('J', 'E') for i in range(3) for j in range(3)]
cells = collections.Counter(); badcells = collections.Counter(); bad = []
for _ in range(4000):
    try:
        x = random.choice(small)
        y = random.choice([random.choice(small), enc(x, random.choice(small), random.choice(small))])
        p = random.choice(small)
        for _ in range(random.randrange(3)): p = enc(x, p, random.choice(small))
        z = random.choice([random.choice(small), enc(x, p, random.choice(small)),
                           enc(op(y, x), p, random.choice(small))])
        N1 = op(y, x); N2 = op(N1, z); N3 = op(x, z); V = op(N2, N3); R = op(y, V)
        k = (kind(y, x), kind(N1, z), kind(x, z), kind(N2, N3))
        cells[k] += 1
        if R != x:
            bad.append((x, y, z, k)); badcells[k] += 1
    except RecursionError: pass
print('random half: %d chains, %d FAILS' % (sum(cells.values()), len(bad)))
print('cells:', dict(cells))
print('bad cells:', dict(badcells))
for (x, y, z, k) in bad[:2]:
    print(' cell', k)
    print('   x=%s' % show(x)); print('   y=%s' % show(y)); print('   z=%s' % show(z))
