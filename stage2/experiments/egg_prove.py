"""Proof-producing ground equality saturation ("egg with receipts").

Extends the validated saturation mechanism (`egg_saturation.py`, results:
`stage2/results/2026-07-23-spotcheck-batches-and-egg-frontier-study.md`) with
term-level provenance and explanation extraction, producing proof expressions
in the exact grammar the offline kernel checks:

    h t1 .. tk | (E).symm | (E1).trans (E2) | congrArg (fun v => CTX) (E)

Soundness story: every explanation is flattened into single-position rewrite
steps, and the renderer REPLAYS each step syntactically on the concrete term
(substituting eq1 at the recorded position and checking the subterm matches)
before emitting anything. A bug anywhere in the e-graph or explanation code
makes the replay fail closed (return None); it cannot emit a wrong proof.
The offline kernel re-verifies independently; the Lean judge is final.

Provenance model
----------------
- every concrete ground term ever added is registered with its e-class;
- a *proof forest* over terms carries one edge per class merge:
  * rule edge  (a, b): a = b is exactly `h σ` at the root (a = eq1.lhs[σ],
    b = eq1.rhs[σ]); traversing it backwards emits `.symm`;
  * congr edge (a, b): a = (a1◇a2), b = (b1◇b2) with a1~b1, a2~b2 merged
    earlier — explained recursively and lifted through the position;
- explanation = unique tree path between two terms (the forest gains exactly
  one edge per successful class merge, so it stays a forest), congr edges
  expanded recursively, yielding root-level single-position steps.
"""
from __future__ import annotations

import time
from itertools import product
from typing import Any

Term = tuple

# ---------------------------------------------------------------------------
# term helpers (standalone; mirror solver.py's conventions)
# ---------------------------------------------------------------------------

def term_size(t: Term) -> int:
    if t[0] == "var":
        return 1
    return term_size(t[1]) + term_size(t[2]) + 1


def term_to_lean(term: Term) -> str:
    if term[0] == "var":
        return str(term[1])
    return f"({term_to_lean(term[1])} ◇ {term_to_lean(term[2])})"


def substitute(term: Term, subst: dict[str, Term]) -> Term:
    if term[0] == "var":
        return subst[term[1]]
    return ("op", substitute(term[1], subst), substitute(term[2], subst))


def subterms(t: Term, acc: list[Term]) -> list[Term]:
    acc.append(t)
    if t[0] == "op":
        subterms(t[1], acc)
        subterms(t[2], acc)
    return acc


def pattern_vars(t: Term, acc: set[str] | None = None) -> set[str]:
    if acc is None:
        acc = set()
    if t[0] == "var":
        acc.add(t[1])
    else:
        pattern_vars(t[1], acc)
        pattern_vars(t[2], acc)
    return acc


def subterm_at(t: Term, pos: tuple[str, ...]) -> Term:
    for step in pos:
        t = t[1] if step == "L" else t[2]
    return t


def replace_at(t: Term, pos: tuple[str, ...], new: Term) -> Term:
    if not pos:
        return new
    if pos[0] == "L":
        return ("op", replace_at(t[1], pos[1:], new), t[2])
    return ("op", t[1], replace_at(t[2], pos[1:], new))


def upper_patterns(eq1: dict[str, Any]) -> tuple[Term, Term, list[str]]:
    """eq1 with vars renamed to uppercase so they never collide with goal
    variables (which are lowercase single letters in this corpus)."""
    def walk(t: Term) -> Term:
        if t[0] == "var":
            return ("var", t[1].upper())
        return ("op", walk(t[1]), walk(t[2]))
    return walk(eq1["lhs"]), walk(eq1["rhs"]), [v.upper() for v in eq1["variables"]]


# ---------------------------------------------------------------------------
# proof-producing e-graph
# ---------------------------------------------------------------------------

class ProvenanceError(Exception):
    pass


# A step is (pos, subst, symm): rewrite subterm at pos, which must equal
# eq1.lhs[subst] (symm=False) or eq1.rhs[subst] (symm=True), into the other
# side, justified by `h subst` (plus .symm when symm=True).
Step = tuple[tuple, dict, bool]

DEBUG = False


