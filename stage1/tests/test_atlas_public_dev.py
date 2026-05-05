from __future__ import annotations

import unittest
from pathlib import Path

import atlas_public_dev


class AtlasPublicDevTests(unittest.TestCase):
    def test_dataset_split_counts_and_no_leakage(self) -> None:
        datasets = atlas_public_dev.load_all_problem_sets()
        split_manifest, rows = atlas_public_dev.build_dataset_split(datasets, dev_ratio=0.2, seed=20260326)
        self.assertEqual(sum(1 for row in rows if row["role"] == "train_corpus"), 1069)
        self.assertEqual(sum(1 for row in rows if row["role"] == "held_out_test"), 600)
        public_ids = set(split_manifest["public_ids"])
        heldout_ids = set(split_manifest["heldout_ids"])
        self.assertFalse(public_ids & heldout_ids)
        self.assertEqual(split_manifest["counts"]["normal"]["total"], 1000)
        self.assertEqual(split_manifest["counts"]["hard1"]["total"], 69)
        self.assertEqual(split_manifest["counts"]["hard2"]["total"], 200)
        self.assertEqual(split_manifest["counts"]["hard3"]["total"], 400)

    def test_public_workflow_generates_budget_variants(self) -> None:
        out_dir = Path("tmp_test_atlas_public_out")
        variant_dir = Path("tmp_test_atlas_public_variants")
        result = atlas_public_dev.build_public_workflow(
            out_dir=out_dir,
            variant_dir=variant_dir,
            dev_ratio=0.2,
            seed=20260326,
            evaluate_public=False,
            evaluate_heldout=False,
        )
        public_rows = [row for row in result["alignments"] if row["role"] == "train_corpus"]
        self.assertEqual(len(public_rows), 1069)
        self.assertLessEqual(sum(1 for row in public_rows if row["unresolved"]), 10)
        self.assertEqual(len(result["variants"]), 3)
        report_by_family = {row["family_id"]: row for row in result["public_report"]["families"]}
        self.assertGreaterEqual(len(result["bundle_catalog"]), 6)
        for variant in result["variants"]:
            self.assertTrue(variant["fits_budget"])
            self.assertLessEqual(variant["byte_size"], 10_240)
            self.assertTrue(variant["selected_bundle_ids"])
            self.assertTrue(variant["selected_rules"])
            for family_id in variant["selected_family_ids"]:
                self.assertGreater(report_by_family[family_id]["aligned_problem_count"], 0)


if __name__ == "__main__":
    unittest.main()
