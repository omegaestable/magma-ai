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

def P1 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a2 (a1 v) ∧ tg (a2 v) = 2 ∧ tg (a2 (a2 v)) = 2 ∧ a1 (a2 v) = a1 (a2 (a2 v)) ∧ u = a2 (a2 (a2 v))
instance (u v : M) : Decidable (P1 u v) := by unfold P1; infer_instance
def P2 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a2 (a1 v) ∧ tg (a2 v) = 2
instance (u v : M) : Decidable (P2 u v) := by unfold P2; infer_instance
def P3 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a2 (a1 v) ∧ tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P3 u v) := by unfold P3; infer_instance
def P4 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a2 (a1 v) ∧ tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P4 u v) := by unfold P4; infer_instance
def P5 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a2 (a1 v) ∧ tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P5 u v) := by unfold P5; infer_instance
def P6 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a2 (a1 v) ∧ tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P6 u v) := by unfold P6; infer_instance
def P7 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ tg (a2 (a2 v)) = 2 ∧ a1 (a2 v) = a1 (a2 (a2 v)) ∧ u = a2 (a2 (a2 v)) ∧ tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P7 u v) := by unfold P7; infer_instance
def P8 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ tg (a2 (a2 v)) = 2 ∧ a1 (a2 v) = a1 (a2 (a2 v)) ∧ u = a2 (a2 (a2 v)) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2 ∧ a1 v = a1 (a2 u)
instance (u v : M) : Decidable (P8 u v) := by unfold P8; infer_instance
def P9 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ tg (a2 (a2 v)) = 2 ∧ a1 (a2 v) = a1 (a2 (a2 v)) ∧ u = a2 (a2 (a2 v)) ∧ tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P9 u v) := by unfold P9; infer_instance
def P10 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ tg (a2 (a2 v)) = 2 ∧ a1 (a2 v) = a1 (a2 (a2 v)) ∧ u = a2 (a2 (a2 v)) ∧ tg u = 2 ∧ tg (a2 u) = 2 ∧ a1 v = a1 (a2 u) ∧ tg (a2 (a2 u)) = 2 ∧ a1 v = a1 (a2 (a2 u)) ∧ tg (a2 (a2 (a2 u))) = 2 ∧ tg (a1 (a2 (a2 (a2 u)))) = 2
instance (u v : M) : Decidable (P10 u v) := by unfold P10; infer_instance
def P11 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P11 u v) := by unfold P11; infer_instance
def P12 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2 ∧ a1 v = a1 (a2 u)
instance (u v : M) : Decidable (P12 u v) := by unfold P12; infer_instance
def P13 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P13 u v) := by unfold P13; infer_instance
def P14 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ tg u = 2 ∧ tg (a2 u) = 2 ∧ a1 v = a1 (a2 u) ∧ tg (a2 (a2 u)) = 2 ∧ a1 v = a1 (a2 (a2 u)) ∧ tg (a2 (a2 (a2 u))) = 2 ∧ tg (a1 (a2 (a2 (a2 u)))) = 2
instance (u v : M) : Decidable (P14 u v) := by unfold P14; infer_instance
def P15 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P15 u v) := by unfold P15; infer_instance
def P16 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2 ∧ a1 v = a1 (a2 u) ∧ tg (a2 (a2 u)) = 2 ∧ a1 v = a1 (a2 (a2 u)) ∧ a2 (a1 u) = a2 (a2 (a2 u))
instance (u v : M) : Decidable (P16 u v) := by unfold P16; infer_instance
def P17 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2 ∧ a1 v = a1 (a2 u) ∧ tg (a2 (a2 u)) = 2 ∧ a1 v = a1 (a2 (a2 u)) ∧ a2 (a1 u) = a2 (a2 (a2 u))
instance (u v : M) : Decidable (P17 u v) := by unfold P17; infer_instance
def P18 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2 ∧ a1 v = a1 (a2 u) ∧ tg (a2 (a2 u)) = 2 ∧ a1 v = a1 (a2 (a2 u)) ∧ a2 (a1 u) = a2 (a2 (a2 u))
instance (u v : M) : Decidable (P18 u v) := by unfold P18; infer_instance
def P19 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2 ∧ a1 v = a1 (a2 u)
instance (u v : M) : Decidable (P19 u v) := by unfold P19; infer_instance
def P20 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2 ∧ a1 v = a1 (a2 u)
instance (u v : M) : Decidable (P20 u v) := by unfold P20; infer_instance
def P21 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2 ∧ a1 v = a1 (a2 u)
instance (u v : M) : Decidable (P21 u v) := by unfold P21; infer_instance
def P22 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2 ∧ a1 v = a1 (a2 u)
instance (u v : M) : Decidable (P22 u v) := by unfold P22; infer_instance
def P23 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P23 u v) := by unfold P23; infer_instance
def P24 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P24 u v) := by unfold P24; infer_instance
def P25 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P25 u v) := by unfold P25; infer_instance
def P26 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P26 u v) := by unfold P26; infer_instance
def P27 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ tg (a2 (a2 v)) = 2 ∧ a1 (a2 v) = a1 (a2 (a2 v)) ∧ u = a2 (a2 (a2 v)) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2 ∧ a1 v = a1 (a2 u) ∧ tg (a2 (a2 u)) = 2 ∧ a1 v = a1 (a2 (a2 u)) ∧ a2 (a1 u) = a2 (a2 (a2 u))
instance (u v : M) : Decidable (P27 u v) := by unfold P27; infer_instance
def P28 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2 ∧ a1 v = a1 (a2 u) ∧ tg (a2 (a2 u)) = 2 ∧ a1 v = a1 (a2 (a2 u)) ∧ a2 (a1 u) = a2 (a2 (a2 u))
instance (u v : M) : Decidable (P28 u v) := by unfold P28; infer_instance
def P29 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2 ∧ a1 v = a1 (a2 u) ∧ tg (a2 (a2 u)) = 2 ∧ a1 v = a1 (a2 (a2 u)) ∧ a2 (a1 u) = a2 (a2 (a2 u))
instance (u v : M) : Decidable (P29 u v) := by unfold P29; infer_instance
def P30 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P30 u v) := by unfold P30; infer_instance
def P31 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P31 u v) := by unfold P31; infer_instance
def P32 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P32 u v) := by unfold P32; infer_instance
def P33 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P33 u v) := by unfold P33; infer_instance
def P34 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P34 u v) := by unfold P34; infer_instance
def P35 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2
instance (u v : M) : Decidable (P35 u v) := by unfold P35; infer_instance
def P36 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P36 u v) := by unfold P36; infer_instance
def P37 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2 ∧ tg (a2 (a2 u)) = 2 ∧ tg (a2 (a2 (a2 u))) = 2 ∧ tg (a1 (a2 (a2 (a2 u)))) = 2
instance (u v : M) : Decidable (P37 u v) := by unfold P37; infer_instance
def P38 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2 ∧ tg (a2 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a2 (a2 u))
instance (u v : M) : Decidable (P38 u v) := by unfold P38; infer_instance
def P39 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2
instance (u v : M) : Decidable (P39 u v) := by unfold P39; infer_instance
def P40 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P40 u v) := by unfold P40; infer_instance
def P41 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2 ∧ tg (a2 (a2 u)) = 2 ∧ tg (a2 (a2 (a2 u))) = 2 ∧ tg (a1 (a2 (a2 (a2 u)))) = 2
instance (u v : M) : Decidable (P41 u v) := by unfold P41; infer_instance
def P42 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2 ∧ tg (a2 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a2 (a2 u))
instance (u v : M) : Decidable (P42 u v) := by unfold P42; infer_instance
def P43 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2
instance (u v : M) : Decidable (P43 u v) := by unfold P43; infer_instance
def P44 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P44 u v) := by unfold P44; infer_instance
def P45 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2 ∧ tg (a2 (a2 u)) = 2 ∧ tg (a2 (a2 (a2 u))) = 2 ∧ tg (a1 (a2 (a2 (a2 u)))) = 2
instance (u v : M) : Decidable (P45 u v) := by unfold P45; infer_instance
def P46 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2 ∧ tg (a2 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a2 (a2 u))
instance (u v : M) : Decidable (P46 u v) := by unfold P46; infer_instance
def P47 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2 ∧ tg (a2 (a2 u)) = 2 ∧ a2 (a1 u) = a2 (a2 (a2 u))
instance (u v : M) : Decidable (P47 u v) := by unfold P47; infer_instance
def P48 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 (a1 u)) = 2 ∧ a2 (a1 u) = v ∧ v = a1 u
instance (u v : M) : Decidable (P48 u v) := by unfold P48; infer_instance
def P49 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2
instance (u v : M) : Decidable (P49 u v) := by unfold P49; infer_instance
def op (u v : M) : M :=
  let p1 := if hs1 : msr (a1 (a2 v)) (u) < msr u v then op (a1 (a2 v)) (u) else J u v
  let p2 := if hs2 : msr (a2 (a1 u)) (u) < msr u v then op (a2 (a1 u)) (u) else J u v
  let p3 := if hs3 : msr (a2 (a1 (p2))) (p2) < msr u v then op (a2 (a1 (p2))) (p2) else J u v
  let p4 := if hs4 : msr (a2 v) (a2 (a1 (p2))) < msr u v then op (a2 v) (a2 (a1 (p2))) else J u v
  let p5 := if hs5 : msr (a2 v) (p4) < msr u v then op (a2 v) (p4) else J u v
  let p6 := if hs6 : msr (a2 (a1 (a2 (a2 (a2 (p2)))))) (a2 (a2 (a2 (p2)))) < msr u v then op (a2 (a1 (a2 (a2 (a2 (p2)))))) (a2 (a2 (a2 (p2)))) else J u v
  let p7 := if hs7 : msr (a2 (a2 (a2 (p2)))) (p2) < msr u v then op (a2 (a2 (a2 (p2)))) (p2) else J u v
  let p8 := if hs8 : msr (a1 v) (a2 (a1 u)) < msr u v then op (a1 v) (a2 (a1 u)) else J u v
  let p9 := if hs9 : msr (a1 v) (p8) < msr u v then op (a1 v) (p8) else J u v
  let p10 := if hs10 : msr (a2 (a1 (a2 (a2 (a2 u))))) (a2 (a2 (a2 u))) < msr u v then op (a2 (a1 (a2 (a2 (a2 u))))) (a2 (a2 (a2 u))) else J u v
  let p11 := if hs11 : msr (a2 (a2 (a2 u))) (u) < msr u v then op (a2 (a2 (a2 u))) (u) else J u v
  let p12 := if hs12 : msr (a2 (a1 (p3))) (p3) < msr u v then op (a2 (a1 (p3))) (p3) else J u v
  let p13 := if hs13 : msr (v) (a2 (a1 (p3))) < msr u v then op (v) (a2 (a1 (p3))) else J u v
  let p14 := if hs14 : msr (v) (p13) < msr u v then op (v) (p13) else J u v
  let p15 := if hs15 : msr (a2 (a1 (a2 (a2 (a2 (p3)))))) (a2 (a2 (a2 (p3)))) < msr u v then op (a2 (a1 (a2 (a2 (a2 (p3)))))) (a2 (a2 (a2 (p3)))) else J u v
  let p16 := if hs16 : msr (a2 (a2 (a2 (p3)))) (p3) < msr u v then op (a2 (a2 (a2 (p3)))) (p3) else J u v
  let p17 := if hs17 : msr (a2 (a1 (p3))) (a2 (a1 u)) < msr u v then op (a2 (a1 (p3))) (a2 (a1 u)) else J u v
  let p18 := if hs18 : msr (a2 (a1 (p3))) (p17) < msr u v then op (a2 (a1 (p3))) (p17) else J u v
  let p19 := if hs19 : msr (a2 (a1 u)) (p2) < msr u v then op (a2 (a1 u)) (p2) else J u v
  let p20 := if hs20 : msr (p2) (p19) < msr u v then op (p2) (p19) else J u v
  let p21 := if hs21 : msr (p2) (p3) < msr u v then op (p2) (p3) else J u v
  if P1 u v then a1 (a2 v)
  else if P2 u v ∧ msr (a1 (a2 v)) (u) < msr u v ∧ a2 (a2 v) = p1 then a1 (a2 v)
  else if P3 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (p2))) (p2) < msr u v ∧ tg (p2) = 2 ∧ tg (a1 (p2)) = 2 ∧ a2 v = p3 ∧ a2 (a1 u) = a2 (a1 (p2)) then a2 (a1 u)
  else if P4 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 v) (a2 (a1 (p2))) < msr u v ∧ msr (a2 (a1 (p2))) (p2) < msr u v ∧ tg (p2) = 2 ∧ tg (a1 (p2)) = 2 ∧ tg (a2 (p2)) = 2 ∧ a2 v = a1 (a2 (p2)) ∧ a2 (a2 (p2)) = p4 ∧ a2 v = p3 ∧ a2 (a1 u) = a2 (a1 (p2)) then a2 (a1 u)
  else if P5 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 v) (a2 (a1 (p2))) < msr u v ∧ msr (a2 v) (p4) < msr u v ∧ msr (a2 (a1 (p2))) (p2) < msr u v ∧ tg (p2) = 2 ∧ tg (a1 (p2)) = 2 ∧ a2 (p2) = p5 ∧ a2 v = p3 ∧ a2 (a1 u) = a2 (a1 (p2)) then a2 (a1 u)
  else if P6 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (a2 (a2 (a2 (p2)))))) (a2 (a2 (a2 (p2)))) < msr u v ∧ msr (a2 (a2 (a2 (p2)))) (p2) < msr u v ∧ tg (p2) = 2 ∧ tg (a2 (p2)) = 2 ∧ a2 v = a1 (a2 (p2)) ∧ tg (a2 (a2 (p2))) = 2 ∧ a2 v = a1 (a2 (a2 (p2))) ∧ tg (a2 (a2 (a2 (p2)))) = 2 ∧ tg (a1 (a2 (a2 (a2 (p2))))) = 2 ∧ a1 (p2) = p6 ∧ a2 v = p7 ∧ a2 (a1 u) = a2 (a2 (a2 (p2))) then a2 (a1 u)
  else if P7 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a1 v = p2 then a1 (a2 v)
  else if P8 u v ∧ msr (a1 v) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a2 (a2 u) = p8 ∧ a1 v = p2 then a1 (a2 v)
  else if P9 u v ∧ msr (a1 v) (a2 (a1 u)) < msr u v ∧ msr (a1 v) (p8) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a2 u = p9 ∧ a1 v = p2 then a1 (a2 v)
  else if P10 u v ∧ msr (a2 (a1 (a2 (a2 (a2 u))))) (a2 (a2 (a2 u))) < msr u v ∧ msr (a2 (a2 (a2 u))) (u) < msr u v ∧ a1 u = p10 ∧ a1 v = p11 then a1 (a2 v)
  else if P11 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a1 (a2 v)) (u) < msr u v ∧ a1 v = p2 ∧ a2 (a2 v) = p1 then a1 (a2 v)
  else if P12 u v ∧ msr (a1 v) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a1 (a2 v)) (u) < msr u v ∧ a2 (a2 u) = p8 ∧ a1 v = p2 ∧ a2 (a2 v) = p1 then a1 (a2 v)
  else if P13 u v ∧ msr (a1 v) (a2 (a1 u)) < msr u v ∧ msr (a1 v) (p8) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a1 (a2 v)) (u) < msr u v ∧ a2 u = p9 ∧ a1 v = p2 ∧ a2 (a2 v) = p1 then a1 (a2 v)
  else if P14 u v ∧ msr (a2 (a1 (a2 (a2 (a2 u))))) (a2 (a2 (a2 u))) < msr u v ∧ msr (a2 (a2 (a2 u))) (u) < msr u v ∧ msr (a1 (a2 v)) (u) < msr u v ∧ a1 u = p10 ∧ a1 v = p11 ∧ a2 (a2 v) = p1 then a1 (a2 v)
  else if P15 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (p2))) (p2) < msr u v ∧ a1 v = p2 ∧ tg (p2) = 2 ∧ tg (a1 (p2)) = 2 ∧ a2 v = p3 ∧ a2 (a1 u) = a2 (a1 (p2)) then a2 (a1 u)
  else if P16 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 v) (a2 (a1 (p2))) < msr u v ∧ msr (a2 (a1 (p2))) (p2) < msr u v ∧ a1 v = p2 ∧ tg (p2) = 2 ∧ tg (a1 (p2)) = 2 ∧ tg (a2 (p2)) = 2 ∧ a2 v = a1 (a2 (p2)) ∧ a2 (a2 (p2)) = p4 ∧ a2 v = p3 ∧ a2 (a1 u) = a2 (a1 (p2)) then a2 (a1 u)
  else if P17 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 v) (a2 (a1 (p2))) < msr u v ∧ msr (a2 v) (p4) < msr u v ∧ msr (a2 (a1 (p2))) (p2) < msr u v ∧ a1 v = p2 ∧ tg (p2) = 2 ∧ tg (a1 (p2)) = 2 ∧ a2 (p2) = p5 ∧ a2 v = p3 ∧ a2 (a1 u) = a2 (a1 (p2)) then a2 (a1 u)
  else if P18 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (a2 (a2 (a2 (p2)))))) (a2 (a2 (a2 (p2)))) < msr u v ∧ msr (a2 (a2 (a2 (p2)))) (p2) < msr u v ∧ a1 v = p2 ∧ tg (p2) = 2 ∧ tg (a2 (p2)) = 2 ∧ a2 v = a1 (a2 (p2)) ∧ tg (a2 (a2 (p2))) = 2 ∧ a2 v = a1 (a2 (a2 (p2))) ∧ tg (a2 (a2 (a2 (p2)))) = 2 ∧ tg (a1 (a2 (a2 (a2 (p2))))) = 2 ∧ a1 (p2) = p6 ∧ a2 v = p7 ∧ a2 (a1 u) = a2 (a2 (a2 (p2))) then a2 (a1 u)
  else if P19 u v ∧ msr (a1 v) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (p2))) (p2) < msr u v ∧ a2 (a2 u) = p8 ∧ a1 v = p2 ∧ tg (p2) = 2 ∧ tg (a1 (p2)) = 2 ∧ tg (a2 (p2)) = 2 ∧ a2 v = a1 (a2 (p2)) ∧ tg (a2 (a2 (p2))) = 2 ∧ a2 v = a1 (a2 (a2 (p2))) ∧ a2 (a1 (p2)) = a2 (a2 (a2 (p2))) ∧ a2 v = p3 ∧ a2 (a1 u) = a2 (a1 (p2)) then a2 (a1 u)
  else if P20 u v ∧ msr (a1 v) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 v) (a2 (a1 (p2))) < msr u v ∧ msr (a2 (a1 (p2))) (p2) < msr u v ∧ a2 (a2 u) = p8 ∧ a1 v = p2 ∧ tg (p2) = 2 ∧ tg (a1 (p2)) = 2 ∧ tg (a2 (p2)) = 2 ∧ a2 v = a1 (a2 (p2)) ∧ a2 (a2 (p2)) = p4 ∧ a2 v = p3 ∧ a2 (a1 u) = a2 (a1 (p2)) then a2 (a1 u)
  else if P21 u v ∧ msr (a1 v) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 v) (a2 (a1 (p2))) < msr u v ∧ msr (a2 v) (p4) < msr u v ∧ msr (a2 (a1 (p2))) (p2) < msr u v ∧ a2 (a2 u) = p8 ∧ a1 v = p2 ∧ tg (p2) = 2 ∧ tg (a1 (p2)) = 2 ∧ a2 (p2) = p5 ∧ a2 v = p3 ∧ a2 (a1 u) = a2 (a1 (p2)) then a2 (a1 u)
  else if P22 u v ∧ msr (a1 v) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (a2 (a2 (a2 (p2)))))) (a2 (a2 (a2 (p2)))) < msr u v ∧ msr (a2 (a2 (a2 (p2)))) (p2) < msr u v ∧ a2 (a2 u) = p8 ∧ a1 v = p2 ∧ tg (p2) = 2 ∧ tg (a2 (p2)) = 2 ∧ a2 v = a1 (a2 (p2)) ∧ tg (a2 (a2 (p2))) = 2 ∧ a2 v = a1 (a2 (a2 (p2))) ∧ tg (a2 (a2 (a2 (p2)))) = 2 ∧ tg (a1 (a2 (a2 (a2 (p2))))) = 2 ∧ a1 (p2) = p6 ∧ a2 v = p7 ∧ a2 (a1 u) = a2 (a2 (a2 (p2))) then a2 (a1 u)
  else if P23 u v ∧ msr (a1 v) (a2 (a1 u)) < msr u v ∧ msr (a1 v) (p8) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (p2))) (p2) < msr u v ∧ a2 u = p9 ∧ a1 v = p2 ∧ tg (p2) = 2 ∧ tg (a1 (p2)) = 2 ∧ tg (a2 (p2)) = 2 ∧ a2 v = a1 (a2 (p2)) ∧ tg (a2 (a2 (p2))) = 2 ∧ a2 v = a1 (a2 (a2 (p2))) ∧ a2 (a1 (p2)) = a2 (a2 (a2 (p2))) ∧ a2 v = p3 ∧ a2 (a1 u) = a2 (a1 (p2)) then a2 (a1 u)
  else if P24 u v ∧ msr (a1 v) (a2 (a1 u)) < msr u v ∧ msr (a1 v) (p8) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 v) (a2 (a1 (p2))) < msr u v ∧ msr (a2 (a1 (p2))) (p2) < msr u v ∧ a2 u = p9 ∧ a1 v = p2 ∧ tg (p2) = 2 ∧ tg (a1 (p2)) = 2 ∧ tg (a2 (p2)) = 2 ∧ a2 v = a1 (a2 (p2)) ∧ a2 (a2 (p2)) = p4 ∧ a2 v = p3 ∧ a2 (a1 u) = a2 (a1 (p2)) then a2 (a1 u)
  else if P25 u v ∧ msr (a1 v) (a2 (a1 u)) < msr u v ∧ msr (a1 v) (p8) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 v) (a2 (a1 (p2))) < msr u v ∧ msr (a2 v) (p4) < msr u v ∧ msr (a2 (a1 (p2))) (p2) < msr u v ∧ a2 u = p9 ∧ a1 v = p2 ∧ tg (p2) = 2 ∧ tg (a1 (p2)) = 2 ∧ a2 (p2) = p5 ∧ a2 v = p3 ∧ a2 (a1 u) = a2 (a1 (p2)) then a2 (a1 u)
  else if P26 u v ∧ msr (a1 v) (a2 (a1 u)) < msr u v ∧ msr (a1 v) (p8) < msr u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (a2 (a2 (a2 (p2)))))) (a2 (a2 (a2 (p2)))) < msr u v ∧ msr (a2 (a2 (a2 (p2)))) (p2) < msr u v ∧ a2 u = p9 ∧ a1 v = p2 ∧ tg (p2) = 2 ∧ tg (a2 (p2)) = 2 ∧ a2 v = a1 (a2 (p2)) ∧ tg (a2 (a2 (p2))) = 2 ∧ a2 v = a1 (a2 (a2 (p2))) ∧ tg (a2 (a2 (a2 (p2)))) = 2 ∧ tg (a1 (a2 (a2 (a2 (p2))))) = 2 ∧ a1 (p2) = p6 ∧ a2 v = p7 ∧ a2 (a1 u) = a2 (a2 (a2 (p2))) then a2 (a1 u)
  else if P27 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ a1 v = p2 then a1 (a2 v)
  else if P28 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a1 (a2 v)) (u) < msr u v ∧ a1 v = p2 ∧ a2 (a2 v) = p1 then a1 (a2 v)
  else if P29 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (p2))) (p2) < msr u v ∧ a1 v = p2 ∧ tg (p2) = 2 ∧ tg (a1 (p2)) = 2 ∧ a2 v = p3 ∧ a2 (a1 u) = a2 (a1 (p2)) then a2 (a1 u)
  else if P30 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (p2))) (p2) < msr u v ∧ msr (a2 (a1 (p3))) (p3) < msr u v ∧ tg (p2) = 2 ∧ tg (a1 (p2)) = 2 ∧ a2 (a1 u) = a2 (a1 (p2)) ∧ tg (p3) = 2 ∧ tg (a1 (p3)) = 2 ∧ v = p12 ∧ tg (a2 (a1 (p3))) = 2 ∧ u = a2 (a2 (a1 (p3))) then a2 (a1 u)
  else if P31 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (p2))) (p2) < msr u v ∧ msr (v) (a2 (a1 (p3))) < msr u v ∧ msr (a2 (a1 (p3))) (p3) < msr u v ∧ tg (p2) = 2 ∧ tg (a1 (p2)) = 2 ∧ a2 (a1 u) = a2 (a1 (p2)) ∧ tg (p3) = 2 ∧ tg (a1 (p3)) = 2 ∧ tg (a2 (p3)) = 2 ∧ v = a1 (a2 (p3)) ∧ a2 (a2 (p3)) = p13 ∧ v = p12 ∧ tg (a2 (a1 (p3))) = 2 ∧ u = a2 (a2 (a1 (p3))) then a2 (a1 u)
  else if P32 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (p2))) (p2) < msr u v ∧ msr (v) (a2 (a1 (p3))) < msr u v ∧ msr (v) (p13) < msr u v ∧ msr (a2 (a1 (p3))) (p3) < msr u v ∧ tg (p2) = 2 ∧ tg (a1 (p2)) = 2 ∧ a2 (a1 u) = a2 (a1 (p2)) ∧ tg (p3) = 2 ∧ tg (a1 (p3)) = 2 ∧ a2 (p3) = p14 ∧ v = p12 ∧ tg (a2 (a1 (p3))) = 2 ∧ u = a2 (a2 (a1 (p3))) then a2 (a1 u)
  else if P33 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (p2))) (p2) < msr u v ∧ msr (a2 (a1 (a2 (a2 (a2 (p3)))))) (a2 (a2 (a2 (p3)))) < msr u v ∧ msr (a2 (a2 (a2 (p3)))) (p3) < msr u v ∧ tg (p2) = 2 ∧ tg (a1 (p2)) = 2 ∧ a2 (a1 u) = a2 (a1 (p2)) ∧ tg (p3) = 2 ∧ tg (a2 (p3)) = 2 ∧ v = a1 (a2 (p3)) ∧ tg (a2 (a2 (p3))) = 2 ∧ v = a1 (a2 (a2 (p3))) ∧ tg (a2 (a2 (a2 (p3)))) = 2 ∧ tg (a1 (a2 (a2 (a2 (p3))))) = 2 ∧ a1 (p3) = p15 ∧ v = p16 ∧ u = a2 (a2 (a2 (a2 (p3)))) then a2 (a1 u)
  else if P34 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (p2))) (p2) < msr u v ∧ msr (a2 (a1 (p3))) (p3) < msr u v ∧ tg (p2) = 2 ∧ tg (a1 (p2)) = 2 ∧ a2 (a1 u) = a2 (a1 (p2)) ∧ tg (p3) = 2 ∧ tg (a1 (p3)) = 2 ∧ v = p12 ∧ a2 (a1 (p3)) = p2 then a2 (a1 u)
  else if P35 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (p2))) (p2) < msr u v ∧ msr (a2 (a1 (p3))) (p3) < msr u v ∧ msr (a2 (a1 (p3))) (a2 (a1 u)) < msr u v ∧ tg (p2) = 2 ∧ tg (a1 (p2)) = 2 ∧ a2 (a1 u) = a2 (a1 (p2)) ∧ tg (p3) = 2 ∧ tg (a1 (p3)) = 2 ∧ tg (a2 (p3)) = 2 ∧ v = a1 (a2 (p3)) ∧ tg (a2 (a2 (p3))) = 2 ∧ v = a1 (a2 (a2 (p3))) ∧ a2 (a1 (p3)) = a2 (a2 (a2 (p3))) ∧ v = p12 ∧ a2 (a1 (p3)) = a1 (a2 u) ∧ a2 (a2 u) = p17 ∧ a2 (a1 (p3)) = p2 then a2 (a1 u)
  else if P36 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (p2))) (p2) < msr u v ∧ msr (a2 (a1 (p3))) (p3) < msr u v ∧ msr (a2 (a1 (p3))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 (p3))) (p17) < msr u v ∧ tg (p2) = 2 ∧ tg (a1 (p2)) = 2 ∧ a2 (a1 u) = a2 (a1 (p2)) ∧ tg (p3) = 2 ∧ tg (a1 (p3)) = 2 ∧ tg (a2 (p3)) = 2 ∧ v = a1 (a2 (p3)) ∧ tg (a2 (a2 (p3))) = 2 ∧ v = a1 (a2 (a2 (p3))) ∧ a2 (a1 (p3)) = a2 (a2 (a2 (p3))) ∧ v = p12 ∧ a2 u = p18 ∧ a2 (a1 (p3)) = p2 then a2 (a1 u)
  else if P37 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (p2))) (p2) < msr u v ∧ msr (a2 (a1 (p3))) (p3) < msr u v ∧ msr (a2 (a1 (a2 (a2 (a2 u))))) (a2 (a2 (a2 u))) < msr u v ∧ msr (a2 (a2 (a2 u))) (u) < msr u v ∧ tg (p2) = 2 ∧ tg (a1 (p2)) = 2 ∧ a2 (a1 u) = a2 (a1 (p2)) ∧ tg (p3) = 2 ∧ tg (a1 (p3)) = 2 ∧ tg (a2 (p3)) = 2 ∧ v = a1 (a2 (p3)) ∧ tg (a2 (a2 (p3))) = 2 ∧ v = a1 (a2 (a2 (p3))) ∧ a2 (a1 (p3)) = a2 (a2 (a2 (p3))) ∧ v = p12 ∧ a2 (a1 (p3)) = a1 (a2 u) ∧ a2 (a1 (p3)) = a1 (a2 (a2 u)) ∧ a1 u = p10 ∧ a2 (a1 (p3)) = p11 then a2 (a1 u)
  else if P38 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (p2))) (p2) < msr u v ∧ msr (v) (a2 (a1 (p3))) < msr u v ∧ msr (a2 (a1 (p3))) (p3) < msr u v ∧ tg (p2) = 2 ∧ tg (a1 (p2)) = 2 ∧ a2 (a1 u) = a2 (a1 (p2)) ∧ tg (p3) = 2 ∧ tg (a1 (p3)) = 2 ∧ tg (a2 (p3)) = 2 ∧ v = a1 (a2 (p3)) ∧ a2 (a2 (p3)) = p13 ∧ v = p12 ∧ a2 (a1 (p3)) = a1 (a2 u) ∧ a2 (a1 (p3)) = a1 (a2 (a2 u)) ∧ a2 (a1 (p3)) = p2 then a2 (a1 u)
  else if P39 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (p2))) (p2) < msr u v ∧ msr (v) (a2 (a1 (p3))) < msr u v ∧ msr (a2 (a1 (p3))) (p3) < msr u v ∧ msr (a2 (a1 (p3))) (a2 (a1 u)) < msr u v ∧ tg (p2) = 2 ∧ tg (a1 (p2)) = 2 ∧ a2 (a1 u) = a2 (a1 (p2)) ∧ tg (p3) = 2 ∧ tg (a1 (p3)) = 2 ∧ tg (a2 (p3)) = 2 ∧ v = a1 (a2 (p3)) ∧ a2 (a2 (p3)) = p13 ∧ v = p12 ∧ a2 (a1 (p3)) = a1 (a2 u) ∧ a2 (a2 u) = p17 ∧ a2 (a1 (p3)) = p2 then a2 (a1 u)
  else if P40 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (p2))) (p2) < msr u v ∧ msr (v) (a2 (a1 (p3))) < msr u v ∧ msr (a2 (a1 (p3))) (p3) < msr u v ∧ msr (a2 (a1 (p3))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 (p3))) (p17) < msr u v ∧ tg (p2) = 2 ∧ tg (a1 (p2)) = 2 ∧ a2 (a1 u) = a2 (a1 (p2)) ∧ tg (p3) = 2 ∧ tg (a1 (p3)) = 2 ∧ tg (a2 (p3)) = 2 ∧ v = a1 (a2 (p3)) ∧ a2 (a2 (p3)) = p13 ∧ v = p12 ∧ a2 u = p18 ∧ a2 (a1 (p3)) = p2 then a2 (a1 u)
  else if P41 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (p2))) (p2) < msr u v ∧ msr (v) (a2 (a1 (p3))) < msr u v ∧ msr (a2 (a1 (p3))) (p3) < msr u v ∧ msr (a2 (a1 (a2 (a2 (a2 u))))) (a2 (a2 (a2 u))) < msr u v ∧ msr (a2 (a2 (a2 u))) (u) < msr u v ∧ tg (p2) = 2 ∧ tg (a1 (p2)) = 2 ∧ a2 (a1 u) = a2 (a1 (p2)) ∧ tg (p3) = 2 ∧ tg (a1 (p3)) = 2 ∧ tg (a2 (p3)) = 2 ∧ v = a1 (a2 (p3)) ∧ a2 (a2 (p3)) = p13 ∧ v = p12 ∧ a2 (a1 (p3)) = a1 (a2 u) ∧ a2 (a1 (p3)) = a1 (a2 (a2 u)) ∧ a1 u = p10 ∧ a2 (a1 (p3)) = p11 then a2 (a1 u)
  else if P42 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (p2))) (p2) < msr u v ∧ msr (v) (a2 (a1 (p3))) < msr u v ∧ msr (v) (p13) < msr u v ∧ msr (a2 (a1 (p3))) (p3) < msr u v ∧ tg (p2) = 2 ∧ tg (a1 (p2)) = 2 ∧ a2 (a1 u) = a2 (a1 (p2)) ∧ tg (p3) = 2 ∧ tg (a1 (p3)) = 2 ∧ a2 (p3) = p14 ∧ v = p12 ∧ a2 (a1 (p3)) = a1 (a2 u) ∧ a2 (a1 (p3)) = a1 (a2 (a2 u)) ∧ a2 (a1 (p3)) = p2 then a2 (a1 u)
  else if P43 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (p2))) (p2) < msr u v ∧ msr (v) (a2 (a1 (p3))) < msr u v ∧ msr (v) (p13) < msr u v ∧ msr (a2 (a1 (p3))) (p3) < msr u v ∧ msr (a2 (a1 (p3))) (a2 (a1 u)) < msr u v ∧ tg (p2) = 2 ∧ tg (a1 (p2)) = 2 ∧ a2 (a1 u) = a2 (a1 (p2)) ∧ tg (p3) = 2 ∧ tg (a1 (p3)) = 2 ∧ a2 (p3) = p14 ∧ v = p12 ∧ a2 (a1 (p3)) = a1 (a2 u) ∧ a2 (a2 u) = p17 ∧ a2 (a1 (p3)) = p2 then a2 (a1 u)
  else if P44 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (p2))) (p2) < msr u v ∧ msr (v) (a2 (a1 (p3))) < msr u v ∧ msr (v) (p13) < msr u v ∧ msr (a2 (a1 (p3))) (p3) < msr u v ∧ msr (a2 (a1 (p3))) (a2 (a1 u)) < msr u v ∧ msr (a2 (a1 (p3))) (p17) < msr u v ∧ tg (p2) = 2 ∧ tg (a1 (p2)) = 2 ∧ a2 (a1 u) = a2 (a1 (p2)) ∧ tg (p3) = 2 ∧ tg (a1 (p3)) = 2 ∧ a2 (p3) = p14 ∧ v = p12 ∧ a2 u = p18 ∧ a2 (a1 (p3)) = p2 then a2 (a1 u)
  else if P45 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (p2))) (p2) < msr u v ∧ msr (v) (a2 (a1 (p3))) < msr u v ∧ msr (v) (p13) < msr u v ∧ msr (a2 (a1 (p3))) (p3) < msr u v ∧ msr (a2 (a1 (a2 (a2 (a2 u))))) (a2 (a2 (a2 u))) < msr u v ∧ msr (a2 (a2 (a2 u))) (u) < msr u v ∧ tg (p2) = 2 ∧ tg (a1 (p2)) = 2 ∧ a2 (a1 u) = a2 (a1 (p2)) ∧ tg (p3) = 2 ∧ tg (a1 (p3)) = 2 ∧ a2 (p3) = p14 ∧ v = p12 ∧ a2 (a1 (p3)) = a1 (a2 u) ∧ a2 (a1 (p3)) = a1 (a2 (a2 u)) ∧ a1 u = p10 ∧ a2 (a1 (p3)) = p11 then a2 (a1 u)
  else if P46 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (p2))) (p2) < msr u v ∧ msr (a2 (a1 (p3))) (p3) < msr u v ∧ tg (p2) = 2 ∧ tg (a1 (p2)) = 2 ∧ a2 (a1 u) = a2 (a1 (p2)) ∧ tg (p3) = 2 ∧ tg (a1 (p3)) = 2 ∧ v = p12 ∧ a2 (a1 (p3)) = a1 (a2 u) ∧ a2 (a1 (p3)) = a1 (a2 (a2 u)) ∧ a2 (a1 (p3)) = p2 then a2 (a1 u)
  else if P47 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (p2))) (p2) < msr u v ∧ msr (a2 (a1 (a2 (a2 (a2 (p3)))))) (a2 (a2 (a2 (p3)))) < msr u v ∧ msr (a2 (a2 (a2 (p3)))) (p3) < msr u v ∧ tg (p2) = 2 ∧ tg (a1 (p2)) = 2 ∧ a2 (a1 u) = a2 (a1 (p2)) ∧ tg (p3) = 2 ∧ tg (a2 (p3)) = 2 ∧ v = a1 (a2 (p3)) ∧ tg (a2 (a2 (p3))) = 2 ∧ v = a1 (a2 (a2 (p3))) ∧ tg (a2 (a2 (a2 (p3)))) = 2 ∧ tg (a1 (a2 (a2 (a2 (p3))))) = 2 ∧ a1 (p3) = p15 ∧ v = p16 ∧ a2 (a2 (a2 (p3))) = a1 (a2 u) ∧ a2 (a2 (a2 (p3))) = a1 (a2 (a2 u)) ∧ a2 (a2 (a2 (p3))) = p2 then a2 (a1 u)
  else if P48 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 u)) (p2) < msr u v ∧ msr (p2) (p19) < msr u v ∧ p2 = a2 (a2 (a1 u)) ∧ p2 = a2 u ∧ v = p20 then a2 (a1 u)
  else if P49 u v ∧ msr (a2 (a1 u)) (u) < msr u v ∧ msr (a2 (a1 (p2))) (p2) < msr u v ∧ msr (p2) (p3) < msr u v ∧ tg (p2) = 2 ∧ tg (a1 (p2)) = 2 ∧ a2 (a1 u) = a2 (a1 (p2)) ∧ v = p21 then a2 (a1 u)
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


