"""_x38565_cand2.py -- heavy validation of SET A for law 38565 (rules free, B101l, B1l),
plus hand-built coincidence instances."""
import sys, os, time, pickle, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import closedform as cf, revalidate as rv, leangen
import fuzz as fz
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 38565
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = ('x', leangen.dual_pat(orig[1]))
with open(os.path.join(HERE, '_x38565_full.pkl'), 'rb') as f:
    full = pickle.load(f)
rules = [full[i] for i in (0, 1, 6)]
for r in rules:
    print(cf.show_rule(r))

g = lambda n: ('g', n)
J = lambda a, b: ('J', a, b)


def ev(o, p, s):
    if isinstance(p, str):
        return s[p]
    return o.op(ev(o, p[0], s), ev(o, p[1], s))


# --- hand coincidence instances: x, y, z built out of the model's own encodings ---
C = cf.Closed(law, rules)


def enc(x, y, z):
    """the free encoding of the law's RHS: y * (y * ((z*(x*z))*y)) evaluated by the model"""
    return ev(C, law[1], {'x': x, 'y': y, 'z': z})


bad = 0
cases = []
gens = [g(0), g(1), g(2)]
# (i) y is an encoding of something
for a in gens:
    for b in gens:
        for c in gens:
            E = enc(a, b, c)
            cases.append(('y=enc', {'x': a, 'y': E, 'z': c}))
            cases.append(('x=enc', {'x': E, 'y': b, 'z': c}))
            cases.append(('z=enc', {'x': a, 'y': b, 'z': E}))
            s2 = C.op(c, C.op(a, c))
            cases.append(('y=J(s2,g)', {'x': a, 'y': J(s2, b), 'z': c}))
            cases.append(('y=J(s2,enc)', {'x': a, 'y': J(s2, E), 'z': c}))
            s3 = C.op(s2, b)
            cases.append(('y=J(s2,s3)', {'x': a, 'y': J(s2, s3), 'z': c}))
            cases.append(('z=J(a,J(b,a))', {'x': a, 'y': b, 'z': J(a, J(b, a))}))
            cases.append(('x=s2', {'x': s2, 'y': b, 'z': c}))
            cases.append(('y=s2', {'x': a, 'y': s2, 'z': c}))
            cases.append(('y=s3', {'x': a, 'y': s3, 'z': c}))
# (ii) nested one level: encode with encodings as parts
for a in gens[:2]:
    for b in gens[:2]:
        for c in gens[:2]:
            E = enc(a, b, c)
            E2 = enc(E, b, c)
            cases.append(('nest1', {'x': E, 'y': E2, 'z': c}))
            cases.append(('nest2', {'x': a, 'y': enc(a, E, c), 'z': E}))
            cases.append(('nest3', {'x': E2, 'y': b, 'z': E}))
seen = set()
for name, s in cases:
    k = (s['x'], s['y'], s['z'])
    if k in seen:
        continue
    seen.add(k)
    got = ev(C, law[1], s)
    if got != s['x']:
        bad += 1
        print('HAND FAIL', name, {kk: size(vv) for kk, vv in s.items()})
print('hand instances: %d distinct, %d fails' % (len(seen), bad))

for seeds in ([3, 4, 5], [77, 78, 79], [101, 202, 303]):
    t0 = time.time()
    f = rv.run_tests(law, rules, seeds, 3000, 12000)
    f = [q for q in f if q[1] != 'recursion']
    print('run_tests %-14s fails %d (%.1fs)' % (str(seeds), len(f), time.time() - t0))
    for q in f[:2]:
        print('  ', {k: size(v) for k, v in q[0].items()})

C2 = cf.Closed(law, rules)
tot = 0
for seed in (1, 2, 3, 55, 606, 7007, 80808, 999983):
    tested, fl = cf.deep_tests(C2, law, 20000, 300, seed)
    fl = [q for q in fl if q[1] != 'recursion']
    tot += len(fl)
    print('deep seed %-8d tested %5d fails %d' % (seed, tested, len(fl)))
print('TOTAL extra deep fails', tot)
