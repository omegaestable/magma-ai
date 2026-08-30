"""_s9_17286_probe.py -- instrument the LEAN-EXACT mirror of gen/_x17286_mut.lean.

Questions:
  Q1  at the top product op(A,B), which branch fires, split by whether A was free or decoded?
  Q2  when A is DECODED, does branch U fire at the top, and if so is a2 A = x?
  Q3  decode uniqueness at the top: how many candidates c satisfy (a2 A = c or cds A c) and op c z = P?
  Q4  candidate global size digests, measured over every decoded pair the sweep produces.
"""
import os, importlib.util, collections
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('lab', os.path.join(HERE, '_x17286_lab.py'))
lab = importlib.util.module_from_spec(spec); spec.loader.exec_module(lab)
g, J, tg, a1, a2, sz, show, encB, deep, terms = (
    lab.g, lab.J, lab.tg, lab.a1, lab.a2, lab.sz, lab.show, lab.encB, lab.deep, lab.terms)


class Mod:
    """byte-for-byte the Lean op/opTail/find."""
    def __init__(self):
        self.memo = {}; self.inprog = set(); self.cycles = 0; self.depth = 0
        self.fired = collections.Counter()
        self.pairs = {}          # (u,v) -> (result, tag)

    def Cd(self, v):
        return tg(v) == 2 and tg(a2(v)) == 2 and a1(v) == a1(a2(v))

    def cds(self, u, c):
        return (tg(c) == 2 and tg(a2(c)) == 2 and a1(c) == a1(a2(c))
                and self.op(u, a1(c)) == a2(a2(c)))

    def find(self, u, T, w, P):
        while True:
            if (tg(T) == 2 and tg(a1(T)) == 2 and tg(a2(a1(T))) == 2
                    and a1(a1(T)) == a1(a2(a1(T)))
                    and self.op(u, a1(a1(T))) == a2(a2(a1(T))) and self.op(a1(T), w) == P):
                return a1(T), 'V'
            if not (tg(T) == 2 and tg(a2(T)) == 2):
                return J(u, u), 'X'
            T = a2(a2(T))

    def opTail(self, u, v):
        if (tg(a2(a2(v))) == 2 and tg(a1(v)) == 2 and tg(a2(a1(v))) == 2
                and a1(a1(v)) == a1(a2(a1(v)))):
            if (self.op(u, a1(a2(a2(v)))) == a2(a2(a2(v)))
                    and self.op(a2(a2(v)), a1(a1(v))) == a2(a2(a1(v)))):
                return J(a1(a2(a2(v))), a2(a2(v))), 'R'
        r, tag = self.find(u, a2(a2(v)), a1(v), a2(a2(v)))
        if r == J(u, u):
            return J(u, v), 'F'
        return r, tag

    def op(self, u, v):
        key = (u, v)
        m = self.memo.get(key)
        if m is not None:
            return m
        if key in self.inprog:
            self.cycles += 1; return J(u, v)
        if self.depth > 400:
            return J(u, v)
        self.inprog.add(key); self.depth += 1
        if self.Cd(v):
            if tg(u) == 2 and self.op(a2(u), a1(v)) == a2(a2(v)):
                res, tag = a2(u), 'U'
            else:
                res, tag = self.opTail(u, v)
        else:
            res, tag = J(u, v), 'F'
        self.depth -= 1; self.inprog.discard(key)
        self.fired[tag] += 1
        self.memo[key] = res
        self.pairs[key] = (res, tag)
        return res


def unwrap_chain(P, cap=40):
    """candidates find inspects, in order."""
    out = []; T = P; n = 0
    while n < cap:
        if tg(T) == 2:
            out.append(a1(T))
        if not (tg(T) == 2 and tg(a2(T)) == 2):
            break
        T = a2(a2(T)); n += 1
    return out


STAT = collections.Counter()
UNIQ = collections.Counter()
BAD = []
SZ = collections.Counter()


