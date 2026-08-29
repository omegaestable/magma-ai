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

def P1 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ tg (a2 (a2 v)) = 2 ∧ a1 (a2 v) = a1 (a2 (a2 v)) ∧ tg (a2 (a2 (a2 v))) = 2 ∧ u = a1 (a2 (a2 (a2 v))) ∧ a1 (a2 v) = a2 (a2 (a2 (a2 v)))
instance (u v : M) : Decidable (P1 u v) := by unfold P1; infer_instance
def P2 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ tg (a2 (a2 v)) = 2 ∧ a1 (a2 v) = a1 (a2 (a2 v))
instance (u v : M) : Decidable (P2 u v) := by unfold P2; infer_instance
def P3 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2
instance (u v : M) : Decidable (P3 u v) := by unfold P3; infer_instance
def op (u v : M) : M :=
  let p1 := if hs1 : msr (u) (a1 (a2 v)) < msr u v then op (u) (a1 (a2 v)) else J u v
  let p2 := if hs2 : msr (a1 (a2 v)) (p1) < msr u v then op (a1 (a2 v)) (p1) else J u v
  if P1 u v then a1 v
  else if P2 u v ∧ msr (u) (a1 (a2 v)) < msr u v ∧ a2 (a2 (a2 v)) = p1 then a1 v
  else if P3 u v ∧ msr (u) (a1 (a2 v)) < msr u v ∧ msr (a1 (a2 v)) (p1) < msr u v ∧ a2 (a2 v) = p2 then a1 v
  else J u v
termination_by msr u v
decreasing_by
  · assumption
  · assumption


def inst : Magma M := { op := fun a b => op b a }

def Pre (u v : M) : Prop := P1 u v ∨ P2 u v ∨ P3 u v

theorem op_free {u v : M} (h : ¬ Pre u v) : op u v = J u v := by
  rw [op.eq_1]; simp only [Pre, not_or] at h; simp [h]

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 0) (g 0) (g 0)
  revert this
  change ¬ g 0 = op (op (op (op (op (g 0) (g 0)) (g 0)) (g 0)) (g 0)) (g 0)
  simp (config := {decide := true}) [op.eq_1, sz, P1, P2, P3]
theorem sz_pos (t : M) : 1 ≤ sz t := by cases t <;> simp [sz] <;> omega
@[simp] theorem sz_J (a b : M) : sz (J a b) = sz a + sz b + 1 := rfl
theorem sz_a1_lt {t : M} (h : tg t = 2) : sz (a1 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a1]; have := sz_pos b; omega
theorem sz_a2_lt {t : M} (h : tg t = 2) : sz (a2 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a2]; have := sz_pos a; omega
theorem msr_lt_r {u b v : M} (h : sz b < sz v) : msr u b < msr u v := by
  have hm : max (sz u) (sz b) ≤ max (sz u) (sz v) := by omega
  rcases Nat.lt_or_eq_of_le hm with hlt | heq
  · exact msr_lt_of_max_lt hlt
  · exact msr_lt_of_max_eq heq (by omega)
theorem msr_lt_both {a b u v : M} (ha : sz a < sz v) (hb : sz b < sz v) : msr a b < msr u v :=
  msr_lt_of_max_lt (by omega)

theorem msr_J_nlt (u v w : M) : ¬ msr w (J u v) < msr u v := by
  have : msr u v < msr w (J u v) := msr_lt_of_max_lt (by simp only [sz_J]; omega)
  omega

