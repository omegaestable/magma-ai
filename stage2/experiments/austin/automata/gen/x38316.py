"""x38316.py [deep|pat]  -- checks of the 38316 rule set against the DUAL L-form law (the generated
chk38316.py tests the R-form law against the unflipped L-form model, which fails everything), and an
instrumented evaluation of the five products of the L-form law recording which rule fires where."""
import sys, os, json, random, time, itertools
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE)
sys.setrecursionlimit(20000)
import closedform as cf
import fuzz as fz
import freetest2 as ft
from freemodel import normalise, catalog, pvars, size, rand_term
from laws import parse_eq

def dual_pat(p):
    return p if isinstance(p, str) else (dual_pat(p[1]), dual_pat(p[0]))

EQ = 38316
src = open(os.path.join(HERE, 'gen', 'chk%d.py' % EQ), encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns)
rules = ns['rules']
orig = normalise(parse_eq(catalog()[EQ]))
law = ('x', dual_pat(orig[1]))
print('L-law', law)
for i, r in enumerate(rules): print('R%d' % (i + 1), cf.show_rule(r))

def show(t):
    if t == 'recursion': return t
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))

def which(C, u, v):
    r = C.op(u, v)
    if r == ('J', u, v): return 0
    for i, (conds, x, tag) in enumerate(C.rules):
        if C.check(conds, u, v) and C.ev(x, u, v) is not None: return i + 1
    return 9

def pattern(C, s):
    x, y, z = s['x'], s['y'], s['z']
    P1 = C.op(z, x); P2 = C.op(y, P1); P3 = C.op(P2, y); P4 = C.op(x, P3); P5 = C.op(y, P4)
    return (which(C, z, x), which(C, y, P1), which(C, P2, y), which(C, x, P3), which(C, y, P4)), P5 == x

mode = sys.argv[1] if len(sys.argv) > 1 else 'deep'
if mode == 'deep':
    for sd in (11, 12, 13):
        C = cf.Closed(law, rules)
        t, f = cf.deep_tests(C, law, 3000, 300, sd)
        print('deep seed', sd, 'tested', t, 'fails', len(f), 'fired', C.fired, flush=True)
        for s, r in f[:3]: print('  FAIL', {k: show(v) for k, v in s.items()}, '->', show(r))
    C = cf.Closed(law, rules)
    t, f = fz.fuzz(C, law, rules, 12000, seed=5)
    print('fuzz tested', t, 'fails', len(f), 'fired', C.fired, flush=True)
    for s, r in f[:3]: print('  FAIL', {k: show(v) for k, v in s.items()}, '->', show(r))
    sys.exit(0)

# ---- pattern census ----
C = cf.Closed(law, rules)
random.seed(int(sys.argv[2]) if len(sys.argv) > 2 else 1)
pats = {}
def rec(s):
    try:
        p, ok = pattern(C, s)
    except RecursionError:
        return
    tot = sum(size(v) for v in s.values())
    if p not in pats or tot < pats[p][0]:
        pats[p] = (tot, {k: show(v) for k, v in s.items()}, ok)
    cnt[p] = cnt.get(p, 0) + 1
    if not ok:
        bad.append({k: show(v) for k, v in s.items()})
cnt = {}; bad = []
# (1) deep-test triples
class Shim: pass
F = Shim(); F.vars = pvars(law[1]); F.rhs = law[1]; F.ev = lambda p, s: C.evp(p, s)
pool = []
for _ in range(4000):
    s = ft.nested_triple(F, pool)
    if max(size(t) for t in s.values()) > 120: continue
    rec(s)
    for t in s.values():
        if size(t) <= 40 and len(pool) < 400: pool.append(t)
print('after deep census:', len(cnt), 'patterns, bad', len(bad), flush=True)
# (2) rule-shaped fuzz pool
pool2 = [('g', i) for i in range(3)]
for d in range(3):
    inst = fz.instances(rules, pool2, 8, d, C)
    for u, v in inst:
        for t in (u, v):
            if size(t) <= 60 and t not in pool2: pool2.append(t)
        try:
            r = C.op(u, v)
            if size(r) <= 60 and r not in pool2: pool2.append(r)
        except RecursionError:
            pass
    if len(pool2) > 3000: pool2 = pool2[:3000]
vs = ['x', 'y', 'z']
def subterms(t, acc):
    acc.append(t)
    if t[0] == 'J': subterms(t[1], acc); subterms(t[2], acc)
    return acc
for _ in range(30000):
    s = {v: random.choice(pool2) for v in vs}
    r = random.random()
    if r < 0.2:
        a, b = random.sample(vs, 2); s[a] = s[b]
    elif r < 0.4:
        a, b = random.choice(pool2), random.choice(pool2)
        try: s[random.choice(vs)] = C.op(a, b)
        except RecursionError: pass
    elif r < 0.7:
        # x or z a subterm / product-with-subterm of y (and vice versa)
        src_v, dst_v = random.sample(vs, 2)
        subs = subterms(s[src_v], [])
        t = random.choice(subs)
        if random.random() < 0.5:
            try: t = C.op(t, random.choice(subs)) if random.random() < 0.5 else C.op(random.choice(subs), t)
            except RecursionError: pass
        s[dst_v] = t
    if max(size(t) for t in s.values()) > 140: continue
    rec(s)
print('after fuzz census:', len(cnt), 'patterns, bad', len(bad), flush=True)
for p in sorted(pats, key=lambda p: (pats[p][0])):
    print('PAT', p, 'count', cnt[p], 'ok', pats[p][2], 'minsize', pats[p][0], pats[p][1])
print('BAD', len(bad))
for b in bad[:5]: print('  ', b)
