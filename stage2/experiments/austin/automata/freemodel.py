"""Generic semantic free model of a law  x = t(x,y,z)  (t = A * B), any orientation.

Carrier: free magma terms over generators ('g',n).  op(u,v) := the unique x such that
some assignment s of the law's variables has eval(A,s)=u, eval(B,s)=v (a *reading*), else J(u,v).
Readings are found top-down: a pattern node (P,Q) against a target w is read either *freely*
(w = J(a,b) with op(a,b)=J(a,b)) or as a *decode* (op(eval P, eval Q) = w with the pair being a root
reading of the law with x-value w).  A decode is resolved structurally by matching the root pattern
against the concrete side, using the invariant that decoded values are subterms of the arguments; a
pattern-vs-pattern residue is matched freely with junk fills.  The law then holds by construction
wherever readings are unique and the structural search is complete; biased random tests measure that.

Usage: python freemodel.py <eq_id> [tests] [seconds]     (prints a JSON summary line)
"""
import sys, os, json, random, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.setrecursionlimit(100000)
from laws import parse_eq, load_rows, ROOT

JUNK = ('g', -1)

def catalog():
    cat = {}
    for i, line in enumerate(open(ROOT + '/vendor/stage2-official/examples/problems/eq_size5.txt', encoding='utf-8'), 1):
        cat[i] = line.strip()
    return cat

def pvars(p, acc=None):
    if acc is None: acc = []
    if isinstance(p, str):
        if p not in acc: acc.append(p)
    else:
        pvars(p[0], acc); pvars(p[1], acc)
    return acc

_SZ = {}
def size(t):
    s = _SZ.get(t)
    if s is None:
        s = 1 if t[0] == 'g' else 1 + size(t[1]) + size(t[2])
        _SZ[t] = s
    return s

_HJ = {}
def has_junk(t):
    r = _HJ.get(t)
    if r is None:
        r = (t[1] < 0) if t[0] == 'g' else (has_junk(t[1]) or has_junk(t[2]))
        _HJ[t] = r
    return r

def concrete(p, s):
    return all(v in s for v in pvars(p))

def normalise(law):
    """put the bare variable on the left and call it x."""
    if not isinstance(law[0], str): law = (law[1], law[0])
    def ren(t, m):
        if isinstance(t, str): return m.get(t, t)
        return (ren(t[0], m), ren(t[1], m))
    if law[0] != 'x':
        m = {law[0]: 'x', 'x': law[0]}
        law = ('x', ren(law[1], m))
    return law

