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

def P1 (u v : M) : Prop := tg v = 2 ∧ u = a1 v ∧ tg (a2 v) = 2 ∧ tg (a2 (a2 v)) = 2 ∧ u = a1 (a2 (a2 v)) ∧ tg (a2 (a2 (a2 v))) = 2 ∧ u = a2 (a2 (a2 (a2 v)))
instance (u v : M) : Decidable (P1 u v) := by unfold P1; infer_instance
def P2 (u v : M) : Prop := tg v = 2 ∧ u = a1 v ∧ tg (a2 v) = 2 ∧ tg (a2 (a2 v)) = 2 ∧ u = a1 (a2 (a2 v)) ∧ tg u = 2
instance (u v : M) : Decidable (P2 u v) := by unfold P2; infer_instance
def P3 (u v : M) : Prop := tg v = 2 ∧ u = a1 v ∧ tg (a2 v) = 2 ∧ tg (a2 (a2 v)) = 2 ∧ u = a1 (a2 (a2 v)) ∧ tg u = 2 ∧ tg (a2 u) = 2 ∧ a2 (a2 (a2 v)) = a1 (a2 u) ∧ tg (a2 (a2 u)) = 2 ∧ a1 u = a1 (a2 (a2 u)) ∧ tg (a2 (a2 (a2 u))) = 2 ∧ a1 u = a2 (a2 (a2 (a2 u)))
instance (u v : M) : Decidable (P3 u v) := by unfold P3; infer_instance
def P4 (u v : M) : Prop := tg v = 2 ∧ u = a1 v ∧ tg (a2 v) = 2 ∧ tg u = 2
instance (u v : M) : Decidable (P4 u v) := by unfold P4; infer_instance
def P5 (u v : M) : Prop := tg v = 2 ∧ u = a1 v ∧ tg u = 2
instance (u v : M) : Decidable (P5 u v) := by unfold P5; infer_instance
def P6 (u v : M) : Prop := tg u = 2
instance (u v : M) : Decidable (P6 u v) := by unfold P6; infer_instance
def op (u v : M) : M :=
  let p1 := if hs1 : sz (a1 u) + sz (u) < sz u + sz v then op (a1 u) (u) else J u v
  let p2 := if hs2 : sz (u) + sz (p1) < sz u + sz v then op (u) (p1) else J u v
  let p3 := if hs3 : sz (a1 (p2)) + sz (p2) < sz u + sz v then op (a1 (p2)) (p2) else J u v
  let p4 := if hs4 : sz (u) + sz (p3) < sz u + sz v then op (u) (p3) else J u v
  if P1 u v then a1 (a2 v)
  else if P2 u v ∧ sz (a1 u) + sz (u) < sz u + sz v ∧ a2 (a2 (a2 v)) = p1 then a1 (a2 v)
  else if P3 u v ∧ sz (a1 u) + sz (u) < sz u + sz v ∧ a2 (a2 (a2 v)) = p1 then a1 (a2 v)
  else if P4 u v ∧ sz (a1 u) + sz (u) < sz u + sz v ∧ sz (u) + sz (p1) < sz u + sz v ∧ a2 (a2 v) = p2 then a1 (a2 v)
  else if P5 u v ∧ sz (a1 u) + sz (u) < sz u + sz v ∧ sz (u) + sz (p1) < sz u + sz v ∧ sz (a1 (p2)) + sz (p2) < sz u + sz v ∧ tg (p2) = 2 ∧ a2 v = p3 then a1 (p2)
  else if P6 u v ∧ sz (a1 u) + sz (u) < sz u + sz v ∧ sz (u) + sz (p1) < sz u + sz v ∧ sz (a1 (p2)) + sz (p2) < sz u + sz v ∧ sz (u) + sz (p3) < sz u + sz v ∧ tg (p2) = 2 ∧ v = p4 then a1 (p2)
  else J u v
termination_by sz u + sz v
decreasing_by
  · assumption
  · assumption
  · assumption
  · assumption


def inst : Magma M := { op := op }

def Pre (u v : M) : Prop := P1 u v ∨ P2 u v ∨ P3 u v ∨ P4 u v ∨ P5 u v ∨ P6 u v