/-- one-unfold characterisation: free, or one of the three rules fired (with its guards). -/
theorem TR (u v : M) : op u v = J u v ∨
    (P1 u v ∧ op u v = a1 v) ∨
    (P2 u v ∧ msr u (a1 (a2 v)) < msr u v ∧ a2 (a2 (a2 v)) = op u (a1 (a2 v)) ∧ op u v = a1 v) ∨
    (P3 u v ∧ msr u (a1 (a2 v)) < msr u v ∧ msr (a1 (a2 v)) (op u (a1 (a2 v))) < msr u v ∧
      a2 (a2 v) = op (a1 (a2 v)) (op u (a1 (a2 v))) ∧ op u v = a1 v) := by
  rw [op.eq_1]
  by_cases hg1 : msr u (a1 (a2 v)) < msr u v
  · rw [dif_pos hg1]
    by_cases hg2 : msr (a1 (a2 v)) (op u (a1 (a2 v))) < msr u v
    · rw [dif_pos hg2]
      split
      · rename_i h1; exact Or.inr (Or.inl ⟨h1, rfl⟩)
      · split
        · rename_i h1 h2
          exact Or.inr (Or.inr (Or.inl ⟨h2.1, hg1, h2.2.2, rfl⟩))
        · split
          · rename_i h1 h2 h3
            exact Or.inr (Or.inr (Or.inr ⟨h3.1, hg1, hg2, h3.2.2.2, rfl⟩))
          · left; rfl
    · rw [dif_neg hg2]
      split
      · rename_i h1; exact Or.inr (Or.inl ⟨h1, rfl⟩)
      · split
        · rename_i h1 h2
          exact Or.inr (Or.inr (Or.inl ⟨h2.1, hg1, h2.2.2, rfl⟩))
        · split
          · rename_i h1 h2 h3; exact absurd h3.2.2.1 hg2
          · left; rfl
  · rw [dif_neg hg1, dif_neg (msr_J_nlt u v _)]
    split
    · rename_i h1; exact Or.inr (Or.inl ⟨h1, rfl⟩)
    · split
      · rename_i h1 h2; exact absurd h2.2.1 hg1
      · split
        · rename_i h1 h2 h3; exact absurd h3.2.1 hg1
        · left; rfl

theorem op_cases (u v : M) : op u v = J u v ∨ (tg v = 2 ∧ op u v = a1 v) := by
  rcases TR u v with h | ⟨h1, h⟩ | ⟨h2, _, _, h⟩ | ⟨h3, _, _, _, h⟩
  · exact Or.inl h
  · exact Or.inr ⟨h1.1, h⟩
  · exact Or.inr ⟨h2.1, h⟩
  · exact Or.inr ⟨h3.1, h⟩

theorem op_fire3 {u v : M} (h : P3 u v) (g1 : msr u (a1 (a2 v)) < msr u v)
    (g2 : msr (a1 (a2 v)) (op u (a1 (a2 v))) < msr u v)
    (h3 : a2 (a2 v) = op (a1 (a2 v)) (op u (a1 (a2 v)))) : op u v = a1 v := by
  rw [op.eq_1]
  simp only [dif_pos g1, dif_pos g2]
  split
  · rfl
  · split
    · rfl
    · split
      · rfl
      · rename_i hn; exact absurd ⟨h, g1, g2, h3⟩ hn

/-- KEY: no rule fires on (z, w) when w is no bigger than z (induction on the size of w). -/
theorem NOFIRE (n : Nat) : ∀ z w : M, sz w ≤ n → sz w ≤ sz z → op z w = J z w := by
  induction n with
  | zero => intro z w h _; have := sz_pos w; omega
  | succ n ih =>
    intro z w hn hz
    rcases TR z w with h | ⟨h1, _⟩ | ⟨h2, hg, h3, _⟩ | ⟨h3, hg1, hg2, h5, _⟩
    · exact h
    · obtain ⟨t1, t2, t3, t4, t5, t6, t7⟩ := h1
      have := sz_a2_lt t1
      have := sz_a2 (a2 w)
      have := sz_a2 (a2 (a2 w))
      have := sz_a1 (a2 (a2 (a2 w)))
      have := congrArg sz t6
      omega
    · obtain ⟨t1, t2, t3, t4⟩ := h2
      have e1 := sz_a2_lt t1
      have e2 := sz_a2_lt t2
      have e3 := sz_a2_lt t3
      have e4 := sz_a1 (a2 w)
      have hv : op z (a1 (a2 w)) = J z (a1 (a2 w)) := ih z _ (by omega) (by omega)
      rw [hv] at h3
      have := congrArg sz h3
      simp only [sz_J] at this
      omega
    · obtain ⟨t1, t2⟩ := h3
      have e1 := sz_a2_lt t1
      have e2 := sz_a2_lt t2
      have e4 := sz_a1 (a2 w)
      have hv : op z (a1 (a2 w)) = J z (a1 (a2 w)) := ih z _ (by omega) (by omega)
      rw [hv] at h5
      rcases op_cases (a1 (a2 w)) (J z (a1 (a2 w))) with hq | ⟨_, hq⟩ <;> rw [hq] at h5
      · have := congrArg sz h5; simp only [sz_J] at this; omega
      · simp only [a1_J_eq] at h5; have := congrArg sz h5; omega

