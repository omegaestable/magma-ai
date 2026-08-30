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

def P1 (u v : M) : Prop := tg v = 2 ∧ tg (a1 (a2 v)) = 2 ∧ a1 (a1 (a2 v)) = u
instance (u v : M) : Decidable (P1 u v) := by unfold P1; infer_instance
def P2 (u v : M) : Prop := tg v = 2 ∧ tg (a1 (a2 v)) = 2 ∧ a1 (a1 (a2 v)) = u
instance (u v : M) : Decidable (P2 u v) := by unfold P2; infer_instance
def P3 (u v : M) : Prop := tg v = 2
instance (u v : M) : Decidable (P3 u v) := by unfold P3; infer_instance
def P4 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2
instance (u v : M) : Decidable (P4 u v) := by unfold P4; infer_instance
def P5 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a2 u) = 2 ∧ a2 v = a1 u ∧ tg (a1 v) = 2 ∧ a2 (a1 v) = u ∧ tg (a1 (a1 v)) = 2 ∧ a1 (a1 (a1 v)) = u
instance (u v : M) : Decidable (P5 u v) := by unfold P5; infer_instance
def op (u v : M) : M :=
  let p1 := if hs1 : msr (a1 (a2 v)) (u) < msr u v then op (a1 (a2 v)) (u) else J u v
  let p2 := if hs2 : msr (u) (a2 (a1 (a2 v))) < msr u v then op (u) (a2 (a1 (a2 v))) else J u v
  let p3 := if hs3 : msr (a1 (a2 (a1 (a2 v)))) (a1 v) < msr u v then op (a1 (a2 (a1 (a2 v)))) (a1 v) else J u v
  let p4 := if hs4 : msr (a2 (a2 (a1 v))) (a1 v) < msr u v then op (a2 (a2 (a1 v))) (a1 v) else J u v
  let p5 := if hs5 : msr (a1 (a2 v)) (a1 v) < msr u v then op (a1 (a2 v)) (a1 v) else J u v
  let p6 := if hs6 : msr (u) (J (a1 (a2 v)) (a1 v)) < msr u v then op (u) (J (a1 (a2 v)) (a1 v)) else J u v
  let p7 := if hs7 : msr (u) (a1 (a1 v)) < msr u v then op (u) (a1 (a1 v)) else J u v
  let p8 := if hs8 : msr (a2 (a2 u)) (u) < msr u v then op (a2 (a2 u)) (u) else J u v
  let p9 := if hs9 : msr (a2 (a2 u)) (a1 v) < msr u v then op (a2 (a2 u)) (a1 v) else J u v
  let p10 := if hs10 : msr (a1 (a1 v)) (u) < msr u v then op (a1 (a1 v)) (u) else J u v
  let p11 := if hs11 : msr (u) (a2 (a1 (a1 v))) < msr u v then op (u) (a2 (a1 (a1 v))) else J u v
  let p12 := if hs12 : msr (a1 (a2 (a1 (a1 v)))) (a2 (a2 u)) < msr u v then op (a1 (a2 (a1 (a1 v)))) (a2 (a2 u)) else J u v
  if P1 u v ∧ msr (a1 (a2 v)) (u) < msr u v ∧ msr (u) (a2 (a1 (a2 v))) < msr u v ∧ msr (a1 (a2 (a1 (a2 v)))) (a1 v) < msr u v ∧ a2 v = p1 ∧ a1 (a2 v) = p2 ∧ a2 (a1 (a2 v)) = p3 then a1 v
  else if P2 u v ∧ msr (a1 (a2 v)) (u) < msr u v ∧ msr (u) (a2 (a1 (a2 v))) < msr u v ∧ msr (a2 (a2 (a1 v))) (a1 v) < msr u v ∧ a2 v = p1 ∧ a1 (a2 v) = p2 ∧ a2 (a1 (a2 v)) = p4 then a1 v
  else if P3 u v ∧ msr (a1 (a2 v)) (u) < msr u v ∧ msr (a1 (a2 v)) (a1 v) < msr u v ∧ msr (u) (J (a1 (a2 v)) (a1 v)) < msr u v ∧ a2 v = p1 ∧ J (a1 (a2 v)) (a1 v) = p5 ∧ a1 (a2 v) = p6 then a1 v
  else if P4 u v ∧ msr (a1 (a2 v)) (u) < msr u v ∧ msr (u) (a1 (a1 v)) < msr u v ∧ msr (a2 (a2 (a1 v))) (a1 v) < msr u v ∧ a2 v = p1 ∧ a1 (a2 v) = p7 ∧ a1 (a1 v) = p4 then a1 v
  else if P5 u v ∧ msr (a2 (a2 u)) (u) < msr u v ∧ msr (a2 (a2 u)) (a1 v) < msr u v ∧ msr (a1 (a1 v)) (u) < msr u v ∧ msr (u) (a2 (a1 (a1 v))) < msr u v ∧ msr (a1 (a2 (a1 (a1 v)))) (a2 (a2 u)) < msr u v ∧ a2 v = p8 ∧ J (a2 (a2 u)) (a1 v) = p9 ∧ a1 v = p10 ∧ a1 (a1 v) = p11 ∧ a2 (a1 (a1 v)) = p12 then a1 v
  else J u v
