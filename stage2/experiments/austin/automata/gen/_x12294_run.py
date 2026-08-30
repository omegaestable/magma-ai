import sys, os, random, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _idc_lib import G, J, sz, show, terms, check, ev
M = __import__(sys.argv[1]); op = M.op
LAW = M.LAW
mode = sys.argv[2]
if mode == 'exh':
    ms, gens, zs = int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
    pool = terms(ms, gens); zp = terms(zs, gens); t0 = time.time()
    n, f = check(op, LAW, pool, pools={'x': pool, 'y': pool, 'z': zp}, limit=4)
    print('%s exh <=%d gens=%d z<=%d: tested=%d FAILS=%d (%.1fs)' % (sys.argv[1], ms, gens, zs, n, len(f), time.time()-t0))
    for s, r in f[:4]:
        print('   x=%s y=%s z=%s -> %s' % (show(s['x'])[:55], show(s['y'])[:55], show(s['z'])[:55], show(r)[:70]))
