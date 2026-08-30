
theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 0) (g 0) (g 0)
  revert this
  change ¬ g 0 = op (op (op (op (g 0) (g 0)) (g 0)) (g 0)) (op (g 0) (g 0))
  simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2, W, K1, K2, L1, L2]

/-- THE LAW: x = y * (((y * x) * z) * (x * z)) -/
theorem law (x y z : M) : op (y) (op (op (op (y) (x)) (z)) (op (x) (z))) = x := by
  sorry

theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