theorem nofire {z w : M} (h : sz w ≤ sz z) : op z w = J z w := NOFIRE (sz w) z w (Nat.le_refl _) h

/-- `a ◇ (b ◇ a)` is always free. -/
theorem JF (a b : M) : op a (J b a) = J a (J b a) := by
  rcases TR a (J b a) with h | ⟨h1, _⟩ | ⟨h2, hg, h3, _⟩ | ⟨h3, hg1, hg2, h5, _⟩
  · exact h
  · obtain ⟨t1, t2, t3, t4, t5, t6, t7⟩ := h1
    simp only [a2_J_eq] at t2 t6
    have := sz_a2_lt t2
    have := sz_a2 (a2 a)
    have := sz_a1 (a2 (a2 a))
    have := congrArg sz t6
    omega
  · obtain ⟨t1, t2, t3, t4⟩ := h2
    simp only [a2_J_eq, a1_J_eq] at t2 h3
    rw [nofire (sz_a1 a)] at h3
    have := congrArg sz h3
    simp only [sz_J] at this
    have := sz_a2_lt t2
    have := sz_a2 (a2 a)
    omega
  · obtain ⟨t1, t2⟩ := h3
    simp only [a2_J_eq, a1_J_eq] at t2 h5
    rw [nofire (sz_a1 a)] at h5
    have := sz_a2_lt t2
    rcases op_cases (a1 a) (J a (a1 a)) with hq | ⟨_, hq⟩ <;> rw [hq] at h5
    · have := congrArg sz h5; simp only [sz_J] at this; omega
    · simp only [a1_J_eq] at h5; have := congrArg sz h5; omega

/-- step 2: `z ◇ (y ◇ z)` is free. -/
theorem B_free (y z : M) : op z (op y z) = J z (op y z) := by
  rcases op_cases y z with hA | ⟨_, hA⟩ <;> rw [hA]
  · exact JF z y
  · exact nofire (sz_a1 z)

/-- step 3: `z ◇ (z ◇ (y ◇ z))` is free. -/
theorem C_free (y z : M) : op z (J z (op y z)) = J z (J z (op y z)) := by
  rcases TR z (J z (op y z)) with h | ⟨h1, _⟩ | ⟨h2, hg, h3, _⟩ | ⟨h3, hg1, hg2, h5, _⟩
  · exact h
  · obtain ⟨t1, t2, t3, t4, t5, t6, t7⟩ := h1
    simp only [a2_J_eq, a1_J_eq] at t2 t3 t6
    have := sz_a2_lt t2
    have := sz_a2 (a2 (op y z))
    have := sz_a1 (a2 (a2 (op y z)))
    have := congrArg sz t6
    rcases op_cases y z with hA | ⟨_, hA⟩
    · rw [hA] at t3 t6
      simp only [a2_J_eq] at t3 t6
      have := sz_a2_lt t3
      have := sz_a1 (a2 z)
      have := congrArg sz t6
      omega
    · have := congrArg sz hA; have := sz_a1 z; omega
  · obtain ⟨t1, t2, t3, t4⟩ := h2
    simp only [a2_J_eq, a1_J_eq] at t2 t3 t4 h3
    have := sz_a2_lt t2
    have := sz_a2_lt t3
    have := sz_a1 (op y z)
    rcases op_cases y z with hA | ⟨_, hA⟩
    · rw [hA] at t3 t4 h3
      simp only [a2_J_eq, a1_J_eq] at t3 t4 h3
      have := sz_a2_lt t3
      have hy : sz y ≤ sz z := by have := congrArg sz t4; have := sz_a1 z; omega
      rw [nofire hy] at h3
      have := congrArg sz h3
      simp only [sz_J] at this
      omega
    · have hq : sz (a1 (op y z)) ≤ sz z := by
        have := congrArg sz hA; have := sz_a1 (op y z); have := sz_a1 z; omega
      rw [nofire hq] at h3
      have := congrArg sz h3
      simp only [sz_J] at this
      have := congrArg sz hA
      have := sz_a1 z
      omega
  · obtain ⟨t1, t2⟩ := h3
    simp only [a2_J_eq, a1_J_eq] at t2 h5
    have := sz_a2_lt t2
    have := sz_a1 (op y z)
    rcases op_cases y z with hA | ⟨_, hA⟩
    · rw [hA] at h5
      simp only [a2_J_eq, a1_J_eq] at h5
      rcases op_cases z y with hB | ⟨_, hB⟩ <;> rw [hB] at h5
      · rw [JF y z] at h5
        have := congrArg sz h5
        simp only [sz_J] at this
        omega
      · rw [nofire (sz_a1 y)] at h5
        have hz : sz y ≤ sz z := by
          have := congrArg sz h5; simp only [sz_J] at this; omega
        rw [nofire hz] at hB
        have := congrArg sz hB
        simp only [sz_J] at this
        have := sz_a1 y
        omega
    · have hq : sz (a1 (op y z)) ≤ sz z := by
        have := congrArg sz hA; have := sz_a1 (op y z); have := sz_a1 z; omega
      rw [nofire hq] at h5
      have := congrArg sz hA
      have := sz_a1 z
      rcases op_cases (a1 (op y z)) (J z (a1 (op y z))) with hq2 | ⟨_, hq2⟩ <;> rw [hq2] at h5
      · have := congrArg sz h5; simp only [sz_J] at this; omega
      · simp only [a1_J_eq] at h5; have := congrArg sz h5; omega

