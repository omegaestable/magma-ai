"""CASE TREE for law 11081 (W3-6 step 3).

chain:  A = op(y,x)   B = op(x,A)   C = op(z,y)   D = op(B,C)   TOP = op(y,D) = x ?

Every instance is CONSTRUCTED by chained encoding, never sampled: the pool starts from generators
and is closed under `encR(p,u,w) = J (J p (op u p)) (J w u)` (the term that decodes to p under key
u by rule 1), so a term in generation k is an encoding nested k deep.  The cell of an instance is
(branch at A, at B, at C, at D); '.' = free, 'Dk' = rule k fired.

usage: python gen/_v11081_ct.py <setname> [generations]
"""
import sys, os, collections, itertools, random
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE)
sys.path.insert(0, HERE + '/gen')
import closedform as cf
from freemodel import normalise, catalog, size
from laws import parse_eq
from _v11081_rs import SETS

EQ = 11081
cat = catalog()
law = normalise(parse_eq(cat[EQ]))
NAME = sys.argv[1] if len(sys.argv) > 1 else 'x12'
GEN = int(sys.argv[2]) if len(sys.argv) > 2 else 2
rules = SETS[NAME]
print('rule set', NAME, ' generations', GEN)
for r in rules:
    print('  ', cf.show_rule(r))

g = lambda n: ('g', n)
J = lambda a, b: ('J', a, b)
a1_ = lambda t: t[1] if t[0] == 'J' else t
a2_ = lambda t: t[2] if t[0] == 'J' else t


def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s.%s)' % (show(t[1]), show(t[2]))


def branch(C, u, v):
    for i, (conds, x, tag) in enumerate(C.rules):
        if C.check(conds, u, v) and C.ev(x, u, v) is not None:
            return i + 1
    return 0


def mark(C, u, v):
    b = branch(C, u, v)
    return 'D%d' % b if b else '.'


C0 = cf.Closed(law, rules)
encR = lambda p, u, w: J(J(p, C0.op(u, p)), J(w, u))

BASE = [g(0), g(1), g(2), J(g(0), g(1)), J(J(g(0), g(1)), g(2))]
pool = list(BASE)
gens = [list(BASE)]
for k in range(GEN):
    nxt = []
    for p in gens[-1] if k else BASE:
        for u in BASE + (gens[-1] if k else []):
            for w in BASE[:3]:
                t = encR(p, u, w)
                if size(t) <= 260:
                    nxt.append(t)
    # also encode a previous-generation term under a base key
    for p in BASE[:3]:
        for u in gens[-1]:
            for w in BASE[:2]:
                t = encR(p, u, w)
                if size(t) <= 260:
                    nxt.append(t)
    seen = set()
    ded = []
    for t in nxt:
        if t not in seen:
            seen.add(t); ded.append(t)
    random.seed(7 + k)
    if len(ded) > 90:
        ded = random.sample(ded, 90)
    gens.append(ded)
    pool += ded
print('pool sizes per generation:', [len(x) for x in gens])

cells = collections.defaultdict(list)
fails = []
tested = 0


def probe(x, y, z, note):
    global tested
    if size(x) + size(y) + size(z) > 700:
        return
    C = cf.Closed(law, rules)
    try:
        a = C.op(y, x); b = C.op(x, a); c = C.op(z, y); d = C.op(b, c); r = C.op(y, d)
    except RecursionError:
        return
    tested += 1
    key = (mark(C, y, x), mark(C, x, a), mark(C, z, y), mark(C, b, c))
    cells[key].append((note, mark(C, y, d)))
    if r != x:
        fails.append((note, key, x, y, z, r))


# ---------- 1. staged construction: z, then y (forces C), then x (forces A) ----------
for z in BASE[:3] + gens[1][:12]:
    ys = BASE[:3] + [encR(p, z, w) for p in BASE[:3] for w in BASE[:2]]
    for y in ys:
        xs = BASE[:3] + [encR(p, y, w) for p in BASE[:3] for w in BASE[:2]]
        for x in xs:
            probe(x, y, z, 'staged')

# ---------- 2. deep pool: every product may decode at any level ----------
random.seed(11)
big = [t for t in pool if size(t) <= 200]
for _ in range(4000):
    x = random.choice(big); y = random.choice(big); z = random.choice(big)
    probe(x, y, z, 'deeppool')

# ---------- 3. D-forcing: make op(B,C) fire ----------
# rule-2 reading at (B,C):  a2 C = a1 (a1 B) = a1 x, with C free (= J z y) => y = a1 x,
# and op(B, a1 (a1 C)) = a2 (a1 C), satisfied by z = J q (op B q).
for x in [J(g(0), g(1)), J(J(g(0), g(1)), g(2)), J(g(0), J(g(1), g(2))),
          encR(g(0), g(1), g(2)), encR(J(g(0), g(1)), g(2), g(0))]:
    y = a1_(x)
    C = cf.Closed(law, rules)
    a = C.op(y, x); b = C.op(x, a)
    for q in BASE[:4]:
        probe(x, y, J(q, C.op(b, q)), 'Dforce2')
        probe(x, y, J(q, J(b, q)), 'Dforce2b')
