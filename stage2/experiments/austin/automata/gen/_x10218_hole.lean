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

def P1 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a2 (a1 v) ∧ tg (a2 v) = 2 ∧ tg (a1 (a2 v)) = 2 ∧ a1 (a1 v) = a2 (a1 (a2 v)) ∧ u = a2 (a2 v)
instance (u v : M) : Decidable (P1 u v) := by unfold P1; infer_instance
def P2 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a2 (a1 v) ∧ tg (a2 v) = 2 ∧ u = a2 (a2 v) ∧ tg (a1 (a1 v)) = 2 ∧ tg (a1 (a1 (a1 v))) = 2
instance (u v : M) : Decidable (P2 u v) := by unfold P2; infer_instance
def P3 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a2 (a1 v) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 (a1 u)) = 2 ∧ a1 (a1 v) = a2 (a2 (a1 u))
instance (u v : M) : Decidable (P3 u v) := by unfold P3; infer_instance
def P4 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a2 (a1 v) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a1 (a1 v)) = 2 ∧ tg (a1 (a1 (a1 v))) = 2
instance (u v : M) : Decidable (P4 u v) := by unfold P4; infer_instance
def P5 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ tg (a1 (a2 v)) = 2 ∧ u = a2 (a2 v)
instance (u v : M) : Decidable (P5 u v) := by unfold P5; infer_instance
def P6 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a2 (a2 v) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2
instance (u v : M) : Decidable (P6 u v) := by unfold P6; infer_instance
def op (u v : M) : M :=
  let p1 := if hs1 : msr (a2 (a1 (a1 (a1 v)))) (a1 (a1 v)) < msr u v then op (a2 (a1 (a1 (a1 v)))) (a1 (a1 v)) else J u v
  let p2 := if hs2 : msr (a2 (a1 u)) (u) < msr u v then op (a2 (a1 u)) (u) else J u v
  let p3 := if hs3 : msr (a2 (a1 (a2 v))) (u) < msr u v then op (a2 (a1 (a2 v))) (u) else J u v
  let p4 := if hs4 : msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v then op (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) else J u v
  if P1 u v then a1 (a1 v)
  else if P2 u v ∧ msr (a2 (a1 (a1 (a1 v)))) (a1 (a1 v)) < msr u v ∧ a1 (a2 v) = p1 then a1 (a1 v)
  else if P3 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a2 v = p2 then a1 (a1 v)
  else if P4 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (a1 (a1 v)))) (a1 (a1 v)) < msr u v ∧ a2 v = p2 ∧ a2 (a1 u) = p1 then a1 (a1 v)
  else if P5 u v ∧ msr (a2 (a1 (a2 v))) (u) < msr u v ∧ a1 v = p3 then a2 (a1 (a2 v))
  else if P6 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ a1 v = p2 ∧ a1 (a2 v) = p4 then a2 (a1 u)
  else J u v
termination_by msr u v
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



theorem sz_pos (t : M) : 1 ≤ sz t := by cases t <;> simp [sz] <;> omega
theorem sz_J (a b : M) : sz (J a b) = sz a + sz b + 1 := rfl
theorem sz_a1_lt {t : M} (h : tg t = 2) : sz (a1 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a1]; have := sz_pos b; omega
theorem sz_a2_lt {t : M} (h : tg t = 2) : sz (a2 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a2]; have := sz_pos a; omega

theorem op_cases (u v : M) : ∃ p1 p2 p3 p4 : M,
    p1 = (if hs1 : msr (a2 (a1 (a1 (a1 v)))) (a1 (a1 v)) < msr u v then op (a2 (a1 (a1 (a1 v)))) (a1 (a1 v)) else J u v) ∧
    p2 = (if hs2 : msr (a2 (a1 u)) (u) < msr u v then op (a2 (a1 u)) (u) else J u v) ∧
    p3 = (if hs3 : msr (a2 (a1 (a2 v))) (u) < msr u v then op (a2 (a1 (a2 v))) (u) else J u v) ∧
    p4 = (if hs4 : msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v then op (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) else J u v) ∧
    op u v = (
  if P1 u v then a1 (a1 v)
  else if P2 u v ∧ msr (a2 (a1 (a1 (a1 v)))) (a1 (a1 v)) < msr u v ∧ a1 (a2 v) = p1 then a1 (a1 v)
  else if P3 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a2 v = p2 then a1 (a1 v)
  else if P4 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (a1 (a1 v)))) (a1 (a1 v)) < msr u v ∧ a2 v = p2 ∧ a2 (a1 u) = p1 then a1 (a1 v)
  else if P5 u v ∧ msr (a2 (a1 (a2 v))) (u) < msr u v ∧ a1 v = p3 then a2 (a1 (a2 v))
  else if P6 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ a1 v = p2 ∧ a1 (a2 v) = p4 then a2 (a1 u)
  else J u v
    ) :=
  ⟨_, _, _, _, rfl, rfl, rfl, rfl, op.eq_1 u v⟩

