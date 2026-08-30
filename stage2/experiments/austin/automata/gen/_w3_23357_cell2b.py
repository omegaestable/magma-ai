"""Is the law's cell 2b (A = op y x decoded AND V = op x (op y z) decoded) REACHABLE for the f4 model?

ONESIDE is false as a general statement here (gen/_w3_23357_oneside.py: 8 both-sided terms in a
434-term pool), but the law only needs the cell to be unreachable ALONG ITS OWN CHAIN, where the same
`y` appears in `A = op y x` and in `B = op y z`.
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
J = lambda a, b: ('J', a, b)
dec = lambda a, b: C.op(a, b) != ('J', a, b)

random.seed(int(argv[1]) if len(argv) > 1 else 11)
pool = [('g', i) for i in range(4)]
for d in range(3):
    for u, v in fz.instances(rules, pool, 12, d, C):
        for t in (u, v):
            if size(t) <= 70 and t not in pool:
                pool.append(t)
        try:
            r = C.op(u, v)
            if size(r) <= 70 and r not in pool:
                pool.append(r)
        except RecursionError:
            pass
for _ in range(300):
    t = rand_term(random.randint(1, 5), 3)
    if t not in pool:
        pool.append(t)
zs = [t for t in pool if size(t) <= 25]
print('pool %d  z-candidates %d' % (len(pool), len(zs)), flush=True)

cells = collections.Counter(); found = []
n = 0
for y in pool:
    for x in pool:
        try:
            if not dec(y, x):
                continue                      # want A decoded
        except RecursionError:
            continue
        A = C.op(y, x)
        for z in zs:
            try:
                B = C.op(y, z); V = C.op(x, B)
                U = C.op(A, y); top = C.op(U, V)
            except RecursionError:
                continue
            n += 1
            cell = ('AD', 'UD' if U != J(A, y) else 'UF',
                    'BD' if B != J(y, z) else 'BF', 'VD' if V != J(x, B) else 'VF')
            cells[cell] += 1
            if cell[3] == 'VD':
                found.append((x, y, z, top == x))
print('tested %d triples with A decoded' % n, flush=True)
for k, c in cells.most_common():
    print('   %-24s %d' % (str(k), c), flush=True)
print('cell 2b (A and V both decoded) hits:', len(found), flush=True)
for x, y, z, ok in found[:3]:
    print('   law holds =', ok, ' x =', show(x)[:150], flush=True)
    print('        y =', show(y)[:150], '  z =', show(z)[:80], flush=True)
