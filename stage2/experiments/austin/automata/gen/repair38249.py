"""repair38249.py : the repaired rule set for law 38249 (dual L-form  x = y * (y * ((z * (x * x)) * y)) ).

The generator's single syntactic rule R1 is not a model: when y itself encodes a payload c by the product
s2 = z*(x*x)  (y = J s2 (J (J a (J c c)) s2)), the THIRD product s3 = s2*y fires R1 and returns c, and the
chain ends at J y (J y c) != x  (gen/cex38249.py).  Every reduction has  u = v.1, so in that case x is still
readable from y = J (J z (J x x)) _ ; the repair is one recursive rule:

   R2 :  v = J u c  &  u.1 = J z (J t t)  &  op(u.1, u) = c   ->   t   (= u.1.2.1)

Size invariant (one unfold, no induction):  op u v = J u v  or  sz (op u v) < sz v  (R1: payload inside v)
or  sz (op u v) < sz u  (R2: payload inside u).  With it the law's chain is:  s1 = x*x free, s2 = z*s1 free,
s3 = s2*y free or reduced (then y.1 = s2 and sz s3 < sz y), s4 = y*s3 free (a reduction needs s3.1 = y),
s5 = y*s4 fires R1 (s3 free) or R2 (s3 reduced).

Usage:  python gen/repair38249.py validate [N]     deep tests (4 seeds), structured fuzz, hand + targeted coincidences
        python gen/repair38249.py emit             leangen.emit into gen/repair38249/ with the repaired rules
"""
import sys, os, random, time
HERE = 'C:\\Users\\nacho\\Documents\\GitHub\\magma-ai\\stage2\\experiments\\austin\\automata'
sys.path.insert(0, HERE)
import closedform as cf
from freemodel import normalise, catalog, size, rand_term
from laws import parse_eq
from leangen import dual_pat

U = ('U',); V = ('V',)
def A1(e): return ('A1', e)
def A2(e): return ('A2', e)
R1 = ([('TG', V), ('EQ', U, A1(V)), ('TG', A2(V)), ('TG', A1(A2(V))), ('TG', A2(A1(A2(V)))),
       ('EQ', A1(A2(A1(A2(V)))), A2(A2(A1(A2(V))))), ('EQ', U, A2(A2(V)))],
      A1(A2(A1(A2(V)))), 'free')
R2 = ([('TG', V), ('EQ', U, A1(V)), ('TG', A1(U)), ('TG', A2(A1(U))), ('EQ', A1(A2(A1(U))), A2(A2(A1(U)))),
       ('OPEQ', ('OP', A1(U), U), A2(V))],
      A1(A2(A1(U))), 'R2')
RULES = [R1, R2]

orig = normalise(parse_eq(catalog()[38249]))
LAW = ('x', dual_pat(orig[1]))

def J(a, b): return ('J', a, b)
def g(n): return ('g', n)
def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else 'J(%s, %s)' % (show(t[1]), show(t[2]))

def which_rule(C, u, v):
    for i, (conds, e, tag) in enumerate(C.rules):
        if C.check(conds, u, v) and C.ev(e, u, v) is not None: return 'R%d' % (i + 1)
    return 'free'

def trace(C, s):
    x, y, z = s['x'], s['y'], s['z']
    s1 = C.op(x, x); s2 = C.op(z, s1); s3 = C.op(s2, y); s4 = C.op(y, s3); s5 = C.op(y, s4)
    steps = ' | '.join('%s:%s' % (n, which_rule(C, a, b)) for n, a, b in
                       [('x*x', x, x), ('z*s1', z, s1), ('s2*y', s2, y), ('y*s3', y, s3), ('y*s4', y, s4)])
    return steps, s5 == x

def lawval(C, s):
    A, B = LAW[1]
    return C.op(C.evp(A, s), C.evp(B, s))

def hand_instances():
    out = []
    # (a) the R1 coincidence of gen/cex38249.py
    x = g(0); z = g(1); s2 = J(z, J(x, x)); y = J(s2, J(J(g(2), J(g(3), g(3))), s2))
    out.append(('a: s3 fires R1', {'x': x, 'y': y, 'z': z}))
    # (b) s3 fires R2:  x = J z'' (J t t), z = x, s2 = J x (J x x), y = J s2 t
    t = g(5); x = J(g(4), J(t, t)); z = x; s2 = J(z, J(x, x)); y = J(s2, t)
    out.append(('b: s3 fires R2', {'x': x, 'y': y, 'z': z}))
    # (c) payload of (a)-shape is itself a reduced-chain term
    ya = out[0][1]['y']
    x = g(6); z = g(7); s2 = J(z, J(x, x)); y = J(s2, J(J(g(8), J(ya, ya)), s2))
    out.append(('c: payload = y of (a)', {'x': x, 'y': y, 'z': z}))
    # (d) x itself is the y of (a); z = g
    out.append(('d: x = y of (a)', {'x': ya, 'y': J(J(g(1), J(ya, ya)), J(J(g(2), J(g(3), g(3))), J(g(1), J(ya, ya)))), 'z': g(1)}))
    # (e) y = J s2 s2 and y = J s2 (J s2 s2)
    x = g(0); z = g(1); s2 = J(z, J(x, x))
    out.append(('e1: y = J s2 s2', {'x': x, 'y': J(s2, s2), 'z': z}))
    out.append(('e2: y = J s2 (J s2 s2)', {'x': x, 'y': J(s2, J(s2, s2)), 'z': z}))
    out.append(('e3: y = s2', {'x': x, 'y': s2, 'z': z}))
    out.append(('e4: y = J x x, z = x', {'x': x, 'y': J(x, x), 'z': x}))
    return out

