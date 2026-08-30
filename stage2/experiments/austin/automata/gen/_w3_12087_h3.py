# -*- coding: utf-8 -*-
"""H3 (law 12234's decisive construction) + per-branch firing counts for the 12087 E-carrier.

H3: make the DECODER variable y itself a genuine encoding involving x, both ways round:
    y = enc(x, w, j)   -- y is an encoding whose decoder is x
    y = enc(j, w, x)   -- y is an encoding whose junk/z slot is x
This family is orthogonal to L1 / deep / the level-k descent (which all nest inside z).
"""
import sys, os, random, collections, time
D = r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, D); sys.path.insert(0, os.path.join(D, 'gen'))
import importlib.util
spec = importlib.util.spec_from_file_location('lab', os.path.join(D, 'gen', '_w3_12087_lab.py'))
lab = importlib.util.module_from_spec(spec); spec.loader.exec_module(lab)
op, sz, show, tg, a1, a2 = lab.op, lab.sz, lab.show, lab.tg, lab.a1, lab.a2

# ---- instrument the five branches -------------------------------------------------
CNT = collections.Counter()
_Dec, _P = lab.Dec, lab.P
def Dec2(u, v, depth=0):
    if tg(v) != 3: return None
    z = a2(a1(v))
    for i, X in enumerate(lab.xc(v)):
        if op(u, X, depth + 1) == a1(a1(v)) and op(X, z, depth + 1) == a2(v):
            CNT['D%d' % (i + 1)] += 1; return X
    return None
def P2(u, v, depth=0):
    if tg(u) == 1: return False
    z = a2(u)
    if tg(a1(u)) != 1 and op(a2(a1(u)), z, depth + 1) == v: CNT['P1'] += 1; return True
    if tg(z) == 3 and op(a1(a1(a1(z))), z, depth + 1) == v: CNT['P2'] += 1; return True
    return False
lab.Dec, lab.P = Dec2, P2
chain, enc, terms = lab.chain, lab.enc, lab.terms

def report(name, bad, n):
    print('%-28s %-8d chains  fails=%d' % (name, n, len(bad)), flush=True)
    for (x, y, z) in bad[:2]:
        print('   x=%s\n   y=%s\n   z=%s' % (show(x), show(y), show(z)), flush=True)

t0 = time.time()
small = [('g', i) for i in range(3)] + [(c, ('g', i), ('g', j))
         for c in ('J', 'E') for i in range(3) for j in range(3)]
def rt(d):
    if d <= 0 or random.random() < 0.35: return ('g', random.randrange(3))
    return (random.choice(('J', 'E')), rt(d - 1), rt(d - 1))

for mode, tag in ((0, 'H3a  y = enc(x, w, j)'), (1, 'H3b  y = enc(j, w, x)')):
    for seed in (5, 19, 23):
        random.seed(seed)
        pool = list(small) + [rt(3) for _ in range(40)]
        bad = []; n = 0
        for _ in range(4000):
            try:
                x = random.choice(pool); w = random.choice(pool); j = random.choice(pool)
                y = enc(x, w, j) if mode == 0 else enc(j, w, x)
                z = random.choice(pool)
                if random.random() < 0.5: z = enc(x, random.choice(pool), random.choice(pool))
                if random.random() < 0.25: z = enc(y, random.choice(pool), random.choice(pool))
                n += 1
                if chain(x, y, z)[4] != x: bad.append((x, y, z))
            except RecursionError: pass
        report('%s seed=%d' % (tag, seed), bad, n)

# H3 combined with the descent: y an encoding by x AND z a nested x-encoding
for seed in (5, 19):
    random.seed(seed)
    pool = list(small) + [rt(3) for _ in range(40)]
    bad = []; n = 0
    for _ in range(3000):
        try:
            x = random.choice(pool)
            y = enc(x, random.choice(pool), random.choice(pool))
            p = random.choice(pool)
            for _ in range(2): p = enc(x, p, random.choice(pool))
            z = enc(x, p, random.choice(pool))
            n += 1
            if chain(x, y, z)[4] != x: bad.append((x, y, z))
        except RecursionError: pass
    report('H3 x descent seed=%d' % seed, bad, n)

print('\nper-branch firing counts over everything above:', flush=True)
for k in ('D1', 'D2', 'P1', 'P2'):
    print('   %-4s %d' % (k, CNT[k]), flush=True)
print('total %.0fs' % (time.time() - t0))
