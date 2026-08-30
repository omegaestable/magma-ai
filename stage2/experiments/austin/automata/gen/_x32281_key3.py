"""On the LAW's own instances: when P = op(x,Z) fires, is x = a1 (a1 Z)?  Which rule fired?
Also: over the whole memo, classify the R3-fired pairs (a1 v free-shaped or not)."""
import sys, os, collections, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _x32281_lib import *
from _x32281_try1 import R1
from _x32281_try2 import R3
import closedform as cf, fuzz as fz, smallcheck as sc
from freemodel import size

RULES = [R1, R3]

def r1_struct(u, v):
    try:
        return (v[0] == 'J' and v[1][0] == 'J' and v[1][1] == u and v[1][2][0] == 'J'
                and v[1][2][1][0] == 'J' and v[1][2][1][2] == v[1][2][2] and v[1][2][1][2] == v[2])
    except Exception:
        return False

st = collections.Counter()
examples = []

def law_probe(C, insts):
    A, B = LAW[1]
    for s in insts:
        try:
            x, Y, Z = s['x'], s['z'], s['y']
            P = C.op(x, Z)
        except (RecursionError, KeyError):
            continue
        if P[0] == 'J' and P[1] == x and P[2] == Z:
            st['P free'] += 1
            continue
        st['P fired'] += 1
        st['P fired R1' if r1_struct(x, Z) else 'P fired R3'] += 1
        key = (Z[0] == 'J' and Z[1][0] == 'J' and Z[1][1] == x)
        st['KEY ok' if key else 'KEY BAD'] += 1
        if not key and len(examples) < 4:
            examples.append((x, Y, Z))

# gather instances the same way the validator does
import types
random.seed(1)
for sd in (3, 4, 5, 101, 202, 303):
    C = cf.Closed(LAW, RULES)
    # deep_tests generates its own; re-do a light version here to capture assignments
    insts = []
    rnd = random.Random(sd)
    from freemodel import rand_term
    pool = [('g', i) for i in range(4)]
    for i in range(6000):
        if rnd.random() < 0.4 and len(pool) < 2000:
            a, b, c = (rnd.choice(pool) for _ in range(3))
            t = ('J', ('J', a, ('J', ('J', b, c), c)), c)
            if size(t) <= 200:
                pool.append(t)
        insts.append({'x': rnd.choice(pool), 'z': rnd.choice(pool), 'y': rnd.choice(pool)})
    law_probe(C, insts)
    # and the real workloads (they populate the memo with adversarial pairs)
    cf.deep_tests(C, LAW, 4000, 180, sd)
    fz.critical_fuzz(C, LAW, 8000, seed=sd + 300)
    fz.closure_fuzz(C, LAW, 8000, seed=sd + 200)

print(dict(st))

# whole-memo classification of R3 fires
C = cf.Closed(LAW, RULES)
for sd in (3, 4, 5):
    cf.deep_tests(C, LAW, 6000, 200, sd)
    fz.fuzz(C, LAW, RULES, 10000, seed=sd + 100)
    fz.critical_fuzz(C, LAW, 10000, seed=sd + 300)
s2 = collections.Counter()
for (u, v), w in C.memo.items():
    if w[0] == 'J' and w[1] == u and w[2] == v:
        continue
    if r1_struct(u, v):
        s2['R1'] += 1
    else:
        s2['R3'] += 1
        s2['R3 KEYok' if (v[0] == 'J' and v[1][0] == 'J' and v[1][1] == u) else 'R3 KEYBAD'] += 1
print(dict(s2))

def sh(t): return 'g%d' % t[1] if t[0] == 'g' else '(' + sh(t[1]) + '*' + sh(t[2]) + ')'
for x, Y, Z in examples:
    print('KEYBAD law instance: x=', sh(x)[:80], ' Z=', sh(Z)[:160])
