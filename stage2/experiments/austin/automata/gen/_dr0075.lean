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
theorem sz_tg (t : M) (h : tg t = 2) : sz t = sz (a1 t) + sz (a2 t) + 1 := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a1, a2]
@[simp] theorem tg_g_eq (n : Nat) : tg (M.g n) = 1 := rfl
@[simp] theorem tg_J_eq (b0 b1 : M) : tg (M.J b0 b1) = 2 := rfl
@[simp] theorem a1_J_eq (b0 b1 : M) : a1 (M.J b0 b1) = b0 := rfl
@[simp] theorem a2_J_eq (b0 b1 : M) : a2 (M.J b0 b1) = b1 := rfl
@[simp] theorem a1_g_eq (n : Nat) : a1 (M.g n) = M.g n := rfl
@[simp] theorem a2_g_eq (n : Nat) : a2 (M.g n) = M.g n := rfl
def msr (u v : M) : Nat := max (sz u) (sz v) * max (sz u) (sz v) + sz u + sz v
theorem msr_lt_of_max_lt {a b u v : M} (h : max (sz a) (sz b) < max (sz u) (sz v)) : msr a b < msr u v := by
  unfold msr
  have h1 : sz a + sz b ≤ 2 * max (sz a) (sz b) := by omega
  have h2 : (max (sz a) (sz b) + 1) * (max (sz a) (sz b) + 1) ≤ max (sz u) (sz v) * max (sz u) (sz v) := Nat.mul_le_mul h h
  simp only [Nat.mul_succ, Nat.succ_mul] at h2
  omega

def P1 (u v : M) : Prop := tg v = 2 ∧ u = a1 v ∧ tg (a2 v) = 2 ∧ tg (a1 (a2 v)) = 2 ∧ tg (a2 (a2 v)) = 2 ∧ a2 (a1 (a2 v)) = a1 (a2 (a2 v)) ∧ u = a2 (a2 (a2 v))
instance (u v : M) : Decidable (P1 u v) := by unfold P1; infer_instance
def P2 (u v : M) : Prop := tg v = 2 ∧ u = a1 v ∧ tg (a2 v) = 2 ∧ tg (a1 (a2 v)) = 2 ∧ tg u = 2 ∧ a2 (a1 (a2 v)) = a1 u
instance (u v : M) : Decidable (P2 u v) := by unfold P2; infer_instance
def P3 (u v : M) : Prop := tg v = 2 ∧ u = a1 v ∧ tg (a2 v) = 2 ∧ tg (a2 (a2 v)) = 2 ∧ u = a2 (a2 (a2 v)) ∧ tg (a1 (a2 (a2 v))) = 2
instance (u v : M) : Decidable (P3 u v) := by unfold P3; infer_instance
def P4 (u v : M) : Prop := tg v = 2 ∧ u = a1 v ∧ tg (a2 v) = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P4 u v) := by unfold P4; infer_instance
def P5 (u v : M) : Prop := tg v = 2 ∧ u = a1 v ∧ tg u = 2
instance (u v : M) : Decidable (P5 u v) := by unfold P5; infer_instance
def P6 (u v : M) : Prop := tg v = 2 ∧ u = a1 v ∧ tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P6 u v) := by unfold P6; infer_instance
def op (u v : M) : M :=
  let p1 := if hs1 : msr (a1 u) (u) < msr u v then op (a1 u) (u) else J u v
  let p2 := if hs2 : msr (a1 (a1 (a2 (a2 v)))) (a1 (a2 (a2 v))) < msr u v then op (a1 (a1 (a2 (a2 v)))) (a1 (a2 (a2 v))) else J u v
  let p3 := if hs3 : msr (a1 (a1 u)) (a1 u) < msr u v then op (a1 (a1 u)) (a1 u) else J u v
  let p4 := if hs4 : msr (a1 (p1)) (p1) < msr u v then op (a1 (p1)) (p1) else J u v
  if P1 u v then a2 (a1 (a2 v))
  else if P2 u v ∧ msr (a1 u) (u) < msr u v ∧ a2 (a2 v) = p1 then a1 u
  else if P3 u v ∧ msr (a1 (a1 (a2 (a2 v)))) (a1 (a2 (a2 v))) < msr u v ∧ a1 (a2 v) = p2 then a1 (a2 (a2 v))
  else if P4 u v ∧ msr (a1 (a1 u)) (a1 u) < msr u v ∧ msr (a1 u) (u) < msr u v ∧ a1 (a2 v) = p3 ∧ a2 (a2 v) = p1 then a1 u
  else if P5 u v ∧ msr (a1 u) (u) < msr u v ∧ msr (a1 (p1)) (p1) < msr u v ∧ tg (p1) = 2 ∧ tg (a1 (p1)) = 2 ∧ a2 (a1 (p1)) = a1 u ∧ a2 v = p4 then a1 u
  else if P6 u v ∧ msr (a1 u) (u) < msr u v ∧ msr (a1 (a1 u)) (a1 u) < msr u v ∧ msr (a1 (p1)) (p1) < msr u v ∧ tg (p1) = 2 ∧ a1 (p1) = p3 ∧ a2 v = p4 then a1 u
  else J u v
