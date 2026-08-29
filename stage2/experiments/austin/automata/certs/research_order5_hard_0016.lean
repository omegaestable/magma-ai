import JudgeProblem
set_option linter.unusedSimpArgs false
set_option linter.unusedVariables false
set_option warn.classDefReducibility false

inductive submission.M : Type where
  | g : Nat → submission.M
  | J : submission.M → submission.M → submission.M
  deriving DecidableEq

namespace submission
open M

def tg : M → Nat
  | .g _ => 1
  | .J _ _ => 2
def a1 : M → M
  | .J x _ => x
  | t => t
def a2 : M → M
  | .J _ x => x
  | t => t
def sz : M → Nat
  | .g _ => 1
  | .J b0 b1 => sz b0 + sz b1 + 1
theorem sz_a1 (u : M) : sz (a1 u) ≤ sz u := by cases u <;> simp [a1, sz] <;> omega
theorem sz_a2 (u : M) : sz (a2 u) ≤ sz u := by cases u <;> simp [a2, sz] <;> omega
theorem tg_J (t : M) (h : tg t = 2) : ∃ b0 b1, t = M.J b0 b1 := by cases t <;> simp_all [tg]
theorem tg_g (t : M) (h : tg t ≠ 2) : ∃ n, t = M.g n := by cases t <;> simp_all [tg]
theorem sz_tg (t : M) (h : tg t = 2) : sz t = sz (a1 t) + sz (a2 t) + 1 := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a1, a2]
@[simp] theorem tg_g_eq (n : Nat) : tg (M.g n) = 1 := rfl
@[simp] theorem tg_J_eq (b0 b1 : M) : tg (M.J b0 b1) = 2 := rfl
@[simp] theorem a1_J_eq (b0 b1 : M) : a1 (M.J b0 b1) = b0 := rfl
@[simp] theorem a2_J_eq (b0 b1 : M) : a2 (M.J b0 b1) = b1 := rfl
@[simp] theorem a1_g_eq (n : Nat) : a1 (M.g n) = M.g n := rfl
@[simp] theorem a2_g_eq (n : Nat) : a2 (M.g n) = M.g n := rfl
/-- the recursion measure: lexicographic (max size, total size), packed into one Nat -/
def msr (u v : M) : Nat := max (sz u) (sz v) * max (sz u) (sz v) + sz u + sz v
theorem msr_lt_of_max_lt {a b u v : M} (h : max (sz a) (sz b) < max (sz u) (sz v)) : msr a b < msr u v := by
  unfold msr
  have h1 : sz a + sz b ≤ 2 * max (sz a) (sz b) := by omega
  have h2 : (max (sz a) (sz b) + 1) * (max (sz a) (sz b) + 1) ≤ max (sz u) (sz v) * max (sz u) (sz v) := Nat.mul_le_mul h h
  simp only [Nat.mul_succ, Nat.succ_mul] at h2
  omega
theorem msr_lt_of_max_eq {a b u v : M} (h : max (sz a) (sz b) = max (sz u) (sz v)) (h2 : sz a + sz b < sz u + sz v) : msr a b < msr u v := by
  unfold msr; rw [h]; omega

def P1 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a1 (a2 v) ∧ tg (a2 (a2 v)) = 2 ∧ tg (a2 (a2 (a2 v))) = 2 ∧ a1 v = a1 (a2 (a2 (a2 v))) ∧ a1 (a2 (a2 v)) = a2 (a2 (a2 (a2 v)))
instance (u v : M) : Decidable (P1 u v) := by unfold P1; infer_instance
def P2 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a1 (a2 v) ∧ tg (a2 (a2 v)) = 2
instance (u v : M) : Decidable (P2 u v) := by unfold P2; infer_instance
def op (u v : M) : M :=
  let p1 := if hs1 : msr (a1 v) (a1 (a2 (a2 v))) < msr u v then op (a1 v) (a1 (a2 (a2 v))) else J u v
  if P1 u v then a1 v
  else if P2 u v ∧ msr (a1 v) (a1 (a2 (a2 v))) < msr u v ∧ a2 (a2 (a2 v)) = p1 then a1 v
  else J u v
