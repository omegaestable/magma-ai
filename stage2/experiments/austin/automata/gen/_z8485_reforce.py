"""_z8485_reforce.py -- RE-FORCING the 8485 variant-f model, against the Lean definition itself.

Session 8's warning (rail 52): every inherited *minimised* model it re-checked was false.  Variant f
is a hand-built 4-rule replacement for the 83 extracted rules, and the Lean file `gen/f8485r.lean`
was produced by a HAND EDIT of variant a's emission, never by `leangen.emit` on variant f.  So the
object that must be re-forced is the Lean `op`, not the Python rule engine.

Stages
  0  cross-check the independent Lean transcription against closedform.Closed(law, variant f)
  1  exhaustive law check over the Lean op    (size<=9 / 1 gen, size<=7 / 2 gens, size<=5 / 3 gens)
  2  junk-variable variation (rail 52a): z is unconstrained by R1, so blow it up
  3  forced firing: construct, per rule and per chain product, an instance from that rule's own
     precondition (rail 52b)
  4  the blocker cell: force  P = op z x  to decode by R2/R3/R4 rather than R1, which is the one
     cell session 2 could not prove and only ever saw by accident
  5  level-k descent (nested encodings) with large junk

Usage: python -u gen/_z8485_reforce.py [stages]      e.g. `python -u gen/_z8485_reforce.py 0 1 4`
"""
import sys, os, time, random, itertools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
sys.setrecursionlimit(200000)

from _z8485_lean import LeanOp, show, sz, tg, a1, a2, msr, P1, P2, P3, P4

G = lambda i: ('g', i)
J = lambda a, b: ('J', a, b)

def terms_upto(maxsize, gens):
    by = {1: [G(i) for i in range(gens)]}
    for n in range(3, maxsize + 1, 2):
        by[n] = []
        for a in range(1, n - 1, 2):
            b = n - 1 - a
            if b in by:
                for s in by[a]:
                    for t in by[b]:
                        by[n].append(J(s, t))
    out = []
    for n in sorted(by): out += by[n]
    return out

def rand_term(d, ng=3, rng=random):
    if d <= 0 or rng.random() < 0.3: return G(rng.randrange(ng))
    return J(rand_term(d - 1, ng, rng), rand_term(d - 1, ng, rng))

FAILS = []
def check(C, x, y, z, tag):
    try:
        r = C.law_lhs(x, y, z)
    except RecursionError:
        FAILS.append((tag, 'recursion', x, y, z)); return False
    if r != x:
        FAILS.append((tag, r, x, y, z)); return False
    return True

def report(tag, n, t0, extra=''):
    bad = len([f for f in FAILS if f[0] == tag])
    print('  %-26s tested %-8d BAD %-5d %6.1fs %s' % (tag, n, bad, time.time() - t0, extra), flush=True)
    return bad

# --------------------------------------------------------------------------- stage 0
def stage0():
    print('[0] cross-check the independent transcription vs closedform.Closed(variant f)', flush=True)
    import closedform as cf
    from freemodel import normalise, catalog
    from laws import parse_eq
    cat = catalog(); law = normalise(parse_eq(cat[8485]))
    src = open(os.path.join(HERE, 'chk8485.py'), encoding='utf-8').read().split('C = cf.Closed')[0]
    ns = {}; exec(src, ns)
    sys.argv = ['x', 'f']
    mn = {}
    exec(open(os.path.join(HERE, '_x8485_min.py'), encoding='utf-8').read().split("if __name__")[0], mn)
    R = mn['VARIANTS']['f']
    CC = cf.Closed(law, R)
    C = LeanOp()
    rng = random.Random(99)
    pool = terms_upto(7, 2)
    n = dis = 0
    t0 = time.time()
    # both random pairs and every small pair
    pairs = [(u, v) for u in pool[:60] for v in pool[:60]]
    pairs += [(rand_term(rng.randrange(1, 5), 3, rng), rand_term(rng.randrange(1, 6), 3, rng))
              for _ in range(20000)]
    for u, v in pairs:
        n += 1
        try:
            b = CC.op(u, v)
        except RecursionError:
            continue
        a = C.op(u, v)
        if a != b:
            dis += 1
            if dis <= 3:
                print('    DISAGREE u=%s v=%s  lean=%s closed=%s' % (show(u), show(v), show(a), show(b)), flush=True)
    print('  compared %d pairs, disagreements %d, cycles in Closed %d  %.1fs'
          % (n, dis, CC.cycles, time.time() - t0), flush=True)
    return dis

# --------------------------------------------------------------------------- stage 1
def stage1():
    print('[1] exhaustive law check on the LEAN op', flush=True)
    tot = 0
    for ms, g in ((9, 1), (7, 2), (5, 3), (5, 2)):
        C = LeanOp(); t0 = time.time(); pool = terms_upto(ms, g); n = 0
        for x, y, z in itertools.product(pool, repeat=3):
            n += 1; check(C, x, y, z, 'exh%d/%d' % (ms, g))
        tot += report('exh%d/%d' % (ms, g), n, t0, 'pool %d, branch counts %s' % (len(pool), C.counts))
    return tot

