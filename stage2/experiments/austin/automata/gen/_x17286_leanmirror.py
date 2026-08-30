"""_x17286_leanmirror.py -- byte-for-byte semantics of the Lean `op`/`find`/`opTail` in
gen/_x17286_mut.lean.  The Lean candidate ORDER differs from lab v6 (find walks T := a2 (a2 T)),
so this model must be validated on its OWN merits, not by assuming it equals v6."""
import sys, os, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('lab', os.path.join(HERE, '_x17286_lab.py'))
lab = importlib.util.module_from_spec(spec); spec.loader.exec_module(lab)
g, J, tg, a1, a2, sz, show, encB, deep, terms, chain = (
    lab.g, lab.J, lab.tg, lab.a1, lab.a2, lab.sz, lab.show, lab.encB, lab.deep, lab.terms, lab.chain)

class Mod:
    def __init__(self):
        self.memo = {}; self.inprog = set(); self.cycles = 0; self.depth = 0; self.fired = {}
    def Cd(self, v):
        return tg(v) == 2 and tg(a2(v)) == 2 and a1(v) == a1(a2(v))
    def find(self, u, T, w, P):
        while True:
            if (tg(T) == 2 and tg(a1(T)) == 2 and tg(a2(a1(T))) == 2
                and a1(a1(T)) == a1(a2(a1(T)))
                and self.op(u, a1(a1(T))) == a2(a2(a1(T))) and self.op(a1(T), w) == P):
                return a1(T), 'V'
            if not (tg(T) == 2 and tg(a2(T)) == 2): return J(u, u), 'X'
            T = a2(a2(T))
    def opTail(self, u, v):
        if (tg(a2(a2(v))) == 2 and tg(a1(v)) == 2 and tg(a2(a1(v))) == 2
            and a1(a1(v)) == a1(a2(a1(v)))):
            if (self.op(u, a1(a2(a2(v)))) == a2(a2(a2(v)))
                and self.op(a2(a2(v)), a1(a1(v))) == a2(a2(a1(v)))):
                return J(a1(a2(a2(v))), a2(a2(v))), 'R'
        r, tag = self.find(u, a2(a2(v)), a1(v), a2(a2(v)))
        if r == J(u, u): return J(u, v), 'F'
        return r, tag
    def op(self, u, v):
        key = (u, v)
        m = self.memo.get(key)
        if m is not None: return m
        if key in self.inprog:
            self.cycles += 1; return J(u, v)
        if self.depth > 400: return J(u, v)
        self.inprog.add(key); self.depth += 1
        if self.Cd(v):
            if tg(u) == 2 and self.op(a2(u), a1(v)) == a2(a2(v)):
                res, tag = a2(u), 'U'
            else:
                res, tag = self.opTail(u, v)
        else:
            res, tag = J(u, v), 'F'
        self.depth -= 1; self.inprog.discard(key)
        self.fired[tag] = self.fired.get(tag, 0) + 1
        self.memo[key] = res
        return res

def stack():
    tot = 0; bad = []
    for mx, gn in ((7, 2), (9, 1)):
        T = terms(mx, gn); M = Mod()
        for x in T:
            for y in T:
                for z in T:
                    if sz(x)+sz(y)+sz(z) > 15: continue
                    try: top, _ = chain(M, x, y, z)
                    except RecursionError: continue
                    tot += 1
                    if top != x: bad.append(('exh%d%d'%(mx,gn), x, y, z, top))
    for lvl in range(0, 4):
        for junk in (g(9), deep(13)):
            ws = [g(20+i) for i in range(lvl+2)]; M = Mod()
            for seed, base in ((1, g(0)), (2, J(g(0), g(1)))):
                ts = [base]
                for w in ws: ts.append(encB(ts[-1], w))
                cands = []
                for t in ts:
                    cands.append(t); cands.append(J(junk, t))
                    if t[0] == 'J': cands += [t[1], t[2]]
                cands = [c for c in cands if sz(c) <= 400][:14]
                k = 0
                for x in cands:
                    for y in cands:
                        for z in cands:
                            if sz(x)+sz(y)+sz(z) > 700 or k > 4000: continue
                            k += 1
                            try: top, _ = chain(M, x, y, z)
                            except RecursionError: continue
                            tot += 1
                            if top != x: bad.append(('lvl%d'%lvl, x, y, z, top))
    for k in range(0, 6):
        M = Mod(); ws = [g(20+i) for i in range(k)]
        for pay in (g(0), J(g(0), g(1)), encB(g(0), g(1))):
            x = pay
            for w in ws: x = encB(x, w)
            for junk in (g(9), J(g(9), g(8)), deep(9)):
                y = J(junk, pay)
                for wz in (g(30), J(g(30), g(31))):
                    for zl in range(0, 3):
                        for base in ((x[2] if x[0]=='J' else x), x):
                            z = base
                            for i in range(zl+1): z = encB(z, J(wz, g(40+i)))
                            if sz(x)+sz(y)+sz(z) > 900: continue
                            try: top, _ = chain(M, x, y, z)
                            except RecursionError: continue
                            tot += 1
                            if top != x: bad.append(('probe%d'%k, x, y, z, top))
        print('  probe level %d branches %s' % (k, dict(sorted(M.fired.items()))))
    print('LEAN MIRROR: %d chains, %d bad' % (tot, len(bad)))
    seen = set()
    for b in bad:
        if b[0] in seen: continue
        seen.add(b[0])
        print('   %-8s x=%s y=%s z=%s -> %s' % (b[0], show(b[1]), show(b[2]), show(b[3]), show(b[4])))

if __name__ == '__main__':
    stack()
