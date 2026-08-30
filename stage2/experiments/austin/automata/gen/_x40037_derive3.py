"""Generic forced-identity search for a law, by ground equality saturation with e-matching.

usage: _x40037_derive3.py <eq> [maxarg=9] [rounds=3] [cap=900000] [gens=1]
Positive control: eq 6912 must derive  a*a = b*b  and  a*a = (a*a)*(a*a)  (gen/_x6912_derive2.py).
"""
import sys, os, itertools, collections
sys.setrecursionlimit(100000)
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE)
from freemodel import normalise, catalog
from laws import parse_eq
EQ = int(sys.argv[1])
MAXARG = int(sys.argv[2]) if len(sys.argv) > 2 else 9
ROUNDS = int(sys.argv[3]) if len(sys.argv) > 3 else 3
CAP = int(sys.argv[4]) if len(sys.argv) > 4 else 900000
NG = int(sys.argv[5]) if len(sys.argv) > 5 else 1
law = normalise(parse_eq(catalog()[EQ]))
PAT = law[1]
VS = sorted({v for v in str(PAT).replace("'", ' ').replace('(', ' ').replace(')', ' ')
             .replace(',', ' ').split() if v.isalpha()})
print('eq %d   x = %s   vars %s' % (EQ, PAT, VS))
A = ('g', 0); B = ('g', 1)
def J(a, b): return ('J', a, b)
def show(t): return 'abc'[t[1]] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))
def inst(p, s):
    return s[p] if isinstance(p, str) else J(inst(p[0], s), inst(p[1], s))
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
def match(p, node, bind):
    """match pattern p against node id, bindings are class reps"""
    if isinstance(p, str):
        r = find(node)
        if p in bind: return bind[p] == r
        bind[p] = r; return True
    k = kids[node]
    if k is None: return False
    b2 = dict(bind)
    if not match(p[0], k[0], b2): return False
    if not match(p[1], k[1], b2): return False
    bind.clear(); bind.update(b2); return True
def ematch():
    ch = 0
    for i in range(len(terms)):
        b = {}
        if match(PAT, i, b) and 'x' in b:
            if union(i, b['x']): ch += 1
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
# BOOST: structured big terms a human derivation reaches for (repeated squaring), size up to 31.
BOOST = []
lvl = list(gens) + ([J(A, B), J(B, A)] if NG > 1 else [])
for t in lvl:
    s0 = t
    for _ in range(3):
        s0 = J(s0, s0); BOOST.append(s0)
    BOOST.append(J(t, J(t, t))); BOOST.append(J(J(t, t), t))
BOOST = list(dict.fromkeys(BOOST))
for t in BOOST: add(t)
congruence()
print('BOOST', [show(t) for t in BOOST][:8], '... %d terms, max size %d'
      % (len(BOOST), max(sz[ids[t]] for t in BOOST)))
for rd in range(ROUNDS):
    reps = sorted({find(i) for i in range(len(terms))})
    pool = [terms[r] for r in reps if sz[r] <= MAXARG]
    pool += [t for t in BOOST if terms[find(ids[t])] not in pool]
    pool = list(dict.fromkeys(pool))
    n0 = len(terms)
    for vals in itertools.product(pool, repeat=len(VS)):
        if len(terms) > CAP: break
        s = dict(zip(VS, vals))
        union(add(inst(PAT, s)), add(s['x']))
    congruence()
    tot = 0
    while True:
        c = ematch()
        if not c: break
        tot += c; congruence()
    cls = collections.defaultdict(list)
    for i in range(len(terms)): cls[find(i)].append(i)
    print('round %d: pool %d nodes %d (+%d) classes %d merged %d ematch %d'
          % (rd + 1, len(pool), len(terms), len(terms) - n0, len(cls),
             sum(1 for c in cls.values() if len(c) > 1), tot), flush=True)
    if len(terms) > CAP:
        print('  node cap hit'); break
print()
pairs = [('a*a', 'b*b'), ('a*a', '(a*a)*(a*a)'), ('a', 'a*a'), ('a', 'b'), ('a*b', 'b*a'),
         ('a*a', 'a*b'), ('(a*a)*(a*a)', '(b*b)*(b*b)'), ('a*a', 'a*(a*a)'), ('a*a', '(a*a)*a')]
for p, q in pairs:
    if p in seeds and q in seeds:
        print('  %-14s = %-14s : %s' % (p, q,
              'DERIVED' if find(ids[seeds[p]]) == find(ids[seeds[q]]) else 'no'))
cls = collections.defaultdict(list)
for i in range(len(terms)): cls[find(i)].append(i)
small = [c for c in cls.values() if len([i for i in c if sz[i] <= 9]) > 1]
print()
print('merged classes with >1 member of size <= 9: %d' % len(small))
for c in sorted(small, key=lambda c: min(sz[i] for i in c))[:10]:
    ts = sorted([terms[i] for i in c if sz[i] <= 11], key=lambda t: len(show(t)))[:5]
    print('   {%s}' % ' = '.join(show(t) for t in ts))
