"""_x17286_v5.py -- carrier variant v5 for law 17286.  + the reconstruction candidate J (a1 P) P

Run:  python gen/_x17286_v5.py      (reproduces the headline result below)
Shared term helpers + oracles come from _x17286_lab.py; only `Mod` differs between variants.
HEADLINE: validated, but termination broken: J (a1 P) P is not a subterm of v
"""
import sys, os, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('lab', os.path.join(HERE, '_x17286_lab.py'))
lab = importlib.util.module_from_spec(spec); spec.loader.exec_module(lab)
g, J, tg, a1, a2, sz, show, encB, deep, terms, chain = (
    lab.g, lab.J, lab.tg, lab.a1, lab.a2, lab.sz, lab.show, lab.encB, lab.deep, lab.terms, lab.chain)


class Mod:
    """v5: v4 with J (a1 P) P added to the V candidate list."""
    def __init__(self):
        self.memo = {}; self.inprog = set(); self.cycles = 0; self.depth = 0; self.fired = {}
    def unwraps(self, P):
        out = []; cur = P; n = 0
        while tg(cur) == 2 and tg(a2(cur)) == 2 and a1(cur) == a1(a2(cur))               and tg(a2(a2(cur))) == 2 and n < 40:
            c = a1(a2(a2(cur))); out.append(c); cur = c; n += 1
        return out
    def codes(self, u, c):
        if tg(c) != 2 or tg(a2(c)) != 2: return False
        if a1(c) != a1(a2(c)): return False
        return self.op(u, a1(c)) == a2(a2(c))
    def ok_u(self, u, c):
        if tg(u) == 2 and a2(u) == c: return True
        return self.codes(u, c)
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
            else:
                cs = ([a1(P), J(a1(P), P)] if tg(P) == 2 else []) + self.unwraps(P)
                seen = set()
                for i, c in enumerate(cs):
                    if c in seen: continue
                    seen.add(c)
                    if self.codes(u, c) and self.op(c, w) == P:
                        res = c; tag = 'V%d' % i; break
        self.depth -= 1; self.inprog.discard(key)
        if res is None: res = J(u, v); tag = 'F'
        self.fired[tag] = self.fired.get(tag, 0) + 1
        self.memo[key] = res
        return res


def headline():
    bad = 0; n = 0
    for lvl in (0, 1):
        for junk in (g(9), deep(13)):
            ws = [g(20 + i) for i in range(lvl + 2)]
            M = Mod()
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
                            n += 1
                            if top != x: bad += 1
            print('  lvl %d junk sz%-3d : cumulative bad %d' % (lvl, sz(junk), bad))
    print('TOTAL %d chains, %d bad' % (n, bad))

def probe():
    """the tower probe -- the ONLY oracle that refutes v4 (18/108 at level 1). Fresh model per level."""
    print('  tower probe (fresh model per level):')
    for k in range(0, 3):
        M = Mod(); ws = [g(20 + i) for i in range(k)]
        bad = []; n = 0
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
                            n += 1
                            if top != x: bad.append((x, y, z, top))
        print('    level %d : %d triples, %d bad   branches %s'
              % (k, n, len(bad), dict(sorted(M.fired.items()))))
        for (x, y, z, top) in bad[:1]:
            print('      FAIL x=%s y=%s z=%s -> %s' % (show(x), show(y), show(z), show(top)))

if __name__ == '__main__':
    headline()
    probe()
