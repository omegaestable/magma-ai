"""Are there elements that are BOTH an A-value ((Y*X)*Y) and a B-value (X*(X*Z))?
That is exactly the configuration in which the 23354 root has no rule to fire."""
import sys, time, itertools
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 23354
cat = catalog(); law = normalise(parse_eq(cat[EQ]))
src = open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chk%d.py' % EQ, encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); rules = ns['rules']
C = cf.Closed(law, rules)
def sh(t): return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (sh(t[1]), sh(t[2]))

MAX = int(sys.argv[1]) if len(sys.argv) > 1 else 7
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
P = [t for n in sorted(terms) for t in terms[n]]
print('pool', len(P))

t0 = time.time()
Aval = {}
for Y in P:
    for X in P:
        try:
            v = C.op(C.op(Y, X), Y)
        except RecursionError:
            continue
        Aval.setdefault(v, (Y, X))
print('A-values', len(Aval), round(time.time() - t0, 1))
Bval = {}
for X in P:
    for Z in P:
        try:
            v = C.op(X, C.op(X, Z))
        except RecursionError:
            continue
        Bval.setdefault(v, (X, Z))
print('B-values', len(Bval), round(time.time() - t0, 1))
inter = [t for t in Aval if t in Bval]
print('BOTH', len(inter))
for t in inter[:10]:
    Y, X = Aval[t]; X2, Z = Bval[t]
    print('   x=%s   A(Y=%s,X=%s)  B(X=%s,Z=%s)' % (sh(t), sh(Y), sh(X), sh(X2), sh(Z)))
    # the law instance that would break: y := Y? no - any y with op(y,x) decoded.
    # left-decode witness: y such that op(y,x) decodes -> y = A-value with payload ... use B's X
    print('      op(%s,%s) = %s' % (sh(X2), sh(t), sh(C.op(X2, t))))