class EggProver:
    def __init__(self) -> None:
        self.parent: list[int] = []
        self.size_rep: list[int] = []          # min size seen per class (v2 semantics)
        self.enodes: dict[tuple, int] = {}
        self.witness: dict[tuple, Term] = {}   # enode key -> founding term
        self.term_class: dict[Term, int] = {}
        self.class_repr: dict[int, Term] = {}  # smallest registered term
        # proof forest: term -> [(other, reason, flipped)]
        # reason ("rule", subst_items): recorded edge (a, b) satisfies
        #   a = eq1.lhs[subst], b = eq1.rhs[subst]; flipped=True on the
        #   reverse adjacency entry.
        # reason ("congr",): symmetric.
        self.adj: dict[Term, list[tuple[Term, tuple, bool]]] = {}

    # -- union-find --------------------------------------------------------

    def find(self, a: int) -> int:
        while self.parent[a] != a:
            self.parent[a] = self.parent[self.parent[a]]
            a = self.parent[a]
        return a

    def canon(self, node: tuple) -> tuple:
        if node[0] == "op":
            return ("op", self.find(node[1]), self.find(node[2]))
        return node

    def _register(self, t: Term, cid: int) -> None:
        if t not in self.term_class:
            self.term_class[t] = cid
        root = self.find(cid)
        best = self.class_repr.get(root)
        if best is None or term_size(t) < term_size(best):
            self.class_repr[root] = t

    def _add_edge(self, a: Term, b: Term, reason: tuple) -> None:
        self.adj.setdefault(a, []).append((b, reason, False))
        self.adj.setdefault(b, []).append((a, reason, True))

    def add_term(self, t: Term) -> int:
        # Fast path: a registered term's class is authoritative. Rebuilding a
        # known term bottom-up between rebuilds would look it up under the
        # CURRENT canonical key while the hashcons still holds the stale key,
        # spawning a duplicate class (the bug that broke saturation parity
        # with egg_saturation v2).
        known = self.term_class.get(t)
        if known is not None:
            return self.find(known)
        if t[0] == "var":
            key: tuple = t
            sz = 1
        else:
            a = self.add_term(t[1])
            b = self.add_term(t[2])
            key = ("op", self.find(a), self.find(b))
            sz = self.size_rep[self.find(a)] + self.size_rep[self.find(b)] + 1
        existing = self.enodes.get(key)
        if existing is not None:
            cid = self.find(existing)
            if sz < self.size_rep[cid]:
                self.size_rep[cid] = sz
            if t not in self.term_class:
                w = self.witness.get(key)
                if w is not None and w != t:
                    # same canonical enode => children pairwise equal already
                    self._add_edge(t, w, ("congr",))
            self._register(t, cid)
            return cid
        cid = len(self.parent)
        self.parent.append(cid)
        self.size_rep.append(sz)
        self.enodes[key] = cid
        self.witness[key] = t
        self._register(t, cid)
        return cid

    def merge_terms(self, a_term: Term, b_term: Term, reason: tuple) -> bool:
        a = self.find(self.term_class[a_term])
        b = self.find(self.term_class[b_term])
        if a_term != b_term:
            # record the edge even when the classes are already equal: a
            # redundant justification is an ALTERNATIVE path, and the BFS in
            # _tree_path picks the shortest — without these, explanations
            # wander the whole merge history (measured: 2,028 steps for a
            # row whose direct justification is a handful of rewrites).
            self._add_edge(a_term, b_term, reason)
        if a == b:
            return False
        self.parent[a] = b
        self.size_rep[b] = min(self.size_rep[b], self.size_rep[a])
        ra, rb = self.class_repr.get(a), self.class_repr.get(b)
        if ra is not None and (rb is None or term_size(ra) < term_size(rb)):
            self.class_repr[b] = ra
        return True

    def rebuild(self) -> None:
        changed = True
        while changed:
            changed = False
            fresh: dict[tuple, int] = {}
            fresh_wit: dict[tuple, Term] = {}
            for node, cid in self.enodes.items():
                node2 = self.canon(node)
                cid = self.find(cid)
                wit = self.witness.get(node)
                other = fresh.get(node2)
                if other is None:
                    fresh[node2] = cid
                    if wit is not None:
                        fresh_wit[node2] = wit
                elif self.find(other) != cid:
                    ow = fresh_wit.get(node2)
                    if wit is not None and ow is not None:
                        self.merge_terms(ow, wit, ("congr",))
                    else:  # no witnesses to justify: merge unexplained;
                        # any explanation crossing it will fail closed
                        self.parent[self.find(other)] = cid
                    changed = True
            self.enodes = fresh
            self.witness = fresh_wit

    def class_of(self, t: Term) -> int:
        return self.find(self.term_class[t])

    # -- explanation -------------------------------------------------------

    def _tree_path(self, s: Term, t: Term) -> list[tuple[Term, Term, tuple, bool]]:
        """Path s..t in the proof forest as (from, to, reason, flipped)."""
        if s == t:
            return []
        prev: dict[Term, tuple[Term, tuple, bool]] = {s: (s, (), False)}
        queue = [s]
        while queue:
            nxt: list[Term] = []
            for u in queue:
                for v, reason, flipped in self.adj.get(u, ()):
                    if v in prev:
                        continue
                    prev[v] = (u, reason, flipped)
                    if v == t:
                        path: list[tuple[Term, Term, tuple, bool]] = []
                        cur = t
                        while cur != s:
                            p, r, f = prev[cur]
                            path.append((p, cur, r, f))
                            cur = p
                        path.reverse()
                        return path
                    nxt.append(v)
            queue = nxt
        raise ProvenanceError("terms not connected in proof forest")

    def explain(self, s: Term, t: Term, *, depth: int = 0,
                budget: list[int] | None = None) -> list[Step]:
        """Flat steps (pos, subst, symm) rewriting s into t."""
        if depth > 300:
            raise ProvenanceError("explanation recursion too deep")
        if budget is None:
            budget = [200000]
        steps: list[Step] = []
        cur = s
        for a, b, reason, flipped in self._tree_path(s, t):
            if a != cur:
                raise ProvenanceError("path does not chain")
            budget[0] -= 1
            if budget[0] < 0:
                raise ProvenanceError("explanation too long")
            if reason and reason[0] == "rule":
                _, subst_items = reason
                # recorded edge (x, y) has x = eq1.lhs[σ], y = eq1.rhs[σ].
                # flipped=True means we walk y -> x, i.e. rhs -> lhs => symm.
                steps.append(((), dict(subst_items), flipped))
                cur = b
            elif reason and reason[0] == "congr":
                if a[0] != "op" or b[0] != "op":
                    raise ProvenanceError("congr edge on non-op terms")
                for sub in self.explain(a[1], b[1], depth=depth + 1, budget=budget):
                    steps.append((("L",) + sub[0], sub[1], sub[2]))
                for sub in self.explain(a[2], b[2], depth=depth + 1, budget=budget):
                    steps.append((("R",) + sub[0], sub[1], sub[2]))
                cur = b
            else:
                raise ProvenanceError(f"unknown reason {reason!r}")
        if cur != t:
            raise ProvenanceError("explanation does not reach target")
        return steps


