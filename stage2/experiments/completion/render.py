"""Turn a completion proof DAG into a Lean lemma-chain certificate."""
from __future__ import annotations

import sys

import os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from kb2 import V, get_at, set_at, subst, tvars

OP = "\u25c7"
LETTERS = [c for c in "abcdefgijklmnopqrsuvw" if c != "t"]
PLACEHOLDER = "t"


def lean(t, top=True):
    if t[0] == "v":
        return t[1]
    s = "%s %s %s" % (lean(t[1], False), OP, lean(t[2], False))
    return s if top else "(" + s + ")"


def chain_vars(eq_lhs, eq_rhs, chain):
    vs = set(tvars(eq_lhs)) | set(tvars(eq_rhs))
    for (_pos, _eid, s, _d) in chain or []:
        for val in s.values():
            vs |= tvars(val)
    return vs


class Renderer:
    def __init__(self, eqs, axiom_id=0, eq1_vars=("x", "y", "z")):
        self.eqs = eqs          # id -> (lhs, rhs, chain, origin)
        self.axiom_id = axiom_id
        self.eq1_vars = list(eq1_vars)
        self.name = {}          # eq id -> lemma name
        self.binders = {}       # eq id -> list of original var names, in binder order
        self.varmap = {}        # eq id -> {origname: letter}

    # -- dependency walk ----------------------------------------------------
    def deps(self, chain, acc):
        for (_pos, eid, _s, _d) in chain:
            if eid == self.axiom_id or eid in acc:
                continue
            acc.add(eid)
            self.deps(self.eqs[eid][2], acc)
        return acc

    def order(self, goal_chain):
        need = self.deps(goal_chain, set())
        return sorted(need)

    # -- rendering ----------------------------------------------------------
    def assign(self, eid):
        lhs, rhs, chain, _o = self.eqs[eid]
        vs = sorted(chain_vars(lhs, rhs, chain))
        if len(vs) > len(LETTERS):
            raise RuntimeError("too many variables in eq %d: %d" % (eid, len(vs)))
        vm = {v: LETTERS[i] for i, v in enumerate(vs)}
        self.varmap[eid] = vm
        self.binders[eid] = vs
        return vm

    def render_step(self, cur_term, step, vm):
        pos, eid, s, d = step
        if eid == self.axiom_id:
            names = self.eq1_vars
            hyp = "h"
            order = names
        else:
            hyp = self.name[eid]
            order = self.binders[eid]
        args = []
        default = None
        for v in order:
            val = s.get(v)
            if val is None:
                if default is None:
                    default = V(sorted(vm.values())[0]) if vm else V("a")
                val = default
            else:
                val = subst(val, {k: V(x) for k, x in vm.items()})
            args.append(lean(val, top=False))
        base = "(%s %s)" % (hyp, " ".join(args))
        if d < 0:
            base = "(%s.symm)" % base
        if pos:
            ctx = set_at(cur_term, pos, V(PLACEHOLDER))
            ctx = subst(ctx, {k: V(x) for k, x in vm.items()})
            base = "(congrArg (fun %s => %s) %s)" % (PLACEHOLDER, lean(ctx), base)
        return base

    def render_chain(self, start, chain, vm, comp_eqs):
        exprs = []
        cur = start
        for step in chain:
            exprs.append(self.render_step(cur, step, vm))
            pos, eid, s, d = step
            lhs, rhs, _c, _o = comp_eqs[eid]
            l, r = (lhs, rhs) if d > 0 else (rhs, lhs)
            assert get_at(cur, pos) == subst(l, s), "chain mismatch"
            cur = set_at(cur, pos, subst(r, s))
        assert exprs, "empty chain"
        out = exprs[-1]
        for e in reversed(exprs[:-1]):
            out = "%s.trans (%s)" % (e, out)
        return out, cur

    def build(self, goal_lhs, goal_rhs, goal_chain, goal_vars):
        ids = self.order(goal_chain)
        for k, eid in enumerate(ids):
            self.name[eid] = "hlem%d" % k
            self.assign(eid)
        lines = ["import JudgeProblem", "", "def submission : Goal := by",
                 "  intro G _ h"]
        for eid in ids:
            lhs, rhs, chain, _o = self.eqs[eid]
            vm = self.varmap[eid]
            binders = [vm[v] for v in self.binders[eid]]
            expr, end = self.render_chain(lhs, chain, vm, self.eqs)
            assert end == rhs, "chain does not reach rhs for eq %d" % eid
            stmt = "%s = %s" % (lean(subst(lhs, {k: V(x) for k, x in vm.items()})),
                                lean(subst(rhs, {k: V(x) for k, x in vm.items()})))
            lines.append("  have %s : \u2200 %s : G, %s := by"
                         % (self.name[eid], " ".join(binders), stmt))
            lines.append("    intro %s" % " ".join(binders))
            lines.append("    exact %s" % expr)
        gvm = {v: v for v in goal_vars}
        expr, end = self.render_chain(goal_lhs, goal_chain, gvm, self.eqs)
        assert end == goal_rhs, "goal chain does not reach rhs"
        lines.append("  intro %s" % " ".join(goal_vars))
        lines.append("  exact %s" % expr)
        return "\n".join(lines) + "\n"
