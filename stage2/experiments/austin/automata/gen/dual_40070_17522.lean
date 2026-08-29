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

def P1 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a1 (a2 v) ∧ tg (a2 (a2 v)) = 2 ∧ tg (a1 (a2 (a2 v))) = 2 ∧ a1 v = a2 (a1 (a2 (a2 v))) ∧ u = a2 (a2 (a2 v))
instance (u v : M) : Decidable (P1 u v) := by unfold P1; infer_instance
def P2 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a1 (a2 v) ∧ tg (a2 (a2 v)) = 2 ∧ u = a2 (a2 (a2 v)) ∧ tg (a1 v) = 2 ∧ tg (a2 (a1 v)) = 2
instance (u v : M) : Decidable (P2 u v) := by unfold P2; infer_instance
def P3 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a1 (a2 v) ∧ tg u = 2 ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a1 v = a2 (a1 (a2 u))
instance (u v : M) : Decidable (P3 u v) := by unfold P3; infer_instance
def P4 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a1 (a2 v) ∧ tg u = 2 ∧ tg (a2 u) = 2 ∧ tg (a1 v) = 2 ∧ tg (a2 (a1 v)) = 2
instance (u v : M) : Decidable (P4 u v) := by unfold P4; infer_instance
def op (u v : M) : M :=
  let p1 := if hs1 : msr (a1 (a2 (a1 v))) (a1 v) < msr u v then op (a1 (a2 (a1 v))) (a1 v) else J u v
  let p2 := if hs2 : msr (a1 (a2 u)) (u) < msr u v then op (a1 (a2 u)) (u) else J u v
  if P1 u v then a1 v
  else if P2 u v ∧ msr (a1 (a2 (a1 v))) (a1 v) < msr u v ∧ a1 (a2 (a2 v)) = p1 then a1 v
  else if P3 u v ∧ msr (a1 (a2 u)) (u) < msr u v ∧ a2 (a2 v) = p2 then a1 v
  else if P4 u v ∧ msr (a1 (a2 u)) (u) < msr u v ∧ msr (a1 (a2 (a1 v))) (a1 v) < msr u v ∧ a2 (a2 v) = p2 ∧ a1 (a2 u) = p1 then a1 v
  else J u v
termination_by msr u v
decreasing_by
  · assumption
  · assumption


def inst : Magma M := { op := fun a b => op b a }

def Pre (u v : M) : Prop := P1 u v ∨ P2 u v ∨ P3 u v ∨ P4 u v

theorem op_free {u v : M} (h : ¬ Pre u v) : op u v = J u v := by
  rw [op.eq_1]; simp only [Pre, not_or] at h; simp [h]

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 0) (g 0) (g 0)
  revert this
  change ¬ g 0 = op (op (op (op (g 0) (g 0)) (g 0)) (g 0)) (op (g 0) (g 0))
  simp (config := {decide := true}) [op.eq_1, sz, P1, P2, P3, P4]
/-- both arguments strictly smaller than `v` makes the measure drop -/
theorem msr_sub {a b u v : M} (ha : sz a < sz v) (hb : sz b < sz v) : msr a b < msr u v :=
  msr_lt_of_max_lt (by omega)

/-- the unfolding of `op` with the two nested calls packed away as opaque variables -/
theorem op_cases (u v : M) : ∃ p1 p2 : M,
    p1 = (if hs1 : msr (a1 (a2 (a1 v))) (a1 v) < msr u v then op (a1 (a2 (a1 v))) (a1 v) else J u v) ∧
    p2 = (if hs2 : msr (a1 (a2 u)) u < msr u v then op (a1 (a2 u)) u else J u v) ∧
    op u v = (
  if P1 u v then a1 v
  else if P2 u v ∧ msr (a1 (a2 (a1 v))) (a1 v) < msr u v ∧ a1 (a2 (a2 v)) = p1 then a1 v
  else if P3 u v ∧ msr (a1 (a2 u)) u < msr u v ∧ a2 (a2 v) = p2 then a1 v
  else if P4 u v ∧ msr (a1 (a2 u)) u < msr u v ∧ msr (a1 (a2 (a1 v))) (a1 v) < msr u v ∧ a2 (a2 v) = p2 ∧ a1 (a2 u) = p1 then a1 v
  else J u v) :=
  ⟨_, _, rfl, rfl, op.eq_1 u v⟩

