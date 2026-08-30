#!/usr/bin/env python3
"""Turn an `audit_corpus.py --file` report into a failure ledger and a summary.

The deep-sweep sessions (2026-08-20, 2026-08-25) all need the same three things
out of a batch, and until now each one rebuilt them by hand:

1. **A failure ledger** — every row that did not produce a verified certificate,
   carried with its equations, its ground-truth label where one exists, its
   wall clock, and structural features of the hypothesis. Four failure classes
   are kept apart because they mean completely different things:
   `oracle_failed` and `label_mismatch` are **soundness** events (a wrong or
   unverifiable certificate — the only kind that can cost points on a row the
   judge would otherwise accept), `crash` is a robustness event (rail 11), and
   `skip` is a plain coverage miss.
2. **A summary** — status counts, verdict split, route histogram, timing
   percentiles, and the clustering of failures by hypothesis law, which on
   order 4 has been the single most informative statistic (the top-5 eq1 ids
   accounted for 58% of misses across 20,000 rows).
3. **A row-id diff against a baseline report** (rail 2: diff by row id, never by
   total), classifying every change as lost / gained / verdict-flipped.

`--diagnose` re-runs each failed row with every engine wrapped in a timer, which
answers "where did the 450 seconds go" without a second guessing pass. It is a
separate opt-in step because it costs another full solve per failed row.

Usage:
    python stage2/experiments/sweep_report.py \
        --audit stage2/results/audit-etp-10k-2026-08-25.json \
        --batch stage2/results/etp-10k-2026-08-25.jsonl \
        --out-prefix stage2/results/etp-10k-2026-08-25
    python stage2/experiments/sweep_report.py --audit ... --batch ... \
        --out-prefix ... --diagnose --diagnose-budget 300
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "stage2" / "solver"))

import solver as S  # noqa: E402

# Engine call sites in `solve_problem_pass`, in the order it runs them. Every
# one is looked up from module globals at call time, so wrapping the attribute
# on the module instruments the real dispatch without touching the solver.
ENGINE_NAMES = (
    "completion_anchored_join_route",
    "distilled_product_constant_route",
    "distilled_spine_constancy_route",
    "find_counterexample",
    "constraint_countermodel",
    "completion_probe_route",
    "completion_helper_collapse_route",
    "egg_probe_route",
    "equational_closure_route",
    "deep_absorption_closure_route",
    "derived_cp_closure_route",
    "projection_bootstrap_route",
    "lemma_bootstrap_route",
    "lemma_chain_bootstrap_route",
    "egg_closure_route",
    "egg_collapse_route",
    "egg_priority_bootstrap_route",
    "egg_bootstrap_route",
    "egg_ladder_route",
    "completion_route",
    "narrow_grind_true_route",
    "local_model_counterexample",
    "constraint_countermodel_wide_domain",
)

SOUNDNESS_STATUSES = ("oracle_failed", "label_mismatch")
FAILURE_STATUSES = SOUNDNESS_STATUSES + ("crash", "skip")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_batch(path: Path | None) -> dict[str, dict]:
    if path is None:
        return {}
    text = path.read_text(encoding="utf-8")
    rows = ([json.loads(line) for line in text.splitlines() if line.strip()]
            if path.suffix == ".jsonl" else json.loads(text))
    return {str(row.get("id", "")): row for row in rows}


def audit_rows(report: dict) -> list[dict]:
    out: list[dict] = []
    for set_name, payload in report.get("sets", {}).items():
        for row in payload.get("rows", []):
            row = dict(row)
            row["set"] = set_name
            out.append(row)
    return out


def classify(row: dict) -> str:
    """Collapse an audit row to one status, keeping the soundness events
    distinct from the coverage ones."""
    if row.get("status") == "crash":
        return "crash"
    if row.get("status") != "solved":
        return "skip"
    oracle = row.get("oracle")
    if oracle == "VERDICT_CONTRADICTS_LABEL":
        return "label_mismatch"
    if oracle == "FAILED":
        return "oracle_failed"
    if oracle not in (None, "ok"):
        return "oracle_failed"
    return "solved"


def features(problem: dict) -> dict:
    """Structural facts about the hypothesis and goal, computed independently of
    whatever the solver decided, so the ledger stays readable if a route is
    renamed."""
    out: dict = {}
    try:
        eq1 = S.parse_equation(str(problem["equation1"]))
        eq2 = S.parse_equation(str(problem["equation2"]))
    except (KeyError, ValueError) as exc:
        return {"feature_error": str(exc)}
    for name, eq in (("eq1", eq1), ("eq2", eq2)):
        # ETP's "order" is the operation count. `term_size` counts NODES, and a
        # binary tree with k operations has 2k+1 of them, so the operation count
        # is (size - 1) // 2 per side -- not (size - 1), which double-counts.
        out[name + "_ops"] = sum((S.term_size(eq[side]) - 1) // 2
                                 for side in ("lhs", "rhs"))
        out[name + "_vars"] = len(eq["variables"])
        out[name + "_canonical"] = S.canonical_eq_text(eq)
    # `x = F(...)`: a bare variable alone on one side of the hypothesis. This is
    # the shape that dominated the order-4 failure frontier, and the same
    # predicate the wide-domain witness search uses to rule itself out. Read
    # through getattr so a rename in the solver costs a missing column here
    # rather than a crashed report.
    bare = getattr(S, "_eq1_has_bare_variable_side", None)
    if bare is not None:
        out["eq1_bare_variable_side"] = bool(bare(eq1))
        out["eq2_bare_variable_side"] = bool(bare(eq2))
    return out


def build_ledger(rows: list[dict], batch: dict[str, dict]) -> list[dict]:
    ledger: list[dict] = []
    for row in rows:
        status = classify(row)
        if status == "solved":
            continue
        problem = batch.get(row["id"], {})
        entry = {
            "id": row["id"],
            "set": row.get("set"),
            "failure": status,
            "seconds": row.get("seconds"),
            "eq1_id": problem.get("eq1_id"),
            "eq2_id": problem.get("eq2_id"),
            "equation1": problem.get("equation1"),
            "equation2": problem.get("equation2"),
        }
        if isinstance(problem.get("answer"), bool):
            entry["label"] = "true" if problem["answer"] else "false"
        for key in ("verdict", "route", "code_bytes", "cert_shape",
                    "nontrivial_models", "checks", "oracle", "oracle_error",
                    "error"):
            if row.get(key) is not None:
                entry[key] = row[key]
        if problem:
            entry.update(features(problem))
        ledger.append(entry)
    return ledger


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, int(round(pct / 100.0 * (len(ordered) - 1))))
    return ordered[index]


def summarize(rows: list[dict], ledger: list[dict]) -> dict:
    statuses = Counter(classify(row) for row in rows)
    solved = [row for row in rows if classify(row) == "solved"]
    seconds = [float(row.get("seconds") or 0.0) for row in rows]
    solved_seconds = [float(row.get("seconds") or 0.0) for row in solved]
    routes = Counter(str(row.get("route", "")) for row in solved)
    families = Counter(str(row.get("route", "")).split(":")[0:2][-1]
                       for row in solved)
    verdicts = Counter(str(row.get("verdict", "")) for row in solved)
    labels = Counter(str(row.get("label", "unlabelled")) for row in ledger)
    # A `true` verdict whose only evidence was a battery with no non-trivial
    # model is not evidence (CLAUDE.md, "oracle vacuous on the trivial magma").
    vacuous = sum(1 for row in solved
                  if row.get("verdict") == "true"
                  and row.get("nontrivial_models") == 0
                  and "proof_kernel_verified" not in (row.get("checks") or [])
                  and "collapse_kernel_verified" not in (row.get("checks") or [])
                  and "lemma_kernel_verified" not in (row.get("checks") or [])
                  and "lemma_chain_kernel_verified" not in (row.get("checks") or []))
    unsupported = sum(1 for row in solved
                      if "proof_kernel_skipped_unsupported_shape"
                      in (row.get("checks") or []))
    slowest = sorted(rows, key=lambda r: -(r.get("seconds") or 0.0))[:15]
    return {
        "rows": len(rows),
        "status_counts": dict(statuses),
        "solved": statuses.get("solved", 0),
        "solved_pct": round(100.0 * statuses.get("solved", 0) / max(1, len(rows)), 3),
        "soundness_events": sum(statuses.get(s, 0) for s in SOUNDNESS_STATUSES),
        "verdicts": dict(verdicts),
        "failure_labels": dict(labels),
        "unverified_true_certs": vacuous,
        "unsupported_cert_shapes": unsupported,
        "seconds_total": round(sum(seconds), 1),
        "seconds_mean": round(statistics.fmean(seconds), 3) if seconds else 0.0,
        "seconds_p50": round(percentile(solved_seconds, 50), 3),
        "seconds_p95": round(percentile(solved_seconds, 95), 3),
        "seconds_p99": round(percentile(solved_seconds, 99), 3),
        "seconds_max_solved": round(max(solved_seconds), 3) if solved_seconds else 0.0,
        "route_families": dict(families.most_common()),
        "routes": dict(routes.most_common(40)),
        "slowest": [{"id": r["id"], "seconds": r.get("seconds"),
                     "status": classify(r), "route": r.get("route")}
                    for r in slowest],
        "failure_eq1_clusters": dict(
            Counter(e.get("eq1_id") for e in ledger).most_common(15)),
        "failure_eq1_canonical_clusters": dict(
            Counter(e.get("eq1_canonical") for e in ledger).most_common(15)),
        "failure_shape_counts": {
            "eq1_bare_variable_side": sum(
                1 for e in ledger if e.get("eq1_bare_variable_side")),
            "eq1_vars": dict(Counter(e.get("eq1_vars") for e in ledger)),
            "eq1_ops": dict(Counter(e.get("eq1_ops") for e in ledger)),
        },
    }


def diff_against(rows: list[dict], baseline_report: dict) -> dict:
    base = {row["id"]: row for row in audit_rows(baseline_report)}
    now = {row["id"]: row for row in rows}
    common = sorted(set(base) & set(now))
    lost, gained, flips = [], [], []
    for row_id in common:
        was, is_ = classify(base[row_id]), classify(now[row_id])
        if was == "solved" and is_ != "solved":
            lost.append({"id": row_id, "now": is_})
        elif was != "solved" and is_ == "solved":
            gained.append({"id": row_id, "was": was,
                           "route": now[row_id].get("route")})
        elif was == "solved" and is_ == "solved":
            if base[row_id].get("verdict") != now[row_id].get("verdict"):
                flips.append({"id": row_id,
                              "was": base[row_id].get("verdict"),
                              "now": now[row_id].get("verdict")})
    return {"common_rows": len(common), "lost": lost, "gained": gained,
            "verdict_flips": flips, "only_in_baseline": len(set(base) - set(now)),
            "only_in_current": len(set(now) - set(base))}


def diagnose_row(problem: dict, effort: str, budget: float) -> dict:
    """Re-solve one row with every engine timed, so a skip says where its wall
    clock went instead of only how much of it there was."""
    trace: list[dict] = []
    originals = {}
    for name in ENGINE_NAMES:
        if not hasattr(S, name):
            continue
        originals[name] = getattr(S, name)

    def wrap(name, fn):
        def wrapper(*args, **kwargs):
            started = time.monotonic()
            try:
                result = fn(*args, **kwargs)
            except Exception as exc:  # noqa: BLE001
                trace.append({"engine": name,
                              "seconds": round(time.monotonic() - started, 3),
                              "outcome": f"raised {type(exc).__name__}"})
                raise
            trace.append({"engine": name,
                          "seconds": round(time.monotonic() - started, 3),
                          "outcome": "hit" if result is not None else "miss"})
            return result
        return wrapper

    for name, fn in originals.items():
        setattr(S, name, wrap(name, fn))
    S.set_effort(effort)
    S.set_hard_deadline(time.monotonic() + budget if budget > 0 else None)
    S.clear_term_caches()
    started = time.monotonic()
    outcome: dict = {}
    try:
        record = S.solve_problem(problem, false_time_budget=2.0)
        outcome["diagnose_status"] = "solved" if record else "skip"
        if record:
            outcome["diagnose_route"] = record["route"]
    except Exception as exc:  # noqa: BLE001
        outcome["diagnose_status"] = "crash"
        outcome["diagnose_error"] = f"{type(exc).__name__}: {exc}"
    finally:
        for name, fn in originals.items():
            setattr(S, name, fn)
        S.set_hard_deadline(None)
    outcome["diagnose_seconds"] = round(time.monotonic() - started, 3)
    spent = [t for t in trace if t["seconds"] >= 0.05]
    outcome["engine_trace"] = sorted(spent, key=lambda t: -t["seconds"])[:12]
    outcome["engine_seconds"] = {
        name: round(sum(t["seconds"] for t in trace if t["engine"] == name), 3)
        for name in {t["engine"] for t in trace}}
    return outcome


def render_markdown(name: str, summary: dict, ledger: list[dict],
                    diff: dict | None) -> str:
    lines = [f"# Sweep report: {name}", ""]
    lines.append(f"- rows: **{summary['rows']}**")
    lines.append(f"- solved: **{summary['solved']} ({summary['solved_pct']}%)**")
    lines.append(f"- soundness events (oracle failure / label mismatch): "
                 f"**{summary['soundness_events']}**")
    lines.append(f"- crashes: **{summary['status_counts'].get('crash', 0)}**")
    lines.append(f"- skips: **{summary['status_counts'].get('skip', 0)}**")
    lines.append(f"- solver-claimed verdicts: {summary['verdicts']}")
    lines.append(f"- TRUE certs with no independent verification "
                 f"(vacuous battery, unsupported shape): "
                 f"{summary['unverified_true_certs']}, "
                 f"{summary['unsupported_cert_shapes']}")
    lines.append(f"- seconds: total {summary['seconds_total']}, "
                 f"mean {summary['seconds_mean']}, p50 {summary['seconds_p50']}, "
                 f"p95 {summary['seconds_p95']}, p99 {summary['seconds_p99']}, "
                 f"slowest solved {summary['seconds_max_solved']}")
    lines.append("")
    lines.append("## Route families")
    lines.append("")
    for family, count in list(summary["route_families"].items())[:25]:
        lines.append(f"- `{family}`: {count}")
    lines.append("")
    lines.append("## Failure clustering by hypothesis law")
    lines.append("")
    for eq1_id, count in summary["failure_eq1_clusters"].items():
        if count > 1:
            lines.append(f"- eq1 `{eq1_id}`: {count} failures")
    lines.append("")
    lines.append(f"Failure shapes: {summary['failure_shape_counts']}")
    lines.append("")
    if diff is not None:
        lines.append("## Row-id diff against baseline")
        lines.append("")
        lines.append(f"- common rows: {diff['common_rows']}")
        lines.append(f"- lost: **{len(diff['lost'])}**, "
                     f"gained: **{len(diff['gained'])}**, "
                     f"verdict flips: **{len(diff['verdict_flips'])}**")
        lines.append("")
    lines.append("## Failure ledger")
    lines.append("")
    for entry in ledger[:80]:
        label = entry.get("label", "unlabelled")
        lines.append(f"- `{entry['id']}` [{entry['failure']}, label={label}, "
                     f"{entry.get('seconds')}s] eq1 `{entry.get('equation1')}` "
                     f"=> eq2 `{entry.get('equation2')}`")
        if entry.get("oracle_error"):
            lines.append(f"  - oracle: {entry['oracle_error']}")
        if entry.get("error"):
            lines.append(f"  - crash: {entry['error']}")
        if entry.get("engine_trace"):
            top = ", ".join(f"{t['engine']} {t['seconds']}s"
                            for t in entry["engine_trace"][:4])
            lines.append(f"  - engine time: {top}")
    if len(ledger) > 80:
        lines.append(f"- ... {len(ledger) - 80} more in the ledger jsonl")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit", type=Path, required=True, nargs="+",
                    help="one or more audit reports; several are merged into a "
                         "single report, which is how a multi-batch sweep "
                         "(10 x 10k) is read as one measurement")
    ap.add_argument("--batch", type=Path, default=[], nargs="*",
                    help="the problem jsonl(s) the audits ran on, for equation "
                         "text and ground-truth labels")
    ap.add_argument("--baseline", type=Path, default=None,
                    help="a prior audit report to diff by row id (rail 2)")
    ap.add_argument("--out-prefix", type=Path, required=True)
    ap.add_argument("--diagnose", action="store_true",
                    help="re-run every failed row with per-engine timing")
    ap.add_argument("--diagnose-budget", type=float, default=300.0)
    ap.add_argument("--diagnose-effort", default="fast",
                    choices=("fast", "standard", "deep"))
    ap.add_argument("--diagnose-limit", type=int, default=200)
    args = ap.parse_args()

    batch: dict[str, dict] = {}
    for path in args.batch:
        batch.update(load_batch(path))
    rows: list[dict] = []
    seen_ids: set[str] = set()
    for path in args.audit:
        for row in audit_rows(load_json(path)):
            # A row id repeated across reports would double-count; batches are
            # drawn disjoint by construction, so a collision is a mistake worth
            # seeing rather than silently averaging over.
            if row["id"] in seen_ids:
                print(f"[warn] duplicate row id across audits: {row['id']}")
                continue
            seen_ids.add(row["id"])
            rows.append(row)
    ledger = build_ledger(rows, batch)

    if args.diagnose:
        targets = [e for e in ledger if e.get("equation1")][: args.diagnose_limit]
        print(f"diagnosing {len(targets)} failed rows "
              f"(budget {args.diagnose_budget}s each)...", flush=True)
        for i, entry in enumerate(targets, 1):
            problem = batch.get(entry["id"], {})
            entry.update(diagnose_row(problem, args.diagnose_effort,
                                      args.diagnose_budget))
            print(f"  [{i}/{len(targets)}] {entry['id']}: "
                  f"{entry.get('diagnose_status')} in "
                  f"{entry.get('diagnose_seconds')}s", flush=True)

    summary = summarize(rows, ledger)
    diff = diff_against(rows, load_json(args.baseline)) if args.baseline else None
    if diff is not None:
        summary["baseline_diff"] = diff

    prefix = args.out_prefix
    prefix.parent.mkdir(parents=True, exist_ok=True)
    ledger_path = prefix.with_name(prefix.name + "-failures.jsonl")
    with ledger_path.open("w", encoding="utf-8") as handle:
        for entry in ledger:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    summary_path = prefix.with_name(prefix.name + "-summary.json")
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False),
                            encoding="utf-8")
    md_path = prefix.with_name(prefix.name + "-summary.md")
    md_path.write_text(render_markdown(prefix.name, summary, ledger, diff),
                       encoding="utf-8")

    print(f"rows {summary['rows']}, solved {summary['solved']} "
          f"({summary['solved_pct']}%), soundness events "
          f"{summary['soundness_events']}, crashes "
          f"{summary['status_counts'].get('crash', 0)}, skips "
          f"{summary['status_counts'].get('skip', 0)}")
    if diff is not None:
        print(f"baseline diff: {len(diff['lost'])} lost, "
              f"{len(diff['gained'])} gained, "
              f"{len(diff['verdict_flips'])} verdict flips over "
              f"{diff['common_rows']} common rows")
    print(f"wrote {ledger_path}\n      {summary_path}\n      {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
