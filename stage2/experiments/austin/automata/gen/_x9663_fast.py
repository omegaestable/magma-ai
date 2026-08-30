"""fast ranking harness: H3 first (the strongest oracle), then deep, then descent. No 3.9M L1."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _x9663_lab4 as L
L.R2ON = 'noR2' not in sys.argv

print('=== fast rank  R2=%s ===' % L.R2ON)
tot = 0
tot += L.sweep('L1 exh size<=3 2gen', L.g_L1(3, 2), 10**9)
for sd in (5, 19):
    tot += L.sweep('H3 (y = enc BY x) seed=%d' % sd, L.g_H3(sd, 3), 8000)
for sd in (5, 19):
    tot += L.sweep('deep seed=%d' % sd, L.g_deep(sd, 5, 3), 8000)
for lv in (0, 1, 2, 3):
    tot += L.sweep('descent lv=%d' % lv, L.g_desc(lv, 7, False, 3), 300)
    tot += L.sweep('descent lv=%d bigjunk' % lv, L.g_desc(lv, 7, True, 3), 300)
print('TOTAL BAD %d' % tot)
