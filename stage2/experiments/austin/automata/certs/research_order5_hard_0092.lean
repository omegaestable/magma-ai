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

def P1 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a1 (a1 v) ∧ tg (a2 (a1 v)) = 2 ∧ u = a2 (a2 (a1 v)) ∧ tg (a2 v) = 2 ∧ u = a2 (a2 v)
instance (u v : M) : Decidable (P1 u v) := by unfold P1; infer_instance
def P2 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a1 (a1 v) ∧ tg (a2 (a1 v)) = 2 ∧ u = a2 (a2 (a1 v)) ∧ tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P2 u v) := by unfold P2; infer_instance
def P3 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a1 (a1 v) ∧ tg (a2 v) = 2 ∧ u = a2 (a2 v) ∧ tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P3 u v) := by unfold P3; infer_instance
def P4 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a1 (a1 v) ∧ tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P4 u v) := by unfold P4; infer_instance
def op (u v : M) : M :=
  let p1 := if hs1 : msr (a1 (a1 u)) (u) < msr u v then op (a1 (a1 u)) (u) else J u v
  if P1 u v then a1 (a2 v)
  else if P2 u v ∧ msr (a1 (a1 u)) (u) < msr u v ∧ a2 v = p1 then a1 (a1 u)
  else if P3 u v ∧ msr (a1 (a1 u)) (u) < msr u v ∧ a2 (a1 v) = p1 then a1 (a2 v)
  else if P4 u v ∧ msr (a1 (a1 u)) (u) < msr u v ∧ a2 (a1 v) = p1 ∧ a2 v = p1 then a1 (a1 u)
  else J u v
termination_by msr u v
decreasing_by
  · assumption


def inst : Magma M := { op := op }

def Pre (u v : M) : Prop := P1 u v ∨ P2 u v ∨ P3 u v ∨ P4 u v

theorem op_free {u v : M} (h : ¬ Pre u v) : op u v = J u v := by
  rw [op.eq_1]; simp only [Pre, not_or] at h; simp [h]

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 1) (g 0) (g 2)
  revert this
  change ¬ g 1 = op (op (g 0) (op (op (g 1) (g 1)) (g 0))) (op (g 2) (g 2))
  simp (config := {decide := true}) [op.eq_1, sz, P1, P2, P3, P4]


theorem sz_pos (t : M) : 1 ≤ sz t := by cases t <;> simp [sz] <;> omega
@[simp] theorem sz_J (a b : M) : sz (J a b) = sz a + sz b + 1 := rfl
theorem sz_a1_lt {t : M} (h : tg t = 2) : sz (a1 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a1]; have := sz_pos b; omega
theorem sz_a2_lt {t : M} (h : tg t = 2) : sz (a2 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a2]; have := sz_pos a; omega

/-- the gate of the nested call passes whenever `v` is bigger than `y` -/
theorem gate_ok {y v : M} (h : sz y < sz v) : msr (a1 (a1 y)) y < msr y v := by
  apply msr_lt_of_max_lt
  have := sz_a1 y; have := sz_a1 (a1 y); omega

/-- the unfolding of `op` with the nested call packed away as an opaque variable -/
theorem op_cases (u v : M) : ∃ p1 : M,
    p1 = (if hs1 : msr (a1 (a1 u)) u < msr u v then op (a1 (a1 u)) u else J u v) ∧
    op u v = (
  if P1 u v then a1 (a2 v)
  else if P2 u v ∧ msr (a1 (a1 u)) u < msr u v ∧ a2 v = p1 then a1 (a1 u)
  else if P3 u v ∧ msr (a1 (a1 u)) u < msr u v ∧ a2 (a1 v) = p1 then a1 (a2 v)
  else if P4 u v ∧ msr (a1 (a1 u)) u < msr u v ∧ a2 (a1 v) = p1 ∧ a2 v = p1 then a1 (a1 u)
  else J u v) :=
  ⟨_, rfl, op.eq_1 u v⟩