def match_pattern(pattern: Term, term: Term,
                  subst: dict[str, Term]) -> dict[str, Term] | None:
    """Match `term` against `pattern` (uppercase vars bind), extending subst."""
    if pattern[0] == "var":
        bound = subst.get(pattern[1])
        if bound is None:
            s2 = dict(subst)
            s2[pattern[1]] = term
            return s2
        return subst if bound == term else None
    if term[0] != "op":
        return None
    s1 = match_pattern(pattern[1], term[1], subst)
    if s1 is None:
        return None
    return match_pattern(pattern[2], term[2], s1)


def _diff_pos(a: Term, b: Term) -> tuple[str, ...] | None:
    """Position of the single differing subtree, or None if a == b or the
    difference is not confined to one subtree."""
    if a == b:
        return None
    if a[0] == "op" and b[0] == "op":
        left = a[1] != b[1]
        right = a[2] != b[2]
        if left and not right:
            sub = _diff_pos(a[1], b[1])
            return ("L",) + sub if sub is not None else ("L",)
        if right and not left:
            sub = _diff_pos(a[2], b[2])
            return ("R",) + sub if sub is not None else ("R",)
    return ()


def one_step_between(s: Term, t: Term, lhs_p: Term, rhs_p: Term) -> Step | None:
    """A single eq1 rewrite turning s into t, if one exists at the diff root."""
    if s == t:
        return None
    pos = _diff_pos(s, t)
    if pos is None:
        return None
    sub_s = subterm_at(s, pos)
    sub_t = subterm_at(t, pos)
    for symm, (frm, to) in ((False, (lhs_p, rhs_p)), (True, (rhs_p, lhs_p))):
        subst = match_pattern(frm, sub_s, {})
        if subst is None:
            continue
        # every rhs var must be bound for the instance to be checkable; free
        # vars only appear going lhs->rhs of an expanding rule, and then the
        # target fixes them
        subst2 = match_pattern(to, sub_t, dict(subst))
        if subst2 is not None and substitute(frm, subst2) == sub_s:
            return (pos, subst2, symm)
    return None


