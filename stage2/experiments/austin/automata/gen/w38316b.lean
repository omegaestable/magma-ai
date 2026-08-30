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
def P5 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2
instance (u v : M) : Decidable (P5 u v) := by unfold P5; infer_instance
def P6 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2
instance (u v : M) : Decidable (P6 u v) := by unfold P6; infer_instance
def P7 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2
instance (u v : M) : Decidable (P7 u v) := by unfold P7; infer_instance
def P8 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a2 u) = 2 ∧ a2 v = a1 u ∧ tg (a1 v) = 2 ∧ a2 (a1 v) = u ∧ tg (a1 (a1 v)) = 2 ∧ a1 (a1 (a1 v)) = u
instance (u v : M) : Decidable (P8 u v) := by unfold P8; infer_instance
def P9 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a2 u) = 2 ∧ a2 v = a1 u ∧ tg (a1 v) = 2 ∧ a2 (a1 v) = u ∧ tg (a1 (a1 v)) = 2 ∧ a1 (a1 (a1 v)) = u
instance (u v : M) : Decidable (P9 u v) := by unfold P9; infer_instance
def P10 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a2 u) = 2 ∧ a2 v = a1 u ∧ tg (a1 v) = 2 ∧ a2 (a1 v) = u
instance (u v : M) : Decidable (P10 u v) := by unfold P10; infer_instance
def P11 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a2 u) = 2 ∧ a2 v = a1 u ∧ tg (a1 v) = 2 ∧ a2 (a1 v) = u ∧ tg (a2 (a2 u)) = 2
instance (u v : M) : Decidable (P11 u v) := by unfold P11; infer_instance
def P12 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a2 u) = 2 ∧ a2 v = a1 u ∧ tg (a1 v) = 2 ∧ a2 (a1 v) = u ∧ tg (a2 (a2 u)) = 2
instance (u v : M) : Decidable (P12 u v) := by unfold P12; infer_instance
def op (u v : M) : M :=
  let p1 := if hs1 : msr (a1 (a2 v)) (u) < msr u v then op (a1 (a2 v)) (u) else J u v
  let p2 := if hs2 : msr (u) (a2 (a1 (a2 v))) < msr u v then op (u) (a2 (a1 (a2 v))) else J u v
  let p3 := if hs3 : msr (a1 (a2 (a1 (a2 v)))) (a1 v) < msr u v then op (a1 (a2 (a1 (a2 v)))) (a1 v) else J u v
  let p4 := if hs4 : msr (a2 (a2 (a1 v))) (a1 v) < msr u v then op (a2 (a2 (a1 v))) (a1 v) else J u v
  let p5 := if hs5 : msr (a1 (a2 v)) (a1 v) < msr u v then op (a1 (a2 v)) (a1 v) else J u v
  let p6 := if hs6 : msr (u) (J (a1 (a2 v)) (a1 v)) < msr u v then op (u) (J (a1 (a2 v)) (a1 v)) else J u v
  let p7 := if hs7 : msr (u) (a1 (a1 v)) < msr u v then op (u) (a1 (a1 v)) else J u v
  let p8 := if hs8 : msr (a1 (a1 (a1 v))) (a1 v) < msr u v then op (a1 (a1 (a1 v))) (a1 v) else J u v
  let p9 := if hs9 : msr (a2 (a2 u)) (u) < msr u v then op (a2 (a2 u)) (u) else J u v
  let p10 := if hs10 : msr (a2 (a2 u)) (a1 v) < msr u v then op (a2 (a2 u)) (a1 v) else J u v
  let p11 := if hs11 : msr (a1 (a1 v)) (u) < msr u v then op (a1 (a1 v)) (u) else J u v
  let p12 := if hs12 : msr (u) (a2 (a1 (a1 v))) < msr u v then op (u) (a2 (a1 (a1 v))) else J u v
  let p13 := if hs13 : msr (a1 (a2 (a1 (a1 v)))) (a2 (a2 u)) < msr u v then op (a1 (a2 (a1 (a1 v)))) (a2 (a2 u)) else J u v
  let p14 := if hs14 : msr (a2 (a2 (a2 (a2 u)))) (a2 (a2 u)) < msr u v then op (a2 (a2 (a2 (a2 u)))) (a2 (a2 u)) else J u v
  let p15 := if hs15 : msr (a1 (a1 v)) (a2 (a2 u)) < msr u v then op (a1 (a1 v)) (a2 (a2 u)) else J u v
  let p16 := if hs16 : msr (u) (J (a1 (a1 v)) (a2 (a2 u))) < msr u v then op (u) (J (a1 (a1 v)) (a2 (a2 u))) else J u v
  let p17 := if hs17 : msr (u) (a1 (a2 (a2 u))) < msr u v then op (u) (a1 (a2 (a2 u))) else J u v
  let p18 := if hs18 : msr (a1 (a1 (a2 (a2 u)))) (a2 (a2 u)) < msr u v then op (a1 (a1 (a2 (a2 u)))) (a2 (a2 u)) else J u v
  if P1 u v ∧ msr (a1 (a2 v)) (u) < msr u v ∧ msr (u) (a2 (a1 (a2 v))) < msr u v ∧ msr (a1 (a2 (a1 (a2 v)))) (a1 v) < msr u v ∧ a2 v = p1 ∧ a1 (a2 v) = p2 ∧ a2 (a1 (a2 v)) = p3 then a1 v
  else if P2 u v ∧ msr (a1 (a2 v)) (u) < msr u v ∧ msr (u) (a2 (a1 (a2 v))) < msr u v ∧ msr (a2 (a2 (a1 v))) (a1 v) < msr u v ∧ a2 v = p1 ∧ a1 (a2 v) = p2 ∧ a2 (a1 (a2 v)) = p4 then a1 v
  else if P3 u v ∧ msr (a1 (a2 v)) (u) < msr u v ∧ msr (a1 (a2 v)) (a1 v) < msr u v ∧ msr (u) (J (a1 (a2 v)) (a1 v)) < msr u v ∧ a2 v = p1 ∧ J (a1 (a2 v)) (a1 v) = p5 ∧ a1 (a2 v) = p6 then a1 v
  else if P4 u v ∧ msr (a1 (a2 v)) (u) < msr u v ∧ msr (u) (a1 (a1 v)) < msr u v ∧ msr (a1 (a1 (a1 v))) (a1 v) < msr u v ∧ a2 v = p1 ∧ a1 (a2 v) = p7 ∧ a1 (a1 v) = p8 then a1 v
  else if P5 u v ∧ msr (a1 (a2 v)) (u) < msr u v ∧ msr (u) (a1 (a1 v)) < msr u v ∧ msr (a2 (a2 (a1 v))) (a1 v) < msr u v ∧ a2 v = p1 ∧ a1 (a2 v) = p7 ∧ a1 (a1 v) = p4 then a1 v
  else if P6 u v ∧ msr (a2 (a2 u)) (u) < msr u v ∧ msr (u) (a1 (a1 v)) < msr u v ∧ msr (a1 (a1 (a1 v))) (a1 v) < msr u v ∧ a2 v = p9 ∧ a2 (a2 u) = p7 ∧ a1 (a1 v) = p8 then a1 v
  else if P7 u v ∧ msr (a2 (a2 u)) (u) < msr u v ∧ msr (u) (a1 (a1 v)) < msr u v ∧ msr (a2 (a2 (a1 v))) (a1 v) < msr u v ∧ a2 v = p9 ∧ a2 (a2 u) = p7 ∧ a1 (a1 v) = p4 then a1 v
  else if P8 u v ∧ msr (a2 (a2 u)) (u) < msr u v ∧ msr (a2 (a2 u)) (a1 v) < msr u v ∧ msr (a1 (a1 v)) (u) < msr u v ∧ msr (u) (a2 (a1 (a1 v))) < msr u v ∧ msr (a1 (a2 (a1 (a1 v)))) (a2 (a2 u)) < msr u v ∧ a2 v = p9 ∧ J (a2 (a2 u)) (a1 v) = p10 ∧ a1 v = p11 ∧ a1 (a1 v) = p12 ∧ a2 (a1 (a1 v)) = p13 then a1 v
  else if P9 u v ∧ msr (a2 (a2 u)) (u) < msr u v ∧ msr (a2 (a2 u)) (a1 v) < msr u v ∧ msr (a1 (a1 v)) (u) < msr u v ∧ msr (u) (a2 (a1 (a1 v))) < msr u v ∧ msr (a2 (a2 (a2 (a2 u)))) (a2 (a2 u)) < msr u v ∧ a2 v = p9 ∧ J (a2 (a2 u)) (a1 v) = p10 ∧ a1 v = p11 ∧ a1 (a1 v) = p12 ∧ a2 (a1 (a1 v)) = p14 then a1 v
  else if P10 u v ∧ msr (a2 (a2 u)) (u) < msr u v ∧ msr (a2 (a2 u)) (a1 v) < msr u v ∧ msr (a1 (a1 v)) (u) < msr u v ∧ msr (a1 (a1 v)) (a2 (a2 u)) < msr u v ∧ msr (u) (J (a1 (a1 v)) (a2 (a2 u))) < msr u v ∧ a2 v = p9 ∧ J (a2 (a2 u)) (a1 v) = p10 ∧ a1 v = p11 ∧ J (a1 (a1 v)) (a2 (a2 u)) = p15 ∧ a1 (a1 v) = p16 then a1 v
  else if P11 u v ∧ msr (a2 (a2 u)) (u) < msr u v ∧ msr (a2 (a2 u)) (a1 v) < msr u v ∧ msr (a1 (a1 v)) (u) < msr u v ∧ msr (u) (a1 (a2 (a2 u))) < msr u v ∧ msr (a1 (a1 (a2 (a2 u)))) (a2 (a2 u)) < msr u v ∧ a2 v = p9 ∧ J (a2 (a2 u)) (a1 v) = p10 ∧ a1 v = p11 ∧ a1 (a1 v) = p17 ∧ a1 (a2 (a2 u)) = p18 then a1 v
  else if P12 u v ∧ msr (a2 (a2 u)) (u) < msr u v ∧ msr (a2 (a2 u)) (a1 v) < msr u v ∧ msr (a1 (a1 v)) (u) < msr u v ∧ msr (u) (a1 (a2 (a2 u))) < msr u v ∧ msr (a2 (a2 (a2 (a2 u)))) (a2 (a2 u)) < msr u v ∧ a2 v = p9 ∧ J (a2 (a2 u)) (a1 v) = p10 ∧ a1 v = p11 ∧ a1 (a1 v) = p17 ∧ a1 (a2 (a2 u)) = p14 then a1 v
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
  · assumption
  · assumption
  · assumption
  · assumption
  · assumption
  · assumption


