"""Is every decode of the 3-rule 23354 model an 'AF read' (u = J (J (a2 u) p) (a2 u))?
Search R3-firing pairs (u,v) with v = J p (J p q) and check whether op(a2 u, a1 v) is itself a decode."""
import sys, time, collections
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 23354
cat = catalog(); law = normalise(parse_eq(cat[EQ]))
src = open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chk%d.py' % EQ, encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); rules4 = ns['rules']
rules = [rules4[0], rules4[1], rules4[2]]
C = cf.Closed(law, rules)

MAXU = int(sys.argv[1]) if len(sys.argv) > 1 else 11
MAXP = int(sys.argv[2]) if len(sys.argv) > 2 else 7
NG = 2

def gen(maxn):
    terms = {1: [('g', i) for i in range(NG)]}
    for n in range(3, maxn + 1, 2):
        acc = []
        for a in range(1, n - 1):
            b = n - 1 - a
            for t1 in terms.get(a, []):
                for t2 in terms.get(b, []):
                    acc.append(('J', t1, t2))
        terms[n] = acc
    return [t for n in sorted(terms) for t in terms[n]]

US = gen(MAXU); PS = gen(MAXP)
print('u candidates', len(US), 'p,q candidates', len(PS))

def which(u, v):
    for i, (conds, x, tag) in enumerate(C.rules):
        if C.check(conds, u, v):
            r = C.ev(x, u, v)
            if r is not None:
                return i
    return -1

def AF(u, p):
    return u[0] == 'J' and u[1][0] == 'J' and u[1][1] == u[2] and u[1][2] == p

n3 = 0; nII = 0; nNotAF = 0
ex = []
t0 = time.time()
for p in PS:
    for q in PS:
        v = ('J', p, ('J', p, q))
        if size(v) > 2 * MAXP + 3: continue
        for u in US:
            if u[0] != 'J': continue
            try:
                w = which(u, v)
            except RecursionError:
                continue
            if w < 0: continue
            r = C.op(u, v)
            if not AF(u, r):
                nNotAF += 1
                if len(ex) < 6: ex.append(('notAF', u, v, r, w))
            if w == 2:
                n3 += 1
                inner = C.op(u[2], p)   # op(a2 u, a1 v)
                if inner != ('J', u[2], p):
                    nII += 1
                    if len(ex) < 12: ex.append(('II', u, v, inner, w))
    if time.time() - t0 > 600: print('TIMEOUT'); break
print('R3 firings', n3, 'of which (II) inner-decoded', nII, ' decodes that are not AF-reads:', nNotAF)
for e in ex: print('  ', e)
print('secs', round(time.time() - t0, 1))
