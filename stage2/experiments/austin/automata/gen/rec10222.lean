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

def P1 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a2 (a1 v) ∧ tg (a2 v) = 2 ∧ tg (a1 (a2 v)) = 2 ∧ u = a2 (a1 (a2 v)) ∧ u = a2 (a2 v)
instance (u v : M) : Decidable (P1 u v) := by unfold P1; infer_instance
def P2 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a2 (a1 v) ∧ tg (a2 v) = 2 ∧ u = a2 (a2 v) ∧ tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P2 u v) := by unfold P2; infer_instance
def P3 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a2 (a1 v) ∧ tg (a2 v) = 2 ∧ u = a2 (a2 v) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 (a2 v) = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ a2 (a1 u) = a2 (a2 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2
instance (u v : M) : Decidable (P3 u v) := by unfold P3; infer_instance
def P4 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a2 (a1 v) ∧ tg (a2 v) = 2 ∧ u = a2 (a2 v) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 (a2 v) = a1 (a1 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2
instance (u v : M) : Decidable (P4 u v) := by unfold P4; infer_instance
def P5 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a2 (a1 v) ∧ tg (a2 v) = 2 ∧ u = a2 (a2 v) ∧ tg u = 2 ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 (a2 u)) = a2 (a2 u)
instance (u v : M) : Decidable (P5 u v) := by unfold P5; infer_instance
def P6 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a2 (a1 v) ∧ tg (a2 v) = 2 ∧ u = a2 (a2 v) ∧ tg u = 2 ∧ tg (a2 u) = 2 ∧ tg (a2 (a2 u)) = 2 ∧ tg (a1 (a2 (a2 u))) = 2
instance (u v : M) : Decidable (P6 u v) := by unfold P6; infer_instance
def P7 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a2 (a1 v) ∧ tg (a2 v) = 2 ∧ u = a2 (a2 v) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 (a2 v) = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P7 u v) := by unfold P7; infer_instance
def P8 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a2 (a1 v) ∧ tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P8 u v) := by unfold P8; infer_instance
def P9 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a2 (a1 v) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a2 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u) ∧ a2 (a1 u) = a1 (a1 u) ∧ a2 (a1 u) = a2 (a2 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2
instance (u v : M) : Decidable (P9 u v) := by unfold P9; infer_instance
def P10 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a2 (a1 v) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a2 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u) ∧ a2 (a1 u) = a1 (a1 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2
instance (u v : M) : Decidable (P10 u v) := by unfold P10; infer_instance
def P11 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a2 (a1 v) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a2 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u) ∧ a2 (a1 (a2 u)) = a2 (a2 u)
instance (u v : M) : Decidable (P11 u v) := by unfold P11; infer_instance
def P12 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a2 (a1 v) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a2 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u) ∧ tg (a2 (a2 u)) = 2 ∧ tg (a1 (a2 (a2 u))) = 2
instance (u v : M) : Decidable (P12 u v) := by unfold P12; infer_instance
def P13 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a2 (a1 v) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a2 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ a2 (a1 u) = a2 (a2 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ a2 (a1 u) = a1 (a1 u) ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P13 u v) := by unfold P13; infer_instance
def P14 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a2 (a1 v) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a2 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ a2 (a1 u) = a2 (a2 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ a2 (a1 u) = a1 (a1 u) ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P14 u v) := by unfold P14; infer_instance
def P15 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a2 (a1 v) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a2 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ a2 (a1 u) = a2 (a2 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ a2 (a1 u) = a1 (a1 u)
instance (u v : M) : Decidable (P15 u v) := by unfold P15; infer_instance
def P16 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a2 (a1 v) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a2 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ a2 (a1 u) = a2 (a2 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 (a2 u)) = a2 (a2 u)
instance (u v : M) : Decidable (P16 u v) := by unfold P16; infer_instance
def P17 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a2 (a1 v) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a2 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ a2 (a1 u) = a2 (a2 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ tg (a2 (a2 u)) = 2 ∧ tg (a1 (a2 (a2 u))) = 2
instance (u v : M) : Decidable (P17 u v) := by unfold P17; infer_instance
def P18 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a2 (a1 v) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a2 v = a1 (a1 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ a2 (a1 u) = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P18 u v) := by unfold P18; infer_instance
def P19 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a2 (a1 v) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a2 v = a1 (a1 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ a2 (a1 u) = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P19 u v) := by unfold P19; infer_instance
def P20 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a2 (a1 v) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a2 v = a1 (a1 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ a2 (a1 u) = a1 (a1 u)
instance (u v : M) : Decidable (P20 u v) := by unfold P20; infer_instance
def P21 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a2 (a1 v) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a2 v = a1 (a1 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 (a2 u)) = a2 (a2 u)
instance (u v : M) : Decidable (P21 u v) := by unfold P21; infer_instance
def P22 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a2 (a1 v) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a2 v = a1 (a1 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ tg (a2 u) = 2 ∧ tg (a2 (a2 u)) = 2 ∧ tg (a1 (a2 (a2 u))) = 2
instance (u v : M) : Decidable (P22 u v) := by unfold P22; infer_instance
def P23 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a2 (a1 v) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a2 (a1 u) = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P23 u v) := by unfold P23; infer_instance
def P24 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a2 (a1 v) ∧ tg u = 2 ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 (a2 u)) = a2 (a2 u) ∧ tg (a1 u) = 2 ∧ a2 (a1 (a2 u)) = a1 (a1 u) ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P24 u v) := by unfold P24; infer_instance
def P25 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a2 (a1 v) ∧ tg u = 2 ∧ tg (a2 u) = 2 ∧ tg (a2 (a2 u)) = 2 ∧ tg (a1 (a2 (a2 u))) = 2 ∧ tg (a1 u) = 2 ∧ a2 (a2 u) = a1 (a1 u) ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P25 u v) := by unfold P25; infer_instance
def P26 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a2 (a1 v) ∧ tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P26 u v) := by unfold P26; infer_instance
def P27 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ tg (a1 (a2 v)) = 2 ∧ u = a2 (a1 (a2 v)) ∧ u = a2 (a2 v) ∧ tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P27 u v) := by unfold P27; infer_instance
def P28 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ tg (a1 (a2 v)) = 2 ∧ u = a2 (a1 (a2 v)) ∧ u = a2 (a2 v) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ a2 (a1 u) = a2 (a2 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2
instance (u v : M) : Decidable (P28 u v) := by unfold P28; infer_instance
def P29 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ tg (a1 (a2 v)) = 2 ∧ u = a2 (a1 (a2 v)) ∧ u = a2 (a2 v) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2
instance (u v : M) : Decidable (P29 u v) := by unfold P29; infer_instance
def P30 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ tg (a1 (a2 v)) = 2 ∧ u = a2 (a1 (a2 v)) ∧ u = a2 (a2 v) ∧ tg u = 2 ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 (a2 u)) = a2 (a2 u)
instance (u v : M) : Decidable (P30 u v) := by unfold P30; infer_instance
def P31 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ tg (a1 (a2 v)) = 2 ∧ u = a2 (a1 (a2 v)) ∧ u = a2 (a2 v) ∧ tg u = 2 ∧ tg (a2 u) = 2 ∧ tg (a2 (a2 u)) = 2 ∧ tg (a1 (a2 (a2 u))) = 2
instance (u v : M) : Decidable (P31 u v) := by unfold P31; infer_instance
def P32 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a2 (a2 v) ∧ tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P32 u v) := by unfold P32; infer_instance
def P33 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a2 (a2 v) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u) ∧ a1 (a2 v) = a1 (a1 u) ∧ a2 (a1 u) = a2 (a2 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2
instance (u v : M) : Decidable (P33 u v) := by unfold P33; infer_instance
def P34 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a2 (a2 v) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u) ∧ a1 (a2 v) = a1 (a1 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2
instance (u v : M) : Decidable (P34 u v) := by unfold P34; infer_instance
def P35 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a2 (a2 v) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u) ∧ a2 (a1 (a2 u)) = a2 (a2 u)
instance (u v : M) : Decidable (P35 u v) := by unfold P35; infer_instance
def P36 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a2 (a2 v) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u) ∧ tg (a2 (a2 u)) = 2 ∧ tg (a1 (a2 (a2 u))) = 2
instance (u v : M) : Decidable (P36 u v) := by unfold P36; infer_instance
def P37 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a2 (a2 v) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ a2 (a1 u) = a2 (a2 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ a1 (a2 v) = a1 (a1 u) ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P37 u v) := by unfold P37; infer_instance
def P38 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a2 (a2 v) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ a2 (a1 u) = a2 (a2 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ a1 (a2 v) = a1 (a1 u) ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P38 u v) := by unfold P38; infer_instance
def P39 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a2 (a2 v) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ a2 (a1 u) = a2 (a2 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ a1 (a2 v) = a1 (a1 u)
instance (u v : M) : Decidable (P39 u v) := by unfold P39; infer_instance
def P40 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a2 (a2 v) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ a2 (a1 u) = a2 (a2 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 (a2 u)) = a2 (a2 u)
instance (u v : M) : Decidable (P40 u v) := by unfold P40; infer_instance
def P41 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a2 (a2 v) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ a2 (a1 u) = a2 (a2 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ tg (a2 (a2 u)) = 2 ∧ tg (a1 (a2 (a2 u))) = 2
instance (u v : M) : Decidable (P41 u v) := by unfold P41; infer_instance
def P42 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a2 (a2 v) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ a1 (a2 v) = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P42 u v) := by unfold P42; infer_instance
def P43 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a2 (a2 v) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ a1 (a2 v) = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P43 u v) := by unfold P43; infer_instance
def P44 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a2 (a2 v) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ a1 (a2 v) = a1 (a1 u)
instance (u v : M) : Decidable (P44 u v) := by unfold P44; infer_instance
def P45 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a2 (a2 v) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 (a2 u)) = a2 (a2 u)
instance (u v : M) : Decidable (P45 u v) := by unfold P45; infer_instance
def P46 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a2 (a2 v) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ tg (a2 u) = 2 ∧ tg (a2 (a2 u)) = 2 ∧ tg (a1 (a2 (a2 u))) = 2
instance (u v : M) : Decidable (P46 u v) := by unfold P46; infer_instance
def P47 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a2 (a2 v) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 (a2 v) = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P47 u v) := by unfold P47; infer_instance
def P48 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a2 (a2 v) ∧ tg u = 2 ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 (a2 u)) = a2 (a2 u) ∧ tg (a1 u) = 2 ∧ a1 (a2 v) = a1 (a1 u) ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P48 u v) := by unfold P48; infer_instance
def P49 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a2 (a2 v) ∧ tg u = 2 ∧ tg (a2 u) = 2 ∧ tg (a2 (a2 u)) = 2 ∧ tg (a1 (a2 (a2 u))) = 2 ∧ tg (a1 u) = 2 ∧ a1 (a2 v) = a1 (a1 u) ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P49 u v) := by unfold P49; infer_instance
def P50 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P50 u v) := by unfold P50; infer_instance
def P51 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u) ∧ a2 v = a1 (a1 u) ∧ a2 (a1 u) = a2 (a2 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2
instance (u v : M) : Decidable (P51 u v) := by unfold P51; infer_instance
def P52 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u) ∧ a2 v = a1 (a1 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2
instance (u v : M) : Decidable (P52 u v) := by unfold P52; infer_instance
def P53 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u) ∧ a2 (a1 (a2 u)) = a2 (a2 u)
instance (u v : M) : Decidable (P53 u v) := by unfold P53; infer_instance
def P54 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u) ∧ tg (a2 (a2 u)) = 2 ∧ tg (a1 (a2 (a2 u))) = 2
instance (u v : M) : Decidable (P54 u v) := by unfold P54; infer_instance
def P55 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ a2 (a1 u) = a2 (a2 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ a2 v = a1 (a1 u) ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P55 u v) := by unfold P55; infer_instance
def P56 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ a2 (a1 u) = a2 (a2 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ a2 v = a1 (a1 u) ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P56 u v) := by unfold P56; infer_instance
def P57 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ a2 (a1 u) = a2 (a2 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ a2 v = a1 (a1 u)
instance (u v : M) : Decidable (P57 u v) := by unfold P57; infer_instance
def P58 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ a2 (a1 u) = a2 (a2 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 (a2 u)) = a2 (a2 u)
instance (u v : M) : Decidable (P58 u v) := by unfold P58; infer_instance
def P59 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ a2 (a1 u) = a2 (a2 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ tg (a2 (a2 u)) = 2 ∧ tg (a1 (a2 (a2 u))) = 2
instance (u v : M) : Decidable (P59 u v) := by unfold P59; infer_instance
def P60 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ a2 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P60 u v) := by unfold P60; infer_instance
def P61 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ a2 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P61 u v) := by unfold P61; infer_instance
def P62 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ a2 v = a1 (a1 u)
instance (u v : M) : Decidable (P62 u v) := by unfold P62; infer_instance
def P63 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 (a2 u)) = a2 (a2 u)
instance (u v : M) : Decidable (P63 u v) := by unfold P63; infer_instance
def P64 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ tg (a2 u) = 2 ∧ tg (a2 (a2 u)) = 2 ∧ tg (a1 (a2 (a2 u))) = 2
instance (u v : M) : Decidable (P64 u v) := by unfold P64; infer_instance
def P65 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a2 (a1 u) = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P65 u v) := by unfold P65; infer_instance
def P66 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u) ∧ a2 v = a1 (a1 u) ∧ a2 (a1 u) = a2 (a2 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ a2 (a1 u) = a1 (a1 u) ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P66 u v) := by unfold P66; infer_instance
def P67 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u) ∧ a2 v = a1 (a1 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ a2 (a1 u) = a1 (a1 u) ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P67 u v) := by unfold P67; infer_instance
def P68 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u) ∧ a2 (a1 (a2 u)) = a2 (a2 u) ∧ a2 (a1 (a2 u)) = a1 (a1 u) ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P68 u v) := by unfold P68; infer_instance
def P69 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u) ∧ tg (a2 (a2 u)) = 2 ∧ tg (a1 (a2 (a2 u))) = 2 ∧ a2 (a2 u) = a1 (a1 u) ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P69 u v) := by unfold P69; infer_instance
def P70 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ a2 (a1 u) = a2 (a2 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ a2 v = a1 (a1 u) ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u) ∧ a2 (a1 u) = a1 (a1 u) ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P70 u v) := by unfold P70; infer_instance
def P71 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ a2 (a1 u) = a2 (a2 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ a2 v = a1 (a1 u) ∧ a2 (a1 u) = a2 (a2 u) ∧ a2 (a1 u) = a1 (a1 u) ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P71 u v) := by unfold P71; infer_instance
def P72 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ a2 (a1 u) = a2 (a2 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ a2 v = a1 (a1 u) ∧ a2 (a1 u) = a1 (a1 u) ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P72 u v) := by unfold P72; infer_instance
def P73 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ a2 (a1 u) = a2 (a2 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 (a2 u)) = a2 (a2 u) ∧ a2 (a1 (a2 u)) = a1 (a1 u) ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P73 u v) := by unfold P73; infer_instance
def P74 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ a2 (a1 u) = a2 (a2 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ tg (a2 (a2 u)) = 2 ∧ tg (a1 (a2 (a2 u))) = 2 ∧ a2 (a2 u) = a1 (a1 u) ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P74 u v) := by unfold P74; infer_instance
def P75 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ a2 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u) ∧ a2 (a1 u) = a1 (a1 u) ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P75 u v) := by unfold P75; infer_instance
def P76 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ a2 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ a2 (a1 u) = a2 (a2 u) ∧ a2 (a1 u) = a1 (a1 u) ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P76 u v) := by unfold P76; infer_instance
def P77 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ a2 v = a1 (a1 u) ∧ a2 (a1 u) = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P77 u v) := by unfold P77; infer_instance
def P78 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 (a2 u)) = a2 (a2 u) ∧ a2 (a1 (a2 u)) = a1 (a1 u) ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P78 u v) := by unfold P78; infer_instance
def P79 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ tg (a2 u) = 2 ∧ tg (a2 (a2 u)) = 2 ∧ tg (a1 (a2 (a2 u))) = 2 ∧ a2 (a2 u) = a1 (a1 u) ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P79 u v) := by unfold P79; infer_instance
def P80 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P80 u v) := by unfold P80; infer_instance
def P81 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ a2 (a1 u) = a2 (a2 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2
instance (u v : M) : Decidable (P81 u v) := by unfold P81; infer_instance
def P82 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2
instance (u v : M) : Decidable (P82 u v) := by unfold P82; infer_instance
def P83 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 (a2 u)) = a2 (a2 u) ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P83 u v) := by unfold P83; infer_instance
def P84 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a2 u) = 2 ∧ tg (a2 (a2 u)) = 2 ∧ tg (a1 (a2 (a2 u))) = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P84 u v) := by unfold P84; infer_instance
def P85 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ tg (a1 (a2 v)) = 2 ∧ u = a2 (a1 (a2 v)) ∧ u = a2 (a2 v) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P85 u v) := by unfold P85; infer_instance
def P86 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a2 (a2 v) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P86 u v) := by unfold P86; infer_instance
def P87 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a2 (a2 v) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u) ∧ a1 (a2 v) = a1 (a1 u) ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P87 u v) := by unfold P87; infer_instance
def P88 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P88 u v) := by unfold P88; infer_instance
def P89 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u) ∧ a2 v = a1 (a1 u) ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u) ∧ a2 (a1 u) = a1 (a1 u) ∧ a2 (a1 u) = a2 (a2 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2
instance (u v : M) : Decidable (P89 u v) := by unfold P89; infer_instance
def P90 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u) ∧ a2 v = a1 (a1 u) ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u) ∧ a2 (a1 u) = a1 (a1 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2
instance (u v : M) : Decidable (P90 u v) := by unfold P90; infer_instance
def P91 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u) ∧ a2 v = a1 (a1 u) ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u) ∧ a2 (a1 (a2 u)) = a2 (a2 u)
instance (u v : M) : Decidable (P91 u v) := by unfold P91; infer_instance
def P92 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u) ∧ a2 v = a1 (a1 u) ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u) ∧ tg (a2 (a2 u)) = 2 ∧ tg (a1 (a2 (a2 u))) = 2
instance (u v : M) : Decidable (P92 u v) := by unfold P92; infer_instance
def P93 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u) ∧ a2 v = a1 (a1 u) ∧ a2 (a1 u) = a2 (a2 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ a2 (a1 u) = a1 (a1 u) ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P93 u v) := by unfold P93; infer_instance
def P94 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u) ∧ a2 v = a1 (a1 u) ∧ a2 (a1 u) = a2 (a2 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ a2 (a1 u) = a1 (a1 u)
instance (u v : M) : Decidable (P94 u v) := by unfold P94; infer_instance
def P95 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u) ∧ a2 v = a1 (a1 u) ∧ a2 (a1 u) = a2 (a2 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ a2 (a1 (a2 u)) = a2 (a2 u)
instance (u v : M) : Decidable (P95 u v) := by unfold P95; infer_instance
def P96 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u) ∧ a2 v = a1 (a1 u) ∧ a2 (a1 u) = a2 (a2 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ tg (a2 (a2 u)) = 2 ∧ tg (a1 (a2 (a2 u))) = 2
instance (u v : M) : Decidable (P96 u v) := by unfold P96; infer_instance
def P97 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u) ∧ a2 v = a1 (a1 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ a2 (a1 u) = a1 (a1 u) ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P97 u v) := by unfold P97; infer_instance
def P98 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u) ∧ a2 v = a1 (a1 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ a2 (a1 u) = a1 (a1 u)
instance (u v : M) : Decidable (P98 u v) := by unfold P98; infer_instance
def P99 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u) ∧ a2 v = a1 (a1 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ a2 (a1 (a2 u)) = a2 (a2 u)
instance (u v : M) : Decidable (P99 u v) := by unfold P99; infer_instance
def P100 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u) ∧ a2 v = a1 (a1 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ tg (a2 (a2 u)) = 2 ∧ tg (a1 (a2 (a2 u))) = 2
instance (u v : M) : Decidable (P100 u v) := by unfold P100; infer_instance
def P101 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u) ∧ a2 (a1 u) = a1 (a1 u) ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P101 u v) := by unfold P101; infer_instance
def P102 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 v = a1 (a1 u) ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P102 u v) := by unfold P102; infer_instance
def P103 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P103 u v) := by unfold P103; infer_instance
def P104 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P104 u v) := by unfold P104; infer_instance
def P105 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P105 u v) := by unfold P105; infer_instance
def P106 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P106 u v) := by unfold P106; infer_instance
def P107 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P107 u v) := by unfold P107; infer_instance
def P108 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P108 u v) := by unfold P108; infer_instance
def P109 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P109 u v) := by unfold P109; infer_instance
def P110 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2 ∧ a2 (a1 u) = a2 (a2 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2
instance (u v : M) : Decidable (P110 u v) := by unfold P110; infer_instance
def P111 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2
instance (u v : M) : Decidable (P111 u v) := by unfold P111; infer_instance
def P112 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 (a2 u)) = a2 (a2 u)
instance (u v : M) : Decidable (P112 u v) := by unfold P112; infer_instance
def P113 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2 ∧ tg (a2 (a2 u)) = 2 ∧ tg (a1 (a2 (a2 u))) = 2
instance (u v : M) : Decidable (P113 u v) := by unfold P113; infer_instance
def P114 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P114 u v) := by unfold P114; infer_instance
def P115 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2 ∧ a2 (a1 u) = a2 (a2 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2
instance (u v : M) : Decidable (P115 u v) := by unfold P115; infer_instance
def P116 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2
instance (u v : M) : Decidable (P116 u v) := by unfold P116; infer_instance
def P117 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 (a2 u)) = a2 (a2 u)
instance (u v : M) : Decidable (P117 u v) := by unfold P117; infer_instance
def P118 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2 ∧ tg (a2 (a2 u)) = 2 ∧ tg (a1 (a2 (a2 u))) = 2
instance (u v : M) : Decidable (P118 u v) := by unfold P118; infer_instance
def P119 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P119 u v) := by unfold P119; infer_instance
def P120 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2 ∧ a2 (a1 u) = a2 (a2 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2
instance (u v : M) : Decidable (P120 u v) := by unfold P120; infer_instance
def P121 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2
instance (u v : M) : Decidable (P121 u v) := by unfold P121; infer_instance
def P122 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 (a2 u)) = a2 (a2 u)
instance (u v : M) : Decidable (P122 u v) := by unfold P122; infer_instance
def P123 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2 ∧ tg (a2 (a2 u)) = 2 ∧ tg (a1 (a2 (a2 u))) = 2
instance (u v : M) : Decidable (P123 u v) := by unfold P123; infer_instance
def P124 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P124 u v) := by unfold P124; infer_instance
def P125 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2 ∧ a2 (a1 u) = a2 (a2 u) ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2
instance (u v : M) : Decidable (P125 u v) := by unfold P125; infer_instance
def P126 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2
instance (u v : M) : Decidable (P126 u v) := by unfold P126; infer_instance
def P127 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 (a2 u)) = a2 (a2 u)
instance (u v : M) : Decidable (P127 u v) := by unfold P127; infer_instance
def P128 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2 ∧ tg (a2 (a2 u)) = 2 ∧ tg (a1 (a2 (a2 u))) = 2
instance (u v : M) : Decidable (P128 u v) := by unfold P128; infer_instance
def P129 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P129 u v) := by unfold P129; infer_instance
def P130 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P130 u v) := by unfold P130; infer_instance
def P131 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a1 (a2 u)) ∧ a2 (a1 u) = a2 (a2 u)
instance (u v : M) : Decidable (P131 u v) := by unfold P131; infer_instance
def P132 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P132 u v) := by unfold P132; infer_instance
def P133 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P133 u v) := by unfold P133; infer_instance
def op (u v : M) : M :=
  let p1 := if hs1 : msr (a2 (a1 u)) (u) < msr u v then op (a2 (a1 u)) (u) else J u v
  let p2 := if hs2 : msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v then op (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) else J u v
  let p3 := if hs3 : msr (a1 (a2 v)) (a2 (a1 (a2 u))) < msr u v then op (a1 (a2 v)) (a2 (a1 (a2 u))) else J u v
  let p4 := if hs4 : msr (a2 (a1 (a2 u))) (u) < msr u v then op (a2 (a1 (a2 u))) (u) else J u v
  let p5 := if hs5 : msr (a1 (a2 v)) (a2 (a2 u)) < msr u v then op (a1 (a2 v)) (a2 (a2 u)) else J u v
  let p6 := if hs6 : msr (a2 (a1 (a2 (a2 u)))) (a2 (a2 u)) < msr u v then op (a2 (a1 (a2 (a2 u)))) (a2 (a2 u)) else J u v
  let p7 := if hs7 : msr (a2 (a2 u)) (u) < msr u v then op (a2 (a2 u)) (u) else J u v
  let p8 := if hs8 : msr (a2 (a1 u)) (a2 (a1 (a2 u))) < msr u v then op (a2 (a1 u)) (a2 (a1 (a2 u))) else J u v
  let p9 := if hs9 : msr (a2 (a1 u)) (a2 (a2 u)) < msr u v then op (a2 (a1 u)) (a2 (a2 u)) else J u v
  let p10 := if hs10 : msr (a2 v) (a2 (a1 (a2 u))) < msr u v then op (a2 v) (a2 (a1 (a2 u))) else J u v
  let p11 := if hs11 : msr (a2 v) (a2 (a2 u)) < msr u v then op (a2 v) (a2 (a2 u)) else J u v
  let p12 := if hs12 : msr (p1) (u) < msr u v then op (p1) (u) else J u v
  let p13 := if hs13 : msr (a1 v) (a2 (a1 (a2 u))) < msr u v then op (a1 v) (a2 (a1 (a2 u))) else J u v
  let p14 := if hs14 : msr (a1 v) (a2 (a2 u)) < msr u v then op (a1 v) (a2 (a2 u)) else J u v
  let p15 := if hs15 : msr (a2 (a1 (p12))) (p12) < msr u v then op (a2 (a1 (p12))) (p12) else J u v
  let p16 := if hs16 : msr (a2 (a1 (a2 (a1 (p12))))) (a2 (a1 (p12))) < msr u v then op (a2 (a1 (a2 (a1 (p12))))) (a2 (a1 (p12))) else J u v
  let p17 := if hs17 : msr (v) (a2 (a1 (a2 (p12)))) < msr u v then op (v) (a2 (a1 (a2 (p12)))) else J u v
  let p18 := if hs18 : msr (a2 (a1 (a2 (p12)))) (p12) < msr u v then op (a2 (a1 (a2 (p12)))) (p12) else J u v
  let p19 := if hs19 : msr (v) (a2 (a2 (p12))) < msr u v then op (v) (a2 (a2 (p12))) else J u v
  let p20 := if hs20 : msr (a2 (a1 (a2 (a2 (p12))))) (a2 (a2 (p12))) < msr u v then op (a2 (a1 (a2 (a2 (p12))))) (a2 (a2 (p12))) else J u v
  let p21 := if hs21 : msr (a2 (a2 (p12))) (p12) < msr u v then op (a2 (a2 (p12))) (p12) else J u v
  let p22 := if hs22 : msr (a2 (a1 (p12))) (a2 (a1 (a2 u))) < msr u v then op (a2 (a1 (p12))) (a2 (a1 (a2 u))) else J u v
  let p23 := if hs23 : msr (a2 (a1 (p12))) (a2 (a2 u)) < msr u v then op (a2 (a1 (p12))) (a2 (a2 u)) else J u v
  let p24 := if hs24 : msr (v) (u) < msr u v then op (v) (u) else J u v
  let p25 := if hs25 : msr (p24) (u) < msr u v then op (p24) (u) else J u v
  let p26 := if hs26 : msr (p1) (p25) < msr u v then op (p1) (p25) else J u v
  let p27 := if hs27 : msr (p1) (p12) < msr u v then op (p1) (p12) else J u v
  if P1 u v then a1 (a1 v)
  else if P2 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a1 (a2 v) = p1 then a1 (a1 v)
  else if P3 u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a1 (a2 u) = p2 ∧ a1 (a2 v) = p1 then a1 (a1 v)
  else if P4 u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a2 u = p2 ∧ a2 (a1 (a2 (a1 u))) = p2 ∧ a1 (a2 v) = p1 then a1 (a1 v)
  else if P5 u v ∧ msr (a1 (a2 v)) (a2 (a1 (a2 u))) < msr u v ∧ msr (a2 (a1 (a2 u))) (u) < msr u v ∧ a1 u = p3 ∧ a1 (a2 v) = p4 then a1 (a1 v)
  else if P6 u v ∧ msr (a1 (a2 v)) (a2 (a2 u)) < msr u v ∧ msr (a2 (a1 (a2 (a2 u)))) (a2 (a2 u)) < msr u v ∧ msr (a2 (a2 u)) (u) < msr u v ∧ a1 u = p5 ∧ a1 (a2 u) = p6 ∧ a1 (a2 v) = p7 then a1 (a1 v)
  else if P7 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a1 (a2 v) = p1 then a1 (a1 v)
  else if P8 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a2 v = p1 ∧ a2 (a1 u) = p1 then a1 (a1 v)
  else if P9 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ a2 v = p1 ∧ a1 (a2 u) = p2 ∧ a2 (a1 u) = p1 then a1 (a1 v)
  else if P10 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ a2 v = p1 ∧ a2 u = p2 ∧ a2 (a1 (a2 (a1 u))) = p2 ∧ a2 (a1 u) = p1 then a1 (a1 v)
  else if P11 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 u)) (a2 (a1 (a2 u))) < msr u v ∧ msr (a2 (a1 (a2 u))) (u) < msr u v ∧ a2 v = p1 ∧ a1 u = p8 ∧ a2 (a1 u) = p4 then a1 (a1 v)
  else if P12 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 u)) (a2 (a2 u)) < msr u v ∧ msr (a2 (a1 (a2 (a2 u)))) (a2 (a2 u)) < msr u v ∧ msr (a2 (a2 u)) (u) < msr u v ∧ a2 v = p1 ∧ a1 u = p9 ∧ a1 (a2 u) = p6 ∧ a2 (a1 u) = p7 then a1 (a1 v)
  else if P13 u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a1 (a2 u) = p2 ∧ a2 v = p1 ∧ a2 (a1 u) = p1 then a1 (a1 v)
  else if P14 u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a1 (a2 u) = p2 ∧ a2 v = p1 ∧ a1 (a2 u) = p2 ∧ a2 (a1 u) = p1 then a1 (a1 v)
  else if P15 u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a1 (a2 u) = p2 ∧ a2 v = p1 ∧ a2 u = p2 ∧ a2 (a1 (a2 (a1 u))) = p2 ∧ a2 (a1 u) = p1 then a1 (a1 v)
  else if P16 u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 u)) (a2 (a1 (a2 u))) < msr u v ∧ msr (a2 (a1 (a2 u))) (u) < msr u v ∧ a1 (a2 u) = p2 ∧ a2 v = p1 ∧ a1 u = p8 ∧ a2 (a1 u) = p4 then a1 (a1 v)
  else if P17 u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 u)) (a2 (a2 u)) < msr u v ∧ msr (a2 (a1 (a2 (a2 u)))) (a2 (a2 u)) < msr u v ∧ msr (a2 (a2 u)) (u) < msr u v ∧ a1 (a2 u) = p2 ∧ a2 v = p1 ∧ a1 u = p9 ∧ a1 (a2 u) = p6 ∧ a2 (a1 u) = p7 then a1 (a1 v)
  else if P18 u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a2 u = p2 ∧ a2 (a1 (a2 (a1 u))) = p2 ∧ a2 v = p1 ∧ a2 (a1 u) = p1 then a1 (a1 v)
  else if P19 u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a2 u = p2 ∧ a2 (a1 (a2 (a1 u))) = p2 ∧ a2 v = p1 ∧ a1 (a2 u) = p2 ∧ a2 (a1 u) = p1 then a1 (a1 v)
  else if P20 u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a2 u = p2 ∧ a2 (a1 (a2 (a1 u))) = p2 ∧ a2 v = p1 ∧ a2 u = p2 ∧ a2 (a1 (a2 (a1 u))) = p2 ∧ a2 (a1 u) = p1 then a1 (a1 v)
  else if P21 u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 u)) (a2 (a1 (a2 u))) < msr u v ∧ msr (a2 (a1 (a2 u))) (u) < msr u v ∧ a2 u = p2 ∧ a2 (a1 (a2 (a1 u))) = p2 ∧ a2 v = p1 ∧ a1 u = p8 ∧ a2 (a1 u) = p4 then a1 (a1 v)
  else if P22 u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 u)) (a2 (a2 u)) < msr u v ∧ msr (a2 (a1 (a2 (a2 u)))) (a2 (a2 u)) < msr u v ∧ msr (a2 (a2 u)) (u) < msr u v ∧ a2 u = p2 ∧ a2 (a1 (a2 (a1 u))) = p2 ∧ a2 v = p1 ∧ a1 u = p9 ∧ a1 (a2 u) = p6 ∧ a2 (a1 u) = p7 then a1 (a1 v)
  else if P23 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a2 v = p1 ∧ a2 (a1 u) = p1 then a1 (a1 v)
  else if P24 u v ∧ msr (a2 v) (a2 (a1 (a2 u))) < msr u v ∧ msr (a2 (a1 (a2 u))) (u) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a1 u = p10 ∧ a2 v = p4 ∧ a2 (a1 (a2 u)) = p1 then a1 (a1 v)
  else if P25 u v ∧ msr (a2 v) (a2 (a2 u)) < msr u v ∧ msr (a2 (a1 (a2 (a2 u)))) (a2 (a2 u)) < msr u v ∧ msr (a2 (a2 u)) (u) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a1 u = p11 ∧ a1 (a2 u) = p6 ∧ a2 v = p7 ∧ a2 (a2 u) = p1 then a1 (a1 v)
  else if P26 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (p1) (u) < msr u v ∧ a2 v = p12 then a1 (a1 v)
  else if P27 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a1 v = p1 then a2 (a1 u)
  else if P28 u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a1 (a2 u) = p2 ∧ a1 v = p1 then a2 (a1 u)
  else if P29 u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a2 u = p2 ∧ a2 (a1 (a2 (a1 u))) = p2 ∧ a1 v = p1 then a2 (a1 u)
  else if P30 u v ∧ msr (a1 v) (a2 (a1 (a2 u))) < msr u v ∧ msr (a2 (a1 (a2 u))) (u) < msr u v ∧ a1 u = p13 ∧ a1 v = p4 then a2 (a1 (a2 u))
  else if P31 u v ∧ msr (a1 v) (a2 (a2 u)) < msr u v ∧ msr (a2 (a1 (a2 (a2 u)))) (a2 (a2 u)) < msr u v ∧ msr (a2 (a2 u)) (u) < msr u v ∧ a1 u = p14 ∧ a1 (a2 u) = p6 ∧ a1 v = p7 then a2 (a2 u)
  else if P32 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a1 v = p1 ∧ a1 (a2 v) = p1 then a2 (a1 u)
  else if P33 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ a1 v = p1 ∧ a1 (a2 u) = p2 ∧ a1 (a2 v) = p1 then a2 (a1 u)
  else if P34 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ a1 v = p1 ∧ a2 u = p2 ∧ a2 (a1 (a2 (a1 u))) = p2 ∧ a1 (a2 v) = p1 then a2 (a1 u)
  else if P35 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a1 (a2 v)) (a2 (a1 (a2 u))) < msr u v ∧ msr (a2 (a1 (a2 u))) (u) < msr u v ∧ a1 v = p1 ∧ a1 u = p3 ∧ a1 (a2 v) = p4 then a2 (a1 u)
  else if P36 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a1 (a2 v)) (a2 (a2 u)) < msr u v ∧ msr (a2 (a1 (a2 (a2 u)))) (a2 (a2 u)) < msr u v ∧ msr (a2 (a2 u)) (u) < msr u v ∧ a1 v = p1 ∧ a1 u = p5 ∧ a1 (a2 u) = p6 ∧ a1 (a2 v) = p7 then a2 (a1 u)
  else if P37 u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a1 (a2 u) = p2 ∧ a1 v = p1 ∧ a1 (a2 v) = p1 then a2 (a1 u)
  else if P38 u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a1 (a2 u) = p2 ∧ a1 v = p1 ∧ a1 (a2 u) = p2 ∧ a1 (a2 v) = p1 then a2 (a1 u)
  else if P39 u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a1 (a2 u) = p2 ∧ a1 v = p1 ∧ a2 u = p2 ∧ a2 (a1 (a2 (a1 u))) = p2 ∧ a1 (a2 v) = p1 then a2 (a1 u)
  else if P40 u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a1 (a2 v)) (a2 (a1 (a2 u))) < msr u v ∧ msr (a2 (a1 (a2 u))) (u) < msr u v ∧ a1 (a2 u) = p2 ∧ a1 v = p1 ∧ a1 u = p3 ∧ a1 (a2 v) = p4 then a2 (a1 u)
  else if P41 u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a1 (a2 v)) (a2 (a2 u)) < msr u v ∧ msr (a2 (a1 (a2 (a2 u)))) (a2 (a2 u)) < msr u v ∧ msr (a2 (a2 u)) (u) < msr u v ∧ a1 (a2 u) = p2 ∧ a1 v = p1 ∧ a1 u = p5 ∧ a1 (a2 u) = p6 ∧ a1 (a2 v) = p7 then a2 (a1 u)
  else if P42 u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a2 u = p2 ∧ a2 (a1 (a2 (a1 u))) = p2 ∧ a1 v = p1 ∧ a1 (a2 v) = p1 then a2 (a1 u)
  else if P43 u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a2 u = p2 ∧ a2 (a1 (a2 (a1 u))) = p2 ∧ a1 v = p1 ∧ a1 (a2 u) = p2 ∧ a1 (a2 v) = p1 then a2 (a1 u)
  else if P44 u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a2 u = p2 ∧ a2 (a1 (a2 (a1 u))) = p2 ∧ a1 v = p1 ∧ a2 u = p2 ∧ a2 (a1 (a2 (a1 u))) = p2 ∧ a1 (a2 v) = p1 then a2 (a1 u)
  else if P45 u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a1 (a2 v)) (a2 (a1 (a2 u))) < msr u v ∧ msr (a2 (a1 (a2 u))) (u) < msr u v ∧ a2 u = p2 ∧ a2 (a1 (a2 (a1 u))) = p2 ∧ a1 v = p1 ∧ a1 u = p3 ∧ a1 (a2 v) = p4 then a2 (a1 u)
  else if P46 u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a1 (a2 v)) (a2 (a2 u)) < msr u v ∧ msr (a2 (a1 (a2 (a2 u)))) (a2 (a2 u)) < msr u v ∧ msr (a2 (a2 u)) (u) < msr u v ∧ a2 u = p2 ∧ a2 (a1 (a2 (a1 u))) = p2 ∧ a1 v = p1 ∧ a1 u = p5 ∧ a1 (a2 u) = p6 ∧ a1 (a2 v) = p7 then a2 (a1 u)
  else if P47 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a1 v = p1 ∧ a1 (a2 v) = p1 then a2 (a1 u)
  else if P48 u v ∧ msr (a1 v) (a2 (a1 (a2 u))) < msr u v ∧ msr (a2 (a1 (a2 u))) (u) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a1 u = p13 ∧ a1 v = p4 ∧ a1 (a2 v) = p1 then a2 (a1 (a2 u))
  else if P49 u v ∧ msr (a1 v) (a2 (a2 u)) < msr u v ∧ msr (a2 (a1 (a2 (a2 u)))) (a2 (a2 u)) < msr u v ∧ msr (a2 (a2 u)) (u) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a1 u = p14 ∧ a1 (a2 u) = p6 ∧ a1 v = p7 ∧ a1 (a2 v) = p1 then a2 (a2 u)
  else if P50 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a1 v = p1 ∧ a2 v = p1 ∧ a2 (a1 u) = p1 then a2 (a1 u)
  else if P51 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ a1 v = p1 ∧ a1 (a2 u) = p2 ∧ a2 v = p1 ∧ a2 (a1 u) = p1 then a2 (a1 u)
  else if P52 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ a1 v = p1 ∧ a2 u = p2 ∧ a2 (a1 (a2 (a1 u))) = p2 ∧ a2 v = p1 ∧ a2 (a1 u) = p1 then a2 (a1 u)
  else if P53 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 v) (a2 (a1 (a2 u))) < msr u v ∧ msr (a2 (a1 (a2 u))) (u) < msr u v ∧ a1 v = p1 ∧ a1 u = p10 ∧ a2 v = p4 ∧ a2 (a1 (a2 u)) = p1 then a2 (a1 u)
  else if P54 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 v) (a2 (a2 u)) < msr u v ∧ msr (a2 (a1 (a2 (a2 u)))) (a2 (a2 u)) < msr u v ∧ msr (a2 (a2 u)) (u) < msr u v ∧ a1 v = p1 ∧ a1 u = p11 ∧ a1 (a2 u) = p6 ∧ a2 v = p7 ∧ a2 (a2 u) = p1 then a2 (a1 u)
  else if P55 u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a1 (a2 u) = p2 ∧ a1 v = p1 ∧ a2 v = p1 ∧ a2 (a1 u) = p1 then a2 (a1 u)
  else if P56 u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a1 (a2 u) = p2 ∧ a1 v = p1 ∧ a1 (a2 u) = p2 ∧ a2 v = p1 ∧ a2 (a1 u) = p1 then a2 (a1 u)
  else if P57 u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a1 (a2 u) = p2 ∧ a1 v = p1 ∧ a2 u = p2 ∧ a2 (a1 (a2 (a1 u))) = p2 ∧ a2 v = p1 ∧ a2 (a1 u) = p1 then a2 (a1 u)
  else if P58 u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 v) (a2 (a1 (a2 u))) < msr u v ∧ msr (a2 (a1 (a2 u))) (u) < msr u v ∧ a1 (a2 u) = p2 ∧ a1 v = p1 ∧ a1 u = p10 ∧ a2 v = p4 ∧ a2 (a1 (a2 u)) = p1 then a2 (a1 u)
  else if P59 u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 v) (a2 (a2 u)) < msr u v ∧ msr (a2 (a1 (a2 (a2 u)))) (a2 (a2 u)) < msr u v ∧ msr (a2 (a2 u)) (u) < msr u v ∧ a1 (a2 u) = p2 ∧ a1 v = p1 ∧ a1 u = p11 ∧ a1 (a2 u) = p6 ∧ a2 v = p7 ∧ a2 (a2 u) = p1 then a2 (a1 u)
  else if P60 u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a2 u = p2 ∧ a2 (a1 (a2 (a1 u))) = p2 ∧ a1 v = p1 ∧ a2 v = p1 ∧ a2 (a1 u) = p1 then a2 (a1 u)
  else if P61 u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a2 u = p2 ∧ a2 (a1 (a2 (a1 u))) = p2 ∧ a1 v = p1 ∧ a1 (a2 u) = p2 ∧ a2 v = p1 ∧ a2 (a1 u) = p1 then a2 (a1 u)
  else if P62 u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a2 u = p2 ∧ a2 (a1 (a2 (a1 u))) = p2 ∧ a1 v = p1 ∧ a2 u = p2 ∧ a2 (a1 (a2 (a1 u))) = p2 ∧ a2 v = p1 ∧ a2 (a1 u) = p1 then a2 (a1 u)
  else if P63 u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 v) (a2 (a1 (a2 u))) < msr u v ∧ msr (a2 (a1 (a2 u))) (u) < msr u v ∧ a2 u = p2 ∧ a2 (a1 (a2 (a1 u))) = p2 ∧ a1 v = p1 ∧ a1 u = p10 ∧ a2 v = p4 ∧ a2 (a1 (a2 u)) = p1 then a2 (a1 u)
  else if P64 u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 v) (a2 (a2 u)) < msr u v ∧ msr (a2 (a1 (a2 (a2 u)))) (a2 (a2 u)) < msr u v ∧ msr (a2 (a2 u)) (u) < msr u v ∧ a2 u = p2 ∧ a2 (a1 (a2 (a1 u))) = p2 ∧ a1 v = p1 ∧ a1 u = p11 ∧ a1 (a2 u) = p6 ∧ a2 v = p7 ∧ a2 (a2 u) = p1 then a2 (a1 u)
  else if P65 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a1 v = p1 ∧ a2 v = p1 ∧ a2 (a1 u) = p1 then a2 (a1 u)
  else if P66 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ a1 v = p1 ∧ a1 (a2 u) = p2 ∧ a2 v = p1 ∧ a2 (a1 u) = p1 then a2 (a1 u)
  else if P67 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ a1 v = p1 ∧ a2 u = p2 ∧ a2 (a1 (a2 (a1 u))) = p2 ∧ a2 v = p1 ∧ a2 (a1 u) = p1 then a2 (a1 u)
  else if P68 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 v) (a2 (a1 (a2 u))) < msr u v ∧ msr (a2 (a1 (a2 u))) (u) < msr u v ∧ a1 v = p1 ∧ a1 u = p10 ∧ a2 v = p4 ∧ a2 (a1 (a2 u)) = p1 then a2 (a1 u)
  else if P69 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 v) (a2 (a2 u)) < msr u v ∧ msr (a2 (a1 (a2 (a2 u)))) (a2 (a2 u)) < msr u v ∧ msr (a2 (a2 u)) (u) < msr u v ∧ a1 v = p1 ∧ a1 u = p11 ∧ a1 (a2 u) = p6 ∧ a2 v = p7 ∧ a2 (a2 u) = p1 then a2 (a1 u)
  else if P70 u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a1 (a2 u) = p2 ∧ a1 v = p1 ∧ a2 v = p1 ∧ a2 (a1 u) = p1 then a2 (a1 u)
  else if P71 u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a1 (a2 u) = p2 ∧ a1 v = p1 ∧ a1 (a2 u) = p2 ∧ a2 v = p1 ∧ a2 (a1 u) = p1 then a2 (a1 u)
  else if P72 u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a1 (a2 u) = p2 ∧ a1 v = p1 ∧ a2 u = p2 ∧ a2 (a1 (a2 (a1 u))) = p2 ∧ a2 v = p1 ∧ a2 (a1 u) = p1 then a2 (a1 u)
  else if P73 u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 v) (a2 (a1 (a2 u))) < msr u v ∧ msr (a2 (a1 (a2 u))) (u) < msr u v ∧ a1 (a2 u) = p2 ∧ a1 v = p1 ∧ a1 u = p10 ∧ a2 v = p4 ∧ a2 (a1 (a2 u)) = p1 then a2 (a1 u)
  else if P74 u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 v) (a2 (a2 u)) < msr u v ∧ msr (a2 (a1 (a2 (a2 u)))) (a2 (a2 u)) < msr u v ∧ msr (a2 (a2 u)) (u) < msr u v ∧ a1 (a2 u) = p2 ∧ a1 v = p1 ∧ a1 u = p11 ∧ a1 (a2 u) = p6 ∧ a2 v = p7 ∧ a2 (a2 u) = p1 then a2 (a1 u)
  else if P75 u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a2 u = p2 ∧ a2 (a1 (a2 (a1 u))) = p2 ∧ a1 v = p1 ∧ a2 v = p1 ∧ a2 (a1 u) = p1 then a2 (a1 u)
  else if P76 u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a2 u = p2 ∧ a2 (a1 (a2 (a1 u))) = p2 ∧ a1 v = p1 ∧ a1 (a2 u) = p2 ∧ a2 v = p1 ∧ a2 (a1 u) = p1 then a2 (a1 u)
  else if P77 u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a2 u = p2 ∧ a2 (a1 (a2 (a1 u))) = p2 ∧ a1 v = p1 ∧ a2 u = p2 ∧ a2 (a1 (a2 (a1 u))) = p2 ∧ a2 v = p1 ∧ a2 (a1 u) = p1 then a2 (a1 u)
  else if P78 u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 v) (a2 (a1 (a2 u))) < msr u v ∧ msr (a2 (a1 (a2 u))) (u) < msr u v ∧ a2 u = p2 ∧ a2 (a1 (a2 (a1 u))) = p2 ∧ a1 v = p1 ∧ a1 u = p10 ∧ a2 v = p4 ∧ a2 (a1 (a2 u)) = p1 then a2 (a1 u)
  else if P79 u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 v) (a2 (a2 u)) < msr u v ∧ msr (a2 (a1 (a2 (a2 u)))) (a2 (a2 u)) < msr u v ∧ msr (a2 (a2 u)) (u) < msr u v ∧ a2 u = p2 ∧ a2 (a1 (a2 (a1 u))) = p2 ∧ a1 v = p1 ∧ a1 u = p11 ∧ a1 (a2 u) = p6 ∧ a2 v = p7 ∧ a2 (a2 u) = p1 then a2 (a1 u)
  else if P80 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (p1) (u) < msr u v ∧ a1 v = p1 ∧ a2 v = p12 then a2 (a1 u)
  else if P81 u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (p1) (u) < msr u v ∧ a1 (a2 u) = p2 ∧ a1 v = p1 ∧ a2 v = p12 then a2 (a1 u)
  else if P82 u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (p1) (u) < msr u v ∧ a2 u = p2 ∧ a2 (a1 (a2 (a1 u))) = p2 ∧ a1 v = p1 ∧ a2 v = p12 then a2 (a1 u)
  else if P83 u v ∧ msr (a1 v) (a2 (a1 (a2 u))) < msr u v ∧ msr (a2 (a1 (a2 u))) (u) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (p1) (u) < msr u v ∧ a1 u = p13 ∧ a1 v = p4 ∧ a2 v = p12 then a2 (a1 (a2 u))
  else if P84 u v ∧ msr (a1 v) (a2 (a2 u)) < msr u v ∧ msr (a2 (a1 (a2 (a2 u)))) (a2 (a2 u)) < msr u v ∧ msr (a2 (a2 u)) (u) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (p1) (u) < msr u v ∧ a1 u = p14 ∧ a1 (a2 u) = p6 ∧ a1 v = p7 ∧ a2 v = p12 then a2 (a2 u)
  else if P85 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a1 v = p1 then a2 (a1 u)
  else if P86 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a1 v = p1 ∧ a1 (a2 v) = p1 then a2 (a1 u)
  else if P87 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a1 v = p1 ∧ a1 (a2 v) = p1 then a2 (a1 u)
  else if P88 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a1 v = p1 ∧ a2 v = p1 ∧ a2 (a1 u) = p1 then a2 (a1 u)
  else if P89 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ a1 v = p1 ∧ a2 v = p1 ∧ a1 (a2 u) = p2 ∧ a2 (a1 u) = p1 then a2 (a1 u)
  else if P90 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ a1 v = p1 ∧ a2 v = p1 ∧ a2 u = p2 ∧ a2 (a1 (a2 (a1 u))) = p2 ∧ a2 (a1 u) = p1 then a2 (a1 u)
  else if P91 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 u)) (a2 (a1 (a2 u))) < msr u v ∧ msr (a2 (a1 (a2 u))) (u) < msr u v ∧ a1 v = p1 ∧ a2 v = p1 ∧ a1 u = p8 ∧ a2 (a1 u) = p4 then a2 (a1 u)
  else if P92 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 u)) (a2 (a2 u)) < msr u v ∧ msr (a2 (a1 (a2 (a2 u)))) (a2 (a2 u)) < msr u v ∧ msr (a2 (a2 u)) (u) < msr u v ∧ a1 v = p1 ∧ a2 v = p1 ∧ a1 u = p9 ∧ a1 (a2 u) = p6 ∧ a2 (a1 u) = p7 then a2 (a1 u)
  else if P93 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ a1 v = p1 ∧ a1 (a2 u) = p2 ∧ a2 v = p1 ∧ a1 (a2 u) = p2 ∧ a2 (a1 u) = p1 then a2 (a1 u)
  else if P94 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ a1 v = p1 ∧ a1 (a2 u) = p2 ∧ a2 v = p1 ∧ a2 u = p2 ∧ a2 (a1 (a2 (a1 u))) = p2 ∧ a2 (a1 u) = p1 then a2 (a1 u)
  else if P95 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (a2 (a1 (a2 u))) < msr u v ∧ msr (a2 (a1 (a2 u))) (u) < msr u v ∧ a1 v = p1 ∧ a1 (a2 u) = p2 ∧ a2 v = p1 ∧ a1 u = p8 ∧ a2 (a1 u) = p4 then a2 (a1 u)
  else if P96 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (a2 (a2 u)) < msr u v ∧ msr (a2 (a1 (a2 (a2 u)))) (a2 (a2 u)) < msr u v ∧ msr (a2 (a2 u)) (u) < msr u v ∧ a1 v = p1 ∧ a1 (a2 u) = p2 ∧ a2 v = p1 ∧ a1 u = p9 ∧ a1 (a2 u) = p6 ∧ a2 (a1 u) = p7 then a2 (a1 u)
  else if P97 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ a1 v = p1 ∧ a2 u = p2 ∧ a2 (a1 (a2 (a1 u))) = p2 ∧ a2 v = p1 ∧ a1 (a2 u) = p2 ∧ a2 (a1 u) = p1 then a2 (a1 u)
  else if P98 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ a1 v = p1 ∧ a2 u = p2 ∧ a2 (a1 (a2 (a1 u))) = p2 ∧ a2 v = p1 ∧ a2 u = p2 ∧ a2 (a1 (a2 (a1 u))) = p2 ∧ a2 (a1 u) = p1 then a2 (a1 u)
  else if P99 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (a2 (a1 (a2 u))) < msr u v ∧ msr (a2 (a1 (a2 u))) (u) < msr u v ∧ a1 v = p1 ∧ a2 u = p2 ∧ a2 (a1 (a2 (a1 u))) = p2 ∧ a2 v = p1 ∧ a1 u = p8 ∧ a2 (a1 u) = p4 then a2 (a1 u)
  else if P100 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (a2 (a2 u)) < msr u v ∧ msr (a2 (a1 (a2 (a2 u)))) (a2 (a2 u)) < msr u v ∧ msr (a2 (a2 u)) (u) < msr u v ∧ a1 v = p1 ∧ a2 u = p2 ∧ a2 (a1 (a2 (a1 u))) = p2 ∧ a2 v = p1 ∧ a1 u = p9 ∧ a1 (a2 u) = p6 ∧ a2 (a1 u) = p7 then a2 (a1 u)
  else if P101 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a1 v = p1 ∧ a2 v = p1 ∧ a2 (a1 u) = p1 then a2 (a1 u)
  else if P102 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (p1) (u) < msr u v ∧ a1 v = p1 ∧ a2 v = p12 then a2 (a1 u)
  else if P103 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (p1) (u) < msr u v ∧ msr (a2 (a1 (p12))) (p12) < msr u v ∧ tg (p12) = 2 ∧ tg (a1 (p12)) = 2 ∧ v = p15 ∧ tg (a2 (a1 (p12))) = 2 ∧ u = a2 (a2 (a1 (p12))) then a1 (a2 (a1 (p12)))
  else if P104 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (p1) (u) < msr u v ∧ msr (a2 (a1 (a2 (a1 (p12))))) (a2 (a1 (p12))) < msr u v ∧ msr (a2 (a1 (p12))) (p12) < msr u v ∧ tg (p12) = 2 ∧ tg (a1 (p12)) = 2 ∧ v = a1 (a1 (p12)) ∧ tg (a2 (p12)) = 2 ∧ a2 (a1 (p12)) = a2 (a2 (p12)) ∧ tg (a2 (a1 (p12))) = 2 ∧ tg (a1 (a2 (a1 (p12)))) = 2 ∧ a1 (a2 (p12)) = p16 ∧ v = p15 ∧ u = a2 (a2 (a1 (p12))) then a1 (a2 (a1 (p12)))
  else if P105 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (p1) (u) < msr u v ∧ msr (a2 (a1 (a2 (a1 (p12))))) (a2 (a1 (p12))) < msr u v ∧ msr (a2 (a1 (p12))) (p12) < msr u v ∧ tg (p12) = 2 ∧ tg (a1 (p12)) = 2 ∧ v = a1 (a1 (p12)) ∧ tg (a2 (a1 (p12))) = 2 ∧ tg (a1 (a2 (a1 (p12)))) = 2 ∧ a2 (p12) = p16 ∧ tg (a2 (a1 (a2 (a1 (p12))))) = 2 ∧ a2 (a1 (p12)) = a2 (a2 (a1 (a2 (a1 (p12))))) ∧ v = p15 ∧ u = a2 (a2 (a1 (p12))) then a1 (a2 (a1 (p12)))
  else if P106 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (p1) (u) < msr u v ∧ msr (a2 (a1 (a2 (a1 (p12))))) (a2 (a1 (p12))) < msr u v ∧ msr (a2 (a1 (p12))) (p12) < msr u v ∧ tg (p12) = 2 ∧ tg (a1 (p12)) = 2 ∧ v = a1 (a1 (p12)) ∧ tg (a2 (a1 (p12))) = 2 ∧ tg (a1 (a2 (a1 (p12)))) = 2 ∧ a2 (p12) = p16 ∧ a2 (a1 (a2 (a1 (p12)))) = p16 ∧ v = p15 ∧ u = a2 (a2 (a1 (p12))) then a1 (a2 (a1 (p12)))
  else if P107 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (p1) (u) < msr u v ∧ msr (v) (a2 (a1 (a2 (p12)))) < msr u v ∧ msr (a2 (a1 (a2 (p12)))) (p12) < msr u v ∧ tg (p12) = 2 ∧ tg (a2 (p12)) = 2 ∧ tg (a1 (a2 (p12))) = 2 ∧ a2 (a1 (a2 (p12))) = a2 (a2 (p12)) ∧ a1 (p12) = p17 ∧ v = p18 ∧ tg (a2 (a1 (a2 (p12)))) = 2 ∧ u = a2 (a2 (a1 (a2 (p12)))) then a1 (a2 (a1 (a2 (p12))))
  else if P108 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (p1) (u) < msr u v ∧ msr (v) (a2 (a2 (p12))) < msr u v ∧ msr (a2 (a1 (a2 (a2 (p12))))) (a2 (a2 (p12))) < msr u v ∧ msr (a2 (a2 (p12))) (p12) < msr u v ∧ tg (p12) = 2 ∧ tg (a2 (p12)) = 2 ∧ a1 (p12) = p19 ∧ tg (a2 (a2 (p12))) = 2 ∧ tg (a1 (a2 (a2 (p12)))) = 2 ∧ a1 (a2 (p12)) = p20 ∧ v = p21 ∧ u = a2 (a2 (a2 (p12))) then a1 (a2 (a2 (p12)))
  else if P109 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (p1) (u) < msr u v ∧ msr (a2 (a1 (p12))) (p12) < msr u v ∧ tg (p12) = 2 ∧ tg (a1 (p12)) = 2 ∧ v = p15 ∧ a2 (a1 (p12)) = p1 then a2 (a1 u)
  else if P110 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (p1) (u) < msr u v ∧ msr (a2 (a1 (p12))) (p12) < msr u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ tg (p12) = 2 ∧ tg (a1 (p12)) = 2 ∧ v = a1 (a1 (p12)) ∧ tg (a2 (p12)) = 2 ∧ tg (a1 (a2 (p12))) = 2 ∧ a2 (a1 (p12)) = a2 (a1 (a2 (p12))) ∧ a2 (a1 (p12)) = a2 (a2 (p12)) ∧ v = p15 ∧ a2 (a1 (p12)) = a1 (a1 u) ∧ a1 (a2 u) = p2 ∧ a2 (a1 (p12)) = p1 then a2 (a1 u)
  else if P111 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (p1) (u) < msr u v ∧ msr (a2 (a1 (p12))) (p12) < msr u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ tg (p12) = 2 ∧ tg (a1 (p12)) = 2 ∧ v = a1 (a1 (p12)) ∧ tg (a2 (p12)) = 2 ∧ tg (a1 (a2 (p12))) = 2 ∧ a2 (a1 (p12)) = a2 (a1 (a2 (p12))) ∧ a2 (a1 (p12)) = a2 (a2 (p12)) ∧ v = p15 ∧ a2 (a1 (p12)) = a1 (a1 u) ∧ a2 u = p2 ∧ a2 (a1 (a2 (a1 u))) = p2 ∧ a2 (a1 (p12)) = p1 then a2 (a1 u)
  else if P112 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (p1) (u) < msr u v ∧ msr (a2 (a1 (p12))) (p12) < msr u v ∧ msr (a2 (a1 (p12))) (a2 (a1 (a2 u))) < msr u v ∧ msr (a2 (a1 (a2 u))) (u) < msr u v ∧ tg (p12) = 2 ∧ tg (a1 (p12)) = 2 ∧ v = a1 (a1 (p12)) ∧ tg (a2 (p12)) = 2 ∧ tg (a1 (a2 (p12))) = 2 ∧ a2 (a1 (p12)) = a2 (a1 (a2 (p12))) ∧ a2 (a1 (p12)) = a2 (a2 (p12)) ∧ v = p15 ∧ a1 u = p22 ∧ a2 (a1 (p12)) = p4 then a2 (a1 (a2 u))
  else if P113 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (p1) (u) < msr u v ∧ msr (a2 (a1 (p12))) (p12) < msr u v ∧ msr (a2 (a1 (p12))) (a2 (a2 u)) < msr u v ∧ msr (a2 (a1 (a2 (a2 u)))) (a2 (a2 u)) < msr u v ∧ msr (a2 (a2 u)) (u) < msr u v ∧ tg (p12) = 2 ∧ tg (a1 (p12)) = 2 ∧ v = a1 (a1 (p12)) ∧ tg (a2 (p12)) = 2 ∧ tg (a1 (a2 (p12))) = 2 ∧ a2 (a1 (p12)) = a2 (a1 (a2 (p12))) ∧ a2 (a1 (p12)) = a2 (a2 (p12)) ∧ v = p15 ∧ a1 u = p23 ∧ a1 (a2 u) = p6 ∧ a2 (a1 (p12)) = p7 then a2 (a2 u)
  else if P114 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (p1) (u) < msr u v ∧ msr (a2 (a1 (a2 (a1 (p12))))) (a2 (a1 (p12))) < msr u v ∧ msr (a2 (a1 (p12))) (p12) < msr u v ∧ tg (p12) = 2 ∧ tg (a1 (p12)) = 2 ∧ v = a1 (a1 (p12)) ∧ tg (a2 (p12)) = 2 ∧ a2 (a1 (p12)) = a2 (a2 (p12)) ∧ tg (a2 (a1 (p12))) = 2 ∧ tg (a1 (a2 (a1 (p12)))) = 2 ∧ a1 (a2 (p12)) = p16 ∧ v = p15 ∧ a2 (a1 (p12)) = a1 (a1 u) ∧ a2 (a1 (p12)) = p1 then a2 (a1 u)
  else if P115 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (p1) (u) < msr u v ∧ msr (a2 (a1 (a2 (a1 (p12))))) (a2 (a1 (p12))) < msr u v ∧ msr (a2 (a1 (p12))) (p12) < msr u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ tg (p12) = 2 ∧ tg (a1 (p12)) = 2 ∧ v = a1 (a1 (p12)) ∧ tg (a2 (p12)) = 2 ∧ a2 (a1 (p12)) = a2 (a2 (p12)) ∧ tg (a2 (a1 (p12))) = 2 ∧ tg (a1 (a2 (a1 (p12)))) = 2 ∧ a1 (a2 (p12)) = p16 ∧ v = p15 ∧ a2 (a1 (p12)) = a1 (a1 u) ∧ a1 (a2 u) = p2 ∧ a2 (a1 (p12)) = p1 then a2 (a1 u)
  else if P116 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (p1) (u) < msr u v ∧ msr (a2 (a1 (a2 (a1 (p12))))) (a2 (a1 (p12))) < msr u v ∧ msr (a2 (a1 (p12))) (p12) < msr u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ tg (p12) = 2 ∧ tg (a1 (p12)) = 2 ∧ v = a1 (a1 (p12)) ∧ tg (a2 (p12)) = 2 ∧ a2 (a1 (p12)) = a2 (a2 (p12)) ∧ tg (a2 (a1 (p12))) = 2 ∧ tg (a1 (a2 (a1 (p12)))) = 2 ∧ a1 (a2 (p12)) = p16 ∧ v = p15 ∧ a2 (a1 (p12)) = a1 (a1 u) ∧ a2 u = p2 ∧ a2 (a1 (a2 (a1 u))) = p2 ∧ a2 (a1 (p12)) = p1 then a2 (a1 u)
  else if P117 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (p1) (u) < msr u v ∧ msr (a2 (a1 (a2 (a1 (p12))))) (a2 (a1 (p12))) < msr u v ∧ msr (a2 (a1 (p12))) (p12) < msr u v ∧ msr (a2 (a1 (p12))) (a2 (a1 (a2 u))) < msr u v ∧ msr (a2 (a1 (a2 u))) (u) < msr u v ∧ tg (p12) = 2 ∧ tg (a1 (p12)) = 2 ∧ v = a1 (a1 (p12)) ∧ tg (a2 (p12)) = 2 ∧ a2 (a1 (p12)) = a2 (a2 (p12)) ∧ tg (a2 (a1 (p12))) = 2 ∧ tg (a1 (a2 (a1 (p12)))) = 2 ∧ a1 (a2 (p12)) = p16 ∧ v = p15 ∧ a1 u = p22 ∧ a2 (a1 (p12)) = p4 then a2 (a1 (a2 u))
  else if P118 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (p1) (u) < msr u v ∧ msr (a2 (a1 (a2 (a1 (p12))))) (a2 (a1 (p12))) < msr u v ∧ msr (a2 (a1 (p12))) (p12) < msr u v ∧ msr (a2 (a1 (p12))) (a2 (a2 u)) < msr u v ∧ msr (a2 (a1 (a2 (a2 u)))) (a2 (a2 u)) < msr u v ∧ msr (a2 (a2 u)) (u) < msr u v ∧ tg (p12) = 2 ∧ tg (a1 (p12)) = 2 ∧ v = a1 (a1 (p12)) ∧ tg (a2 (p12)) = 2 ∧ a2 (a1 (p12)) = a2 (a2 (p12)) ∧ tg (a2 (a1 (p12))) = 2 ∧ tg (a1 (a2 (a1 (p12)))) = 2 ∧ a1 (a2 (p12)) = p16 ∧ v = p15 ∧ a1 u = p23 ∧ a1 (a2 u) = p6 ∧ a2 (a1 (p12)) = p7 then a2 (a2 u)
  else if P119 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (p1) (u) < msr u v ∧ msr (a2 (a1 (a2 (a1 (p12))))) (a2 (a1 (p12))) < msr u v ∧ msr (a2 (a1 (p12))) (p12) < msr u v ∧ tg (p12) = 2 ∧ tg (a1 (p12)) = 2 ∧ v = a1 (a1 (p12)) ∧ tg (a2 (a1 (p12))) = 2 ∧ tg (a1 (a2 (a1 (p12)))) = 2 ∧ a2 (p12) = p16 ∧ tg (a2 (a1 (a2 (a1 (p12))))) = 2 ∧ a2 (a1 (p12)) = a2 (a2 (a1 (a2 (a1 (p12))))) ∧ v = p15 ∧ a2 (a1 (p12)) = a1 (a1 u) ∧ a2 (a1 (p12)) = p1 then a2 (a1 u)
  else if P120 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (p1) (u) < msr u v ∧ msr (a2 (a1 (a2 (a1 (p12))))) (a2 (a1 (p12))) < msr u v ∧ msr (a2 (a1 (p12))) (p12) < msr u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ tg (p12) = 2 ∧ tg (a1 (p12)) = 2 ∧ v = a1 (a1 (p12)) ∧ tg (a2 (a1 (p12))) = 2 ∧ tg (a1 (a2 (a1 (p12)))) = 2 ∧ a2 (p12) = p16 ∧ tg (a2 (a1 (a2 (a1 (p12))))) = 2 ∧ a2 (a1 (p12)) = a2 (a2 (a1 (a2 (a1 (p12))))) ∧ v = p15 ∧ a2 (a1 (p12)) = a1 (a1 u) ∧ a1 (a2 u) = p2 ∧ a2 (a1 (p12)) = p1 then a2 (a1 u)
  else if P121 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (p1) (u) < msr u v ∧ msr (a2 (a1 (a2 (a1 (p12))))) (a2 (a1 (p12))) < msr u v ∧ msr (a2 (a1 (p12))) (p12) < msr u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ tg (p12) = 2 ∧ tg (a1 (p12)) = 2 ∧ v = a1 (a1 (p12)) ∧ tg (a2 (a1 (p12))) = 2 ∧ tg (a1 (a2 (a1 (p12)))) = 2 ∧ a2 (p12) = p16 ∧ tg (a2 (a1 (a2 (a1 (p12))))) = 2 ∧ a2 (a1 (p12)) = a2 (a2 (a1 (a2 (a1 (p12))))) ∧ v = p15 ∧ a2 (a1 (p12)) = a1 (a1 u) ∧ a2 u = p2 ∧ a2 (a1 (a2 (a1 u))) = p2 ∧ a2 (a1 (p12)) = p1 then a2 (a1 u)
  else if P122 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (p1) (u) < msr u v ∧ msr (a2 (a1 (a2 (a1 (p12))))) (a2 (a1 (p12))) < msr u v ∧ msr (a2 (a1 (p12))) (p12) < msr u v ∧ msr (a2 (a1 (p12))) (a2 (a1 (a2 u))) < msr u v ∧ msr (a2 (a1 (a2 u))) (u) < msr u v ∧ tg (p12) = 2 ∧ tg (a1 (p12)) = 2 ∧ v = a1 (a1 (p12)) ∧ tg (a2 (a1 (p12))) = 2 ∧ tg (a1 (a2 (a1 (p12)))) = 2 ∧ a2 (p12) = p16 ∧ tg (a2 (a1 (a2 (a1 (p12))))) = 2 ∧ a2 (a1 (p12)) = a2 (a2 (a1 (a2 (a1 (p12))))) ∧ v = p15 ∧ a1 u = p22 ∧ a2 (a1 (p12)) = p4 then a2 (a1 (a2 u))
  else if P123 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (p1) (u) < msr u v ∧ msr (a2 (a1 (a2 (a1 (p12))))) (a2 (a1 (p12))) < msr u v ∧ msr (a2 (a1 (p12))) (p12) < msr u v ∧ msr (a2 (a1 (p12))) (a2 (a2 u)) < msr u v ∧ msr (a2 (a1 (a2 (a2 u)))) (a2 (a2 u)) < msr u v ∧ msr (a2 (a2 u)) (u) < msr u v ∧ tg (p12) = 2 ∧ tg (a1 (p12)) = 2 ∧ v = a1 (a1 (p12)) ∧ tg (a2 (a1 (p12))) = 2 ∧ tg (a1 (a2 (a1 (p12)))) = 2 ∧ a2 (p12) = p16 ∧ tg (a2 (a1 (a2 (a1 (p12))))) = 2 ∧ a2 (a1 (p12)) = a2 (a2 (a1 (a2 (a1 (p12))))) ∧ v = p15 ∧ a1 u = p23 ∧ a1 (a2 u) = p6 ∧ a2 (a1 (p12)) = p7 then a2 (a2 u)
  else if P124 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (p1) (u) < msr u v ∧ msr (a2 (a1 (a2 (a1 (p12))))) (a2 (a1 (p12))) < msr u v ∧ msr (a2 (a1 (p12))) (p12) < msr u v ∧ tg (p12) = 2 ∧ tg (a1 (p12)) = 2 ∧ v = a1 (a1 (p12)) ∧ tg (a2 (a1 (p12))) = 2 ∧ tg (a1 (a2 (a1 (p12)))) = 2 ∧ a2 (p12) = p16 ∧ a2 (a1 (a2 (a1 (p12)))) = p16 ∧ v = p15 ∧ a2 (a1 (p12)) = a1 (a1 u) ∧ a2 (a1 (p12)) = p1 then a2 (a1 u)
  else if P125 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (p1) (u) < msr u v ∧ msr (a2 (a1 (a2 (a1 (p12))))) (a2 (a1 (p12))) < msr u v ∧ msr (a2 (a1 (p12))) (p12) < msr u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ tg (p12) = 2 ∧ tg (a1 (p12)) = 2 ∧ v = a1 (a1 (p12)) ∧ tg (a2 (a1 (p12))) = 2 ∧ tg (a1 (a2 (a1 (p12)))) = 2 ∧ a2 (p12) = p16 ∧ a2 (a1 (a2 (a1 (p12)))) = p16 ∧ v = p15 ∧ a2 (a1 (p12)) = a1 (a1 u) ∧ a1 (a2 u) = p2 ∧ a2 (a1 (p12)) = p1 then a2 (a1 u)
  else if P126 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (p1) (u) < msr u v ∧ msr (a2 (a1 (a2 (a1 (p12))))) (a2 (a1 (p12))) < msr u v ∧ msr (a2 (a1 (p12))) (p12) < msr u v ∧ msr (a2 (a1 (a2 (a1 u)))) (a2 (a1 u)) < msr u v ∧ tg (p12) = 2 ∧ tg (a1 (p12)) = 2 ∧ v = a1 (a1 (p12)) ∧ tg (a2 (a1 (p12))) = 2 ∧ tg (a1 (a2 (a1 (p12)))) = 2 ∧ a2 (p12) = p16 ∧ a2 (a1 (a2 (a1 (p12)))) = p16 ∧ v = p15 ∧ a2 (a1 (p12)) = a1 (a1 u) ∧ a2 u = p2 ∧ a2 (a1 (a2 (a1 u))) = p2 ∧ a2 (a1 (p12)) = p1 then a2 (a1 u)
  else if P127 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (p1) (u) < msr u v ∧ msr (a2 (a1 (a2 (a1 (p12))))) (a2 (a1 (p12))) < msr u v ∧ msr (a2 (a1 (p12))) (p12) < msr u v ∧ msr (a2 (a1 (p12))) (a2 (a1 (a2 u))) < msr u v ∧ msr (a2 (a1 (a2 u))) (u) < msr u v ∧ tg (p12) = 2 ∧ tg (a1 (p12)) = 2 ∧ v = a1 (a1 (p12)) ∧ tg (a2 (a1 (p12))) = 2 ∧ tg (a1 (a2 (a1 (p12)))) = 2 ∧ a2 (p12) = p16 ∧ a2 (a1 (a2 (a1 (p12)))) = p16 ∧ v = p15 ∧ a1 u = p22 ∧ a2 (a1 (p12)) = p4 then a2 (a1 (a2 u))
  else if P128 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (p1) (u) < msr u v ∧ msr (a2 (a1 (a2 (a1 (p12))))) (a2 (a1 (p12))) < msr u v ∧ msr (a2 (a1 (p12))) (p12) < msr u v ∧ msr (a2 (a1 (p12))) (a2 (a2 u)) < msr u v ∧ msr (a2 (a1 (a2 (a2 u)))) (a2 (a2 u)) < msr u v ∧ msr (a2 (a2 u)) (u) < msr u v ∧ tg (p12) = 2 ∧ tg (a1 (p12)) = 2 ∧ v = a1 (a1 (p12)) ∧ tg (a2 (a1 (p12))) = 2 ∧ tg (a1 (a2 (a1 (p12)))) = 2 ∧ a2 (p12) = p16 ∧ a2 (a1 (a2 (a1 (p12)))) = p16 ∧ v = p15 ∧ a1 u = p23 ∧ a1 (a2 u) = p6 ∧ a2 (a1 (p12)) = p7 then a2 (a2 u)
  else if P129 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (p1) (u) < msr u v ∧ msr (a2 (a1 (p12))) (p12) < msr u v ∧ tg (p12) = 2 ∧ tg (a1 (p12)) = 2 ∧ v = p15 ∧ a2 (a1 (p12)) = a1 (a1 u) ∧ a2 (a1 (p12)) = p1 then a2 (a1 u)
  else if P130 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (p1) (u) < msr u v ∧ msr (v) (a2 (a1 (a2 (p12)))) < msr u v ∧ msr (a2 (a1 (a2 (p12)))) (p12) < msr u v ∧ tg (p12) = 2 ∧ tg (a2 (p12)) = 2 ∧ tg (a1 (a2 (p12))) = 2 ∧ a2 (a1 (a2 (p12))) = a2 (a2 (p12)) ∧ a1 (p12) = p17 ∧ v = p18 ∧ a2 (a1 (a2 (p12))) = a1 (a1 u) ∧ a2 (a1 (a2 (p12))) = p1 then a2 (a1 u)
  else if P131 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (p1) (u) < msr u v ∧ msr (v) (a2 (a2 (p12))) < msr u v ∧ msr (a2 (a1 (a2 (a2 (p12))))) (a2 (a2 (p12))) < msr u v ∧ msr (a2 (a2 (p12))) (p12) < msr u v ∧ tg (p12) = 2 ∧ tg (a2 (p12)) = 2 ∧ a1 (p12) = p19 ∧ tg (a2 (a2 (p12))) = 2 ∧ tg (a1 (a2 (a2 (p12)))) = 2 ∧ a1 (a2 (p12)) = p20 ∧ v = p21 ∧ a2 (a2 (p12)) = a1 (a1 u) ∧ a2 (a2 (p12)) = p1 then a2 (a1 u)
  else if P132 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (v) (u) < msr u v ∧ msr (p24) (u) < msr u v ∧ msr (p1) (p25) < msr u v ∧ u = p1 ∧ p1 = a2 (a1 u) ∧ p1 = a2 u ∧ v = p26 then a2 (a1 u)
  else if P133 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (p1) (u) < msr u v ∧ msr (p1) (p12) < msr u v ∧ v = p27 then a2 (a1 u)
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


