from __future__ import annotations

import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch

import analyze_hard_false_families


class AnalyzeHardFalseFamiliesTests(unittest.TestCase):
    def test_build_fact_family_index_counts_only_false_families(self) -> None:
        entries = [
            {
                "filename": "/tmp/SmallMagmas.lean",
                "name": "SmallMagmas.eq",
                "variant": {"facts": {"satisfied": ["Equation10"], "refuted": ["Equation20"]}},
            },
            {
                "filename": "/tmp/Subgraph.lean",
                "name": "Subgraph.eq",
                "variant": {"facts": {"satisfied": ["Equation10"], "refuted": ["Equation30"]}},
            },
        ]
        index = analyze_hard_false_families.build_fact_family_index(entries)
        self.assertEqual(index[10]["small_finite_magma"], 1)
        self.assertNotIn("subgraph_seed", index[10])

    @patch("analyze_hard_false_families.distill.find_verified_witnesses")
    @patch("analyze_hard_false_families.distill.extract_pair_features")
    def test_rank_false_pair_prioritizes_shared_family_support(self, mock_features, mock_witnesses) -> None:
        mock_features.return_value = {
            "new_vars_in_e2": ["w"],
            "lp_obstruction": True,
            "rp_obstruction": False,
        }
        mock_witnesses.return_value = [{"name": "XOR"}]
        row = {"id": "hard_x", "equation1": "x = x", "equation2": "x = y"}
        benchmark_row = {"eq1_id": 10, "eq2_id": 20}
        family_index = {
            10: Counter({"all4x4_table_counterexamples": 3}),
            20: Counter({"all4x4_table_counterexamples": 2}),
        }
        ranked = analyze_hard_false_families.rank_false_pair(row, benchmark_row, family_index)
        self.assertEqual(ranked["primary_family"], "all4x4_table_counterexamples")
        self.assertTrue(ranked["verified_witnesses"])

    def test_analyze_result_file_filters_false_positives(self) -> None:
        result_payload = {
            "results": [
                {"id": "hard_0001", "ground_truth": False, "predicted": True, "equation1": "x = x", "equation2": "x = y"},
                {"id": "hard_0002", "ground_truth": False, "predicted": False, "equation1": "x = x", "equation2": "x = y"},
            ]
        }
        bench_line = {
            "id": "hard_0001",
            "eq1_id": 10,
            "eq2_id": 20,
            "equation1": "x = x",
            "equation2": "x = y",
        }
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            result_path = root / "sim_meta-llama_llama-3.3-70b-instruct_hard_balanced40_true20_false20_rotation0001_20260403_163406_v23_20260403_105851.json"
            result_path.write_text(__import__("json").dumps(result_payload), encoding="utf-8")
            benchmark_dir = root / "data" / "benchmark"
            benchmark_dir.mkdir(parents=True)
            benchmark_path = benchmark_dir / "hard_balanced40_true20_false20_rotation0001_20260403_163406.jsonl"
            benchmark_path.write_text(__import__("json").dumps(bench_line) + "\n", encoding="utf-8")
            with patch.object(analyze_hard_false_families, "ROOT", root):
                report = analyze_hard_false_families.analyze_result_file(result_path, {})
        self.assertEqual(report["false_positive_count"], 1)
        self.assertEqual(len(report["rows"]), 1)


if __name__ == "__main__":
    unittest.main()