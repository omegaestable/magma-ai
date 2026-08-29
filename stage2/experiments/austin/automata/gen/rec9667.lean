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

def P1 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a2 (a1 v) ∧ tg (a2 v) = 2 ∧ tg (a2 (a2 v)) = 2 ∧ u = a1 (a2 (a2 v)) ∧ u = a2 (a2 (a2 v))
instance (u v : M) : Decidable (P1 u v) := by unfold P1; infer_instance
def P2 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ tg (a2 (a2 v)) = 2 ∧ u = a1 (a2 (a2 v)) ∧ u = a2 (a2 (a2 v)) ∧ tg u = 2 ∧ tg (a2 u) = 2 ∧ tg (a2 (a2 u)) = 2
instance (u v : M) : Decidable (P2 u v) := by unfold P2; infer_instance
def op (u v : M) : M :=
  let p1 := if hs1 : msr (a1 (a2 (a2 u))) (u) < msr u v then op (a1 (a2 (a2 u))) (u) else J u v
  if P1 u v then a1 (a2 v)
  else if P2 u v ∧ msr (a1 (a2 (a2 u))) (u) < msr u v ∧ a1 v = p1 then a1 (a2 v)
  else J u v
termination_by msr u v
decreasing_by
  · assumption


def inst : Magma M := { op := op }

def Pre (u v : M) : Prop := P1 u v ∨ P2 u v

theorem op_free {u v : M} (h : ¬ Pre u v) : op u v = J u v := by
  rw [op.eq_1]; simp only [Pre, not_or] at h; simp [h]

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 1) (g 0) (g 2)
  revert this
  change ¬ g 1 = op (op (g 0) (op (op (g 1) (g 1)) (g 0))) (op (g 2) (g 2))
  simp (config := {decide := true}) [op.eq_1, sz, P1, P2]


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

/-- one-unfold characterisation: free, or R1 (P1) fired, or R2 (P2) fired with its guard. -/
theorem TR (u v : M) : op u v = J u v ∨
    (P1 u v ∧ op u v = a1 (a2 v)) ∨
    (P2 u v ∧ msr (a1 (a2 (a2 u))) u < msr u v ∧ a1 v = op (a1 (a2 (a2 u))) u ∧ op u v = a1 (a2 v)) := by
  rw [op.eq_1]
  by_cases hg1 : msr (a1 (a2 (a2 u))) (u) < msr u v
  · rw [dif_pos hg1]
    split
    · rename_i h1; exact Or.inr (Or.inl ⟨h1, rfl⟩)
    · split
      · rename_i h1 h2; exact Or.inr (Or.inr ⟨h2.1, hg1, h2.2.2, rfl⟩)
      · left; rfl
  · rw [dif_neg hg1]
    split
    · rename_i h1; exact Or.inr (Or.inl ⟨h1, rfl⟩)
    · split
      · rename_i h1 h2; exact absurd h2.2.1 hg1
      · left; rfl

theorem op_val (u v : M) : op u v = J u v ∨ op u v = a1 (a2 v) := by
  rcases TR u v with h | ⟨_, h⟩ | ⟨_, _, _, h⟩
  · exact Or.inl h
  · exact Or.inr h
  · exact Or.inr h

/-- if `op u v` reduces, the encoding shape holds: `u = a2 (a2 (a2 v))` and the three tags. -/
theorem fire_needs {u v : M} (h : op u v ≠ J u v) :
    u = a2 (a2 (a2 v)) ∧ tg v = 2 ∧ tg (a2 v) = 2 ∧ tg (a2 (a2 v)) = 2 := by
  rcases TR u v with hf | ⟨hp, _⟩ | ⟨hp, _, _, _⟩
  · exact absurd hf h
  · exact ⟨hp.2.2.2.2.2.2, hp.1, hp.2.2.2.1, hp.2.2.2.2.1⟩
  · exact ⟨hp.2.2.2.2.1, hp.1, hp.2.1, hp.2.2.1⟩

/-- KEY: no rule fires on `(z, w)` when `w` is no bigger than `z` (both rules need `z = a2^3 w`). -/
theorem nofire {z w : M} (h : sz w ≤ sz z) : op z w = J z w := by
  rcases TR z w with hf | ⟨h1, _⟩ | ⟨h2, _, _, _⟩
  · exact hf
  · obtain ⟨tw, _, _, _, _, _, hz⟩ := h1
    have := sz_a2_lt tw; have := sz_a2 (a2 w); have := sz_a2 (a2 (a2 w)); have := congrArg sz hz; omega
  · obtain ⟨tw, _, _, _, hz, _, _, _⟩ := h2
    have := sz_a2_lt tw; have := sz_a2 (a2 w); have := sz_a2 (a2 (a2 w)); have := congrArg sz hz; omega

/-- `op a (J x (J y y))` is free unless `a = a2 y`: firing needs `a = a2 (a2 (a2 (J x (J y y)))) = a2 y`. -/
theorem mid_free {a x y : M} (h : sz a ≠ sz (a2 y)) : op a (J x (J y y)) = J a (J x (J y y)) := by
  rcases TR a (J x (J y y)) with hf | ⟨hp, _⟩ | ⟨hp, _, _, _⟩
  · exact hf
  · have he : a = a2 y := by have := hp.2.2.2.2.2.2; simpa using this
    exact absurd (congrArg sz he) h
  · have he : a = a2 y := by have := hp.2.2.2.2.1; simpa using this
    exact absurd (congrArg sz he) h