def inst : Magma M := { op := op }

def Pre (u v : M) : Prop := P1 u v ∨ P2 u v ∨ P3 u v ∨ P4 u v ∨ P5 u v ∨ P6 u v ∨ P7 u v ∨ P8 u v ∨ P9 u v ∨ P10 u v ∨ P11 u v ∨ P12 u v ∨ P13 u v ∨ P14 u v ∨ P15 u v ∨ P16 u v ∨ P17 u v ∨ P18 u v ∨ P19 u v ∨ P20 u v ∨ P21 u v ∨ P22 u v ∨ P23 u v ∨ P24 u v ∨ P25 u v ∨ P26 u v ∨ P27 u v ∨ P28 u v ∨ P29 u v ∨ P30 u v ∨ P31 u v ∨ P32 u v ∨ P33 u v ∨ P34 u v ∨ P35 u v ∨ P36 u v ∨ P37 u v ∨ P38 u v ∨ P39 u v ∨ P40 u v ∨ P41 u v ∨ P42 u v ∨ P43 u v ∨ P44 u v ∨ P45 u v ∨ P46 u v ∨ P47 u v ∨ P48 u v ∨ P49 u v

theorem op_free {u v : M} (h : ¬ Pre u v) : op u v = J u v := by
  rw [op.eq_1]; simp only [Pre, not_or] at h; simp [h]

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 2) (g 0) (g 1)
  revert this
  change ¬ g 2 = op (op (g 0) (op (g 1) (g 0))) (op (op (g 2) (g 2)) (g 0))
  simp (config := {decide := true}) [op.eq_1, sz, P1, P2, P3, P4, P5, P6, P7, P8, P9, P10, P11, P12, P13, P14, P15, P16, P17, P18, P19, P20, P21, P22, P23, P24, P25, P26, P27, P28, P29, P30, P31, P32, P33, P34, P35, P36, P37, P38, P39, P40, P41, P42, P43, P44, P45, P46, P47, P48, P49]


/-- THE LAW: x = y * ((z * y) * (x * (x * y))) -/
theorem law (x y z : M) : op (y) (op (op (z) (y)) (op (x) (op (x) (y)))) = x := by
  sorry


theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