/-- one unfold of `op`: free, or one of the four rules with its guard -/
theorem TR (u v : M) : op u v = J u v ∨
    (P1 u v ∧ op u v = a1 (a2 v)) ∨
    (P2 u v ∧ a2 v = op (a1 (a1 u)) u ∧ op u v = a1 (a1 u)) ∨
    (P3 u v ∧ a2 (a1 v) = op (a1 (a1 u)) u ∧ op u v = a1 (a2 v)) ∨
    (P4 u v ∧ a2 (a1 v) = op (a1 (a1 u)) u ∧ a2 v = op (a1 (a1 u)) u ∧ op u v = a1 (a1 u)) := by
  obtain ⟨p1, hp1, hop⟩ := op_cases u v
  rw [hop]
  split
  · rename_i h; exact Or.inr (Or.inl ⟨h, rfl⟩)
  · split
    · rename_i h1 h
      obtain ⟨h2, hs1, he⟩ := h
      rw [dif_pos hs1] at hp1; subst hp1
      exact Or.inr (Or.inr (Or.inl ⟨h2, he, rfl⟩))
    · split
      · rename_i h1 h2 h
        obtain ⟨h3, hs1, he⟩ := h
        rw [dif_pos hs1] at hp1; subst hp1
        exact Or.inr (Or.inr (Or.inr (Or.inl ⟨h3, he, rfl⟩)))
      · split
        · rename_i h1 h2 h3 h
          obtain ⟨h4, hs1, he1, he2⟩ := h
          rw [dif_pos hs1] at hp1; subst hp1
          exact Or.inr (Or.inr (Or.inr (Or.inr ⟨h4, he1, he2, rfl⟩)))
        · left; rfl

/-- every fired rule needs `u = a1 (a1 v)`; the result is `a1 (a2 v)` (with `u = a2 (a2 v)`) or `a1 (a1 u)` (with `a2 v` decoded) -/
theorem TRm (u v : M) : op u v = J u v ∨ (tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a1 (a1 v) ∧
    ((tg (a2 v) = 2 ∧ u = a2 (a2 v) ∧ op u v = a1 (a2 v)) ∨
     (tg u = 2 ∧ tg (a1 u) = 2 ∧ a2 v = op (a1 (a1 u)) u ∧ op u v = a1 (a1 u)))) := by
  rcases TR u v with h | ⟨h1, h⟩ | ⟨h2, he, h⟩ | ⟨h3, he, h⟩ | ⟨h4, he1, he2, h⟩
  · exact Or.inl h
  · obtain ⟨t1, t2, t3, t4, t5, t6, t7⟩ := h1
    exact Or.inr ⟨t1, t2, t3, Or.inl ⟨t6, t7, h⟩⟩
  · obtain ⟨t1, t2, t3, t4, t5, t6, t7⟩ := h2
    exact Or.inr ⟨t1, t2, t3, Or.inr ⟨t6, t7, he, h⟩⟩
  · obtain ⟨t1, t2, t3, t4, t5, t6, t7⟩ := h3
    exact Or.inr ⟨t1, t2, t3, Or.inl ⟨t4, t5, h⟩⟩
  · obtain ⟨t1, t2, t3, t4, t5⟩ := h4
    exact Or.inr ⟨t1, t2, t3, Or.inr ⟨t4, t5, he2, h⟩⟩

/-- free, or `u = a1 (a1 v)` and the result is smaller than `v` -/
theorem TRw (u v : M) : op u v = J u v ∨ (tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a1 (a1 v) ∧ sz (op u v) < sz v) := by
  rcases TRm u v with h | ⟨t1, t2, t3, ⟨t6, t7, h⟩ | ⟨t6, t7, he, h⟩⟩
  · exact Or.inl h
  · right; refine ⟨t1, t2, t3, ?_⟩
    rw [h]; have := sz_a1_lt t6; have := sz_a2_lt t1; omega
  · right; refine ⟨t1, t2, t3, ?_⟩
    rw [h]; have := sz_a1 (a1 u); have := sz_a1 u; have := congrArg sz t3
    have := sz_a1_lt t1; have := sz_a1_lt t2; omega

