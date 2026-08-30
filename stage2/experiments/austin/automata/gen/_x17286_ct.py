"""_x17286_ct.py -- the CASE TREE for law 17286  x = (y*x) * (z*(z*(x*z)))

chain products:  A = op(y,x),  P = op(x,z),  Q = op(z,P),  B = op(z,Q),  top = op(A,B)
16 cells = (A free/dec) x (P free/dec) x (Q free/dec) x (B free/dec).

Forcing a decode:  op(J(q,p), encB(p,w)) = p   (rule R1).
"""
import sys, os, itertools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import closedform as cf
import freemodel as fm
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 17286
cat = catalog()
orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
import leangen
law = (('x', leangen.dual_pat(orig[1])) if dualized else orig)
print('law', law, 'dualized', dualized)
RULES = cf.Extractor(law).rules(exist=False)
print('rules', len(RULES))

g = lambda n: ('g', n)
J = lambda a, b: ('J', a, b)


def show(t, cap=28):
    if size(t) > cap: return '<sz%d>' % size(t)
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1], 99), show(t[2], 99))


def encB(p, w):
    """the free value of  z*(z*(p*z))  with z:=w -- decodes p against any J(_,p)"""
    return J(w, J(w, J(p, w)))


def encA(q, p):
    return J(q, p)


def cell(rules, x, y, z):
    C = cf.Closed(law, rules)
    try:
        A = C.op(y, x); P = C.op(x, z); Q = C.op(z, P); B = C.op(z, Q); top = C.op(A, B)
    except RecursionError:
        return None
    c = (A != J(y, x), P != J(x, z), Q != J(z, P), B != J(z, Q))
    return c, top, (A, P, Q, B)


def sem(x, y, z):
    F = fm.Free(law)
    try:
        A = F.op(y, x); P = F.op(x, z); Q = F.op(z, P); B = F.op(z, Q); top = F.op(A, B)
    except Exception as e:
        return ('ERR', repr(e))
    return top


def report(name, x, y, z, rules=RULES):
    r = cell(rules, x, y, z)
    if r is None:
        print('%-26s RECURSION' % name); return
    c, top, prods = r
    s = sem(x, y, z)
    tag = ''.join('D' if b else 'f' for b in c)
    ok = 'OK ' if top == x else '**FAIL**'
    oks = 'ok' if s == x else '**SEMFAIL**'
    print('%-26s cell=%s(A P Q B) top=%-10s %s  sem=%-10s %s  |x|=%d' %
          (name, tag, show(top), ok, show(s) if not isinstance(s, tuple) or s[0] != 'ERR' else s[1][:30], oks, size(x)))
    return tag, top == x, s == x


CASES = []

# ---- ffff : everything free
CASES.append(('ffff base', g(0), g(1), g(2)))

# ---- A decoded (x is the encB of the payload), P/Q/B free (z a generator)
pa = g(5)
CASES.append(('A dec', encB(pa, g(6)), encA(g(1), pa), g(2)))
pa2 = J(g(5), g(7))
CASES.append(('A dec (J payload)', encB(pa2, g(6)), encA(g(1), pa2), g(2)))

# ---- P decoded : x = J(q,px), z = encB(px,w).  keep A free by px = generator
px = g(5)
CASES.append(('P dec', J(g(4), px), g(1), encB(px, g(6))))

# ---- Q decoded : z = J(qz,pq), P must be encB(pq,w).
#      P = op(x,z); make P free = J(x,z) and require J(x,z) = encB(pq,w) = J(w,J(w,J(pq,w)))
#      => x = w, z = J(w, J(pq,w)) and z = J(qz,pq) => qz = w, pq = J(pq,w) impossible.
#      Instead let P decode?  (that is the PQ cell.)   Try: z = J(qz,pq) with P decoded to encB(pq,w):
#      P = op(x,z) -> needs x = J(_,p) and z = encB(p,w2); p = encB(pq,w)
w = g(6); pq = g(7)
p_mid = encB(pq, w)
CASES.append(('P dec then Q dec', J(g(4), p_mid), g(1), encB(p_mid, g(8))))

# ---- B decoded : z = J(qz,pb), Q = encB(pb,wb)
#      Q free = J(z,P) must equal J(wb, J(wb, J(pb,wb))) => z = wb, P = J(wb,J(pb,wb))
#      P free = J(x,z) => x = wb = z and z = J(pb, wb) ... z=wb and z=J(pb,wb) impossible.
#      Q free = J(z,P) with P DECODED to J(z,J(pb,z)):  z = wb, P = J(z, J(pb,z))
#      P = op(x,z) decodes to J(z,J(pb,z)) : need x = J(_, J(z,J(pb,z))) and z = encB(J(z,J(pb,z)), w2)
#      but z must also equal J(qz,pb).  z = encB(t,w2) = J(w2,J(w2,J(t,w2))) => qz=w2, pb=J(w2,J(t,w2))
#      and t = J(z,J(pb,z)) mentions z -> circular. try with B via rule P3 instead (Q decoded).
CASES.append(('B via z=J', J(g(4), g(5)), g(1), J(g(2), g(3))))

# generic sweep: all shapes built from a few generators
GENS = [g(0), g(1), g(2), J(g(0), g(1)), J(g(1), g(0)), encB(g(0), g(1)), encB(g(1), g(0)),
        encA(g(2), g(0)), encA(g(0), g(2)), encB(J(g(0), g(1)), g(2)), encA(g(3), encB(g(0), g(1)))]

for n, x, y, z in CASES:
    report(n, x, y, z)

print('\n--- sweep over %d^3 small shapes ---' % len(GENS))
seen = {}
bad = []
for x, y, z in itertools.product(GENS, repeat=3):
    r = cell(RULES, x, y, z)
    if r is None: continue
    c, top, _ = r
    tag = ''.join('D' if b else 'f' for b in c)
    seen.setdefault(tag, 0)
    seen[tag] += 1
    if top != x:
        bad.append((tag, x, y, z, top))
for k in sorted(seen): print('  %s %d' % (k, seen[k]))
print('  law failures:', len(bad))
for t in bad[:8]:
    print('   ', t[0], 'x=', show(t[1]), 'y=', show(t[2]), 'z=', show(t[3]), '->', show(t[4]))