termination_by msr u v
decreasing_by
  · assumption
  · assumption
  · assumption
  · assumption


def inst : Magma M := { op := fun a b => op b a }

def Pre (u v : M) : Prop := P1 u v ∨ P2 u v ∨ P3 u v ∨ P4 u v ∨ P5 u v ∨ P6 u v

theorem op_free {u v : M} (h : ¬ Pre u v) : op u v = J u v := by
  rw [op.eq_1]; simp only [Pre, not_or] at h; simp [h]

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 0) (g 0) (g 0)
  revert this
  change ¬ g 0 = op (g 0) (op (op (op (g 0) (op (g 0) (g 0))) (g 0)) (g 0))
  simp (config := {decide := true}) [op.eq_1, sz, P1, P2, P3, P4, P5, P6]
theorem szJ1 (a b : M) : sz b < sz (J a b) := by simp only [sz]; omega
theorem szJ2 (a b : M) : sz a < sz (J a b) := by simp only [sz]; omega
theorem ne_of_sz {a t : M} (h : sz a < sz t) : a ≠ t := fun e => by rw [e] at h; exact Nat.lt_irrefl _ h
theorem gJ {a b u c : M} (h1 : sz a ≤ sz u ∨ sz a ≤ sz c) (h2 : sz b ≤ sz u ∨ sz b ≤ sz c) : msr a b < msr u (J u c) :=
  msr_lt_of_max_lt (by simp only [sz]; omega)

theorem op_cases (u v : M) : ∃ p1 p2 p3 p4 : M,
    p1 = (if hs1 : msr (a1 u) u < msr u v then op (a1 u) u else J u v) ∧
    p2 = (if hs2 : msr (a1 (a1 (a2 (a2 v)))) (a1 (a2 (a2 v))) < msr u v then op (a1 (a1 (a2 (a2 v)))) (a1 (a2 (a2 v))) else J u v) ∧
    p3 = (if hs3 : msr (a1 (a1 u)) (a1 u) < msr u v then op (a1 (a1 u)) (a1 u) else J u v) ∧
    p4 = (if hs4 : msr (a1 p1) p1 < msr u v then op (a1 p1) p1 else J u v) ∧
    op u v = (
  if P1 u v then a2 (a1 (a2 v))
  else if P2 u v ∧ msr (a1 u) u < msr u v ∧ a2 (a2 v) = p1 then a1 u
  else if P3 u v ∧ msr (a1 (a1 (a2 (a2 v)))) (a1 (a2 (a2 v))) < msr u v ∧ a1 (a2 v) = p2 then a1 (a2 (a2 v))
  else if P4 u v ∧ msr (a1 (a1 u)) (a1 u) < msr u v ∧ msr (a1 u) u < msr u v ∧ a1 (a2 v) = p3 ∧ a2 (a2 v) = p1 then a1 u
  else if P5 u v ∧ msr (a1 u) u < msr u v ∧ msr (a1 p1) p1 < msr u v ∧ tg p1 = 2 ∧ tg (a1 p1) = 2 ∧ a2 (a1 p1) = a1 u ∧ a2 v = p4 then a1 u
  else if P6 u v ∧ msr (a1 u) u < msr u v ∧ msr (a1 (a1 u)) (a1 u) < msr u v ∧ msr (a1 p1) p1 < msr u v ∧ tg p1 = 2 ∧ a1 p1 = p3 ∧ a2 v = p4 then a1 u
  else J u v) :=
  ⟨_, _, _, _, rfl, rfl, rfl, rfl, op.eq_1 u v⟩