/-- one unfold of `op`: free, or a rule fired (every rule returns `a1 v`) with its recursive guard -/
theorem TR4 (u v : M) : op u v = J u v ∨ (op u v = a1 v ∧ (
    P1 u v ∨
    (P2 u v ∧ a1 (a2 (a2 v)) = op (a1 (a2 (a1 v))) (a1 v)) ∨
    (P3 u v ∧ a2 (a2 v) = op (a1 (a2 u)) u) ∨
    (P4 u v ∧ a2 (a2 v) = op (a1 (a2 u)) u ∧ a1 (a2 u) = op (a1 (a2 (a1 v))) (a1 v)))) := by
  obtain ⟨p1, p2, hp1, hp2, hop⟩ := op_cases u v
  rw [hop]
  split
  · rename_i h; exact Or.inr ⟨rfl, Or.inl h⟩
  · split
    · rename_i h1 h
      obtain ⟨h2, hs1, he⟩ := h
      rw [dif_pos hs1] at hp1; subst hp1
      exact Or.inr ⟨rfl, Or.inr (Or.inl ⟨h2, he⟩)⟩
    · split
      · rename_i h1 h2 h
        obtain ⟨h3, hs2, he⟩ := h
        rw [dif_pos hs2] at hp2; subst hp2
        exact Or.inr ⟨rfl, Or.inr (Or.inr (Or.inl ⟨h3, he⟩))⟩
      · split
        · rename_i h1 h2 h3 h
          obtain ⟨h4, hs2, hs1, he2, he1⟩ := h
          rw [dif_pos hs1] at hp1; subst hp1
          rw [dif_pos hs2] at hp2; subst hp2
          exact Or.inr ⟨rfl, Or.inr (Or.inr (Or.inr ⟨h4, he2, he1⟩))⟩
        · left; rfl

/-- the weak characterisation: a non-free product needs `v = J _ (J u _)` and returns `a1 v` -/
theorem TR (u v : M) : op u v = J u v ∨ (tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a1 (a2 v) ∧ op u v = a1 v) := by
  rcases TR4 u v with h | ⟨hr, h | ⟨h, -⟩ | ⟨h, -⟩ | ⟨h, -, -⟩⟩
  · exact Or.inl h
  · exact Or.inr ⟨h.1, h.2.1, h.2.2.1, hr⟩
  · exact Or.inr ⟨h.1, h.2.1, h.2.2.1, hr⟩
  · exact Or.inr ⟨h.1, h.2.1, h.2.2.1, hr⟩
  · exact Or.inr ⟨h.1, h.2.1, h.2.2.1, hr⟩