# rule-1 reading at (B,C):  tg (a2 C) = 2 and B = a2 (a2 C); with C free that needs y = J _ B.
for x0 in BASE[:4]:
    for y0 in BASE[:4]:
        C = cf.Closed(law, rules)
        b0 = C.op(x0, C.op(y0, x0))
        for w in BASE[:3]:
            y = J(w, b0)
            for z in BASE[:3]:
                for x in BASE[:3] + [x0, b0]:
                    probe(x, y, z, 'Dforce1')

# ---------- 4. A-and-C simultaneously decoded, two levels deep ----------
for z in BASE[:3]:
    for p1 in BASE[:3]:
        for w1 in BASE[:2]:
            y1 = encR(p1, z, w1)
            for p2 in BASE[:2]:
                for w2 in BASE[:2]:
                    y2 = encR(p2, y1, w2)
                    for x in BASE[:2] + [encR(g(0), y2, g(1)), encR(y1, y2, g(0))]:
                        probe(x, y2, z, 'deep2')
                        probe(x, y2, y1, 'deep2z')
                        probe(x, y1, y2, 'deep2y')

# ---------- 5. rule-2 encodings: encR2(p,u) decodes to p under key u BY RULE 2 ----------
# (needs u itself rule-1-decodable, i.e. u = encR(q,k,w))
encR2 = lambda p, u: J(J(p, C0.op(u, p)), a1_(a1_(u)))
KEYS = [encR(q, k, w) for q in BASE[:3] for k in BASE[:2] for w in BASE[:2]]
for z in KEYS:
    for pc in BASE[:3]:
        y = encR2(pc, z)                       # C = op(z,y) fires by RULE 2
        xs = BASE[:3] + [encR(p, y, w) for p in BASE[:2] for w in BASE[:2]] + [encR2(g(0), y)]
        for x in xs:
            probe(x, y, z, 'C-rule2')
for z in KEYS[:6]:
    for pa in BASE[:2]:
        for k2 in KEYS[:3]:
            y = encR2(pa, k2)
            probe(BASE[0], y, z, 'C-rule2b')
            probe(encR(g(0), y, g(1)), y, z, 'C-rule2c')
# force A to decode by rule 2: x = encR2(p, y) with y a rule-1-decodable key
for y in KEYS:
    for p in BASE[:3]:
        x = encR2(p, y)
        for z in BASE[:3] + [a2_(a2_(y))]:
            probe(x, y, z, 'A-rule2')
# force B / D with an encR-shaped key
for y in KEYS[:6]:
    C = cf.Closed(law, rules)
    for x in BASE[:3]:
        a = C.op(y, x); b = C.op(x, a)
        for q in BASE[:3]:
            probe(x, y, J(q, C.op(b, q)), 'BD-rule2')
            probe(x, a1_(x) if x[0] == 'J' else x, J(q, C.op(b, q)), 'BD-rule2b')

# ---------- 6. hand-derived attacks on the "Dec u" over-approximations ----------
# x = J P (J w P) makes Aok(a1 x, a2 x) / Dec B true by shape; y = a1 x = P
for P0 in [g(0), g(1), J(g(0), g(1)), J(J(g(0), g(1)), g(2))]:
    for w0 in [g(1), g(2), J(g(0), g(2))]:
        C = cf.Closed(law, rules)
        x = J(P0, J(w0, P0))
        y = P0
        a = C.op(y, x); b = C.op(x, a)
        for Q in [J(g(3), g(4)), J(J(g(3), g(4)), g(5)), g(3), encR(g(0), g(1), g(2))]:
            for w1 in [g(2), g(5)]:
                probe(x, y, J(Q, J(w1, Q)), 'attackDec')
                probe(x, y, J(Q, C.op(w1, Q)), 'attackDec2')
                probe(x, y, J(Q, C.op(b, Q)), 'attackDec3')
        # the y = J (a1 y) B shape (K1 at D)
        for w1 in [g(2), J(g(2), g(3))]:
            y2 = J(w1, b)
            for z2 in [g(3), J(g(3), g(4)), J(J(g(3), g(4)), J(g(5), J(g(3), g(4))))]:
                probe(x, y2, z2, 'attackK1D')

print('\ntested %d constructed instances, %d law failures' % (tested, len(fails)))
print('%-4s %-4s %-4s %-4s  %s' % ('A', 'B', 'C', 'D', 'count / notes / TOP marks'))
for k in sorted(cells, key=lambda k: -len(cells[k])):
    tops = collections.Counter(t for _, t in cells[k])
    notes = collections.Counter(n for n, _ in cells[k])
    print('%-4s %-4s %-4s %-4s  %5d  %s  TOP=%s' % (k[0], k[1], k[2], k[3], len(cells[k]),
                                                    dict(notes), dict(tops)))
marks = ['.'] + ['D%d' % (i + 1) for i in range(len(rules))]
miss = [c for c in itertools.product(marks, repeat=4) if c not in cells]
print('\ncells never realised (%d of %d):' % (len(miss), len(marks) ** 4), miss[:40])
fails.sort(key=lambda f: size(f[2]) + size(f[3]) + size(f[4]))
for (note, key, x, y, z, r) in fails[:3]:
    print('\nLAW FAILS  note=%s cell=%s  sizes x=%d y=%d z=%d' % (note, key, size(x), size(y), size(z)))
    print('  x =', show(x))
    print('  y =', show(y))
    print('  z =', show(z))
    print('  got =', show(r))