/-- step 4: `x ◇ (z ◇ (z ◇ (y ◇ z)))` is free. -/
theorem D_free (x y z : M) : op x (J z (J z (op y z))) = J x (J z (J z (op y z))) := by
  rcases TR x (J z (J z (op y z))) with h | ⟨h1, _⟩ | ⟨h2, hg, h3, _⟩ | ⟨h3, hg1, hg2, h5, _⟩
  · exact h
  · obtain ⟨t1, t2, t3, t4, t5, t6, t7⟩ := h1
    simp only [a2_J_eq, a1_J_eq] at t3 t5 t7
    have := sz_a2_lt t3
    have := sz_a2_lt t5
    have := congrArg sz t7
    rcases op_cases y z with hA | ⟨_, hA⟩
    · rw [hA] at t5 t7
      simp only [a2_J_eq] at t5 t7
      have := sz_a2_lt t5
      have := congrArg sz t7
      omega
    · have := congrArg sz hA; have := sz_a1 z; omega
  · obtain ⟨t1, t2, t3, t4⟩ := h2
    simp only [a2_J_eq, a1_J_eq] at t3 t4 h3
    have := sz_a2_lt t3
    rcases op_cases y z with hA | ⟨_, hA⟩
    · rw [hA] at h3
      simp only [a2_J_eq] at h3
      rcases op_cases x z with hB | ⟨ht, hB⟩ <;> rw [hB] at h3
      · have := congrArg sz h3; simp only [sz_J] at this; omega
      · have := congrArg sz h3; have := sz_a1_lt ht; omega
    · have := congrArg sz hA
      have := sz_a1 z
      rcases op_cases x z with hB | ⟨ht, hB⟩ <;> rw [hB] at h3
      · have := congrArg sz h3; simp only [sz_J] at this; omega
      · have := congrArg sz h3; omega
  · obtain ⟨t1, t2⟩ := h3
    simp only [a2_J_eq, a1_J_eq] at h5
    rw [B_free x z] at h5
    rcases op_cases y z with hA | ⟨_, hA⟩
    · rw [hA] at h5
      obtain ⟨_, h6⟩ := M.J.inj h5
      rcases op_cases x z with hB | ⟨ht, hB⟩ <;> rw [hB] at h6
      · have := congrArg sz h6; simp only [sz_J] at this; omega
      · have := congrArg sz h6; have := sz_a1_lt ht; omega
    · rw [hA] at h5
      have := congrArg sz h5
      simp only [sz_J] at this
      have := sz_a1 z
      omega

/-- THE LAW: x = y * (x * (z * (z * (y * z)))) -/
theorem law (x y z : M) : op (y) (op (x) (op (z) (op (z) (op (y) (z))))) = x := by
  rw [B_free, C_free, D_free]
  apply op_fire3
  · exact ⟨rfl, rfl⟩
  · simp only [a2_J_eq, a1_J_eq]
    apply msr_lt_r
    simp only [sz_J]
    omega
  · simp only [a2_J_eq, a1_J_eq]
    apply msr_lt_both <;> simp only [sz_J] <;> omega
  · simp only [a2_J_eq, a1_J_eq]
    exact (B_free y z).symm


theorem lhs : @EquationLHS M inst := by
  intro x y z
  first | exact (law x y z).symm | exact (law x z y).symm | exact (law y x z).symm | exact (law y z x).symm | exact (law z x y).symm | exact (law z y x).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