theorem op_free {u v : M} (h : ¬ Pre u v) : op u v = J u v := by
  rw [op.eq_1]; simp only [Pre, not_or] at h; simp [h]

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 2) (g 0) (g 1)
  revert this
  change ¬ g 2 = op (op (g 0) (op (g 0) (op (op (g 1) (g 1)) (g 2)))) (g 0)
  simp (config := {decide := true}) [op.eq_1, sz, P1, P2, P3, P4, P5, P6]


theorem tg_sz {u : M} (h : tg u = 2) : sz (a1 u) < sz u ∧ sz (a2 u) < sz u := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp only [a1_J_eq, a2_J_eq, sz]; omega

/-- one-unfold shape of `op u v`: free, or `v = J u (J A (J u C))` with result `A`, where
`C = J B u` (R1) or `C = op (a1 u) u` with `tg u = 2` (R2..R6 all reduce to this). -/
abbrev Sh (u v r : M) : Prop :=
  r = J u v ∨ (tg v = 2 ∧ a1 v = u ∧ tg (a2 v) = 2 ∧ tg (a2 (a2 v)) = 2 ∧ a1 (a2 (a2 v)) = u ∧ r = a1 (a2 v) ∧
    ((tg (a2 (a2 (a2 v))) = 2 ∧ a2 (a2 (a2 (a2 v))) = u) ∨ (tg u = 2 ∧ a2 (a2 (a2 v)) = op (a1 u) u)))

theorem op_unf (u v p1 p2 p3 p4 : M)
    (h1 : p1 = if hs1 : sz (a1 u) + sz u < sz u + sz v then op (a1 u) u else J u v)
    (h2 : p2 = if hs2 : sz u + sz p1 < sz u + sz v then op u p1 else J u v)
    (h3 : p3 = if hs3 : sz (a1 p2) + sz p2 < sz u + sz v then op (a1 p2) p2 else J u v)
    (h4 : p4 = if hs4 : sz u + sz p3 < sz u + sz v then op u p3 else J u v) :
    op u v = (if P1 u v then a1 (a2 v)
      else if P2 u v ∧ sz (a1 u) + sz u < sz u + sz v ∧ a2 (a2 (a2 v)) = p1 then a1 (a2 v)
      else if P3 u v ∧ sz (a1 u) + sz u < sz u + sz v ∧ a2 (a2 (a2 v)) = p1 then a1 (a2 v)
      else if P4 u v ∧ sz (a1 u) + sz u < sz u + sz v ∧ sz u + sz p1 < sz u + sz v ∧ a2 (a2 v) = p2 then a1 (a2 v)
      else if P5 u v ∧ sz (a1 u) + sz u < sz u + sz v ∧ sz u + sz p1 < sz u + sz v ∧ sz (a1 p2) + sz p2 < sz u + sz v ∧ tg p2 = 2 ∧ a2 v = p3 then a1 p2
      else if P6 u v ∧ sz (a1 u) + sz u < sz u + sz v ∧ sz u + sz p1 < sz u + sz v ∧ sz (a1 p2) + sz p2 < sz u + sz v ∧ sz u + sz p3 < sz u + sz v ∧ tg p2 = 2 ∧ v = p4 then a1 p2
      else J u v) := by
  subst h4; subst h3; subst h2; subst h1; exact op.eq_1 u v