/-- free, or `v = J u _` with a strictly smaller result -/
theorem TRs (u v : M) : op u v = J u v ∨ (tg v = 2 ∧ a1 v = u ∧ sz (op u v) < sz v) := by
  obtain ⟨p1, p2, p3, p4, -, -, -, -, hop⟩ := op_cases u v
  rw [hop]
  split
  · rename_i h
    have := sz_tg v h.1; have := sz_a1 (a2 v); have := sz_a2 (a1 (a2 v))
    exact Or.inr ⟨h.1, h.2.1.symm, by omega⟩
  · split
    · rename_i h
      have := sz_tg v h.1.1; have := congrArg sz h.1.2.1; have := sz_a1 u
      exact Or.inr ⟨h.1.1, h.1.2.1.symm, by omega⟩
    · split
      · rename_i h
        have := sz_tg v h.1.1; have := sz_a2 (a2 v); have := sz_a1 (a2 (a2 v))
        exact Or.inr ⟨h.1.1, h.1.2.1.symm, by omega⟩
      · split
        · rename_i h
          have := sz_tg v h.1.1; have := congrArg sz h.1.2.1; have := sz_a1 u
          exact Or.inr ⟨h.1.1, h.1.2.1.symm, by omega⟩
        · split
          · rename_i h
            have := sz_tg v h.1.1; have := congrArg sz h.1.2.1; have := sz_a1 u
            exact Or.inr ⟨h.1.1, h.1.2.1.symm, by omega⟩
          · split
            · rename_i h
              have := sz_tg v h.1.1; have := congrArg sz h.1.2.1; have := sz_a1 u
              exact Or.inr ⟨h.1.1, h.1.2.1.symm, by omega⟩
            · exact Or.inl rfl

theorem NE (u v : M) : op u v ≠ v := by
  intro h
  rcases TRs u v with h' | ⟨-, -, h'⟩
  · rw [h] at h'; have := congrArg sz h'; simp only [sz] at this; omega
  · rw [h] at h'; exact Nat.lt_irrefl _ h'

theorem Wne {u a : M} (b : M) (h : a ≠ u) : op u (J a b) = J u (J a b) :=
  op_free (fun hp => by
    rcases hp with h1 | h1 | h1 | h1 | h1 | h1 <;>
      exact h (by have e := h1.2.1; simp only [a1_J_eq] at e; exact e.symm))

theorem Wsz {u c : M} (h : sz c ≤ sz u) : op u c = J u c := by
  rcases TRs u c with h' | ⟨hct, hcu, -⟩
  · exact h'
  · exfalso; have := sz_tg c hct; rw [hcu] at this; omega

theorem red1 (u : M) (h2 : tg (a1 (op (a1 u) u)) = 2) (h3 : a2 (a1 (op (a1 u) u)) = a1 u) : sz (op (a1 u) u) < sz u := by
  rcases TRs (a1 u) u with h | ⟨-, -, h⟩
  · rw [h] at h2 h3; simp only [a1_J_eq] at h2 h3
    have := sz_tg _ h2; have := congrArg sz h3; omega
  · exact h

theorem red2 (u : M) (h3 : a1 (op (a1 u) u) = op (a1 (a1 u)) (a1 u)) : sz (op (a1 u) u) < sz u := by
  rcases TRs (a1 u) u with h | ⟨-, -, h⟩
  · rw [h] at h3; simp only [a1_J_eq] at h3; exact absurd h3.symm (NE _ _)
  · exact h

