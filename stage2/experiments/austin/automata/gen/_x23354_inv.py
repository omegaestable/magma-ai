"""Candidate invariants for the 23354 model, tested over all pairs from a term pool."""
import sys, time
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
def a1(t): return t[1] if t[0] == 'J' else t
def a2(t): return t[2] if t[0] == 'J' else t

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
P = [t for n in sorted(terms) for t in terms[n]]
print('pool', len(P))

t0 = time.time()
nd = 0; bad_a = []; bad_d = []
for u in P:
    for v in P:
        try: r = C.op(u, v)
        except RecursionError: continue
        if r == ('J', u, v): continue
        nd += 1
        if not (size(r) < size(u)): bad_a.append((u, v, r))
print('decoded pairs', nd, '| (a) sz(op u v) < sz u  violations:', len(bad_a), round(time.time()-t0, 1))
for u, v, r in bad_a[:3]: print('    u=%s v=%s r=%s' % (sh(u), sh(v), sh(r)))

# (b) op(a2 x, x) = a1 x ?
bb = [x for x in P if x[0] == 'J' and C.op(a2(x), x) == a1(x)]
print('(b) op(a2 x, x) = a1 x  instances:', len(bb))
for x in bb[:3]: print('    x=%s' % sh(x))

# (d) BB(t): exists w in pool with op(a2 t, w) = a1 t decoded -> sz(a1 t) < sz(a2 t) ?
viol = []
nbb = 0
for t in P:
    if t[0] != 'J': continue
    for w in P:
        try: r = C.op(a2(t), w)
        except RecursionError: continue
        if r == ('J', a2(t), w): continue
        if r == a1(t):
            nbb += 1
            if not (size(a1(t)) < size(a2(t))): viol.append((t, w))
            break
print('(d) BB witnesses', nbb, 'violations of sz(a1 t) < sz(a2 t):', len(viol), round(time.time()-t0, 1))
for t, w in viol[:3]: print('    t=%s w=%s' % (sh(t), sh(w)))
