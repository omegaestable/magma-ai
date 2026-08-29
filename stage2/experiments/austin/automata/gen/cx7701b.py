"""Light validation of a PROPOSED repaired rule set for 7701 (R1..R3 + R4).

R4 = R3 with the R1-shape guard on a2 (a1 u) replaced by the R2-style op-guard:
   J?v & u = v.1 & J?u & op(u.1, u) == v.2 & J?u.1 & J?u.1.1 & op(u.1.1.1, u.1.1) == u.1.2 -> u.1.1
i.e. the case where BOTH z*x and (x*(z*x))*y are decoded.  Not a proof: coincidence search + deep tests only.
"""
import sys, itertools, time
sys.path.insert(0, 'C:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf
from freemodel import normalise, catalog
from laws import parse_eq

law = normalise(parse_eq(catalog()[7701]))
exec(open('C:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chk7701.py').read().split('rules = ')[1].split('\nC = ')[0].join(['rules = ', '']))
U = ('U',); V = ('V',)
def A1(e): return ('A1', e)
def A2(e): return ('A2', e)
def OP(a, b): return ('OP', a, b)
R4 = ([('TG', V), ('EQ', U, A1(V)), ('TG', U), ('OPEQ', OP(A1(U), U), A2(V)),
       ('TG', A1(U)), ('TG', A1(A1(U))), ('OPEQ', OP(A1(A1(A1(U))), A1(A1(U))), A2(A1(U)))],
      A1(A1(U)), 'B1l+B101l')
rules4 = rules + [R4]
for r in rules4: print(cf.show_rule(r))
C = cf.Closed(law, rules4)

def g(n): return ('g', n)
def J(a, b): return ('J', a, b)
def show(t):
    if t[0] == 'g': return 'g%d' % t[1]
    return '(%s %s)' % (show(t[1]), show(t[2]))
def enc(u, x0, z0): return J(u, J(J(x0, J(z0, x0)), u))
rhs = law[1]
def run(x, y, z, label):
    r = C.evp(rhs, {'x': x, 'y': y, 'z': z})
    ok = (r == x)
    if not ok:
        print('%s: FAIL' % label)
        print('  x =', show(x)); print('  y =', show(y)); print('  z =', show(z))
        q1 = C.op(z, x); q2 = C.op(x, q1); q3 = C.op(q2, y); q4 = C.op(y, q3); q5 = C.op(y, q4)
        print('  z*x =', show(q1)); print('  x*(z*x) =', show(q2)); print('  (..)*y =', show(q3))
        print('  y*(..) =', show(q4)); print('  y*(y*(..)) =', show(q5))
    return ok

z = g(0); x = enc(z, g(1), g(2)); q2 = C.op(x, C.op(z, x)); y = enc(q2, g(3), g(4))
print('hand instance:', 'OK' if run(x, y, z, 'hand') else 'FAIL')

# systematic level-2 / level-3 coincidence search
fails = 0; tested = 0
pool = [g(0), g(1)]
def xs(z):
    out = [z, J(z, g(0)), J(g(0), z)]
    for x0 in pool:
        for z0 in pool:
            out.append(enc(z, x0, z0))
            out.append(enc(z, J(x0, z0), z0))
            out.append(enc(z, enc(z, x0, z0), z0))
            out.append(J(z, J(J(x0, C.op(z0, x0)), z)))
    return out
t0 = time.time()
for z in pool + [J(g(0), g(1))]:
    for x in xs(z):
        q1 = C.op(z, x); q2 = C.op(x, q1)
        ys = [x, z, q2, J(q2, g(0)), J(q2, x), J(x, q1)]
        for y0 in pool + [x, z, q2]:
            for yz in pool + [q2, x, z]:
                ys += [enc(q2, y0, yz), enc(q2, enc(q2, y0, yz), yz), J(q2, J(J(y0, C.op(yz, y0)), q2)),
                       enc(x, y0, yz), enc(z, y0, yz), J(q2, C.op(J(y0, C.op(yz, y0)), q2))]
                # y whose left child is q2 and right child encodes through q2's own left child
                ys += [J(q2, J(J(y0, C.op(x, y0)), q2)), J(q2, C.op(J(y0, J(x, y0)), q2))]
        for y in ys:
            tested += 1
            if not run(x, y, z, 'sys'):
                fails += 1
                if fails > 5: break
        if fails > 5: break
    if fails > 5: break
print('systematic tested', tested, 'fails', fails, 'in %.1fs' % (time.time() - t0))

N = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
for seed in (11, 7):
    t0 = time.time()
    tested, fl = cf.deep_tests(C, law, N, 300, seed)
    print('deep_tests seed', seed, 'tested', tested, 'fails', len(fl), 'in %.0fs' % (time.time() - t0))
    for f in fl[:3]: print('  ', f)
print('fired counts', C.fired)