/-- `op x (op y y) = op x (J y y)` is always free. -/
theorem xyy_free (x y : M) : op x (J y y) = J x (J y y) := by
  rcases TR x (J y y) with hf | ⟨hp, _⟩ | ⟨hp, _, hguard, _⟩
  · exact hf
  · exfalso
    obtain ⟨_, _, e2, _, t4, _, e6⟩ := hp
    simp only [a1_J_eq, a2_J_eq] at e2 t4 e6
    rw [← e2] at t4 e6
    have := sz_a2_lt t4; have := congrArg sz e6; omega
  · exfalso
    obtain ⟨_, _, _, _, e4, t5, _, _⟩ := hp
    simp only [a1_J_eq, a2_J_eq] at e4 hguard
    rcases op_val (a1 (a2 (a2 x))) x with hq | hq <;> rw [hq] at hguard
    · have hay : a2 y = x := by simp [hguard]
      rw [hay] at e4
      have := sz_a2_lt t5; have := congrArg sz e4; omega
    · have := sz_a2_lt t5; have := sz_a1 (a2 x); have := congrArg sz hguard
      have := sz_a2 (a2 y); have := sz_a2 y; have := congrArg sz e4; omega

theorem op_cases (u v : M) : ∃ p1 : M,
    p1 = (if hs1 : msr (a1 (a2 (a2 u))) (u) < msr u v then op (a1 (a2 (a2 u))) (u) else J u v) ∧
    op u v = (if P1 u v then a1 (a2 v)
      else if P2 u v ∧ msr (a1 (a2 (a2 u))) (u) < msr u v ∧ a1 v = p1 then a1 (a2 v)
      else J u v) :=
  ⟨_, rfl, op.eq_1 u v⟩

theorem op_fire1 {u v : M} (h : P1 u v) : op u v = a1 (a2 v) := by
  obtain ⟨p1, _, hop⟩ := op_cases u v
  rw [hop, if_pos h]

theorem op_fire2 {u v : M} (h2 : P2 u v) (g1 : msr (a1 (a2 (a2 u))) u < msr u v)
    (hguard : a1 v = op (a1 (a2 (a2 u))) u) : op u v = a1 (a2 v) := by
  obtain ⟨p1, hp1, hop⟩ := op_cases u v
  rw [dif_pos g1] at hp1
  rw [hop]
  split
  · rfl
  · rw [if_pos ⟨h2, g1, by rw [hp1]; exact hguard⟩]

/-- THE LAW: x = y * ((z * y) * (x * (y * y))) -/
theorem law (x y z : M) : op (y) (op (op (z) (y)) (op (x) (op (y) (y)))) = x := by
  rw [nofire (z := y) (w := y) (Nat.le_refl _), xyy_free x y]
  rcases TR z y with hzy | ⟨hp1, hzy⟩ | ⟨hp2, _, _, hzy⟩
  · -- op z y free: outer fires R1 (P1)
    rw [hzy, mid_free (a := J z y) (x := x) (y := y) (by simp only [sz_J]; have := sz_a2 y; omega)]
    rw [op_fire1 (u := y) (v := J (J z y) (J x (J y y))) ⟨rfl, rfl, rfl, rfl, rfl, rfl, rfl⟩]
    simp only [a2_J_eq, a1_J_eq]
  · -- op z y reduced via P1 z y: outer fires R2 (P2)
    rw [hzy, mid_free (a := a1 (a2 y)) (x := x) (y := y)
        (by have := sz_a1_lt (show tg (a2 y) = 2 from hp1.2.2.2.1); omega)]
    rw [op_fire2 (u := y) (v := J (a1 (a2 y)) (J x (J y y)))
      ⟨rfl, rfl, rfl, rfl, rfl, hp1.1, hp1.2.2.2.1, hp1.2.2.2.2.1⟩
      (by apply msr_lt_both
          · simp only [sz_J]; have := sz_a1 (a2 (a2 y)); have := sz_a2 (a2 y); have := sz_a2 y; omega
          · simp only [sz_J]; omega)
      (by simp only [a1_J_eq]; rw [← hp1.2.2.2.2.2.1, hzy])]
    simp only [a2_J_eq, a1_J_eq]
  · -- op z y reduced via P2 z y: outer fires R2 (P2)
    rw [hzy, mid_free (a := a1 (a2 y)) (x := x) (y := y)
        (by have := sz_a1_lt (show tg (a2 y) = 2 from hp2.2.1); omega)]
    rw [op_fire2 (u := y) (v := J (a1 (a2 y)) (J x (J y y)))
      ⟨rfl, rfl, rfl, rfl, rfl, hp2.1, hp2.2.1, hp2.2.2.1⟩
      (by apply msr_lt_both
          · simp only [sz_J]; have := sz_a1 (a2 (a2 y)); have := sz_a2 (a2 y); have := sz_a2 y; omega
          · simp only [sz_J]; omega)
      (by simp only [a1_J_eq]; rw [← hp2.2.2.2.1, hzy])]
    simp only [a2_J_eq, a1_J_eq]


theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