def inst : Magma M := { op := op }

def Pre (u v : M) : Prop := P1 u v ∨ P2 u v ∨ P3 u v ∨ P4 u v ∨ P5 u v ∨ P6 u v ∨ P7 u v ∨ P8 u v ∨ P9 u v ∨ P10 u v ∨ P11 u v ∨ P12 u v ∨ P13 u v ∨ P14 u v ∨ P15 u v ∨ P16 u v ∨ P17 u v ∨ P18 u v ∨ P19 u v ∨ P20 u v ∨ P21 u v ∨ P22 u v ∨ P23 u v ∨ P24 u v ∨ P25 u v ∨ P26 u v ∨ P27 u v ∨ P28 u v ∨ P29 u v ∨ P30 u v ∨ P31 u v ∨ P32 u v ∨ P33 u v ∨ P34 u v ∨ P35 u v ∨ P36 u v ∨ P37 u v ∨ P38 u v ∨ P39 u v ∨ P40 u v ∨ P41 u v ∨ P42 u v ∨ P43 u v ∨ P44 u v ∨ P45 u v ∨ P46 u v ∨ P47 u v ∨ P48 u v ∨ P49 u v ∨ P50 u v ∨ P51 u v ∨ P52 u v ∨ P53 u v ∨ P54 u v ∨ P55 u v ∨ P56 u v ∨ P57 u v ∨ P58 u v ∨ P59 u v ∨ P60 u v ∨ P61 u v ∨ P62 u v ∨ P63 u v ∨ P64 u v ∨ P65 u v ∨ P66 u v ∨ P67 u v ∨ P68 u v ∨ P69 u v ∨ P70 u v ∨ P71 u v ∨ P72 u v ∨ P73 u v ∨ P74 u v ∨ P75 u v ∨ P76 u v ∨ P77 u v ∨ P78 u v ∨ P79 u v ∨ P80 u v ∨ P81 u v ∨ P82 u v ∨ P83 u v ∨ P84 u v ∨ P85 u v ∨ P86 u v ∨ P87 u v ∨ P88 u v ∨ P89 u v ∨ P90 u v ∨ P91 u v ∨ P92 u v ∨ P93 u v ∨ P94 u v ∨ P95 u v ∨ P96 u v ∨ P97 u v ∨ P98 u v ∨ P99 u v ∨ P100 u v ∨ P101 u v ∨ P102 u v ∨ P103 u v ∨ P104 u v ∨ P105 u v ∨ P106 u v ∨ P107 u v ∨ P108 u v ∨ P109 u v ∨ P110 u v ∨ P111 u v ∨ P112 u v ∨ P113 u v ∨ P114 u v ∨ P115 u v ∨ P116 u v ∨ P117 u v ∨ P118 u v ∨ P119 u v ∨ P120 u v ∨ P121 u v ∨ P122 u v ∨ P123 u v ∨ P124 u v ∨ P125 u v ∨ P126 u v ∨ P127 u v ∨ P128 u v ∨ P129 u v ∨ P130 u v ∨ P131 u v ∨ P132 u v ∨ P133 u v

