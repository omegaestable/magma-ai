"""qz_validate24.py -- the full validation battery for gen/qz_m24.py (law 12073).

Run:  PYTHONIOENCODING=utf-8 python gen/qz_validate24.py
Every number printed here is quoted in the session report.  The `identity` probe is the one that
matters: it builds x out of the model's OWN codes (E_y = psi_y(y)*Sq(z), then codes of codes) and it
is what refuted models 15/16/17/18, all of which passed 130k-assignment exhaustive checks and 240k
deep random tests first.
"""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qz_lib as L
import qz_m24 as M

law, txt = L.law_of(M.EQ)
L.UN = list(M.UN)
L.CONST = list(M.CONST)
op = M.op
out = {}

t0 = time.time()
for ms, g in ((5, 1), (5, 2)):
    n, pool, f = L.exhaustive(op, law, ms, g, M.CT, limit=5, un=M.UN)
    out['exhaustive_%d/%d' % (ms, g)] = dict(pool=len(pool), assignments=n, fails=len(f))

# (y,x) exhaustive to size 7 (1 generator) x every z of size <= 3 (2 generators)
pool = L.terms_upto(7, 1, ('P',), ('C',))
zs = L.terms_upto(3, 2, ('P',), ('C',))
n = 0
f = []
for y in pool:
    for x in pool:
        u2 = op(op(op(y, x), x), x) if False else op(op(y, x), x)
        for z in zs:
            n += 1
            if op(y, op(u2, op(z, z))) != x:
                f.append((y, x, z))
out['exhaustive_yx7g1_z3g2'] = dict(pool=len(pool), zs=len(zs), assignments=n, fails=len(f))

for N, seeds in ((60000, (11, 23, 37, 101, 202)),):
    tot = {}
    nf = 0
    for sd in seeds:
        for name, fn, k in (('deep', L.deep_tests, N), ('closure', L.closure_tests, N // 2),
                            ('critical', L.critical_tests, N // 2)):
            c, ff = fn(op, law, k, sd, gens=3, ctors=M.CT, depth=3)
            tot[name] = tot.get(name, 0) + c
            nf += len(ff)
    out['random'] = dict(seeds=list(seeds), counts=tot, fails=nf)

n, f = L.identity_probe(op, law, gens=3, ctors=M.CT, depth=3, seeds=tuple(range(1, 41)), rounds=1500)
out['identity_probe'] = dict(instances=n, fails=len(f))

import random
rng = random.Random(9)
bad = sum(1 for _ in range(5000) if op(*(lambda a: (a, a))(L.rand_term(3, 3, M.CT, rng))) != M.E)
out['square_is_E_violations'] = bad
out['secs'] = round(time.time() - t0, 1)
print(json.dumps(out, indent=1))
