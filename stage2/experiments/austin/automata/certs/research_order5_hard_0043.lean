import JudgeProblem
import Mathlib.Tactic
set_option warn.classDefReducibility false

def submission.op (x y : ℚ) : ℚ :=
  if x ≤ 0 ∧ y ≤ x then -y/2 + x/2
  else if 0 ≤ x ∧ y ≤ 0 then -y/2 + x
  else -y + x

def submission.carrier : Type := ℚ

def submission.inst : Magma submission.carrier := { op := fun a b => (submission.op a b : ℚ) }

theorem submission.cases (x y : ℚ) :
    (x ≤ 0 ∧ y ≤ x ∧ submission.op x y = -y/2 + x/2) ∨
    (0 < x ∧ y ≤ 0 ∧ submission.op x y = -y/2 + x) ∨
    (x ≤ 0 ∧ x < y ∧ submission.op x y = -y + x) ∨
    (0 < x ∧ 0 < y ∧ submission.op x y = -y + x) := by
  unfold submission.op
  split_ifs with h1 h2
  · exact Or.inl ⟨h1.1, h1.2, rfl⟩
  · rcases not_and_or.mp h1 with h | h
    · exact Or.inr (Or.inl ⟨lt_of_not_ge h, h2.2, rfl⟩)
    · exfalso; exact h (by linarith [h2.2, h2.1])
  · by_cases hx : x ≤ 0
    · rcases not_and_or.mp h1 with h | h
      · exact absurd hx h
      · exact Or.inr (Or.inr (Or.inl ⟨hx, lt_of_not_ge h, rfl⟩))
    · rcases not_and_or.mp h2 with g | g
      · exact absurd (le_of_lt (lt_of_not_ge hx)) g
      · exact Or.inr (Or.inr (Or.inr ⟨lt_of_not_ge hx, lt_of_not_ge g, rfl⟩))

theorem submission.sq (z : ℚ) : submission.op z z = 0 := by
  rcases submission.cases z z with ⟨_, _, e⟩ | ⟨_, _, e⟩ | ⟨_, h, _⟩ | ⟨_, _, e⟩ <;> linarith

theorem submission.law (x y z : ℚ) :
    submission.op (submission.op y y) (submission.op (submission.op (submission.op z x) x) z) = x := by
  rw [submission.sq]
  rcases submission.cases z x with ⟨h1, h2, e⟩ | ⟨h1, h2, e⟩ | ⟨h1, h2, e⟩ | ⟨h1, h2, e⟩ <;>
  rcases submission.cases (submission.op z x) x with ⟨g1, g2, f⟩ | ⟨g1, g2, f⟩ | ⟨g1, g2, f⟩ | ⟨g1, g2, f⟩ <;>
  (try linarith) <;>
  rcases submission.cases (submission.op (submission.op z x) x) z with ⟨k1, k2, m⟩ | ⟨k1, k2, m⟩ | ⟨k1, k2, m⟩ | ⟨k1, k2, m⟩ <;>
  (try linarith) <;>
  rcases submission.cases 0 (submission.op (submission.op (submission.op z x) x) z) with ⟨l1, l2, n⟩ | ⟨l1, l2, n⟩ | ⟨l1, l2, n⟩ | ⟨l1, l2, n⟩ <;>
  linarith

theorem submission.lhs : @EquationLHS submission.carrier submission.inst := by
  intro x y z
  exact (submission.law x y z).symm

theorem submission.rhs : ¬ @EquationRHS submission.carrier submission.inst := by
  intro h
  have hh : (-3:ℚ) = submission.op (submission.op (-3:ℚ) (-3:ℚ)) (submission.op (submission.op (-3:ℚ) (submission.op (-3:ℚ) (-3:ℚ))) (-3:ℚ)) := h (-3:ℚ) (-3:ℚ) (-3:ℚ)
  norm_num [submission.op] at hh

def submission : Goal :=
  Exists.intro submission.carrier (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
