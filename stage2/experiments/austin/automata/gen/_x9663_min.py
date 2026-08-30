import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _x9663_lab as L
L.TAGV, L.DECV = sys.argv[1], sys.argv[2]
L.R2ON = (len(sys.argv) < 4 or sys.argv[3] != 'noR2')
n, bad, cells, pool = L.L1(5, 2, limit=10**9)
print('L1 n=%d BAD=%d pool=%d' % (n, len(bad), len(pool)))
for k in sorted(cells, key=lambda k: -cells[k][1])[:8]:
    print('   %-24s %8d  %d bad' % (','.join(k), cells[k][0], cells[k][1]))
bad.sort(key=lambda t: L.sz(t[0]) + L.sz(t[1]) + L.sz(t[2]))
for x, y, z in bad[:3]:
    P, Q, A, C, R = L.chain(x, y, z)
    print('--- BAD prof=%s' % ','.join(L.prof(x, y, z)))
    print('    x=%s' % L.show(x)); print('    y=%s' % L.show(y)); print('    z=%s' % L.show(z))
    print('    P=%s  Q=%s' % (L.show(P), L.show(Q)))
    print('    A=%s  C=%s' % (L.show(A), L.show(C)))
    print('    R=%s   expected %s' % (L.show(R), L.show(x)))
