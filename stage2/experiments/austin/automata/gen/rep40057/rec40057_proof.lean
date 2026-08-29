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

def P1 (u v : M) : Prop := tg v = 2 ∧ u = a1 v ∧ tg (a2 v) = 2 ∧ tg (a2 (a2 v)) = 2 ∧ tg (a1 (a2 (a2 v))) = 2 ∧ a1 (a2 v) = a2 (a1 (a2 (a2 v))) ∧ u = a2 (a2 (a2 v))
instance (u v : M) : Decidable (P1 u v) := by unfold P1; infer_instance
def P2 (u v : M) : Prop := tg v = 2 ∧ u = a1 v ∧ tg (a2 v) = 2 ∧ tg (a2 (a2 v)) = 2 ∧ u = a2 (a2 (a2 v)) ∧ tg (a1 (a2 v)) = 2
instance (u v : M) : Decidable (P2 u v) := by unfold P2; infer_instance
def P3 (u v : M) : Prop := tg v = 2 ∧ u = a1 v ∧ tg (a2 v) = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 (a2 v) = a2 (a1 u)
instance (u v : M) : Decidable (P3 u v) := by unfold P3; infer_instance
def P4 (u v : M) : Prop := tg v = 2 ∧ u = a1 v ∧ tg (a2 v) = 2 ∧ tg u = 2 ∧ tg (a1 (a2 v)) = 2
instance (u v : M) : Decidable (P4 u v) := by unfold P4; infer_instance
def P5 (u v : M) : Prop := tg v = 2 ∧ u = a1 v ∧ tg u = 2 ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ tg (a1 u) = 2 ∧ a2 (a1 u) = a1 (a1 (a2 u))
instance (u v : M) : Decidable (P5 u v) := by unfold P5; infer_instance
def P6 (u v : M) : Prop := tg v = 2 ∧ u = a1 v ∧ tg u = 2 ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ tg (a1 (a1 (a2 u))) = 2
instance (u v : M) : Decidable (P6 u v) := by unfold P6; infer_instance
def op (u v : M) : M :=
  let p1 := if hs1 : msr (a1 (a1 (a2 v))) (a1 (a2 v)) < msr u v then op (a1 (a1 (a2 v))) (a1 (a2 v)) else J u v
  let p2 := if hs2 : msr (a1 u) (u) < msr u v then op (a1 u) (u) else J u v
  let p3 := if hs3 : msr (a1 (a1 (a2 u))) (a1 (a2 u)) < msr u v then op (a1 (a1 (a2 u))) (a1 (a2 u)) else J u v
  let p4 := if hs4 : msr (a1 (a1 (a1 (a2 u)))) (a1 (a1 (a2 u))) < msr u v then op (a1 (a1 (a1 (a2 u)))) (a1 (a1 (a2 u))) else J u v
  if P1 u v then a1 (a2 v)
  else if P2 u v ∧ msr (a1 (a1 (a2 v))) (a1 (a2 v)) < msr u v ∧ a1 (a2 (a2 v)) = p1 then a1 (a2 v)
  else if P3 u v ∧ msr (a1 u) (u) < msr u v ∧ a2 (a2 v) = p2 then a1 (a2 v)
  else if P4 u v ∧ msr (a1 u) (u) < msr u v ∧ msr (a1 (a1 (a2 v))) (a1 (a2 v)) < msr u v ∧ a2 (a2 v) = p2 ∧ a1 u = p1 then a1 (a2 v)
  else if P5 u v ∧ msr (a1 (a1 (a2 u))) (a1 (a2 u)) < msr u v ∧ msr (a1 u) (u) < msr u v ∧ a2 v = p3 ∧ a1 (a2 u) = p2 then a1 (a1 (a2 u))
  else if P6 u v ∧ msr (a1 (a1 (a2 u))) (a1 (a2 u)) < msr u v ∧ msr (a1 u) (u) < msr u v ∧ msr (a1 (a1 (a1 (a2 u)))) (a1 (a1 (a2 u))) < msr u v ∧ a2 v = p3 ∧ a1 (a2 u) = p2 ∧ a1 u = p4 then a1 (a1 (a2 u))
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
  have := h (g 1) (g 0) (g 2)
  revert this
  change ¬ g 1 = op (op (g 2) (g 0)) (op (g 1) (op (g 0) (op (g 0) (g 0))))
  simp (config := {decide := true}) [op.eq_1, sz, P1, P2, P3, P4, P5, P6]


