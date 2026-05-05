# V26 Witness Admissibility Audit

- false_positives=77
- true_pairs=30
- admissible_covered=35
- admissible_uncovered=42
- assignment_only_extra=40

## Counts By Classification

- admissible=2168
- assignment_only=1325
- assignment_unsafe=16180

## Greedy Admissible Cover

- [[2, 1, 2], [2, 2, 2], [2, 2, 2]] size=3 +13 -> 13
- [[0, 2, 1], [0, 1, 2], [0, 1, 2]] size=3 +5 -> 18
- [[0, 0, 1], [1, 1, 0], [2, 2, 2]] size=3 +4 -> 22
- [[0, 2, 0], [0, 0, 0], [0, 0, 0]] size=3 +3 -> 25
- a*b = (b+1) mod 3 size=3 +3 -> 28
- [[0, 1, 2], [1, 0, 0], [2, 2, 0]] size=3 +1 -> 29
- [[0, 0, 0], [1, 1, 0], [2, 0, 2]] size=3 +1 -> 30
- [[2, 1, 0], [1, 0, 2], [0, 2, 1]] size=3 +1 -> 31
- [[0, 0, 2], [0, 0, 2], [1, 1, 2]] size=3 +1 -> 32
- [[2, 1, 1], [0, 2, 0], [1, 2, 2]] size=3 +1 -> 33
- [[0, 2, 0], [0, 0, 2], [2, 0, 2]] size=3 +1 -> 34
- [[1, 1, 1], [0, 0, 0], [2, 2, 2]] size=3 +1 -> 35

## Top Candidates

- admissible | [[2, 1, 2], [2, 2, 2], [2, 2, 2]] | universal=13 | cycling=12 | u_flags=0 | c_flags=0
- admissible | [[0, 0, 0], [0, 0, 0], [0, 1, 0]] | universal=13 | cycling=2 | u_flags=0 | c_flags=0
- admissible | [[2, 2, 2], [0, 2, 2], [2, 2, 2]] | universal=13 | cycling=1 | u_flags=0 | c_flags=0
- admissible | [[0, 0, 0], [0, 0, 2], [0, 0, 0]] | universal=13 | cycling=0 | u_flags=0 | c_flags=0
- admissible | [[1, 1, 1], [1, 1, 1], [0, 1, 1]] | universal=13 | cycling=0 | u_flags=0 | c_flags=0
- admissible | [[1, 1, 2], [1, 1, 1], [1, 1, 1]] | universal=13 | cycling=0 | u_flags=0 | c_flags=0
- admissible | [[1, 2, 1], [1, 1, 1], [1, 1, 1]] | universal=11 | cycling=14 | u_flags=0 | c_flags=0
- admissible | [[1, 2, 2], [1, 1, 1], [1, 1, 1]] | universal=11 | cycling=13 | u_flags=0 | c_flags=0
- admissible | [[2, 1, 1], [2, 2, 2], [2, 2, 2]] | universal=11 | cycling=13 | u_flags=0 | c_flags=0
- admissible | [[0, 0, 0], [0, 0, 0], [1, 0, 0]] | universal=11 | cycling=9 | u_flags=0 | c_flags=0

