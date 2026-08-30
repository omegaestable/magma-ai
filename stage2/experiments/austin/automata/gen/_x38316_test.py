"""Full test battery for a candidate 38316 rule set.

usage: _x38316_test.py <setname|all|v0> [--quick]
Runs: the known counterexample, the hunt family (c decoding), the coincidence battery F1..F6,
then (unless --quick) rv.run_tests on 3 seeds + 20k deep on 2 more seeds.
"""
import sys, os, random, itertools, time
from collections import Counter
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, revalidate as rv, leangen
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 38316
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = ('x', leangen.dual_pat(orig[1]))
GEN = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/'
src = open(GEN + 'chkrep38316.py', encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); ALL = ns['rules']

name = sys.argv[1] if len(sys.argv) > 1 else 'cand'
if name == 'all':
    RULES = ALL
elif name == 'v0':
    RULES = [r for r in ALL if r[2].startswith('V0')]
else:
    ns2 = {}
    exec(open(GEN + '_x38316_rules_%s.py' % name, encoding='utf-8').read(), ns2)
    RULES = ns2['rules']
TAGS = [r[2] for r in RULES]
C = cf.Closed(law, RULES)
print('set %s: %s' % (name, TAGS), flush=True)

def J(a, b): return ('J', a, b)
def g(n): return ('g', n)
def sh(t): return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (sh(t[1]), sh(t[2]))
def which(u, v):
    for i, (conds, xx, tag) in enumerate(C.rules):
        if C.check(conds, u, v) and C.ev(xx, u, v) is not None:
            return i
    return -1

cnt = Counter(); bad = []; wit = {}
def record(x, y, z, fam):
    try:
        a = C.op(z, x); b = C.op(y, a); c = C.op(b, y); d = C.op(x, c); top = C.op(y, d)
        pat = (which(z, x), which(y, a), which(b, y), which(x, c), which(y, d))
    except RecursionError:
        return
    cnt[pat] += 1
    tot = size(x) + size(y) + size(z)
    if pat not in wit or tot < wit[pat][0]:
        wit[pat] = (tot, (x, y, z))
    if top != x:
        bad.append((x, y, z, fam, pat))

def ENC(u, P, Z):
    a = C.op(Z, P); b = C.op(u, a); c = C.op(b, u); return J(P, c)
def CPART(y, Z, P):
    a = C.op(Z, P); b = C.op(y, a); return C.op(b, y)

# ---------- 0: the known counterexample and its family ----------
G5 = [g(i) for i in range(5)]
n0 = 0
for z, y1, W3, A1 in itertools.product(G5, repeat=4):
    W2 = J(W3, y1); w = J(z, W2); y = J(y1, J(w, z)); A = J(A1, z); q = J(y, A); x = J(q, y)
    record(x, y, z, 'HUNT'); n0 += 1
# same family with a bigger y1 (gate passes) and a bigger z (gate cut)
for y1 in (g(0), J(g(0), g(1)), J(J(g(0), g(1)), g(2))):
    for z in (g(2), J(g(2), g(3)), J(J(g(2), g(3)), g(4))):
        for W3 in (g(1), J(g(1), g(0))):
            for A1 in (g(3), J(g(3), g(0))):
                W2 = J(W3, y1); w = J(z, W2); y = J(y1, J(w, z)); A = J(A1, z); q = J(y, A); x = J(q, y)
                record(x, y, z, 'HUNT2'); n0 += 1
print('HUNT: %d instances, failures so far %d' % (n0, len(bad)), flush=True)

# ---------- battery F1..F6 ----------
G = [g(i) for i in range(3)]
terms = list(G)
for _ in range(3):
    new = list(terms)
    for a in terms:
        for b in terms:
            t = J(a, b)
            if size(t) <= 5 and t not in new: new.append(t)
    terms = new
terms = [t for t in terms if size(t) <= 5]
small = [t for t in terms if size(t) <= 3]
for x in terms:
    for y in terms:
        for z in terms:
            if size(x) + size(y) + size(z) <= 11: record(x, y, z, 'F1')
print('F1 done, failures %d' % len(bad), flush=True)
for z, P, Z in itertools.product(small, repeat=3):
    x = ENC(z, P, Z)
    if size(x) <= 120:
        for y in small: record(x, y, z, 'F2')
        record(x, P, z, 'F2'); record(x, Z, z, 'F2')
for z, P, Z in itertools.product(small[:6], repeat=3):
    x1 = ENC(z, P, Z)
    if size(x1) <= 60:
        x = ENC(z, x1, Z)
        if size(x) <= 400:
            for y in small[:4]: record(x, y, z, 'F2b')
for y, Z, z in itertools.product(small, repeat=3):
    x = CPART(y, Z, z)
    if size(x) <= 200: record(x, y, z, 'F3')
for y, Z, z in itertools.product(small[:6], repeat=3):
    x0 = CPART(y, Z, z)
    if size(x0) <= 100:
        for P in small[:4]:
            x = ENC(z, x0, P)
            if size(x) <= 400: record(x, y, z, 'F3b')
for w, x, z in itertools.product(terms, small, small):
    y = J(w, x)
    if size(y) <= 8: record(x, y, z, 'F4')
for w, z, P in itertools.product(small, small, small):
    x = ENC(z, P, w)
    if size(x) <= 120: record(x, J(w, x), z, 'F4b')
random.seed(7)
pool = list(terms)
for _ in range(4000):
    x = random.choice(pool); z = random.choice(pool)
    a = C.op(z, x)
    y = J(random.choice(small), J(random.choice(small), random.choice([a, x, z, C.op(x, z)])))
    if size(y) <= 60: record(x, y, z, 'F5')
random.seed(11)
for _ in range(4000):
    y = random.choice(small); z = random.choice(small); P = random.choice(small); Z = random.choice(small)
    r = random.random()
    if r < 0.34: x = ENC(z, CPART(y, Z, z), P)
    elif r < 0.67: x = CPART(y, Z, ENC(z, P, Z))
    else:
        x = ENC(z, P, Z); y = J(random.choice(small), x)
    if size(x) <= 400 and size(y) <= 400: record(x, y, z, 'F6')
print('battery done: %d instances, %d law failures' % (sum(cnt.values()), len(bad)), flush=True)
for b in bad[:4]:
    print('  BAD [%s] pat=%s' % (b[3], b[4]))
    print('    x=%s' % sh(b[0])); print('    y=%s' % sh(b[1])); print('    z=%s' % sh(b[2]))
print('patterns:')
for pat, c in sorted(cnt.items(), key=lambda kv: -kv[1]):
    print('  %-24s x%-8d %s' % (str(pat), c, '|'.join((TAGS[i] if i >= 0 else 'free') for i in pat)))

if '--quick' not in sys.argv:
    t0 = time.time()
    fails = rv.run_tests(law, RULES, [3, 4, 5], 3000, 12000)
    print('rv.run_tests fails %d (%.0fs) %s' % (len(fails), time.time() - t0, Counter([f[2] for f in fails])), flush=True)
    for f in fails[:3]:
        print('   ', f)
    if not fails:
        for sd in (777, 4242):
            C2 = cf.Closed(law, RULES)
            t, df = cf.deep_tests(C2, law, 20000, 300, sd)
            print('deep seed %d: %d tested, %d fails' % (sd, t, len(df)), flush=True)
