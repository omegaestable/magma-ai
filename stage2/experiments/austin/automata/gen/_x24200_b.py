"""Test the structural claims needed for the Lean proof of law 24200.

FREE : op (op a b) b = J (op a b) b
R    : op y x = J y x  OR  (a) tg T1 = 2 & a2 T1 = x
                       OR  (b) tg x = 2 & tg (a1 x) = 2 & a1 (a1 x) = T1 & a2 (a1 x) = a2 x
                       OR  (c) tg x = 2 & a1 x = op T1 (a2 x)          (T1 = op y x)
DIG  : op u v = J u v  OR  op u v = a2 u  OR  op u v = u
SELF : op u v = u  ->  tg u = 2 & a1 u = op u (a2 u)
"""
import sys, os, random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import closedform as cf
import fuzz as fz
from freemodel import normalise, catalog, size, rand_term
from laws import parse_eq
from collections import Counter

eq = 24200
cat = catalog(); law = normalise(parse_eq(cat[eq]))
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chk%d.py' % eq)
src = open(p, encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns)
rules = ns['rules']
C = cf.Closed(law, rules)

def a1(t): return t[1] if t[0] == 'J' else t
def a2(t): return t[2] if t[0] == 'J' else t
def tg(t): return 2 if t[0] == 'J' else 1

def which_rule(u, v):
    for i, (conds, xexp, tag) in enumerate(rules):
        if C.check(conds, u, v):
            r = C.ev(xexp, u, v)
            if r is not None:
                return i, r
    return None, ('J', u, v)

seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
N = int(sys.argv[2]) if len(sys.argv) > 2 else 20000
random.seed(seed)
pool = [('g', i) for i in range(4)]
for depth in range(4):
    inst = fz.instances(rules, pool, 60, depth, C)
    for u, v in inst:
        try:
            t1 = C.op(u, v)
        except RecursionError:
            continue
        for t in (u, v, t1):
            if size(t) <= 60 and t not in pool: pool.append(t)
    if len(pool) > 1500: pool = pool[:1500]
print("pool size", len(pool))

def all_trees(depth, gens):
    if depth == 0:
        for g in gens: yield g
        return
    for g in gens: yield g
    for a in all_trees(depth - 1, gens):
        for b in all_trees(depth - 1, gens):
            yield ('J', a, b)

gens = [('g', 0), ('g', 1), ('g', 2)]
small = list(all_trees(3, gens))
print("small trees (depth<=3):", len(small))

badFREE = []; badR = Counter(); badRex = {}; badDIG = []; badSELF = []
Rhist = Counter(); innerrule = Counter()

def check_pair(y, x):
    try:
        T1 = C.op(y, x)
        T2 = C.op(T1, x)
    except RecursionError:
        return
    if T2 != ('J', T1, x):
        if len(badFREE) < 5: badFREE.append((y, x, T1, T2))
    w, res = which_rule(y, x)
    innerrule[(w + 1) if w is not None else None] += 1
    # DIG
    if T1 != ('J', y, x):
        if not (T1 == a2(y) or T1 == y):
            if len(badDIG) < 5: badDIG.append((y, x, T1))
        if T1 == y:
            try:
                q = C.op(y, a2(y))
            except RecursionError:
                q = None
            if not (tg(y) == 2 and q == a1(y)):
                if len(badSELF) < 5: badSELF.append((y, x, T1, q))
    # R
    if T1 == ('J', y, x):
        Rhist['free'] += 1; return
    ca = tg(T1) == 2 and a2(T1) == x
    cb = tg(x) == 2 and tg(a1(x)) == 2 and a1(a1(x)) == T1 and a2(a1(x)) == a2(x)
    try:
        cc = tg(x) == 2 and a1(x) == C.op(T1, a2(x))
    except RecursionError:
        cc = False
    Rhist[(ca, cb, cc)] += 1
    if not (ca or cb or cc):
        badR[(w + 1) if w is not None else None] += 1
        if (w + 1) not in badRex: badRex[w + 1] = (y, x, T1)

for _ in range(N):
    r = random.random()
    if r < 0.5:
        y = random.choice(pool); x = random.choice(pool)
    else:
        y = rand_term(random.choice([1, 2, 3, 4, 5]))
        x = rand_term(random.choice([1, 2, 3, 4, 5]))
    check_pair(y, x)

for y in small:
    for x in small:
        check_pair(y, x)

print("FREE violations:", len(badFREE), badFREE[:2])
print("DIG violations:", len(badDIG), badDIG[:2])
print("SELF violations:", len(badSELF), badSELF[:2])
print("R violations by inner rule:", dict(badR))
for k, v in badRex.items(): print("   ex rule", k, v)
print("R histogram (ca,cb,cc):", dict(Rhist))
print("inner rule histogram:", dict(innerrule))
