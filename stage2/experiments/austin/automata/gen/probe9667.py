"""probe9667.py : over the deep-test + fuzz distribution, for law 9667 record which of the products in
op y (op (op z y) (op x (op y y))) fire a rule (reduce) vs stay free, so the Lean case analysis is complete."""
import sys, os, random, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import closedform as cf
import fuzz as fz
import freetest2 as ft
from freemodel import normalise, catalog, size, pvars
from laws import parse_eq

law = normalise(parse_eq(catalog()[9667]))
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chk9667.py'), encoding='utf-8').read()
     .split('C = cf.Closed')[0].split('law = ')[1].join(['rules = ', '']) if False else 'pass')
# load rules from chk9667.py
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chk9667.py'), encoding='utf-8').read()
exec(src[src.index('rules = '):src.index('C = cf.Closed')])

def J(a, b): return ('J', a, b)
def freeq(C, u, v):
    return C.op(u, v) == J(u, v)

def classify(C, s):
    x, y, z = s['x'], s['y'], s['z']
    yy = C.op(y, y)
    xyy = C.op(x, yy)
    zy = C.op(z, y)
    mid = C.op(zy, xyy)
    outer = C.op(y, mid)
    tags = []
    tags.append('yy' + ('F' if yy == J(y, y) else 'R'))
    tags.append('xyy' + ('F' if xyy == J(x, yy) else 'R'))
    tags.append('zy' + ('F' if zy == J(z, y) else 'R'))
    tags.append('mid' + ('F' if mid == J(zy, xyy) else 'R'))
    tags.append('out' + ('F' if outer == J(y, mid) else 'R'))
    return tuple(tags), outer == x

cnt = collections.Counter()
bad = []
random.seed(1)
class Shim: pass
F = Shim(); F.vars = pvars(law[1]); F.rhs = law[1]; F.ev = lambda p, sub: cf.Closed(law, rules).evp(p, sub)
pool = []
C = cf.Closed(law, rules)
for i in range(60000):
    s = ft.nested_triple(F, pool)
    if max(size(t) for t in s.values()) > 120: continue
    for t in s.values():
        if size(t) <= 40 and len(pool) < 400: pool.append(t)
    try:
        tags, ok = classify(C, s)
    except RecursionError:
        continue
    cnt[tags] += 1
    if not ok and len(bad) < 5:
        bad.append({k: size(v) for k, v in s.items()})
# also structured fuzz pool
random.seed(7)
poolf = [('g', i) for i in range(3)]
for d in range(3):
    for u, v in fz.instances(rules, poolf, 8, d, C):
        for t in (u, v, C.op(u, v)):
            if size(t) <= 60 and t not in poolf: poolf.append(t)
    if len(poolf) > 2000: poolf = poolf[:2000]
vs = pvars(law[1])
for i in range(60000):
    s = {v: random.choice(poolf) for v in vs}
    r = random.random()
    if r < 0.35:
        a, b = random.sample(vs, 2); s[a] = s[b]
    elif r < 0.6:
        try: s[random.choice(vs)] = C.op(random.choice(poolf), random.choice(poolf))
        except RecursionError: pass
    if max(size(t) for t in s.values()) > 140: continue
    try:
        tags, ok = classify(C, s)
    except RecursionError:
        continue
    cnt[tags] += 1
    if not ok and len(bad) < 5:
        bad.append({k: size(v) for k, v in s.items()})

print("distinct firing patterns (product freeness: F=free, R=reduced), sorted by count:")
for tags, n in cnt.most_common():
    print("  %6d  %s" % (n, ' '.join(tags)))
print("total", sum(cnt.values()), "law violations:", len(bad), bad)
