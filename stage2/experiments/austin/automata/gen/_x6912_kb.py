"""Ordered completion from law 6912 alone: what identities does it derive?
Also: is it collapsing (x = y derivable)?  Are the three row goals joinable?"""
import sys, os, time
REPO = 'c:/Users/nacho/Documents/GitHub/magma-ai'
sys.path.insert(0, REPO + '/stage2/experiments/completion')
from kb2 import Completion, F, V, tstr
import solve_row as SR

LAWS = {
    6912: 'x = y * (y * ((z * z) * (x * y)))',
    28770: 'x = (((y * y) * y) * x) * (y * z)',
    15535: 'x = y * (((x * (z * z)) * y) * y)',
}
budget = float(sys.argv[1]) if len(sys.argv) > 1 else 120.0
maxsize = int(sys.argv[2]) if len(sys.argv) > 2 else 44

eq1 = SR.parse_eq(LAWS[6912].replace('*', '\u25c7'))
comp = Completion([eq1], max_size=maxsize, max_active=900)
t0 = time.time()
for a in list(comp.active):
    for b in list(comp.active):
        for (l, r, ch) in comp.crit_pairs(a, b):
            comp.push(l, r, ch, 'cp')
n = 0
collapse = None
while time.time() - t0 < budget:
    e = comp.step()
    if e is None:
        print('SATURATED after %d equations, %.1fs' % (n, time.time() - t0), flush=True)
        break
    n += 1
    if e.lhs[0] == 'V' and e.rhs[0] == 'V' and e.lhs != e.rhs:
        collapse = e
        print('COLLAPSE derived:', tstr(e.lhs), '=', tstr(e.rhs), flush=True)
        break
print('processed', n, 'equations in %.1fs; active %d' % (time.time() - t0, len(comp.active)))
print('collapse:', collapse is not None)

# the derived identity we proved by hand:  (a*a) = (a*a)*(a*a)
a = V('a'); sq = F(a, a)
tgt = (sq, F(sq, sq))
nl, _ = comp.normalize(tgt[0]); nr, _ = comp.normalize(tgt[1])
print('square-idempotence  a*a = (a*a)*(a*a):  normal forms', tstr(nl), '|', tstr(nr), '-> joinable', nl == nr)

print('\nsmallest 30 derived equations:')
eqs = sorted(comp.active, key=lambda e: (len(tstr(e.lhs)) + len(tstr(e.rhs))))
for e in eqs[:30]:
    print('   %s  =  %s' % (tstr(e.lhs), tstr(e.rhs)))

for gid in (28770, 15535):
    g = SR.parse_eq(LAWS[gid].replace('*', '\u25c7'))
    j = SR.joinable(comp, g[0], g[1])
    print('goal %d joinable: %s' % (gid, j is not None))
