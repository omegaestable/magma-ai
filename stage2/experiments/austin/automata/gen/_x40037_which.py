"""Which rule fires at each chain product of law 40037 (4-rule model), over the exhaustive pool.

Also records, whenever s1 = op(y,x) is DECODED, whether P3's structural conditions hold for x with
W = a1(a2 x) = y (the fact rule R3 needs).
"""
import sys, os, itertools, collections
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'gen'))
import closedform as cf, leangen, smallcheck as sc
from freemodel import normalise, catalog, size
from laws import parse_eq
import _x40037_rules as R

EQ = 40037
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = ('x', leangen.dual_pat(orig[1]))
idx = [int(i) for i in (sys.argv[1] if len(sys.argv) > 1 else '1,2,14,10').split(',')]
rules = [R.ALL[i - 1] for i in idx]

WHICH = {}


class Which(cf.Closed):
    def op(self, u, v):
        k = (u, v)
        if k in self.memo:
            return self.memo[k]
        r = super().op(u, v)
        if r != ('J', u, v) and k not in WHICH:
            # re-run the rules one at a time to see which fires first
            for i, rl in enumerate(rules):
                sub = cf.Closed(law, rules)
                sub.memo = self.memo
                if sub.check(rl[0], u, v):
                    WHICH[k] = i
                    break
            else:
                WHICH[k] = -1
        return r


def J(a, b):
    return ('J', a, b)


def a1(t):
    return t[1] if t[0] == 'J' else t


def a2(t):
    return t[2] if t[0] == 'J' else t


def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))


def isJ(t):
    return t[0] == 'J'


def P3ok(x):
    """P3's structural conditions on A = a1 v = x"""
    if not isJ(x):
        return False
    if not isJ(a2(x)):
        return False
    if not isJ(a2(a2(x))):
        return False
    if not isJ(a1(a2(a2(x)))):
        return False
    if a2(a1(a2(a2(x)))) != a1(x):
        return False
    if a1(a1(a2(a2(x)))) != a2(a2(a2(x))):
        return False
    return True


C = Which(law, rules)
tab = collections.Counter()
p3tab = collections.Counter()
bad = []
ex = {}

pool = sc.terms_upto(9, 1) + sc.terms_upto(7, 2)
pool = list(dict.fromkeys(pool))
n = 0
for x, y, z in itertools.product(pool, repeat=3):
    try:
        s1 = C.op(y, x); s2 = C.op(s1, y); s3 = C.op(z, s2); s4 = C.op(x, s3); s5 = C.op(z, s4)
    except RecursionError:
        continue
    n += 1
    m = tuple('F' if a == J(*b) else 'D%d' % (WHICH.get(b, -1) + 1)
              for a, b in ((s1, (y, x)), (s2, (s1, y)), (s3, (z, s2)), (s4, (x, s3)), (s5, (z, s4))))
    tab[m] += 1
    ex.setdefault(m, (x, y, z))
    if m[0] != 'F':
        ok = P3ok(x) and a1(a2(x)) == y
        p3tab[(m[0], ok)] += 1
        if not ok:
            ex.setdefault(('NOP3', m[0]), (x, y, z))
    if s5 != x:
        bad.append(((x, y, z), m))

print('assignments', n, 'law fails', len(bad))
print('%-30s %s' % ('(s1,s2,s3,s4,s5) rule#', 'count'))
for k, c in sorted(tab.items(), key=lambda kv: -kv[1]):
    x, y, z = ex[k]
    print('%-30s %-9d  x=%s' % (str(k), c, show(x)[:50]))
print()
print('when s1 decoded: (rule, P3(x) and a1(a2 x)=y) ->', dict(p3tab))
for k, v in ex.items():
    if isinstance(k, tuple) and k and k[0] == 'NOP3':
        print('  NO-P3 example', k, 'x=%s' % show(v[0])[:70], 'y=%s' % show(v[1])[:70])
