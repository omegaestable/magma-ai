"""_x33020_cases.py : which rule fires at each product of the 12883 chain, over deep+fuzz instances.
Chain: s1 = op y x, s2 = op z s1, s3 = op x s2, s4 = op s3 y, T = op y s4.
Prints the histogram of (r1,r2,r3,r4,rT) and, for each distinct pattern, a witness instance.
"""
import sys, os, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import closedform as cf, fuzz as fz, leangen
from freemodel import normalise, catalog, size
from laws import parse_eq

cat = catalog(); orig = normalise(parse_eq(cat[33020]))
law = ('x', leangen.dual_pat(orig[1]))
src = open(os.path.join(HERE, 'repair33020', 'chk33020.py'), encoding='utf-8').read()
ns = {}
exec(src[src.index('rules = '):src.index('C = cf.Closed')], {'cf': cf}, ns)
rules = ns['rules']

def which(C, u, v):
    for i, (conds, e, tag) in enumerate(rules):
        if C.check(conds, u, v) and C.ev(e, u, v) is not None:
            return 'R%d' % (i + 1)
    return '.'

def pat(C, s):
    x, y, z = s['x'], s['y'], s['z']
    s1 = C.op(y, x); s2 = C.op(z, s1); s3 = C.op(x, s2); s4 = C.op(s3, y); T = C.op(y, s4)
    return (which(C, y, x), which(C, z, s1), which(C, x, s2), which(C, s3, y), which(C, y, s4)), T == x

hist = collections.Counter(); wit = {}
import random
for seed in range(1, 9):
    C = cf.Closed(law, rules)
    tested, fails = cf.deep_tests(C, law, 8000, 200, seed)
    # deep_tests does not hand back the assignments; re-do our own sampling instead
for seed in range(1, 7):
    rng = random.Random(seed)
    C = cf.Closed(law, rules)
    A, B = law[1]
    def rnd(d):
        if d <= 0 or rng.random() < 0.35:
            return ('g', rng.randrange(3))
        return ('J', rnd(d - 1), rnd(d - 1))
    for _ in range(4000):
        s = {'x': rnd(rng.randrange(4)), 'y': rnd(rng.randrange(4)), 'z': rnd(rng.randrange(4))}
        if rng.random() < 0.5:
            # coincidence-flavoured: rebuild one variable as an encoding of the others
            try:
                s2 = dict(s)
                enc = C.evp(B, s2)
                which_v = rng.choice('xyz')
                s[which_v] = enc
            except Exception:
                pass
        try:
            p, ok = pat(C, s)
        except RecursionError:
            continue
        hist[(p, ok)] += 1
        if p not in wit:
            wit[p] = s
for seed in (7, 8, 9):
    C = cf.Closed(law, rules)
    try:
        tested, fails = fz.fuzz(C, law, rules, 4000, seed=seed)
    except Exception as e:
        print('fuzz err', e)

for (p, ok), n in sorted(hist.items(), key=lambda kv: -kv[1]):
    print('%-30s ok=%-5s %6d' % ('/'.join(p), ok, n))
print()
def show(t): return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))
for p, s in sorted(wit.items()):
    print('/'.join(p), '  sizes', {k: size(v) for k, v in s.items()})