def bridge_steps(start: Term, steps: list[Step],
                 lhs_p: Term, rhs_p: Term) -> list[Step] | None:
    """Greedy shortcutting: from each state jump to the FARTHEST later state
    reachable by a single eq1 rewrite. Sound because every emitted step is a
    checked eq1 instance; render_steps replays everything again anyway."""
    states: list[Term] = [start]
    cur = start
    for pos, subst, symm in steps:
        to_t = substitute(lhs_p if symm else rhs_p, subst)
        cur = replace_at(cur, pos, to_t)
        states.append(cur)
    out: list[Step] = []
    i = 0
    while i < len(states) - 1:
        jumped = False
        for j in range(len(states) - 1, i, -1):
            if j == i + 1:
                break
            step = one_step_between(states[i], states[j], lhs_p, rhs_p)
            if step is not None:
                out.append(step)
                i = j
                jumped = True
                break
        if not jumped:
            out.append(steps[i] if len(steps) == len(states) - 1 else None)
            if out[-1] is None:
                return None
            i += 1
    return out


def shorten_steps(start: Term, steps: list[Step],
                  lhs_p: Term, rhs_p: Term) -> list[Step] | None:
    """Replay the chain and cut every cycle in the term-state sequence.

    Explanation walks through the merge history revisit the same term many
    times (measured: a 2,028-step explanation for a goal whose direct chain
    is a handful of rewrites). Whenever a state recurs, everything between
    the two visits is provably a no-op and is dropped. Also serves as a full
    replay validation of the incoming steps."""
    kept: list[Step] = []
    states: list[Term] = [start]
    index: dict[Term, int] = {start: 0}
    cur = start
    for pos, subst, symm in steps:
        from_t = substitute(rhs_p if symm else lhs_p, subst)
        try:
            if subterm_at(cur, pos) != from_t:
                return None
        except (IndexError, TypeError):
            return None
        to_t = substitute(lhs_p if symm else rhs_p, subst)
        nxt = replace_at(cur, pos, to_t)
        seen = index.get(nxt)
        if seen is not None:
            for t in states[seen + 1:]:
                index.pop(t, None)
            del kept[seen:]
            del states[seen + 1:]
        else:
            kept.append((pos, subst, symm))
            states.append(nxt)
            index[nxt] = len(states) - 1
        cur = nxt
    return kept


# ---------------------------------------------------------------------------
# rendering with replay self-check
# ---------------------------------------------------------------------------

_BINDER_CANDIDATES = ("t", "q", "p", "s", "r", "m", "n", "k")

# The production judge rejects code over 100_000 UTF-8 bytes as malformed —
# `judge.max_code_length` in vendor/stage2-official/pipeline/config.json, which
# pipeline/proxy.py passes into the judge. This comment used to name 50_000 and
# cite the 2026-07-23 ladder ("a 59,820-byte cert bounced"); that ladder ran
# through judge_rows.py, which called verify_answer() with no config and so
# measured judge/verify.py's no-config *fallback* against itself. Re-tested
# 2026-08-13 with only the cap varying: the same 60,015-byte certificate is
# CODE_TOO_LONG at 50_000 and accepted at 100_000. Budget in BYTES, leaving
# room for the certificate wrapper.
MAX_PROOF_BYTES = 49_000


def _balanced_trans(parts: list[str]) -> str:
    """Compose step proofs with balanced .trans nesting (depth ~log n), so
    neither the offline kernel's recursive evaluator nor Lean's elaborator
    sees a nesting as deep as the step count."""
    if len(parts) == 1:
        return parts[0]
    mid = len(parts) // 2
    left = _balanced_trans(parts[:mid])
    right = _balanced_trans(parts[mid:])
    return f"({left}).trans ({right})"


