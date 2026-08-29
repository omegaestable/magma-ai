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

def P1 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a1 (a1 v) ∧ tg (a2 (a1 v)) = 2 ∧ tg (a1 (a2 (a1 v))) = 2 ∧ a2 (a1 (a2 (a1 v))) = a2 (a2 (a1 v)) ∧ a2 (a1 (a2 (a1 v))) = a2 v
instance (u v : M) : Decidable (P1 u v) := by unfold P1; infer_instance
def P2 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a1 (a1 v) ∧ tg (a2 (a1 v)) = 2 ∧ a2 (a2 (a1 v)) = a2 v ∧ tg (a2 (a2 (a1 v))) = 2 ∧ tg (a1 (a2 (a2 (a1 v)))) = 2 ∧ tg (a2 (a1 (a2 (a2 (a1 v))))) = 2 ∧ tg (a1 (a2 (a1 (a2 (a2 (a1 v)))))) = 2
instance (u v : M) : Decidable (P2 u v) := by unfold P2; infer_instance
def P3 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a1 (a1 v) ∧ tg (a2 (a1 v)) = 2 ∧ a2 (a2 (a1 v)) = a2 v ∧ tg (a2 (a2 (a1 v))) = 2 ∧ tg (a1 (a2 (a2 (a1 v)))) = 2 ∧ tg (a2 (a1 (a2 (a2 (a1 v))))) = 2 ∧ a2 (a2 (a1 (a2 (a2 (a1 v))))) = a2 (a2 (a2 (a1 v)))
instance (u v : M) : Decidable (P3 u v) := by unfold P3; infer_instance
def P4 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a1 (a1 v) ∧ tg (a2 (a1 v)) = 2 ∧ a2 (a2 (a1 v)) = a2 v ∧ tg (a2 (a2 (a1 v))) = 2 ∧ tg (a1 (a2 (a2 (a1 v)))) = 2
instance (u v : M) : Decidable (P4 u v) := by unfold P4; infer_instance
def P5 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a1 (a1 v) ∧ tg (a2 (a1 v)) = 2 ∧ a2 (a2 (a1 v)) = a2 v ∧ tg (a2 (a2 (a1 v))) = 2
instance (u v : M) : Decidable (P5 u v) := by unfold P5; infer_instance
def P6 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a1 (a1 v) ∧ tg (a2 (a1 v)) = 2 ∧ a2 (a2 (a1 v)) = a2 v ∧ tg (a2 (a2 (a1 v))) = 2 ∧ tg (a1 (a2 (a2 (a1 v)))) = 2 ∧ tg (a2 (a1 (a2 (a2 (a1 v))))) = 2 ∧ tg (a1 (a2 (a1 (a2 (a2 (a1 v)))))) = 2 ∧ a1 (a2 (a1 v)) = a1 (a1 (a2 (a1 (a2 (a2 (a1 v)))))) ∧ a2 (a1 (a2 (a1 (a2 (a2 (a1 v)))))) = a2 (a2 (a1 (a2 (a2 (a1 v))))) ∧ a2 (a1 (a2 (a1 (a2 (a2 (a1 v)))))) = a2 (a2 (a2 (a1 v)))
instance (u v : M) : Decidable (P6 u v) := by unfold P6; infer_instance
def P7 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a1 (a1 v) ∧ tg (a2 v) = 2 ∧ tg (a1 (a2 v)) = 2 ∧ tg (a2 (a1 (a2 v))) = 2 ∧ tg (a1 (a2 (a1 (a2 v)))) = 2
instance (u v : M) : Decidable (P7 u v) := by unfold P7; infer_instance
def P8 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a1 (a1 v) ∧ tg (a2 v) = 2 ∧ tg (a1 (a2 v)) = 2 ∧ tg (a2 (a1 (a2 v))) = 2 ∧ tg (a1 (a2 (a1 (a2 v)))) = 2 ∧ a2 (a1 v) = a1 (a1 (a2 (a1 (a2 v)))) ∧ a2 (a1 (a2 (a1 (a2 v)))) = a2 (a2 (a1 (a2 v))) ∧ a2 (a1 (a2 (a1 (a2 v)))) = a2 (a2 v) ∧ a2 (a2 (a1 (a2 v))) = a2 (a2 v)
instance (u v : M) : Decidable (P8 u v) := by unfold P8; infer_instance
def P9 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a1 (a1 v) ∧ tg (a2 v) = 2 ∧ tg (a1 (a2 v)) = 2 ∧ tg (a2 (a1 (a2 v))) = 2 ∧ tg (a1 (a2 (a1 (a2 v)))) = 2 ∧ a2 (a1 v) = a1 (a1 (a2 (a1 (a2 v)))) ∧ a2 (a1 (a2 (a1 (a2 v)))) = a2 (a2 (a1 (a2 v))) ∧ a2 (a1 (a2 (a1 (a2 v)))) = a2 (a2 v)
instance (u v : M) : Decidable (P9 u v) := by unfold P9; infer_instance
def P10 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a1 (a1 v) ∧ tg (a2 v) = 2 ∧ tg (a1 (a2 v)) = 2 ∧ tg (a2 (a1 (a2 v))) = 2 ∧ tg (a1 (a2 (a1 (a2 v)))) = 2 ∧ a2 (a1 v) = a1 (a1 (a2 (a1 (a2 v)))) ∧ a2 (a1 (a2 (a1 (a2 v)))) = a2 (a2 (a1 (a2 v))) ∧ a2 (a1 (a2 (a1 (a2 v)))) = a2 (a2 v)
instance (u v : M) : Decidable (P10 u v) := by unfold P10; infer_instance
def P11 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a1 (a1 v) ∧ tg (a2 v) = 2 ∧ tg (a1 (a2 v)) = 2 ∧ tg (a2 (a1 (a2 v))) = 2 ∧ a2 (a2 (a1 (a2 v))) = a2 (a2 v) ∧ tg (a1 (a2 (a1 (a2 v)))) = 2 ∧ a2 (a2 (a1 (a2 v))) = a1 (a1 (a2 (a1 (a2 v)))) ∧ a2 (a1 (a2 (a1 (a2 v)))) = a2 (a2 (a1 (a2 v))) ∧ a2 (a1 (a2 (a1 (a2 v)))) = a2 (a2 v)
instance (u v : M) : Decidable (P11 u v) := by unfold P11; infer_instance
def P12 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a1 (a1 v) ∧ tg (a2 v) = 2 ∧ tg (a1 (a2 v)) = 2 ∧ tg (a2 (a1 (a2 v))) = 2 ∧ a2 (a2 (a1 (a2 v))) = a2 (a2 v) ∧ a2 (a2 (a1 (a2 v))) = a2 (a2 v)
instance (u v : M) : Decidable (P12 u v) := by unfold P12; infer_instance
def P13 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a1 (a1 v) ∧ tg (a2 v) = 2 ∧ tg (a1 (a2 v)) = 2 ∧ tg (a2 (a1 (a2 v))) = 2 ∧ a2 (a2 (a1 (a2 v))) = a2 (a2 v)
instance (u v : M) : Decidable (P13 u v) := by unfold P13; infer_instance
def P14 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a1 (a1 v) ∧ tg (a2 v) = 2 ∧ tg (a1 (a2 v)) = 2 ∧ tg (a2 (a1 (a2 v))) = 2 ∧ a2 (a2 (a1 (a2 v))) = a2 (a2 v)
instance (u v : M) : Decidable (P14 u v) := by unfold P14; infer_instance
def P15 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a1 (a1 v) ∧ tg (a2 v) = 2 ∧ tg (a1 (a2 v)) = 2 ∧ tg (a2 (a1 (a2 v))) = 2 ∧ tg (a1 (a2 (a1 (a2 v)))) = 2 ∧ a2 (a2 v) = a1 (a1 (a2 (a1 (a2 v)))) ∧ a2 (a1 (a2 (a1 (a2 v)))) = a2 (a2 (a1 (a2 v))) ∧ a2 (a1 (a2 (a1 (a2 v)))) = a2 (a2 v)
instance (u v : M) : Decidable (P15 u v) := by unfold P15; infer_instance
def P16 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a1 (a1 v) ∧ tg (a2 v) = 2 ∧ tg (a1 (a2 v)) = 2 ∧ tg (a2 (a1 (a2 v))) = 2 ∧ a2 (a2 (a1 (a2 v))) = a2 (a2 v)
instance (u v : M) : Decidable (P16 u v) := by unfold P16; infer_instance
def P17 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a1 (a1 v) ∧ tg (a2 v) = 2 ∧ tg (a1 (a2 v)) = 2
instance (u v : M) : Decidable (P17 u v) := by unfold P17; infer_instance
def P18 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a1 (a1 v) ∧ tg (a2 v) = 2 ∧ tg (a1 (a2 v)) = 2
instance (u v : M) : Decidable (P18 u v) := by unfold P18; infer_instance
def P19 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a1 (a1 v) ∧ tg (a2 v) = 2 ∧ tg (a1 (a2 v)) = 2 ∧ tg (a2 (a1 (a2 v))) = 2 ∧ tg (a1 (a2 (a1 (a2 v)))) = 2 ∧ a2 (a1 (a2 (a1 (a2 v)))) = a1 (a1 (a2 (a1 (a2 v)))) ∧ a2 (a1 (a2 (a1 (a2 v)))) = a2 (a2 (a1 (a2 v))) ∧ a2 (a1 (a2 (a1 (a2 v)))) = a2 (a2 v)
instance (u v : M) : Decidable (P19 u v) := by unfold P19; infer_instance
def P20 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a1 (a1 v) ∧ tg (a2 v) = 2 ∧ tg (a1 (a2 v)) = 2 ∧ tg (a2 (a1 (a2 v))) = 2 ∧ a2 (a2 (a1 (a2 v))) = a2 (a2 v) ∧ tg (a1 (a2 (a1 (a2 v)))) = 2 ∧ a2 (a2 (a1 (a2 v))) = a1 (a1 (a2 (a1 (a2 v)))) ∧ a2 (a1 (a2 (a1 (a2 v)))) = a2 (a2 (a1 (a2 v))) ∧ a2 (a1 (a2 (a1 (a2 v)))) = a2 (a2 v)
instance (u v : M) : Decidable (P20 u v) := by unfold P20; infer_instance
def P21 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a1 (a1 v) ∧ tg (a2 v) = 2 ∧ tg (a1 (a2 v)) = 2 ∧ tg (a2 (a1 (a2 v))) = 2 ∧ tg (a1 (a2 (a1 (a2 v)))) = 2 ∧ a2 (a2 v) = a1 (a1 (a2 (a1 (a2 v)))) ∧ a2 (a1 (a2 (a1 (a2 v)))) = a2 (a2 (a1 (a2 v))) ∧ a2 (a1 (a2 (a1 (a2 v)))) = a2 (a2 v)
instance (u v : M) : Decidable (P21 u v) := by unfold P21; infer_instance
def P22 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a1 (a1 v) ∧ tg (a2 v) = 2 ∧ tg (a1 (a2 v)) = 2 ∧ tg (a2 (a1 (a2 v))) = 2 ∧ tg (a1 (a2 (a1 (a2 v)))) = 2 ∧ a2 (a2 v) = a1 (a1 (a2 (a1 (a2 v)))) ∧ a2 (a1 (a2 (a1 (a2 v)))) = a2 (a2 (a1 (a2 v))) ∧ a2 (a1 (a2 (a1 (a2 v)))) = a2 (a2 v)
instance (u v : M) : Decidable (P22 u v) := by unfold P22; infer_instance
def P23 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a1 (a1 v) ∧ tg (a2 v) = 2 ∧ tg (a1 (a2 v)) = 2 ∧ tg (a2 (a1 (a2 v))) = 2 ∧ tg (a1 (a2 (a1 (a2 v)))) = 2
instance (u v : M) : Decidable (P23 u v) := by unfold P23; infer_instance
def P24 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ tg (a1 (a2 v)) = 2 ∧ tg (a2 (a1 (a2 v))) = 2 ∧ tg (a1 (a2 (a1 (a2 v)))) = 2
instance (u v : M) : Decidable (P24 u v) := by unfold P24; infer_instance
def op (u v : M) : M :=
  let p1 := if hs1 : msr (a2 (a1 (a2 (a1 (a2 (a2 (a1 v))))))) (a2 (a2 (a1 v))) < msr u v then op (a2 (a1 (a2 (a1 (a2 (a2 (a1 v))))))) (a2 (a2 (a1 v))) else J u v
  let p2 := if hs2 : msr (a1 (a2 (a1 v))) (a2 (a2 (a1 (a2 (a2 (a1 v)))))) < msr u v then op (a1 (a2 (a1 v))) (a2 (a2 (a1 (a2 (a2 (a1 v)))))) else J u v
  let p3 := if hs3 : msr (a2 (a2 (a1 (a2 (a2 (a1 v)))))) (a2 (a2 (a1 v))) < msr u v then op (a2 (a2 (a1 (a2 (a2 (a1 v)))))) (a2 (a2 (a1 v))) else J u v
  let p4 := if hs4 : msr (a1 (a2 (a1 v))) (a2 (a2 (a2 (a1 v)))) < msr u v then op (a1 (a2 (a1 v))) (a2 (a2 (a2 (a1 v)))) else J u v
  let p5 := if hs5 : msr (p4) (a2 (a2 (a2 (a1 v)))) < msr u v then op (p4) (a2 (a2 (a2 (a1 v)))) else J u v
  let p6 := if hs6 : msr (a2 (a2 (a2 (a1 v)))) (a2 (a2 (a1 v))) < msr u v then op (a2 (a2 (a2 (a1 v)))) (a2 (a2 (a1 v))) else J u v
  let p7 := if hs7 : msr (a2 (a1 (a2 (a1 (p5))))) (p5) < msr u v then op (a2 (a1 (a2 (a1 (p5))))) (p5) else J u v
  let p8 := if hs8 : msr (a1 (a1 (a2 (a2 (a1 v))))) (a2 (a2 (a1 v))) < msr u v then op (a1 (a1 (a2 (a2 (a1 v))))) (a2 (a2 (a1 v))) else J u v
  let p9 := if hs9 : msr (a2 (a1 (a2 (a1 (a2 v))))) (a2 v) < msr u v then op (a2 (a1 (a2 (a1 (a2 v))))) (a2 v) else J u v
  let p10 := if hs10 : msr (a2 (a1 (a2 (a1 (a2 v))))) (a2 (a2 (a1 (a2 v)))) < msr u v then op (a2 (a1 (a2 (a1 (a2 v))))) (a2 (a2 (a1 (a2 v)))) else J u v
  let p11 := if hs11 : msr (a2 (a2 (a1 (a2 v)))) (a2 v) < msr u v then op (a2 (a2 (a1 (a2 v)))) (a2 v) else J u v
  let p12 := if hs12 : msr (a2 (a1 (a2 (a1 (a2 v))))) (a2 (a2 v)) < msr u v then op (a2 (a1 (a2 (a1 (a2 v))))) (a2 (a2 v)) else J u v
  let p13 := if hs13 : msr (p12) (a2 (a2 v)) < msr u v then op (p12) (a2 (a2 v)) else J u v
  let p14 := if hs14 : msr (a2 (a2 v)) (a2 v) < msr u v then op (a2 (a2 v)) (a2 v) else J u v
  let p15 := if hs15 : msr (a2 (a1 (a2 (a1 (p13))))) (p13) < msr u v then op (a2 (a1 (a2 (a1 (p13))))) (p13) else J u v
  let p16 := if hs16 : msr (a2 (a1 v)) (a2 (a2 (a1 (a2 v)))) < msr u v then op (a2 (a1 v)) (a2 (a2 (a1 (a2 v)))) else J u v
  let p17 := if hs17 : msr (a2 (a2 (a1 (a2 v)))) (a2 (a2 (a1 (a2 v)))) < msr u v then op (a2 (a2 (a1 (a2 v)))) (a2 (a2 (a1 (a2 v)))) else J u v
  let p18 := if hs18 : msr (a2 (a2 (a1 (a2 v)))) (a2 (a2 v)) < msr u v then op (a2 (a2 (a1 (a2 v)))) (a2 (a2 v)) else J u v
  let p19 := if hs19 : msr (p18) (a2 (a2 v)) < msr u v then op (p18) (a2 (a2 v)) else J u v
  let p20 := if hs20 : msr (a2 (a1 (a2 (a1 (p19))))) (p19) < msr u v then op (a2 (a1 (a2 (a1 (p19))))) (p19) else J u v
  let p21 := if hs21 : msr (a2 (a1 v)) (a2 (a2 v)) < msr u v then op (a2 (a1 v)) (a2 (a2 v)) else J u v
  let p22 := if hs22 : msr (p21) (a2 (a2 v)) < msr u v then op (p21) (a2 (a2 v)) else J u v
  let p23 := if hs23 : msr (a2 (a2 v)) (a2 (a2 (a1 (a2 v)))) < msr u v then op (a2 (a2 v)) (a2 (a2 (a1 (a2 v)))) else J u v
  let p24 := if hs24 : msr (a2 (a2 v)) (a2 (a2 v)) < msr u v then op (a2 (a2 v)) (a2 (a2 v)) else J u v
  let p25 := if hs25 : msr (p24) (a2 (a2 v)) < msr u v then op (p24) (a2 (a2 v)) else J u v
  let p26 := if hs26 : msr (a2 (a1 (a2 (a1 (p25))))) (p25) < msr u v then op (a2 (a1 (a2 (a1 (p25))))) (p25) else J u v
  let p27 := if hs27 : msr (a1 (a1 (a2 v))) (a2 v) < msr u v then op (a1 (a1 (a2 v))) (a2 v) else J u v
  let p28 := if hs28 : msr (a2 (a1 (a2 (a1 (p22))))) (p22) < msr u v then op (a2 (a1 (a2 (a1 (p22))))) (p22) else J u v
  let p29 := if hs29 : msr (p9) (a2 v) < msr u v then op (p9) (a2 v) else J u v
  let p30 := if hs30 : msr (u) (p29) < msr u v then op (u) (p29) else J u v
  if P1 u v then a1 (a1 (a2 (a1 v)))
  else if P2 u v ∧ msr (a2 (a1 (a2 (a1 (a2 (a2 (a1 v))))))) (a2 (a2 (a1 v))) < msr u v ∧ a1 (a2 (a1 v)) = p1 then a2 (a1 (a2 (a1 (a2 (a2 (a1 v))))))
  else if P3 u v ∧ msr (a1 (a2 (a1 v))) (a2 (a2 (a1 (a2 (a2 (a1 v)))))) < msr u v ∧ msr (a2 (a2 (a1 (a2 (a2 (a1 v)))))) (a2 (a2 (a1 v))) < msr u v ∧ a1 (a2 (a1 (a2 (a2 (a1 v))))) = p2 ∧ a1 (a2 (a1 v)) = p3 then a2 (a2 (a1 (a2 (a2 (a1 v)))))
  else if P4 u v ∧ msr (a1 (a2 (a1 v))) (a2 (a2 (a2 (a1 v)))) < msr u v ∧ msr (p4) (a2 (a2 (a2 (a1 v)))) < msr u v ∧ msr (a2 (a2 (a2 (a1 v)))) (a2 (a2 (a1 v))) < msr u v ∧ a2 (a1 (a2 (a2 (a1 v)))) = p5 ∧ a1 (a2 (a1 v)) = p6 then a2 (a2 (a2 (a1 v)))
  else if P5 u v ∧ msr (a1 (a2 (a1 v))) (a2 (a2 (a2 (a1 v)))) < msr u v ∧ msr (p4) (a2 (a2 (a2 (a1 v)))) < msr u v ∧ msr (a2 (a1 (a2 (a1 (p5))))) (p5) < msr u v ∧ msr (a2 (a2 (a2 (a1 v)))) (a2 (a2 (a1 v))) < msr u v ∧ tg (p5) = 2 ∧ tg (a1 (p5)) = 2 ∧ tg (a2 (a1 (p5))) = 2 ∧ tg (a1 (a2 (a1 (p5)))) = 2 ∧ a1 (a2 (a2 (a1 v))) = p7 ∧ a1 (a2 (a1 v)) = p6 then a2 (a2 (a2 (a1 v)))
  else if P6 u v ∧ msr (a1 (a1 (a2 (a2 (a1 v))))) (a2 (a2 (a1 v))) < msr u v ∧ a1 (a2 (a1 v)) = p8 then a1 (a1 (a2 (a2 (a1 v))))
  else if P7 u v ∧ msr (a2 (a1 (a2 (a1 (a2 v))))) (a2 v) < msr u v ∧ a2 (a1 v) = p9 ∧ a2 (a1 (a2 (a1 (a2 v)))) = p9 then a2 (a1 (a2 (a1 (a2 v))))
  else if P8 u v ∧ msr (a2 (a1 (a2 (a1 (a2 v))))) (a2 v) < msr u v ∧ msr (a2 (a1 (a2 (a1 (a2 v))))) (a2 (a2 (a1 (a2 v)))) < msr u v ∧ msr (a2 (a2 (a1 (a2 v)))) (a2 v) < msr u v ∧ a2 (a1 v) = p9 ∧ a1 (a2 (a1 (a2 v))) = p10 ∧ a2 (a1 (a2 (a1 (a2 v)))) = p11 then a2 (a2 (a1 (a2 v)))
  else if P9 u v ∧ msr (a2 (a1 (a2 (a1 (a2 v))))) (a2 v) < msr u v ∧ msr (a2 (a1 (a2 (a1 (a2 v))))) (a2 (a2 v)) < msr u v ∧ msr (p12) (a2 (a2 v)) < msr u v ∧ msr (a2 (a2 v)) (a2 v) < msr u v ∧ a2 (a1 v) = p9 ∧ a2 (a1 (a2 v)) = p13 ∧ a2 (a1 (a2 (a1 (a2 v)))) = p14 then a2 (a2 v)
  else if P10 u v ∧ msr (a2 (a1 (a2 (a1 (a2 v))))) (a2 v) < msr u v ∧ msr (a2 (a1 (a2 (a1 (a2 v))))) (a2 (a2 v)) < msr u v ∧ msr (p12) (a2 (a2 v)) < msr u v ∧ msr (a2 (a1 (a2 (a1 (p13))))) (p13) < msr u v ∧ msr (a2 (a2 v)) (a2 v) < msr u v ∧ a2 (a1 v) = p9 ∧ tg (p13) = 2 ∧ tg (a1 (p13)) = 2 ∧ tg (a2 (a1 (p13))) = 2 ∧ tg (a1 (a2 (a1 (p13)))) = 2 ∧ a1 (a2 v) = p15 ∧ a2 (a1 (a2 (a1 (a2 v)))) = p14 then a2 (a2 v)
  else if P11 u v ∧ msr (a2 (a1 v)) (a2 (a2 (a1 (a2 v)))) < msr u v ∧ msr (a2 (a2 (a1 (a2 v)))) (a2 v) < msr u v ∧ msr (a2 (a1 (a2 (a1 (a2 v))))) (a2 v) < msr u v ∧ a1 (a2 (a1 (a2 v))) = p16 ∧ a2 (a1 v) = p11 ∧ a2 (a2 (a1 (a2 v))) = p9 then a2 (a1 (a2 (a1 (a2 v))))
  else if P12 u v ∧ msr (a2 (a1 v)) (a2 (a2 (a1 (a2 v)))) < msr u v ∧ msr (a2 (a2 (a1 (a2 v)))) (a2 v) < msr u v ∧ msr (a2 (a2 (a1 (a2 v)))) (a2 (a2 (a1 (a2 v)))) < msr u v ∧ a1 (a2 (a1 (a2 v))) = p16 ∧ a2 (a1 v) = p11 ∧ a1 (a2 (a1 (a2 v))) = p17 ∧ a2 (a2 (a1 (a2 v))) = p11 then a2 (a2 (a1 (a2 v)))
  else if P13 u v ∧ msr (a2 (a1 v)) (a2 (a2 (a1 (a2 v)))) < msr u v ∧ msr (a2 (a2 (a1 (a2 v)))) (a2 v) < msr u v ∧ msr (a2 (a2 (a1 (a2 v)))) (a2 (a2 v)) < msr u v ∧ msr (p18) (a2 (a2 v)) < msr u v ∧ msr (a2 (a2 v)) (a2 v) < msr u v ∧ a1 (a2 (a1 (a2 v))) = p16 ∧ a2 (a1 v) = p11 ∧ a2 (a1 (a2 v)) = p19 ∧ a2 (a2 (a1 (a2 v))) = p14 then a2 (a2 v)
  else if P14 u v ∧ msr (a2 (a1 v)) (a2 (a2 (a1 (a2 v)))) < msr u v ∧ msr (a2 (a2 (a1 (a2 v)))) (a2 v) < msr u v ∧ msr (a2 (a2 (a1 (a2 v)))) (a2 (a2 v)) < msr u v ∧ msr (p18) (a2 (a2 v)) < msr u v ∧ msr (a2 (a1 (a2 (a1 (p19))))) (p19) < msr u v ∧ msr (a2 (a2 v)) (a2 v) < msr u v ∧ a1 (a2 (a1 (a2 v))) = p16 ∧ a2 (a1 v) = p11 ∧ tg (p19) = 2 ∧ tg (a1 (p19)) = 2 ∧ tg (a2 (a1 (p19))) = 2 ∧ tg (a1 (a2 (a1 (p19)))) = 2 ∧ a1 (a2 v) = p20 ∧ a2 (a2 (a1 (a2 v))) = p14 then a2 (a2 v)
  else if P15 u v ∧ msr (a2 (a1 v)) (a2 (a2 v)) < msr u v ∧ msr (p21) (a2 (a2 v)) < msr u v ∧ msr (a2 (a2 v)) (a2 v) < msr u v ∧ msr (a2 (a1 (a2 (a1 (a2 v))))) (a2 v) < msr u v ∧ a2 (a1 (a2 v)) = p22 ∧ a2 (a1 v) = p14 ∧ a2 (a2 v) = p9 then a2 (a1 (a2 (a1 (a2 v))))
  else if P16 u v ∧ msr (a2 (a1 v)) (a2 (a2 v)) < msr u v ∧ msr (p21) (a2 (a2 v)) < msr u v ∧ msr (a2 (a2 v)) (a2 v) < msr u v ∧ msr (a2 (a2 v)) (a2 (a2 (a1 (a2 v)))) < msr u v ∧ msr (a2 (a2 (a1 (a2 v)))) (a2 v) < msr u v ∧ a2 (a1 (a2 v)) = p22 ∧ a2 (a1 v) = p14 ∧ a1 (a2 (a1 (a2 v))) = p23 ∧ a2 (a2 v) = p11 then a2 (a2 (a1 (a2 v)))
  else if P17 u v ∧ msr (a2 (a1 v)) (a2 (a2 v)) < msr u v ∧ msr (p21) (a2 (a2 v)) < msr u v ∧ msr (a2 (a2 v)) (a2 v) < msr u v ∧ msr (a2 (a2 v)) (a2 (a2 v)) < msr u v ∧ msr (p24) (a2 (a2 v)) < msr u v ∧ a2 (a1 (a2 v)) = p22 ∧ a2 (a1 v) = p14 ∧ a2 (a1 (a2 v)) = p25 ∧ a2 (a2 v) = p14 then a2 (a2 v)
  else if P18 u v ∧ msr (a2 (a1 v)) (a2 (a2 v)) < msr u v ∧ msr (p21) (a2 (a2 v)) < msr u v ∧ msr (a2 (a2 v)) (a2 v) < msr u v ∧ msr (a2 (a2 v)) (a2 (a2 v)) < msr u v ∧ msr (p24) (a2 (a2 v)) < msr u v ∧ msr (a2 (a1 (a2 (a1 (p25))))) (p25) < msr u v ∧ a2 (a1 (a2 v)) = p22 ∧ a2 (a1 v) = p14 ∧ tg (p25) = 2 ∧ tg (a1 (p25)) = 2 ∧ tg (a2 (a1 (p25))) = 2 ∧ tg (a1 (a2 (a1 (p25)))) = 2 ∧ a1 (a2 v) = p26 ∧ a2 (a2 v) = p14 then a2 (a2 v)
  else if P19 u v ∧ msr (a2 (a1 (a2 (a1 (a2 v))))) (a2 v) < msr u v ∧ msr (a1 (a1 (a2 v))) (a2 v) < msr u v ∧ a2 (a1 v) = p9 ∧ a2 (a1 (a2 (a1 (a2 v)))) = p27 then a1 (a1 (a2 v))
  else if P20 u v ∧ msr (a2 (a1 v)) (a2 (a2 (a1 (a2 v)))) < msr u v ∧ msr (a2 (a2 (a1 (a2 v)))) (a2 v) < msr u v ∧ msr (a1 (a1 (a2 v))) (a2 v) < msr u v ∧ a1 (a2 (a1 (a2 v))) = p16 ∧ a2 (a1 v) = p11 ∧ a2 (a2 (a1 (a2 v))) = p27 then a1 (a1 (a2 v))
  else if P21 u v ∧ msr (a2 (a1 v)) (a2 (a2 v)) < msr u v ∧ msr (p21) (a2 (a2 v)) < msr u v ∧ msr (a2 (a2 v)) (a2 v) < msr u v ∧ msr (a1 (a1 (a2 v))) (a2 v) < msr u v ∧ a2 (a1 (a2 v)) = p22 ∧ a2 (a1 v) = p14 ∧ a2 (a2 v) = p27 then a1 (a1 (a2 v))
  else if P22 u v ∧ msr (a2 (a1 v)) (a2 (a2 v)) < msr u v ∧ msr (p21) (a2 (a2 v)) < msr u v ∧ msr (a2 (a1 (a2 (a1 (p22))))) (p22) < msr u v ∧ msr (a2 (a2 v)) (a2 v) < msr u v ∧ msr (a1 (a1 (a2 v))) (a2 v) < msr u v ∧ tg (p22) = 2 ∧ tg (a1 (p22)) = 2 ∧ tg (a2 (a1 (p22))) = 2 ∧ tg (a1 (a2 (a1 (p22)))) = 2 ∧ a1 (a2 v) = p28 ∧ a2 (a1 v) = p14 ∧ a2 (a2 v) = p27 then a1 (a1 (a2 v))
  else if P23 u v ∧ msr (a2 (a1 (a2 (a1 (a2 v))))) (a2 v) < msr u v ∧ msr (p9) (a2 v) < msr u v ∧ a2 (a1 v) = p29 then a2 (a1 (a2 (a1 (a2 v))))
  else if P24 u v ∧ msr (a2 (a1 (a2 (a1 (a2 v))))) (a2 v) < msr u v ∧ msr (p9) (a2 v) < msr u v ∧ msr (u) (p29) < msr u v ∧ a1 v = p30 then a2 (a1 (a2 (a1 (a2 v))))
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

