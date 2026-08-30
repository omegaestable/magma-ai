"""Corrected forcing suite for the 4-rule 9663 carrier + descent saturation census.

To force rule k, construct the product inside rule k's OWN guard as an encoding, and ASSERT IN THE
CENSUS THAT RULE k FIRED -- a suite that never fires rule k has tested nothing about it.
Also: report the per-rule census of the descent at each level, to detect saturation (a level whose
first rule fires everywhere is measuring nothing deeper).
"""
import sys, os, random, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _x9663_lab4 as L
from _x9663_lab4 import op, chain, prof, sz, show, tg, a1, a2, G, J, E, F, PROF

def rule(u, v):
    op(u, v)
    return PROF.get((u, v)) or '.'

def rt(rng, d, gens=3):
    if d <= 0 or rng.random() < .3: return G(rng.randrange(gens))
    return (rng.choice(('J', 'E', 'F')), rt(rng, d - 1, gens), rt(rng, d - 1, gens))

rng = random.Random(4242)
pool = [rt(rng, 3) for _ in range(120)] + [G(0), G(1), G(2)]

fired = collections.Counter(); bad = collections.Counter(); wit = {}
def trial(tag, x, y, z):
    try:
        r = chain(x, y, z)[4]; pr = prof(x, y, z)
    except RecursionError:
        return
    for k in pr: fired[(tag, k)] += 1
    fired[(tag, 'N')] += 1
    if r != x:
        bad[tag] += 1
        wit.setdefault(tag, (x, y, z, r))

# --- force DEC at the root: build y,x so the chain's Q really is an F container
for _ in range(4000):
    x = rng.choice(pool); y = rng.choice(pool); z = rng.choice(pool)
    P = op(x, y)
    if rule(x, P) != 'F': continue          # Q must be an F node = DEC's own guard
    trial('DEC', x, y, z)
# --- force R2: y an encoding of an encoding by x (the descent shape), asserted by R firing
for _ in range(6000):
    x = rng.choice(pool); p = rng.choice(pool); j = rng.choice(pool)
    try:
        p1 = L.enc(x, p, j); y = L.enc(x, p1, j)
    except RecursionError: continue
    if op(x, y) != p1: continue
    trial('R2', x, y, rng.choice(pool))
# --- force TAGF: v is genuinely op(u,w)
for _ in range(4000):
    u = rng.choice(pool); w = rng.choice(pool)
    v = op(u, w)
    if rule(u, v) != 'F': continue
    trial('TAGF', v, u, rng.choice(pool))
    trial('TAGF2', rng.choice(pool), v, rng.choice(pool))
# --- force TAGE
for _ in range(4000):
    u = rng.choice(pool); v = rng.choice(pool)
    if tg(v) == 1 or rule(u, v) != 'E': continue
    trial('TAGE', u, op(u, v), rng.choice(pool))

print('=== forcing suite: did each rule actually FIRE? ===')
for tag in ('DEC', 'R2', 'TAGF', 'TAGF2', 'TAGE'):
    n = fired[(tag, 'N')]
    if not n: print('  %-6s NO INSTANCES CONSTRUCTED -- suite tests nothing' % tag); continue
    print('  %-6s trials=%-5d BAD=%-4d   fired: D=%d R=%d F=%d E=%d free=%d'
          % (tag, n, bad[tag], fired[(tag, 'D')], fired[(tag, 'R')], fired[(tag, 'F')],
             fired[(tag, 'E')], fired[(tag, '.')]))
    if fired[(tag, 'D')] == 0 and tag == 'DEC': print('     ^^ DEC never fired: VACUOUS SUITE')
    if fired[(tag, 'R')] == 0 and tag == 'R2': print('     ^^ R2 never fired: VACUOUS SUITE')
for tag, (x, y, z, r) in wit.items():
    print('  BAD[%s] x=%s' % (tag, show(x)[:90])); print('          y=%s' % show(y)[:90])
    print('          z=%s -> %s' % (show(z)[:60], show(r)[:70]))

print('=== descent per-rule census (saturation check) ===')
for lv in (0, 1, 2, 3, 4):
    g = L.g_desc(lv, 7, False, 3); c = collections.Counter(); n = 0; b = 0
    for _ in range(400):
        x, y, z = next(g)
        try:
            pr = prof(x, y, z); r = chain(x, y, z)[4]
        except RecursionError: continue
        n += 1; c[pr] += 1
        if r != x: b += 1
    print('  lv=%d n=%d BAD=%d  distinct profiles=%d' % (lv, n, b, len(c)))
    for k, m in c.most_common(4):
        print('       %-18s %d' % (','.join(k), m))
