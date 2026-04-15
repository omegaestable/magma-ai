from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import v26_recovery


def make_row(
    row_id: str,
    *,
    eq1: str,
    eq2: str,
    ground_truth: bool,
    predicted,
) -> dict:
    return {
        "id": row_id,
        "equation1": eq1,
        "equation2": eq2,
        "ground_truth": ground_truth,
        "predicted": predicted,
        "parsed_ok": predicted is not None,
    }


def write_result_file(
    path: Path,
    *,
    candidate: str,
    model: str,
    subset: str,
    rows: list[dict],
    repeats: int = 1,
) -> Path:
    total = len(rows)
    correct = sum(1 for row in rows if row["predicted"] == row["ground_truth"])
    parsed = sum(1 for row in rows if row["parsed_ok"])
    payload = {
        "model": model,
        "cheatsheet": f"cheatsheets/{candidate}.txt",
        "subset": subset,
        "repeats": repeats,
        "summary": {
            "accuracy": correct / total if total else 0.0,
            "parse_rate": parsed / total if total else 0.0,
        },
        "results": rows,
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


class V26RecoveryTests(unittest.TestCase):
    def test_compare_runs_groups_only_exact_matches(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            rows = [
                make_row(
                    "same_1",
                    eq1="x = x * y",
                    eq2="x = y * x",
                    ground_truth=False,
                    predicted=True,
                ),
                make_row(
                    "same_2",
                    eq1="x = x",
                    eq2="x = x",
                    ground_truth=True,
                    predicted=True,
                ),
            ]
            run_a = write_result_file(
                root / "run_a.json",
                candidate="v26b",
                model="gpt-oss-120b",
                subset="normal",
                rows=rows,
            )
            run_b = write_result_file(
                root / "run_b.json",
                candidate="v26c",
                model="gpt-oss-120b",
                subset="normal",
                rows=rows,
            )
            run_c = write_result_file(
                root / "run_c.json",
                candidate="v26d",
                model="llama-3-3-70b-instruct",
                subset="normal",
                rows=rows,
            )

            report = v26_recovery.compare_runs([run_a, run_b, run_c])

        self.assertEqual(report["comparable_group_count"], 1)
        self.assertEqual(report["incomparable_run_count"], 1)
        group = report["comparable_groups"][0]
        self.assertEqual({run["candidate"] for run in group["runs"]}, {"v26b", "v26c"})
        self.assertEqual(group["model"], "gpt-oss-120b")

    def test_compare_runs_tracks_fixed_false_positives(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            base_rows = [
                make_row(
                    "fp_old",
                    eq1="x = x * y",
                    eq2="x = y * x",
                    ground_truth=False,
                    predicted=True,
                ),
                make_row(
                    "steady_true",
                    eq1="x = x",
                    eq2="x = x",
                    ground_truth=True,
                    predicted=True,
                ),
            ]
            challenger_rows = [
                make_row(
                    "fp_old",
                    eq1="x = x * y",
                    eq2="x = y * x",
                    ground_truth=False,
                    predicted=False,
                ),
                make_row(
                    "steady_true",
                    eq1="x = x",
                    eq2="x = x",
                    ground_truth=True,
                    predicted=True,
                ),
            ]
            run_a = write_result_file(
                root / "run_a.json",
                candidate="v26b",
                model="gpt-oss-120b",
                subset="hard3",
                rows=base_rows,
            )
            run_b = write_result_file(
                root / "run_b.json",
                candidate="v26c",
                model="gpt-oss-120b",
                subset="hard3",
                rows=challenger_rows,
            )

            report = v26_recovery.compare_runs([run_a, run_b])

        delta = report["comparable_groups"][0]["pairwise_deltas"][0]
        self.assertEqual(delta["fp_fixed"], ["fp_old"])
        self.assertEqual(delta["fp_introduced"], [])
        self.assertGreater(delta["accuracy_delta"], 0.0)

    def test_assignment_only_separator_is_not_admissible(self) -> None:
        table = [[0, 0], [1, 0]]
        eq1 = "x = x * y"
        eq2 = "x = y * x"

        self.assertTrue(v26_recovery.separates_with_cycling_assignment(table, eq1, eq2))
        self.assertFalse(v26_recovery.separates_universally(table, eq1, eq2))

        candidate = {
            "universal_caught_ids": [],
            "cycling_caught_ids": ["fp1"],
            "universal_true_flags": [],
            "cycling_true_flags": [],
        }
        self.assertEqual(v26_recovery.classify_magma_candidate(candidate), "assignment_only")

    def test_audit_magmas_finds_admissible_universal_cover(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            rows = [
                make_row(
                    "fp1",
                    eq1="x = x * y",
                    eq2="x = y * x",
                    ground_truth=False,
                    predicted=True,
                ),
            ]
            result_file = write_result_file(
                root / "audit.json",
                candidate="v26b",
                model="gpt-oss-120b",
                subset="normal",
                rows=rows,
            )

            report = v26_recovery.audit_magmas([result_file], max_size=2)

        self.assertIn("fp1", report["admissible_covered_ids"])
        self.assertGreaterEqual(report["counts_by_classification"].get("admissible", 0), 1)

    def test_audit_magmas_flags_family_unsafe_when_true_pair_is_separated(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            rows = [
                make_row(
                    "fp1",
                    eq1="x = x * y",
                    eq2="x = y * x",
                    ground_truth=False,
                    predicted=True,
                ),
                make_row(
                    "tp1",
                    eq1="x = x * y",
                    eq2="x = y * x",
                    ground_truth=True,
                    predicted=True,
                ),
            ]
            result_file = write_result_file(
                root / "unsafe.json",
                candidate="v26b",
                model="gpt-oss-120b",
                subset="normal",
                rows=rows,
            )

            report = v26_recovery.audit_magmas([result_file], max_size=2)

        self.assertGreaterEqual(report["counts_by_classification"].get("family_unsafe", 0), 1)


if __name__ == "__main__":
    unittest.main()