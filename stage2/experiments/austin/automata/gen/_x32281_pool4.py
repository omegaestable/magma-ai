"""POOL 4 -- the corrected validation pool for law 32281 (session 4, agent C).

Why it exists: `AF` (`op z (op (op x y) y) = J z (op (op x y) y)`) was refuted by an instance
that THREE earlier batteries missed (_x32281_afsf.py 170,410 triples, _x32281_junk.py 32,000,
_x32281_pre.py 60,330).  None of them ever puts the SAME non-generator term in both the payload
slot and the decoder slot of an encoding, nor makes both slots encodings, nor uses the op-BUILT
encoding.  This pool does all three, plus junk arms and a targeted constructive attack on SF.

Model: `_x32281_leanmirror.py`, transcribed line by line from the certificate's `def op`, so this
tests the LEAN definition, not the python rule set.  (sz there is memoised on repr, not id --
id-memoising a tuple is unsound because CPython recycles ids of collected tuples.)

Run:  PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe gen/_x32281_pool4.py
"""
import sys, os, collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _x32281_leanmirror import (G, J, sz, tg, a1, a2, msr, P1, P2, P3, op, enc, openc, rnd)
import random

MAXSZ = 4000  # skip triples whose terms are absurd -- keeps the run inside the recursion limit


