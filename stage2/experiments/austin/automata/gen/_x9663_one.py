import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _x9663_lab4 as L

gen = L.g_deep(int(sys.argv[-1]) if sys.argv[-1].isdigit() else 5, 5, 3); bad = []; cells = {}
for i in range(30000):
    x, y, z = next(gen)
    try:
        pr = L.prof(x, y, z); r = L.chain(x, y, z)[4]
    except RecursionError: continue
    c = cells.setdefault(pr, [0, 0]); c[0] += 1
    if r != x: c[1] += 1; bad.append((x, y, z))
print('deep seed=5 n=30000 BAD=%d cells=%d' % (len(bad), len(cells)))
for k in sorted(cells, key=lambda k: -cells[k][1])[:5]:
    print('   %-18s %6d  %d bad' % (','.join(k), cells[k][0], cells[k][1]))
for x, y, z in sorted(bad, key=lambda t: sum(L.sz(q) for q in t))[:2]:
    P, Q, A, C, R = L.chain(x, y, z)
    print('--- prof=%s  sz x=%d y=%d z=%d' % (','.join(L.prof(x, y, z)), L.sz(x), L.sz(y), L.sz(z)))
    print('   x=%s' % L.show(x)[:130]); print('   y=%s' % L.show(y)[:130]); print('   z=%s' % L.show(z)[:130])
    print('   P=%s' % L.show(P)[:130]); print('   Q=%s' % L.show(Q)[:130])
    print('   A=%s' % L.show(A)[:130]); print('   C=%s' % L.show(C)[:130]); print('   R=%s' % L.show(R)[:130])
