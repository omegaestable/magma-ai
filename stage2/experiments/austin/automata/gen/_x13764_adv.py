"""Adversarial, structure-driven tests for the 13764 candidate model.

Built from the hand case analysis: every branch of the A-step and every
sub-case of the C-step, instantiated with random fillers.  This is what found
the hole the 400k random/exhaustive tests missed.
"""
import sys, os, random, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _x13764_lab import *

MOD = os.environ.get('X13764_MOD', '_x13764_v9')
V = __import__(MOD)
op, opr = mk_op(V.rules)

g = lambda n: ('g', n)
Jc = lambda a, b: ('J', a, b)
Ec = lambda a, b: ('E', a, b)

rng = random.Random(4242)
POOL = gen_terms(5, 2) + [rand_term(rng, 3, 3) for _ in range(80)]
P = lambda: rng.choice(POOL)

fails = []


def test(name, x, y, z):
    try:
        r, steps = chain_r(opr, x, y, z)
    except RecursionError:
        return
    if r != x:
        fails.append((name, x, y, z))


def y_caseIV():
    """the four shapes with a1(a1 y) = a2 y = z  (A = B = z)"""
    z = P()
    R = Jc(P(), z)                      # a2 R = z
    out = []
    out.append(('IVa', Jc(Ec(z, R), z)))                       # alpha: tg(a1 y)=3
    out.append(('IVb', Jc(Jc(z, Jc(P(), z)), z)))              # beta
    # delta: tg y=2, a2 y=z, a1(a1 y)=z, a2(a1 y)=a2 z, a1(a1 z)=a2 z
    zz = None
    t = P()
    zd = Jc(Jc(t, t), t)                                        # a1(a1 zd)=t=a2 zd
    out.append(('IVd', Jc(Jc(zd, ('g', 0)), zd)))               # a2(a1 y)=g0 ; needs =a2 zd=t
    out.append(('IVd2', Jc(Jc(zd, t), zd)))                     # a2(a1 y)=t=a2 zd  OK
    out.append(('IVz', Ec(Jc(z, P()), z)))                      # zeta: tg y=3
    return out


def z_decodeshapes(x):
    """z such that op(x, z) decodes (all of c3), plus c2 and c4 shapes"""
    out = []
    q = Jc(P(), x)                                  # a2 q = x
    out.append(Jc(Ec(P(), q), x))                   # W1 at (x,z)
    out.append(Jc(Jc(P(), Jc(P(), x)), x))          # W4 at (x,z)
    out.append(Ec(Jc(P(), P()), x))                 # W3 at (x,z)
    if a1(a1(x)) == a2(x):
        out.append(Jc(Jc(P(), a2(x)), x))           # W5 at (x,z)
        out.append(Jc(a1(a1(a2(x))), x))            # W6 at (x,z)
    out.append(Jc(Jc(P(), P()), P()))               # c2: W2 shape -> E x z ... needs a2(a1 z)=a2 z
    t = P()
    out.append(Jc(Jc(P(), t), t))                   # c2 proper
    return out


# ---- case IV crossed with every C sub-case
for rep in range(4000):
    for nm, y in y_caseIV():
        z = a2(y)
        if a1(a1(y)) != z:
            continue
        for x in [P(), y, z] + ([a2(z)] if tg(z) != 1 else []):
            test(nm + '/generic-x', x, y, z)
# build z first, then y around it, so that op(x,z) decodes
for rep in range(4000):
    x = P()
    for z in z_decodeshapes(x):
        R = Jc(P(), z)
        ys = [Jc(Ec(z, R), z), Jc(Jc(z, Jc(P(), z)), z), Ec(Jc(z, P()), z)]
        for y in ys:
            if a1(a1(y)) != a2(y):
                continue
            test('IV/c3', x, y, z)

# ---- generic branches with adversarial x
for rep in range(6000):
    z = P(); y = P(); x = P()
    test('plain', x, y, z)
    # x chosen to be y, or an encoding
    test('x=y', y, y, z)
    B = op(op(z, y), y)
    test('x=a2B', a2(B), y, z)
    test('x=B', B, y, z)
    test('x=a1B', a1(B), y, z)
    test('x=a1a1B', a1(a1(B)), y, z)

# ---- y built as an encoding of something, z arbitrary
for rep in range(6000):
    p = P(); q = P(); r = P()
    ys = [Jc(Ec(p, Jc(q, r)), r), Jc(Jc(p, Jc(q, r)), r), Ec(Jc(p, q), r),
          Jc(Jc(p, q), q), Jc(Ec(p, q), q), Jc(p, q)]
    for y in ys:
        for z in [P(), a2(y), a1(a1(y)), r]:
            for x in [P(), y, a2(y)]:
                test('encY', x, y, z)

print('MOD=%s   adversarial fails = %d' % (MOD, len(fails)))
seen = set()
for (nm, x, y, z) in fails:
    if nm in seen:
        continue
    seen.add(nm)
    print('--- FAIL', nm)
    explain(V.rules, x, y, z)
