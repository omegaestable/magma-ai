"""Heavy validation of the candidate 13764 model in gen/_x13764_v6.py."""
import sys, os, random, itertools, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _x13764_lab import *
import _x13764_v9 as V

rules = V.rules
op, opr = mk_op(rules)


def report(tag, fails):
    print('%-34s fails=%d' % (tag, len(fails)))
    for (x, y, z) in fails[:3]:
        print('--- FAIL', tag)
        explain(rules, x, y, z)
    return fails


t0 = time.time()
allf = []

# 1. mixed-size exhaustive: one variable large, two small
S3 = gen_terms(5, 2)
S4 = gen_terms(7, 2)
print('|S3|=%d |S4|=%d' % (len(S3), len(S4)))
for slot in range(3):
    f = []
    for big in S4:
        for a in S3:
            for b in S3:
                x, y, z = (big, a, b) if slot == 0 else ((a, big, b) if slot == 1 else (a, b, big))
                r, _ = chain(op, x, y, z)
                if r != x:
                    f.append((x, y, z))
                    if len(f) >= 5:
                        break
            if len(f) >= 5:
                break
        if len(f) >= 5:
            break
    allf += report('exh slot%d (size<=4 x <=3 x <=3)' % slot, f)
print('  t=%.1fs' % (time.time() - t0))

# 2. exhaustive size<=3 over 3 generators
S3g = gen_terms(5, 3)
f = []
for y in S3g:
    for x in S3g:
        for z in S3g:
            r, _ = chain(op, x, y, z)
            if r != x:
                f.append((x, y, z))
                if len(f) >= 5:
                    break
        if len(f) >= 5:
            break
    if len(f) >= 5:
        break
allf += report('exh size<=3, 3 generators (%d)' % len(S3g), f)
print('  t=%.1fs' % (time.time() - t0))

# 3. deep random, many seeds and depths
f = []
for seed in range(40, 60):
    f += deep(op, 5000, seed, depth=6, ngen=3, limit=3)
allf += report('deep random depth<=6 x100k', f)

# 4. coincidence, many seeds
f = []
for seed in range(100, 130):
    f += coincidence(op, 4000, seed, limit=3)
allf += report('coincidence x120k', f)

# 5. targeted: y built as the encoding shapes the rules recognise
rng = random.Random(7)
pool = gen_terms(3, 3) + [rand_term(rng, 3, 3) for _ in range(60)]


def enc_shapes(rng):
    p = rng.choice(pool); q = rng.choice(pool); r = rng.choice(pool)
    return [
        ('J', ('E', p, ('J', q, r)), r),
        ('J', ('E', p, ('J', q, r)), p),
        ('J', ('J', p, ('J', q, r)), r),
        ('J', ('J', p, q), q),
        ('E', ('J', p, q), r),
        ('E', ('J', p, q), p),
        ('J', ('E', p, q), q),
        ('J', ('J', p, ('J', q, p)), p),
        op(p, op(op(q, p), p)),
        op(op(p, op(op(q, p), p)), p),
        ('E', p, q),
        ('J', ('E', p, ('J', q, p)), p),
    ]


f = []
for _ in range(60000):
    cs = enc_shapes(rng)
    x = rng.choice(cs + pool); y = rng.choice(cs + pool); z = rng.choice(cs + pool)
    try:
        r, _ = chain(op, x, y, z)
    except RecursionError:
        continue
    if r != x:
        f.append((x, y, z))
        if len(f) >= 3:
            break
allf += report('targeted encoding shapes x60k', f)

# 6. nested: use chain outputs as inputs, iterated
f = []
cur = [rng.choice(pool) for _ in range(40)]
for it in range(400):
    nxt = []
    for _ in range(40):
        x = rng.choice(cur); y = rng.choice(cur); z = rng.choice(cur)
        r, (A, B, C, D) = chain(op, x, y, z)
        if r != x:
            f.append((x, y, z))
        nxt += [A, B, C, D, r]
    cur = [t for t in nxt if sz(t) < 400]
    if not cur:
        cur = [rng.choice(pool) for _ in range(40)]
    if len(f) >= 3:
        break
allf += report('closure iteration', f)

print('TOTAL fails = %d   (%.1fs)' % (len(allf), time.time() - t0))
