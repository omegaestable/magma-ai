"""Unfailing (ordered) Knuth-Bendix completion, v2: interreduction + indexing.

Proof tracking as in v1: every equation carries a rewrite chain
[(position, parent_eq_id, substitution, direction)] taking lhs to rhs.
"""
from __future__ import annotations

import heapq
import itertools
import sys

sys.setrecursionlimit(100000)


def V(n):
    return ("v", n)


def F(a, b):
    return ("f", a, b)


def tvars(t, acc=None):
    if acc is None:
        acc = set()
    stack = [t]
    while stack:
        s = stack.pop()
        if s[0] == "v":
            acc.add(s[1])
        else:
            stack.append(s[1])
            stack.append(s[2])
    return acc


def subst(t, s):
    if not s:
        return t
    if t[0] == "v":
        return s.get(t[1], t)
    return ("f", subst(t[1], s), subst(t[2], s))


_SIZE = {}


def size(t):
    r = _SIZE.get(t)
    if r is None:
        r = 1 if t[0] == "v" else 1 + size(t[1]) + size(t[2])
        _SIZE[t] = r
    return r


def varcount(t, acc=None):
    if acc is None:
        acc = {}
    stack = [t]
    while stack:
        s = stack.pop()
        if s[0] == "v":
            acc[s[1]] = acc.get(s[1], 0) + 1
        else:
            stack.append(s[1])
            stack.append(s[2])
    return acc


def tstr(t):
    if t[0] == "v":
        return t[1]
    return "(%s.%s)" % (tstr(t[1]), tstr(t[2]))


# ---------------- KBO ----------------
def kbo_gt(s, t):
    vs = varcount(s)
    vt = varcount(t)
    for v, c in vt.items():
        if vs.get(v, 0) < c:
            return False
    return _kbo(s, t)


def _kbo(s, t):
    ws, wt = size(s), size(t)
    if ws != wt:
        return ws > wt
    if s[0] == "v" or t[0] == "v":
        return False
    if s[1] != t[1]:
        return _kbo(s[1], t[1])
    return _kbo(s[2], t[2])


# ---------------- unification / matching ----------------
def _occurs(v, t):
    stack = [t]
    while stack:
        s = stack.pop()
        if s[0] == "v":
            if s[1] == v:
                return True
        else:
            stack.append(s[1])
            stack.append(s[2])
    return False


def unify(t1, t2):
    return _unify(t1, t2, {})


def _unify(a, b, s):
    a = subst(a, s)
    b = subst(b, s)
    if a == b:
        return s
    if a[0] == "v":
        if _occurs(a[1], b):
            return None
        ns = {k: subst(v, {a[1]: b}) for k, v in s.items()}
        ns[a[1]] = b
        return ns
    if b[0] == "v":
        return _unify(b, a, s)
    s = _unify(a[1], b[1], s)
    if s is None:
        return None
    return _unify(a[2], b[2], s)


def match(pat, t, s=None):
    if s is None:
        s = {}
    stack = [(pat, t)]
    out = dict(s)
    while stack:
        p, u = stack.pop()
        if p[0] == "v":
            cur = out.get(p[1])
            if cur is None:
                out[p[1]] = u
            elif cur != u:
                return None
        else:
            if u[0] != "f":
                return None
            stack.append((p[1], u[1]))
            stack.append((p[2], u[2]))
    return out


# ---------------- positions ----------------
def positions(t, pre=()):
    yield pre, t
    if t[0] == "f":
        yield from positions(t[1], pre + (1,))
        yield from positions(t[2], pre + (2,))


def get_at(t, pos):
    for p in pos:
        t = t[p]
    return t


def set_at(t, pos, new):
    if not pos:
        return new
    p = pos[0]
    if p == 1:
        return ("f", set_at(t[1], pos[1:], new), t[2])
    return ("f", t[1], set_at(t[2], pos[1:], new))


# ---------------- shape mask index ----------------
_POS = []
for _d in range(0, 4):
    for _c in itertools.product((1, 2), repeat=_d):
        _POS.append(_c)
_POSIDX = {p: i for i, p in enumerate(_POS)}
_MASK = {}