# --------------------------------------------------------------------------- stage 2
def stage2(N=40000):
    """rail 52a: z is the variable NO rule constrains in the free cell.  Blow it up."""
    print('[2] junk-variable variation: large z (and large y), small/structured x', flush=True)
    tot = 0
    for seed in (11, 23, 37):
        rng = random.Random(seed)
        C = LeanOp(); t0 = time.time(); n = 0
        for _ in range(N):
            # x small-ish so the free cell is reachable, z BIG
            x = rand_term(rng.randrange(0, 4), 3, rng)
            y = rand_term(rng.randrange(0, 4), 3, rng)
            z = rand_term(rng.randrange(4, 8), 4, rng)
            if sz(z) > 400: continue
            n += 1; check(C, x, y, z, 'junkz s%d' % seed)
        tot += report('junkz s%d' % seed, n, t0, 'branches %s' % C.counts)
    for seed in (11, 23):
        rng = random.Random(seed)
        C = LeanOp(); t0 = time.time(); n = 0
        for _ in range(N):
            x = rand_term(rng.randrange(0, 4), 3, rng)
            y = rand_term(rng.randrange(4, 7), 4, rng)
            z = rand_term(rng.randrange(0, 4), 3, rng)
            if sz(y) > 400: continue
            n += 1; check(C, x, y, z, 'junky s%d' % seed)
        tot += report('junky s%d' % seed, n, t0, 'branches %s' % C.counts)
    return tot

# --------------------------------------------------------------------------- encodings
def enc(C, u, w, j):
    """enc(u,w,j) with  op(u, enc(u,w,j)) = w   -- the law with y=u, x=w, z=j"""
    return C.op(w, C.op(C.op(C.op(j, w), u), u))

# --------------------------------------------------------------------------- stage 3
def stage3(N=6000):
    """rail 52b: force each rule to fire at each chain product, constructed from its own precondition."""
    print('[3] forced firing per rule per chain product (constructed, not sampled)', flush=True)
    tot = 0
    got = {}
    for seed in (5, 19, 41):
        rng = random.Random(seed)
        C = LeanOp(); t0 = time.time(); n = 0
        for _ in range(N):
            mode = rng.randrange(4)
            u0 = rand_term(rng.randrange(0, 3), 3, rng)
            w = rand_term(rng.randrange(0, 3), 3, rng)
            j = rand_term(rng.randrange(0, 4), 4, rng)
            if mode == 0:      # make P = op z x decode: x := enc(z, w, j)
                z = u0; x = enc(C, z, w, j); y = rand_term(rng.randrange(0, 3), 3, rng)
            elif mode == 1:    # make Q = op P y decode: choose x,z so P is what enc wants
                y = u0; z = rand_term(rng.randrange(0, 3), 3, rng)
                x = rand_term(rng.randrange(0, 3), 3, rng)
                P = C.op(z, x)
                # we cannot pick P, so instead force the pair (P,y) via a fresh chain: skip if free
                y = u0; pass
            elif mode == 2:    # nested: x is a 2-level encoding
                z = u0
                x = enc(C, z, enc(C, z, w, j), rand_term(2, 3, rng))
                y = rand_term(rng.randrange(0, 3), 3, rng)
            else:              # y is an encoding too (drives R3/R4 paths)
                z = u0; x = enc(C, z, w, j)
                y = enc(C, rand_term(1, 3, rng), rand_term(1, 3, rng), rand_term(2, 3, rng))
            if max(sz(x), sz(y), sz(z)) > 600: continue
            n += 1
            if check(C, x, y, z, 'force s%d' % seed):
                cl, _ = C.cells(x, y, z)
                got[cl] = got.get(cl, 0) + 1
        tot += report('force s%d' % seed, n, t0)
    print('  cells seen:', dict(sorted(got.items(), key=lambda kv: -kv[1])[:14]), flush=True)
    return tot

