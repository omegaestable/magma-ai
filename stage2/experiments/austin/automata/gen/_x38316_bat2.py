"""Wave-3 standard-raising battery for 38316 (dualized L-form  x = y*(x*((y*(z*x))*y))).
chain: a = op z x ; b = op y a ; c = op b y ; d = op x c ; top = op y d

Three families the old F1..F6 battery structurally cannot generate:
  G1  c DECODES TO A GENERATOR  -- the exact shape of the size-35 counterexample that falsified
      the 10-rule model: y is itself a free encoding of a generator by b.
  G2  JUNK VARIABLE varied      -- z occurs once, only inside (z*x); no rule constrains it.
      Every earlier pool drew z from small terms.  Draw it LARGE, including encodings.
  G3  CROSS-POSITION FIRING     -- for each rule, build terms matching its u/v patterns and place
      them at EVERY chain slot, not only the one the rule was extracted for (law 40037's mechanism).
usage: _x38316_bat2.py <setname|all|v0> [N]
"""
import sys, os, random, itertools
from collections import Counter
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, leangen
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 38316
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = ('x', leangen.dual_pat(orig[1]))
GEN = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/'
name = sys.argv[1] if len(sys.argv) > 1 else 'cand4'
src = open(GEN + 'chkrep38316.py', encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); ALL = ns['rules']
if name == 'all':
    RULES = ALL
elif name == 'v0':
    RULES = [r for r in ALL if r[2].startswith('V0')]
else:
    ns2 = {}; exec(open(GEN + '_x38316_rules_%s.py' % name, encoding='utf-8').read(), ns2)
    RULES = ns2['rules']
TAGS = [r[2] for r in RULES]
C = cf.Closed(law, RULES)
print('set %s: %d rules %s' % (name, len(RULES), TAGS), flush=True)

J = lambda a, b: ('J', a, b)
g = lambda n: ('g', n)
def sh(t): return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (sh(t[1]), sh(t[2]))
def which(u, v):
    for i, (conds, xx, tag) in enumerate(C.rules):
        if C.check(conds, u, v) and C.ev(xx, u, v) is not None: return i
    return -1

cells = Counter(); bad = []
def record(x, y, z, fam):
    try:
        a = C.op(z, x); b = C.op(y, a); c = C.op(b, y); d = C.op(x, c); top = C.op(y, d)
        pat = (which(z, x), which(y, a), which(b, y), which(x, c), which(y, d))
    except RecursionError:
        return
    cells[(pat, fam)] += 1
    if top != x:
        bad.append((x, y, z, fam, pat, top))

def ENC(u, P, Z):
    """the reading v with op(u,v) = P: v = J P (op(op(u, op(Z,P)), u))"""
    a = C.op(Z, P); b = C.op(u, a); c = C.op(b, u); return J(P, c)

G = [g(i) for i in range(4)]
small = [g(0), g(1), g(2), J(g(0), g(1)), J(g(1), g(0)), J(g(2), g(0)), J(g(0), J(g(1), g(2)))]
big = [ENC(g(0), g(1), g(2)), ENC(g(1), J(g(0), g(2)), g(0)),
       J(J(g(0), g(1)), J(J(g(2), g(0)), J(g(1), g(2)))),
       ENC(g(2), ENC(g(0), g(1), g(2)), g(1))]

# ---- G1: c decodes to a GENERATOR ----
n1 = 0
for zz, P, Z in itertools.product(small[:5], small[:5], small[:5]):
    for Wg in G[:3]:                                   # the generator c must decode to
        # b must come out of op(y, a); take y = ENC(b, Wg, Z') so that c = op(b,y) = Wg
        for bcand in list(G[:3]) + [J(g(0), g(1))]:
            y = ENC(bcand, Wg, Z)
            if size(y) > 200: continue
            # and x chosen so that a = op(z,x) is free and b = op(y,a) really is bcand
            for x in [ENC(zz, P, Z), J(J(y, J(P, zz)), y), J(y, J(P, zz))]:
                if size(x) > 400: continue
                record(x, y, zz, 'G1'); n1 += 1
