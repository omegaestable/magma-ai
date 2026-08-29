"""fuzz8485.py [N] [seed] : encoding-closure fuzz for law 8485 on the shipped rules of gen/rec8485.lean.
The pool is closed under enc(key a; payload b, junk q) = b * (((q*b)*a)*a) evaluated in the model, plus products;
the law is tested on random triples from the pool.  Prints the failure rate and the smallest failing instances."""
import sys, os, random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import closedform as cf
from freemodel import normalise, catalog, size
from laws import parse_eq
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chk8485.py'), encoding='utf-8').read()
exec(src[src.index('rules = '):src.index('C = cf.Closed')])
law = normalise(parse_eq(catalog()[8485]))
A, B = law[1]
N = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
seed = int(sys.argv[2]) if len(sys.argv) > 2 else 1
random.seed(seed)
C = cf.Closed(law, rules)
def which_rule(u, v):
    for i, (conds, e, tag) in enumerate(rules):
        if C.check(conds, u, v) and C.ev(e, u, v) is not None: return 'R%d' % (i + 1)
    return 'free'
def trace(s):
    x, y, z = s['x'], s['y'], s['z']
    P = C.op(z, x); Q = C.op(P, y); R = C.op(Q, y); S = C.op(x, R); T = C.op(y, S)
    return ' | '.join('%s:%s' % (n, which_rule(a, b)) for n, a, b in [('z*x', z, x), ('P*y', P, y), ('Q*y', Q, y), ('x*R', x, R), ('y*S', y, S)])
def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s %s)' % (show(t[1]), show(t[2]))
pool = [('g', 0), ('g', 1), ('g', 2)]
fails = []; tested = 0
for it in range(N):
    a, b, q = (random.choice(pool) for _ in range(3))
    r = random.random()
    if r < 0.6: t = C.evp(B, {'x': b, 'y': a, 'z': q})     # a-encoding of b
    elif r < 0.8: t = C.op(a, b)
    else: t = ('J', a, b)
    if size(t) <= 45: pool.append(t)
    if len(pool) > 300: pool.pop(random.randrange(3, len(pool)))
    s = {v: random.choice(pool) for v in ('x', 'y', 'z')}
    if random.random() < 0.3: s['z'] = s['x']
    tested += 1
    lhs = C.op(C.evp(A, s), C.evp(B, s))
    if lhs != s['x']: fails.append((size(s['x']) + size(s['y']) + size(s['z']), s))
fails.sort(key=lambda f: f[0])
print('tested', tested, 'fails', len(fails), 'rate', round(len(fails) / max(tested, 1), 4))
seen = set()
for tot, s in fails:
    tr = trace(s)
    if tr in seen: continue
    seen.add(tr)
    print('  sizes', size(s['x']), size(s['y']), size(s['z']), '|', tr)
    print('    x =', show(s['x'])); print('    y =', show(s['y'])); print('    z =', show(s['z']))
    if len(seen) >= 6: break
