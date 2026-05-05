from __future__ import annotations

import unittest

import make_unseen_30_30_sets as rotating


def sample_rows(subset: str, true_count: int, false_count: int) -> list[dict]:
    rows: list[dict] = []
    for index in range(true_count):
        rows.append({
            "id": f"{subset}_true_{index:03d}",
            "index": index,
            "difficulty": subset,
            "equation1": f"x = t{index}",
            "equation2": f"x = u{index}",
            "answer": True,
        })
    for index in range(false_count):
        rows.append({
            "id": f"{subset}_false_{index:03d}",
            "index": true_count + index,
            "difficulty": subset,
            "equation1": f"x = f{index}",
            "equation2": f"y = g{index}",
            "answer": False,
        })
    return rows


class RotatingBenchmarkTests(unittest.TestCase):
    def test_consecutive_rotations_do_not_reuse_ids_within_cycle(self) -> None:
        rows = sample_rows("normal", true_count=6, false_count=6)
        state = rotating.default_state()

        first_rows, first_meta = rotating.build_bundle_rows(
            rows=rows,
            subset="normal",
            n_true=2,
            n_false=2,
            state=state,
            rotation_index=1,
        )
        second_rows, second_meta = rotating.build_bundle_rows(
            rows=rows,
            subset="normal",
            n_true=2,
            n_false=2,
            state=state,
            rotation_index=2,
        )

        self.assertFalse({row["id"] for row in first_rows} & {row["id"] for row in second_rows})
        self.assertEqual(first_meta["true_bucket"]["cycle"], 0)
        self.assertEqual(second_meta["true_bucket"]["cycle"], 0)
        self.assertEqual(state["subsets"]["normal"]["true"]["offset"], 4)
        self.assertEqual(state["subsets"]["normal"]["false"]["offset"], 4)

    def test_rotation_wraps_to_new_cycle_after_pool_exhaustion(self) -> None:
        rows = sample_rows("hard3", true_count=4, false_count=4)
        state = rotating.default_state()

        rotating.build_bundle_rows(rows, "hard3", 2, 2, state, rotation_index=1)
        rotating.build_bundle_rows(rows, "hard3", 2, 2, state, rotation_index=2)
        wrapped_rows, wrapped_meta = rotating.build_bundle_rows(rows, "hard3", 2, 2, state, rotation_index=3)

        self.assertEqual(len(wrapped_rows), 4)
        self.assertEqual(wrapped_meta["true_bucket"]["cycle"], 1)
        self.assertEqual(wrapped_meta["false_bucket"]["cycle"], 1)
        self.assertTrue(wrapped_meta["true_bucket"]["wrapped"])
        self.assertTrue(wrapped_meta["false_bucket"]["wrapped"])
        self.assertEqual(state["subsets"]["hard3"]["true"]["offset"], 2)
        self.assertEqual(state["subsets"]["hard3"]["false"]["offset"], 2)

    def test_request_larger_than_bucket_raises(self) -> None:
        rows = sample_rows("hard", true_count=3, false_count=3)
        state = rotating.default_state()
        with self.assertRaises(ValueError):
            rotating.build_bundle_rows(rows, "hard", 4, 2, state, rotation_index=1)


if __name__ == "__main__":
    unittest.main()