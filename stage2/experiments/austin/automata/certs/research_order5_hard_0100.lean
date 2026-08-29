import JudgeProblem
import Mathlib.Tactic
set_option warn.classDefReducibility false

def submission.op (x y : ℚ) : ℚ :=
  if y ≤ 0 ∧ x ≤ y then -x/2 + y/2
  else if 0 ≤ y ∧ x ≤ 0 then -x/2 + y
  else -x + y

def submission.carrier : Type := ℚ

def submission.inst : Magma submission.carrier := { op := fun a b => (submission.op a b : ℚ) }

theorem submission.cases (x y : ℚ) :
    (y ≤ 0 ∧ x ≤ y ∧ submission.op x y = -x/2 + y/2) ∨
    (0 < y ∧ x ≤ 0 ∧ submission.op x y = -x/2 + y) ∨
    (y ≤ 0 ∧ y < x ∧ submission.op x y = -x + y) ∨
    (0 < y ∧ 0 < x ∧ submission.op x y = -x + y) := by
  unfold submission.op
  split_ifs with h1 h2
  · exact Or.inl ⟨h1.1, h1.2, rfl⟩
  · rcases not_and_or.mp h1 with h | h
    · exact Or.inr (Or.inl ⟨lt_of_not_ge h, h2.2, rfl⟩)
    · exfalso; exact h (by linarith [h2.2, h2.1])
  · by_cases hy : y ≤ 0
    · rcases not_and_or.mp h1 with h | h
      · exact absurd hy h
      · exact Or.inr (Or.inr (Or.inl ⟨hy, lt_of_not_ge h, rfl⟩))
    · rcases not_and_or.mp h2 with g | g
      · exact absurd (le_of_lt (lt_of_not_ge hy)) g
      · exact Or.inr (Or.inr (Or.inr ⟨lt_of_not_ge hy, lt_of_not_ge g, rfl⟩))

theorem submission.sq (z : ℚ) : submission.op z z = 0 := by
  rcases submission.cases z z with ⟨_, _, e⟩ | ⟨_, _, e⟩ | ⟨_, h, _⟩ | ⟨_, _, e⟩ <;> linarith

theorem submission.law (x y z : ℚ) :
    submission.op (submission.op y (submission.op x (submission.op x y))) (submission.op z z) = x := by
  rw [submission.sq]
  rcases submission.cases x y with ⟨h1, h2, e⟩ | ⟨h1, h2, e⟩ | ⟨h1, h2, e⟩ | ⟨h1, h2, e⟩ <;>
  rcases submission.cases x (submission.op x y) with ⟨g1, g2, f⟩ | ⟨g1, g2, f⟩ | ⟨g1, g2, f⟩ | ⟨g1, g2, f⟩ <;>
  (try linarith) <;>
  rcases submission.cases y (submission.op x (submission.op x y)) with ⟨k1, k2, m⟩ | ⟨k1, k2, m⟩ | ⟨k1, k2, m⟩ | ⟨k1, k2, m⟩ <;>
  (try linarith) <;>
  rcases submission.cases (submission.op y (submission.op x (submission.op x y))) 0 with ⟨l1, l2, n⟩ | ⟨l1, l2, n⟩ | ⟨l1, l2, n⟩ | ⟨l1, l2, n⟩ <;>
  linarith

theorem submission.lhs : @EquationLHS submission.carrier submission.inst := by
  intro x y z
  exact (submission.law x y z).symm

theorem submission.rhs : ¬ @EquationRHS submission.carrier submission.inst := by
  intro h
  have hh : (1:ℚ) = submission.op 0 (submission.op 1 (submission.op 1 (submission.op 0 (submission.op 0 0)))) := h (1:ℚ) (0:ℚ) (0:ℚ)
  norm_num [submission.op] at hh

def submission : Goal :=
  Exists.intro submission.carrier (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
