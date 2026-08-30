# -*- coding: utf-8 -*-
"""Per-rule, per-family FIRING census for 38316/cand4 -- counts every rule application anywhere in
the evaluation (not only at the five chain slots), across every family the batteries use.
A rule that never fires is untested however large the totals are."""
import sys, random, itertools
from collections import Counter
D = r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, D)
import closedform as cf, leangen
from freemodel import normalise, catalog, size
from laws import parse_eq
EQ = 38316
law = ('x', leangen.dual_pat(normalise(parse_eq(catalog()[EQ]))[1]))
ns = {}; exec(open(D + '/gen/_x38316_rules_cand6.py', encoding='utf-8').read(), ns)
RULES = ns['rules']; TAGS = [r[2] for r in RULES]

class CC(cf.Closed):
    def __init__(self, law, rules):
        super().__init__(law, rules); self.fire = Counter()
    def op(self, u, v):
        key = (u, v)
        m = self.memo.get(key)
        if m is not None: return m
        if key in self.inprog:
            self.cycles += 1; return ('J', u, v)
        self.inprog.add(key); res = None
        for i, (co, xx, tg) in enumerate(self.rules):
            if self.check(co, u, v):
                r = self.ev(xx, u, v)
                if r is not None:
                    res = r; self.fire[i] += 1; break
        self.inprog.discard(key)
        if res is None: res = ('J', u, v)
        self.memo[key] = res
        return res

J = lambda a, b: ('J', a, b); g = lambda n: ('g', n)
fam = {}
def run(name, gen):
    C = CC(law, RULES); bad = 0; n = 0
    for x, y, z in gen:
        try:
            a = C.op(z, x); b = C.op(y, a); c = C.op(b, y); d = C.op(x, c); t = C.op(y, d)
        except RecursionError:
            continue
        n += 1
        if t != x: bad += 1
    fam[name] = (n, bad, Counter(C.fire))
    print('%-6s n=%-7d bad=%-3d fired: %s' % (name, n, bad,
          {TAGS[i]: c for i, c in sorted(C.fire.items())}), flush=True)

def enc_with(C):
    def enc(u, P, Z):
        a = C.op(Z, P); b = C.op(u, a); c = C.op(b, u); return J(P, c)
    return enc
CE = CC(law, RULES); enc = enc_with(CE)
G = [g(i) for i in range(5)]
small = G[:3] + [J(g(0), g(1)), J(g(1), g(2)), J(g(2), g(0))]

def F1():
    terms = list(G[:3])
    for _ in range(3):
        new = list(terms)
        for a in terms:
            for b in terms:
                t = J(a, b)
                if size(t) <= 5 and t not in new: new.append(t)
        terms = new
    terms = [t for t in terms if size(t) <= 5]
    for x in terms:
        for y in terms:
            for z in terms:
                if size(x) + size(y) + size(z) <= 11: yield (x, y, z)
def G1():
    for zz, P, Z in itertools.product(small[:5], repeat=3):
        for Wg in G[:3]:
            for bc in list(G[:3]) + [J(g(0), g(1))]:
                y = enc(bc, Wg, Z)
                if size(y) > 200: continue
                for x in [enc(zz, P, Z), J(J(y, J(P, zz)), y), J(y, J(P, zz))]:
                    if size(x) <= 400: yield (x, y, zz)
def G1b():
    for a0, a1, a2, a3 in itertools.product(range(4), repeat=4):
        y = J(g(a0), J(J(g(a1), J(g(a2), g(a0))), g(a1))); z = g(a1)
        for w in [J(g(a3), g(a1)), g(a3), J(g(a3), J(g(a0), g(a1)))]:
            yield (J(J(y, w), y), y, z)
def D3():
    for W1, W2, Z in itertools.product(G[:3], G[:3], small[:3]):
        for bc in [g(0), J(g(0), g(1)), enc(g(0), g(1), g(2))]:
            for k in (1, 2, 3):
                yy = bc
                for _ in range(k): yy = enc(bc, W1, Z)
                if size(yy) > 4000: continue
                for zz in small[:3]:
                    for xx in [enc(yy, W2, zz), enc(yy, enc(yy, W2, zz), zz), J(J(yy, J(W2, zz)), yy)]:
                        if size(xx) <= 12000: yield (xx, yy, zz)
def RND():
    random.seed(99); pool = list(small)
    for _ in range(40):
        t = enc(random.choice(pool), random.choice(pool), random.choice(pool))
        if size(t) <= 2000: pool.append(t)
    for _ in range(12000):
        x = random.choice(pool); y = random.choice(pool); z = random.choice(pool)
        if size(x) + size(y) + size(z) <= 3000: yield (x, y, z)

for nm, gg in (('F1', F1()), ('G1', G1()), ('G1b', G1b()), ('D3', D3()), ('RND', RND())):
    run(nm, gg)
tot = Counter()
for n, b, c in fam.values(): tot.update(c)
print('=== TOTAL firings per rule ===')
never = []
for i, t in enumerate(TAGS):
    print('  %-12s %d' % (t, tot.get(i, 0)))
    if tot.get(i, 0) == 0: never.append(t)
print('NEVER FIRES ANYWHERE:', never if never else 'none')