termination_by msr u v
decreasing_by
  · assumption


def inst : Magma M := { op := fun a b => op b a }

def Pre (u v : M) : Prop := P1 u v ∨ P2 u v

theorem op_free {u v : M} (h : ¬ Pre u v) : op u v = J u v := by
  rw [op.eq_1]; simp only [Pre, not_or] at h; simp [h]

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 1) (g 0) (g 2)
  revert this
  change ¬ g 1 = op (op (op (op (op (g 2) (g 2)) (g 0)) (g 1)) (g 1)) (g 0)
  simp (config := {decide := true}) [op.eq_1, sz, P1, P2]


theorem P1_P2 {u v : M} (h : P1 u v) : P2 u v := ⟨h.1, h.2.1, h.2.2.1, h.2.2.2.1⟩

/-- the three size equations carried by the R2 shape `v = J _ (J u (J _ _))` -/
theorem P2_sz {u v : M} (h : P2 u v) : sz v = sz (a1 v) + sz (a2 v) + 1 ∧ sz (a2 v) = sz u + sz (a2 (a2 v)) + 1 ∧
    sz (a2 (a2 v)) = sz (a1 (a2 (a2 v))) + sz (a2 (a2 (a2 v))) + 1 := by
  obtain ⟨h1, h2, h3, h4⟩ := h
  have t1 := sz_tg v h1
  have t2 := sz_tg (a2 v) h2
  have t3 := sz_tg (a2 (a2 v)) h4
  rw [← h3] at t2
  exact ⟨t1, t2, t3⟩

/-- the extra size equation of the R1 shape `v = J x (J u (J y (J x y)))` -/
theorem P1_sz {u v : M} (h : P1 u v) : sz (a2 (a2 (a2 v))) = sz (a1 v) + sz (a1 (a2 (a2 v))) + 1 := by
  obtain ⟨h1, h2, h3, h4, h5, h6, h7⟩ := h
  have t := sz_tg _ h5
  rw [← h6, ← h7] at t
  exact t

/-- the unfolding of `op` with the nested call packed away as an opaque variable -/
theorem op_cases (u v : M) : ∃ p1 : M,
    p1 = (if hs1 : msr (a1 v) (a1 (a2 (a2 v))) < msr u v then op (a1 v) (a1 (a2 (a2 v))) else J u v) ∧
    op u v = (
  if P1 u v then a1 v
  else if P2 u v ∧ msr (a1 v) (a1 (a2 (a2 v))) < msr u v ∧ a2 (a2 (a2 v)) = p1 then a1 v
  else J u v) :=
  ⟨_, rfl, op.eq_1 u v⟩

/-- one unfold of `op`: free, or R1, or R2 with its guard -/
theorem TR (u v : M) : op u v = J u v ∨ (P1 u v ∧ op u v = a1 v) ∨
    (P2 u v ∧ a2 (a2 (a2 v)) = op (a1 v) (a1 (a2 (a2 v))) ∧ op u v = a1 v) := by
  obtain ⟨p1, hp1, hop⟩ := op_cases u v
  rw [hop]
  split
  · rename_i h; exact Or.inr (Or.inl ⟨h, rfl⟩)
  · split
    · rename_i h1 h
      obtain ⟨h2, hs1, he⟩ := h
      rw [dif_pos hs1] at hp1; subst hp1
      exact Or.inr (Or.inr ⟨h2, he, rfl⟩)
    · left; rfl

/-- no rule fires unless `u` sits strictly inside `a2 v` -/
theorem NF {u v : M} (h : sz (a2 v) ≤ sz u) : op u v = J u v := by
  rcases TR u v with h' | ⟨h1, -⟩ | ⟨h1, -, -⟩
  · exact h'
  · have := P2_sz (P1_P2 h1); omega
  · have := P2_sz h1; omega

