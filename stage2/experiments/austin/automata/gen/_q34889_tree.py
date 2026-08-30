"""Case tree for 34889's quotient model: which rule fires at each of the 4 chain products,
coverage per cell, and any law failure inside a cell.  Also chained-encoding constructions that
force the deep cells (a sampler cannot reach a cell of measure zero -- rail 50 / W3-6)."""
import sys, os, itertools, random, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qmod
qmod.UNARY = []
from qmod import E, sz, show, terms_upto
from q34889 import M, J, msr

Mo = M()
op = Mo.op

def which(u, v):
    """name the rule that fires on (u,v)"""
    if u == v: return 'SQ'
    m = msr(u, v)
    if v[0] == 'J' and v[2] == E:
        w = v[1]
        if w[0] == 'J':
            a, b = w[1], w[2]
            if not (a == E and b == E) and Mo.g(u, a, m) == b: return 'DEC'
        if u[0] == 'J' and u[1] == w and Mo.g(E, w, m) == u[2]: return 'SELFE'
    return 'FREE'

def chain(x, y, z):
    s = op(y, y)                     # always E
    q = op(z, x)
    p = op(x, q)
    c = op(p, s)
    r = op(z, c)
    cell = (which(z, x), which(x, q), which(p, s), which(z, c))
    return cell, r

def code(z, x):
    """the code of x under z: op(op(x, op(z,x)), E)"""
    return op(op(x, op(z, x)), E)

cells = collections.Counter(); bad = []
pool = terms_upto(7, 2)
random.seed(1)
sample = pool + [random.choice(pool) for _ in range(0)]
for x in pool:
    for z in pool:
        cell, r = chain(x, ('g', 0), z)
        cells[cell] += 1
        if r != x: bad.append((x, z, cell, r))
print('exhaustive <=7/2gen pairs:', len(pool) ** 2, 'cells:', len(cells), 'fails:', len(bad))

# chained encodings: force the root to see a code whose body is itself a code, 3 levels deep
gens = [('g', 0), ('g', 1), E, J(('g', 0), E), J(E, ('g', 0)), J(('g',0),('g',1))]
built = []
for z0 in gens:
    for x0 in gens:
        c1 = code(z0, x0)
        built.append(c1)
        for z1 in gens:
            c2 = code(z1, c1)
            built.append(c2)
            c3 = code(z0, c2)
            built.append(c3)
built = [t for t in set(built) if sz(t) <= 60]
print('chained-encoding pool:', len(built))
for x in built + gens:
    for z in built + gens:
        cell, r = chain(x, ('g', 1), z)
        cells[cell] += 1
        if r != x: bad.append((x, z, cell, r))
print('after chained encodings: cells:', len(cells), 'fails:', len(bad))
for c, n in sorted(cells.items(), key=lambda kv: -kv[1]):
    print('   %-34s %d' % (str(c), n))
for x, z, cell, r in bad[:6]:
    print('FAIL x=%s z=%s cell=%s -> %s' % (show(x), show(z), cell, show(r)))

# identity probe: x built out of the model's own codes, three levels deep, y ranging over the pool
print('--- identity probe (x = deep codes, y over a pool, z over a pool) ---')
n = 0; nf = 0
small = [('g', 0), ('g', 1), E, J(('g',0),E), J(E,('g',0)), J(('g',0),('g',1)), J(('g',0),J(E,('g',0)))]
for x in built:
    for z in small:
        for y in small:
            n += 1
            _, r = chain(x, y, z)
            if r != x:
                nf += 1
                if nf <= 3: print('   FAIL x=%s y=%s z=%s -> %s' % (show(x), show(y), show(z), show(r)))
print('identity probe assignments:', n, 'fails:', nf)