def term_mask(t):
    m = _MASK.get(t)
    if m is not None:
        return m
    m = 0
    stack = [((), t)]
    while stack:
        pos, sub = stack.pop()
        if sub[0] == "f":
            i = _POSIDX.get(pos)
            if i is not None:
                m |= 1 << i
            if len(pos) < 3:
                stack.append((pos + (1,), sub[1]))
                stack.append((pos + (2,), sub[2]))
    _MASK[t] = m
    return m


# ---------------- canonical forms ----------------
def canon_pair(l, r):
    mapping = {}

    def go(t):
        if t[0] == "v":
            if t[1] not in mapping:
                mapping[t[1]] = "v%d" % len(mapping)
            return ("v", mapping[t[1]])
        return ("f", go(t[1]), go(t[2]))

    return (go(l), go(r))


def canon_eq(l, r):
    a = canon_pair(l, r)
    b = canon_pair(r, l)
    return min((a, b), key=repr)


_TAG = itertools.count()


def rename_apart(l, r):
    tag = "r%d" % next(_TAG)
    m = {v: ("v", "%s%s" % (v, tag)) for v in (tvars(l) | tvars(r))}
    return subst(l, m), subst(r, m), tag


# ---------------- equations ----------------
class Eq:
    __slots__ = ("id", "lhs", "rhs", "chain", "weight", "origin", "ori")

    def __init__(self, eid, lhs, rhs, chain, origin=""):
        self.id = eid
        self.lhs = lhs
        self.rhs = rhs
        self.chain = chain
        self.weight = size(lhs) + size(rhs)
        self.origin = origin
        self.ori = []
        vl, vr = tvars(lhs), tvars(rhs)
        if vr <= vl:
            self.ori.append((lhs, rhs, 1, term_mask(lhs), size(lhs)))
        if vl <= vr and lhs != rhs:
            self.ori.append((rhs, lhs, -1, term_mask(rhs), size(rhs)))

    def __repr__(self):
        return "E%d: %s = %s" % (self.id, tstr(self.lhs), tstr(self.rhs))


