"""Case table for law 38316 over the FUZZ distributions (rule-shaped / closure / critical).

For every sampled assignment record (rule at op(z,x), op(y,a), op(b,y), op(x,c), op(y,d)) where -1 = free.
Prints the distinct patterns with counts and a smallest witness for each."""
import sys, os, random
from collections import Counter
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, leangen, fuzz as fz
from freemodel import normalise, catalog, size, pvars
from laws import parse_eq

EQ = 38316
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = ('x', leangen.dual_pat(orig[1]))
src = open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chkrep38316.py',
           encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); rules = ns['rules']
TAGS = [r[2] for r in rules]

C = cf.Closed(law, rules)
A, B = law[1]
vs = pvars(law[1])

def which(u, v):
    for i, (conds, x, tag) in enumerate(C.rules):
        if C.check(conds, u, v):
            r = C.ev(x, u, v)
            if r is not None:
                return i
    return -1

cnt = Counter(); wit = {}; bad = []

def record(s):
    x, y, z = s['x'], s['y'], s['z']
    try:
        a = C.op(z, x); b = C.op(y, a); c = C.op(b, y); d = C.op(x, c); top = C.op(y, d)
        pat = (which(z, x), which(y, a), which(b, y), which(x, c), which(y, d))
    except RecursionError:
        return
    cnt[pat] += 1
    tot = sum(size(t) for t in (x, y, z))
    if pat not in wit or tot < wit[pat][0]:
        wit[pat] = (tot, dict(s))
    if top != x:
        bad.append(dict(s))

# ---- pool builders copied from fuzz.py ----
def pool_fuzz(seed):
    random.seed(seed)
    pool = [('g', i) for i in range(3)]
    for d in range(3):
        inst = fz.instances(rules, pool, 6, d, C)
        for u, v in inst:
            for t in (u, v):
                if size(t) <= 60 and t not in pool: pool.append(t)
            try:
                r = C.op(u, v)
                if size(r) <= 60 and r not in pool: pool.append(r)
            except RecursionError:
                pass
        if len(pool) > 3000: pool = pool[:3000]
    return pool

def run_fuzz(N, seed):
    pool = pool_fuzz(seed)
    for _ in range(N):
        s = {v: random.choice(pool) for v in vs}
        r = random.random()
        if r < 0.3:
            p, q = random.sample(vs, 2); s[p] = s[q]
        elif r < 0.5:
            aa, bb = random.choice(pool), random.choice(pool)
            try: s[random.choice(vs)] = C.op(aa, bb)
            except RecursionError: pass
        if max(size(t) for t in s.values()) > 140: continue
        record(s)

def run_critical(N, seed):
    random.seed(seed)
    gens = [('g', i) for i in range(4)]
    def prod(aa, bb):
        try: return C.op(aa, bb)
        except RecursionError: return None
    def term(vals, depth):
        if depth == 0 or random.random() < 0.3: return random.choice(vals)
        aa, bb = term(vals, depth - 1), term(vals, depth - 1)
        r = prod(aa, bb)
        return r if r is not None else aa
    subs = []
    def collect(p):
        if isinstance(p, str): return
        subs.append(p); collect(p[0]); collect(p[1])
    collect(law[1])
    def enc(vals, depth):
        s = {v: term(vals, 1) for v in vs}
        if random.random() < 0.4:
            p, q = random.sample(vs, 2); s[p] = s[q]
        if depth > 0 and random.random() < 0.5:
            s[random.choice(vs)] = enc(vals, depth - 1)
        r = random.random()
        p = B if r < 0.4 else (law[1] if r < 0.6 else random.choice(subs))
        try: return C.evp(p, s)
        except RecursionError: return random.choice(vals)
    for _ in range(N):
        base = {v: random.choice(gens) for v in vs}
        vals = list(base.values()) + gens[:2]
        s = dict(base)
        for _ in range(random.choice([1, 1, 2, 2, 3])):
            v = random.choice(vs)
            r = random.random()
            if r < 0.5: s[v] = enc(vals, random.choice([0, 1, 1, 2]))
            elif r < 0.8: s[v] = term(vals, 2)
            else:
                w = random.choice(vs); s[v] = s[w]
            vals = list(s.values()) + gens[:2]
        if max(size(t) for t in s.values()) > 160: continue
        record(s)

def run_closure(N, seed):
    random.seed(seed)
    subs = []
    def collect(p):
        if isinstance(p, str): return
        subs.append(p); collect(p[0]); collect(p[1])
    collect(law[1])
    pool = [('g', i) for i in range(3)]; seen = set(pool); encs = []
    def add(t):
        if size(t) <= 60 and t not in seen and len(pool) < 4000:
            seen.add(t); pool.append(t)
            if t[0] == 'J': add(t[1]); add(t[2])
    for _ in range(6):
        for _ in range(120):
            p = random.choice(subs)
            s = {v: random.choice(pool) for v in vs}
            if encs and random.random() < 0.5:
                t0, s0 = random.choice(encs)
                for v in vs:
                    if random.random() < 0.5: s[v] = s0[v]
                if random.random() < 0.5: s[random.choice(vs)] = t0
            try: t = C.evp(p, s)
            except RecursionError: continue
            if size(t) > 140: continue
            add(t)
            if p is law[1] or p is B: encs.append((t, s))
            if random.random() < 0.5:
                aa, bb = random.choice(pool), random.choice(pool)
                try: add(C.op(aa, bb))
                except RecursionError: pass
    for _ in range(N):
        s = {v: random.choice(pool) for v in vs}
        r = random.random()
        if r < 0.4 and encs:
            t0, s0 = random.choice(encs)
            for v in vs:
                if random.random() < 0.6: s[v] = s0[v]
            s[random.choice(vs)] = t0
        elif r < 0.6:
            p, q = random.sample(vs, 2); s[p] = s[q]
        if max(size(t) for t in s.values()) > 140: continue
        record(s)

N = int(sys.argv[1]) if len(sys.argv) > 1 else 4000
for sd in (3, 4, 5):
    run_fuzz(N, sd + 100)
    run_closure(N, sd + 200)
    run_critical(N, sd + 300)
print('bad', len(bad))
print('patterns (a,b,c,d,top), -1 = free:')
def nm(i): return 'free' if i < 0 else TAGS[i]
for pat, c in sorted(cnt.items(), key=lambda kv: -kv[1]):
    print('  %-28s x%-7d  %s' % (str(pat), c, ' | '.join(nm(i) for i in pat)))
    tot, s = wit[pat]
    if c < 500:
        print('        witness size %d: %s' % (tot, {k: cf.fm.show(v) if hasattr(cf, 'fm') else str(v) for k, v in s.items()}))