def inst : Magma M := { op := fun a b => op b a }

def Pre (u v : M) : Prop := P1 u v ∨ P2 u v ∨ P3 u v ∨ P4 u v ∨ P5 u v ∨ P6 u v ∨ P7 u v ∨ P8 u v ∨ P9 u v ∨ P10 u v ∨ P11 u v ∨ P12 u v

theorem op_free {u v : M} (h : ¬ Pre u v) : op u v = J u v := by
  rw [op.eq_1]; simp only [Pre, not_or] at h; simp [h]

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 0) (g 0) (g 0)
  revert this
  change ¬ g 0 = op (op (g 0) (op (op (g 0) (g 0)) (g 0))) (op (g 0) (g 0))
  simp (config := {decide := true}) [op.eq_1, sz, P1, P2, P3, P4, P5, P6, P7, P8, P9, P10, P11, P12]


/-- THE LAW: x = ((y * ((x * z) * y)) * x) * y (stated for the DUAL L-form law; the served magma flips op, so EquationLHS unfolds to exactly this) -/
theorem sz_pos (t : M) : 1 ≤ sz t := by cases t <;> simp [sz] <;> omega
theorem sz_J (a b : M) : sz (J a b) = sz a + sz b + 1 := rfl
theorem sz_a1_lt {t : M} (h : tg t = 2) : sz (a1 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a1]; have := sz_pos b; omega
theorem sz_a2_lt {t : M} (h : tg t = 2) : sz (a2 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a2]; have := sz_pos a; omega