termination_by msr u v
decreasing_by
  · assumption
  · assumption
  · assumption
  · assumption
  · assumption
  · assumption
  · assumption
  · assumption
  · assumption
  · assumption
  · assumption
  · assumption


def inst : Magma M := { op := fun a b => op b a }

def Pre (u v : M) : Prop := P1 u v ∨ P2 u v ∨ P3 u v ∨ P4 u v ∨ P5 u v

theorem op_free {u v : M} (h : ¬ Pre u v) : op u v = J u v := by
  rw [op.eq_1]; simp only [Pre, not_or] at h; simp [h]

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 1) (g 0) (g 2)
  revert this
  change ¬ g 1 = op (op (g 0) (op (g 2) (g 0))) (op (op (g 1) (g 1)) (g 0))
  simp (config := {decide := true}) [op.eq_1, sz, P1, P2, P3, P4, P5]


/-- THE LAW: x = ((y * ((x * z) * y)) * x) * y (stated for the DUAL L-form law; the served magma flips op, so EquationLHS unfolds to exactly this) -/
theorem sz_pos (t : M) : 1 ≤ sz t := by cases t <;> simp [sz] <;> omega
theorem sz_J (a b : M) : sz (J a b) = sz a + sz b + 1 := rfl
theorem sz_a1_lt {t : M} (h : tg t = 2) : sz (a1 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a1]; have := sz_pos b; omega
theorem sz_a2_lt {t : M} (h : tg t = 2) : sz (a2 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a2]; have := sz_pos a; omega

theorem Z {c : Prop} [Decidable c] {a b u v : M} (h1 : a = J u v ∨ a = a1 v)
    (h2 : b = J u v ∨ b = a1 v) : (if c then a else b) = J u v ∨ (if c then a else b) = a1 v := by
  by_cases h : c
  · rw [if_pos h]; exact h1
  · rw [if_neg h]; exact h2

theorem Wdig (u v : M) : op u v = J u v ∨ op u v = a1 v := by
  rw [op.eq_1]
  exact Z (Or.inr rfl) (Z (Or.inr rfl) (Z (Or.inr rfl) (Z (Or.inr rfl) (Z (Or.inr rfl) (Or.inl rfl)))))

theorem Pdig {u v : M} (h : Pre u v) : tg v = 2 := by
  rcases h with h|h|h|h|h
  · exact h.1
  · exact h.1
  · exact h
  · exact h.1
  · exact h.1

theorem Wsz (u v : M) : op u v = J u v ∨ (tg v = 2 ∧ op u v = a1 v ∧ sz (op u v) < sz v) := by
  by_cases h : Pre u v
  · rcases Wdig u v with h1 | h1
    · exact Or.inl h1
    · have ht := Pdig h
      exact Or.inr ⟨ht, h1, by rw [h1]; exact sz_a1_lt ht⟩
  · exact Or.inl (op_free h)

theorem NEFREE {u v : M} (h : sz (op u v) < sz v) : op u v ≠ J u v := by
  intro hc; rw [hc] at h; simp only [sz_J] at h; have := sz_pos u; omega

theorem NOSELF {u v : M} (h : op u v = v) : False := by
  rcases Wsz u v with hf | ⟨-, -, hs⟩
  · rw [hf] at h
    have e := congrArg sz h; simp only [sz_J] at e
    have := sz_pos u; omega
  · rw [h] at hs; exact Nat.lt_irrefl _ hs

