"""Census of which rule fires at each product of the 5837 chain, over a rich pool.

chain: P0 = op z y ; P1 = op P0 y ; L3 = op y P1 ; E = op x L3 ; F = op y E   (must be x)
Prints the distinct 5-tuples of (rule index or 'f' for free) and a witness for each.
"""
import sys, os, random, time
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, leangen
from freemodel import normalise, catalog, size, rand_term
from laws import parse_eq
import importlib.util
spec = importlib.util.spec_from_file_location('_x5837_val', 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/_x5837_val.py')

# rebuild rules here (do not exec the validator)
U = ('U',); V = ('V',)
def A1(e): return ('A1', e)
def A2(e): return ('A2', e)
def OP(a, b): return ('OP', a, b)
def TG(e): return ('TG', e)
def EQ_(a, b): return ('EQ', a, b)
def OPEQ(a, b): return ('OPEQ', a, b)
R1 = ([TG(V), TG(A2(V)), EQ_(U, A1(A2(V))), TG(A2(A2(V))), TG(A1(A2(A2(V)))), EQ_(U, A2(A1(A2(A2(V))))), EQ_(U, A2(A2(A2(V))))], A1(V), 'free')
R2 = ([TG(V), TG(A2(V)), EQ_(U, A1(A2(V))), TG(A2(A2(V))), EQ_(U, A2(A2(A2(V)))), TG(U), TG(A2(U)), OPEQ(OP(A1(A2(U)), U), A1(A2(A2(V))))], A1(V), 'B110l')
R2p = ([TG(V), TG(A2(V)), EQ_(U, A1(A2(V))), TG(A2(A2(V))), EQ_(U, A2(A2(A2(V)))), OPEQ(OP(U, U), A1(A2(A2(V))))], A1(V), 'R2p')
R3 = ([TG(V), TG(A2(V)), EQ_(U, A1(A2(V))), TG(U), TG(A2(U)), OPEQ(OP(A1(A2(U)), U), A2(A2(V))), OPEQ(OP(A1(A2(U)), U), A1(A2(U)))], A1(V), 'B11l,B110l')
q = A1(U); xx = A1(q)
common = [EQ_(V, U), TG(U), TG(A2(U)), EQ_(A1(U), A1(A2(U))), OPEQ(OP(A1(U), U), A1(U)), TG(q)]
R4a = (common + [TG(A2(q)), TG(A1(A2(q))), EQ_(xx, A2(A1(A2(q)))), EQ_(xx, A2(A2(q)))], xx, 'R4a')
R4b = (common + [TG(A2(q)), EQ_(xx, A2(A2(q))), TG(xx), TG(A2(xx)), OPEQ(OP(A1(A2(xx)), xx), A1(A2(q)))], xx, 'R4b')
R4bp = (common + [TG(A2(q)), EQ_(xx, A2(A2(q))), OPEQ(OP(xx, xx), A1(A2(q)))], xx, 'R4bp')
R4c = (common + [TG(xx), TG(A2(xx)), OPEQ(OP(A1(A2(xx)), xx), A2(q)), OPEQ(OP(A1(A2(xx)), xx), A1(A2(xx)))], xx, 'R4c')
RULES = [R1, R2, R2p, R3, R4a, R4b, R4bp, R4c]

EQN = 5837
cat = catalog(); law = normalise(parse_eq(cat[EQN]))
C = cf.Closed(law, RULES)

def which(a, b):
    """index (1-based) of the rule that fires on (a,b), or 'f'"""
    r = C.op(a, b)
    if r == ('J', a, b):
        # could still be a rule returning J a b; check
        pass
    for i, (conds, x, tag) in enumerate(RULES):
        if C.check(conds, a, b):
            e = C.ev(x, a, b)
            if e is not None:
                return i + 1
    return 'f'

def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))

def chain(x, y, z):
    P0 = C.op(z, y); P1 = C.op(P0, y); L3 = C.op(y, P1); E = C.op(x, L3); F = C.op(y, E)
    return (P0, P1, L3, E, F)

def modes(x, y, z):
    P0 = C.op(z, y); P1 = C.op(P0, y); L3 = C.op(y, P1); E = C.op(x, L3); F = C.op(y, E)
    return (which(z, y), which(P0, y), which(y, P1), which(x, L3), which(y, E)), F

def g(n): return ('g', n)

def op(a, b): return C.op(a, b)
def inner(a, b): return op(a, op(op(b, a), a))       # y-side inner: u*((w*u)*u)  -- law B side minus x
def enc(p, u, w): return op(p, inner(u, w))           # a full encoding of p relative to u

base = [g(0), g(1), g(2)]
pool = list(base)
for a in base:
    for b in base:
        for t in (op(a, b), inner(a, b), ('J', a, b)):
            if t not in pool: pool.append(t)
for a in base:
    for b in base:
        for c in base:
            t = enc(a, b, c)
            if t not in pool: pool.append(t)
print('pool', len(pool))

seen = {}
bad = []
def rec(x, y, z, tag):
    if max(size(x), size(y), size(z)) > 500: return
    try:
        m, F = modes(x, y, z)
    except RecursionError:
        return
    if F != x:
        bad.append((x, y, z, tag))
    if m not in seen:
        seen[m] = (tag, show(x)[:60], show(y)[:70], show(z)[:60])

t0 = time.time()
# level-1 cube
for x in pool:
    for y in pool:
        for z in pool:
            rec(x, y, z, 'L1')
print('cube done', len(seen), 'secs', round(time.time() - t0, 1), flush=True)
# coincidence families
random.seed(7)
n = 0
while n < 60000 and time.time() - t0 < 240:
    p, u, w, x = (random.choice(pool) for _ in range(4))
    y = enc(p, u, w)
    rec(x, y, u, 'crit'); rec(x, y, p, 'crit2'); rec(p, y, u, 'crit3')
    z2 = inner(x, random.choice(pool))
    rec(x, enc(z2, z2, random.choice(pool)), z2, 'hole')
    n += 4
print('coincidence done', len(seen), 'secs', round(time.time() - t0, 1), flush=True)
# random deep
for i in range(4000):
    random.seed(1000 + i)
    x = rand_term(3); y = rand_term(3); z = rand_term(3)
    rec(x, y, z, 'rand')

print('bad', len(bad))
print('distinct mode tuples:', len(seen))
for m in sorted(seen, key=lambda t: str(t)):
    tag, sx, sy, sz = seen[m]
    print('  (z*y)=%-3s (P0*y)=%-3s (y*P1)=%-3s (x*L3)=%-3s (y*E)=%-3s   [%s]' % (m[0], m[1], m[2], m[3], m[4], tag))
    print('        x=%s\n        y=%s\n        z=%s' % (sx, sy, sz))