theorem MainN (n : Nat) : ∀ u v r : M, sz u + sz v < n → op u v = r → Sh u v r := by
  induction n with
  | zero => intro u v r h; exact absurd h (Nat.not_lt_zero _)
  | succ n ih =>
    intro u v r hn hr
    have hW : ∀ w : M, tg w = 2 → sz (a1 w) + sz w < n →
        sz (a1 (op (a1 w) w)) < sz w ∧ sz (a1 (a2 (op (a1 w) w))) < sz w := by
      intro w hw h1
      have s := tg_sz hw
      rcases ih (a1 w) w _ h1 rfl with h | ⟨-, -, -, -, -, h, -⟩
      · rw [h]; simp only [a1_J_eq, a2_J_eq]; omega
      · rw [h]
        have := sz_a1 (a1 (a2 w)); have := sz_a1 (a2 (a1 (a2 w))); have := sz_a2 (a1 (a2 w)); have := sz_a1 (a2 w)
        omega
    have hW2 : ∀ w : M, tg w = 2 → sz (a1 w) + sz w < n → sz w + sz (op (a1 w) w) < n →
        op w (op (a1 w) w) = J w (op (a1 w) w) := by
      intro w hw h1 h2
      rcases ih w (op (a1 w) w) _ h2 rfl with h | ⟨-, h, -, -, -, -, -⟩
      · exact h
      · exfalso; have := congrArg sz h; have := (hW w hw h1).1; omega
    have hV2 : ∀ w : M, tg w = 2 → sz (a1 w) + sz w < n → sz w + sz (J w (op (a1 w) w)) < n →
        op w (J w (op (a1 w) w)) = J w (J w (op (a1 w) w)) := by
      intro w hw h1 h3
      rcases ih w (J w (op (a1 w) w)) _ h3 rfl with h | ⟨-, -, -, -, h, -, -⟩
      · exact h
      · exfalso; simp only [a2_J_eq] at h; have := congrArg sz h; have := (hW w hw h1).2; omega
    have hV3 : ∀ w : M, tg w = 2 → sz (a1 w) + sz w < n → sz w + sz (J w (J w (op (a1 w) w))) < n →
        op w (J w (J w (op (a1 w) w))) = J w (J w (J w (op (a1 w) w))) := by
      intro w hw h1 h4
      rcases ih w (J w (J w (op (a1 w) w))) _ h4 rfl with h | ⟨-, -, -, -, h, -, -⟩
      · exact h
      · exfalso; simp only [a2_J_eq] at h; have := congrArg sz h; have := (hW w hw h1).1; omega
    obtain ⟨p1, hp1⟩ : ∃ p1, p1 = (if hs1 : sz (a1 u) + sz u < sz u + sz v then op (a1 u) u else J u v) := ⟨_, rfl⟩
    obtain ⟨p2, hp2⟩ : ∃ p2, p2 = (if hs2 : sz u + sz p1 < sz u + sz v then op u p1 else J u v) := ⟨_, rfl⟩
    obtain ⟨p3, hp3⟩ : ∃ p3, p3 = (if hs3 : sz (a1 p2) + sz p2 < sz u + sz v then op (a1 p2) p2 else J u v) := ⟨_, rfl⟩
    obtain ⟨p4, hp4⟩ : ∃ p4, p4 = (if hs4 : sz u + sz p3 < sz u + sz v then op u p3 else J u v) := ⟨_, rfl⟩
    rw [op_unf u v p1 p2 p3 p4 hp1 hp2 hp3 hp4] at hr
    split at hr
    · rename_i h
      obtain ⟨h1, h2, h3, h4, h5, h6, h7⟩ := h
      exact Or.inr ⟨h1, h2.symm, h3, h4, h5.symm, hr.symm, Or.inl ⟨h6, h7.symm⟩⟩
    by_cases A1 : sz (a1 u) + sz u < sz u + sz v
    · rw [dif_pos A1] at hp1
      subst hp1
      split at hr
      · rename_i h
        obtain ⟨⟨h1, h2, h3, h4, h5, hu⟩, -, he⟩ := h
        exact Or.inr ⟨h1, h2.symm, h3, h4, h5.symm, hr.symm, Or.inr ⟨hu, he⟩⟩
      split at hr
      · rename_i h
        obtain ⟨⟨h1, h2, h3, h4, h5, hu, -⟩, -, he⟩ := h
        exact Or.inr ⟨h1, h2.symm, h3, h4, h5.symm, hr.symm, Or.inr ⟨hu, he⟩⟩
      by_cases A2 : sz u + sz (op (a1 u) u) < sz u + sz v
      · rw [dif_pos A2] at hp2
        subst hp2
        split at hr
        · rename_i h
          obtain ⟨⟨h1, h2, h3, hu⟩, -, -, he⟩ := h
          rw [hW2 u hu (by omega) (by omega)] at he
          refine Or.inr ⟨h1, h2.symm, h3, ?_, ?_, hr.symm, Or.inr ⟨hu, ?_⟩⟩
          · simp only [he, tg_J_eq]
          · simp only [he, a1_J_eq]
          · simp only [he, a2_J_eq]
        by_cases A3 : sz (a1 (op u (op (a1 u) u))) + sz (op u (op (a1 u) u)) < sz u + sz v
        · rw [dif_pos A3] at hp3
          subst hp3
          split at hr
          · rename_i h
            obtain ⟨⟨h1, h2, hu⟩, -, -, -, ht, he⟩ := h
            rw [hW2 u hu (by omega) (by omega)] at A3 he hr
            simp only [a1_J_eq] at A3 he hr
            rw [hV2 u hu (by omega) (by omega)] at he
            subst hr
            refine Or.inr ⟨h1, h2.symm, ?_, ?_, ?_, ?_, Or.inr ⟨hu, ?_⟩⟩
            · simp only [he, tg_J_eq]
            · simp only [he, a2_J_eq, tg_J_eq]
            · simp only [he, a2_J_eq, a1_J_eq]
            · simp only [he, a1_J_eq]
            · simp only [he, a2_J_eq]
          by_cases A4 : sz u + sz (op (a1 (op u (op (a1 u) u))) (op u (op (a1 u) u))) < sz u + sz v
          · rw [dif_pos A4] at hp4
            subst hp4
            split at hr
            · rename_i h
              obtain ⟨hu, -, -, -, -, ht, he⟩ := h
              have hu : tg u = 2 := hu
              rw [hW2 u hu (by omega) (by omega)] at A3 A4 he hr
              simp only [a1_J_eq] at A3 A4 he hr
              rw [hV2 u hu (by omega) (by omega)] at A4 he
              rw [hV3 u hu (by omega) (by omega)] at he
              subst hr
              subst he
              exact Or.inr ⟨rfl, rfl, rfl, rfl, rfl, rfl, Or.inr ⟨hu, rfl⟩⟩
            · exact Or.inl hr.symm
          · simp only [A4, false_and, and_false, if_false] at hr
            exact Or.inl hr.symm
        · simp only [A3, false_and, and_false, if_false] at hr
          exact Or.inl hr.symm
      · simp only [A2, false_and, and_false, if_false] at hr
        exact Or.inl hr.symm
    · simp only [A1, false_and, and_false, if_false] at hr
      exact Or.inl hr.symm