def targeted(C, N, seed):
    """x, z, a, c from a pool of small terms and of previously built y's; y built in every rule-shaped way
    from the same z, x (and their products), so that s3 = s2*y is a redex whenever the rules allow it."""
    random.seed(seed)
    pool = [g(i) for i in range(4)]
    fails = []; tested = 0
    for _ in range(N):
        pick = lambda: random.choice(pool) if random.random() < 0.8 else rand_term(random.choice([1, 2]))
        x, z, a, c, w = (pick() for _ in range(5))
        s2 = J(z, J(x, x))
        kind = random.randrange(8)
        if kind == 0: y = J(s2, J(J(a, J(c, c)), s2))            # y encodes c by s2 (R1 shape)
        elif kind == 1: y = J(s2, c)                              # R2 shape with c arbitrary
        elif kind == 2: y = J(s2, C.op(s2, w))                    # R2 shape with c = a product of s2
        elif kind == 3: y = J(s2, C.op(s2, J(s2, J(J(a, J(c, c)), s2))))  # c = the R1 payload
        elif kind == 4: y = J(J(x, J(x, x)), c); z = x            # s2 = J x (J x x)
        elif kind == 5: y = J(s2, J(J(a, J(s2, s2)), s2))         # payload = s2 itself
        elif kind == 6: y = C.op(s2, J(s2, J(J(a, J(c, c)), s2))) # y = a reduced product
        else: y = J(J(s2, J(J(a, J(c, c)), s2)), w)              # y.1 encodes c by s2
        if max(size(x), size(y), size(z)) > 400: continue
        s = {'x': x, 'y': y, 'z': z}
        tested += 1
        r = lawval(C, s)
        if r != x: fails.append((s, r))
        for t in (y, C.op(s2, y), C.op(y, C.op(s2, y))):
            if size(t) <= 60 and len(pool) < 300: pool.append(t)
    return tested, fails

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'validate'
    if mode == 'validate':
        N = int(sys.argv[2]) if len(sys.argv) > 2 else 10000
        print('law (dual):', LAW)
        for r in RULES: print('  ', cf.show_rule(r))
        C = cf.Closed(LAW, RULES)
        for name, s in hand_instances():
            C = cf.Closed(LAW, RULES)
            steps, ok = trace(C, s)
            r = lawval(C, s)
            print('%-28s %s  -> %s' % (name, steps, 'OK' if r == s['x'] else 'FAIL: got ' + show(r)))
        t0 = time.time(); tot = nf = 0
        for seed in (11, 12, 13, 14):
            C = cf.Closed(LAW, RULES)
            tested, fails = cf.deep_tests(C, LAW, N, 300, seed)
            tot += tested; nf += len(fails)
            for s, l in fails[:2]:
                print('   deep fail (seed %d) sizes x,y,z = %d %d %d -> %s' % (seed, size(s['x']), size(s['y']), size(s['z']), trace(C, s)[0]))
        print('deep tests', tot, 'fails', nf, 'secs', round(time.time() - t0, 1))
        import fuzz as fz
        t0 = time.time()
        ft, ff = fz.fuzz(cf.Closed(LAW, RULES), LAW, RULES, 12000, seed=38249)
        print('fuzz', ft, 'fails', len(ff), 'secs', round(time.time() - t0, 1))
        for s, l in ff[:3]:
            print('   fuzz fail sizes x,y,z = %d %d %d -> %s' % (size(s['x']), size(s['y']), size(s['z']), trace(cf.Closed(LAW, RULES), s)[0]))
        t0 = time.time(); tot = nf = 0
        for seed in (1, 2, 3):
            C = cf.Closed(LAW, RULES)
            tested, fails = targeted(C, N, seed)
            tot += tested; nf += len(fails)
            for s, l in fails[:2]:
                print('   targeted fail (seed %d) sizes x,y,z = %d %d %d -> %s' % (seed, size(s['x']), size(s['y']), size(s['z']), trace(C, s)[0]))
        print('targeted', tot, 'fails', nf, 'secs', round(time.time() - t0, 1))
    elif mode == 'emit':
        import json, leangen
        outdir = os.path.join(HERE, 'gen', 'repair38249')
        print(json.dumps(leangen.emit(38249, outdir, rules_override=RULES)))
