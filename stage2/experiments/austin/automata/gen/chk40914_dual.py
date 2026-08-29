"""chk40914_dual.py [N] : deep tests + coincidence-targeted tests of the 40914 rule set against the DUAL L-form law
x = z * (x * (z * (y * (x * y))))  (the skeleton's op models the dual; gen/chk40914.py tested the undualised R-form pattern,
which is why it reports 3000/3000 failures)."""
import sys, os, random, itertools
sys.path.insert(0, 'C:\\Users\\nacho\\Documents\\GitHub\\magma-ai\\stage2\\experiments\\austin\\automata')
import closedform as cf
from freemodel import normalise, catalog
from laws import parse_eq, dual

orig = normalise(parse_eq(catalog()[40914]))
law = (orig[0], dual(orig[1]))
print('original :', orig)
print('dual law :', law)
rules = [([('TG', ('V',)), ('TG', ('A2', ('V',))), ('EQ', ('U',), ('A1', ('A2', ('V',)))), ('TG', ('A2', ('A2', ('V',)))), ('TG', ('A2', ('A2', ('A2', ('V',))))), ('EQ', ('A1', ('V',)), ('A1', ('A2', ('A2', ('A2', ('V',)))))), ('EQ', ('A1', ('A2', ('A2', ('V',)))), ('A2', ('A2', ('A2', ('A2', ('V',))))))], ('A1', ('V',)), 'free'), ([('TG', ('V',)), ('TG', ('A2', ('V',))), ('EQ', ('U',), ('A1', ('A2', ('V',)))), ('TG', ('A2', ('A2', ('V',)))), ('OPEQ', ('OP', ('A1', ('V',)), ('A1', ('A2', ('A2', ('V',))))), ('A2', ('A2', ('A2', ('V',)))))], ('A1', ('V',)), 'B111l')]

N = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
for seed in (11, 12):
    C = cf.Closed(law, rules)
    tested, fails = cf.deep_tests(C, law, N, 300, seed)
    print('deep_tests seed', seed, ': tested', tested, 'fails', len(fails), 'fired', C.fired)
    if fails:
        print('FIRST FAIL', fails[0])

# the five products of the dual law
def lawval(C, x, y, z):
    q1 = C.op(x, y); q2 = C.op(y, q1); q3 = C.op(z, q2); q4 = C.op(x, q3); return C.op(z, q4)

def subterms(t, acc):
    acc.add(t)
    if t[0] == 'J':
        subterms(t[1], acc); subterms(t[2], acc)
    return acc

C = cf.Closed(law, rules)
random.seed(40914)
g = lambda i: ('g', i)
base = [g(0), g(1), g(2)]
pool = list(base)
# close a small pool under J and op
for _ in range(2):
    new = []
    for a in pool:
        for b in pool:
            new.append(('J', a, b)); new.append(C.op(a, b))
    pool = list({t for t in pool + new if cf.size(t) <= 25})
pool.sort(key=lambda t: (cf.size(t), str(t)))
pool = pool[:12] + random.sample(pool[12:], min(28, max(0, len(pool) - 12)))
print('pool size', len(pool))
bad = 0; cnt = 0
for x in pool:
    for y in pool:
        for z in pool:
            cnt += 1
            if lawval(C, x, y, z) != x:
                bad += 1
                if bad <= 3: print('FAIL exhaustive', x, y, z, lawval(C, x, y, z))
print('exhaustive triples over pool:', cnt, 'fails', bad)

# targeted: R2-shaped and R1-shaped y with x, z from its subterms/products
bad = 0; cnt = 0
for it in range(4000):
    a, b, c, d = (random.choice(pool) for _ in range(4))
    shapes = [('J', a, ('J', c, ('J', b, C.op(a, b)))),          # R2 shape for u = c
              ('J', a, ('J', c, ('J', b, ('J', a, b)))),         # R1 shape for u = c
              ('J', a, ('J', c, ('J', b, d))),
              ('J', c, ('J', a, ('J', c, ('J', b, C.op(a, b))))),
              ('J', d, ('J', a, ('J', c, ('J', b, C.op(a, b)))))]
    y = random.choice(shapes)
    cands = list(subterms(y, set())) + [a, b, c, d, C.op(a, b), C.op(c, y), C.op(y, y), C.op(a, y)]
    cands = [t for t in cands if cf.size(t) <= 60]
    for x in random.sample(cands, min(6, len(cands))):
        for z in random.sample(cands, min(6, len(cands))):
            cnt += 1
            for (xx, yy, zz) in ((x, y, z), (y, x, z), (x, z, y), (z, y, x), (y, y, x), (x, y, y), (x, y, x), (z, y, z)):
                if lawval(C, xx, yy, zz) != xx:
                    bad += 1
                    if bad <= 3: print('FAIL targeted', xx, yy, zz)
print('targeted instances:', cnt, 'fails', bad, 'fired', C.fired, 'cycles', C.cycles)