/-- the third product `y * (q0 * y)` is always free -/
theorem Q2 (q0 y : M) : op y (op q0 y) = J y (op q0 y) := by
  rcases TR y (op q0 y) with h | ⟨-, h2, h3, -⟩
  · exact h
  · exfalso
    rcases TR q0 y with h' | ⟨hy1, -, -, h'⟩
    · rw [h'] at h2 h3
      simp only [a2_J_eq] at h2 h3
      have := sz_tg y h2
      have := congrArg sz h3
      omega
    · rw [h'] at h3
      have := sz_tg y hy1
      have := sz_a1 (a2 (a1 y))
      have := sz_a2 (a1 y)
      have := congrArg sz h3
      omega

/-- the fourth product `x * (J y (q0 * y))` with `q0 = z * x` is free (size) -/
theorem Q3 (x y z : M) : op x (J y (op (op z x) y)) = J x (J y (op (op z x) y)) := by
  rcases TR4 x (J y (op (op z x) y)) with h | ⟨-, hc⟩
  · exact h
  · exfalso
    rcases TR (op z x) y with hq1 | ⟨hy1, hy2, hy3, hq1⟩
    · have hx : x = op z x := by
        rcases hc with h | ⟨h, -⟩ | ⟨h, -⟩ | ⟨h, -, -⟩ <;>
          (have h3 := h.2.2.1; rw [hq1] at h3; simp only [a1_J_eq, a2_J_eq] at h3; exact h3)
      rcases TR z x with hq0 | ⟨hx1, -, -, hq0⟩
      · rw [hq0] at hx; have := congrArg sz hx; simp only [sz] at this; omega
      · rw [hq0] at hx; have := congrArg sz hx; have := sz_tg x hx1; omega
    · rw [hq1] at hc
      have s1 := sz_tg y hy1
      have s2 := sz_a1 (a2 (a1 y))
      have s3 := sz_a2 (a1 y)
      have s4 := sz_a2 (a1 (a2 (a1 y)))
      have s5 := sz_a1 (a1 y)
      rcases hc with h | ⟨h, he⟩ | ⟨h, -⟩ | ⟨h, -, he⟩
      · obtain ⟨-, -, -, -, -, h6, -⟩ := h
        simp only [a1_J_eq, a2_J_eq] at h6
        have := congrArg sz h6; omega
      · obtain ⟨-, h2, -, -, -, -, -⟩ := h
        simp only [a1_J_eq, a2_J_eq] at h2 he
        rw [← hy3, hq1] at he
        have := sz_tg (a1 y) h2
        have := congrArg sz he; omega
      · obtain ⟨-, -, h3, -, -, -, h7⟩ := h
        simp only [a1_J_eq, a2_J_eq] at h3 h7
        have := congrArg sz h3
        have := congrArg sz h7
        have := sz_a2 (a1 (a2 x)); have := sz_a1 (a2 x); have := sz_a2 x
        omega
      · obtain ⟨-, h2, h3, -, -, -, -⟩ := h
        simp only [a1_J_eq, a2_J_eq] at h2 h3 he
        rw [← hy3, hq1] at he
        have := sz_tg (a1 y) h2
        have := congrArg sz h3
        have := congrArg sz he
        have := sz_a1 (a2 x); have := sz_a2 x
        omega

/-- P1: everything free -/
theorem op_R1 (u x z : M) : op u (J x (J u (J (J z x) u))) = x := by
  obtain ⟨p1, p2, -, -, hop⟩ := op_cases u (J x (J u (J (J z x) u)))
  have h1 : P1 u (J x (J u (J (J z x) u))) := ⟨rfl, rfl, rfl, rfl, rfl, rfl, rfl⟩
  rw [hop, if_pos h1]
  rfl

/-- P2: `z * x` fired (`q0 = a1 x`), `q0 * u` free -/
theorem op_R2 (u x : M) (hx1 : tg x = 2) (hx2 : tg (a2 x) = 2) (hq : op (a1 (a2 x)) x = a1 x) :
    op u (J x (J u (J (a1 x) u))) = x := by
  obtain ⟨p1, p2, hp1, hp2, hop⟩ := op_cases u (J x (J u (J (a1 x) u)))
  have hs1 : msr (a1 (a2 (a1 (J x (J u (J (a1 x) u)))))) (a1 (J x (J u (J (a1 x) u)))) < msr u (J x (J u (J (a1 x) u))) := by
    simp only [a1_J_eq]
    have := sz_a1 (a2 x); have := sz_a2 x
    apply msr_sub <;> simp only [sz] <;> omega
  rw [dif_pos hs1] at hp1
  simp only [a1_J_eq] at hp1
  rw [hq] at hp1
  subst hp1
  rw [hop]
  split
  · rfl
  · split
    · rfl
    · rename_i h1 h2
      exfalso; apply h2
      exact ⟨⟨rfl, rfl, rfl, rfl, rfl, hx1, hx2⟩, hs1, rfl⟩

/-- P3: `z * x` free, `(J z x) * y` fired (`q1 = a1 y`) -/
theorem op_R3 (y x z : M) (hy1 : tg y = 2) (hy2 : tg (a2 y) = 2) (hy3 : J z x = a1 (a2 y))
    (hq1 : op (J z x) y = a1 y) : op y (J x (J y (a1 y))) = x := by
  obtain ⟨p1, p2, hp1, hp2, hop⟩ := op_cases y (J x (J y (a1 y)))
  have hs2 : msr (a1 (a2 y)) y < msr y (J x (J y (a1 y))) := by
    have := sz_a1 (a2 y); have := sz_a2 y
    apply msr_sub <;> simp only [sz] <;> omega
  rw [dif_pos hs2, ← hy3, hq1] at hp2
  subst hp2
  rw [hop]
  split
  · rfl
  · split
    · rfl
    · split
      · rfl
      · rename_i h1 h2 h3
        exfalso; apply h3
        exact ⟨⟨rfl, rfl, rfl, hy1, hy2, (congrArg tg hy3).symm.trans (tg_J_eq z x), congrArg a2 hy3⟩, hs2, rfl⟩

/-- P4: both `z * x` and `q0 * y` fired -/
theorem op_R4 (y x : M) (hy1 : tg y = 2) (hy2 : tg (a2 y) = 2) (hx1 : tg x = 2) (hx2 : tg (a2 x) = 2)
    (hy3 : a1 x = a1 (a2 y)) (hq0 : op (a1 (a2 x)) x = a1 x) (hq1 : op (a1 x) y = a1 y) :
    op y (J x (J y (a1 y))) = x := by
  obtain ⟨p1, p2, hp1, hp2, hop⟩ := op_cases y (J x (J y (a1 y)))
  have hs1 : msr (a1 (a2 (a1 (J x (J y (a1 y)))))) (a1 (J x (J y (a1 y)))) < msr y (J x (J y (a1 y))) := by
    simp only [a1_J_eq]
    have := sz_a1 (a2 x); have := sz_a2 x
    apply msr_sub <;> simp only [sz] <;> omega
  have hs2 : msr (a1 (a2 y)) y < msr y (J x (J y (a1 y))) := by
    have := sz_a1 (a2 y); have := sz_a2 y
    apply msr_sub <;> simp only [sz] <;> omega
  rw [dif_pos hs1] at hp1
  simp only [a1_J_eq] at hp1
  rw [hq0] at hp1
  subst hp1
  rw [dif_pos hs2, ← hy3, hq1] at hp2
  subst hp2
  rw [hop]
  split
  · rfl
  · split
    · rfl
    · split
      · rfl
      · split
        · rfl
        · rename_i h1 h2 h3 h4
          exfalso; apply h4
          exact ⟨⟨rfl, rfl, rfl, hy1, hy2, hx1, hx2⟩, hs2, hs1, rfl, hy3.symm⟩

/-- THE LAW: x = y * (x * (y * ((z * x) * y))) -/
theorem law (x y z : M) : op (y) (op (x) (op (y) (op (op (z) (x)) (y)))) = x := by
  rw [Q2, Q3]
  rcases TR (op z x) y with hq1 | ⟨hy1, hy2, hy3, hq1⟩
  · rw [hq1]
    rcases TR z x with hq0 | ⟨hx1, hx2, hx3, hq0⟩
    · rw [hq0]; exact op_R1 y x z
    · rw [hq0]; subst hx3; exact op_R2 y x hx1 hx2 hq0
  · rw [hq1]
    rcases TR z x with hq0 | ⟨hx1, hx2, hx3, hq0⟩
    · rw [hq0] at hy3 hq1; exact op_R3 y x z hy1 hy2 hy3 hq1
    · subst hx3; rw [hq0] at hy3 hq1; exact op_R4 y x hy1 hy2 hx1 hx2 hy3 hq0 hq1


theorem lhs : @EquationLHS M inst := by
  intro x y z
  first | exact (law x y z).symm | exact (law x z y).symm | exact (law y x z).symm | exact (law y z x).symm | exact (law z x y).symm | exact (law z y x).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
