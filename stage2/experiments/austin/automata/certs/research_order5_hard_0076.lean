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

def P1 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ tg (a2 (a1 v)) = 2 ∧ tg (a1 (a2 (a1 v))) = 2 ∧ u = a2 (a1 (a2 (a1 v))) ∧ u = a2 (a2 (a1 v)) ∧ u = a2 v
instance (u v : M) : Decidable (P1 u v) := by unfold P1; infer_instance
def P2 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ tg (a2 (a1 v)) = 2 ∧ u = a2 (a2 (a1 v)) ∧ u = a2 v ∧ tg u = 2
instance (u v : M) : Decidable (P2 u v) := by unfold P2; infer_instance
def P3 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a2 v ∧ tg u = 2
instance (u v : M) : Decidable (P3 u v) := by unfold P3; infer_instance
def P4 (u v : M) : Prop := tg v = 2 ∧ u = a2 v ∧ tg u = 2
instance (u v : M) : Decidable (P4 u v) := by unfold P4; infer_instance
def op (u v : M) : M :=
  let p1 := if hs1 : msr (a2 u) (u) < msr u v then op (a2 u) (u) else J u v
  let p2 := if hs2 : msr (p1) (u) < msr u v then op (p1) (u) else J u v
  let p3 := if hs3 : msr (a2 (p2)) (p2) < msr u v then op (a2 (p2)) (p2) else J u v
  if P1 u v then a1 (a1 (a2 (a1 v)))
  else if P2 u v ∧ msr (a2 u) (u) < msr u v ∧ a1 (a2 (a1 v)) = p1 then a2 u
  else if P3 u v ∧ msr (a2 u) (u) < msr u v ∧ a2 (a1 v) = p1 ∧ a2 u = p1 then a2 u
  else if P4 u v ∧ msr (a2 u) (u) < msr u v ∧ msr (p1) (u) < msr u v ∧ msr (a2 (p2)) (p2) < msr u v ∧ tg (p2) = 2 ∧ a1 v = p3 then a2 u
  else J u v
termination_by msr u v
decreasing_by
  · assumption
  · assumption
  · assumption


def inst : Magma M := { op := op }

def Pre (u v : M) : Prop := P1 u v ∨ P2 u v ∨ P3 u v ∨ P4 u v

theorem op_free {u v : M} (h : ¬ Pre u v) : op u v = J u v := by
  rw [op.eq_1]; simp only [Pre, not_or] at h; simp [h]

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 2) (g 0) (g 1)
  revert this
  change ¬ g 2 = op (op (g 0) (op (g 0) (op (op (g 1) (g 1)) (g 2)))) (g 0)
  simp (config := {decide := true}) [op.eq_1, sz, P1, P2, P3, P4]


theorem msr_ge {a b u v : M} (h : max (sz u) (sz v) ≤ max (sz a) (sz b)) (h2 : sz u + sz v ≤ sz a + sz b) : msr u v ≤ msr a b := by
  unfold msr; have := Nat.mul_le_mul h h; omega
theorem ngJ (u v : M) : ¬ msr (J u v) u < msr u v :=
  Nat.not_lt.mpr (msr_ge (by simp only [sz]; omega) (by simp only [sz]; omega))
theorem ngJ2 (u v : M) : ¬ msr (a2 (J u v)) (J u v) < msr u v :=
  Nat.not_lt.mpr (msr_ge (by simp only [sz, a2_J_eq]; omega) (by simp only [sz, a2_J_eq]; omega))

