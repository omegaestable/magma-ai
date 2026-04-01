#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

import jinja2

from v21_data_infrastructure import (
    build_equation_map,
    compute_witness_masks,
    implication_answer,
    load_equations,
    load_implications_csv,
    normalize_eq,
    witness_separates,
)
from v21_verify_structural_rules import (
    rule_AND,
    rule_C0,
    rule_LP,
    rule_RP,
    rule_XNOR,
    rule_XOR,
    rule_Z3A,
)

CSV_CERT_LABEL = {
    3: "matrix:implicit_proof_true",
    4: "matrix:explicit_proof_true",
    -3: "matrix:implicit_proof_false",
    -4: "matrix:explicit_proof_false",
}


def parse_render_fields(rendered: str):
    out = {"auto_result": None, "auto_reason": None, "copied_verdict": None, "copied_reason": None}
    for line in rendered.splitlines():
        s = line.strip()
        if s.startswith("AUTO-COMPUTED RESULT:") or s.startswith("AUTO-RESULT:"):
            out["auto_result"] = s.split(":", 1)[1].strip()
        elif s.startswith("AUTO-REASON:"):
            out["auto_reason"] = s.split(":", 1)[1].strip()
        elif s.startswith("VERDICT:") and out["copied_verdict"] is None:
            out["copied_verdict"] = s.split(":", 1)[1].strip()
        elif s.startswith("REASONING:") and out["copied_reason"] is None:
            out["copied_reason"] = s.split(":", 1)[1].strip()
    return out


def structural_sep(eq1, eq2):
    l1, r1 = eq1.split(" = ", 1)
    l2, r2 = eq2.split(" = ", 1)
    checks = [
        ("LP", rule_LP(l1, r1), rule_LP(l2, r2)),
        ("RP", rule_RP(l1, r1), rule_RP(l2, r2)),
        ("C0", rule_C0(l1, r1), rule_C0(l2, r2)),
        ("VARS", rule_AND(l1, r1), rule_AND(l2, r2)),
        ("XOR", rule_XOR(l1, r1), rule_XOR(l2, r2)),
        ("Z3A", rule_Z3A(l1, r1), rule_Z3A(l2, r2)),
        ("XNOR", rule_XNOR(l1, r1), rule_XNOR(l2, r2)),
    ]
    return [name for name, a, b in checks if a and not b]


def best_certificate(eq1, eq2, eq_map, masks, matrix):
    i = eq_map.get(normalize_eq(eq1))
    j = eq_map.get(normalize_eq(eq2))
    if i is None or j is None:
        return "unmapped"
    gt = implication_answer(matrix, i, j)
    if gt is False:
        ws = witness_separates(masks, i, j)
        if ws:
            return f"counterexample witness(s): {','.join(ws)}"
        cell = matrix[i][j]
        return f"counterexample in matrix ({CSV_CERT_LABEL.get(cell, str(cell))})"
    if gt is True:
        cell = matrix[i][j]
        return f"implication true in matrix ({CSV_CERT_LABEL.get(cell, str(cell))})"
    return "unknown"


def infer_cause(gt, pred, auto_reason, structural):
    reason = (auto_reason or "").lower()
    if gt and (pred is False):
        if "heuristic" in reason or "oracle" in reason:
            return "FN from over-aggressive false lane"
        if structural:
            return "FN from unsound structural trigger"
        return "FN from conservative false default"
    if (not gt) and pred:
        if "no separating witness" in reason:
            return "FP from missing deterministic separator"
        return "FP from incomplete hard-false coverage"
    return "other"


def find_result_files(results_dir: Path, contains: str):
    files = sorted(results_dir.glob("sim_*.json"))
    if not contains:
        return files
    needle = contains.lower()
    return [p for p in files if needle in p.name.lower()]


def write_markdown(path: Path, lines):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Analyze seeded run failures with corrected certificates.")
    parser.add_argument("--cheatsheet", default="cheatsheets/v22_witness.txt")
    parser.add_argument("--results-dir", default="results")
    parser.add_argument("--contains", default="")
    parser.add_argument("--result-files", default="")
    parser.add_argument("--out", default="results/seed_failure_report.md")
    args = parser.parse_args()

    cheatsheet_path = Path(args.cheatsheet)
    tmpl = jinja2.Template(cheatsheet_path.read_text(encoding="utf-8"))
    equations = load_equations()
    eq_map = build_equation_map(equations)
    masks = compute_witness_masks(equations)
    matrix = load_implications_csv()

    if args.result_files.strip():
        result_files = [Path(p.strip()) for p in args.result_files.split(",") if p.strip()]
    else:
        result_files = find_result_files(Path(args.results_dir), args.contains)

    if not result_files:
        raise SystemExit("No result files selected. Use --result-files or adjust --contains.")

    total_fail = 0
    out_lines = []
    out_lines.append("# Seed Failure Analysis")
    out_lines.append("")
    out_lines.append(f"Cheatsheet: {cheatsheet_path.as_posix()}")
    out_lines.append(f"Files analyzed: {len(result_files)}")
    out_lines.append("")

    for rf in result_files:
        data = json.loads(rf.read_text(encoding="utf-8"))
        fails = [r for r in data["results"] if not r["correct"]]
        total_fail += len(fails)
        out_lines.append(f"## {rf.name}")
        out_lines.append(f"fails={len(fails)}")
        out_lines.append("")
        for idx, r in enumerate(fails, 1):
            eq1 = r["equation1"]
            eq2 = r["equation2"]
            rendered = tmpl.render(equation1=eq1, equation2=eq2)
            p = parse_render_fields(rendered)
            seps = structural_sep(eq1, eq2)
            cert = best_certificate(eq1, eq2, eq_map, masks, matrix)
            cause = infer_cause(r["ground_truth"], r["predicted"], p["auto_reason"], seps)

            out_lines.append(f"### [{idx}] {r['id']}")
            out_lines.append(f"- gt={r['ground_truth']} pred={r['predicted']}")
            out_lines.append(f"- cause={cause}")
            out_lines.append(f"- auto_result={p['auto_result']} auto_reason={p['auto_reason']}")
            out_lines.append(f"- structural_separators={seps if seps else 'none'}")
            out_lines.append(f"- corrected_certificate={cert}")
            if r["ground_truth"]:
                out_lines.append("- corrected_proof=TRUE in Teorth matrix; no finite counterexample exists")
                out_lines.append("- corrected_counterexample=None")
            else:
                out_lines.append(f"- corrected_proof=FALSE by certificate source: {cert}")
                out_lines.append("- corrected_counterexample=exists (see witness/source above)")
            out_lines.append(f"- eq1={eq1}")
            out_lines.append(f"- eq2={eq2}")
            out_lines.append("")

    out_lines.append(f"total_failures={total_fail}")

    out_path = Path(args.out)
    write_markdown(out_path, out_lines)

    print("=" * 90)
    print(f"WROTE {out_path.as_posix()}")
    print(f"total_failures={total_fail}")
    print("=" * 90)


if __name__ == "__main__":
    main()
