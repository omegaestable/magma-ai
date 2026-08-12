"""Diagnose egg extraction size on the open frontier.

Why this exists: `normal_0491` is *proved* by the e-graph in seconds, but the
extracted proof renders at ~135 KB against the judge's 50 KB cap, so the route
drops it. Extraction currently minimises STEP COUNT; the rendered bytes are
dominated by the one-hole context term each step re-renders in full.

This probe captures the shortened step list (by monkeypatching the renderer, so
`solver.py` needs no debug hooks) and reports, per row and per target:

    steps, flat rendered bytes, and the max/mean context size

Usage:
    python stage2/experiments/egg_bytes_probe.py --ids normal_0491 --target goal
    python stage2/experiments/egg_bytes_probe.py --open --target collapse
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "stage2" / "solver"))

import solver as S  # noqa: E402

PROBLEMS_DIR = REPO_ROOT / "data" / "stage2_official_problems"
HF_DIR = REPO_ROOT / "data" / "hf_cache"

SET_FILES = [
    PROBLEMS_DIR / "normal.jsonl",
    PROBLEMS_DIR / "hard1.jsonl",
    PROBLEMS_DIR / "hard2.jsonl",
    PROBLEMS_DIR / "hard3.jsonl",
    HF_DIR / "evaluation_normal.jsonl",
    HF_DIR / "evaluation_hard.jsonl",
    HF_DIR / "evaluation_extra_hard.jsonl",
    HF_DIR / "evaluation_order5.jsonl",
]

# Rows unsolved at `fast` tier, measured 2026-08-11
# (`stage2/results/audit-2026-08-11{,-hf}.json`). This is a *diagnostic* list for
# the probes below — regenerate it from the newest audit rather than trusting it,
# because a stale frontier list is how a probe reports on rows that already work.
#     python -c "import json;print(sorted(r['id'] for f in
#       ['stage2/results/audit-2026-08-11.json',
#        'stage2/results/audit-2026-08-11-hf.json']
#       for p in json.load(open(f,encoding='utf-8'))['sets'].values()
#       for r in p['rows'] if r['status']!='solved'))"
OPEN_ROWS = (
    # official (5)
    "hard1_0062", "hard2_0073", "hard2_0123", "hard3_0214", "hard3_0314",
    # HF mirrors (6)
    "evaluation_hard_0116", "evaluation_hard_0196",
    "evaluation_order5_0014", "evaluation_order5_0040",
    "evaluation_order5_0042", "evaluation_order5_0164",
)


def load_rows() -> dict[str, dict]:
    rows: dict[str, dict] = {}
    for path in SET_FILES:
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            rows[str(row.get("id", ""))] = row
    return rows


def capture_steps(eq1: dict, eq2: dict, budget: float):
    """Run the real saturation loop, capturing every extraction stage.

    Stages are recorded separately because "no certificate" has four very
    different causes: classes never merged, `explain` raised, the shortener
    rejected a step, or the render exceeded the byte cap.
    """
    captured: dict = {}
    orig_render = S._egg_render_steps
    orig_explain = S._EggProver.explain
    orig_shorten = S._egg_shorten_steps

    def render_spy(start, target, steps, lhs_p, rhs_p, eq1_vars, goal_vars):
        captured["args"] = (start, target, list(steps), lhs_p, rhs_p,
                            list(eq1_vars), list(goal_vars))
        return orig_render(start, target, steps, lhs_p, rhs_p, eq1_vars, goal_vars)

    def explain_spy(self, s, t, **kw):
        try:
            out = orig_explain(self, s, t, **kw)
        except Exception as exc:  # noqa: BLE001
            if not kw.get("depth"):
                captured["explain_error"] = f"{type(exc).__name__}: {exc}"
            raise
        if not kw.get("depth"):
            captured["raw_steps"] = len(out)
        return out

    def shorten_spy(start, steps, lhs_p, rhs_p):
        out = orig_shorten(start, steps, lhs_p, rhs_p)
        captured.setdefault("shorten_calls", []).append(
            None if out is None else len(out))
        return out

    S._egg_render_steps = render_spy
    S._EggProver.explain = explain_spy
    S._egg_shorten_steps = shorten_spy
    try:
        rendered = S.egg_saturate_prove(eq1, eq2, time_budget=budget)
    finally:
        S._egg_render_steps = orig_render
        S._EggProver.explain = orig_explain
        S._egg_shorten_steps = orig_shorten
    return rendered, captured


def flat_bytes(args) -> tuple[int, list[int]]:
    """Bytes the current flat renderer would emit, plus per-step context sizes."""
    start, target, steps, lhs_p, rhs_p, eq1_vars, goal_vars = args
    binder = next((b for b in S._EGG_BINDER_CANDIDATES if b not in goal_vars), "t")
    cur = start
    total = 0
    ctx_sizes: list[int] = []
    for pos, subst, symm in steps:
        to_t = S._egg_substitute(lhs_p if symm else rhs_p, subst)
        args_txt = " ".join(S.term_to_lean(subst[v]) for v in eq1_vars)
        inner = f"(h {args_txt})" if args_txt else "(h)"
        if symm:
            inner = f"{inner}.symm"
        if pos:
            ctx = S._egg_replace_at(cur, pos, ("var", binder))
            step_proof = f"congrArg (fun {binder} => {S.term_to_lean(ctx)}) ({inner})"
        else:
            step_proof = inner
        ctx_sizes.append(len(step_proof.encode("utf-8")))
        total += len(step_proof.encode("utf-8")) + 10
        cur = S._egg_replace_at(cur, pos, to_t)
    return total, ctx_sizes


def describe(row_id: str, row: dict, target: str, budget: float) -> dict:
    eq1 = S.parse_equation(str(row["equation1"]))
    if target == "goal":
        eq2 = S.parse_equation(str(row["equation2"]))
    else:
        eq2 = S.lemma_goal({"collapse": "a = b",
                            "left_projection": "a ◇ b = a",
                            "right_projection": "a ◇ b = b"}[target])
    rendered, cap = capture_steps(eq1, eq2, budget)
    args = cap.get("args")
    out: dict = {"id": row_id, "target": target,
                 "merged": "raw_steps" in cap or "explain_error" in cap,
                 "rendered": rendered is not None}
    for key in ("raw_steps", "explain_error", "shorten_calls"):
        if key in cap:
            out[key] = cap[key]
    if args is None:
        return out
    total, ctx = flat_bytes(args)
    out.update(steps=len(args[2]), flat_bytes=total,
               max_step_bytes=max(ctx) if ctx else 0,
               mean_step_bytes=round(sum(ctx) / len(ctx)) if ctx else 0)
    if rendered is not None:
        out["rendered_bytes"] = len(rendered.encode("utf-8"))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", default="")
    ap.add_argument("--open", action="store_true")
    ap.add_argument("--target", default="goal",
                    choices=("goal", "collapse", "left_projection",
                             "right_projection"))
    ap.add_argument("--budget", type=float, default=40.0)
    ap.add_argument("--effort", default="fast")
    args = ap.parse_args()

    S.set_effort(args.effort)
    rows = load_rows()
    ids = [i for i in args.ids.split(",") if i.strip()]
    if args.open:
        ids = list(OPEN_ROWS)
    for row_id in ids:
        row = rows.get(row_id)
        if row is None:
            print(json.dumps({"id": row_id, "error": "not found"}))
            continue
        try:
            print(json.dumps(describe(row_id, row, args.target, args.budget)))
        except Exception as exc:  # noqa: BLE001
            print(json.dumps({"id": row_id, "error": f"{type(exc).__name__}: {exc}"}))
        sys.stdout.flush()


if __name__ == "__main__":
    main()