theorem TR (u v : M) : op u v = J u v ∨ (tg v = 2 ∧ sz v = sz (a1 v) + sz (a2 v) + 1 ∧ u = a2 v ∧ (op u v = a1 (a1 (a2 (a1 v))) ∨ op u v = a2 u)) := by
  have n1 := ngJ u v
  have n2 := ngJ2 u v
  rw [op.eq_1]
  by_cases g1 : msr (a2 u) u < msr u v <;> by_cases g2 : msr (op (a2 u) u) u < msr u v <;>
    by_cases g3 : msr (a2 (op (op (a2 u) u) u)) (op (op (a2 u) u) u) < msr u v
  all_goals
    split
    · rename_i h; obtain ⟨h1, -, -, -, -, -, h7⟩ := h; exact Or.inr ⟨h1, sz_tg _ h1, h7, Or.inl rfl⟩
    · split
      · rename_i h; obtain ⟨⟨h1, -, -, -, h5, -⟩, -⟩ := h; exact Or.inr ⟨h1, sz_tg _ h1, h5, Or.inr rfl⟩
      · split
        · rename_i h; obtain ⟨⟨h1, -, h3, -⟩, -⟩ := h; exact Or.inr ⟨h1, sz_tg _ h1, h3, Or.inr rfl⟩
        · split
          · rename_i h; obtain ⟨⟨h1, h2, -⟩, -⟩ := h; exact Or.inr ⟨h1, sz_tg _ h1, h2, Or.inr rfl⟩
          · exact Or.inl rfl

theorem TRsz (u v : M) : op u v = J u v ∨ (tg v = 2 ∧ u = a2 v ∧ sz (op u v) < sz v) := by
  rcases TR u v with h | ⟨h1, h2, h3, h4 | h4⟩
  · exact Or.inl h
  · right; refine ⟨h1, h3, ?_⟩; rw [h4]
    have := sz_a1 (a1 (a2 (a1 v))); have := sz_a1 (a2 (a1 v)); have := sz_a2 (a1 v); omega
  · right; refine ⟨h1, h3, ?_⟩; rw [h4, h3]; have := sz_a2 (a2 v); omega

theorem op_big {u v : M} (h : sz v ≤ sz u) : op u v = J u v := by
  rcases TRsz u v with h2 | ⟨h1, h2, -⟩
  · exact h2
  · exfalso; have := sz_tg _ h1; rw [h2] at h; omega

theorem gate1 {u v : M} (h : sz u < sz v) : msr (a2 u) u < msr u v := by
  apply msr_lt_of_max_lt; have := sz_a2 u; omega

theorem op_R1 (u z x : M) : op u (J (J z (J (J x u) u)) u) = x := by
  rw [op.eq_1]; simp [P1]

theorem op_R2 (u z P : M) (hu : tg u = 2) (hP : op (a2 u) u = P) : op u (J (J z (J P u)) u) = a2 u := by
  have g1 : msr (a2 u) u < msr u (J (J z (J P u)) u) := gate1 (by simp only [sz]; omega)
  rw [op.eq_1]
  split
  · rename_i h
    obtain ⟨-, -, -, h4, h5, -, -⟩ := h
    simp only [a1_J_eq, a2_J_eq] at h4 h5
    obtain ⟨b0, b1, rfl⟩ := tg_J _ h4
    simp only [a2_J_eq] at h5; subst h5
    simp only [a1_J_eq, a2_J_eq]
    rcases TRsz (a2 u) u with h2 | ⟨-, -, h2⟩
    · rw [hP] at h2; injection h2 with h3 _; try exact h3.symm
    · rw [hP] at h2; have : sz (J b0 u) = sz b0 + sz u + 1 := rfl; omega
  · split
    · rfl
    · rename_i h1 h; exfalso
      exact h ⟨⟨rfl, rfl, rfl, rfl, rfl, hu⟩, g1, by simp only [hP, a1_J_eq, a2_J_eq]⟩

theorem op_R3 (u z : M) (hu : tg u = 2) (hP : op (a2 u) u = a2 u) : op u (J (J z (a2 u)) u) = a2 u := by
  have g1 : msr (a2 u) u < msr u (J (J z (a2 u)) u) := gate1 (by simp only [sz]; omega)
  have hs := sz_tg _ hu
  have s1 := sz_a2 (a2 u)
  rw [op.eq_1]
  split
  · rename_i h; exfalso
    obtain ⟨-, -, -, -, -, h6, -⟩ := h
    simp only [a1_J_eq, a2_J_eq] at h6
    have := congrArg sz h6; omega
  · split
    · rename_i h1 h; exfalso
      obtain ⟨⟨-, -, -, h4, -, -⟩, -⟩ := h
      simp only [a1_J_eq, a2_J_eq] at h4
      have := congrArg sz h4; omega
    · split
      · rfl
      · rename_i h1 h2 h; exfalso
        exact h ⟨⟨rfl, rfl, rfl, hu⟩, g1, by simp only [hP, a1_J_eq, a2_J_eq], by simp only [hP]⟩

