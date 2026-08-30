"""Targeted coincidence battery for law 38316 (dualized L-form  x = y*(x*((y*(z*x))*y))).

Families, each derived from the model's own decoding conditions:
  F1  brute force over all small triples (size <= 5, total <= 11)
  F2  a-decoding:  x := ENC(z, P, Z)  (x is a reading with u = z), nested up to twice
  F3  b-decoding:  x := C(y, Z, z)    so that a = J z x is itself a reading with u = y
  F4  d-candidate: y := J w x         (the shape KL forces if op(x, c) is to decode with c free)
  F5  c-candidate: y := J w1 (J w2 t) for t drawn from the chain values
  F6  mixtures of F2/F3/F4 with shared variables
Reports the (a,b,c,d,top) rule pattern for each and any law failure.

usage: _x38316_battery.py [tags|all] [N]
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
src = open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chkrep38316.py',
           encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); ALL = ns['rules']

sel = sys.argv[1] if len(sys.argv) > 1 else 'all'
RULES = ALL if sel == 'all' else [r for r in ALL if r[2] in sel.split(',')]
TAGS = [r[2] for r in RULES]
C = cf.Closed(law, RULES)
print('rules:', TAGS)

def J(a, b): return ('J', a, b)
def g(n): return ('g', n)
def sh(t): return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (sh(t[1]), sh(t[2]))

def which(u, v):
    for i, (conds, xx, tag) in enumerate(C.rules):
        if C.check(conds, u, v):
            if C.ev(xx, u, v) is not None:
                return i
    return -1

def chain(x, y, z):
    a = C.op(z, x); b = C.op(y, a); c = C.op(b, y); d = C.op(x, c); top = C.op(y, d)
    return (which(z, x), which(y, a), which(b, y), which(x, c), which(y, d)), top

cnt = Counter(); wit = {}; bad = []
def record(x, y, z, fam):
    try:
        pat, top = chain(x, y, z)
    except RecursionError:
        return
    cnt[(pat, fam)] += 1
    tot = size(x) + size(y) + size(z)
    if (pat, fam) not in wit or tot < wit[(pat, fam)][0]:
        wit[(pat, fam)] = (tot, (x, y, z))
    if top != x:
        bad.append((x, y, z, fam, pat))

def ENC(u, P, Z):
    """the reading v with op(u,v) = P:  v = J P (op(op(u, op(Z,P)), u))"""
    a = C.op(Z, P); b = C.op(u, a); c = C.op(b, u)
    return J(P, c)

def CPART(y, Z, P):
    """the value of the chain node c = op(op(y, op(Z,P)), y)"""
    a = C.op(Z, P); b = C.op(y, a); return C.op(b, y)

G = [g(i) for i in range(3)]

# ---- F1: brute force ----
terms = list(G)
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
            if size(x) + size(y) + size(z) <= 11:
                record(x, y, z, 'F1')
print('F1 done (%d terms)' % len(terms), flush=True)

small = [t for t in terms if size(t) <= 3]

# ---- F2: a-decoding ----
for z, P, Z in itertools.product(small, repeat=3):
    if size(P) + size(Z) > 5: continue
    x = ENC(z, P, Z)
    if size(x) > 120: continue
    for y in small:
        record(x, y, z, 'F2')
    record(x, P, z, 'F2'); record(x, Z, z, 'F2')
print('F2 done', flush=True)

# ---- F2b: doubly nested a-decoding ----
for z, P, Z in itertools.product(small[:6], repeat=3):
    x1 = ENC(z, P, Z)
    if size(x1) > 60: continue
    x = ENC(z, x1, Z)
    if size(x) > 400: continue
    for y in small[:4]:
        record(x, y, z, 'F2b')
print('F2b done', flush=True)

# ---- F3: b-decoding ----
for y, Z, z in itertools.product(small, repeat=3):
    x = CPART(y, Z, z)
    if size(x) > 200: continue
    record(x, y, z, 'F3')
print('F3 done', flush=True)

# ---- F3b: b-decoding with a itself decoded ----
for y, Z, z in itertools.product(small[:6], repeat=3):
    x0 = CPART(y, Z, z)
    if size(x0) > 100: continue
    for P in small[:4]:
        x = ENC(z, x0, P)
        if size(x) > 400: continue
        record(x, y, z, 'F3b')
print('F3b done', flush=True)

# ---- F4: y = J w x ----
for w, x, z in itertools.product(terms, small, small):
    if size(w) > 5: continue
    y = J(w, x)
    if size(y) > 8: continue
    record(x, y, z, 'F4')
# with x itself an encoding
for w, z, P in itertools.product(small, small, small):
    x = ENC(z, P, w)
    if size(x) > 120: continue
    y = J(w, x)
    record(x, y, z, 'F4b')
print('F4 done', flush=True)

# ---- F5: y with structure J w1 (J w2 t) ----
random.seed(7)
pool = list(terms)
for _ in range(4000):
    x = random.choice(pool); z = random.choice(pool)
    a = C.op(z, x)
    w1 = random.choice(small); w2 = random.choice(small)
    t = random.choice([a, x, z, C.op(x, z)])
    y = J(w1, J(w2, t))
    if size(y) > 60: continue
    record(x, y, z, 'F5')
print('F5 done', flush=True)

# ---- F6: mixtures ----
random.seed(11)
for _ in range(4000):
    y = random.choice(small); z = random.choice(small); P = random.choice(small); Z = random.choice(small)
    r = random.random()
    if r < 0.34:
        x = ENC(z, CPART(y, Z, z), P)
    elif r < 0.67:
        x = CPART(y, Z, ENC(z, P, Z))
    else:
        x = ENC(z, P, Z); y = J(random.choice(small), x)
    if size(x) > 400 or size(y) > 400: continue
    record(x, y, z, 'F6')
print('F6 done', flush=True)

print('=== law failures: %d ===' % len(bad))
for b in bad[:5]:
    print('  BAD [%s] x=%s y=%s z=%s pat=%s' % (b[3], sh(b[0]), sh(b[1]), sh(b[2]), b[4]))
print('=== patterns (a,b,c,d,top), -1 = free ===')
agg = Counter()
for (pat, fam), c in cnt.items():
    agg[pat] += c
for pat, c in sorted(agg.items(), key=lambda kv: -kv[1]):
    fams = sorted({f for (p, f) in cnt if p == pat})
    print('  %-24s x%-8d %-40s  fams %s' % (str(pat), c,
          '|'.join((TAGS[i] if i >= 0 else 'free') for i in pat), fams))
    k = [(p, f) for (p, f) in wit if p == pat]
    tot, tri = min((wit[q] for q in k), key=lambda w: w[0])
    if c < 100000:
        print('        x=%s' % sh(tri[0]))
        print('        y=%s' % sh(tri[1]))
        print('        z=%s' % sh(tri[2]))
