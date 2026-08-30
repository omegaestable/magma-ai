"""Hunt for the dangerous root case of 23354: W = op(y,x) decoded AND F = op(x,z) decoded.
Brute force over all terms up to a size bound on 2 generators."""
import sys, itertools, collections
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 23354
cat = catalog(); law = normalise(parse_eq(cat[EQ]))
src = open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chk%d.py' % EQ, encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); rules = ns['rules']
C = cf.Closed(law, rules)

MAX = int(sys.argv[1]) if len(sys.argv) > 1 else 9
NG = int(sys.argv[2]) if len(sys.argv) > 2 else 2

terms = {1: [('g', i) for i in range(NG)]}
for n in range(3, MAX + 1, 2):
    acc = []
    for a in range(1, n - 1):
        b = n - 1 - a
        for t1 in terms.get(a, []):
            for t2 in terms.get(b, []):
                acc.append(('J', t1, t2))
    terms[n] = acc
allt = [t for n in sorted(terms) for t in terms[n]]
print('terms', len(allt))

def which(u, v):
    for i, (conds, x, tag) in enumerate(C.rules):
        if C.check(conds, u, v):
            r = C.ev(x, u, v)
            if r is not None:
                return i
    return -1

decL = collections.defaultdict(list)   # x -> [y : op(y,x) decoded]
decR = collections.defaultdict(list)   # x -> [z : op(x,z) decoded]
for x in allt:
    for y in allt:
        try:
            if which(y, x) >= 0: decL[x].append(y)
        except RecursionError: pass
    for z in allt:
        try:
            if which(x, z) >= 0: decR[x].append(z)
        except RecursionError: pass
both = [x for x in allt if decL[x] and decR[x]]
print('x with a left-decode :', len(decL), 'with a right-decode:', len([x for x in allt if decR[x]]))
print('x with BOTH          :', len(both))
tab = collections.Counter()
bad = 0
for x in both:
    for y in decL[x][:4]:
        for z in decR[x][:4]:
            W = C.op(y, x); U = C.op(W, y); Fv = C.op(x, z); V = C.op(x, Fv)
            root = C.op(U, V)
            tab[(which(y, x), which(x, z), which(W, y), which(x, Fv), which(U, V), root == x)] += 1
            if root != x and bad < 5:
                bad += 1
                print('  BAD x=%s y=%s z=%s -> %s' % (x, y, z, root))
for k, c in sorted(tab.items(), key=lambda kv: -kv[1]):
    print('   ', k, c)