print('G1 done (%d), failures %d' % (n1, len(bad)), flush=True)

# ---- G1b: the literal counterexample family, generalised over 4 generators ----
n1b = 0
for a0, a1, a2, a3 in itertools.product(range(4), repeat=4):
    y = J(g(a0), J(J(g(a1), J(g(a2), g(a0))), g(a1)))    # y encodes g a0 by g a1
    z = g(a1)
    for w in [J(g(a3), g(a1)), g(a3), J(g(a3), J(g(a0), g(a1)))]:
        x = J(J(y, w), y)
        record(x, y, z, 'G1b'); n1b += 1
print('G1b done (%d), failures %d' % (n1b, len(bad)), flush=True)

# ---- G2: junk variable z LARGE ----
n2 = 0
random.seed(38316)
for _ in range(6000):
    z = random.choice(big + [ENC(random.choice(small), random.choice(small), random.choice(big))])
    x = random.choice(small + big); y = random.choice(small + big)
    if random.random() < 0.5:
        y = ENC(random.choice(small), x, random.choice(small))
    if size(x) + size(y) + size(z) > 900: continue
    record(x, y, z, 'G2'); n2 += 1
# and z large with the G1b shape
for a0, a1 in itertools.product(range(3), repeat=2):
    y = J(g(a0), J(J(g(a1), J(g(2), g(a0))), g(a1)))
    for z in big:
        x = J(J(y, J(g(3), z)), y)
        record(x, y, z, 'G2b'); n2 += 1
print('G2 done (%d), failures %d' % (n2, len(bad)), flush=True)

# ---- G3: cross-position firing.  Build terms that satisfy each rule's STRUCTURAL conditions and
#          put them at every chain slot. ----
def struct_ok(i, u, v):
    conds = C.rules[i][0]
    return C.check([c for c in conds if c[0] != 'OPEQ'], u, v)

pool = small + big + [ENC(a, b, c0) for a in small[:3] for b in small[:3] for c0 in small[:2]]
pool = [t for t in pool if size(t) <= 200]
n3 = 0; hit = Counter()
random.seed(7)
for _ in range(int(sys.argv[2]) if len(sys.argv) > 2 else 25000):
    x = random.choice(pool); y = random.choice(pool); z = random.choice(pool)
    if size(x) + size(y) + size(z) > 900: continue
    try:
        a = C.op(z, x); b = C.op(y, a); c = C.op(b, y); d = C.op(x, c)
    except RecursionError:
        continue
    slots = [(z, x), (y, a), (b, y), (x, c), (y, d)]
    for si, (u, v) in enumerate(slots):
        for ri in range(len(C.rules)):
            if struct_ok(ri, u, v):
                hit[(ri, si)] += 1
    record(x, y, z, 'G3'); n3 += 1
print('G3 done (%d)' % n3, flush=True)
print('rule x slot structural hits (slot 0=a,1=b,2=c,3=d,4=top):')
for ri in range(len(C.rules)):
    row = ' '.join('%6d' % hit.get((ri, si), 0) for si in range(5))
    print('  %-12s %s' % (TAGS[ri], row))

print('=== instances %d, LAW FAILURES %d ===' % (sum(cells.values()), len(bad)))
for b in bad[:5]:
    print('  BAD [%s] pat=%s' % (b[3], b[4]))
    print('    x=%s' % (sh(b[0]) if size(b[0]) < 200 else '<sz %d>' % size(b[0])))
    print('    y=%s' % (sh(b[1]) if size(b[1]) < 200 else '<sz %d>' % size(b[1])))
    print('    z=%s' % (sh(b[2]) if size(b[2]) < 200 else '<sz %d>' % size(b[2])))
agg = Counter()
for (pat, fam), c0 in cells.items(): agg[pat] += c0
print('=== patterns ===')
for pat, c0 in sorted(agg.items(), key=lambda kv: -kv[1])[:16]:
    print('  %-26s x%-8d %s' % (str(pat), c0, '|'.join((TAGS[i] if i >= 0 else 'free') for i in pat)))