theorem Y {c : Prop} [Decidable c] {a b u v : M} {Q : Prop} (h1 : c → Q) (h2 : b ≠ J u v → Q) :
    (if c then a else b) ≠ J u v → Q := by
  by_cases h : c
  · intro _; exact h1 h
  · rw [if_neg h]; exact h2

theorem AD1 {u v W : M} (he : a2 v = op W u) :
    (tg (a2 v) = 2 ∧ a2 (a2 v) = u) ∨ a2 v = a1 u := by
  rcases Wdig W u with hf | hf
  · rw [hf] at he; exact Or.inl ⟨by rw [he]; rfl, by rw [he]; rfl⟩
  · exact Or.inr (he.trans hf)

theorem Adig {u v : M} (h : op u v ≠ J u v) :
    (tg (a2 v) = 2 ∧ a2 (a2 v) = u) ∨ a2 v = a1 u := by
  rw [op.eq_1] at h
  revert h
  exact Y
    (fun h => by have e := h.2.2.2.2.1; rw [dif_pos (h.2.1)] at e; exact AD1 e)
    (Y
    (fun h => by have e := h.2.2.2.2.1; rw [dif_pos (h.2.1)] at e; exact AD1 e)
    (Y
    (fun h => by have e := h.2.2.2.2.1; rw [dif_pos (h.2.1)] at e; exact AD1 e)
    (Y
    (fun h => by have e := h.2.2.2.2.1; rw [dif_pos (h.2.1)] at e; exact AD1 e)
    (Y
    (fun h => by have e := h.2.2.2.2.2.2.1; rw [dif_pos (h.2.1)] at e; exact AD1 e)
    ((fun hh => absurd rfl hh))))))

theorem TR {u v : M} (h : op u v ≠ J u v) :
    (P1 u v ∧ a2 v = op (a1 (a2 v)) (u) ∧ a1 (a2 v) = op (u) (a2 (a1 (a2 v))) ∧ a2 (a1 (a2 v)) = op (a1 (a2 (a1 (a2 v)))) (a1 v)) ∨
    (P2 u v ∧ a2 v = op (a1 (a2 v)) (u) ∧ a1 (a2 v) = op (u) (a2 (a1 (a2 v))) ∧ a2 (a1 (a2 v)) = op (a2 (a2 (a1 v))) (a1 v)) ∨
    (P3 u v ∧ a2 v = op (a1 (a2 v)) (u) ∧ J (a1 (a2 v)) (a1 v) = op (a1 (a2 v)) (a1 v) ∧ a1 (a2 v) = op (u) (J (a1 (a2 v)) (a1 v))) ∨
    (P4 u v ∧ a2 v = op (a1 (a2 v)) (u) ∧ a1 (a2 v) = op (u) (a1 (a1 v)) ∧ a1 (a1 v) = op (a2 (a2 (a1 v))) (a1 v)) ∨
    (P5 u v ∧ a2 v = op (a2 (a2 u)) (u) ∧ J (a2 (a2 u)) (a1 v) = op (a2 (a2 u)) (a1 v) ∧ a1 v = op (a1 (a1 v)) (u) ∧ a1 (a1 v) = op (u) (a2 (a1 (a1 v))) ∧ a2 (a1 (a1 v)) = op (a1 (a2 (a1 (a1 v)))) (a2 (a2 u))) := by
  rw [op.eq_1] at h
  revert h
  exact Y
    (fun h => Or.inl (⟨h.1, (by have e := h.2.2.2.2.1; rw [dif_pos (h.2.1)] at e; exact e), (by have e := h.2.2.2.2.2.1; rw [dif_pos (h.2.2.1)] at e; exact e), (by have e := h.2.2.2.2.2.2; rw [dif_pos (h.2.2.2.1)] at e; exact e)⟩))
    (Y
    (fun h => Or.inr (Or.inl (⟨h.1, (by have e := h.2.2.2.2.1; rw [dif_pos (h.2.1)] at e; exact e), (by have e := h.2.2.2.2.2.1; rw [dif_pos (h.2.2.1)] at e; exact e), (by have e := h.2.2.2.2.2.2; rw [dif_pos (h.2.2.2.1)] at e; exact e)⟩)))
    (Y
    (fun h => Or.inr (Or.inr (Or.inl (⟨h.1, (by have e := h.2.2.2.2.1; rw [dif_pos (h.2.1)] at e; exact e), (by have e := h.2.2.2.2.2.1; rw [dif_pos (h.2.2.1)] at e; exact e), (by have e := h.2.2.2.2.2.2; rw [dif_pos (h.2.2.2.1)] at e; exact e)⟩))))
    (Y
    (fun h => Or.inr (Or.inr (Or.inr (Or.inl (⟨h.1, (by have e := h.2.2.2.2.1; rw [dif_pos (h.2.1)] at e; exact e), (by have e := h.2.2.2.2.2.1; rw [dif_pos (h.2.2.1)] at e; exact e), (by have e := h.2.2.2.2.2.2; rw [dif_pos (h.2.2.2.1)] at e; exact e)⟩)))))
    (Y
    (fun h => Or.inr (Or.inr (Or.inr (Or.inr (⟨h.1, (by have e := h.2.2.2.2.2.2.1; rw [dif_pos (h.2.1)] at e; exact e), (by have e := h.2.2.2.2.2.2.2.1; rw [dif_pos (h.2.2.1)] at e; exact e), (by have e := h.2.2.2.2.2.2.2.2.1; rw [dif_pos (h.2.2.2.1)] at e; exact e), (by have e := h.2.2.2.2.2.2.2.2.2.1; rw [dif_pos (h.2.2.2.2.1)] at e; exact e), (by have e := h.2.2.2.2.2.2.2.2.2.2; rw [dif_pos (h.2.2.2.2.2.1)] at e; exact e)⟩)))))
    ((fun hh => absurd rfl hh))))))