def render_steps(start: Term, target: Term, steps: list[Step],
                 lhs_p: Term, rhs_p: Term, eq1_vars: list[str],
                 goal_vars: list[str]) -> str | None:
    """Render flat steps into one kernel-grammar proof expression.

    Replays every step syntactically: the subterm at the recorded position
    must equal the instantiated eq1 side. Any mismatch returns None.
    """
    binder = next((b for b in _BINDER_CANDIDATES if b not in goal_vars), None)
    if binder is None:
        return None
    cur = start
    parts: list[str] = []
    total = 0
    for pos, subst, symm in steps:
        from_t = substitute(rhs_p if symm else lhs_p, subst)
        to_t = substitute(lhs_p if symm else rhs_p, subst)
        try:
            if subterm_at(cur, pos) != from_t:
                if DEBUG:
                    print(f"[egg debug] replay mismatch at step {len(parts)}: "
                          f"pos={pos} want={term_to_lean(from_t)} "
                          f"have={term_to_lean(subterm_at(cur, pos))}")
                return None
        except (IndexError, TypeError):
            return None
        args = " ".join(term_to_lean(subst[v]) for v in eq1_vars)
        inner = f"(h {args})" if args else "(h)"
        if symm:
            inner = f"{inner}.symm"
        if pos:
            ctx = replace_at(cur, pos, ("var", binder))
            step_proof = f"congrArg (fun {binder} => {term_to_lean(ctx)}) ({inner})"
        else:
            step_proof = inner
        cur = replace_at(cur, pos, to_t)
        parts.append(step_proof)
        total += len(step_proof.encode("utf-8")) + 10
        if total > MAX_PROOF_BYTES:
            if DEBUG:
                print(f"[egg debug] proof too large (> {MAX_PROOF_BYTES} bytes)")
            return None
    if cur != target:
        if DEBUG:
            print(f"[egg debug] replay ended at {term_to_lean(cur)} "
                  f"!= target {term_to_lean(target)}")
        return None
    if not parts:
        return "rfl"
    return _balanced_trans(parts)


# ---------------------------------------------------------------------------
# saturation with provenance
# ---------------------------------------------------------------------------

def ematch(egg: EggProver, pattern: Term, cid: int, subst: dict,
           by_class: dict[int, list[tuple]]):
    cid = egg.find(cid)
    if pattern[0] == "var":
        v = pattern[1]
        bound = subst.get(v)
        if bound is not None:
            if egg.find(bound) == cid:
                yield subst
            return
        s2 = dict(subst)
        s2[v] = cid
        yield s2
        return
    for node in by_class.get(cid, ()):
        if node[0] != "op":
            continue
        for s1 in ematch(egg, pattern[1], node[1], subst, by_class):
            yield from ematch(egg, pattern[2], node[2], s1, by_class)