theorem op_R4 (u R : M) (hu : tg u = 2) (hx : tg (a2 u) = 2) (hP : op (a2 u) u = a2 u)
    (hR : op (a2 (a2 u)) (a2 u) = R) : op u (J R u) = a2 u := by
  have hs := sz_tg _ hu
  have hs2 := sz_tg _ hx
  have g1 : msr (a2 u) u < msr u (J R u) := gate1 (by simp only [sz]; omega)
  have g2 : msr (op (a2 u) u) u < msr u (J R u) := by rw [hP]; exact g1
  have g3' : msr (a2 (a2 u)) (a2 u) < msr u (J R u) := by
    apply msr_lt_of_max_lt; have := sz_a2 (a2 u); simp only [sz]; omega
  have g3 : msr (a2 (op (op (a2 u) u) u)) (op (op (a2 u) u) u) < msr u (J R u) := by rw [hP, hP]; exact g3'
  have tR := TR (a2 (a2 u)) (a2 u)
  rw [hR] at tR
  rw [op.eq_1]
  split
  · rename_i h; exfalso
    obtain ⟨-, -, -, -, -, h6, -⟩ := h
    simp only [a1_J_eq, a2_J_eq] at h6
    grind [sz, a1_J_eq, a2_J_eq, sz_a1, sz_a2]
  · split
    · rename_i h1 h; exfalso
      obtain ⟨⟨-, -, -, h4, -, -⟩, -⟩ := h
      simp only [a1_J_eq, a2_J_eq] at h4
      grind [sz, a1_J_eq, a2_J_eq, sz_a1, sz_a2]
    · split
      · rfl
      · split
        · rfl
        · rename_i h1 h2 h3 h; exfalso
          simp [hP, hR, P4, hu, hx, g1, g2, g3, g3'] at h

theorem N_R1 (x y : M) : op y (J (J x y) y) = J y (J (J x y) y) := by
  have s1 := sz_a2 y
  have g1 : msr (a2 y) y < msr y (J (J x y) y) := gate1 (by simp only [sz]; omega)
  have g2 : msr (op (a2 y) y) y < msr y (J (J x y) y) := by
    apply msr_lt_of_max_lt
    rcases TRsz (a2 y) y with h | ⟨-, -, h⟩
    · rw [h]; simp only [sz]; omega
    · simp only [sz]; omega
  rw [op.eq_1]
  by_cases g3 : msr (a2 (op (op (a2 y) y) y)) (op (op (a2 y) y) y) < msr y (J (J x y) y)
  all_goals
    split
    · rename_i h; exfalso
      obtain ⟨-, -, h3, -, -, h6, -⟩ := h
      simp only [a1_J_eq, a2_J_eq] at h3 h6
      have := sz_tg _ h3; have := congrArg sz h6; omega
    · split
      · rename_i h1 h; exfalso
        obtain ⟨⟨-, -, h3, h4, -, -⟩, -⟩ := h
        simp only [a1_J_eq, a2_J_eq] at h3 h4
        have := sz_tg _ h3; have := congrArg sz h4; omega
      · split
        · rename_i h1 h2 h; exfalso
          obtain ⟨⟨-, -, -, h4⟩, -, h5, h6⟩ := h
          simp only [a1_J_eq, a2_J_eq] at h5
          have := sz_tg _ h4; have := congrArg sz (h5.trans h6.symm); omega
        · split
          · rename_i h1 h2 h3 h; exfalso
            obtain ⟨⟨-, -, h4⟩, -, -, -, h5, h6⟩ := h
            have hys := sz_tg _ h4
            have t1 := TR (a2 y) y
            generalize hp1 : op (a2 y) y = p1 at *
            have t2 := TR p1 y
            generalize hp2 : op p1 y = p2 at *
            have t3 := TR (a2 p2) p2
            generalize hp3 : op (a2 p2) p2 = p3 at *
            grind [sz, a1_J_eq, a2_J_eq, sz_a1, sz_a2]
          · rfl

theorem N_R2 (P y : M) (hu : tg y = 2) (hs : sz P < sz y) (hP : op (a2 y) y = P) : op y (J P y) = J y (J P y) := by
  have hys := sz_tg _ hu
  have s1 := sz_a2 P
  have s2 := sz_a2 (a2 P)
  have g1 : msr (a2 y) y < msr y (J P y) := gate1 (by simp only [sz]; omega)
  have g2 : msr (op (a2 y) y) y < msr y (J P y) := by
    rw [hP]; apply msr_lt_of_max_lt; simp only [sz]; omega
  rw [op.eq_1]
  by_cases g3 : msr (a2 (op (op (a2 y) y) y)) (op (op (a2 y) y) y) < msr y (J P y)
  all_goals
    split
    · rename_i h; exfalso
      obtain ⟨-, -, -, -, -, h6, -⟩ := h
      simp only [a1_J_eq, a2_J_eq] at h6
      have := congrArg sz h6; omega
    · split
      · rename_i h1 h; exfalso
        obtain ⟨⟨-, -, -, h4, -, -⟩, -⟩ := h
        simp only [a1_J_eq, a2_J_eq] at h4
        have := congrArg sz h4; omega
      · split
        · rename_i h1 h2 h; exfalso
          obtain ⟨⟨-, h2b, -, -⟩, -, h5, -⟩ := h
          simp only [a1_J_eq, a2_J_eq, hP] at h2b h5
          have := sz_tg _ h2b; have := congrArg sz h5; omega
        · split
          · rename_i h1 h2 h3 h; exfalso
            obtain ⟨-, -, -, -, h5, h6⟩ := h
            have t2 := TR (op (a2 y) y) y
            rw [hP] at t2 h5
            try rw [hP] at h6
            generalize hp2 : op P y = p2 at *
            have t3 := TR (a2 p2) p2
            generalize hp3 : op (a2 p2) p2 = p3 at *
            grind [sz, a1_J_eq, a2_J_eq, sz_a1, sz_a2]
          · rfl

/-- THE LAW: x = y * ((z * ((x * y) * y)) * y) -/
theorem law (x y z : M) : op (y) (op (op (z) (op (op (x) (y)) (y))) (y)) = x := by
  rcases TRsz x y with hP | ⟨hy, hx, hsP⟩
  · have hQ : op (J x y) y = J (J x y) y := op_big (by simp only [sz]; omega)
    rw [hP, hQ]
    rcases TRsz z (J (J x y) y) with hR | ⟨-, hz, hR⟩
    · have hS : op (J z (J (J x y) y)) y = J (J z (J (J x y) y)) y := op_big (by simp only [sz]; omega)
      rw [hR, hS]; exact op_R1 y z x
    · exfalso; simp only [a2_J_eq] at hz; rw [hz, N_R1] at hR; simp only [sz] at hR; omega
  · have hys := sz_tg _ hy
    generalize hPP : op x y = P at hsP ⊢
    rcases TRsz P y with hQ | ⟨-, hPy, -⟩
    · rw [hQ]
      rcases TRsz z (J P y) with hR | ⟨-, hz, hR⟩
      · have hS : op (J z (J P y)) y = J (J z (J P y)) y := op_big (by simp only [sz]; omega)
        rw [hR, hS, hx]
        exact op_R2 y z P hy (by rw [← hx]; exact hPP)
      · exfalso; simp only [a2_J_eq] at hz
        rw [hz, N_R2 P y hy hsP (by rw [← hx]; exact hPP)] at hR; simp only [sz] at hR; omega
    · have hPx : P = x := by rw [hPy, hx]
      subst hPx
      rw [hPP]
      rcases TRsz z P with hR | ⟨hPt, hz, hR⟩
      · rw [hR]
        rcases TRsz (J z P) y with hS | ⟨-, hS, -⟩
        · rw [hS, hx]; exact op_R3 y z hy (by rw [← hx]; exact hPP)
        · exfalso; rw [← hx] at hS; have := congrArg sz hS; simp only [sz] at this; omega
      · rcases TRsz (op z P) y with hS | ⟨-, hS, -⟩
        · rw [hS, hx]
          exact op_R4 y _ hy (by rw [← hx]; exact hPt) (by rw [← hx]; exact hPP) (by rw [hz, hx])
        · exfalso; rw [← hx] at hS; rw [hS] at hR; omega

theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