class Free:
    def __init__(self, law, maxdepth=400):
        self.lhs, self.rhs = law
        assert isinstance(self.lhs, str)
        self.A, self.B = self.rhs
        self.vars = pvars(self.rhs)
        self.memo = {}
        self.inprog = {}
        self.tainted = 0
        self.escapes = 0
        self.spurious = 0
        self.unverified = 0
        self.cycles = 0
        self.conflicts = []
        self.depth = 0
        self.maxdepth = maxdepth
        self.bail = 0
        self.evals = 0
        self.junk_used = 0
        self.junk_readings = 0
        self.bound = None
        self.cuts = 0
        self.rdepth = 0
        self.max_rdepth = 300
        self.rbail = 0
        self.active = {}
        self.frames = []
        self.rcycles = 0

    class Abort(Exception): pass

    @staticmethod
    def measure(a, b):
        sa, sb = size(a), size(b)
        return (max(sa, sb), sa + sb)

    def opb(self, a, b):
        """op strictly below the current measure; None (cut) otherwise."""
        if self.bound is not None and self.measure(a, b) >= self.bound:
            self.cuts += 1
            return None
        return self.op(a, b)

    def ev(self, p, s):
        if isinstance(p, str): return s[p]
        r = self.opb(self.ev(p[0], s), self.ev(p[1], s))
        if r is None: raise Free.Abort()
        return r

    def evj(self, p, s):
        """evaluate with unbound variables filled by JUNK."""
        if isinstance(p, str):
            if p in s: return s[p]
            self.junk_used += 1
            return JUNK
        r = self.opb(self.evj(p[0], s), self.evj(p[1], s))
        if r is None: raise Free.Abort()
        return r

    # ---- readings of pattern p against concrete target w, extending s ----
    def readings(self, p, w, s):
        if isinstance(p, str):
            if p in s:
                if s[p] == w: yield s
            else:
                s2 = dict(s); s2[p] = w; yield s2
            return
        if self.rdepth > self.max_rdepth:
            self.rbail += 1
            return
        key = (p, w, tuple(sorted((k, v) for k, v in s.items() if k != '__obl')))
        owner = self.active.get(key)
        if owner is not None:
            self.rcycles += 1        # a reading that needs itself is not well-founded (least fixed point)
            self.taint_above(owner)  # op frames strictly inside the owner saw a provisional answer
            return
        level = len(self.frames)
        self.active[key] = level; self.rdepth += 1
        held = True
        try:
            for r in self._readings(p, w, s):
                # a question re-asked from inside the consumer of an answer is not a cycle: release while suspended
                self.active.pop(key, None); self.rdepth -= 1; held = False
                yield r
                self.active[key] = level; self.rdepth += 1; held = True
        finally:
            if held: self.rdepth -= 1; self.active.pop(key, None)

    def taint_above(self, level):
        """results of op frames deeper than `level` may depend on a provisional cut: never memoize them."""
        for i in range(level, len(self.frames)):
            self.frames[i] = True

    def _readings(self, p, w, s):
        P, Q = p
        # (a) free reading
        if w[0] == 'J':
            a, b = w[1], w[2]
            if self.opb(a, b) == w:
                for s1 in self.readings(P, a, s):
                    for s2 in self.readings(Q, b, s1):
                        yield s2
        # (b) decode reading: (eval P, eval Q) is a root reading with x-value w
        if has_junk(w): return          # junk terms are never real elements: no decode can produce them
        cP, cQ = concrete(P, s), concrete(Q, s)
        try:
            if cP and cQ:
                a = self.ev(P, s); b = self.ev(Q, s)
                if self.opb(a, b) == w and not (w[0] == 'J' and w[1] == a and w[2] == b):
                    yield s
                return
            # root reading r with r[x] = w; match the concrete side first
            if cQ:
                b = self.ev(Q, s)
                if has_junk(b): return
                for r in self.readings(self.B, b, {'x': w}):
                    try:
                        a = self.evj(self.A, r)
                        if self.opb(a, b) != w: continue
                    except Free.Abort:
                        continue
                    for s2 in self.readings(P, a, s):
                        yield s2
                return
            if cP:
                a = self.ev(P, s)
                for r in self.readings(self.A, a, {'x': w}):
                    for s2, r2, left in self.matchpp(Q, s, self.B, r):
                        if left or not concrete(Q, s2):
                            yield self.oblige(s2, p, w); continue
                        try:
                            b = self.ev(Q, s2)
                            if self.opb(a, b) == w and not (w[0] == 'J' and w[1] == a and w[2] == b):
                                yield s2
                        except Free.Abort:
                            continue
                return
            # neither concrete: pattern-vs-pattern on both sides, solved jointly
            r0 = {'x': w}
            cons = []
            def collect(q, b):
                if isinstance(q, str) or isinstance(b, str):
                    cons.append((q, b)); return
                collect(q[0], b[0]); collect(q[1], b[1])
            collect(P, self.A); collect(Q, self.B)
            for s2, r2, left in self._solve(cons, s, r0):
                if left or not (concrete(P, s2) and concrete(Q, s2)):
                    yield self.oblige(s2, p, w); continue
                try:
                    a = self.ev(P, s2); b = self.ev(Q, s2)
                    if self.opb(a, b) == w and not (w[0] == 'J' and w[1] == a and w[2] == b):
                        yield s2
                except Free.Abort:
                    continue
        except Free.Abort:
            return

    def matchpp(self, q, s, bpat, r):
        """yield (s', r') with eval(q,s') = eval(bpat,r'): free unification of two patterns, each with its own
        partial assignment.  Leaf constraints are collected first, then solved: constraints with a concrete side
        are resolved by `readings` (which may bind variables on either side), and only what nothing determines is
        junk-filled."""
        cons = []
        def collect(q, b):
            if isinstance(q, str) or isinstance(b, str):
                cons.append((q, b)); return True
            return collect(q[0], b[0]) and collect(q[1], b[1])
        collect(q, bpat)
        yield from self._solve(cons, s, r)

    def oblige(self, s, p, w):
        s2 = dict(s); s2['__obl'] = s.get('__obl', ()) + ((p, w),); self.junk_readings += 1
        return s2

    def holds(self, p, w, s):
        """op(eval P, eval Q) = w as a decode (not the free product)"""
        try:
            a = self.ev(p[0], s); b = self.ev(p[1], s)
        except Free.Abort:
            return False
        r = self.opb(a, b)
        return r == w and not (w[0] == 'J' and w[1] == a and w[2] == b)

    def discharge(self, s):
        """re-verify obligations whose variables got bound; the rest are witnessed with fresh generators."""
        for _ in range(8):
            obl = s.get('__obl', ())
            if not obl: return s
            s = dict(s); s['__obl'] = ()
            progress = False; pending = []
            for p, w in obl:
                if concrete(p, s):
                    if not self.holds(p, w, s): return None
                    continue
                it = self.readings(p, w, s); found = next(it, None); it.close()
                if found is None: return None
                newvars = set(found) - set(s) - {'__obl'}
                if newvars:
                    for k in newvars: s[k] = found[k]
                    progress = True
                fobl = found.get('__obl', ())
                for o in fobl:
                    if o not in pending: pending.append(o)
                if (p, w) not in fobl and not concrete(p, s) and (p, w) not in pending:
                    pending.append((p, w))
            if not progress:
                sj = dict(s); k = 0
                for p, w in pending:
                    for v in pvars(p):
                        if v not in sj: k += 1; sj[v] = ('g', -1000 - k)
                for p, w in pending:
                    if not self.holds(p, w, sj): return None
                return s
            s['__obl'] = tuple(pending)
        return None

    def _solve(self, cons, s, r):
        """yield (s', r', leftover): resolve every constraint with a concrete side through `readings`;
        constraints that nothing determines are returned as leftovers (obligations)."""
        for i, (q, b) in enumerate(cons):
            rest = cons[:i] + cons[i + 1:]
            if concrete(q, s):
                try: val = self.ev(q, s)
                except Free.Abort: return
                for r2 in self.readings(b, val, r):
                    yield from self._solve(rest, s, r2)
                return
            if concrete(b, r):
                try: val = self.ev(b, r)
                except Free.Abort: return
                for s2 in self.readings(q, val, s):
                    yield from self._solve(rest, s2, r)
                return
        yield s, r, cons

    def op(self, u, v):
        key = (u, v)
        m = self.memo.get(key)
        if m is not None: return m
        owner = self.inprog.get(key)
        if owner is not None:
            self.cycles += 1
            self.taint_above(owner)
            return ('J', u, v)
        if self.depth > self.maxdepth:
            self.bail += 1
            self.taint_above(0)
            return ('J', u, v)
        self.inprog[key] = len(self.frames); self.frames.append(False); self.depth += 1; self.evals += 1
        saved = self.bound; self.bound = self.measure(u, v)
        xs = []
        try:
            if isinstance(self.A, str) or not isinstance(self.B, str):
                gen = (s2 for s1 in self.readings(self.A, u, {}) for s2 in self.readings(self.B, v, s1))
            else:
                gen = (s2 for s1 in self.readings(self.B, v, {}) for s2 in self.readings(self.A, u, s1))
            for s2 in gen:
                s3 = self.discharge(s2)
                if s3 is None or 'x' not in s3: continue
                # soundness: every accepted reading is re-evaluated (free variables witnessed by fresh generators)
                sj = {k: t for k, t in s3.items() if k != '__obl'}; k = 0
                for var in self.vars:
                    if var not in sj: k += 1; sj[var] = ('g', -2000 - k)
                try:
                    if self.ev(self.A, sj) != u or self.ev(self.B, sj) != v:
                        self.spurious += 1; continue
                except Free.Abort:
                    self.unverified += 1; continue
                x = s3['x']
                if x not in xs: xs.append(x)
        except BaseException as e:
            self.escapes += 1
            if self.escapes <= 2:
                import traceback; traceback.print_exc(limit=12)
            raise
        finally:
            self.bound = saved
            self.depth -= 1; del self.inprog[key]
            tainted = self.frames.pop()
        if len(xs) > 1:
            self.conflicts.append((u, v, xs))
        res = xs[0] if xs else ('J', u, v)
        if not tainted:
            self.memo[key] = res
        else:
            self.tainted += 1
        return res