/-- no rule fires on `(y, J y (J x y))` -/
theorem L1 (x y : M) : op y (J y (J x y)) = J y (J y (J x y)) := by
  obtain ⟨p1, p2, p3, p4, hp1, -, hp3, hp4, hop⟩ := op_cases y (J y (J x y))
  have hs1 : msr (a1 y) y < msr y (J y (J x y)) := gJ (Or.inl (sz_a1 _)) (Or.inl (Nat.le_refl _))
  have hs3 : msr (a1 (a1 y)) (a1 y) < msr y (J y (J x y)) := gJ (Or.inl (Nat.le_trans (sz_a1 _) (sz_a1 _))) (Or.inl (sz_a1 _))
  rw [dif_pos hs1] at hp1; subst hp1
  rw [dif_pos hs3] at hp3; subst hp3
  rw [hop]; split
  · rename_i h; exfalso
    obtain ⟨-, -, -, -, h5, -, h7⟩ := h
    simp only [a2_J_eq] at h5 h7
    have := sz_tg y h5; have := congrArg sz h7; omega
  · split
    · rename_i h; exfalso
      obtain ⟨-, -, he⟩ := h
      simp only [a2_J_eq] at he
      exact NE _ _ he.symm
    · split
      · rename_i h; exfalso
        obtain ⟨⟨-, -, -, h4, h5, -⟩, -, -⟩ := h
        simp only [a2_J_eq] at h4 h5
        have := sz_tg y h4; have := congrArg sz h5; omega
      · split
        · rename_i h; exfalso
          obtain ⟨-, -, -, -, he⟩ := h
          simp only [a2_J_eq] at he
          exact NE _ _ he.symm
        · split
          · rename_i h; exfalso
            obtain ⟨-, -, hs4, -, h5, h6, he⟩ := h
            rw [dif_pos hs4] at hp4; subst hp4
            simp only [a2_J_eq] at he
            have hr := red1 y h5 h6
            rcases TRs (a1 (op (a1 y) y)) (op (a1 y) y) with h' | ⟨-, -, h'⟩
            · rw [h'] at he; rw [← (M.J.inj he).2] at hr; exact Nat.lt_irrefl _ hr
            · rw [← he] at h'; simp only [sz] at h'; omega
          · split
            · rename_i h; exfalso
              obtain ⟨-, -, -, hs4, -, h5, he⟩ := h
              rw [dif_pos hs4] at hp4; subst hp4
              simp only [a2_J_eq] at he
              have hr := red2 y h5
              rcases TRs (a1 (op (a1 y) y)) (op (a1 y) y) with h' | ⟨-, -, h'⟩
              · rw [h'] at he; rw [← (M.J.inj he).2] at hr; exact Nat.lt_irrefl _ hr
              · rw [← he] at h'; simp only [sz] at h'; omega
            · rfl

/-- no rule fires on `(x, J x x)` -/
theorem SELF (x : M) : op x (J x x) = J x (J x x) := by
  obtain ⟨p1, p2, p3, p4, hp1, -, hp3, hp4, hop⟩ := op_cases x (J x x)
  have hs1 : msr (a1 x) x < msr x (J x x) := gJ (Or.inl (sz_a1 _)) (Or.inl (Nat.le_refl _))
  have hs3 : msr (a1 (a1 x)) (a1 x) < msr x (J x x) := gJ (Or.inl (Nat.le_trans (sz_a1 _) (sz_a1 _))) (Or.inl (sz_a1 _))
  rw [dif_pos hs1] at hp1; subst hp1
  rw [dif_pos hs3] at hp3; subst hp3
  rw [hop]; split
  · rename_i h; exfalso
    obtain ⟨-, -, h3, -, h5, -, h7⟩ := h
    simp only [a2_J_eq] at h3 h5 h7
    have := sz_tg x h3; have := sz_tg _ h5; have := congrArg sz h7; omega
  · split
    · rename_i h; exfalso
      obtain ⟨⟨-, -, -, h4, -, h6⟩, -, -⟩ := h
      simp only [a1_J_eq, a2_J_eq] at h4 h6
      have := sz_tg _ h4; have := congrArg sz h6; omega
    · split
      · rename_i h; exfalso
        obtain ⟨⟨-, -, h3, h4, h5, -⟩, -, -⟩ := h
        simp only [a2_J_eq] at h3 h4 h5
        have := sz_tg x h3; have := sz_tg _ h4; have := congrArg sz h5; omega
      · split
        · rename_i h; exfalso
          obtain ⟨-, -, -, he, -⟩ := h
          simp only [a1_J_eq, a2_J_eq] at he
          exact NE _ _ he.symm
        · split
          · rename_i h; exfalso
            obtain ⟨-, -, hs4, -, h5, h6, he⟩ := h
            rw [dif_pos hs4] at hp4; subst hp4
            simp only [a2_J_eq] at he
            have hr := red1 x h5 h6
            rcases TRs (a1 (op (a1 x) x)) (op (a1 x) x) with h' | ⟨-, -, h'⟩
            · rw [h'] at he
              have e := congrArg a1 he; simp only [a1_J_eq] at e
              have := sz_tg _ h5; have := congrArg sz (h6.trans e); omega
            · rw [← he] at h'; omega
          · split
            · rename_i h; exfalso
              obtain ⟨-, -, -, hs4, -, h5, he⟩ := h
              rw [dif_pos hs4] at hp4; subst hp4
              simp only [a2_J_eq] at he
              have hr := red2 x h5
              rcases TRs (a1 (op (a1 x) x)) (op (a1 x) x) with h' | ⟨-, -, h'⟩
              · rw [h'] at he
                have e := congrArg a1 he; simp only [a1_J_eq] at e
                exact NE _ _ (h5.symm.trans e.symm)
              · rw [← he] at h'; omega
            · rfl

theorem L1' (x y a : M) : op y (J a (J x y)) = J y (J a (J x y)) := by
  by_cases h : a = y
  · rw [h]; exact L1 x y
  · exact Wne _ h

/-- R1: a, b free -/
theorem op_R1 (x y z : M) : op y (op y (J (J z x) (J x y))) = x := by
  rw [L1']
  obtain ⟨p1, p2, p3, p4, -, -, -, -, hop⟩ := op_cases y (J y (J (J z x) (J x y)))
  rw [hop, if_pos (show P1 y (J y (J (J z x) (J x y))) from ⟨rfl, rfl, rfl, rfl, rfl, rfl, rfl⟩)]
  rfl

/-- R2: b decoded, a free -/
theorem op_R2 (x y2 z u : M) (hu : u = J x y2) (hsb : sz (op x u) < sz u) : op u (op u (J (J z x) (op x u))) = x := by
  have hw : op u (J (J z x) (op x u)) = J u (J (J z x) (op x u)) := by
    by_cases h : J z x = u
    · exfalso; subst hu; obtain ⟨rfl, rfl⟩ := M.J.inj h
      rw [SELF] at hsb; simp only [sz] at hsb; omega
    · exact Wne _ h
  rw [hw]
  obtain ⟨p1, p2, p3, p4, hp1, -, -, -, hop⟩ := op_cases u (J u (J (J z x) (op x u)))
  have hs1 : msr (a1 u) u < msr u (J u (J (J z x) (op x u))) := gJ (Or.inl (sz_a1 _)) (Or.inl (Nat.le_refl _))
  rw [dif_pos hs1] at hp1; subst hu
  simp only [a1_J_eq] at hp1; subst hp1
  rw [hop]; split
  · rename_i h; exfalso
    obtain ⟨-, -, -, -, -, -, h7⟩ := h
    simp only [a2_J_eq] at h7
    have := congrArg sz h7; have := sz_a2 (op x (J x y2)); omega
  · split
    · rfl
    · rename_i h; exact absurd ⟨⟨rfl, rfl, rfl, rfl, rfl, rfl⟩, hs1, rfl⟩ h

/-- R3: a decoded, b free -/
theorem op_R3 (x2 y z u : M) (hu : u = J z x2) (hsa : sz (op z u) < sz u) : op y (op y (J (op z u) (J u y))) = u := by
  rw [L1']
  generalize hv : J y (J (op z u) (J u y)) = v
  obtain ⟨p1, p2, p3, p4, hp1, hp2, -, -, hop⟩ := op_cases y v
  have hs1 : msr (a1 y) y < msr y v := by subst hv; exact gJ (Or.inl (sz_a1 _)) (Or.inl (Nat.le_refl _))
  have hs2 : msr (a1 (a1 (a2 (a2 v)))) (a1 (a2 (a2 v))) < msr y v := by
    subst hv; simp only [a1_J_eq, a2_J_eq]
    exact gJ (Or.inr (by simp only [sz]; have := sz_a1 u; omega)) (Or.inr (by simp only [sz]; omega))
  rw [dif_pos hs1] at hp1; subst hp1
  rw [dif_pos hs2] at hp2; subst hv; subst hu
  simp only [a1_J_eq, a2_J_eq] at hp2; subst hp2
  rw [hop]; split
  · rename_i h; exfalso
    obtain ⟨-, -, -, -, -, h6, -⟩ := h
    simp only [a1_J_eq, a2_J_eq] at h6
    have := congrArg sz h6; have := sz_a2 (op z (J z x2)); omega
  · split
    · rename_i h; exfalso
      obtain ⟨⟨-, -, -, -, -, h6⟩, -, he⟩ := h
      simp only [a1_J_eq, a2_J_eq] at h6 he
      rcases TRs (a1 y) y with h' | ⟨-, -, h'⟩
      · rw [h'] at he; rw [← (M.J.inj he).1] at h6
        have := congrArg sz h6; have := sz_a2 (op z (J z x2)); omega
      · rw [← he] at h'; simp only [sz] at h'; omega
    · split
      · rfl
      · rename_i h; exact absurd ⟨⟨rfl, rfl, rfl, rfl, rfl, rfl⟩, hs2, rfl⟩ h

/-- R4: a and b decoded -/
theorem op_R4 (x2 y2 z x u : M) (hx : x = J z x2) (hu : u = J x y2) (hsa : sz (op z x) < sz x) (hsb : sz (op x u) < sz u) : op u (op u (J (op z x) (op x u))) = x := by
  have hw : op u (J (op z x) (op x u)) = J u (J (op z x) (op x u)) :=
    Wne _ (ne_of_sz (Nat.lt_trans hsa (by subst hu; exact szJ2 _ _)))
  rw [hw]
  generalize hv : J u (J (op z x) (op x u)) = v
  obtain ⟨p1, p2, p3, p4, hp1, -, hp3, -, hop⟩ := op_cases u v
  have hs1 : msr (a1 u) u < msr u v := by subst hv; exact gJ (Or.inl (sz_a1 _)) (Or.inl (Nat.le_refl _))
  have hs3 : msr (a1 (a1 u)) (a1 u) < msr u v := by subst hv; exact gJ (Or.inl (Nat.le_trans (sz_a1 _) (sz_a1 _))) (Or.inl (sz_a1 _))
  rw [dif_pos hs1] at hp1; rw [dif_pos hs3] at hp3
  subst hv; subst hu; subst hx
  simp only [a1_J_eq] at hp1 hp3; subst hp1; subst hp3
  rw [hop]; split
  · rename_i h; exfalso
    obtain ⟨-, -, -, -, -, -, h7⟩ := h
    simp only [a2_J_eq] at h7
    have := congrArg sz h7; have := sz_a2 (op (J z x2) (J (J z x2) y2)); omega
  · split
    · rename_i h; exfalso
      obtain ⟨⟨-, -, -, -, -, h6⟩, -, -⟩ := h
      simp only [a1_J_eq, a2_J_eq] at h6
      have := congrArg sz h6; have := sz_a2 (op z (J z x2)); omega
    · split
      · rename_i h; exfalso
        obtain ⟨⟨-, -, -, -, h5, -⟩, -, -⟩ := h
        simp only [a2_J_eq] at h5
        have := congrArg sz h5; have := sz_a2 (op (J z x2) (J (J z x2) y2)); omega
      · split
        · rfl
        · rename_i h; exact absurd ⟨⟨rfl, rfl, rfl, rfl, rfl⟩, hs3, hs1, rfl, rfl⟩ h

/-- R5: c decoded, a free -/
theorem op_R5 (x y2 z b2 u c : M) (hu : u = J x y2) (hb : op x u = J (J z x) b2) (hc : op (J z x) (J (J z x) b2) = c) (hsb : sz (J (J z x) b2) < sz u) (hsc : sz c < sz (J (J z x) b2)) : op u (op u c) = x := by
  have hw : op u c = J u c := Wsz (by omega)
  rw [hw]
  obtain ⟨p1, p2, p3, p4, hp1, -, -, hp4, hop⟩ := op_cases u (J u c)
  have hs1 : msr (a1 u) u < msr u (J u c) := gJ (Or.inl (sz_a1 _)) (Or.inl (Nat.le_refl _))
  rw [dif_pos hs1] at hp1; subst hu
  simp only [a1_J_eq] at hp1; rw [hb] at hp1; subst hp1
  have hs4 : msr (a1 (J (J z x) b2)) (J (J z x) b2) < msr (J x y2) (J (J x y2) c) := gJ (Or.inl (Nat.le_trans (sz_a1 _) (Nat.le_of_lt hsb))) (Or.inl (Nat.le_of_lt hsb))
  rw [dif_pos hs4] at hp4; subst hp4
  rw [hop]; split
  · rename_i h; exfalso
    obtain ⟨-, -, -, -, -, -, h7⟩ := h
    simp only [a2_J_eq] at h7
    have := congrArg sz h7; have := sz_a2 (a2 c); have := sz_a2 c; omega
  · split
    · rename_i h; exfalso
      obtain ⟨-, -, he⟩ := h
      simp only [a2_J_eq] at he
      have := congrArg sz he; have := sz_a2 c; omega
    · split
      · rename_i h; exfalso
        obtain ⟨⟨-, -, -, -, h5, -⟩, -, -⟩ := h
        simp only [a2_J_eq] at h5
        have := congrArg sz h5; have := sz_a2 (a2 c); have := sz_a2 c; omega
      · split
        · rename_i h; exfalso
          obtain ⟨-, -, -, -, he⟩ := h
          simp only [a2_J_eq] at he
          have := congrArg sz he; have := sz_a2 c; omega
        · split
          · rfl
          · rename_i h; exact absurd ⟨⟨rfl, rfl, rfl⟩, hs1, hs4, rfl, rfl, rfl, hc.symm⟩ h

/-- R6: c decoded, a decoded -/
theorem op_R6 (x2 y2 z b2 x u c : M) (hx : x = J z x2) (hu : u = J x y2) (hsa : sz (op z x) < sz x) (hb : op x u = J (op z x) b2) (hc : op (op z x) (J (op z x) b2) = c) (hsb : sz (J (op z x) b2) < sz u) (hsc : sz c < sz (J (op z x) b2)) : op u (op u c) = x := by
  have hw : op u c = J u c := Wsz (by omega)
  rw [hw]
  obtain ⟨p1, p2, p3, p4, hp1, -, hp3, hp4, hop⟩ := op_cases u (J u c)
  have hs1 : msr (a1 u) u < msr u (J u c) := gJ (Or.inl (sz_a1 _)) (Or.inl (Nat.le_refl _))
  have hs3 : msr (a1 (a1 u)) (a1 u) < msr u (J u c) := gJ (Or.inl (Nat.le_trans (sz_a1 _) (sz_a1 _))) (Or.inl (sz_a1 _))
  rw [dif_pos hs1] at hp1; rw [dif_pos hs3] at hp3; subst hu
  simp only [a1_J_eq] at hp1 hp3; rw [hb] at hp1; subst hp1; subst hx
  simp only [a1_J_eq] at hp3; subst hp3
  have hs4 : msr (a1 (J (op z (J z x2)) b2)) (J (op z (J z x2)) b2) < msr (J (J z x2) y2) (J (J (J z x2) y2) c) := gJ (Or.inl (Nat.le_trans (sz_a1 _) (Nat.le_of_lt hsb))) (Or.inl (Nat.le_of_lt hsb))
  rw [dif_pos hs4] at hp4; subst hp4
  rw [hop]; split
  · rename_i h; exfalso
    obtain ⟨-, -, -, -, -, -, h7⟩ := h
    simp only [a2_J_eq] at h7
    have := congrArg sz h7; have := sz_a2 (a2 c); have := sz_a2 c; omega
  · split
    · rename_i h; exfalso
      obtain ⟨-, -, he⟩ := h
      simp only [a2_J_eq] at he
      have := congrArg sz he; have := sz_a2 c; omega
    · split
      · rename_i h; exfalso
        obtain ⟨⟨-, -, -, -, h5, -⟩, -, -⟩ := h
        simp only [a2_J_eq] at h5
        have := congrArg sz h5; have := sz_a2 (a2 c); have := sz_a2 c; omega
      · split
        · rename_i h; exfalso
          obtain ⟨-, -, -, -, he⟩ := h
          simp only [a2_J_eq] at he
          have := congrArg sz he; have := sz_a2 c; omega
        · split
          · rename_i h; exfalso
            obtain ⟨-, -, -, -, h5, h6, -⟩ := h
            simp only [a1_J_eq, a2_J_eq] at h5 h6
            have := sz_tg _ h5; have := congrArg sz h6; omega
          · split
            · rfl
            · rename_i h; exact absurd ⟨⟨rfl, rfl, rfl, rfl⟩, hs1, hs3, hs4, rfl, rfl, hc.symm⟩ h

/-- THE LAW: x = y * (y * ((z * x) * (x * y))) -/
theorem law (x y z : M) : op (y) (op (y) (op (op (z) (x)) (op (x) (y)))) = x := by
  rcases TRs z x with ha | ⟨hxt, hxz, hsa⟩
  · rw [ha]
    rcases TRs x y with hb | ⟨hyt, hyx, hsb⟩
    · rw [hb, Wne _ (ne_of_sz (szJ1 z x))]; exact op_R1 x y z
    · obtain ⟨x', y2, rfl⟩ := tg_J y hyt
      simp only [a1_J_eq] at hyx; subst x'
      rcases TRs (J z x) (op x (J x y2)) with hc | ⟨hbt, hba, hsc⟩
      · rw [hc]; exact op_R2 _ _ _ _ rfl hsb
      · obtain ⟨a', b2, hb'⟩ := tg_J _ hbt
        rw [hb'] at hba; simp only [a1_J_eq] at hba; subst a'
        rw [hb'] at hsb hsc ⊢
        exact op_R5 _ _ _ _ _ _ rfl hb' rfl hsb hsc
  · obtain ⟨z', x2, rfl⟩ := tg_J x hxt
    simp only [a1_J_eq] at hxz; subst z'
    rcases TRs (J z x2) y with hb | ⟨hyt, hyx, hsb⟩
    · rw [hb, Wne _ (ne_of_sz hsa).symm]; exact op_R3 _ _ _ _ rfl hsa
    · obtain ⟨x', y2, rfl⟩ := tg_J y hyt
      simp only [a1_J_eq] at hyx; subst x'
      rcases TRs (op z (J z x2)) (op (J z x2) (J (J z x2) y2)) with hc | ⟨hbt, hba, hsc⟩
      · rw [hc]; exact op_R4 _ _ _ _ _ rfl rfl hsa hsb
      · obtain ⟨a', b2, hb'⟩ := tg_J _ hbt
        rw [hb'] at hba; simp only [a1_J_eq] at hba; subst a'
        rw [hb'] at hsb hsc ⊢
        exact op_R6 _ _ _ _ _ _ _ rfl rfl hsa hb' rfl hsb hsc


theorem lhs : @EquationLHS M inst := by
  intro x y z
  first | exact (law x y z).symm | exact (law x z y).symm | exact (law y x z).symm | exact (law y z x).symm | exact (law z x y).symm | exact (law z y x).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