/-- every rule needs `u` to sit at `a2 (a1 v)` or at `a2 (a2 v)` -/
theorem Pdig {u v : M} (h : Pre u v) :
    tg v = 2 ∧ ((tg (a1 v) = 2 ∧ u = a2 (a1 v)) ∨ (tg (a2 v) = 2 ∧ u = a2 (a2 v))) := by
  rcases h with h|h|h|h|h|h
  · exact ⟨h.1, Or.inl ⟨h.2.1, h.2.2.1⟩⟩
  · exact ⟨h.1, Or.inl ⟨h.2.1, h.2.2.1⟩⟩
  · exact ⟨h.1, Or.inl ⟨h.2.1, h.2.2.1⟩⟩
  · exact ⟨h.1, Or.inl ⟨h.2.1, h.2.2.1⟩⟩
  · exact ⟨h.1, Or.inr ⟨h.2.1, h.2.2.2⟩⟩
  · exact ⟨h.1, Or.inr ⟨h.2.1, h.2.2.1⟩⟩

/-- a product whose right argument is no bigger than its left argument is free -/
theorem Wsz {u v : M} (h : sz v ≤ sz u) : op u v = J u v := by
  by_cases hp : Pre u v
  · exfalso
    obtain ⟨hv, hc⟩ := Pdig hp
    have e0 := sz_a1_lt hv
    have e1 := sz_a2_lt hv
    rcases hc with ⟨h1, h2⟩ | ⟨h1, h2⟩
    · have := sz_a2 (a1 v); rw [← h2] at this; omega
    · have := sz_a2 (a2 v); rw [← h2] at this; omega
  · exact op_free hp

/-- the result of any product is `a1 (a1 v)`, `a2 (a1 (a2 v))` or `a2 (a1 u)` -/
theorem TRs (u v : M) : op u v = J u v ∨
    (tg v = 2 ∧ (op u v = a1 (a1 v) ∨ op u v = a2 (a1 (a2 v)) ∨
      (tg u = 2 ∧ tg (a1 u) = 2 ∧ op u v = a2 (a1 u)))) := by
  by_cases hp : Pre u v
  · obtain ⟨p1, p2, p3, p4, -, -, -, -, hop⟩ := op_cases u v
    have hv := (Pdig hp).1
    rw [hop]
    split
    · exact Or.inr ⟨hv, Or.inl rfl⟩
    · split
      · exact Or.inr ⟨hv, Or.inl rfl⟩
      · split
        · exact Or.inr ⟨hv, Or.inl rfl⟩
        · split
          · exact Or.inr ⟨hv, Or.inl rfl⟩
          · split
            · exact Or.inr ⟨hv, Or.inr (Or.inl rfl)⟩
            · split
              · rename_i h
                exact Or.inr ⟨hv, Or.inr (Or.inr ⟨h.1.2.2.2.1, h.1.2.2.2.2.1, rfl⟩)⟩
              · exact Or.inl rfl
  · exact Or.inl (op_free hp)

/-- a decoded product is strictly smaller than `v`, or (the R6 shape) strictly smaller than `u` -/
theorem TRz (u v : M) : op u v = J u v ∨ sz (op u v) < sz v ∨ sz (op u v) < sz u := by
  rcases TRs u v with h | ⟨hv, h | h | ⟨hu, -, h⟩⟩
  · exact Or.inl h
  · exact Or.inr (Or.inl (by have := sz_a1 (a1 v); have := sz_a1_lt hv; rw [h]; omega))
  · exact Or.inr (Or.inl (by
      have := sz_a2 (a1 (a2 v)); have := sz_a1 (a2 v); have := sz_a2_lt hv; rw [h]; omega))
  · exact Or.inr (Or.inr (by have := sz_a2 (a1 u); have := sz_a1_lt hu; rw [h]; omega))