/-- whatever `op x y` is, its second component sits inside `y` -/
theorem sz_a2_op (x y : M) : sz (a2 (op x y)) ≤ sz y := by
  rcases TR x y with h | ⟨-, h⟩ | ⟨-, -, h⟩
  · rw [h, a2_J_eq]; exact Nat.le_refl _
  · rw [h]; have := sz_a2 (a1 y); have := sz_a1 y; omega
  · rw [h]; have := sz_a2 (a1 y); have := sz_a1 y; omega

/-- product 2 of the law is free -/
theorem N2 (x y : M) : op y (op x y) = J y (op x y) := NF (sz_a2_op x y)

/-- product 3 of the law is free -/
theorem N3 (x y z : M) : op z (J y (op x y)) = J z (J y (op x y)) := by
  have s := sz_a2_op x y
  have s1 := sz_a2 (a2 (op x y))
  have s2 := sz_a1 (a2 (op x y))
  have s3 := sz_a2 (a1 (a2 (op x y)))
  rcases TR z (J y (op x y)) with h | ⟨h1, -⟩ | ⟨h1, he, -⟩
  · exact h
  · have t := P1_sz h1
    simp only [a1_J_eq, a2_J_eq] at t
    omega
  · simp only [a1_J_eq, a2_J_eq] at he
    rw [NF (by omega : sz (a2 (a1 (a2 (op x y)))) ≤ sz y)] at he
    have := congrArg sz he
    simp only [sz] at this
    omega

/-- product 4 of the law is free -/
theorem N4 (x y z : M) : op x (J z (J y (op x y))) = J x (J z (J y (op x y))) := by
  rcases TR x (J z (J y (op x y))) with h | ⟨h1, -⟩ | ⟨h1, he, -⟩
  · exact h
  · obtain ⟨-, -, h3, -, h5, -, h7⟩ := h1
    simp only [a1_J_eq, a2_J_eq] at h3 h5 h7
    subst h3
    rw [NF (sz_a2 _)] at h5 h7
    simp only [a1_J_eq, a2_J_eq] at h5 h7
    have := sz_tg _ h5
    have := congrArg sz h7
    omega
  · obtain ⟨-, -, h3, -⟩ := h1
    simp only [a1_J_eq, a2_J_eq] at h3 he
    subst h3
    rw [NF (sz_a2 _)] at he
    simp only [a1_J_eq, a2_J_eq] at he
    rcases TR z x with h' | ⟨h1', h'⟩ | ⟨h1', -, h'⟩
    · rw [h'] at he; have := congrArg sz he; simp only [sz] at this; omega
    · rw [h'] at he; have := (P2_sz (P1_P2 h1')).1; have := congrArg sz he; omega
    · rw [h'] at he; have := (P2_sz h1').1; have := congrArg sz he; omega

/-- product 5: rule R1 or R2 fires and returns `x` -/
theorem R2 (x y z : M) : op z (J x (J z (J y (op x y)))) = x := by
  obtain ⟨p1, hp1, hop⟩ := op_cases z (J x (J z (J y (op x y))))
  have hs1 : msr (a1 (J x (J z (J y (op x y))))) (a1 (a2 (a2 (J x (J z (J y (op x y))))))) < msr z (J x (J z (J y (op x y)))) := by
    simp only [a1_J_eq, a2_J_eq]
    apply msr_lt_of_max_lt
    simp only [sz]
    omega
  rw [dif_pos hs1] at hp1; subst hp1
  rw [hop]
  split
  · rfl
  · split
    · rfl
    · rename_i h1 h2
      exfalso; apply h2
      exact ⟨⟨rfl, rfl, rfl, rfl⟩, hs1, rfl⟩

/-- THE LAW: x = ((((y * x) * y) * z) * x) * z (stated for the DUAL L-form law; the served magma flips op, so EquationLHS unfolds to exactly this) -/
theorem law (x y z : M) : op (z) (op (x) (op (z) (op (y) (op (x) (y))))) = x := by
  rw [N2, N3, N4]
  exact R2 x y z


theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
