# -*- coding: utf-8 -*-
"""Which (N1,N2,N3,V) branch combinations are reachable in the E-carrier?  Reachable cells must be
exhibited in `law`; unreachable ones must be refuted, and that is the expensive half."""
import sys, os, random, collections
D = r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, D); sys.path.insert(0, os.path.join(D, 'gen'))
import importlib.util
spec = importlib.util.spec_from_file_location('lab', os.path.join(D, 'gen', '_w3_12087_lab.py'))
lab = importlib.util.module_from_spec(spec); spec.loader.exec_module(lab)
op, sz, show, tg, a1, a2 = lab.op, lab.sz, lab.show, lab.tg, lab.a1, lab.a2
enc, terms, chain = lab.enc, lab.terms, lab.chain

def kind(u, v):
    r = op(u, v)
    if r == ('J', u, v): return 'F'
    if r == ('E', u, v): return 'T'
    return 'D'

cells = collections.Counter()
def note(x, y, z):
    N1 = op(y, x); N2 = op(N1, z); N3 = op(x, z); V = op(N2, N3)
    cells[(kind(y, x), kind(N1, z), kind(x, z), kind(N2, N3))] += 1
    return op(y, V) == x

pool = terms(5, 2)
bad = 0
for x in pool:
    for y in pool:
        for z in pool:
            try:
                if not note(x, y, z): bad += 1
            except RecursionError: bad += 1
print('L1 (size<=5, 2 gens): %d chains, %d fails' % (sum(cells.values()), bad), flush=True)

random.seed(5)
small = [('g', i) for i in range(3)] + [(c, ('g', i), ('g', j)) for c in ('J', 'E') for i in range(3) for j in range(3)]
for _ in range(4000):
    try:
        x = random.choice(small)
        y = random.choice([random.choice(small), enc(x, random.choice(small), random.choice(small))])
        p = random.choice(small)
        for _ in range(random.randrange(3)): p = enc(x, p, random.choice(small))
        z = random.choice([random.choice(small), enc(x, p, random.choice(small)),
                           enc(op(y, x), p, random.choice(small))])
        if not note(x, y, z): bad += 1
    except RecursionError: pass

print('\ncell (N1,N2,N3,V)   count      [F=free  T=tagged  D=decoded]', flush=True)
for k, n in sorted(cells.items(), key=lambda kv: -kv[1]):
    print('   %-22s %d' % (str(k), n), flush=True)
print('\nreachable cells: %d of 81' % len(cells), flush=True)
print('N2 kinds seen:', sorted(set(k[1] for k in cells)), flush=True)
print('V  kinds seen:', sorted(set(k[3] for k in cells)), flush=True)
print('N1 kinds seen:', sorted(set(k[0] for k in cells)), flush=True)
print('N3 kinds seen:', sorted(set(k[2] for k in cells)), flush=True)