theorem sz_pos (t : M) : 1 ≤ sz t := by cases t <;> simp [sz] <;> omega
@[simp] theorem sz_J (a b : M) : sz (J a b) = sz a + sz b + 1 := rfl
theorem sz_a1_lt {t : M} (h : tg t = 2) : sz (a1 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a1]; have := sz_pos b; omega
theorem sz_a2_lt {t : M} (h : tg t = 2) : sz (a2 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a2]; have := sz_pos a; omega
theorem msr_lt_both {a b u v : M} (ha : sz a < sz v) (hb : sz b < sz v) : msr a b < msr u v :=
  msr_lt_of_max_lt (by omega)
theorem msr_lt_r {u b v : M} (h : sz b < sz v) : msr u b < msr u v := by
  have hm : max (sz u) (sz b) ≤ max (sz u) (sz v) := by omega
  rcases Nat.lt_or_eq_of_le hm with hlt | heq
  · exact msr_lt_of_max_lt hlt
  · exact msr_lt_of_max_eq heq (by omega)

theorem op_cases (u v : M) : ∃ p1 p2 p3 p4 : M,
    p1 = (if hs1 : msr (a1 (a1 (a2 v))) (a1 (a2 v)) < msr u v then op (a1 (a1 (a2 v))) (a1 (a2 v)) else J u v) ∧
    p2 = (if hs2 : msr (a1 u) (u) < msr u v then op (a1 u) (u) else J u v) ∧
    p3 = (if hs3 : msr (a1 (a1 (a2 u))) (a1 (a2 u)) < msr u v then op (a1 (a1 (a2 u))) (a1 (a2 u)) else J u v) ∧
    p4 = (if hs4 : msr (a1 (a1 (a1 (a2 u)))) (a1 (a1 (a2 u))) < msr u v then op (a1 (a1 (a1 (a2 u)))) (a1 (a1 (a2 u))) else J u v) ∧
    op u v = (
  if P1 u v then a1 (a2 v)
  else if P2 u v ∧ msr (a1 (a1 (a2 v))) (a1 (a2 v)) < msr u v ∧ a1 (a2 (a2 v)) = p1 then a1 (a2 v)
  else if P3 u v ∧ msr (a1 u) (u) < msr u v ∧ a2 (a2 v) = p2 then a1 (a2 v)
  else if P4 u v ∧ msr (a1 u) (u) < msr u v ∧ msr (a1 (a1 (a2 v))) (a1 (a2 v)) < msr u v ∧ a2 (a2 v) = p2 ∧ a1 u = p1 then a1 (a2 v)
  else if P5 u v ∧ msr (a1 (a1 (a2 u))) (a1 (a2 u)) < msr u v ∧ msr (a1 u) (u) < msr u v ∧ a2 v = p3 ∧ a1 (a2 u) = p2 then a1 (a1 (a2 u))
  else if P6 u v ∧ msr (a1 (a1 (a2 u))) (a1 (a2 u)) < msr u v ∧ msr (a1 u) (u) < msr u v ∧ msr (a1 (a1 (a1 (a2 u)))) (a1 (a1 (a2 u))) < msr u v ∧ a2 v = p3 ∧ a1 (a2 u) = p2 ∧ a1 u = p4 then a1 (a1 (a2 u))
  else J u v) :=
  ⟨_, _, _, _, rfl, rfl, rfl, rfl, op.eq_1 u v⟩