def rand_term(d, ng=3):
    if d <= 0 or random.random() < 0.3: return ('g', random.randrange(ng))
    return ('J', rand_term(d - 1, ng), rand_term(d - 1, ng))

def all_subpatterns(p, acc):
    if not isinstance(p, str):
        acc.append(p); all_subpatterns(p[0], acc); all_subpatterns(p[1], acc)
    return acc

def biased_triple(F, depth, pool):
    """x,y,z from a pool that includes law-subterm evaluations (critical-pair bait)."""
    s = {v: (random.choice(pool) if pool and random.random() < 0.5 else rand_term(depth)) for v in F.vars}
    r = random.random()
    if r < 0.5:
        subs = all_subpatterns(F.rhs, [])
        p = random.choice(subs)
        s0 = {v: rand_term(depth) for v in F.vars}
        for v in F.vars:
            if random.random() < 0.5: s0[v] = s[random.choice(F.vars)]
        tgt = random.choice(F.vars)
        s[tgt] = F.ev(p, s0)
    elif r < 0.7:
        a, b = random.sample(F.vars, 2); s[a] = s[b]
    return s

def run(eq, N, secs, verbose=False):
    cat = catalog()
    law = normalise(parse_eq(cat[eq]))
    F = Free(law)
    random.seed(eq)
    t0 = time.time(); fails = []; tested = 0; pool = []
    while tested < N and time.time() - t0 < secs:
        s = biased_triple(F, 1, pool)
        lhs = F.op(F.ev(F.A, s), F.ev(F.B, s))
        tested += 1
        if len(pool) < 200:
            for v in s.values():
                if size(v) <= 25: pool.append(v)
        if lhs != s['x']:
            fails.append(s)
            if len(fails) > 5: break
        if verbose and tested % 50 == 0:
            print(tested, 'memo', len(F.memo), 'fails', len(fails), 'conf', len(F.conflicts), 'cyc', F.cycles, 'bail', F.bail, round(time.time() - t0, 1), flush=True)
        if len(F.memo) > 2000000: break
    rows = [r for r in load_rows() if int(r['eq1_id']) == eq]
    goals = {}
    for r in rows:
        g = normalise(parse_eq(cat[int(r['eq2_id'])]))
        gv = pvars(g[1]); ref = None
        for _ in range(2000):
            s = {v: rand_term(2) for v in gv}
            if random.random() < 0.3 and len(gv) > 1:
                a, b = random.sample(gv, 2); s[a] = s[b]
            try:
                if s[g[0]] != F.ev(g[1], s):
                    ref = s; break
            except RecursionError:
                break
        goals[r['eq2_id']] = None if ref is None else {k: str(v) for k, v in ref.items()}
    return dict(eq=eq, law=cat[eq], tested=tested, fails=len(fails), conflicts=len(F.conflicts), cycles=F.cycles,
                bail=F.bail, rbail=F.rbail, rcycles=F.rcycles, tainted=F.tainted, spurious=F.spurious, unverified=F.unverified, junk=F.junk_used, junk_readings=F.junk_readings, cuts=F.cuts, memo=len(F.memo), secs=round(time.time() - t0, 1),
                goals_refuted={k: v is not None for k, v in goals.items()},
                fail_examples=[{k: str(v) for k, v in f.items()} for f in fails[:2]],
                conflict_examples=[(str(u), str(v), [str(x) for x in xs]) for u, v, xs in F.conflicts[:2]])

if __name__ == '__main__':
    eq = int(sys.argv[1]); N = int(sys.argv[2]) if len(sys.argv) > 2 else 400
    secs = float(sys.argv[3]) if len(sys.argv) > 3 else 300
    print(json.dumps(run(eq, N, secs, verbose='-v' in sys.argv)))