theorem TR (u v : M) : Sh u v (op u v) := MainN (sz u + sz v + 1) u v _ (Nat.lt_succ_self _) rfl

theorem Wfact {u : M} (hu : tg u = 2) :
    sz (a1 (op (a1 u) u)) < sz u ∧ sz (a1 (a2 (op (a1 u) u))) < sz u ∧ sz (op (a1 u) u) ≠ sz u := by
  have s := tg_sz hu
  rcases TR (a1 u) u with h | ⟨-, -, -, -, -, h, -⟩
  · rw [h]; simp only [a1_J_eq, a2_J_eq, sz]; omega
  · rw [h]
    have := sz_a1 (a1 (a2 u)); have := sz_a1 (a2 (a1 (a2 u))); have := sz_a2 (a1 (a2 u)); have := sz_a1 (a2 u)
    omega

theorem W2eq {u : M} (hu : tg u = 2) : op u (op (a1 u) u) = J u (op (a1 u) u) := by
  rcases TR u (op (a1 u) u) with h | ⟨-, h, -, -, -, -, -⟩
  · exact h
  · exfalso; have := congrArg sz h; have := (Wfact hu).1; omega

theorem op_R1 (u A B : M) : op u (J u (J A (J u (J B u)))) = A := by
  rw [op.eq_1]; simp [P1]

theorem op_R2 (u A : M) (hu : tg u = 2) : op u (J u (J A (J u (op (a1 u) u)))) = A := by
  have A1 : sz (a1 u) + sz u < sz u + sz (J u (J A (J u (op (a1 u) u)))) := by
    have := sz_a1 u; simp only [sz]; omega
  rw [op.eq_1]
  by_cases hP1 : P1 u (J u (J A (J u (op (a1 u) u))))
  · rw [if_pos hP1]; rfl
  · rw [if_neg hP1, if_pos]
    · rfl
    · exact ⟨by simp [P2, hu], A1, by simp only [dif_pos A1, a2_J_eq]⟩

