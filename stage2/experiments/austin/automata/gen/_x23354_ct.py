"""Case tree for law 23354:  x = ((y*x)*y) * (x*(x*z)).
chain:  p = op(y,x) ; q = op(p,y) ; r = op(x,z) ; s = op(x,r) ; top = op(q,s)
Enumerate the 2^4 free/decoded combinations of (p,q,r,s) by CHAINED ENCODING, not sampling.

The model's only decoding shape (R1) is:  op(J(J(A,X),A), J(X,J(X,D))) = X.
So to force a product to decode we build its left argument as ENCL(A,X)=J(J(A,X),A)
and its right argument as ENCR(X,D)=J(X,J(X,D)).
usage: _x23354_ct.py [rec|rep]
"""
import sys, os, itertools, random
from collections import Counter
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, leangen
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 23354
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = orig
GEN = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/'
which = sys.argv[1] if len(sys.argv) > 1 else 'rec'
src = open(GEN + ('chk23354.py' if which == 'rec' else 'rep23354/chk23354.py'), encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); RULES = ns['rules']
TAGS = [r[2] for r in RULES]
C = cf.Closed(law, RULES)
print('%s: %d rules %s' % (which, len(RULES), TAGS), flush=True)

J = lambda a, b: ('J', a, b)
g = lambda n: ('g', n)
def sh(t): return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (sh(t[1]), sh(t[2]))
def which_rule(u, v):
    for i, (conds, xx, tag) in enumerate(C.rules):
        if C.check(conds, u, v) and C.ev(xx, u, v) is not None: return i
    return -1

ENCL = lambda A, X: J(J(A, X), A)          # left arg of a decoding pair, payload X
ENCR = lambda X, D: J(X, J(X, D))          # right arg of a decoding pair, payload X

cells = Counter(); bad = []; wit = {}
def record(x, y, z, fam):
    try:
        p = C.op(y, x); q = C.op(p, y); r = C.op(x, z); s = C.op(x, r); top = C.op(q, s)
    except RecursionError:
        return
    key = (p != J(y, x), q != J(p, y), r != J(x, z), s != J(x, r))
    pat = (which_rule(y, x), which_rule(p, y), which_rule(x, z), which_rule(x, r), which_rule(q, s))
    cells[key] += 1
    tot = size(x) + size(y) + size(z)
    if key not in wit or tot < wit[key][0]: wit[key] = (tot, (x, y, z), pat)
    if top != x: bad.append((x, y, z, fam, key, pat, top))

G = [g(i) for i in range(4)]
# --- F0: exhaustive small triples over 3 generators ---
terms = list(G[:3])
for _ in range(3):
    new = list(terms)
    for a in terms:
        for b in terms:
            t = J(a, b)
            if size(t) <= 5 and t not in new: new.append(t)
    terms = new
terms = [t for t in terms if size(t) <= 5]
small = [t for t in terms if size(t) <= 3]
for x in terms:
    for y in terms:
        for z in terms:
            if size(x) + size(y) + size(z) <= 11: record(x, y, z, 'F0')
print('F0 done (%d terms), fails %d' % (len(terms), len(bad)), flush=True)

# --- F1: p decodes  (y = ENCL(A,X), x = ENCR(X,D)) ---
for A, X, D in itertools.product(small, repeat=3):
    y = ENCL(A, X); x = ENCR(X, D)
    for z in small: record(x, y, z, 'F1')
# --- F2: r decodes  (x = ENCL(A,X), z = ENCR(X,D)) ---
for A, X, D in itertools.product(small, repeat=3):
    x = ENCL(A, X); z = ENCR(X, D)
    for y in small: record(x, y, z, 'F2')
