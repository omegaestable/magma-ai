# -*- coding: utf-8 -*-
"""Session 9: characterise the 632 L1 failures of the four-constructor 9663 carrier."""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _x9663_lab4 as L

pool = L.terms(5, 2)
print('pool size', len(pool))
bad = []
for x in pool:
    for y in pool:
        for z in pool:
            try:
                pr = L.prof(x, y, z); r = L.chain(x, y, z)[4]
            except RecursionError:
                continue
            if r != x:
                bad.append((x, y, z, pr))
print('BAD', len(bad))

# group by (profile, shape of y, sizes)
c = collections.Counter()
for x, y, z, pr in bad:
    c[(','.join(pr), y[0], L.sz(x), L.sz(y), L.sz(z))] += 1
for k, v in sorted(c.items(), key=lambda kv: -kv[1])[:25]:
    print('  %-24s ytag=%s sx=%d sy=%d sz=%d : %d' % (k[0], k[1], k[2], k[3], k[4], v))

print()
print('--- distinct y values among failures ---')
ys = collections.Counter(L.show(y) for x, y, z, pr in bad)
for k, v in ys.most_common(20):
    print('  %-60s %d' % (k[:60], v))
print('distinct y:', len(ys))
print()
print('--- distinct x ---')
xs = collections.Counter(L.show(x) for x, y, z, pr in bad)
for k, v in xs.most_common(10):
    print('  %-60s %d' % (k[:60], v))
print('distinct x:', len(xs))
print()
print('--- distinct (x,y) ---')
xys = collections.Counter((L.show(x), L.show(y)) for x, y, z, pr in bad)
print('distinct (x,y):', len(xys))
for k, v in xys.most_common(12):
    print('  x=%-24s y=%-40s %d' % (k[0][:24], k[1][:40], v))

print()
print('--- smallest few witnesses, full chain ---')
for x, y, z, pr in sorted(bad, key=lambda t: (L.sz(t[0]) + L.sz(t[1]) + L.sz(t[2])))[:6]:
    P, Q, A, C, R = L.chain(x, y, z)
    print('prof=%s' % ','.join(pr))
    print('  x=%s' % L.show(x))
    print('  y=%s' % L.show(y))
    print('  z=%s' % L.show(z))
    print('  P=%s' % L.show(P))
    print('  Q=%s' % L.show(Q))
    print('  A=%s' % L.show(A))
    print('  C=%s' % L.show(C))
    print('  R=%s' % L.show(R))
    print()