def sh(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (sh(t[1]), sh(t[2]))


def rule(u, v):
    """which branch of `op` fires at (u,v): 'F' free, 'R1', 'R2', 'R3'."""
    M = msr(u, v)
    Ju = J(u, v)
    if P1(u, v):
        return 'R1'
    g1 = msr(a1(a1(a2(v))), a2(v)) < M
    b = op(a1(a1(a2(v))), a2(v)) if g1 else Ju
    g2 = msr(b, a2(v)) < M
    c = op(b, a2(v)) if g2 else Ju
    g3 = msr(u, c) < M
    d = op(u, c) if g3 else Ju
    if P2(u, v) and g1 and g2 and g3 and a1(v) == d:
        return 'R2'
    g4 = msr(a1(a1(a2(a2(v)))), a2(a2(v))) < M
    e = op(a1(a1(a2(a2(v)))), a2(a2(v))) if g4 else Ju
    g5 = msr(e, a2(a2(v))) < M
    f = op(e, a2(a2(v))) if g5 else Ju
    g6 = msr(a1(a2(v)), f) < M
    i = op(a1(a2(v)), f) if g6 else Ju
    g7 = msr(u, i) < M
    j = op(u, i) if g7 else Ju
    g8 = msr(u, J(j, f)) < M
    k = op(u, J(j, f)) if g8 else Ju
    g9 = msr(k, a2(v)) < M
    l = op(k, a2(v)) if g9 else Ju
    g10 = msr(l, a2(v)) < M
    m = op(l, a2(v)) if g10 else Ju
    g11 = msr(u, m) < M
    n = op(u, m) if g11 else Ju
    if P3(u, v) and g4 and g5 and g6 and g7 and g8 and g9 and g10 and g11 and a1(v) == n:
        return 'R3'
    return 'F'


CLAIMS = ['law', 'SFg', 'SF', 'AF', 'SFaH', 'SFaG', 'AFJ']
witness = {}


def check(arm, x, y, z, cnt):
    if sz(x) > MAXSZ or sz(y) > MAXSZ or sz(z) > MAXSZ:
        cnt['skip_big'] += 1
        return
    cnt['n'] += 1
    P = op(x, y)
    Q = op(P, y)
    A = op(z, Q)
    S = op(A, y)
    top = op(z, S)
    AJ = J(z, Q)
    SJ = op(AJ, y)

    def fail(name):
        cnt['**%s**' % name] += 1
        witness.setdefault(name, (arm, x, y, z))

    if top != x:
        fail('law')
    if S != J(A, y):
        fail('SFg')
    if SJ != J(AJ, y):
        fail('SF')
    if A != J(z, Q):
        fail('AF')
    # 4. the SFa hypotheses -- `False` is the claim, so a HIT here is a refutation
    if tg(y) == 2 and a1(a1(y)) == AJ:
        fail('SFaH')
    if tg(y) == 2 and a1(a1(y)) == A:
        fail('SFaG')
    # 8. SF's branch-3 residue: is the R2 guard product free when the decoder is `J z Q`?
    D = a2(y)
    C = a1(a1(a2(y)))
    Cc = op(op(C, D), D)
    if op(AJ, Cc) != J(AJ, Cc):
        fail('AFJ')
    # 5. the hk trichotomy at (x,y)
    if P != J(x, y):
        k1 = (tg(y) == 2 and tg(a1(y)) == 2 and a1(a1(y)) == x)
        k2 = rule(z, S) == 'R3'
        cnt['hk:decoded'] += 1
        cnt['hk:a1a1=x' if k1 else 'hk:a1a1!=x'] += 1
        if k2:
            cnt['hk:topR3'] += 1
        if not k1 and not k2:
            cnt['**hk:NEITHER**'] += 1
            witness.setdefault('hk:NEITHER', (arm, x, y, z))
        if k1 and k2:
            cnt['hk:BOTH'] += 1
    cnt['top:' + rule(z, S)] += 1


# ----------------------------------------------------------------------------- the pools
GEN = [G(0), G(1), G(2)]
JUNK = [G(7), G(8), G(9)]
ALL = GEN + JUNK
E1 = [enc(a, b, c) for a in GEN for b in GEN for c in GEN]          # level-1 encodings
NG = [J(G(0), G(1)), J(G(1), J(G(2), G(0)))] + E1[:6]               # non-generator terms


def safe(f, *a):
    try:
        return f(*a)
    except RecursionError:
        return None


ARMS = collections.OrderedDict()

# A. payload slot == decoder slot, both a NON-GENERATOR (the shape that refuted AF)
A_pool = []
for a in NG:
    for c in ALL[:4]:
        A_pool.append((a, enc(a, a, c), a))
        for z in GEN[:2]:
            A_pool.append((a, enc(a, a, c), z))
ARMS['A same-slot(non-gen)'] = A_pool

# B. THE refuting family, generalised: Q0 = enc(z,r,w); x = Q0; y = enc(Q0,Q0,v)
B_pool = []
for z in ALL[:4]:
    for r in ALL[:4]:
        for w in ALL[:3]:
            Q0 = enc(z, r, w)
            for v in ALL[:3]:
                B_pool.append((Q0, enc(Q0, Q0, v), z))
                B_pool.append((Q0, enc(Q0, Q0, v), r))
ARMS['B refuting family'] = B_pool

# C. both slots independently encodings, 2 and 3 levels
C_pool = []
for e1 in E1[:6]:
    for e2 in E1[:6]:
        for c in ALL[:3]:
            C_pool.append((e1, enc(e1, e2, c), e2))
            C_pool.append((e2, enc(e2, e1, c), G(0)))
for e in E1[:4]:
    ee = enc(e, e, G(0))
    for v in ALL[:3]:
        C_pool.append((ee, enc(ee, ee, v), e))
        C_pool.append((e, enc(ee, ee, v), e))
ARMS['C both-slots enc 2/3lvl'] = C_pool

# D. self-referential nestings: enc(E,E,E)
D_pool = []
for e in E1[:8]:
    ee = safe(enc, e, e, e)
    if ee is None:
        continue
    for z in ALL[:4]:
        D_pool.append((e, ee, z))
        D_pool.append((ee, ee, z))
        D_pool.append((e, enc(ee, ee, G(1)), z))
ARMS['D self-referential'] = D_pool

# E. junk generators (appear nowhere else) in each slot in turn
E_pool = []
for jn in JUNK:
    for e in E1[:4]:
        E_pool.append((e, enc(e, e, jn), G(0)))
        E_pool.append((jn, enc(jn, jn, e), G(0)))
        E_pool.append((e, enc(e, e, G(0)), jn))
        E_pool.append((e, enc(jn, jn, G(0)), e))
        ee = enc(e, jn, G(2))
        E_pool.append((ee, enc(ee, ee, jn), jn))
ARMS['E junk slots'] = E_pool

# F. the op-BUILT encoding J (op u (op (op p w) w)) w -- not the free J-built one
F_pool = []
for u in GEN + NG[:4]:
    for p in GEN + NG[:2]:
        for w in ALL[:3]:
            oe = safe(openc, u, p, w)
            if oe is None or sz(oe) > MAXSZ:
                continue
            F_pool.append((p, oe, u))
            F_pool.append((u, oe, p))
            oe2 = safe(openc, oe, oe, w)
            if oe2 is not None and sz(oe2) <= MAXSZ:
                F_pool.append((oe, oe2, u))
ARMS['F op-built enc'] = F_pool

# G. targeted CONSTRUCTIVE attack on SF: plant `J z q0` as the decoder of y, so that if the
#    chain ever produces Q = q0 then A = J z Q is exactly y's key and `op A y` decodes.
G_pool = []
for z in GEN[:3]:
    for q0 in GEN + NG[:4] + E1[:3]:
        K = J(z, q0)
        for p in GEN[:2] + NG[:2]:
            for w in ALL[:3]:
                y = enc(K, p, w)
                for x in [K, z, q0, p, J(z, y)]:
                    G_pool.append((x, y, z))
ARMS['G SF constructive attack'] = G_pool

# H. random control, deep
H_pool = []
rng = random.Random(20260830)
for _ in range(2000):
    H_pool.append((rnd(rng, 4), rnd(rng, 4), rnd(rng, 4)))
for _ in range(2000):
    e = enc(rnd(rng, 2), rnd(rng, 2), rnd(rng, 2))
    H_pool.append((rnd(rng, 2), enc(e, e, rnd(rng, 2)), rnd(rng, 2)))
for _ in range(1500):
    e = enc(rnd(rng, 2), rnd(rng, 2), rnd(rng, 2))
    f = safe(openc, e, e, rnd(rng, 2))
    if f is not None and sz(f) <= MAXSZ:
        H_pool.append((e, f, rnd(rng, 2)))
        H_pool.append((rnd(rng, 2), enc(f, f, rnd(rng, 2)), e))
ARMS['H random control'] = H_pool

# I. THE `AFJ` ATTACK.  Plant `J z u0` as the decoder of an encoding that the (C,D) chain rebuilds:
#      k = J z u0,  Q0 = enc k r w,  D = enc Q0 Q0 v,  y = enc u0 u0 D,  x = u0
#    then Q = u0, so J z Q = k exactly, a1 (a1 (a2 y)) = Q0, op (op Q0 D) D = Q0 = enc k r w, and
#    `op (J z Q) (op (op C D) D)` DECODES.  This is the arm that refutes the lemma `SF`'s two
#    residues would need; `SF` itself survives because the R2 guard EQUATION then fails.
I_pool = []
I_probe = []
for u0 in [G(5), J(G(5), G(6)), enc(G(5), G(6), G(4)), J(J(G(4), G(5)), G(6))]:
    for z in [G(0), J(G(0), G(1)), G(7)]:
        for r in [G(1), J(G(1), G(2)), G(8)]:
            for w in [G(2), G(9)]:
                for v in [G(3), G(4)]:
                    k = J(z, u0)
                    Q0 = safe(enc, k, r, w)
                    if Q0 is None:
                        continue
                    D = enc(Q0, Q0, v)
                    y = enc(u0, u0, D)
                    if sz(y) > MAXSZ:
                        continue
                    I_pool.append((u0, y, z))
                    I_probe.append((u0, y, z, k))
ARMS['I AFJ attack'] = I_pool

# J. standalone `AFJ` (`op (J u v) (op (op C D) D)` free for ARBITRARY u,v,C,D) -- reported
#    separately below, because it is a different quantifier pattern from the per-triple claims.
J_probe = []
for u in [G(0), J(G(0), G(1))]:
    for vv in [G(5), J(G(5), G(6)), enc(G(5), G(6), G(4))]:
        for r in [G(1), J(G(1), G(2))]:
            for w in [G(2), G(9)]:
                for v2 in [G(3), G(4)]:
                    K = J(u, vv)
                    Q0 = enc(K, r, w)
                    Dd = enc(Q0, Q0, v2)
                    J_probe.append((K, Q0, Dd))

# K. the level-2 cell (`gen/_x32281_exctop.py`'s instance) -- the ONE shape where `hk` fails and
#    R3 fires at the top.  Arms A-I never generate it, so without this arm the hk column reads a
#    misleading 100%.  Parameterised by substituting the leaf `g2` for other terms.
def _PA(s):
    s = s.strip()
    if s.startswith('g'):
        return G(int(s[1:]))
    d = 0
    for i, ch in enumerate(s[1:-1], 1):
        if ch == '(':
            d += 1
        elif ch == ')':
            d -= 1
        elif ch == '*' and d == 0:
            return J(_PA(s[1:i]), _PA(s[i + 1:-1]))
    raise ValueError(s)


def _subst(t, leaf, r):
    if t[0] == 'g':
        return r if t == leaf else t
    return J(_subst(t[1], leaf, r), _subst(t[2], leaf, r))


_EXC_X = '(g2*g2)'
_EXC_Y = ('((((g2*g2)*((g2*(g2*g2))*(g2*g2)))*(g2*g2))*(((((g2*g2)*(((((g2*g2)*((g2*(g2*g2))*'
          '(g2*g2)))*(g2*g2))*(g2*g2))*(g2*g2)))*(g2*g2))*(((((g2*g2)*(((((g2*g2)*((g2*(g2*g2))*'
          '(g2*g2)))*(g2*g2))*(g2*g2))*(g2*g2)))*(g2*g2))*(g2*g2))*(g2*g2)))*(g2*g2)))')
K_pool = []
_bx, _by = _PA(_EXC_X), _PA(_EXC_Y)
for t in [G(2), G(0), G(1), G(9), J(G(5), G(6)), J(G(0), J(G(1), G(2)))]:
    xx = _subst(_bx, G(2), t)
    yy = _subst(_by, G(2), t)
    if sz(yy) > MAXSZ:
        continue
    for z in [G(0), G(1), G(7), J(G(0), G(1))]:
        K_pool.append((xx, yy, z))
ARMS['K level-2 cell'] = K_pool

# ----------------------------------------------------------------------------- run
if __name__ == '__main__':
    total = collections.Counter()
    print('%-26s %7s %7s  %s' % ('arm', 'n', 'skip', 'failures'))
    for name, pool in ARMS.items():
        cnt = collections.Counter()
        for (x, y, z) in pool:
            try:
                check(name, x, y, z, cnt)
            except RecursionError:
                cnt['recursion'] += 1
        total.update(cnt)
        bad = ' '.join('%s=%d' % (k, v) for k, v in sorted(cnt.items()) if k.startswith('**'))
        print('%-26s %7d %7d  %s' % (name, cnt['n'], cnt['skip_big'], bad or '-'))
    print()
    print('TOTAL triples checked: %d  (skipped %d, recursion %d)'
          % (total['n'], total['skip_big'], total['recursion']))
    for k in sorted(total):
        if k in ('n', 'skip_big'):
            continue
        print('   %-22s %d' % (k, total[k]))
    print()
    # arm I: is the guard PRODUCT free, and does the guard EQUATION nevertheless fail?
    gp_dec = gp_free = eq_holds = key_hit = 0
    for (x, y, z, k) in I_probe:
        Q = op(op(x, y), y)
        AJ = J(z, Q)
        if AJ == k:
            key_hit += 1
        D = a2(y)
        C = a1(a1(a2(y)))
        Cc = op(op(C, D), D)
        g = op(AJ, Cc)
        if g == J(AJ, Cc):
            gp_free += 1
        else:
            gp_dec += 1
        if a1(y) == g:
            eq_holds += 1
    print('arm I probe (%d): J z Q hits the planted key %d, guard PRODUCT decoded %d / free %d, '
          'guard EQUATION `a1 y = op A Cc` holds %d'
          % (len(I_probe), key_hit, gp_dec, gp_free, eq_holds))
    # standalone AFJ
    sa_dec = 0
    for (K, C, D) in J_probe:
        Cc = op(op(C, D), D)
        if op(K, Cc) != J(K, Cc):
            sa_dec += 1
    print('standalone AFJ probe (%d): `op (J u v) (op (op C D) D)` DECODED %d times'
          % (len(J_probe), sa_dec))
    print()
    for k, (arm, x, y, z) in witness.items():
        print('%s  first witness (arm %s):' % (k, arm))
        print('   x = %s' % sh(x)[:220])
        print('   y = %s' % sh(y)[:220])
        print('   z = %s' % sh(z)[:220])
