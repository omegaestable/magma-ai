import sys, os, json, random, itertools, time
sys.path.insert(0, 'C:\\Users\\nacho\\Documents\\GitHub\\magma-ai\\stage2\\experiments\\austin\\automata')
import closedform as cf
from freemodel import normalise, catalog, size
from laws import parse_eq
from leangen import dual_pat
orig = normalise(parse_eq(catalog()[39163]))
law = ('x', dual_pat(orig[1]))
U = ('U',); V = ('V',)
def A1(e): return ('A1', e)
def A2(e): return ('A2', e)
def OP(a, b): return ('OP', a, b)
def JJ(a, b): return ('J', a, b)
def TG(e): return ('TG', e)
def EQ(a, b): return ('EQ', a, b)
def OPEQ(a, b): return ('OPEQ', a, b)
R1 = ([TG(V), EQ(U, A1(V)), TG(A2(V)), TG(A1(A2(V))), EQ(U, A2(A1(A2(V)))), TG(A2(A2(V))), EQ(U, A2(A2(A2(V))))], A1(A2(A2(V))), 'free')
R2 = ([TG(V), EQ(U, A1(V)), TG(A2(V)), TG(A1(A2(V))), EQ(U, A2(A1(A2(V)))), TG(U), OPEQ(OP(A1(U), U), A2(A2(V)))], A1(U), 'B11l')
R3 = ([TG(V), EQ(U, A1(V)), TG(A2(V)), TG(A2(A2(V))), EQ(U, A2(A2(A2(V)))), TG(U), OPEQ(OP(A1(U), U), A1(A2(V)))], A1(A2(A2(V))), 'B10l')
R4 = ([TG(V), EQ(U, A1(V)), TG(A2(V)), TG(U), OPEQ(OP(A1(U), U), A1(A2(V))), OPEQ(OP(A1(U), U), A2(A2(V)))], A1(U), 'B10l,B11l')
# repair: v = J u z, u = J p p, a1 z = p, op p z = p  ->  J z u   (the payload x = J z u whose product (z*u)*((z*u)*u) collapsed to z by R4)
R5 = ([TG(V), EQ(U, A1(V)), TG(A2(V)), TG(U), EQ(A1(U), A2(U)), EQ(A1(U), A1(A2(V))), OPEQ(OP(A1(A2(V)), A2(V)), A1(U))], JJ(A2(V), U), 'rep5')
RULESETS = {'base': [R1, R2, R3, R4], 'r5': [R1, R2, R3, R4, R5]}
variant = sys.argv[1] if len(sys.argv) > 1 else 'base'
rules = RULESETS[variant]
C = cf.Closed(law, rules)
print("law", law, "variant", variant, "nrules", len(rules))

def J(a, b): return ('J', a, b)
def g(n): return ('g', n)
def show(t):
    if t[0] == 'g': return 'g%d' % t[1]
    return '(' + show(t[1]) + ' ' + show(t[2]) + ')'

A_, B_ = law[1]
def lawlhs(s):
    return C.op(C.evp(A_, s), C.evp(B_, s))

# --- hand-derived instance ---
w = g(0); t = g(1)
y = J(w, w)
z = J(w, J(J(t, w), J(w, w)))
x = J(z, y)
s = {'x': x, 'y': y, 'z': z}
lhs = lawlhs(s)
print("HAND instance: x =", show(x), " y =", show(y), " z =", show(z))
print("  law lhs =", show(lhs), "  equal?", lhs == x)

def subterms(t, acc):
    acc.add(t)
    if t[0] == 'J':
        subterms(t[1], acc); subterms(t[2], acc)
    return acc

seed = int(sys.argv[2]) if len(sys.argv) > 2 else 3
random.seed(seed)
atoms = [g(0), g(1), g(2)]
def rterm(d):
    if d == 0 or random.random() < 0.3: return random.choice(atoms)
    return J(rterm(d - 1), rterm(d - 1))
subpats = cf.fm.all_subpatterns(law[1], [])
MAXSZ = 160