class Completion:
    def __init__(self, axioms, max_size=40, max_active=600, max_passive=200000):
        self.eqs = {}
        self.active = []
        self.next_id = 0
        self.seen = set()
        self.passive = []
        self.counter = itertools.count()
        self.max_size = max_size
        self.max_active = max_active
        self.max_passive = max_passive
        self.axiom_ids = []
        for (l, r) in axioms:
            e = Eq(self.next_id, l, r, None, "axiom")
            self.eqs[e.id] = e
            self.axiom_ids.append(e.id)
            self.next_id += 1
            self.active.append(e)
            self.seen.add(canon_eq(l, r))

    # ---- rewriting ----
    def rewrite_once(self, t, avoid=()):
        for pos, sub in positions(t):
            if sub[0] == "v":
                continue
            sm = term_mask(sub)
            ss = size(sub)
            for e in self.active:
                if e.id in avoid:
                    continue
                for (l, r, d, lm, ls) in e.ori:
                    if ls > ss or (lm & ~sm):
                        continue
                    m = match(l, sub)
                    if m is None:
                        continue
                    rs = subst(r, m)
                    if rs == sub or not kbo_gt(sub, rs):
                        continue
                    return set_at(t, pos, rs), (pos, e.id, m, d)
        return None

    def normalize(self, t, limit=120, avoid=()):
        steps = []
        for _ in range(limit):
            res = self.rewrite_once(t, avoid=avoid)
            if res is None:
                break
            t, st = res
            steps.append(st)
        return t, steps

    # ---- passive ----
    def push(self, lhs, rhs, chain, origin):
        if size(lhs) + size(rhs) > self.max_size:
            return
        if len(self.passive) > self.max_passive:
            return
        heapq.heappush(
            self.passive,
            (size(lhs) + size(rhs), next(self.counter), lhs, rhs, chain, origin),
        )

    def subsumed(self, lhs, rhs):
        lm, rm = term_mask(lhs), term_mask(rhs)
        ls, rs = size(lhs), size(rhs)
        for e in self.active:
            for (a, b) in ((e.lhs, e.rhs), (e.rhs, e.lhs)):
                if size(a) > ls or size(b) > rs:
                    continue
                if (term_mask(a) & ~lm) or (term_mask(b) & ~rm):
                    continue
                m = match(a, lhs)
                if m is None:
                    continue
                if match(b, rhs, m) is not None:
                    return True
        return False

    # ---- critical pairs ----
    def crit_pairs(self, e1, e2):
        out = []
        for (l1, r1, d1, _m1, _s1) in e1.ori:
            for (l2o, r2o, d2, _m2, _s2) in e2.ori:
                l2, r2, tag = rename_apart(l2o, r2o)
                for pos, sub in positions(l1):
                    if sub[0] == "v":
                        continue
                    s = unify(sub, l2)
                    if s is None:
                        continue
                    l1s = subst(l1, s)
                    r1s = subst(r1, s)
                    if kbo_gt(r1s, l1s):
                        continue
                    l2s = subst(l2, s)
                    r2s = subst(r2, s)
                    if kbo_gt(r2s, l2s):
                        continue
                    new_lhs = subst(set_at(l1, pos, r2), s)
                    new_rhs = r1s
                    if new_lhs == new_rhs:
                        continue
                    sub2 = {}
                    for v in tvars(l2o) | tvars(r2o):
                        sub2[v] = subst(V(v + tag), s)
                    sub1 = {v: subst(V(v), s)
                            for v in tvars(e1.lhs) | tvars(e1.rhs)}
                    chain = [(pos, e2.id, sub2, -d2), ((), e1.id, sub1, d1)]
                    out.append((new_lhs, new_rhs, chain))
        return out

    # ---- main loop ----
    def step(self):
        """Process one passive equation. Returns the new Eq or None."""
        while self.passive:
            w, _, lhs, rhs, chain, origin = heapq.heappop(self.passive)
            nl, sl = self.normalize(lhs)
            nr, sr = self.normalize(rhs)
            if nl == nr:
                continue
            full = ([(p, i, s, -d) for (p, i, s, d) in reversed(sl)]
                    + chain + sr)
            key = canon_eq(nl, nr)
            if key in self.seen:
                continue
            if self.subsumed(nl, nr):
                continue
            self.seen.add(key)
            e = Eq(self.next_id, nl, nr, full, origin)
            self.next_id += 1
            self.eqs[e.id] = e
            self.active.append(e)
            return e
        return None

    def interreduce(self, e):
        """Collapse active equations reducible by e; re-push them."""
        keep = []
        repush = []
        for old in self.active:
            if old is e or old.chain is None:
                keep.append(old)
                continue
            red = None
            for (a, sidefn) in ((old.lhs, 0), (old.rhs, 1)):
                r = self._reduce_with(a, e)
                if r is not None:
                    red = (sidefn, r)
                    break
            if red is None:
                keep.append(old)
                continue
            sidefn, (new_side, st) = red
            if sidefn == 0:
                nl, nr = new_side, old.rhs
                chain = [(st[0], st[1], st[2], -st[3])] + old.chain
            else:
                nl, nr = old.lhs, new_side
                chain = old.chain + [st]
            repush.append((nl, nr, chain, "collapse(%d by %d)" % (old.id, e.id)))
        if repush:
            self.active = keep
            for (nl, nr, chain, origin) in repush:
                self.seen.discard(canon_eq(nl, nr))
                self.push(nl, nr, chain, origin)
        return len(repush)

    def _reduce_with(self, t, e):
        for pos, sub in positions(t):
            if sub[0] == "v":
                continue
            sm = term_mask(sub)
            ss = size(sub)
            for (l, r, d, lm, ls) in e.ori:
                if ls > ss or (lm & ~sm):
                    continue
                m = match(l, sub)
                if m is None:
                    continue
                rs = subst(r, m)
                if rs == sub or not kbo_gt(sub, rs):
                    continue
                return set_at(t, pos, rs), (pos, e.id, m, d)
        return None


def replay(comp, start, chain):
    t = start
    for (pos, eid, s, d) in chain:
        e = comp.eqs[eid]
        l, r = (e.lhs, e.rhs) if d > 0 else (e.rhs, e.lhs)
        want = subst(l, s)
        got = get_at(t, pos)
        if got != want:
            raise AssertionError("replay mismatch at %s: have %s want %s"
                                 % (pos, tstr(got), tstr(want)))
        t = set_at(t, pos, subst(r, s))
    return t