/-- `op (a1 y) (J y (op z y))` is free or smaller than `y` (refutes the decoded gate of the fourth product) -/
theorem Kfree (y z : M) : op (a1 y) (J y (op z y)) = J (a1 y) (J y (op z y)) ∨ sz (op (a1 y) (J y (op z y))) < sz y := by
  rcases TRm (a1 y) (J y (op z y)) with h | ⟨t1, t2, t3, ⟨t6, t7, h⟩ | ⟨t6, t7, he, h⟩⟩
  · exact Or.inl h
  · simp only [a1_J_eq, a2_J_eq] at t2 t6 t7 h
    right; rw [h]
    rcases TRw z y with hA | ⟨-, -, -, hsA⟩
    · rw [hA] at t7; simp only [a2_J_eq] at t7
      have := sz_a1_lt t2; have := congrArg sz t7; omega
    · have := sz_a1 (op z y); omega
  · simp only [a1_J_eq] at t2
    right; rw [h]
    have := sz_a1_lt t2; have := sz_a1 (a1 y); have := sz_a1 (a1 (a1 y)); omega

/-- the second product `y ◇ (z ◇ y)` is always free -/
theorem B_free (y z : M) : op y (op z y) = J y (op z y) := by
  rcases TRw z y with hA | ⟨t1, t2, t3, hsA⟩
  · rw [hA]
    rcases TRm y (J z y) with h | ⟨s1, s2, s3, ⟨s6, s7, h⟩ | ⟨s6, s7, he, h⟩⟩
    · exact h
    · simp only [a2_J_eq] at s6 s7
      have := sz_a2_lt s6; have := congrArg sz s7; omega
    · simp only [a2_J_eq] at he
      rcases TRw (a1 (a1 y)) y with hq | ⟨-, -, -, hq⟩
      · rw [hq] at he; have := congrArg sz he; simp only [sz_J] at this; omega
      · rw [← he] at hq; exact absurd hq (Nat.lt_irrefl _)
  · rcases TRw y (op z y) with h | ⟨s1, s2, s3, -⟩
    · exact h
    · have := sz_a1_lt s1; have := sz_a1_lt s2; have := congrArg sz s3; omega

/-- the fourth product `(y ◇ A) ◇ C` is always free -/
theorem D_free (x y z : M) : op (J y (op z y)) (op x y) = J (J y (op z y)) (op x y) := by
  rcases TRw x y with hC | ⟨t1, t2, t3, hsC⟩
  · rw [hC]
    rcases TRm (J y (op z y)) (J x y) with h | ⟨s1, s2, s3, ⟨s6, s7, h⟩ | ⟨s6, s7, he, h⟩⟩
    · exact h
    · simp only [a2_J_eq] at s6 s7
      have := sz_a2_lt s6; have := congrArg sz s7; simp only [sz_J] at this; omega
    · simp only [a1_J_eq, a2_J_eq] at he
      rcases Kfree y z with hq | hq
      · rw [hq] at he; have := congrArg sz he; simp only [sz_J] at this; omega
      · rw [← he] at hq; exact absurd hq (Nat.lt_irrefl _)
  · rcases TRw (J y (op z y)) (op x y) with h | ⟨s1, s2, s3, -⟩
    · exact h
    · have := sz_a1_lt s1; have := sz_a1_lt s2; have := congrArg sz s3; simp only [sz_J] at this; omega

/-- R1: both `z ◇ y` and `x ◇ y` free -/
theorem op_R1 (y z x : M) : op y (J (J y (J z y)) (J x y)) = x := by
  obtain ⟨p1, -, hop⟩ := op_cases y (J (J y (J z y)) (J x y))
  have h1 : P1 y (J (J y (J z y)) (J x y)) := ⟨rfl, rfl, rfl, rfl, rfl, rfl, rfl⟩
  rw [hop, if_pos h1]
  rfl

/-- R2: `z ◇ y` free, `x ◇ y` decoded (so `x = a1 (a1 y)`) -/
theorem op_R2 (y z : M) (hy : tg y = 2) (hy1 : tg (a1 y) = 2) (hs : sz (op (a1 (a1 y)) y) < sz y) :
    op y (J (J y (J z y)) (op (a1 (a1 y)) y)) = a1 (a1 y) := by
  obtain ⟨p1, hp1, hop⟩ := op_cases y (J (J y (J z y)) (op (a1 (a1 y)) y))
  have hg : msr (a1 (a1 y)) y < msr y (J (J y (J z y)) (op (a1 (a1 y)) y)) := gate_ok (by simp only [sz_J]; omega)
  rw [dif_pos hg] at hp1; subst hp1
  rw [hop]
  split
  · rename_i h
    obtain ⟨-, -, -, -, -, -, h7⟩ := h
    simp only [a2_J_eq] at h7
    exfalso; have := sz_a2 (op (a1 (a1 y)) y); have := congrArg sz h7; omega
  · split
    · rfl
    · rename_i h1 h2
      exfalso; apply h2
      exact ⟨⟨rfl, rfl, rfl, rfl, rfl, hy, hy1⟩, hg, rfl⟩