# --- F3: s decodes  (x = ENCL(A,X), r = ENCR(X,D) i.e. op(x,z) must equal ENCR(X,D)) ---
#     easiest: z free so r = J(x,z) -- then r = ENCR(X,D) needs x = X and J(X,D)=z; but x=ENCL(A,X)!=X.
#     so s can only decode when r DECODED to ENCR(X,D): r = op(x,z) = payload of z's encoding.
for A, X, D in itertools.product(small, repeat=3):
    x = ENCL(A, X)                      # so op(x, ENCR(P,Q)) = P
    tgt = ENCR(X, D)                    # what r must be for s to decode with payload X
    z = ENCR(tgt, random.choice(small)) # op(x,z) = tgt = r
    for y in small: record(x, y, z, 'F3')
# --- F4: q decodes  (p = ENCL(A,X), y = ENCR(X,D)) ---
#     p free = J(y,x): need J(y,x) = J(J(A,X),A) -> y = J(A,X), x = A
for A, X, D in itertools.product(small, repeat=3):
    y0 = J(A, X); x = A
    if ENCR(X, D) == y0:
        for z in small: record(x, y0, z, 'F4a')
#     the honest way: y must be BOTH J(A,X) (for p free) and ENCR(X,D) -> y = J(X, J(X,D)) with A=X, X=J(X,D)?? impossible.
#     so q decodes only when p DECODED to ENCL(A,X): y = ENCL(A2,ENCL(A,X)) and x = ENCR(ENCL(A,X), D2)
for A, X, A2, D2 in itertools.product(small[:4], repeat=4):
    P = ENCL(A, X)
    y = ENCL(A2, P); x = ENCR(P, D2)
    if size(x) + size(y) > 120: continue
    for z in small[:4]: record(x, y, z, 'F4b')
print('F1-F4 done, fails %d' % len(bad), flush=True)

# --- F5: p decoded AND r/s decoded simultaneously (x must serve both roles) ---
for A, X, D in itertools.product(small[:4], repeat=3):
    # x = ENCR(X,D) makes p decode; for r to decode x must be ENCL(A',X') -> ENCR(X,D)=J(X,J(X,D))
    # matches J(J(A',X'),A') iff X = J(A',X') and J(X,D) = A' -> A' = J(X,D), X = J(J(X,D),X') : impossible by size.
    # instead: let r decode via x's OUTER shape by choosing X = J(A',X') and D = A'
    for Ap, Xp in itertools.product(small[:4], repeat=2):
        X2 = J(Ap, Xp); D2 = Ap
        y = ENCL(A, X2); x = ENCR(X2, D2)   # x = J(J(Ap,Xp), J(J(Ap,Xp),Ap))  -- a1 x = J(Ap,Xp)
        for z in [ENCR(Xp, q) for q in small[:3]] + small[:3]:
            record(x, y, z, 'F5')
print('F5 done, fails %d' % len(bad), flush=True)

# --- F6: random mixtures with nesting ---
random.seed(23354)
pool = terms + [ENCL(a, b) for a in small[:3] for b in small[:3]] + [ENCR(a, b) for a in small[:3] for b in small[:3]]
for _ in range(20000):
    x = random.choice(pool); y = random.choice(pool); z = random.choice(pool)
    r = random.random()
    if r < 0.25: y = ENCL(random.choice(small), random.choice(pool))
    elif r < 0.5: x = ENCR(random.choice(pool), random.choice(small))
    elif r < 0.75: z = ENCR(random.choice(pool), random.choice(small))
    if size(x) + size(y) + size(z) > 200: continue
    record(x, y, z, 'F6')
print('F6 done', flush=True)

print('=== instances %d, law failures %d ===' % (sum(cells.values()), len(bad)))
for b in bad[:5]:
    print('  BAD [%s] cell=%s pat=%s' % (b[3], b[4], b[5]))
    print('    x=%s' % sh(b[0])); print('    y=%s' % sh(b[1])); print('    z=%s' % sh(b[2]))
print('=== cells (p,q,r,s) decoded? ===')
for k in itertools.product([False, True], repeat=4):
    c = cells.get(k, 0)
    if c:
        tot, tri, pat = wit[k]
        print('  %-28s x%-8d pat=%s  minsize %d' % (str(k), c, pat, tot))
    else:
        print('  %-28s UNREACHED' % str(k))
