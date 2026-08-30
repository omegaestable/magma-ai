# -*- coding: utf-8 -*-
"""Deliberate probe of the near-zero branch P2 (and D2), with the level-k descent instrumented."""
import sys, os, random, collections, time
D = r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, D); sys.path.insert(0, os.path.join(D, 'gen'))
import importlib.util
spec = importlib.util.spec_from_file_location('lab', os.path.join(D, 'gen', '_w3_12087_lab.py'))
lab = importlib.util.module_from_spec(spec); spec.loader.exec_module(lab)
op, sz, show, tg, a1, a2 = lab.op, lab.sz, lab.show, lab.tg, lab.a1, lab.a2
CNT = collections.Counter()
def Dec2(u, v, depth=0):
    if tg(v) != 3: return None
    z = a2(a1(v))
    for i, X in enumerate(lab.xc(v)):
        if op(u, X, depth + 1) == a1(a1(v)) and op(X, z, depth + 1) == a2(v):
            CNT['D%d' % (i + 1)] += 1; return X
    return None
def P2f(u, v, depth=0):
    if tg(u) == 1: return False
    z = a2(u)
    if tg(a1(u)) != 1 and op(a2(a1(u)), z, depth + 1) == v: CNT['P1'] += 1; return True
    if tg(z) == 3 and op(a1(a1(a1(z))), z, depth + 1) == v: CNT['P2'] += 1; return True
    return False
lab.Dec, lab.P = Dec2, P2f
chain, enc, descent, deep = lab.chain, lab.enc, lab.descent, lab.deep

t0 = time.time()
for lv in (0, 2, 4):
    for bj in (False, True):
        CNT.clear()
        h, b = descent(lv, 5, 400, bj)
        print('descent lv=%d junk=%-5s hits=%-4d fails=%d   D1=%-6d D2=%-6d P1=%-6d P2=%d'
              % (lv, bj, h, len(b), CNT['D1'], CNT['D2'], CNT['P1'], CNT['P2']), flush=True)
CNT.clear(); b = deep(1, 8000)
print('deep 8000                       fails=%d   D1=%-6d D2=%-6d P1=%-6d P2=%d'
      % (len(b), CNT['D1'], CNT['D2'], CNT['P1'], CNT['P2']), flush=True)

# targeted: force the V-product to take P2, i.e. N3 decoded at the V pair.
# P2 needs tg (a2 u) = 3 with a2 u a tag whose payload reading gives x, and op x (a2 u) = v.
CNT.clear(); random.seed(3)
small = [('g', i) for i in range(3)] + [(c, ('g', i), ('g', j)) for c in ('J', 'E') for i in range(3) for j in range(3)]
bad = []; n = 0; hit = 0
for _ in range(6000):
    try:
        x = random.choice(small); w = random.choice(small); j = random.choice(small)
        z = enc(x, w, j)                       # z is a tag whose decoder is x  -> op x z decodes
        if op(x, z) == ('J', x, z): continue
        y = random.choice(small)
        n += 1
        before = CNT['P2']
        r = chain(x, y, z)[4]
        if CNT['P2'] > before: hit += 1
        if r != x: bad.append((x, y, z))
    except RecursionError: pass
print('targeted P2 family: %d chains, P2 fired on %d of them, fails=%d' % (n, hit, len(bad)), flush=True)
for (x, y, z) in bad[:2]:
    print('   x=%s\n   y=%s\n   z=%s' % (show(x), show(y), show(z)), flush=True)
print('branch totals in the targeted family: D1=%d D2=%d P1=%d P2=%d'
      % (CNT['D1'], CNT['D2'], CNT['P1'], CNT['P2']), flush=True)
print('total %.0fs' % (time.time() - t0))