# --------------------------------------------------------------------------- stage 4  (THE BLOCKER)
def stage4(N=4000):
    """Force  P = op z x  to decode by R2 / R3 / R4 rather than R1.

    R2 at (z,x) needs:  x = J X1 X2, X1 = J A B, B = J Cc z0,  and
                        op(op(op(z0, X1), z), z) = X2.
    So pick X1 and z0 freely, set X2 := that chain, x := J X1 X2.  Then op z x = X1 by R2 -- unless
    R1 fires first, which we detect and record.

    R3 at (z,x) needs:  z = J .. with tg(a2 z)=tg(a2(a2 z))=2, z0 := a1(a2(a2 z)),
                        op(op(op(z0, a1 x), z), z) = a2 x.
    R4 likewise one accessor deeper.
    """
    print('[4] THE BLOCKER: P decoded by a rule other than R1', flush=True)
    tot = 0; seen = {}
    for seed in (7, 13, 29, 101):
        rng = random.Random(seed)
        C = LeanOp(); t0 = time.time(); n = 0
        for _ in range(N):
            which = rng.randrange(3)
            z0 = rand_term(rng.randrange(0, 3), 3, rng)
            A = rand_term(rng.randrange(0, 3), 3, rng)
            Cc = rand_term(rng.randrange(0, 3), 3, rng)
            if which == 0:
                z = rand_term(rng.randrange(0, 3), 3, rng)
                X1 = J(A, J(Cc, z0))
                try:
                    X2 = C.op(C.op(C.op(z0, X1), z), z)
                except RecursionError: continue
                x = J(X1, X2)
            elif which == 1:
                # R3: z carries the locator
                X1 = rand_term(rng.randrange(0, 3), 3, rng)
                zt = J(rand_term(1, 3, rng), J(rand_term(1, 3, rng), J(z0, rand_term(1, 3, rng))))
                z = zt
                try:
                    X2 = C.op(C.op(C.op(z0, X1), z), z)
                except RecursionError: continue
                x = J(X1, X2)
            else:
                X1 = rand_term(rng.randrange(0, 3), 3, rng)
                z = J(rand_term(1, 3, rng), J(rand_term(1, 3, rng), J(J(z0, rand_term(1, 3, rng)), rand_term(1, 3, rng))))
                try:
                    X2 = C.op(C.op(C.op(z0, X1), z), z)
                except RecursionError: continue
                x = J(X1, X2)
            if max(sz(x), sz(z)) > 700: continue
            try:
                P = C.op(z, x)
            except RecursionError: continue
            br = C.fired[(z, x)]
            if br in (0, 1): continue          # not the cell we want
            for _y in range(3):
                y = rand_term(rng.randrange(0, 4), 3, rng)
                if sz(x) + sz(y) + sz(z) > 900: continue
                n += 1
                ok = check(C, x, y, z, 'blocker s%d' % seed)
                cl, _ = C.cells(x, y, z)
                seen[cl] = seen.get(cl, 0) + 1
        tot += report('blocker s%d' % seed, n, t0)
    print('  cells with P decoded by R2/R3/R4:', dict(sorted(seen.items(), key=lambda kv: -kv[1])[:16]), flush=True)
    return tot

# --------------------------------------------------------------------------- stage 5
def stage5(N=120):
    """level-k descent: nest encodings under a fixed left element, with large junk."""
    print('[5] level-k descent (nested encodings), levels 0..4, small and large junk', flush=True)
    tot = 0
    for levels in range(5):
        for big in (False, True):
            for seed in (5, 19):
                rng = random.Random(seed * 31 + levels)
                C = LeanOp(); t0 = time.time(); n = 0
                for _ in range(N):
                    u0 = rand_term(rng.randrange(0, 3), 3, rng)
                    p = rand_term(rng.randrange(0, 3), 3, rng)
                    okrun = True
                    for _i in range(levels + 1):
                        junk = rand_term(rng.randrange(5, 8), 3, rng) if big else rand_term(rng.randrange(0, 3), 3, rng)
                        try:
                            p = enc(C, u0, p, junk)
                        except RecursionError:
                            okrun = False; break
                        if sz(p) > 1500: okrun = False; break
                    if not okrun: continue
                    x = p; z = u0
                    y = rand_term(rng.randrange(0, 4), 3, rng)
                    n += 1
                    check(C, x, y, z, 'descent L%d %s' % (levels, 'big' if big else 'sml'))
                tot += report('descent L%d %s s%d' % (levels, 'big' if big else 'sml', seed), n, t0)
    return tot

# --------------------------------------------------------------------------- stage 6
def stage6(N=250000):
    """broad structured random, three shapes of assignment, three seeds."""
    print('[6] broad structured random', flush=True)
    tot = 0
    for seed in (2, 8, 64):
        rng = random.Random(seed)
        C = LeanOp(); t0 = time.time(); n = 0
        pool = []
        for _ in range(N):
            r = rng.random()
            def pick():
                if pool and rng.random() < 0.45: return rng.choice(pool)
                return rand_term(rng.randrange(0, 5), 3, rng)
            x, y, z = pick(), pick(), pick()
            if sz(x) + sz(y) + sz(z) > 260: continue
            n += 1
            if check(C, x, y, z, 'broad s%d' % seed):
                if len(pool) < 500:
                    P = C.op(z, x); Q = C.op(P, y); R = C.op(Q, y); S = C.op(x, R)
                    for t in (P, Q, R, S):
                        if sz(t) <= 40: pool.append(t)
        tot += report('broad s%d' % seed, n, t0, 'branches %s' % C.counts)
    return tot


STAGES = {0: stage0, 1: stage1, 2: stage2, 3: stage3, 4: stage4, 5: stage5, 6: stage6}

if __name__ == '__main__':
    want = [int(a) for a in sys.argv[1:] if a.isdigit()] or sorted(STAGES)
    T0 = time.time()
    for s in want:
        STAGES[s]()
    print('\n=== TOTAL BAD %d  (%.1fs) ===' % (len(FAILS), time.time() - T0), flush=True)
    for f in FAILS[:8]:
        print('FAIL', f[0], 'x=%s' % show(f[2]), 'y=%s' % show(f[3]), 'z=%s' % show(f[4]),
              '->', (f[1] if isinstance(f[1], str) else show(f[1])), flush=True)