/-- the `Z` combinator: peel one `if` of the chain without `split` (which dies past ~10 rules) -/
theorem Z {c : Prop} [Decidable c] {a b u v : M} (h1 : a = J u v ∨ a = a1 v)
    (h2 : b = J u v ∨ b = a1 v) : (if c then a else b) = J u v ∨ (if c then a else b) = a1 v := by
  by_cases h : c
  · rw [if_pos h]; exact h1
  · rw [if_neg h]; exact h2

/-- every one of the 12 rules returns `a1 v`; the fallback is `J u v`. No `split`, no `op_cases`. -/
theorem Wdig (u v : M) : op u v = J u v ∨ op u v = a1 v := by
  rw [op.eq_1]
  exact Z (Or.inr rfl) (Z (Or.inr rfl) (Z (Or.inr rfl) (Z (Or.inr rfl) (Z (Or.inr rfl) (Z (Or.inr rfl) (Z (Or.inr rfl) (Z (Or.inr rfl) (Z (Or.inr rfl) (Z (Or.inr rfl) (Z (Or.inr rfl) (Z (Or.inr rfl) (Or.inl rfl))))))))))))

/-- every rule needs `tg v = 2` -/
theorem Pdig {u v : M} (h : Pre u v) : tg v = 2 := by
  rcases h with h|h|h|h|h|h|h|h|h|h|h|h
  · exact h.1
  · exact h.1
  · exact h
  · exact h.1
  · exact h.1
  · exact h.1
  · exact h.1
  · exact h.1
  · exact h.1
  · exact h.1
  · exact h.1
  · exact h.1

