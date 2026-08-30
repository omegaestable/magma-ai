"""Check the invariant the Lean MAIN lemma needs:  inimg (op z u) u   for all z,u."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _idc_lib import G, J, sz, show, terms
import q9663c as M
op, inimg = M.op, M.inimg
for ms, gens in ((13, 1), (7, 2)):
    pool = terms(ms, gens)
    bad = []
    for z in pool:
        for u in pool:
            if not inimg(op(z, u), u):
                bad.append((z, u))
    print('inimg (op z u) u : size<=%d gens=%d pool=%d pairs=%d COUNTEREX=%d'
          % (ms, gens, len(pool), len(pool)**2, len(bad)))
    for z, u in bad[:3]:
        print('   z=%s u=%s -> op=%s' % (show(z)[:50], show(u)[:50], show(op(z, u))[:50]))
