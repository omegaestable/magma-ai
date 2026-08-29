"""coincidence-targeted check of the 11280 rule set: x, z drawn from subterms / products of rule-shaped y."""
import sys, random, time
sys.path.insert(0, 'C:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
sys.setrecursionlimit(20000)
import closedform as cf
from freemodel import normalise, catalog, size, rand_term
from laws import parse_eq
law = normalise(parse_eq(catalog()[11280]))
# the rule list, verbatim from gen/chk11280.py
src = open('C:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chk11280.py', encoding='utf-8').read()
rules_line = [l for l in src.splitlines() if l.startswith('rules = ')][0]
ns = {}
exec(rules_line, ns)
rules = ns['rules']
C = cf.Closed(law, rules)
A, B = law[1]

def J(a, b): return ('J', a, b)
def subterms(t, acc=None):
    if acc is None: acc = []
    acc.append(t)
    if t[0] == 'J':
        subterms(t[1], acc); subterms(t[2], acc)
    return acc

N = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
seed = int(sys.argv[2]) if len(sys.argv) > 2 else 11280
random.seed(seed)
pool = [rand_term(random.choice([0, 1, 1, 2, 2, 3])) for _ in range(200)]
fails = []
tested = 0
t0 = time.time()

def ev_law(x, y, z):
    s = {'x': x, 'y': y, 'z': z}
    return C.op(C.evp(A, s), C.evp(B, s))

def ymaker():
    a, b, c, d = (random.choice(pool) for _ in range(4))
    q, r, s_, t = (random.choice(pool) for _ in range(4))
    k = random.randrange(12)
    if k == 0: return J(J(a, J(b, a)), J(c, a))          # P1 shape for u = a
    if k == 1: return J(J(a, J(b, a)), d)                # P2 shape
    if k == 2: return J(J(a, b), J(c, a))                # P3 shape
    if k == 3: return J(J(a, b), c)                      # P4 shape
    if k == 4: return J(q, J(r, q))                      # a1 y = a2 (a2 y)
    if k == 5: return J(q, J(J(s_, J(t, q)), q))          # r = J s (J t q)
    if k == 6: return J(q, q)
    if k == 7: return C.op(a, b)                         # a product
    if k == 8: return J(a, C.op(b, a))                   # B-shape J y' A
    if k == 9: return J(J(a, C.op(b, a)), C.op(c, a))    # D-shape
    if k == 10: return C.op(a, J(J(a, J(b, a)), J(c, a)))  # a decoded value
    return random.choice(pool)

def xz_candidates(y):
    subs = subterms(y)
    cands = list(subs) + [y]
    for _ in range(6):
        s1, s2 = random.choice(subs), random.choice(subs)
        cands.append(C.op(s1, s2))
        cands.append(J(s1, s2))
    # the D-fire candidates from the hand analysis
    for zz in (y, random.choice(subs)):
        Av = C.op(zz, y)
        Bv = J(y, Av)
        w = random.choice(subs)
        cands.append(J(Bv, w))
        cands.append(J(Bv, J(w, Bv)))
        cands.append(J(J(Bv, J(w, Bv)), J(w, Bv)))
    # y-shape relatives
    if y[0] == 'J':
        cands.append(y[1])
        if y[1][0] == 'J': cands.append(y[1][1]); cands.append(y[1][2])
        cands.append(y[2])
    return cands

while tested < N and time.time() - t0 < 600:
    y = ymaker()
    if size(y) > 200: continue
    cands = xz_candidates(y)
    for _ in range(4):
        x = random.choice(cands); z = random.choice(cands)
        if random.random() < 0.3: z = y
        if random.random() < 0.15: x = y
        if max(size(x), size(z)) > 200: continue
        try:
            r = ev_law(x, y, z)
        except RecursionError:
            fails.append(('recursion', x, y, z)); tested += 1; continue
        tested += 1
        if r != x:
            fails.append((r, x, y, z))
            if len(fails) <= 3:
                print('FAIL sizes x,y,z =', size(x), size(y), size(z))
                print('  x =', x); print('  y =', y); print('  z =', z); print('  got =', r)
print('tested', tested, 'fails', len(fails), 'secs', round(time.time() - t0, 1), 'fired', C.fired)