theorem op_free {u v : M} (h : ¬ Pre u v) : op u v = J u v := by
  rw [op.eq_1]; simp only [Pre, not_or] at h; simp [h]

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 2) (g 0) (g 1)
  revert this
  change ¬ g 2 = op (op (g 0) (g 0)) (op (op (g 1) (op (g 2) (g 2))) (g 1))
  simp (config := {decide := true}) [op.eq_1, sz, P1, P2, P3, P4, P5, P6, P7, P8, P9, P10, P11, P12, P13, P14, P15, P16, P17, P18, P19, P20, P21, P22, P23, P24, P25, P26, P27, P28, P29, P30, P31, P32, P33, P34, P35, P36, P37, P38, P39, P40, P41, P42, P43, P44, P45, P46, P47, P48, P49, P50, P51, P52, P53, P54, P55, P56, P57, P58, P59, P60, P61, P62, P63, P64, P65, P66, P67, P68, P69, P70, P71, P72, P73, P74, P75, P76, P77, P78, P79, P80, P81, P82, P83, P84, P85, P86, P87, P88, P89, P90, P91, P92, P93, P94, P95, P96, P97, P98, P99, P100, P101, P102, P103, P104, P105, P106, P107, P108, P109, P110, P111, P112, P113, P114, P115, P116, P117, P118, P119, P120, P121, P122, P123, P124, P125, P126, P127, P128, P129, P130, P131, P132, P133]


/-- THE LAW: x = y * ((x * y) * ((z * y) * y)) -/
theorem law (x y z : M) : op (y) (op (op (x) (y)) (op (op (z) (y)) (y))) = x := by
  sorry


theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