theorem Bdig {u v : M} (h : op u v ≠ J u v) : Pre u v := by
  by_cases hp : Pre u v
  · exact hp
  · exact absurd (op_free hp) h

theorem mxl {a b c d : M} (h1 : sz a < sz d) (h2 : sz b < sz d) :
    max (sz a) (sz b) < max (sz c) (sz d) := by
  rw [Nat.max_def, Nat.max_def]; split <;> split <;> omega

theorem GT {A B u v : M} (h1 : sz A < sz v) (h2 : sz B < sz v) : msr A B < msr u v :=
  msr_lt_of_max_lt (mxl h1 h2)

theorem ZP {c : Prop} [Decidable c] {a b r : M} (h1 : a = r) (h2 : b = r) :
    (if c then a else b) = r := by
  by_cases h : c
  · rw [if_pos h]; exact h1
  · rw [if_neg h]; exact h2

theorem cell1 (x y z : M) (ha : op z x = J z x) (hb : op y (J z x) = J y (J z x))
    (hc : op (J y (J z x)) y = J (J y (J z x)) y) :
    op y (J x (J (J y (J z x)) y)) = x := by
  rw [op.eq_1]
  refine (if_pos ⟨⟨rfl, rfl, rfl⟩, ?_, ?_, ?_, ?_, ?_, ?_⟩).trans rfl
  · exact GT (by simp only [a1_J_eq, a2_J_eq, sz_J]; omega) (by simp only [sz_J]; omega)
  · exact GT (by simp only [sz_J]; omega) (by simp only [a1_J_eq, a2_J_eq, sz_J]; omega)
  · exact GT (by simp only [a1_J_eq, a2_J_eq, sz_J]; omega) (by simp only [a1_J_eq, sz_J]; omega)
  · rw [dif_pos (GT (by simp only [a1_J_eq, a2_J_eq, sz_J]; omega) (by simp only [sz_J]; omega))]
    exact hc.symm
  · rw [dif_pos (GT (by simp only [sz_J]; omega) (by simp only [a1_J_eq, a2_J_eq, sz_J]; omega))]
    exact hb.symm
  · rw [dif_pos (GT (by simp only [a1_J_eq, a2_J_eq, sz_J]; omega) (by simp only [a1_J_eq, sz_J]; omega))]
    exact ha.symm