def probe(M, x, y, z):
    A = M.op(y, x); P = M.op(x, z); Q = M.op(z, P); B = M.op(z, Q); top = M.op(A, B)
    if top != x:
        BAD.append(('law', x, y, z, top))
    Afree = (A == J(y, x))
    if Q != J(z, P):
        BAD.append(('F1', x, y, z, Q))
    if B != J(z, Q):
        BAD.append(('F2', x, y, z, B))
    tag = M.pairs.get((A, B), (None, '?'))[1]
    STAT[('Afree' if Afree else 'Adec', tag)] += 1
    if not Afree:
        # Q2: does branch U fire at the top and is a2 A = x?
        if tg(A) == 2 and M.op(a2(A), z) == P:
            STAT[('AdecU', 'a2A==x' if a2(A) == x else 'a2A!=x')] += 1
        # Q3: how many valid candidates?
        cands = []
        if tg(A) == 2:
            cands.append(('U', a2(A)))
        if tg(P) == 2:
            cands.append(('R', J(a1(P), P)))
        for i, c in enumerate(unwrap_chain(P)):
            cands.append(('V%d' % i, c))
        ok = []
        for nm, c in cands:
            uok = (nm == 'U') or M.cds(A, c)
            if uok and M.op(c, z) == P:
                ok.append((nm, c))
        UNIQ[(len(ok), all(c == x for _, c in ok))] += 1
    return top


def digest(M):
    """Q4: size invariants over every decoded pair produced."""
    res = collections.Counter()
    for (u, v), (r, tag) in M.pairs.items():
        if tag == 'F':
            continue
        res['decoded'] += 1
        if sz(r) < sz(u):
            res['r<u'] += 1
        if sz(r) < sz(v):
            res['r<v'] += 1
        if sz(r) < sz(u) or sz(r) < sz(v):
            res['r<u or r<v'] += 1
        if sz(r) <= max(sz(u), sz(v)):
            res['r<=max'] += 1
        if tag == 'U' and not (sz(r) < sz(u)):
            res['U !r<u'] += 1
        if tag == 'R' and not (sz(r) < sz(v)):
            res['R !r<v'] += 1
        if tag == 'V' and not (sz(r) < sz(v)):
            res['V !r<v'] += 1
    return res


def run():
    M = Mod()
    # exhaustive small
    for mx, gn in ((7, 2), (9, 1)):
        T = terms(mx, gn)
        for x in T:
            for y in T:
                for z in T:
                    if sz(x) + sz(y) + sz(z) > 15:
                        continue
                    try:
                        probe(M, x, y, z)
                    except RecursionError:
                        pass
    print('after exhaustive: fired', dict(M.fired), 'cycles', M.cycles)
    # level-k descent, both junk pools
    for lvl in range(0, 4):
        for junk in (g(9), deep(13)):
            ws = [g(20 + i) for i in range(lvl + 2)]
            for seed, base in ((1, g(0)), (2, J(g(0), g(1)))):
                ts = [base]
                for w in ws:
                    ts.append(encB(ts[-1], w))
                cands = []
                for t in ts:
                    cands.append(t); cands.append(J(junk, t))
                    if t[0] == 'J':
                        cands += [t[1], t[2]]
                cands = [c for c in cands if sz(c) <= 400][:14]
                k = 0
                for x in cands:
                    for y in cands:
                        for z in cands:
                            if sz(x) + sz(y) + sz(z) > 700 or k > 4000:
                                continue
                            k += 1
                            try:
                                probe(M, x, y, z)
                            except RecursionError:
                                pass
    # tower probe
    for k in range(0, 6):
        ws = [g(20 + i) for i in range(k)]
        for pay in (g(0), J(g(0), g(1)), encB(g(0), g(1))):
            x = pay
            for w in ws:
                x = encB(x, w)
            for junk in (g(9), J(g(9), g(8)), deep(9)):
                y = J(junk, pay)
                for wz in (g(30), J(g(30), g(31))):
                    for zl in range(0, 3):
                        for base in ((x[2] if x[0] == 'J' else x), x):
                            z = base
                            for i in range(zl + 1):
                                z = encB(z, J(wz, g(40 + i)))
                            if sz(x) + sz(y) + sz(z) > 900:
                                continue
                            try:
                                probe(M, x, y, z)
                            except RecursionError:
                                pass
    print('BAD:', len(BAD))
    for b in BAD[:6]:
        print('   ', b[0], show(b[1]), show(b[2]), show(b[3]), '->', show(b[4]))
    print()
    print('Q1/Q2  top-product branch by A status:')
    for k in sorted(STAT, key=str):
        print('   %-20s %d' % (str(k), STAT[k]))
    print()
    print('Q3  #valid candidates at top when A decoded  (count, all==x):')
    for k in sorted(UNIQ, key=str):
        print('   %-20s %d' % (str(k), UNIQ[k]))
    print()
    print('Q4  size digest over decoded pairs:')
    d = digest(M)
    for k in sorted(d):
        print('   %-16s %d' % (k, d[k]))
    print('   fired', dict(M.fired), 'cycles', M.cycles)


if __name__ == '__main__':
    run()
