"""Does law 40037  x = (((y*(x*y))*z)*x)*z  force a square identity?  (LEMMA_LIBRARY, E-quotient §)

Method: ground equality saturation.  Hash-consed terms over generators a,b; union-find with
congruence closure; the law is applied as  rhs(x,y,z) = x  for representatives x,y,z of bounded
size, adding rhs to the graph.  Any two distinct seed terms that end up in one class is a DERIVED
identity of the law -- the same thing gen/_x6912_derive2.py derives by hand, but searched.

usage: _x40037_derive.py [maxarg=3] [rounds=3] [cap=200000]
"""
import sys, itertools, collections
sys.setrecursionlimit(100000)

MAXARG = int(sys.argv[1]) if len(sys.argv) > 1 else 3
ROUNDS = int(sys.argv[2]) if len(sys.argv) > 2 else 3
CAP = int(sys.argv[3]) if len(sys.argv) > 3 else 200000

A = ('g', 0); B = ('g', 1)
def J(a, b): return ('J', a, b)
def size(t): return 1 if t[0] == 'g' else size(t[1]) + size(t[2]) + 1
def show(t):
    return ('a' if t[1] == 0 else 'b') if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))

# law 40037, ORIGINAL orientation:  x = (((y*(x*y))*z)*x)*z
def rhs(x, y, z):
    return J(J(J(J(y, J(x, y)), z), x), z)

ids = {}          # term -> id
terms = []        # id -> term
kids = []         # id -> (l,r) ids or None
par = []

def find(i):
    while par[i] != i:
        par[i] = par[par[i]]; i = par[i]
    return i

def add(t):
    if t in ids: return ids[t]
    if t[0] == 'g':
        k = None
    else:
        k = (add(t[1]), add(t[2]))
    i = len(terms); ids[t] = i; terms.append(t); kids.append(k); par.append(i)
    return i

pending = []
def union(i, j):
    a, b = find(i), find(j)
    if a != b:
        if size(terms[a]) > size(terms[b]): a, b = b, a   # keep the smaller term as rep
        par[b] = a; pending.append(1)

def congruence():
    changed = True
    while changed:
        changed = False
        sig = {}
        for i in range(len(terms)):
            if kids[i] is None: continue
            s = (find(kids[i][0]), find(kids[i][1]))
            if s in sig:
                if find(sig[s]) != find(i):
                    union(sig[s], i); changed = True
            else:
                sig[s] = i

seeds = {'a': A, 'b': B, 'a*a': J(A, A), 'b*b': J(B, B), 'a*b': J(A, B), 'b*a': J(B, A),
         '(a*a)*(a*a)': J(J(A, A), J(A, A)), '(b*b)*(b*b)': J(J(B, B), J(B, B)),
         'a*(a*a)': J(A, J(A, A)), '(a*a)*a': J(J(A, A), A)}
for t in seeds.values(): add(t)

for rd in range(ROUNDS):
    reps = sorted({find(i) for i in range(len(terms))})
    pool = [terms[r] for r in reps if size(terms[r]) <= MAXARG]
    n0 = len(terms)
    for x, y, z in itertools.product(pool, repeat=3):
        t = rhs(x, y, z)
        if size(t) > 2 * MAXARG * 3 + 6: continue
        if len(terms) > CAP: break
        union(add(t), add(x))
    congruence()
    cls = collections.defaultdict(list)
    for i in range(len(terms)): cls[find(i)].append(i)
    big = [c for c in cls.values() if len(c) > 1]
    print('round %d: pool %d, nodes %d, classes %d, merged classes %d'
          % (rd + 1, len(pool), len(terms), len(cls), len(big)), flush=True)

print()
print('seed classes:')
for name, t in seeds.items():
    print('  %-14s -> class rep %s' % (name, show(terms[find(ids[t])])[:70]))
print()
pairs = [('a*a', 'b*b'), ('a*a', '(a*a)*(a*a)'), ('a*a', 'a*b'), ('a', 'a*a'), ('a', 'b'),
         ('a*b', 'b*a'), ('(a*a)*(a*a)', '(b*b)*(b*b)'), ('a*a', 'a*(a*a)'), ('a*a', '(a*a)*a')]
for p, q in pairs:
    same = find(ids[seeds[p]]) == find(ids[seeds[q]])
    print('  %-14s = %-14s : %s' % (p, q, 'DERIVED' if same else 'no'))
cls = collections.defaultdict(list)
for i in range(len(terms)): cls[find(i)].append(i)
big = sorted([c for c in cls.values() if len(c) > 1], key=lambda c: -len(c))
print()
print('largest merged classes (%d total):' % len(big))
for c in big[:6]:
    ts = sorted((terms[i] for i in c), key=size)[:6]
    print('   {%s}' % ' = '.join(show(t)[:44] for t in ts))
