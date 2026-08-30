"""Scenario / provenance fuzz for law 38316.

The generic fuzzers set a *variable* to a pool term; the coincidences this law needs are of the shape
"x is the value of the subpattern c under an assignment that shares y and z with the instance".
So: build values of every subpattern together with the assignment that produced them, then form the
instance from that same assignment with one variable overwritten by the value.

Reports the case table (which chain product decoded, and by which rule) and any law failure.

usage: _x38316_scen.py [N] [seed] [--rules keep|all]
"""
import sys, os, random
from collections import Counter
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, leangen
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 38316
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = ('x', leangen.dual_pat(orig[1]))
src = open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chkrep38316.py',
           encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); ALL = ns['rules']

def load_rules(which):
    if which == 'all':
        return ALL
    if ',' in which:
        tags = which.split(',')
        return [r for r in ALL if r[2] in tags]
    import json
    keep = json.load(open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/_x38316_keep.json'))
    return [r for r in ALL if r[2] in keep]

RULES = load_rules(sys.argv[3] if len(sys.argv) > 3 else 'all')
TAGS = [r[2] for r in RULES]
C = cf.Closed(law, RULES)
print('rules:', TAGS)

SUBS = []
def collect(p):
    if isinstance(p, str): return
    SUBS.append(p); collect(p[0]); collect(p[1])
collect(law[1])

def which(u, v):
    for i, (conds, xx, tag) in enumerate(C.rules):
        if C.check(conds, u, v):
            r = C.ev(xx, u, v)
            if r is not None:
                return i
    return -1

def chain(x, y, z):
    a = C.op(z, x); b = C.op(y, a); c = C.op(b, y); d = C.op(x, c); top = C.op(y, d)
    return (which(z, x), which(y, a), which(b, y), which(x, c), which(y, d)), top

cnt = Counter(); wit = {}; bad = []
def record(s):
    try:
        pat, top = chain(s['x'], s['y'], s['z'])
    except RecursionError:
        return
    cnt[pat] += 1
    tot = sum(size(t) for t in s.values())
    if pat not in wit or tot < wit[pat][0]:
        wit[pat] = (tot, dict(s))
    if top != s['x']:
        bad.append(dict(s))

def sh(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (sh(t[1]), sh(t[2]))

N = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
random.seed(int(sys.argv[2]) if len(sys.argv) > 2 else 1)
GENS = [('g', i) for i in range(4)]
pool = list(GENS)

for it in range(N):
    # a random base assignment over the pool
    s0 = {v: random.choice(pool) for v in ('x', 'y', 'z')}
    if random.random() < 0.3:
        p, q = random.sample(['x', 'y', 'z'], 2); s0[p] = s0[q]
    # overwrite 1..2 variables with values of subpatterns of the SAME assignment (provenance coincidence)
    s = dict(s0)
    for _ in range(random.choice([1, 1, 2])):
        p = random.choice(SUBS)
        v = random.choice(['x', 'y', 'z'])
        s1 = dict(s)
        # optionally permute which pool term plays which role inside the subpattern
        if random.random() < 0.5:
            s1 = {k: random.choice(pool + list(s.values())) for k in ('x', 'y', 'z')}
            for k in random.sample(['x', 'y', 'z'], random.randint(1, 3)):
                s1[k] = s[k]
        try:
            t = C.evp(p, s1)
        except RecursionError:
            continue
        if size(t) > 200:
            continue
        s[v] = t
    if max(size(t) for t in s.values()) > 200:
        continue
    record(s)
    if len(pool) < 300 and random.random() < 0.2:
        for t in s.values():
            if size(t) <= 40 and t not in pool:
                pool.append(t)

print('instances %d  law failures %d' % (sum(cnt.values()), len(bad)))
for b in bad[:5]:
    print('  BAD x=%s y=%s z=%s' % (sh(b['x']), sh(b['y']), sh(b['z'])))
print('patterns (a,b,c,d,top):')
for pat, c in sorted(cnt.items(), key=lambda kv: -kv[1]):
    tot, s = wit[pat]
    print('  %-24s x%-6d %-46s  wit sz %d' % (str(pat), c,
          '|'.join((TAGS[i] if i >= 0 else 'free') for i in pat), tot))
    if c < 20000:
        print('        x=%s\n        y=%s\n        z=%s' % (sh(s['x']), sh(s['y']), sh(s['z'])))
