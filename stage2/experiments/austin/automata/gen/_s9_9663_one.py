# -*- coding: utf-8 -*-
"""print the full chain + profile of one witness under a given FEAT set."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _s9_9663_lab5 as L
for a in sys.argv[1:]:
    if a.startswith('f:'): L.FEAT = set(x for x in a[2:].split(',') if x)
G, J, E, F = L.G, L.J, L.E, L.F

CASES = {
 'tagf2': (J(F(J(G(1), G(0)), F(G(2), G(2))), E(G(0), J(G(0), G(0)))), J(G(0), G(0)), G(2)),
 'deep23': (J(G(2), F(G(0), J(G(0), G(0)))), J(G(0), F(G(0), G(0))), G(2)),
 'old632': (G(0), F(G(0), J(G(0), G(0))), G(0)),
}
for name in sys.argv[1:]:
    if name not in CASES: continue
    x, y, z = CASES[name]
    P, Q, A, C, R = L.chain(x, y, z)
    pr = L.prof(x, y, z)
    print('--- %s  FEAT={%s}  prof=%s  OK=%s' % (name, ','.join(sorted(L.FEAT)), ','.join(pr), R == x))
    for n, t in (('x', x), ('y', y), ('z', z), ('P', P), ('Q', Q), ('A', A), ('C', C), ('R', R)):
        print('   %s = %s' % (n, L.show(t)))
    print('   wf(x)=%s wf(y)=%s wf(z)=%s' % (L.wf(x), L.wf(y), L.wf(z)))
