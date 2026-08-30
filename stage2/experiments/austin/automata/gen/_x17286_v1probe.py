"""Targeted probe of branch V1+ -- the UNWRAP branch, the whole reason this carrier differs from the
free model.  It fired only twice in the whole stack, so exercise it deliberately at every tower level."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib.util
spec = importlib.util.spec_from_file_location('lab', os.path.join(os.path.dirname(os.path.abspath(__file__)), '_x17286_lab.py'))
lab = importlib.util.module_from_spec(spec); spec.loader.exec_module(lab)
g, J, sz, show, encB, Mod, chain = lab.g, lab.J, lab.sz, lab.show, lab.encB, lab.Mod, lab.chain
deep = lab.deep

def tower_x(payload, ws):
    """x = encB(encB(...encB(payload,w0)...,w_{k-1}))  -- k levels of code around payload"""
    t = payload
    for w in ws: t = encB(t, w)
    return t

print('level  triples  bad   branch counts (this level only)')
for k in range(0, 5):
    M = Mod()                      # fresh per level so the counts are INDEPENDENT
    ws = [g(20+i) for i in range(k)]
    bad = []; n = 0
    payloads = [g(0), J(g(0),g(1)), encB(g(0),g(1))]
    junks    = [g(9), J(g(9),g(8)), deep(9)]
    for pay in payloads:
        x = tower_x(pay, ws)                      # x is a k-level code of pay
        for junk in junks:
            y = J(junk, pay)                      # so op(y,x) decodes to pay  => A decoded
            for wz in (g(30), J(g(30),g(31))):
                for zl in range(0, 3):
                    # z is an l-level code of (a2 x) or of x itself -> forces P to decode deeper
                    for base in (x[2] if x[0]=='J' else x, x):
                        z = base
                        for i in range(zl+1): z = encB(z, J(wz, g(40+i)))
                        if sz(x)+sz(y)+sz(z) > 900: continue
                        try: top, _ = chain(M, x, y, z)
                        except RecursionError: continue
                        n += 1
                        if top != x: bad.append((x,y,z,top))
    cnt = {kk:v for kk,v in sorted(M.fired.items())}
    print('%-6d %-8d %-5d %s' % (k, n, len(bad), cnt))
    for (x,y,z,top) in bad[:2]:
        print('    FAIL x=%s y=%s z=%s -> %s' % (show(x), show(y), show(z), show(top)))
