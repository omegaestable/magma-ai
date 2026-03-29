from __future__ import annotations

import unittest

import proof_atlas


class ProofAtlasTests(unittest.TestCase):
    def test_dual_round_trip(self) -> None:
        eq = "x = (y * z) * x"
        lhs1, rhs1 = proof_atlas.parse_equation_tree(eq)
        lhs2, rhs2 = proof_atlas.parse_equation_tree(proof_atlas.dualize_equation(proof_atlas.dualize_equation(eq)))
        self.assertEqual(proof_atlas.tree_to_expr(lhs1), proof_atlas.tree_to_expr(lhs2))
        self.assertEqual(proof_atlas.tree_to_expr(rhs1), proof_atlas.tree_to_expr(rhs2))

    def test_literal_x_target_detection(self) -> None:
        self.assertTrue(proof_atlas.is_literal_x_target("x = y * z"))
        self.assertFalse(proof_atlas.is_literal_x_target("x * y = z"))

    def test_classify_known_families(self) -> None:
        entry = {
            "filename": "/tmp/Generated/TrivialBruteforce/theorems/Apply.lean",
            "name": "Apply.Equation10_implies_Equation110",
            "variant": {"implication": {"lhs": "Equation10", "rhs": "Equation110", "finite": False}},
        }
        self.assertEqual(proof_atlas.classify_entry(entry), "rewrite_metatheorem")

        entry["filename"] = "/tmp/equational_theories/LinearOps.lean"
        entry["variant"] = {"facts": {"satisfied": ["Equation1"], "refuted": ["Equation2"], "finite": True}}
        self.assertEqual(proof_atlas.classify_entry(entry), "linear_translation")

        entry["filename"] = "/tmp/equational_theories/Generated/All4x4Tables/Refutation1.lean"
        self.assertEqual(proof_atlas.classify_entry(entry), "all4x4_table_counterexamples")

        entry["filename"] = "/tmp/equational_theories/CentralGroupoids.lean"
        self.assertEqual(proof_atlas.classify_entry(entry), "central_groupoid_counterexamples")

    def test_rendered_cheatsheet_fits_budget(self) -> None:
        atlas_records = []
        for base_family in [
            "singleton_rewrite",
            "projection_family_counterexamples",
            "small_finite_magma",
            "modified_lifted_magma",
            "linear_translation",
            "rewrite_metatheorem",
            "subgraph_seed",
            "automated_reasoner",
            "canonizer_confluence",
            "exceptional_hard",
        ]:
            atlas_records.append(
                proof_atlas.initialize_family_record(
                    base_family=base_family,
                    polarity="true" if "rewrite" in base_family or base_family in {"subgraph_seed", "automated_reasoner"} else "false",
                    scope="general",
                    closure_mode="explicit",
                    benchmark_alignment={"patterns": {}, "witnesses": {}},
                )
            )
        rendered = proof_atlas.render_cheatsheet(atlas_records)
        self.assertIn("{{ equation1 }}", rendered)
        self.assertLessEqual(len(rendered.encode("utf-8")), 10_240)


if __name__ == "__main__":
    unittest.main()
