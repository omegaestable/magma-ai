# Mathematical Notes

These notes distinguish verified facts from heuristics.

## Verified Facts

1. `equations.txt` contains 4694 equations.
2. `export_raw_implications_14_3_2026.csv` is a dense 4694 x 4694 matrix.
3. The matrix contains 8,178,279 positive ordered pairs and 13,855,357 negative ordered pairs, so the positive rate is about 37.1172%.
4. Equation 1 is `x = x`.
5. Equation 2 is `x = y`.
6. Equation 3 is `x = x ◇ x`.
7. Equation 4 is `x = x ◇ y`.
8. Equation 5 is `x = y ◇ x`.
9. Equation 43 is `x ◇ y = y ◇ x`.
10. Equation 4512 is `x ◇ (y ◇ z) = (x ◇ y) ◇ z`.
11. Equation 4 implies Equation 3 by specialization `y := x`.
12. The dual of Equation 4 is Equation 5.

## High-Influence Equations In The Dense Matrix

Outgoing-positive maxima observed locally include equations 3241, 3243, 3244, 3245, 3246, 3248, 3249, 3250, 3251, and 3252; each has positive entries across the full row in the dense matrix.

Incoming-positive maxima observed locally include equations 1, 3253, 4065, 4118, 3319, 3862, 4269, 4316, 4584, and 4631.

These are matrix facts, not automatically safe cheatsheet facts.

## Safe Cheatsheet Content

1. Trivial-case handling for `x = x` and `x = y`.
2. Specialization as a proof pattern.
3. Duality as a transport rule.
4. Small explicit counterexample search over 2-element and 3-element magmas.
5. Linear-model search over small moduli as a counterexample tool.

## Unsafe Or Currently Unsupported Claims

1. Any exact equivalence-class count not backed by a reproducible derivation in this repo.
2. Any global accuracy number not backed by a saved benchmark artifact.
3. Any statement that “most pairs are FALSE” based on a made-up base rate. The dense matrix in this repo is about 37% positive, not 6% positive.
4. Any theorem-like structural claim derived only from correlations in the matrix.