def Pre (u v : M) : Prop := P1 u v ∨ P2 u v ∨ P3 u v ∨ P4 u v ∨ P5 u v ∨ P6 u v ∨ P7 u v ∨ P8 u v ∨ P9 u v ∨ P10 u v ∨ P11 u v ∨ P12 u v ∨ P13 u v ∨ P14 u v ∨ P15 u v ∨ P16 u v ∨ P17 u v ∨ P18 u v ∨ P19 u v ∨ P20 u v ∨ P21 u v ∨ P22 u v ∨ P23 u v ∨ P24 u v

theorem op_free {u v : M} (h : ¬ Pre u v) : op u v = J u v := by
  rw [op.eq_1]; simp only [Pre, not_or] at h; simp [h]

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 2) (g 0) (g 1)
  revert this
  change ¬ g 2 = op (g 1) (op (g 2) (op (g 2) (op (g 1) (op (g 0) (g 0)))))
  simp (config := {decide := true}) [op.eq_1, sz, P1, P2, P3, P4, P5, P6, P7, P8, P9, P10, P11, P12, P13, P14, P15, P16, P17, P18, P19, P20, P21, P22, P23, P24]


/-- THE LAW: x = (y * ((y * (y * x)) * z)) * z (stated for the DUAL L-form law; the served magma flips op, so EquationLHS unfolds to exactly this) -/
theorem law (x y z : M) : op (z) (op (op (z) (op (op (x) (y)) (y))) (y)) = x := by
  sorry


theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
