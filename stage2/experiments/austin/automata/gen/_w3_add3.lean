
/-- HOLE 1 -- the fourth product is free.  0 violations in 24,000 targeted trials
    (gen/_w3_12087_tree.py: V is 'F' in every reachable cell). -/
theorem VF (x y z : M) : op (op (op y x) z) (op x z) = J (op (op y x) z) (op x z) := sorry

/-- HOLE 2 -- the second and third products never both decode.  0 violations in 24,000 trials. -/
theorem BC (x y z : M) (hB : op (op y x) z ≠ J (op y x) z) : op x z = J x z := sorry

/-- HOLE 3 -- first and third products decode, second free (1007/6000 census hits). -/
theorem AD {x y z : M} (hA : op y x ≠ J y x) (hC : op x z ≠ J x z) :
    op y (J (J (op y x) z) (op x z)) = x := sorry
