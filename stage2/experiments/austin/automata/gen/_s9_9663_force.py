# -*- coding: utf-8 -*-
"""Session 9 forcing suite for the 9663 four-constructor carrier (lab5, FEAT-parameterised).

Ported verbatim from `_x9663_force4.py` (rung 12: a new carrier inherits the old one's adversary)
and extended with:
  * rung 7  -- vary the junk variable: a large term over FRESH generators in the z slot
  * rung 4  -- the both-decoded census (two chain products firing DEC at once)
  * rung 11 -- the positive control is printed per rule; a 0 means the rule was untested
  * a NEW forcing target `NU`: construct chains where the root's `a1 C = A` is a DECODE
    (so `A` is a proper subterm, the case that could make `a1 v != u` fail at the root).

usage:  python _s9_9663_force.py f:nu,v34
"""
import sys, os, random, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _s9_9663_lab5 as L

for a in sys.argv[1:]:
    if a.startswith('f:'): L.FEAT = set(x for x in a[2:].split(',') if x)
print('=== FEAT={%s} ===' % ','.join(sorted(L.FEAT)))

op, chain, prof, sz, show = L.op, L.chain, L.prof, L.sz, L.show
tg, a1, a2, G, J, E, F, PROF = L.tg, L.a1, L.a2, L.G, L.J, L.E, L.F, L.PROF


def rule(u, v):
    op(u, v)
    return PROF.get((u, v)) or '.'


def rt(rng, d, gens=3, base=0):
    if d <= 0 or rng.random() < .3: return G(base + rng.randrange(gens))
    return (rng.choice(('J', 'E', 'F')), rt(rng, d - 1, gens, base), rt(rng, d - 1, gens, base))


rng = random.Random(4242)
pool = [rt(rng, 3) for _ in range(120)] + [G(0), G(1), G(2)]
# rung 7: junk terms over FRESH generators (100..102), deliberately large
junkbig = [rt(rng, 6, 3, 100) for _ in range(60)]

fired = collections.Counter(); bad = collections.Counter(); wit = {}
bothdec = collections.Counter()


def trial(tag, x, y, z):
    try:
        r = chain(x, y, z)[4]; pr = prof(x, y, z)
    except RecursionError:
        return
    for k in pr: fired[(tag, k)] += 1
    fired[(tag, 'N')] += 1
    if pr.count('D') >= 2: bothdec[tag] += 1
    if r != x:
        bad[tag] += 1
        wit.setdefault(tag, (x, y, z, r))


def pickz(rng, big):
    return rng.choice(junkbig) if big else rng.choice(pool)


for big in (False, True):
    sfx = '+bigjunk' if big else ''
    # --- force DEC at the root: build y,x so the chain's Q really is an F container
    for _ in range(4000):
        x = rng.choice(pool); y = rng.choice(pool); z = pickz(rng, big)
        P = op(x, y)
        if rule(x, P) != 'F': continue
        trial('DEC' + sfx, x, y, z)
    # --- force R2: y an encoding of an encoding by x (the descent shape)
    for _ in range(6000):
        x = rng.choice(pool); p = rng.choice(pool); j = rng.choice(pool)
        try:
            p1 = L.enc(x, p, j); y = L.enc(x, p1, j)
        except RecursionError: continue
        if op(x, y) != p1: continue
        trial('R2' + sfx, x, y, pickz(rng, big))
    # --- force TAGF: v is genuinely op(u,w)
    for _ in range(4000):
        u = rng.choice(pool); w = rng.choice(pool)
        v = op(u, w)
        if rule(u, v) != 'F': continue
        trial('TAGF' + sfx, v, u, pickz(rng, big))
        trial('TAGF2' + sfx, rng.choice(pool), v, pickz(rng, big))
    # --- force TAGE
    for _ in range(4000):
        u = rng.choice(pool); v = rng.choice(pool)
        if tg(v) == 1 or rule(u, v) != 'E': continue
        trial('TAGE' + sfx, u, op(u, v), pickz(rng, big))
    # --- NEW: force the root's A slot to be a DECODE, i.e. a1 C is a proper subterm.
    #     This is the case in which the new `a1 v != u` guard could fail AT THE ROOT.
    #     CONSTRUCTED, not sampled: y = enc(z, w, j) makes op z y = w by construction.
    n = 0
    for _ in range(30000):
        if n >= 4000: break
        z = pickz(rng, big); w = rng.choice(pool); j = rng.choice(pool)
        try:
            y = L.enc(z, w, j)
        except RecursionError: continue
        if rule(z, y) not in ('D', 'R'): continue
        n += 1
        trial('Adec' + sfx, rng.choice(pool), y, z)
    # --- NEW: chains where A == y exactly (the exact `a1 v = u` collision at the root)
    for _ in range(30000):
        y = rng.choice(pool + junkbig); z = rng.choice(pool + junkbig)
        try:
            if op(z, y) != y: continue
        except RecursionError: continue
        trial('Aeqy' + sfx, rng.choice(pool), y, z)
    # --- NEW: y itself an encoding BY z (H3 aimed at the z slot rather than the x slot)
    for _ in range(4000):
        z = pickz(rng, big); w = rng.choice(pool); j = rng.choice(pool)
        try:
            y = L.enc(z, w, j)
        except RecursionError: continue
        trial('H3z' + sfx, rng.choice(pool), y, z)
    # --- NEW: y an encoding by x AND z an encoding by x (both slots loaded)
    for _ in range(4000):
        x = rng.choice(pool); w = rng.choice(pool); j = rng.choice(pool)
        try:
            y = L.enc(j, w, x); z = L.enc(rng.choice(pool), rng.choice(pool), x)
        except RecursionError: continue
        trial('H3xz' + sfx, x, y, z)

print('=== forcing suite: did each rule actually FIRE?  (rung 11 positive control) ===')
for tag in sorted(set(k[0] for k in fired)):
    n = fired[(tag, 'N')]
    if not n:
        print('  %-14s NO INSTANCES CONSTRUCTED -- suite tests nothing' % tag); continue
    print('  %-14s trials=%-6d BAD=%-4d bothdec=%-5d  fired: D=%d R=%d F=%d E=%d free=%d'
          % (tag, n, bad[tag], bothdec[tag], fired[(tag, 'D')], fired[(tag, 'R')],
             fired[(tag, 'F')], fired[(tag, 'E')], fired[(tag, '.')]))
for tag, (x, y, z, r) in wit.items():
    print('  BAD[%s] x=%s' % (tag, show(x)[:90])); print('          y=%s' % show(y)[:90])
    print('          z=%s -> %s' % (show(z)[:60], show(r)[:70]))

print('=== descent per-rule census (saturation check, rung 6/10) ===')
for lv in (0, 1, 2, 3, 4):
    for bj in (False, True):
        g = L.g_desc(lv, 7, bj, 3); c = collections.Counter(); n = 0; b = 0; bd = 0
        for _ in range(400):
            x, y, z = next(g)
            try:
                pr = prof(x, y, z); r = chain(x, y, z)[4]
            except RecursionError: continue
            n += 1; c[pr] += 1
            if pr.count('D') >= 2: bd += 1
            if r != x: b += 1
        print('  lv=%d bj=%-5s n=%d BAD=%d bothdec=%d distinct=%d  %s'
              % (lv, bj, n, b, bd, len(c), ' '.join('%s:%d' % (','.join(k), m) for k, m in c.most_common(3))))
