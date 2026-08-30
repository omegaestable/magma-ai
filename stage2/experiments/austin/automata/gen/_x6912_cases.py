"""Case table for the 4-rule 6912 model: which rule fires at each of the 5 chain products.

Products, in evaluation order:
  S = op z z ;  E = op x y ;  W = op S E ;  B = op y W ;  F = op y B  (must be x)
"""
import sys, os, random, pickle, collections
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen')
import closedform as cf, trace as TR
from freemodel import size, rand_term
import _x6912_rep as R

law = R.law
rules = pickle.load(open('gen/_x6912_four.pkl', 'rb')) if os.path.exists('gen/_x6912_four.pkl') else \
        [r for r in R.VARIANTS['bare'] if r[2] in {'free', 'B11l', 'B1l,B11v', 'B1v-struct'}]
tags = [r[2] for r in rules]
print('rules:', tags)

C = TR.Tracing(law, rules)

def fire(a, b):
    C.trace_on = True; C.log = []
    r = C.op(a, b)
    C.trace_on = False
    which = C.log[-1][2] if C.log else None
    return r, (None if which is None else which + 1)

def chain(x, y, z):
    S, rS = fire(z, z)
    E, rE = fire(x, y)
    W, rW = fire(S, E)
    B, rB = fire(y, W)
    F, rF = fire(y, B)
    return (rS, rE, rW, rB, rF), (F == x), dict(S=S, E=E, W=W, B=B, F=F)

tab = collections.Counter()
bad = []
random.seed(20260829)
pool = []
for d in (0, 1, 2, 3):
    for _ in range(400):
        pool.append(rand_term(d))
# structured pool: encodings of each other
for trial in range(60000):
    x = random.choice(pool); y = random.choice(pool); z = random.choice(pool)
    mode = random.randrange(6)
    if mode == 1:
        z2 = random.choice(pool); x = ('J', z2, z2)
    if mode == 2:
        w = random.choice(pool); b = random.choice(pool)
        y = ('J', ('J', b, b), ('J', w, x))
    if mode == 3:
        z2 = random.choice(pool); x = ('J', z2, z2)
        w = random.choice(pool); b = random.choice(pool)
        y = ('J', ('J', b, b), ('J', w, x))
    if mode == 4:
        y = ('J', ('J', z, z), random.choice(pool))
    if mode == 5:
        y = ('J', x, random.choice(pool))
    if size(x) + size(y) + size(z) > 60: continue
    try:
        k, ok, vals = chain(x, y, z)
    except RecursionError:
        continue
    tab[k] += 1
    if not ok and len(bad) < 8:
        bad.append((x, y, z, k, vals))
for k, n in sorted(tab.items(), key=lambda t: -t[1]):
    print('  S=%s E=%s W=%s B=%s F=%s   x%d' % (*[('free' if q is None else 'R%d' % q) for q in k], n))
print('failures:', len(bad))
for x, y, z, k, vals in bad:
    print('  x=%s y=%s z=%s  %s' % (TR.show(x), TR.show(y), TR.show(z), k))