theorem TR (u v : M) : op u v = J u v ∨ (tg v = 2 ∧ u = a1 v ∧ (
    (op u v = a1 (a2 v) ∧ tg (a2 v) = 2 ∧ (
       (tg (a2 (a2 v)) = 2 ∧ u = a2 (a2 (a2 v))) ∨
       (tg u = 2 ∧ a2 (a2 v) = op (a1 u) u))) ∨
    (op u v = a1 (a1 (a2 u)) ∧ tg u = 2 ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧
       a2 v = op (a1 (a1 (a2 u))) (a1 (a2 u)) ∧ a1 (a2 u) = op (a1 u) u ∧
       ((tg (a1 u) = 2 ∧ a2 (a1 u) = a1 (a1 (a2 u))) ∨
        (tg (a1 (a1 (a2 u))) = 2 ∧ a1 u = op (a1 (a1 (a1 (a2 u)))) (a1 (a1 (a2 u)))))))) := by
  obtain ⟨p1, p2, p3, p4, hp1, hp2, hp3, hp4, hop⟩ := op_cases u v
  rw [hop]
  split
  · rename_i h
    obtain ⟨h1, h2, h3, h4, h5, h6, h7⟩ := h
    exact Or.inr ⟨h1, h2, Or.inl ⟨rfl, h3, Or.inl ⟨h4, h7⟩⟩⟩
  · split
    · rename_i h
      obtain ⟨⟨h1, h2, h3, h4, h5, h6⟩, hs1, he⟩ := h
      exact Or.inr ⟨h1, h2, Or.inl ⟨rfl, h3, Or.inl ⟨h4, h5⟩⟩⟩
    · split
      · rename_i h
        obtain ⟨⟨h1, h2, h3, h4, h5, h6⟩, hs2, he⟩ := h
        rw [dif_pos hs2] at hp2; subst hp2
        exact Or.inr ⟨h1, h2, Or.inl ⟨rfl, h3, Or.inr ⟨h4, he⟩⟩⟩
      · split
        · rename_i h
          obtain ⟨⟨h1, h2, h3, h4, h5⟩, hs2, hs1, he, he2⟩ := h
          rw [dif_pos hs2] at hp2; subst hp2
          exact Or.inr ⟨h1, h2, Or.inl ⟨rfl, h3, Or.inr ⟨h4, he⟩⟩⟩
        · split
          · rename_i h
            obtain ⟨⟨h1, h2, h3, h4, h5, h6, h7⟩, hs3, hs2, he3, he2⟩ := h
            rw [dif_pos hs3] at hp3; subst hp3
            rw [dif_pos hs2] at hp2; subst hp2
            exact Or.inr ⟨h1, h2, Or.inr ⟨rfl, h3, h4, h5, he3, he2, Or.inl ⟨h6, h7⟩⟩⟩
          · split
            · rename_i h
              obtain ⟨⟨h1, h2, h3, h4, h5, h6⟩, hs3, hs2, hs4, he3, he2, he4⟩ := h
              rw [dif_pos hs3] at hp3; subst hp3
              rw [dif_pos hs2] at hp2; subst hp2
              rw [dif_pos hs4] at hp4; subst hp4
              exact Or.inr ⟨h1, h2, Or.inr ⟨rfl, h3, h4, h5, he3, he2, Or.inr ⟨h6, he4⟩⟩⟩
            · left; rfl

theorem TR2 (u v : M) : op u v = J u v ∨ (tg v = 2 ∧ u = a1 v ∧ sz (op u v) < sz v ∧
    ((op u v = a1 (a2 v) ∧ tg (a2 v) = 2) ∨
     (op u v = a1 (a1 (a2 u)) ∧ tg u = 2 ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2))) := by
  rcases TR u v with h | ⟨h1, h2, ⟨hr, h3, -⟩ | ⟨hr, h3, h4, h5, -⟩⟩
  · exact Or.inl h
  · right; refine ⟨h1, h2, ?_, Or.inl ⟨hr, h3⟩⟩
    rw [hr]; have := sz_a1 (a2 v); have := sz_a2_lt h1; omega
  · right; refine ⟨h1, h2, ?_, Or.inr ⟨hr, h3, h4, h5⟩⟩
    rw [hr]; have := sz_a1 (a1 (a2 u)); have := sz_a1 (a2 u); have := sz_a2 u
    have := sz_a1_lt h1; rw [← h2] at this; omega