/-- every rule pins `u` inside `v`, so a decoded product has `sz u < sz v` -/
theorem Dsz {u v : M} (h : op u v ≠ J u v) : sz u < sz v := by
  by_cases hp : Pre u v
  · obtain ⟨hv, hc⟩ := Pdig hp
    rcases hc with ⟨h1, h2⟩ | ⟨h1, h2⟩
    · have e := sz_a2 (a1 v); rw [← h2] at e; have := sz_a1_lt hv; omega
    · have e := sz_a2 (a2 v); rw [← h2] at e; have := sz_a2_lt hv; omega
  · exact absurd (op_free hp) h

/-- and its value is smaller than `v` as well -/
theorem Dv {u v : M} (h : op u v ≠ J u v) : sz (op u v) < sz v := by
  have hs := Dsz h
  rcases TRz u v with h' | h' | h'
  · exact absurd h' h
  · exact h'
  · omega

/-- freeness from two disequalities: nothing else can make a rule fire -/
theorem Wne {u v : M} (h1 : u ≠ a2 (a1 v)) (h2 : u ≠ a2 (a2 v)) : op u v = J u v := by
  by_cases hp : Pre u v
  · exfalso; rcases (Pdig hp).2 with ⟨-, e⟩ | ⟨-, e⟩
    · exact h1 e
    · exact h2 e
  · exact op_free hp


theorem mxl {a b c d : M} (h1 : sz a < sz d) (h2 : sz b < sz d) :
    max (sz a) (sz b) < max (sz c) (sz d) := by
  rw [Nat.max_def, Nat.max_def]; split <;> split <;> omega

/-- the root product when the two inner products are free: rules 1-4 return `a1 (a1 v) = x` when
    `op x y` is free, and all four are impossible when it is not, where rule 5 fires with an
    `rfl` guard. -/
theorem ROOT (x y z : M) : op y (J (op x y) (J (J z x) y)) = x := by
  by_cases hf : op x y = J x y
  · rw [hf]
    obtain ⟨p1, p2, p3, p4, -, -, -, -, hop⟩ := op_cases y (J (J x y) (J (J z x) y))
    rw [hop, if_pos (show P1 y (J (J x y) (J (J z x) y)) from
      ⟨rfl, rfl, rfl, rfl, rfl, rfl, rfl⟩)]
    rfl
  · have hd : sz (op x y) < sz y := Dv hf
    have hsv : sz (J (op x y) (J (J z x) y))
        = sz (op x y) + (sz z + sz x + 1 + sz y + 1) + 1 := rfl
    have hx := sz_pos x; have hy := sz_pos y; have hz := sz_pos z; have ht := sz_pos (op x y)
    have g3 : msr (a2 (a1 (a2 (J (op x y) (J (J z x) y))))) y
        < msr y (J (op x y) (J (J z x) y)) := by
      simp only [a1_J_eq, a2_J_eq]
      exact msr_lt_of_max_lt (mxl (by omega) (by omega))
    obtain ⟨p1, p2, p3, p4, -, -, hp3, -, hop⟩ := op_cases y (J (op x y) (J (J z x) y))
    rw [dif_pos g3] at hp3
    simp only [a1_J_eq, a2_J_eq] at hp3
    subst hp3
    have hne : y ≠ a2 (op x y) := by
      intro he; have := sz_a2 (op x y); rw [← he] at this; omega
    rw [hop]
    split
    · rename_i h; exact absurd h.2.2.1 hne
    · split
      · rename_i h1 h; exact absurd h.1.2.2.1 hne
      · split
        · rename_i h1 h2 h; exact absurd h.1.2.2.1 hne
        · split
          · rename_i h1 h2 h3 h; exact absurd h.1.2.2.1 hne
          · split
            · rfl
            · rename_i h1 h2 h3 h4 h
              exact absurd ⟨⟨rfl, rfl, rfl, rfl⟩, g3, rfl⟩ h


theorem hole : op (g 0) (op (op (J (g 0) (J (J (g 0) (g 0)) (J (J (g 0) (g 0)) (J (J (g 0) (g 0)) (g 0))))) (g 0)) (op (op (J (J (g 0) (g 0)) (J (J (g 0) (g 0)) (g 0))) (J (g 0) (J (J (g 0) (g 0)) (J (J (g 0) (g 0)) (J (J (g 0) (g 0)) (g 0)))))) (g 0))) = (J (g 0) (J (J (g 0) (g 0)) (J (J (g 0) (g 0)) (J (J (g 0) (g 0)) (g 0))))) := by
  simp (config := {decide := true}) [op.eq_1, sz, P1, P2, P3, P4, P5, P6]

theorem law (x y z : M) : op (y) (op (op (x) (y)) (op (op (z) (x)) (y))) = x := by
  sorry

theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
