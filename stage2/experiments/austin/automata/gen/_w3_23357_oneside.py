"""Is 23354's ONESIDE true for the validated 4-rule 23357 model?

ONESIDE : no term x is both the RIGHT argument of a decoding pair and the LEFT argument of one,
          i.e. no x with (op u x != J u x) and (op x w != J x w) for some u, w.
It is the lemma that closes the law's last cell (A decoded AND V decoded).  Search a pool built the
same way the gap hunter builds one, plus the chain products of random instances.
"""
import sys, random, collections
D = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, D)
import closedform as cf, trace as tr, fuzz as fz
from freemodel import size, rand_term
import importlib.util
spec = importlib.util.spec_from_file_location('_f4', D + '/gen/_w3_23357_f4.py')
m = importlib.util.module_from_spec(spec)
argv = list(sys.argv); sys.argv = [sys.argv[0]]
spec.loader.exec_module(m)
law, rules = m.law, m.rules
show = tr.show
C = cf.Closed(law, rules)
dec = lambda a, b: C.op(a, b) != ('J', a, b)

random.seed(int(argv[1]) if len(argv) > 1 else 7)
pool = [('g', i) for i in range(4)]
for d in range(3):
    for u, v in fz.instances(rules, pool, 10, d, C):
        for t in (u, v):
            if size(t) <= 70 and t not in pool:
                pool.append(t)
        try:
            r = C.op(u, v)
            if size(r) <= 70 and r not in pool:
                pool.append(r)
        except RecursionError:
            pass
for _ in range(400):
    t = rand_term(random.randint(1, 5), 3)
    if t not in pool:
        pool.append(t)
print('pool', len(pool), flush=True)

RIGHT = {}   # x -> (u) with op u x decoding
LEFT = {}    # x -> (w) with op x w decoding
for a in pool:
    for b in pool:
        try:
            if dec(a, b):
                RIGHT.setdefault(b, a)
                LEFT.setdefault(a, b)
        except RecursionError:
            pass
both = sorted(set(RIGHT) & set(LEFT), key=size)
print('right-args %d  left-args %d  BOTH %d' % (len(RIGHT), len(LEFT), len(both)), flush=True)
for x in both[:5]:
    u, w = RIGHT[x], LEFT[x]
    print('  x =', show(x)[:220], flush=True)
    print('     u =', show(u)[:220], '   op u x =', show(C.op(u, x))[:120], flush=True)
    print('     w =', show(w)[:220], '   op x w =', show(C.op(x, w))[:120], flush=True)
