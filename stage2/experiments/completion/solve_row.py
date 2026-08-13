"""Row-agnostic: ordered KB completion with proof recording -> Lean lemma_chain.

    python solve_row.py <row_id> [budget_secs] [max_size] [max_active]

Reads the row from the benchmark catalog, parses eq1/eq2, completes from eq1
alone, tries to join eq2's two sides under the current rewrite system after
every processed equation, renders the joining chain as a Lean certificate and
kernel-verifies it with the repo's independent oracle.
"""
from __future__ import annotations

import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
# Derived, not hardcoded: this tool spent its first life in a per-session OS
# temp directory with an absolute path baked in, which is why the pipeline
# CLAUDE.md called "the durable result" was reproducible on exactly one machine.
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "stage2", "tests"))
sys.path.insert(0, os.path.join(REPO, "stage2", "solver"))
sys.path.insert(0, os.path.join(REPO, "stage2", "experiments"))
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

from kb2 import Completion, F, V, replay, tstr  # noqa: E402
from render import Renderer  # noqa: E402

OP = "\u25c7"


# ---------------------------------------------------------------- parsing
def tokenize(text):
    return re.findall(r"[a-z]|\(|\)|%s|\*" % OP, text)


def parse_side(text):
    """Left-assoc-free: the benchmark text is fully parenthesised except at top."""
    toks = tokenize(text)
    pos = [0]

    def atom():
        t = toks[pos[0]]
        if t == "(":
            pos[0] += 1
            e = expr()
            assert toks[pos[0]] == ")", toks[pos[0]]
            pos[0] += 1
            return e
        pos[0] += 1
        return V(t)

    def expr():
        left = atom()
        while pos[0] < len(toks) and toks[pos[0]] in (OP, "*"):
            pos[0] += 1
            right = atom()
            left = F(left, right)
        return left

    e = expr()
    assert pos[0] == len(toks), (text, pos[0], len(toks))
    return e


def parse_eq(text):
    l, r = text.split("=")
    return parse_side(l.strip()), parse_side(r.strip())


def var_order(text):
    """The judge's binder order: first appearance in the equation text."""
    seen, out = set(), []
    for v in re.findall(r"\b([a-z])\b", text):
        if v not in seen:
            seen.add(v)
            out.append(v)
    return out


# ---------------------------------------------------------------- catalog
def load_row(rid):
    from judge_rows import all_problems
    return all_problems()[rid]


# ---------------------------------------------------------------- driver
def joinable(comp, lhs, rhs):
    nl, sl = comp.normalize(lhs)
    nr, sr = comp.normalize(rhs)
    if nl != nr:
        return None
    return sl + [(p, i, s, -d) for (p, i, s, d) in reversed(sr)]


def run(eq1, eq2, budget=200.0, max_size=44, max_active=800, verbose=True,
        report_every=0.0):
    e1l, e1r = eq1
    e2l, e2r = eq2
    comp = Completion([(e1l, e1r)], max_size=max_size, max_active=max_active)
    t0 = time.time()
    for a in list(comp.active):
        for b in list(comp.active):
            for (l, r, ch) in comp.crit_pairs(a, b):
                comp.push(l, r, ch, "cp")
    j = joinable(comp, e2l, e2r)
    if j is not None:
        return comp, j, 0
    n = 0
    last = t0
    while time.time() - t0 < budget:
        e = comp.step()
        if e is None:
            if verbose:
                print("SATURATED after %d equations, %.1fs (passive empty)"
                      % (n, time.time() - t0), flush=True)
            break
        n += 1
        assert replay(comp, e.lhs, e.chain) == e.rhs
        j = joinable(comp, e2l, e2r)
        if j is not None:
            assert replay(comp, e2l, j) == e2r
            if verbose:
                print("GOAL JOINABLE after %d equations, %.1fs"
                      % (n, time.time() - t0), flush=True)
            return comp, j, n
        comp.interreduce(e)
        for other in list(comp.active):
            for (l, r, ch) in comp.crit_pairs(e, other):
                comp.push(l, r, ch, "cp")
            if other.id != e.id:
                for (l, r, ch) in comp.crit_pairs(other, e):
                    comp.push(l, r, ch, "cp")
        if report_every and time.time() - last > report_every:
            last = time.time()
            print("  [%.0fs] processed=%d active=%d passive=%d smallest_active=%s"
                  % (time.time() - t0, n, len(comp.active), len(comp.passive),
                     min((e2.weight for e2 in comp.active), default=-1)),
                  flush=True)
    return comp, None, n


def build_cert(comp, goal_chain, eq1_text, eq2_text, eq2_terms):
    eqs = {k: (v.lhs, v.rhs, v.chain, v.origin) for k, v in comp.eqs.items()}
    r = Renderer(eqs, axiom_id=0, eq1_vars=var_order(eq1_text))
    ids = r.order(goal_chain)
    code = r.build(eq2_terms[0], eq2_terms[1], goal_chain, var_order(eq2_text))
    return code, ids, eqs


def verify(code, eq1_text, eq2_text):
    import oracles
    import solver as S
    eq1 = S.parse_equation(eq1_text)
    eq2 = S.parse_equation(eq2_text)
    oracles.check_no_banned_tactics(code)
    shape = oracles.classify_true_certificate(code)
    oracles.check_true_lemma_chain_certificate(code, eq1, eq2)
    return shape


def main():
    rid = sys.argv[1]
    budget = float(sys.argv[2]) if len(sys.argv) > 2 else 200.0
    max_size = int(sys.argv[3]) if len(sys.argv) > 3 else 44
    max_active = int(sys.argv[4]) if len(sys.argv) > 4 else 800
    row = load_row(rid)
    t1, t2 = row["equation1"], row["equation2"]
    print("%s\n  eq1: %s\n  eq2: %s\n  max_size=%d max_active=%d budget=%.0fs"
          % (rid, t1, t2, max_size, max_active, budget), flush=True)
    eq1, eq2 = parse_eq(t1), parse_eq(t2)
    comp, chain, n = run(eq1, eq2, budget, max_size, max_active,
                         report_every=20.0)
    if chain is None:
        print("NO PROOF: processed=%d active=%d passive=%d"
              % (n, len(comp.active), len(comp.passive)))
        for e in sorted(comp.active, key=lambda e: e.weight)[:40]:
            print("   %s" % e)
        return 1
    code, ids, eqs = build_cert(comp, chain, t1, t2, eq2)
    outdir = os.path.join(HERE, rid)
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "%s_cert.lean" % rid)
    open(path, "w", encoding="utf-8", newline="\n").write(code)
    print("lemmas: %d %s" % (len(ids), ids))
    for eid in ids:
        lhs, rhs, ch, o = eqs[eid]
        print("   E%-4d %s = %s   (%d steps, %s)"
              % (eid, tstr(lhs), tstr(rhs), len(ch), o))
    print("bytes: %d -> %s" % (len(code.encode("utf-8")), path))
    print("shape:", verify(code, t1, t2), "KERNEL OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