theorem Tfree {x y z P0 P1 E : M} (hP0 : op z x = P0) (hP1 : op P0 y = P1) (hE : op x P1 = E) :
    op y E = J y E := by
  rcases TR y E with h | ⟨htE, hyE, h⟩
  · exact h
  · exfalso
    have hszE : sz y < sz E := by have := sz_a1_lt htE; rw [← hyE] at this; exact this
    have tE := TR2 x P1; rw [hE] at tE
    have tP := TR2 P0 y; rw [hP1] at tP
    have tZ := TR2 z x; rw [hP0] at tZ
    rcases tE with hEf | ⟨htP1, hxP1, hszE2, hEloc⟩
    · subst hEf
      simp only [a1_J_eq] at hyE
      subst x
      simp only [a2_J_eq, a1_J_eq] at h
      rcases h with ⟨-, htP1, ⟨htAA, hu⟩ | ⟨-, hop⟩⟩ | ⟨-, hty, hta2y, hta12, hv, hq, -⟩
      · have s1 := sz_a2_lt htP1; have s2 := sz_a2_lt htAA; have s3 := congrArg sz hu
        rcases tP with hPf | ⟨-, -, hszP1, -⟩
        · subst hPf
          simp only [a2_J_eq] at hu htAA s3
          have := sz_a2_lt htAA; omega
        · omega
      · rcases tP with hPf | ⟨-, hP0y, hszP1, -⟩
        · subst hPf; simp only [a2_J_eq] at hop
          rcases TR2 (a1 y) y with hf | ⟨-, -, hs, -⟩
          · rw [hf] at hop; have := congrArg sz hop; simp only [sz_J] at this; omega
          · rw [← hop] at hs; exact Nat.lt_irrefl _ hs
        · rw [← hP0y, hP1] at hop
          have := congrArg sz hop; have := sz_a2_lt htP1; omega
      · rcases tP with hPf | ⟨-, hP0y, hszP1, -⟩
        · subst hPf
          rcases TR2 (a1 (a1 (a2 y))) (a1 (a2 y)) with hf | ⟨-, -, hs, -⟩
          · rw [hf] at hv; obtain ⟨-, h2⟩ := M.J.inj hv
            have := congrArg sz h2; have := sz_a1 (a2 y); have := sz_a2_lt hty; omega
          · rw [← hv] at hs; simp only [sz_J] at hs; have := sz_a1 (a2 y); have := sz_a2_lt hty; omega
        · rw [← hP0y, hP1] at hq
          rw [hq] at hv
          rcases TR2 (a1 P1) P1 with hf | ⟨-, -, hs, -⟩
          · rw [hf] at hv; have := congrArg sz hv; simp only [sz_J] at this; omega
          · rw [← hv] at hs; exact Nat.lt_irrefl _ hs
    · rcases tP with hPf | ⟨-, -, hszP1, -⟩
      · subst hPf
        simp only [a1_J_eq, a2_J_eq] at hxP1 hEloc
        rcases hEloc with ⟨hEl, -⟩ | ⟨-, -, -, -⟩
        · have := congrArg sz hEl; have := sz_a1 y; omega
        · rw [← hxP1] at tZ
          rcases tZ with hf | ⟨-, -, hs, -⟩
          · have := congrArg sz hf; simp only [sz_J] at this; omega
          · exact Nat.lt_irrefl _ hs
      · omega