theorem cell3 (x y z : M) (ha : op z x = J z x) (hb : op y (J z x) = z)
    (hc : op z y = J z y) : op y (J x (J z y)) = x := by
  rw [op.eq_1]
  refine ZP rfl (ZP rfl ((if_pos ⟨rfl, ?_, ?_, ?_, ?_, ?_, ?_⟩).trans rfl))
  · exact GT (by simp only [a1_J_eq, a2_J_eq, sz_J]; omega) (by simp only [sz_J]; omega)
  · exact GT (by simp only [a1_J_eq, a2_J_eq, sz_J]; omega) (by simp only [a1_J_eq, sz_J]; omega)
  · exact GT (by simp only [sz_J]; omega) (by simp only [a1_J_eq, a2_J_eq, sz_J]; omega)
  · rw [dif_pos (GT (by simp only [a1_J_eq, a2_J_eq, sz_J]; omega) (by simp only [sz_J]; omega))]
    exact hc.symm
  · rw [dif_pos (GT (by simp only [a1_J_eq, a2_J_eq, sz_J]; omega) (by simp only [a1_J_eq, sz_J]; omega))]
    exact ha.symm
  · rw [dif_pos (GT (by simp only [sz_J]; omega) (by simp only [a1_J_eq, a2_J_eq, sz_J]; omega))]
    exact hb.symm

theorem cell2 (x y z : M) (htx : tg x = 2) (hz : a2 (a2 x) = z) (ha : op z x = a1 x)
    (hb : op y (a1 x) = J y (a1 x)) (hc : op (J y (a1 x)) y = J (J y (a1 x)) y) :
    op y (J x (J (J y (a1 x)) y)) = x := by
  have s1 := sz_a1_lt htx
  rw [op.eq_1]
  refine ZP rfl ((if_pos ⟨⟨rfl, rfl, rfl⟩, ?_, ?_, ?_, ?_, ?_, ?_⟩).trans rfl)
  · exact GT (by simp only [a1_J_eq, a2_J_eq, sz_J]; omega) (by simp only [sz_J]; omega)
  · exact GT (by simp only [sz_J]; omega) (by simp only [a1_J_eq, a2_J_eq, sz_J]; omega)
  · exact GT (by simp only [a1_J_eq, a2_J_eq, sz_J]; have := sz_a2 (a2 x); have := sz_a2 x; omega) (by simp only [a1_J_eq, sz_J]; omega)
  · rw [dif_pos (GT (by simp only [a1_J_eq, a2_J_eq, sz_J]; omega) (by simp only [sz_J]; omega))]
    exact hc.symm
  · rw [dif_pos (GT (by simp only [sz_J]; omega) (by simp only [a1_J_eq, a2_J_eq, sz_J]; omega))]
    exact hb.symm
  · rw [dif_pos (GT (by simp only [a1_J_eq, a2_J_eq, sz_J]; have := sz_a2 (a2 x); have := sz_a2 x; omega) (by simp only [a1_J_eq, sz_J]; omega))]
    simp only [a1_J_eq, a2_J_eq]
    rw [hz]; exact ha.symm

theorem cell4 (x y z : M) (htx : tg x = 2) (hz : a2 (a2 x) = z) (ha : op z x = a1 x)
    (hb : op y (a1 x) = a1 (a1 x)) (hc : op (a1 (a1 x)) y = J (a1 (a1 x)) y) :
    op y (J x (J (a1 (a1 x)) y)) = x := by
  have s1 := sz_a1_lt htx
  have s2 := sz_a1 (a1 x)
  rw [op.eq_1]
  refine ZP rfl (ZP rfl (ZP rfl ((if_pos ⟨⟨rfl, htx⟩, ?_, ?_, ?_, ?_, ?_, ?_⟩).trans rfl)))
  · exact GT (by simp only [a1_J_eq, a2_J_eq, sz_J]; omega) (by simp only [sz_J]; omega)
  · exact GT (by simp only [sz_J]; omega) (by simp only [a1_J_eq, a2_J_eq, sz_J]; omega)
  · exact GT (by simp only [a1_J_eq, a2_J_eq, sz_J]; have := sz_a2 (a2 x); have := sz_a2 x; omega) (by simp only [a1_J_eq, sz_J]; omega)
  · rw [dif_pos (GT (by simp only [a1_J_eq, a2_J_eq, sz_J]; omega) (by simp only [sz_J]; omega))]
    exact hc.symm
  · rw [dif_pos (GT (by simp only [sz_J]; omega) (by simp only [a1_J_eq, a2_J_eq, sz_J]; omega))]
    simp only [a1_J_eq, a2_J_eq]; exact hb.symm
  · rw [dif_pos (GT (by simp only [a1_J_eq, a2_J_eq, sz_J]; have := sz_a2 (a2 x); have := sz_a2 x; omega) (by simp only [a1_J_eq, sz_J]; omega))]
    simp only [a1_J_eq, a2_J_eq]
    rw [hz]; exact ha.symm