def grow(pool, rounds):
    """rule-driven closure: encodings, decoding chains, R-shaped coincidences"""
    for _ in range(rounds):
        r = random.random()
        u = random.choice(pool); a = random.choice(pool); b = random.choice(pool)
        new = []
        if r < 0.2:
            new.append(C.op(a, b)); new.append(J(a, b))
        elif r < 0.45:
            sp = random.choice(subpats)
            s0 = {v: random.choice(pool) for v in ('x', 'y', 'z')}
            if random.random() < 0.5: s0[random.choice(['x', 'z'])] = s0['y']
            if random.random() < 0.3: s0['x'] = s0['z']
            new.append(C.evp(sp, s0))
        elif r < 0.6:
            # encoding of a by u with z-slot b, and its decode
            enc = C.evp(B_, {'x': a, 'y': u, 'z': b})
            new += [enc, C.op(u, enc), J(u, enc)]
        elif r < 0.75:
            if u[0] == 'J':
                p = C.op(u[1], u)
                new += [p, J(p, p), J(u, J(p, p)), J(u, J(J(b, u), p)), J(u, J(p, J(a, u))), J(J(b, u), p), J(p, J(a, u))]
        elif r < 0.9:
            # the R5 family: y = J p p, z an encoding of p by p, x = J z y ; and one level up
            p = u
            zz = C.evp(B_, {'x': p, 'y': p, 'z': b})
            if random.random() < 0.5: zz = J(p, J(J(b, p), J(p, p)))
            yy = J(p, p); xx = J(zz, yy)
            new += [zz, yy, xx, C.op(zz, yy), C.op(xx, yy), C.op(yy, zz), J(yy, zz)]
        else:
            if u[0] == 'J':
                p = u[1]
                if C.op(p, u) == p:
                    yy = J(p, p); xx = J(u, yy)
                    new += [yy, xx, J(yy, u), C.op(yy, J(yy, u))]
        for q in new:
            if size(q) <= MAXSZ and q not in pool: pool.append(q)
    return pool

fails = []
tested = 0
t0 = time.time()
N = int(sys.argv[3]) if len(sys.argv) > 3 else 20000
while tested < N and time.time() - t0 < 900:
    base = [rterm(random.choice([1, 2, 2, 3])) for _ in range(3)]
    pool = set()
    for b in base: subterms(b, pool)
    pool = list(pool) + atoms[:2]
    pool = grow(pool, random.choice([3, 5, 8, 12]))
    for _ in range(8):
        s = {'x': random.choice(pool), 'y': random.choice(pool), 'z': random.choice(pool)}
        r = random.random()
        yv = s['y']
        if r < 0.12 and yv[0] == 'J': s['x'] = yv[1]
        elif r < 0.24 and yv[0] == 'J': s['z'] = yv[1]
        elif r < 0.36: s['x'] = C.op(s['z'], yv)
        elif r < 0.48: s['x'] = J(s['z'], yv)
        elif r < 0.56: s['z'] = C.op(s['x'], yv)
        elif r < 0.64: s['x'] = s['z']
        elif r < 0.72 and yv[0] == 'J' and yv[1] == yv[2]: s['x'] = J(s['z'], yv)
        if max(size(v) for v in s.values()) > MAXSZ: continue
        try:
            lhs = lawlhs(s)
        except RecursionError:
            fails.append((s, 'recursion')); tested += 1; continue
        tested += 1
        if lhs != s['x']:
            fails.append((s, lhs))
print("targeted: tested", tested, "fails", len(fails), "time %.1f" % (time.time() - t0), "fired", C.fired)
fails.sort(key=lambda f: sum(size(v) for v in f[0].values()))
seen = set()
shown = 0
for s, lhs in fails:
    key = (s['x'], s['y'], s['z'])
    if key in seen: continue
    seen.add(key)
    print("FAIL x =", show(s['x']), "y =", show(s['y']), "z =", show(s['z']), "-> lhs =", show(lhs) if lhs != 'recursion' else lhs)
    shown += 1
    if shown >= 8: break
if len(sys.argv) > 4:
    Nd = int(sys.argv[4])
    for sd in (11, 12, 13, 14):
        C2 = cf.Closed(law, rules)
        t1 = time.time()
        tested, fails = cf.deep_tests(C2, law, Nd, 900, sd)
        print("deep_tests seed", sd, "tested", tested, "fails", len(fails), "time %.1f" % (time.time() - t1))
        for s, lhs in fails[:3]:
            print("  FAIL x =", show(s['x']), "y =", show(s['y']), "z =", show(s['z']), "-> lhs =", show(lhs) if lhs != 'recursion' else lhs)
