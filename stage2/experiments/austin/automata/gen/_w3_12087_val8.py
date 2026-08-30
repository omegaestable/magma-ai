# -*- coding: utf-8 -*-
"""Full validation battery for the v8 E-carrier of 12087, plus goal refutations for 28770 and 22818."""
import sys, os, random, itertools, time
D = r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, D); sys.path.insert(0, os.path.join(D, 'gen'))
import importlib.util
spec = importlib.util.spec_from_file_location('lab', os.path.join(D, 'gen', '_w3_12087_lab.py'))
lab = importlib.util.module_from_spec(spec); spec.loader.exec_module(lab)
op, sz, show, tg, a1, a2 = lab.op, lab.sz, lab.show, lab.tg, lab.a1, lab.a2
chain, terms, deep, descent, enc = lab.chain, lab.terms, lab.deep, lab.descent, lab.enc
t0 = time.time()

# 1. exhaustive, 2 generators, size <= 5  (already 405,224) and a 3-generator slice
n, bad, pool = lab.L1(5, 2)
print('L1  size<=5 gens=2  %-8d chains  fails=%d' % (n, len(bad)), flush=True)
pool3 = terms(3, 3); big = terms(5, 2)
n2 = 0; bad2 = []
for x in pool3:
    for y in pool3:
        for z in big:
            n2 += 1
            try:
                if chain(x, y, z)[4] != x: bad2.append((x, y, z))
            except RecursionError: bad2.append((x, y, z))
print('L1b x,y size<=3 gens=3, z size<=5 gens=2  %-8d chains  fails=%d' % (n2, len(bad2)), flush=True)

# 2. deep random, 6 seeds x 20,000
tot = 0
for sd in range(1, 7):
    b = deep(sd, 20000)
    tot += len(b)
    print('deep seed %d  20000 chains  fails=%d' % (sd, len(b)), flush=True)

# 3. the level-k descent, levels 0..4, both junk pools, 4 seeds
dtot = 0
for lv in range(0, 5):
    for bj in (False, True):
        for sd in (5, 19, 23, 31):
            h, b = descent(lv, sd, 400, bj)
            dtot += len(b)
            if b or lv <= 1:
                print('descent lv=%d junk=%-5s seed=%-3d hits=%-4d fails=%d' % (lv, bj, sd, h, len(b)), flush=True)
print('descent TOTAL fails=%d' % dtot, flush=True)

# 4. coincidence: x,y,z drawn from the model's own chain values
random.seed(7)
base = [('g', i) for i in range(3)] + [(c, ('g', i), ('g', j)) for c in ('J', 'E') for i in range(3) for j in range(3)]
poolc = list(base)
for _ in range(500):
    try: poolc.append(enc(random.choice(poolc), random.choice(poolc), random.choice(poolc)))
    except RecursionError: pass
for _ in range(300):
    try:
        a, b_, c = random.choice(poolc), random.choice(poolc), random.choice(poolc)
        poolc += [op(a, b_), op(b_, c), op(op(a, b_), c)]
    except RecursionError: pass
cb = 0; cn = 0
for _ in range(30000):
    x, y, z = random.choice(poolc), random.choice(poolc), random.choice(poolc)
    try:
        cn += 1
        if chain(x, y, z)[4] != x: cb += 1
    except RecursionError: pass
print('coincidence (x,y,z from the model own values) %d chains fails=%d' % (cn, cb), flush=True)

# 5. goal refutations
def evg(pat, s):
    if isinstance(pat, str): return s[pat]
    return op(evg(pat[0], s), evg(pat[1], s))
from freemodel import normalise, catalog
from laws import parse_eq
cat = catalog()
for g in (28770, 22818):
    law_g = normalise(parse_eq(cat[g]))
    vs = sorted(set(v for v in 'xyzwu' if v in str(law_g)))
    found = None
    cands = [('g', 0), ('g', 1), ('g', 2), ('J', ('g', 0), ('g', 1)), ('E', ('g', 0), ('g', 1))]
    for combo in itertools.product(cands, repeat=len(vs)):
        s = dict(zip(vs, combo))
        try:
            if evg(law_g[1], s) != s[law_g[0]]: found = s; break
        except RecursionError: pass
    print('goal %d  %s  refuted=%s  %s' % (g, cat[g], found is not None,
          {k: show(v) for k, v in found.items()} if found else ''), flush=True)
print('total %.0fs' % (time.time() - t0))