/-- R3: `z ◇ y` decoded (so `z = a1 (a1 y)`), `x ◇ y` free -/
theorem op_R3 (y x : M) (hy : tg y = 2) (hy1 : tg (a1 y) = 2) (hs : sz (op (a1 (a1 y)) y) < sz y) :
    op y (J (J y (op (a1 (a1 y)) y)) (J x y)) = x := by
  obtain ⟨p1, hp1, hop⟩ := op_cases y (J (J y (op (a1 (a1 y)) y)) (J x y))
  have hg : msr (a1 (a1 y)) y < msr y (J (J y (op (a1 (a1 y)) y)) (J x y)) := gate_ok (by simp only [sz_J]; omega)
  rw [dif_pos hg] at hp1; subst hp1
  rw [hop]
  split
  · rfl
  · split
    · rename_i h1 h
      obtain ⟨⟨-, -, -, -, h5, -, -⟩, -, -⟩ := h
      simp only [a1_J_eq, a2_J_eq] at h5
      exfalso; have := sz_a2 (op (a1 (a1 y)) y); have := congrArg sz h5; omega
    · split
      · rfl
      · rename_i h1 h2 h3
        exfalso; apply h3
        exact ⟨⟨rfl, rfl, rfl, rfl, rfl, hy, hy1⟩, hg, rfl⟩

/-- R4: both decoded (so `x = z = a1 (a1 y)`) -/
theorem op_R4 (y : M) (hy : tg y = 2) (hy1 : tg (a1 y) = 2) (hs : sz (op (a1 (a1 y)) y) < sz y) :
    op y (J (J y (op (a1 (a1 y)) y)) (op (a1 (a1 y)) y)) = a1 (a1 y) := by
  obtain ⟨p1, hp1, hop⟩ := op_cases y (J (J y (op (a1 (a1 y)) y)) (op (a1 (a1 y)) y))
  have hg : msr (a1 (a1 y)) y < msr y (J (J y (op (a1 (a1 y)) y)) (op (a1 (a1 y)) y)) := gate_ok (by simp only [sz_J]; omega)
  rw [dif_pos hg] at hp1; subst hp1
  rw [hop]
  have hne : sz y ≠ sz (a2 (op (a1 (a1 y)) y)) := by have := sz_a2 (op (a1 (a1 y)) y); omega
  split
  · rename_i h
    obtain ⟨-, -, -, -, -, -, h7⟩ := h
    simp only [a2_J_eq] at h7
    exact absurd (congrArg sz h7) hne
  · split
    · rename_i h1 h
      obtain ⟨⟨-, -, -, -, h5, -, -⟩, -, -⟩ := h
      simp only [a1_J_eq, a2_J_eq] at h5
      exact absurd (congrArg sz h5) hne
    · split
      · rename_i h1 h2 h
        obtain ⟨⟨-, -, -, -, h5, -, -⟩, -, -⟩ := h
        simp only [a2_J_eq] at h5
        exact absurd (congrArg sz h5) hne
      · split
        · rfl
        · rename_i h1 h2 h3 h4
          exfalso; apply h4
          exact ⟨⟨rfl, rfl, rfl, hy, hy1⟩, hg, rfl, rfl⟩

/-- THE LAW: x = y * ((y * (z * y)) * (x * y)) -/
theorem law (x y z : M) : op (y) (op (op (y) (op (z) (y))) (op (x) (y))) = x := by
  rw [B_free y z, D_free x y z]
  rcases TRw z y with hA | ⟨hy, hy1, hz, hsA⟩
  · rcases TRw x y with hC | ⟨hy, hy1, hx, hsC⟩
    · rw [hA, hC]; exact op_R1 y z x
    · subst hx; rw [hA]; exact op_R2 y z hy hy1 hsC
  · subst hz
    rcases TRw x y with hC | ⟨-, -, hx, hsC⟩
    · rw [hC]; exact op_R3 y x hy hy1 hsA
    · subst hx; exact op_R4 y hy hy1 hsA


theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
