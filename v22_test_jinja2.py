#!/usr/bin/env python3
"""
v22_test_jinja2.py — Validate v22 Jinja2 cheatsheet against all benchmarks
and structural rule ground truth.

Tests:
  1. Render template for every normal benchmark problem, check verdict matches ground truth
  2. Validate structural test results match v21_verify_structural_rules.py
  3. Check byte budget
  4. Measure rendered output length

Run:
    python v22_test_jinja2.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import jinja2

from v21_data_infrastructure import (
    ROOT,
    load_equations,
    build_equation_map,
    normalize_eq,
    load_all_benchmarks,
    map_benchmark_to_ids,
)
from v21_verify_structural_rules import (
    STRUCTURAL_RULES,
)

CHEATSHEET_PATH = ROOT / "cheatsheets" / "v22_lookup.txt"
MAX_BYTES = 10_240


def parse_verdict(rendered: str) -> bool | None:
    """Extract VERDICT from rendered output."""
    for line in rendered.split('\n'):
        stripped = line.strip()
        if stripped.startswith('VERDICT:'):
            val = stripped.split('VERDICT:')[1].strip().upper()
            if val.startswith('TRUE'):
                return True
            if val.startswith('FALSE'):
                return False
    return None


def parse_test_results(rendered: str) -> dict[str, tuple[str, str]]:
    """Parse test results table from rendered output.
    Returns {test_name: (e1_result, e2_result)}."""
    results = {}
    for line in rendered.split('\n'):
        stripped = line.strip()
        for name in ['LP', 'RP', 'C0', 'VARS', 'XOR', 'Z3A', 'XNOR']:
            if stripped.startswith(f'{name}:'):
                parts = stripped.split()
                # Format: "LP:   E1=HOLD  E2=FAIL  ★SEP"
                e1_val = e2_val = None
                for p in parts:
                    if p.startswith('E1='):
                        e1_val = p.split('=')[1]
                    elif p.startswith('E2='):
                        e2_val = p.split('=')[1]
                if e1_val and e2_val:
                    results[name] = (e1_val, e2_val)
                break
    return results


def main():
    print("=" * 72)
    print("v22 Jinja2 Cheatsheet Validation")
    print("=" * 72)

    # Load template
    if not CHEATSHEET_PATH.exists():
        print(f"ERROR: {CHEATSHEET_PATH} not found. Run v22_build_cheatsheet.py first.")
        sys.exit(1)

    template_text = CHEATSHEET_PATH.read_text(encoding="utf-8")
    raw_bytes = len(CHEATSHEET_PATH.read_bytes())
    print(f"\n[1] Template: {CHEATSHEET_PATH.name}")
    print(f"    Size: {raw_bytes} bytes ({100*raw_bytes/MAX_BYTES:.1f}% of {MAX_BYTES})")
    if raw_bytes > MAX_BYTES:
        print(f"    FAIL: Over budget by {raw_bytes - MAX_BYTES} bytes!")
        sys.exit(1)
    print(f"    OK: Under budget by {MAX_BYTES - raw_bytes} bytes")

    template = jinja2.Template(template_text)

    # Load equations and benchmarks
    print("\n[2] Loading data ...")
    equations = load_equations()
    eq_map = build_equation_map(equations)
    all_problems = load_all_benchmarks()
    mapped, unmapped = map_benchmark_to_ids(all_problems, eq_map)
    normal = [p for p in mapped if p.get("difficulty") == "normal"]
    print(f"    Normal problems: {len(normal)}")

    # Test 1: Verdict correctness on all normal benchmarks
    print("\n[3] Testing verdict correctness on all normal problems ...")
    correct = 0
    wrong = 0
    errors = []
    render_lens = []

    for i, p in enumerate(normal):
        try:
            rendered = template.render(
                equation1=p["equation1"],
                equation2=p["equation2"],
            )
            render_lens.append(len(rendered))
            verdict = parse_verdict(rendered)
            expected = p["answer"]

            if verdict == expected:
                correct += 1
            else:
                wrong += 1
                errors.append({
                    "id": p["id"],
                    "eq1": p["equation1"],
                    "eq2": p["equation2"],
                    "expected": expected,
                    "got": verdict,
                    "file": p["_benchmark_file"],
                })
        except Exception as exc:
            wrong += 1
            errors.append({
                "id": p["id"],
                "error": str(exc),
            })

        if (i + 1) % 100 == 0:
            print(f"    Progress: {i+1}/{len(normal)} ({correct} correct, {wrong} wrong)")

    total = correct + wrong
    accuracy = 100 * correct / total if total > 0 else 0
    print(f"\n    RESULTS: {correct}/{total} correct ({accuracy:.1f}%)")
    print(f"    Rendered length: min={min(render_lens)}, max={max(render_lens)}, "
          f"avg={sum(render_lens)//len(render_lens)}")

    if errors:
        # Classify errors
        fp = [e for e in errors if e.get("expected") is False and e.get("got") is True]
        fn = [e for e in errors if e.get("expected") is True and e.get("got") is False]
        parse_fail = [e for e in errors if e.get("got") is None]
        exc = [e for e in errors if "error" in e]

        print(f"\n    Error breakdown:")
        print(f"      False Positives (predicted TRUE, actual FALSE): {len(fp)}")
        print(f"      False Negatives (predicted FALSE, actual TRUE): {len(fn)}")
        print(f"      Parse failures: {len(parse_fail)}")
        print(f"      Exceptions: {len(exc)}")

        print(f"\n    FALSE POSITIVES (should be FALSE, got TRUE):")
        for e in fp[:20]:
            print(f"      {e['id']} [{e['file']}]: E1='{e['eq1']}' E2='{e['eq2']}'")

        if fn:
            print(f"\n    FALSE NEGATIVES (should be TRUE, got FALSE):")
            for e in fn[:10]:
                print(f"      {e['id']} [{e['file']}]: E1='{e['eq1']}' E2='{e['eq2']}'")

        if parse_fail:
            print(f"\n    PARSE FAILURES:")
            for e in parse_fail[:5]:
                print(f"      {e['id']}: {e}")

        if exc:
            print(f"\n    EXCEPTIONS:")
            for e in exc[:5]:
                print(f"      {e['id']}: {e['error']}")

    # Test 2: Validate structural tests match ground truth
    print("\n[4] Validating structural test computations ...")
    # Check LP and RP on a sample of equations
    from v21_verify_structural_rules import rule_LP, rule_RP, rule_C0, rule_AND, rule_XOR, rule_Z3A, rule_XNOR

    struct_errors = 0
    struct_total = 0
    for p in normal[:100]:
        rendered = template.render(
            equation1=p["equation1"],
            equation2=p["equation2"],
        )
        test_results = parse_test_results(rendered)

        for eq_text, eq_label in [(p["equation1"], "E1"), (p["equation2"], "E2")]:
            parts = normalize_eq(eq_text).split(' = ', 1)
            if len(parts) != 2:
                continue
            lhs, rhs = parts[0].strip(), parts[1].strip()

            for test_name, rule_fn, jinja_name in [
                ("LP", rule_LP, "LP"),
                ("RP", rule_RP, "RP"),
                ("C0", rule_C0, "C0"),
                ("AND", rule_AND, "VARS"),
                ("XOR", rule_XOR, "XOR"),
                ("Z3A", rule_Z3A, "Z3A"),
                ("XNOR", rule_XNOR, "XNOR"),
            ]:
                expected_holds = rule_fn(lhs, rhs)
                if jinja_name in test_results:
                    idx = 0 if eq_label == "E1" else 1
                    jinja_val = test_results[jinja_name][idx]
                    jinja_holds = (jinja_val == "HOLD")
                    struct_total += 1
                    if jinja_holds != expected_holds:
                        struct_errors += 1
                        if struct_errors <= 10:
                            print(f"      MISMATCH {test_name} on {eq_label}: "
                                  f"'{eq_text}' expected={expected_holds} jinja={jinja_holds}")
                            print(f"        LHS='{lhs}' RHS='{rhs}'")

    print(f"    Structural test checks: {struct_total - struct_errors}/{struct_total} correct")
    if struct_errors > 0:
        print(f"    WARNING: {struct_errors} structural test mismatches!")

    # Per-benchmark file accuracy
    print("\n[5] Per-benchmark accuracy ...")
    by_file = Counter()
    by_file_total = Counter()
    for p in normal:
        bf = p["_benchmark_file"]
        by_file_total[bf] += 1
        rendered = template.render(equation1=p["equation1"], equation2=p["equation2"])
        verdict = parse_verdict(rendered)
        if verdict == p["answer"]:
            by_file[bf] += 1

    for bf in sorted(by_file_total):
        c = by_file[bf]
        t = by_file_total[bf]
        print(f"    {bf}: {c}/{t} ({100*c/t:.0f}%)")

    print("\n" + "=" * 72)
    print("Validation complete.")
    print("=" * 72)


if __name__ == "__main__":
    main()