/-- THE LAW: x = y * (y * (x * (y * (z * y)))) -/
theorem law (x y z : M) : op (y) (op (y) (op (x) (op (y) (op (z) (y))))) = x := by
  by_cases hy : tg y = 2
  · have ⟨w1, w2, w3⟩ := Wfact hy
    have s := tg_sz hy
    by_cases hz : a1 y = z
    · subst hz
      rw [W2eq hy]
      have hr : op x (J y (op (a1 y) y)) = J x (J y (op (a1 y) y)) := by
        rcases TR x (J y (op (a1 y) y)) with h | ⟨-, h2, -, -, h5, -, -⟩
        · exact h
        · exfalso; simp only [a1_J_eq, a2_J_eq] at h2 h5; subst h2; have := congrArg sz h5; omega
      rw [hr]
      have hs : op y (J x (J y (op (a1 y) y))) = J y (J x (J y (op (a1 y) y))) := by
        rcases TR y (J x (J y (op (a1 y) y))) with h | ⟨-, h2, -, -, h5, -, -⟩
        · exact h
        · exfalso; simp only [a1_J_eq, a2_J_eq] at h2 h5; subst h2; have := congrArg sz h5; omega
      rw [hs]
      exact op_R2 y x hy
    · have hp : op z y = J z y := by
        rcases TR z y with h | ⟨-, h2, -, -, -, -, -⟩
        · exact h
        · exact absurd h2 hz
      rw [hp]
      have hq : op y (J z y) = J y (J z y) := by
        rcases TR y (J z y) with h | ⟨-, -, -, -, h5, -, -⟩
        · exact h
        · exfalso; simp only [a1_J_eq, a2_J_eq] at h5; have := congrArg sz h5; have := sz_a1 (a2 y); omega
      rw [hq]
      have hr : op x (J y (J z y)) = J x (J y (J z y)) := by
        rcases TR x (J y (J z y)) with h | ⟨-, h2, -, -, h5, -, -⟩
        · exact h
        · exfalso; simp only [a1_J_eq, a2_J_eq] at h2 h5; subst h2; have := congrArg sz h5; omega
      rw [hr]
      have hs : op y (J x (J y (J z y))) = J y (J x (J y (J z y))) := by
        rcases TR y (J x (J y (J z y))) with h | ⟨-, -, -, -, -, -, ⟨-, h7⟩ | ⟨-, h7⟩⟩
        · exact h
        · exfalso; simp only [a2_J_eq] at h7; have := congrArg sz h7; omega
        · exfalso; simp only [a2_J_eq] at h7; have := congrArg sz h7; omega
      rw [hs]
      exact op_R1 y x z
  · have hp : op z y = J z y := by
      rcases TR z y with h | ⟨h1, -, -, -, -, -, -⟩
      · exact h
      · exact absurd h1 hy
    rw [hp]
    have hq : op y (J z y) = J y (J z y) := by
      rcases TR y (J z y) with h | ⟨-, -, h3, -, -, -, -⟩
      · exact h
      · exfalso; simp only [a2_J_eq] at h3; exact hy h3
    rw [hq]
    have hr : op x (J y (J z y)) = J x (J y (J z y)) := by
      rcases TR x (J y (J z y)) with h | ⟨-, -, -, h4, -, -, -⟩
      · exact h
      · exfalso; simp only [a2_J_eq] at h4; exact hy h4
    rw [hr]
    have hs : op y (J x (J y (J z y))) = J y (J x (J y (J z y))) := by
      rcases TR y (J x (J y (J z y))) with h | ⟨-, -, -, -, -, -, ⟨h7, -⟩ | ⟨h7, -⟩⟩
      · exact h
      · exfalso; simp only [a2_J_eq] at h7; exact hy h7
      · exact absurd h7 hy
    rw [hs]
    exact op_R1 y x z


theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
