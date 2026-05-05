from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import proof_construction_atlas


class ProofConstructionAtlasTests(unittest.TestCase):
    def test_infer_page_families_from_text_blocks(self) -> None:
        row = {
            "title": "Proof of hard case",
            "code_blocks": ["counterexample family via shift operator on a tree"],
            "pre_blocks": [],
            "table_blocks": [],
            "theorem_links": [],
            "fact_links": [],
            "all_links": [],
        }
        families = proof_construction_atlas.infer_page_families(row)
        self.assertIn("linear_translation", families)
        self.assertIn("exceptional_hard", families)

    def test_annotate_row_prefers_entry_provenance(self) -> None:
        row = {
            "pair": [11, 22],
            "ok": True,
            "url": "https://example.test",
            "title": "placeholder page",
            "code_blocks": ["shift operator"],
            "pre_blocks": [],
            "table_blocks": [],
            "pair_links": [],
            "theorem_links": [],
            "fact_links": [],
            "all_links": [],
        }
        entry = {
            "name": "Apply.Equation11_implies_Equation22",
            "filename": "/tmp/Generated/All4x4Tables/Refutation1.lean",
            "line": 10,
            "variant": {"implication": {"lhs": "Equation11", "rhs": "Equation22", "finite": True}},
        }
        annotated = proof_construction_atlas.annotate_row(row, {(11, 22): [entry]})
        self.assertEqual(annotated["primary_family"], "all4x4_table_counterexamples")

    def test_build_atlas_writes_outputs(self) -> None:
        crawl_line = {
            "pair": [11, 22],
            "ok": True,
            "url": "https://example.test",
            "title": "central groupoid construction",
            "code_blocks": [],
            "pre_blocks": [],
            "table_blocks": [],
            "pair_links": [],
            "theorem_links": [],
            "fact_links": [],
            "all_links": [],
        }
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            crawl_jsonl = root / "crawl.jsonl"
            crawl_jsonl.write_text(__import__("json").dumps(crawl_line) + "\n", encoding="utf-8")
            with patch("proof_construction_atlas.load_full_entries", return_value=[]):
                result = proof_construction_atlas.build_atlas(crawl_jsonl, root / "atlas")
            self.assertTrue(result["pair_jsonl"].exists())
            self.assertTrue(result["family_json"].exists())
            self.assertTrue(result["summary_md"].exists())


if __name__ == "__main__":
    unittest.main()