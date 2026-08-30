"""Does law 40037  x = (((y*(x*y))*z)*x)*z  force a square identity?

Ground equality saturation WITH e-matching: every node whose shape matches
    (((Y*(X*Y))*Z)*X)*Z     (the equalities checked up to the current congruence)
is merged with X, and new law instances are added for representatives of bounded size.
Iterated to fixpoint.  This is gen/_x6912_derive2.py's hand derivation, searched.

usage: _x40037_derive2.py [maxarg=5] [rounds=6] [cap=600000] [gens=2]
"""
import sys, itertools, collections
sys.setrecursionlimit(100000)
MAXARG = int(sys.argv[1]) if len(sys.argv) > 1 else 5
ROUNDS = int(sys.argv[2]) if len(sys.argv) > 2 else 6
CAP = int(sys.argv[3]) if len(sys.argv) > 3 else 600000
NG = int(sys.argv[4]) if len(sys.argv) > 4 else 2
A = ('g', 0); B = ('g', 1)
def J(a, b): return ('J', a, b)
def show(t):
    return 'ab c'[t[1]] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))
def rhs(x, y, z): return J(J(J(J(y, J(x, y)), z), x), z)

ids = {}; terms = []; kids = []; par = []; sz = []
def find(i):
    while par[i] != i:
        par[i] = par[par[i]]; i = par[i]
    return i
def add(t):
    i = ids.get(t)
    if i is not None: return i
    k = None if t[0] == 'g' else (add(t[1]), add(t[2]))
    i = len(terms); ids[t] = i; terms.append(t); kids.append(k); par.append(i)
    sz.append(1 if k is None else sz[k[0]] + sz[k[1]] + 1)
    return i
def union(i, j):
    a, b = find(i), find(j)
    if a == b: return False
    if sz[a] > sz[b]: a, b = b, a
    par[b] = a; return True
def congruence():
    ch = True
    while ch:
        ch = False; sig = {}
        for i in range(len(terms)):
            if kids[i] is None: continue
            s = (find(kids[i][0]), find(kids[i][1]))
            j = sig.get(s)
            if j is None: sig[s] = i
            elif union(j, i): ch = True
def ematch():
    """merge every node of shape (((Y*(X*Y))*Z)*X)*Z with X (equalities up to congruence)"""
    ch = 0
    for i in range(len(terms)):
        k = kids[i]
        if k is None: continue
        m4, z2 = k
        k4 = kids[m4]
        if k4 is None: continue
        m3, x3 = k4
        k3 = kids[m3]
        if k3 is None: continue
        m2, z = k3
        if find(z) != find(z2): continue
        k2 = kids[m2]
        if k2 is None: continue
        y, m1 = k2
        k1 = kids[m1]
        if k1 is None: continue
        x2, y2 = k1
        if find(y) != find(y2) or find(x2) != find(x3): continue
        if union(i, x2): ch += 1
    return ch

seeds = {'a': A, 'b': B, 'a*a': J(A, A), 'b*b': J(B, B), 'a*b': J(A, B), 'b*a': J(B, A),
         '(a*a)*(a*a)': J(J(A, A), J(A, A)), '(b*b)*(b*b)': J(J(B, B), J(B, B)),
         'a*(a*a)': J(A, J(A, A)), '(a*a)*a': J(J(A, A), A), '(a*b)*(a*b)': J(J(A, B), J(A, B))}
for t in seeds.values(): add(t)
gens = [A, B][:NG]
def allterms(maxs):
    by = {1: list(gens)}
    for n in range(3, maxs + 1, 2):
        by[n] = [J(s, t) for a in range(1, n - 1, 2) if (n - 1 - a) in by
                 for s in by[a] for t in by[n - 1 - a]]
    return [t for n in sorted(by) for t in by[n]]
for t in allterms(MAXARG): add(t)
congruence(); ematch(); congruence()

SIZECAP = 2 * MAXARG * 3 + 6
for rd in range(ROUNDS):
    reps = sorted({find(i) for i in range(len(terms))})
    pool = [terms[r] for r in reps if sz[r] <= MAXARG]
    n0 = len(terms); added = 0
    for x, y, z in itertools.product(pool, repeat=3):
        if len(terms) > CAP: break
        t = rhs(x, y, z)
        if len(t) and sum(1 for _ in [0]):
            pass
        i = add(t)
        if sz[i] <= SIZECAP:
            union(i, add(x)); added += 1
    congruence()
    tot = 0
    while True:
        c = ematch()
        if not c: break
        tot += c; congruence()
    cls = collections.defaultdict(list)
    for i in range(len(terms)): cls[find(i)].append(i)
    big = [c for c in cls.values() if len(c) > 1]
    print('round %d: pool %d nodes %d (+%d) classes %d merged-classes %d ematch-merges %d'
          % (rd + 1, len(pool), len(terms), len(terms) - n0, len(cls), len(big), tot), flush=True)
    if len(terms) > CAP:
        print('  node cap hit'); break

print()
pairs = [('a*a', 'b*b'), ('a*a', '(a*a)*(a*a)'), ('a*a', 'a*b'), ('a', 'a*a'), ('a', 'b'),
         ('a*b', 'b*a'), ('(a*a)*(a*a)', '(b*b)*(b*b)'), ('a*a', 'a*(a*a)'), ('a*a', '(a*a)*a'),
         ('a*a', '(a*b)*(a*b)')]
for p, q in pairs:
    print('  %-14s = %-14s : %s' % (p, q, 'DERIVED' if find(ids[seeds[p]]) == find(ids[seeds[q]]) else 'no'))
cls = collections.defaultdict(list)
for i in range(len(terms)): cls[find(i)].append(i)
small = [c for c in cls.values() if len(c) > 1 and min(sz[i] for i in c) <= 7 and
         len([i for i in c if sz[i] <= 9]) > 1]
print()
print('merged classes containing >1 term of size <= 9  (%d):' % len(small))
for c in sorted(small, key=lambda c: min(sz[i] for i in c))[:12]:
    ts = sorted((terms[i] for i in c if sz[ids[terms[i]]] <= 11), key=lambda t: len(show(t)))[:5]
    print('   {%s}' % ' = '.join(show(t) for t in ts))