def saturate_prove(eq1: dict[str, Any], eq2: dict[str, Any], *,
                   rounds: int = 30, time_budget: float = 15.0,
                   pool_max: int = 36, expand_cap: int = 900,
                   max_enodes: int = 60000,
                   deadline_check=None) -> str | None:
    """Return a kernel-grammar proof expression proving eq2 from eq1, or None.

    `deadline_check`: optional zero-arg callable returning True when the
    caller's deadline/memory guard has tripped (solver integration point).
    """
    lhs_p, rhs_p, eq1_vars = upper_patterns(eq1)
    goal_vars = list(eq2["variables"])
    L, R = eq2["lhs"], eq2["rhs"]

    egg = EggProver()
    pool: list[int] = []
    for t in subterms(L, []) + subterms(R, []):
        cid = egg.add_term(t)
        if cid not in pool:
            pool.append(cid)

    orientations = []
    for symm, (a, b) in ((False, (lhs_p, rhs_p)), (True, (rhs_p, lhs_p))):
        free = sorted(pattern_vars(b) - pattern_vars(a))
        orientations.append((a, b, free, symm))

    deadline = time.monotonic() + time_budget
    done: set = set()

    def expired() -> bool:
        if time.monotonic() > deadline:
            return True
        return bool(deadline_check and deadline_check())

    proved = egg.class_of(L) == egg.class_of(R)
    for rnd in range(rounds):
        if proved or expired() or len(egg.enodes) > max_enodes:
            break
        expand_targets = min(pool_max, 10 + 6 * rnd)
        free_pool = min(18, 8 + 2 * rnd)

        cur_pool = sorted({egg.find(c) for c in pool},
                          key=lambda c: egg.size_rep[c])
        pool = cur_pool[:pool_max]
        prods = []
        for p in pool[:expand_targets]:
            for q in pool[:expand_targets]:
                prods.append(egg.add_term(
                    ("op", egg.class_repr[egg.find(p)],
                     egg.class_repr[egg.find(q)])))
        for c in prods:
            c = egg.find(c)
            if c not in pool and len(pool) < pool_max:
                pool.append(c)

        by_class: dict[int, list[tuple]] = {}
        for node, cid in egg.enodes.items():
            by_class.setdefault(egg.find(cid), []).append(egg.canon(node))

        apps = []
        for oi, (a, b, free, symm) in enumerate(orientations):
            classes = pool[:expand_targets] if a[0] == "var" else list(by_class)
            for cid in classes:
                if expired():
                    break
                for subst in ematch(egg, a, cid, {}, by_class):
                    key = (oi, egg.find(cid),
                           tuple(sorted((v, egg.find(c)) for v, c in subst.items())))
                    if not free:
                        if key in done:
                            continue
                        apps.append((0, key, a, b, subst, symm))
                    else:
                        for combo in product(pool[:free_pool], repeat=len(free)):
                            key2 = key + (tuple(egg.find(c) for c in combo),)
                            if key2 in done:
                                continue
                            s2 = dict(subst)
                            s2.update(zip(free, combo))
                            cost = sum(egg.size_rep[egg.find(c)]
                                       for c in s2.values())
                            apps.append((cost, key2, a, b, s2, symm))
        apps.sort(key=lambda x: x[0])

        merged_any = False
        capped = False
        applied_now = 0
        for cost, key, lhs_pat, rhs_pat, subst_cls, symm in apps:
            if applied_now > expand_cap and cost > 0:
                capped = True
                break
            if expired() or len(egg.enodes) > max_enodes:
                capped = True
                break
            if key in done:
                continue
            done.add(key)
            applied_now += 1
            subst_terms = {v: egg.class_repr[egg.find(c)]
                           for v, c in subst_cls.items()}
            l_term = substitute(lhs_pat, subst_terms)
            r_term = substitute(rhs_pat, subst_terms)
            egg.add_term(l_term)
            egg.add_term(r_term)
            # normalize the rule edge to eq1 orientation: (lhs[σ], rhs[σ])
            if symm:
                edge = (r_term, l_term)
            else:
                edge = (l_term, r_term)
            subst_items = tuple(sorted(subst_terms.items()))
            if egg.merge_terms(edge[0], edge[1], ("rule", subst_items)):
                merged_any = True
            if egg.class_of(L) == egg.class_of(R):
                proved = True
                break
        egg.rebuild()
        if egg.class_of(L) == egg.class_of(R):
            proved = True
        if proved or (not merged_any and not capped):
            break

    if egg.class_of(L) != egg.class_of(R):
        if DEBUG:
            print(f"[egg debug] not saturated: enodes={len(egg.enodes)} "
                  f"terms={len(egg.term_class)}")
        return None
    try:
        steps = egg.explain(L, R)
    except (ProvenanceError, RecursionError) as exc:
        if DEBUG:
            print(f"[egg debug] explain failed: {exc}")
        return None
    shortened = shorten_steps(L, steps, lhs_p, rhs_p)
    if shortened is None:
        if DEBUG:
            print(f"[egg debug] shorten replay failed on {len(steps)} steps")
        return None
    # shorten+bridge to fixpoint: bridging creates new states, which open new
    # cycle cuts and new shortcuts
    for _ in range(4):
        before = len(shortened)
        bridged = bridge_steps(L, shortened, lhs_p, rhs_p)
        if bridged is None:
            break
        cut = shorten_steps(L, bridged, lhs_p, rhs_p)
        if cut is None:
            break
        shortened = cut
        if len(shortened) >= before:
            break
    if DEBUG:
        print(f"[egg debug] steps {len(steps)} -> {len(shortened)}")
    rendered = render_steps(L, R, shortened, lhs_p, rhs_p, eq1_vars, goal_vars)
    if DEBUG and rendered is None:
        print(f"[egg debug] render failed (replay mismatch), {len(steps)} steps")
    return rendered
