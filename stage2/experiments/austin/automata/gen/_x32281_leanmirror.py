"""Lean-exact mirror of gen/w135e.lean's `def op`, transcribed line by line from the Lean source.
Checks the law, AF and SF on random terms.  This is the "build the Lean-exact mirror, do not eyeball
the transcription" rail: everything else validated the PYTHON rule set, not the Lean definition."""
import sys, random
sys.setrecursionlimit(100000)

# M ::= ('g', n) | ('J', a, b)
def G(n): return ('g', n)
def J(a, b): return ('J', a, b)

_sz = {}
def sz(t):
    k = repr(t)
    r = _sz.get(k)
    if r is not None: return r
    r = 1 if t[0] == 'g' else sz(t[1]) + sz(t[2]) + 1
    _sz[k] = r
    return r

def tg(t): return 1 if t[0] == 'g' else 2
def a1(t): return t[1] if t[0] == 'J' else t
def a2(t): return t[2] if t[0] == 'J' else t
def msr(u, v):
    m = max(sz(u), sz(v)); return m * m + sz(u) + sz(v)

def P1(u, v):
    return (tg(v) == 2 and tg(a1(v)) == 2 and u == a1(a1(v)) and tg(a2(a1(v))) == 2
            and tg(a1(a2(a1(v)))) == 2 and a2(a1(a2(a1(v)))) == a2(a2(a1(v)))
            and a2(a1(a2(a1(v)))) == a2(v))
def P2(u, v): return tg(v) == 2 and tg(a2(v)) == 2 and tg(a1(a2(v))) == 2
def P3(u, v): return tg(v) == 2 and tg(a2(v)) == 2 and tg(a2(a2(v))) == 2 and tg(a1(a2(a2(v)))) == 2

_op = {}
def op(u, v):
    key = (repr(u), repr(v))
    r = _op.get(key)
    if r is not None: return r
    M = msr(u, v); Ju = J(u, v)
    g1 = msr(a1(a1(a2(v))), a2(v)) < M
    b = op(a1(a1(a2(v))), a2(v)) if g1 else Ju
    g2 = msr(b, a2(v)) < M
    c = op(b, a2(v)) if g2 else Ju
    g3 = msr(u, c) < M
    d = op(u, c) if g3 else Ju
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
    if P1(u, v): r = a1(a1(a2(a1(v))))
    elif P2(u, v) and g1 and g2 and g3 and a1(v) == d: r = a1(a1(a2(v)))
    elif P3(u, v) and g4 and g5 and g6 and g7 and g8 and g9 and g10 and g11 and a1(v) == n: r = k
    else: r = Ju
    _op[key] = r
    return r

def rnd(rng, d):
    if d <= 0 or rng.random() < 0.3: return G(rng.randrange(4))
    return J(rnd(rng, d - 1), rnd(rng, d - 1))

def enc(u, p, w):      # the free R1 encoding: v = J (J u (J (J p w) w)) w
    return J(J(u, J(J(p, w), w)), w)

def openc(u, p, w):    # the op-built encoding the R2/R3 guards test
    return J(op(u, op(op(p, w), w)), w)

def run(seed, n, depth, mk):
    rng = random.Random(seed)
    bad = {'law': 0, 'AF': 0, 'SF': 0}
    for _ in range(n):
        x, y, z = mk(rng, depth)
        Q = op(op(x, y), y); A = op(z, Q); S = op(A, y)
        if A != J(z, Q): bad['AF'] += 1
        if S != J(A, y): bad['SF'] += 1
        if op(z, S) != x: bad['law'] += 1
    return bad

if __name__ == '__main__':
    tot = {'law': 0, 'AF': 0, 'SF': 0}; N = 0
    # arm 1: plain random terms
    for s in (1, 2, 3):
        r = run(s, 400, 4, lambda rng, d: (rnd(rng, d), rnd(rng, d), rnd(rng, d)))
        for k in tot: tot[k] += r[k]
        N += 400
    # arm 2: y is a genuine free encoding, so decodes really happen
    def mk_enc(rng, d):
        x = rnd(rng, d); w = rnd(rng, d); u = rnd(rng, d)
        return (x, enc(u, x, w), u)
    for s in (11, 22, 33):
        r = run(s, 400, 3, mk_enc); [tot.__setitem__(k, tot[k] + r[k]) for k in tot]; N += 400
    # arm 3: y is an op-built (level-2) encoding -- the cell that killed the 2-rule set
    def mk_enc2(rng, d):
        x = rnd(rng, d); w = rnd(rng, d); u = rnd(rng, d)
        inner = enc(u, x, w)
        return (x, opencsafe(u, x, inner), u)
    def opencsafe(u, p, w):
        try: return openc(u, p, w)
        except RecursionError: return enc(u, p, w)
    for s in (111, 222):
        r = run(s, 150, 2, mk_enc2); [tot.__setitem__(k, tot[k] + r[k]) for k in tot]; N += 150
    print('LEAN-EXACT MIRROR:', N, 'triples ->', tot)
