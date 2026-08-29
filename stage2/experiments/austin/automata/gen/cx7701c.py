"""Wider validation of the repaired 7701 rule set (R1..R4): level-3 coincidences (size-capped) + N deep tests x seeds.
usage: python -u cx7701c.py [N] [seed ...]      (hard caps: term size <= CAP, <= 120 s per seed)
"""
import sys, time
sys.path.insert(0, 'C:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
sys.path.insert(0, 'C:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen')
import closedform as cf
from freemodel import normalise, catalog
from laws import parse_eq
from rules7701fix import rules4

CAP = 60
law = normalise(parse_eq(catalog()[7701]))
C = cf.Closed(law, rules4)
rhs = law[1]
def g(n): return ('g', n)
def J(a, b): return ('J', a, b)
def show(t):
    if t[0] == 'g': return 'g%d' % t[1]
    return '(%s %s)' % (show(t[1]), show(t[2]))
def enc(u, x0, z0): return J(u, J(J(x0, J(z0, x0)), u))
def encop(u, x0, z0):
    if cf.size(u) + cf.size(x0) + cf.size(z0) > CAP // 2: return None
    return C.op(u, C.op(C.op(x0, C.op(z0, x0)), u))
def run(x, y, z):
    r = C.evp(rhs, {'x': x, 'y': y, 'z': z})
    if r != x:
        print('FAIL x =', show(x)); print('     y =', show(y)); print('     z =', show(z))
        q1 = C.op(z, x); q2 = C.op(x, q1); q3 = C.op(q2, y); q4 = C.op(y, q3); q5 = C.op(y, q4)
        print('  z*x =', show(q1)); print('  x*(z*x) =', show(q2)); print('  (..)*y =', show(q3))
        print('  y*(..) =', show(q4)); print('  y*(y*(..)) =', show(q5))
        return False
    return True
def small(ts): return [t for t in {t: None for t in ts if t is not None} if cf.size(t) <= CAP]

t0 = time.time(); tested = 0; fails = 0
base = [g(0), g(1), J(g(0), g(1)), J(g(1), g(0))]
lvl1 = list(base)
for u in base:
    for x0 in base:
        for z0 in base:
            lvl1.append(encop(u, x0, z0)); lvl1.append(enc(u, x0, z0))
lvl1 = small(lvl1)
lvl2 = list(lvl1)
for u in lvl1[:20]:
    for x0 in lvl1[:10]:
        for z0 in base + [u]:
            lvl2.append(encop(u, x0, z0))
lvl2 = small(lvl2)
print('pool sizes', len(lvl1), len(lvl2), 'max size', max(cf.size(t) for t in lvl2), flush=True)
for z in lvl1:
    for x in lvl2:
        q1 = C.op(z, x); q2 = C.op(x, q1)
        if cf.size(q2) > CAP: continue
        ys = [x, z, q2, J(q2, z), J(q2, x)]
        for y0 in [g(0), x, z, q2]:
            for yz in [g(1), q2, x, z]:
                e1 = encop(q2, y0, yz)
                ys += [e1, enc(q2, y0, yz), encop(x, y0, yz), encop(z, y0, yz)]
                if e1 is not None: ys.append(encop(q2, e1, yz))
        for y in small(ys):
            tested += 1
            if not run(x, y, z):
                fails += 1
                if fails > 3: break
        if fails > 3: break
    if fails > 3: break
print('level-3 coincidence tested', tested, 'fails', fails, 'in %.1fs' % (time.time() - t0), 'memo', len(C.memo), flush=True)

N = int(sys.argv[1]) if len(sys.argv) > 1 else 40000
seeds = [int(s) for s in sys.argv[2:]] or [1, 2, 3]
for seed in seeds:
    C = cf.Closed(law, rules4)   # fresh memo per seed
    t0 = time.time()
    tst, fl = cf.deep_tests(C, law, N, 120, seed)
    print('deep_tests seed', seed, 'tested', tst, 'fails', len(fl), 'in %.0fs' % (time.time() - t0), 'fired', C.fired, flush=True)
    for f in fl[:3]: print('  ', f)
