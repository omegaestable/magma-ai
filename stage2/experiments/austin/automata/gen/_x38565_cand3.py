"""_x38565_cand3.py -- validate the 4-rule set (free, B101l, B1l, B1l+B101l) for law 38565,
including a systematic generator for the four cases of the chain case-tree
   (s1 = op x z free/decoded) x (s3 = op (op z s1) y free/decoded)
which random deep tests do not reach (DD occurs 0 times in 30,000 random draws)."""
import sys, os, time, pickle, random, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import closedform as cf, revalidate as rv, leangen
import freemodel as fm
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 38565
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = ('x', leangen.dual_pat(orig[1]))
with open(os.path.join(HERE, '_x38565_full.pkl'), 'rb') as f:
    full = pickle.load(f)
IDX = tuple(int(a) for a in (sys.argv[1].split(',') if len(sys.argv) > 1 else ['0', '1', '6', '10']))
rules = [full[i] for i in IDX]
print('SET', IDX)
for r in rules:
    print(' ', cf.show_rule(r))

g = lambda n: ('g', n)
J = lambda a, b: ('J', a, b)


def encfree(a, b, c):
    """free value of  b*(b*((c*(a*c))*b))"""
    return J(b, J(J(c, J(a, c)), b))


def rnd(depth, rng):
    if depth <= 0 or rng.random() < 0.4:
        return g(rng.randrange(3))
    return J(rnd(depth - 1, rng), rnd(depth - 1, rng))


C = cf.Closed(law, rules)


def chain(x, y, z):
    s1 = C.op(x, z); s2 = C.op(z, s1); s3 = C.op(s2, y); s4 = C.op(y, s3); top = C.op(y, s4)
    return ('D' if s1 != J(x, z) else 'F') + ('D' if s3 != J(s2, y) else 'F'), \
        ('D' if s2 != J(z, s1) else 'F') + ('D' if s4 != J(y, s3) else 'F'), top == x, top


rng = random.Random(7)
cnt = collections.Counter()
bad = []
tests = []
# FF / DF: free x, or z an encoding so that op(x,z) decodes
for t in range(400):
    x = rnd(2, rng); y = rnd(2, rng); z = rnd(2, rng)
    tests.append(('rand', x, y, z))
    xpp = rnd(2, rng); zpp = rnd(2, rng)
    zz = encfree(xpp, x, zpp)                      # op(x,zz) -> xpp  (s1 decoded)
    tests.append(('DF', x, y, zz))
    s1 = C.op(x, zz); s2 = C.op(zz, s1)
    w = rnd(2, rng); z3 = rnd(2, rng)
    yy = encfree(w, s2, z3)                        # op(s2,yy) -> w   (s3 decoded)
    tests.append(('DD', x, yy, zz))
    # FD: s1 free, s3 decoded
    s1b = J(x, z); s2b = J(z, s1b)
    if C.op(x, z) == s1b and C.op(z, s1b) == s2b:
        yy2 = encfree(w, s2b, z3)
        tests.append(('FD', x, yy2, z))
for name, x, y, z in tests:
    try:
        pat, pat2, ok, top = chain(x, y, z)
    except RecursionError:
        continue
    cnt[(name, pat, pat2, ok)] += 1
    if not ok:
        bad.append((name, x, y, z))
for k in sorted(cnt, key=lambda k: (k[0], -cnt[k])):
    print('  %-5s s1s3=%s s2s4=%s ok=%s  n=%d' % (k[0], k[1], k[2], k[3], cnt[k]))
print('case-tree instances: %d, fails %d' % (len(tests), len(bad)))
for b in bad[:3]:
    print('   FAIL', b[0], [size(t) for t in b[1:]])

if not bad:
    for seeds in ([3, 4, 5], [77, 78, 79], [101, 202, 303]):
        t0 = time.time()
        f = rv.run_tests(law, rules, seeds, 3000, 12000)
        f = [q for q in f if q[1] != 'recursion']
        print('run_tests %-14s fails %d (%.1fs)' % (str(seeds), len(f), time.time() - t0))
        for q in f[:2]:
            print('   ', {k: size(v) for k, v in q[0].items()})
    C2 = cf.Closed(law, rules)
    tot = 0
    for seed in (777, 991, 1, 2, 3, 55, 606, 7007, 80808, 999983):
        tested, fl = cf.deep_tests(C2, law, 20000, 300, seed)
        fl = [q for q in fl if q[1] != 'recursion']
        tot += len(fl)
        if fl:
            print('deep seed %-8d fails %d' % (seed, len(fl)))
    print('deep 10 x 20000: TOTAL fails', tot)