/-- the digest: free, or `tg v = 2` and the result is the strictly smaller `a1 v` -/
theorem Wsz (u v : M) : op u v = J u v ∨ (tg v = 2 ∧ op u v = a1 v ∧ sz (op u v) < sz v) := by
  by_cases h : Pre u v
  · rcases Wdig u v with h1 | h1
    · exact Or.inl h1
    · have ht := Pdig h
      exact Or.inr ⟨ht, h1, by rw [h1]; exact sz_a1_lt ht⟩
  · exact Or.inl (op_free h)

/-- a product that shrank below its right argument is not the free product -/
theorem NEFREE {u v : M} (h : sz (op u v) < sz v) : op u v ≠ J u v := by
  intro hc; rw [hc] at h; simp only [sz_J] at h; have := sz_pos u; omega

/-- `op u v` never returns `v` itself -/
theorem NOSELF {u v : M} (h : op u v = v) : False := by
  rcases Wsz u v with hf | ⟨-, -, hs⟩
  · rw [hf] at h
    have e := congrArg sz h; simp only [sz_J] at e
    have := sz_pos u; omega
  · rw [h] at hs; exact Nat.lt_irrefl _ hs

/-- free whenever the right argument cannot supply a strictly smaller `a1 v` -/
theorem Wfree {u v : M} (h : sz v ≤ sz (op u v)) (h2 : op u v ≠ J u v) : False := by
  rcases Wsz u v with hf | ⟨-, -, hs⟩
  · exact h2 hf
  · omega

/-- peel one `if` of the chain on the CONDITION side, again without `split` -/
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

/-- **every** rule needs `op W u = a2 v` for `W = a1 (a2 v)` (rules 1-5) or `W = a2 (a2 u)`
    (rules 6-12); `Wdig` then forces `a2 v` to be either `J W u` or `a1 u`. -/
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
    (fun h => by have e := h.2.2.2.2.1; rw [dif_pos (h.2.1)] at e; exact AD1 e)
    (Y
    (fun h => by have e := h.2.2.2.2.1; rw [dif_pos (h.2.1)] at e; exact AD1 e)
    (Y
    (fun h => by have e := h.2.2.2.2.1; rw [dif_pos (h.2.1)] at e; exact AD1 e)
    (Y
    (fun h => by have e := h.2.2.2.2.2.2.1; rw [dif_pos (h.2.1)] at e; exact AD1 e)
    (Y
    (fun h => by have e := h.2.2.2.2.2.2.1; rw [dif_pos (h.2.1)] at e; exact AD1 e)
    (Y
    (fun h => by have e := h.2.2.2.2.2.2.1; rw [dif_pos (h.2.1)] at e; exact AD1 e)
    (Y
    (fun h => by have e := h.2.2.2.2.2.2.1; rw [dif_pos (h.2.1)] at e; exact AD1 e)
    (Y
    (fun h => by have e := h.2.2.2.2.2.2.1; rw [dif_pos (h.2.1)] at e; exact AD1 e)
    ((fun hh => absurd rfl hh)))))))))))))

theorem mxl {a b c d : M} (h1 : sz a < sz d) (h2 : sz b < sz d) :
    max (sz a) (sz b) < max (sz c) (sz d) := by
  rw [Nat.max_def, Nat.max_def]; split <;> split <;> omega

theorem GT {A B u v : M} (h1 : sz A < sz v) (h2 : sz B < sz v) : msr A B < msr u v :=
  msr_lt_of_max_lt (mxl h1 h2)

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

theorem law (x y z : M) : op (y) (op (x) (op (op (y) (op (z) (x))) (y))) = x := by
  sorry


theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