theorem cell5 (y z w : M) (hty : tg y = 2) (hy2 : tg (a2 y) = 2) (hz : a2 (a2 y) = z)
    (hdeep : w = op (a1 w) z) (ha : op z (J (J y w) y) = J z (J (J y w) y))
    (hc : op z y = a1 y) : op y (J (J (J y w) y) (a1 y)) = J (J y w) y := by
  have s1 := sz_a1_lt hty
  have s2 := sz_a2_lt hy2
  have s3 := sz_a2 y
  have s4 := sz_a1 w
  have s5 := sz_a2 (a2 y)
  have e3 : op (J y w) y = J (J y w) y := by
    rcases Wdig (J y w) y with q | q
    · exact q
    · exfalso; have := congrArg sz q; simp only [sz_J] at this; have := sz_a1 y; omega
  have e4 : op y w = J y w := by
    rcases Wdig y w with q | q
    · exact q
    · exfalso; have := congrArg sz q; simp only [sz_J] at this; omega
  rw [op.eq_1]
  refine ZP rfl (ZP rfl (ZP rfl (ZP rfl ((if_pos ⟨⟨rfl, hty, hy2, rfl, rfl, rfl, rfl, rfl⟩,
    ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩).trans rfl))))
  · exact GT (by simp only [a1_J_eq, a2_J_eq, sz_J]; omega) (by simp only [sz_J]; omega)
  · exact GT (by simp only [a1_J_eq, a2_J_eq, sz_J]; omega) (by simp only [a1_J_eq, sz_J]; omega)
  · exact GT (by simp only [a1_J_eq, a2_J_eq, sz_J]; omega) (by simp only [sz_J]; omega)
  · exact GT (by simp only [sz_J]; omega) (by simp only [a1_J_eq, a2_J_eq, sz_J]; omega)
  · exact GT (by simp only [a1_J_eq, a2_J_eq, sz_J]; omega)
      (by simp only [a1_J_eq, a2_J_eq, sz_J]; omega)
  · rw [dif_pos (GT (by simp only [a1_J_eq, a2_J_eq, sz_J]; omega) (by simp only [sz_J]; omega))]
    simp only [a1_J_eq, a2_J_eq]; rw [hz]; exact hc.symm
  · rw [dif_pos (GT (by simp only [a1_J_eq, a2_J_eq, sz_J]; omega)
      (by simp only [a1_J_eq, sz_J]; omega))]
    simp only [a1_J_eq, a2_J_eq]; rw [hz]; exact ha.symm
  · rw [dif_pos (GT (by simp only [a1_J_eq, a2_J_eq, sz_J]; omega) (by simp only [sz_J]; omega))]
    simp only [a1_J_eq, a2_J_eq]; exact e3.symm
  · rw [dif_pos (GT (by simp only [sz_J]; omega) (by simp only [a1_J_eq, a2_J_eq, sz_J]; omega))]
    simp only [a1_J_eq, a2_J_eq]; exact e4.symm
  · rw [dif_pos (GT (by simp only [a1_J_eq, a2_J_eq, sz_J]; omega)
      (by simp only [a1_J_eq, a2_J_eq, sz_J]; omega))]
    simp only [a1_J_eq, a2_J_eq]; rw [hz]; exact hdeep

theorem law (x y z : M) : op (y) (op (x) (op (op (y) (op (z) (x))) (y))) = x := by
  rcases Wdig x (op (op y (op z x)) y) with hd | hd
  · rw [hd]
    rcases Wdig y (J x (op (op y (op z x)) y)) with ht | ht
    · exfalso
      have e := congrArg sz ht
      simp only [sz_J] at e
      have := sz_pos y; have := sz_pos (op (op y (op z x)) y); omega
    · rw [ht]; rfl
  · rw [hd]
    sorry


theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
