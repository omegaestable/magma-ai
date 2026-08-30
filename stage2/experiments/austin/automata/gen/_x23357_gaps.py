"""23357: hand-built 'gap' instances predicted by the mode analysis.

Each case names the configuration of the chain a = op y x, u = op a y, b = op y z, v = op x b, and asserts
the law.  Prints the rule that fired at every product so a surviving case tells you which rule saved it.
"""
import sys, os
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, trace as tr
from freemodel import size
import importlib.util
spec = importlib.util.spec_from_file_location(
    '_x23357_rep', 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/_x23357_rep.py')
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
law, rules = mod.law, mod.rules

G = lambda n: ('g', n)
J = lambda a, b: ('J', a, b)
show = tr.show

T = tr.Tracing(law, rules)


def fired(a, b):
    for i, (conds, x, tag) in enumerate(rules):
        if T.check(conds, a, b):
            r = T.ev(x, a, b)
            if r is not None:
                return r, 'R%d %s' % (i + 1, tag)
    return ('J', a, b), 'free'


def check(name, x, y, z):
    a, ra = fired(y, x)
    u, ru = fired(a, y)
    b, rb = fired(y, z)
    v, rv = fired(x, b)
    t, rt = fired(u, v)
    ok = (t == x)
    print('%-34s a:%-18s u:%-18s b:%-18s v:%-18s top:%-18s %s'
          % (name, ra, ru, rb, rv, rt, 'OK' if ok else '*** LAW FAILS ***'))
    if not ok:
        print('     x =', show(x))
        print('     y =', show(y), '  z =', show(z))
        print('     u =', show(u) if size(u) < 70 else '<%d>' % size(u))
        print('     v =', show(v) if size(v) < 70 else '<%d>' % size(v))
        print('     got', show(t) if size(t) < 70 else '<%d>' % size(t))
    return ok


CASES = []

# --- case P4@(x,w): b free, v decoded L-type through rule 4 at (x, J y z) ---
for (yv, zv, pv) in [(G(0), G(1), G(2)), (G(0), G(0), G(1)), (G(1), J(G(0), G(0)), G(2)),
                     (J(G(0), G(1)), G(2), G(0))]:
    w = J(yv, zv)
    v0 = J(J(pv, w), pv)
    xv = J(J(w, v0), w)
    CASES.append(('P4@(x,w) y=%s p=%s' % (show(yv), show(pv)), xv, yv, zv))

# --- case P9@(y,z): b decoded through the 'As' rule at (y,z) ---
# op(op(Y,b),Y) = y  with  z = J b (J Y zz);  pick Y, b so the inner products are free
for (Yv, bv, xv) in [(G(0), G(1), G(2)), (G(0), J(G(1), G(2)), G(1)), (J(G(0), G(1)), G(2), G(0))]:
    inner = fired(Yv, bv)[0]
    yv = fired(inner, Yv)[0]
    zv = J(bv, J(Yv, G(9)))
    CASES.append(('P9@(y,z) Y=%s b=%s' % (show(Yv), show(bv)), xv, yv, zv))

# --- case: v decoded R-type via P9 at (x,b) ---
for (Yv, zz) in [(G(0), G(1)), (J(G(0), G(1)), G(2))]:
    yv = G(3)
    bb = J(yv, zz)                       # b free = J y z
    xv = fired(fired(Yv, yv)[0], Yv)[0]  # x = op(op(Y,y),Y) so P9 fires at (x,b) giving a1 b = y
    CASES.append(('P9@(x,b) Y=%s' % show(Yv), xv, yv, zz))

if __name__ == '__main__':
    nbad = 0
    for name, x, y, z in CASES:
        if not check(name, x, y, z):
            nbad += 1
    print('bad', nbad, 'of', len(CASES))