theorem main {x y z P0 P1 E : M} (hP0 : op z x = P0) (hP1 : op P0 y = P1) (hE : op x P1 = E) :
    op y (J y E) = x := by
  have tE := TR2 x P1; rw [hE] at tE
  have tP := TR2 P0 y; rw [hP1] at tP
  have tZ := TR2 z x; rw [hP0] at tZ
  obtain ⟨p1, p2, p3, p4, hp1, hp2, hp3, hp4, hop⟩ := op_cases y (J y E)
  rw [hop]
  rcases tE with hEf | ⟨htP1, hxP1, hszE, hEloc⟩
  · -- E = J x P1: one of R1-R4 fires, and each returns a1 (a2 v) = x
    subst hEf
    split
    · rfl
    · split
      · rfl
      · split
        · rfl
        · split
          · rfl
          · exfalso
            rename_i h1 h2 h3 h4
            rcases tP with hPf | ⟨hty, hP0y, hszP1, -⟩
            · subst hPf
              rcases tZ with hZf | ⟨htx, hzx, hszP0, -⟩
              · subst hZf
                exact h1 ⟨rfl, rfl, rfl, rfl, rfl, rfl, rfl⟩
              · have g1 : msr (a1 (a1 (a2 (J y (J x (J P0 y)))))) (a1 (a2 (J y (J x (J P0 y))))) < msr y (J y (J x (J P0 y))) := by
                  simp only [a1_J_eq, a2_J_eq]
                  apply msr_lt_both <;> (simp only [sz_J]; have := sz_a1 x; omega)
                rw [dif_pos g1] at hp1; subst hp1
                apply h2
                refine ⟨⟨rfl, rfl, rfl, rfl, rfl, htx⟩, g1, ?_⟩
                simp only [a1_J_eq, a2_J_eq]
                rw [← hzx]; exact hP0.symm
            · have g2 : msr (a1 y) y < msr y (J y (J x P1)) :=
                msr_lt_both (by simp only [sz_J]; have := sz_a1 y; omega) (by simp only [sz_J]; omega)
              rw [dif_pos g2] at hp2; subst hp2
              rcases tZ with hZf | ⟨htx, hzx, hszP0, -⟩
              · apply h3
                refine ⟨⟨rfl, rfl, rfl, hty, ?_, ?_⟩, g2, ?_⟩
                · rw [← hP0y, hZf]; rfl
                · simp only [a1_J_eq, a2_J_eq]; rw [← hP0y, hZf]; rfl
                · simp only [a1_J_eq, a2_J_eq]; rw [← hP0y]; exact hP1.symm
              · have g1 : msr (a1 (a1 (a2 (J y (J x P1))))) (a1 (a2 (J y (J x P1)))) < msr y (J y (J x P1)) := by
                  simp only [a1_J_eq, a2_J_eq]
                  apply msr_lt_both <;> (simp only [sz_J]; have := sz_a1 x; omega)
                rw [dif_pos g1] at hp1; subst hp1
                apply h4
                refine ⟨⟨rfl, rfl, rfl, hty, htx⟩, g2, g1, ?_, ?_⟩
                · simp only [a1_J_eq, a2_J_eq]; rw [← hP0y]; exact hP1.symm
                · simp only [a1_J_eq, a2_J_eq]; rw [← hP0y, ← hzx]; exact hP0.symm
  · -- E is a decoded payload: x = a1 P1, P1 = a1 (a2 y); R1-R4 cannot fire; R5 or R6 does
    rcases tP with hPf | ⟨hty, hP0y, hszP1, hloc⟩
    · exfalso
      subst hPf
      simp only [a1_J_eq] at hxP1
      rw [← hxP1] at tZ
      rcases tZ with hf | ⟨-, -, hs, -⟩
      · have := congrArg sz hf; simp only [sz_J] at this; omega
      · exact Nat.lt_irrefl _ hs
    · have hsP1 : sz (a1 P1) < sz P1 := sz_a1_lt htP1
      rcases hloc with ⟨hP1y, hta2y⟩ | ⟨hP1l, htP0, -, -⟩
      · split
        · rename_i h
          obtain ⟨-, -, htA, htAA, -, -, hu⟩ := h
          simp only [a2_J_eq] at htA htAA hu
          have := sz_a2_lt htA; have := sz_a2_lt htAA; have := congrArg sz hu; omega
        · split
          · rename_i h
            obtain ⟨⟨-, -, htA, htAA, hu, -⟩, -, -⟩ := h
            simp only [a2_J_eq] at htA htAA hu
            have := sz_a2_lt htA; have := sz_a2_lt htAA; have := congrArg sz hu; omega
          · split
            · rename_i h
              obtain ⟨-, hg2, heq⟩ := h
              rw [dif_pos hg2] at hp2; subst hp2
              simp only [a2_J_eq] at heq
              rw [← hP0y, hP1] at heq
              have := congrArg sz heq; have := sz_a2 E; omega
            · split
              · rename_i h
                obtain ⟨-, hg2, -, heq, -⟩ := h
                rw [dif_pos hg2] at hp2; subst hp2
                simp only [a2_J_eq] at heq
                rw [← hP0y, hP1] at heq
                have := congrArg sz heq; have := sz_a2 E; omega
              · have s1 := sz_a1 (a2 y); have s2 := sz_a2 y; have s3 := sz_a1 (a1 (a2 y)); have s4 := sz_a1 y
                have s5 := sz_a1 (a1 (a1 (a2 y)))
                have g3 : msr (a1 (a1 (a2 y))) (a1 (a2 y)) < msr y (J y E) :=
                  msr_lt_both (by simp only [sz_J]; omega) (by simp only [sz_J]; omega)
                have g2 : msr (a1 y) y < msr y (J y E) :=
                  msr_lt_both (by simp only [sz_J]; omega) (by simp only [sz_J]; omega)
                have g4 : msr (a1 (a1 (a1 (a2 y)))) (a1 (a1 (a2 y))) < msr y (J y E) :=
                  msr_lt_both (by simp only [sz_J]; omega) (by simp only [sz_J]; omega)
                rw [dif_pos g3] at hp3; subst hp3
                rw [dif_pos g2] at hp2; subst hp2
                rw [dif_pos g4] at hp4; subst hp4
                have hE' : a2 (J y E) = op (a1 (a1 (a2 y))) (a1 (a2 y)) := by
                  simp only [a2_J_eq]; rw [← hP1y, ← hxP1]; exact hE.symm
                have hq : a1 (a2 y) = op (a1 y) y := by rw [← hP0y, hP1, hP1y]
                have h5 : tg (a1 (a2 y)) = 2 := by rw [← hP1y]; exact htP1
                rcases tZ with hZf | ⟨htx, hzx, hszP0, -⟩
                · have h6 : tg (a1 y) = 2 := by rw [← hP0y, hZf]; rfl
                  have h7 : a2 (a1 y) = a1 (a1 (a2 y)) := by rw [← hP0y, hZf, ← hP1y, ← hxP1]; rfl
                  rw [if_pos ⟨⟨rfl, rfl, hty, hta2y, h5, h6, h7⟩, g3, g2, hE', hq⟩]
                  rw [← hP1y, ← hxP1]
                · split
                  · rename_i h
                    obtain ⟨⟨-, -, -, -, -, -, heq⟩, -⟩ := h
                    rw [← hP0y, ← hP1y, ← hxP1] at heq
                    have := congrArg sz heq; have := sz_a2 P0; omega
                  · have h6 : tg (a1 (a1 (a2 y))) = 2 := by rw [← hP1y, ← hxP1]; exact htx
                    have h8 : a1 y = op (a1 (a1 (a1 (a2 y)))) (a1 (a1 (a2 y))) := by
                      rw [← hP0y, ← hP1y, ← hxP1, ← hzx]; exact hP0.symm
                    rw [if_pos ⟨⟨rfl, rfl, hty, hta2y, h5, h6⟩, g3, g2, g4, hE', hq, h8⟩]
                    rw [← hP1y, ← hxP1]
      · exfalso
        have s1 := sz_a1 (a1 (a2 P0)); have s2 := sz_a1 (a2 P0); have s3 := sz_a2_lt htP0
        rcases tZ with hZf | ⟨-, -, hszP0, -⟩
        · subst hZf
          simp only [a2_J_eq] at hP1l s1 s2
          have := congrArg sz hP1l; have := congrArg sz hxP1; have := sz_a1 x; omega
        · have := congrArg sz hP1l; have := congrArg sz hxP1; omega

theorem law (x y z : M) : op (y) (op (y) (op (x) (op (op (z) (x)) (y)))) = x := by
  have h1 : op y (op x (op (op z x) y)) = J y (op x (op (op z x) y)) := Tfree rfl rfl rfl
  rw [h1]
  exact main rfl rfl rfl


theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
