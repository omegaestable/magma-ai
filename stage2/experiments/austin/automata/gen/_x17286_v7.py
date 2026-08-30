"""_x17286_v7.py -- v6 with the unwrap expressed as SELF-recursion instead of an unbounded list.

v6's branch V walks candidates [a1 P] ++ unwraps(P).  The unwrap chain has no fixed length, so the
Lean `op` would need a `find` helper mutually recursive with `op`.  v7 asks whether one self-call
does the same job:  when nothing fires at `v`, retry at  v' = J w (J w (a2 (a2 P))),  whose FIRST
candidate  a1 (a2 (a2 P))  is exactly v6's second candidate.  sz v' < sz v, so `sz u + sz v` still
decreases and there is no mutual recursion at all.

CAVEAT this file exists to test: from the THIRD candidate on, v7 descends via a2(a2 .) while v6
descends into the payload, so the two models are NOT identical -- only the first two agree.
"""
import sys, os, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('lab', os.path.join(HERE, '_x17286_lab.py'))
lab = importlib.util.module_from_spec(spec); spec.loader.exec_module(lab)
g, J, tg, a1, a2, sz, show, encB, deep, terms, chain = (
    lab.g, lab.J, lab.tg, lab.a1, lab.a2, lab.sz, lab.show, lab.encB, lab.deep, lab.terms, lab.chain)

class Mod:
    def __init__(self):
        self.memo = {}; self.inprog = set(); self.cycles = 0; self.depth = 0; self.fired = {}
    def codes(self, u, c):
        if tg(c) != 2 or tg(a2(c)) != 2: return False
        if a1(c) != a1(a2(c)): return False
        return self.op(u, a1(c)) == a2(a2(c))
    def op(self, u, v):
        key = (u, v)
        m = self.memo.get(key)
        if m is not None: return m
        if key in self.inprog:
            self.cycles += 1; return J(u, v)
        if self.depth > 400: return J(u, v)
        self.inprog.add(key); self.depth += 1
        res = None; tag = None
        if tg(v) == 2 and tg(a2(v)) == 2 and a1(v) == a1(a2(v)):
            w = a1(v); P = a2(a2(v))
            if tg(u) == 2 and self.op(a2(u), w) == P:
                res = a2(u); tag = 'U'
            elif (tg(P) == 2 and tg(w) == 2 and tg(a2(w)) == 2 and a1(w) == a1(a2(w))
                  and self.op(u, a1(P)) == a2(P)
                  and self.op(P, a1(w)) == a2(a2(w))):
                res = J(a1(P), P); tag = 'R'
            elif tg(P) == 2 and self.codes(u, a1(P)) and self.op(a1(P), w) == P:
                res = a1(P); tag = 'V0'
            elif tg(P) == 2 and tg(a2(P)) == 2 and a1(P) == a1(a2(P)) and tg(a2(a2(P))) == 2:
                # SELF-RECURSION: retry one unwrap down, on a strictly smaller v
                r = self.op(u, J(w, J(w, a2(a2(P)))))
                if r != J(u, J(w, J(w, a2(a2(P))))): res = r; tag = 'S'
        self.depth -= 1; self.inprog.discard(key)
        if res is None: res = J(u, v); tag = 'F'
        self.fired[tag] = self.fired.get(tag, 0) + 1
        self.memo[key] = res
        return res

def full():
    tot = 0; bad = []
    for mx, gn in ((7, 2), (9, 1)):
        T = terms(mx, gn); M = Mod()
        for x in T:
            for y in T:
                for z in T:
                    if sz(x) + sz(y) + sz(z) > 15: continue
                    try: top, _ = chain(M, x, y, z)
                    except RecursionError: continue
                    tot += 1
                    if top != x: bad.append(('exh', x, y, z, top))
    for lvl in range(0, 4):
        for junk in (g(9), deep(13)):
            ws = [g(20 + i) for i in range(lvl + 2)]; M = Mod()
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
                            if sz(x) + sz(y) + sz(z) > 700 or k > 4000: continue
                            k += 1
                            try: top, _ = chain(M, x, y, z)
                            except RecursionError: continue
                            tot += 1
                            if top != x: bad.append(('lvl%d' % lvl, x, y, z, top))
    for k in range(0, 6):
        M = Mod(); ws = [g(20 + i) for i in range(k)]
        for pay in (g(0), J(g(0), g(1)), encB(g(0), g(1))):
            x = pay
            for w in ws: x = encB(x, w)
            for junk in (g(9), J(g(9), g(8)), deep(9)):
                y = J(junk, pay)
                for wz in (g(30), J(g(30), g(31))):
                    for zl in range(0, 3):
                        for base in ((x[2] if x[0] == 'J' else x), x):
                            z = base
                            for i in range(zl + 1): z = encB(z, J(wz, g(40 + i)))
                            if sz(x) + sz(y) + sz(z) > 900: continue
                            try: top, _ = chain(M, x, y, z)
                            except RecursionError: continue
                            tot += 1
                            if top != x: bad.append(('probe%d' % k, x, y, z, top))
        print('  probe level %d branches %s' % (k, dict(sorted(M.fired.items()))))
    print('v7: %d chains, %d bad' % (tot, len(bad)))
    seen = set()
    for b in bad:
        if b[0] in seen: continue
        seen.add(b[0])
        print('   %-8s x=%s y=%s z=%s -> %s' % (b[0], show(b[1]), show(b[2]), show(b[3]), show(b[4])))

if __name__ == '__main__':
    full()
