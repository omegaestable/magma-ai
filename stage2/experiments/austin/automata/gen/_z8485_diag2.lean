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

def P1 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ tg (a1 (a2 v)) = 2 ∧ tg (a1 (a1 (a2 v))) = 2 ∧ a1 v = a2 (a1 (a1 (a2 v))) ∧ u = a2 (a1 (a2 v)) ∧ u = a2 (a2 v)
instance (u v : M) : Decidable (P1 u v) := by unfold P1; infer_instance
def P2 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ tg (a2 (a1 v)) = 2
instance (u v : M) : Decidable (P2 u v) := by unfold P2; infer_instance
def P3 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a2 u) = 2 ∧ tg (a2 (a2 u)) = 2
instance (u v : M) : Decidable (P3 u v) := by unfold P3; infer_instance
def P4 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a2 u) = 2 ∧ tg (a2 (a2 u)) = 2 ∧ tg (a1 (a2 (a2 u))) = 2
instance (u v : M) : Decidable (P4 u v) := by unfold P4; infer_instance
def op (u v : M) : M :=
  let p1 := if hs1 : msr (a2 (a2 (a1 v))) (a1 v) < msr u v then op (a2 (a2 (a1 v))) (a1 v) else J u v
  let p2 := if hs2 : msr (p1) (u) < msr u v then op (p1) (u) else J u v
  let p3 := if hs3 : msr (p2) (u) < msr u v then op (p2) (u) else J u v
  let p4 := if hs4 : msr (a1 (a2 (a2 u))) (a1 v) < msr u v then op (a1 (a2 (a2 u))) (a1 v) else J u v
  let p5 := if hs5 : msr (p4) (u) < msr u v then op (p4) (u) else J u v
  let p6 := if hs6 : msr (p5) (u) < msr u v then op (p5) (u) else J u v
  let p7 := if hs7 : msr (a1 (a1 (a2 (a2 u)))) (a1 v) < msr u v then op (a1 (a1 (a2 (a2 u)))) (a1 v) else J u v
  let p8 := if hs8 : msr (p7) (u) < msr u v then op (p7) (u) else J u v
  let p9 := if hs9 : msr (p8) (u) < msr u v then op (p8) (u) else J u v
  if P1 u v then a1 v
  else if P2 u v ∧ msr (a2 (a2 (a1 v))) (a1 v) < msr u v ∧ msr (p1) (u) < msr u v ∧ msr (p2) (u) < msr u v ∧ a2 v = p3 then a1 v
  else if P3 u v ∧ msr (a1 (a2 (a2 u))) (a1 v) < msr u v ∧ msr (p4) (u) < msr u v ∧ msr (p5) (u) < msr u v ∧ a2 v = p6 then a1 v
  else if P4 u v ∧ msr (a1 (a1 (a2 (a2 u)))) (a1 v) < msr u v ∧ msr (p7) (u) < msr u v ∧ msr (p8) (u) < msr u v ∧ a2 v = p9 then a1 v
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


def inst : Magma M := { op := op }

def Pre (u v : M) : Prop := P1 u v ∨ P2 u v ∨ P3 u v ∨ P4 u v

theorem op_free {u v : M} (h : ¬ Pre u v) : op u v = J u v := by
  rw [op.eq_1]; simp only [Pre, not_or] at h; simp [h]


-- ---------------- DIAGNOSTIC (not a certificate) ----------------
-- z0=g0 A=g0 Cc=g0 zz=g0 y=g0   (the smallest instance of _z8485_break.py)
def X1d : M := J (g 0) (J (g 0) (g 0))
def cd  : M := J (g 0) X1d
def xd  : M := J X1d cd
def yd  : M := g 0
def zd  : M := J cd (J (J (J (g 0) cd) cd) cd)

#eval (op (g 0) X1d == cd)                      -- want true  (c is the free product)
#eval (op cd zd == cd)                          -- want true  (P1 fires)
#eval (op zd xd == X1d)                         -- P = a1 x, decoded
#eval (a2 (a2 xd) == zd)                        -- FALSE: the locator is destroyed
#eval (op yd (op xd (op (op (op zd xd) yd) yd)) == xd)   -- THE LAW: expect FALSE
#eval sz xd
#eval sz zd

theorem broken : op yd (op xd (op (op (op zd xd) yd) yd)) ≠ xd := by decide
end submission
