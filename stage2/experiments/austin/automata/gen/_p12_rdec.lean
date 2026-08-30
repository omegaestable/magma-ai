import JudgeProblem
set_option linter.unusedSimpArgs false
set_option linter.unusedVariables false
set_option warn.classDefReducibility false

inductive submission.M : Type where
  | g : Nat → submission.M
  | J : submission.M → submission.M → submission.M
  deriving DecidableEq, Repr

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

def P1 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 (a1 u) = a2 u ∧ tg v = 2 ∧ a2 (a1 u) = a1 v ∧ tg (a2 v) = 2 ∧ a1 (a1 u) = a1 (a2 v)
instance (u v : M) : Decidable (P1 u v) := by unfold P1; infer_instance
def P2 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 (a1 u) = a2 u ∧ tg v = 2 ∧ a2 (a1 u) = a1 v ∧ tg (a1 (a1 u)) = 2 ∧ tg (a1 (a1 (a1 u))) = 2 ∧ a2 v = a2 (a1 (a1 (a1 u))) ∧ a1 (a1 (a1 (a1 u))) = a2 (a1 (a1 u))
instance (u v : M) : Decidable (P2 u v) := by unfold P2; infer_instance
def P3 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 (a1 u) = a2 u ∧ tg v = 2 ∧ a2 (a1 u) = a1 v ∧ tg (a1 (a1 u)) = 2
instance (u v : M) : Decidable (P3 u v) := by unfold P3; infer_instance
def P4 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 (a1 u) = a2 u ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ v = a2 (a1 (a2 (a1 u))) ∧ a1 (a1 (a2 (a1 u))) = a2 (a2 (a1 u)) ∧ a1 (a1 u) = v
instance (u v : M) : Decidable (P4 u v) := by unfold P4; infer_instance
def P5 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 (a1 u) = a2 u ∧ tg (a2 (a1 u)) = 2 ∧ a1 (a1 u) = v
instance (u v : M) : Decidable (P5 u v) := by unfold P5; infer_instance
def P6 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 (a1 u) = a2 u ∧ tg (a1 (a1 u)) = 2 ∧ tg (a1 (a1 (a1 u))) = 2 ∧ a1 (a1 (a1 (a1 u))) = a2 (a1 (a1 u))
instance (u v : M) : Decidable (P6 u v) := by unfold P6; infer_instance
def P7 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 (a1 u) = a2 u ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ a1 (a1 (a2 (a1 u))) = a2 (a2 (a1 u)) ∧ v = a2 (a1 (a2 (a1 u))) ∧ tg (a1 (a1 u)) = 2 ∧ a1 (a1 (a1 u)) = v ∧ a2 (a1 (a1 u)) = a2 (a1 u)
instance (u v : M) : Decidable (P7 u v) := by unfold P7; infer_instance
def P8 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 (a1 u) = a2 u ∧ tg (a2 (a2 (a1 u))) = 2 ∧ a1 (a2 (a2 (a1 u))) = a1 (a1 u)
instance (u v : M) : Decidable (P8 u v) := by unfold P8; infer_instance
def P9 (u v : M) : Prop := tg u = 2 ∧ tg v = 2 ∧ tg (a2 v) = 2 ∧ a2 u = a1 (a2 v)
instance (u v : M) : Decidable (P9 u v) := by unfold P9; infer_instance
def P10 (u v : M) : Prop := tg u = 2 ∧ tg v = 2 ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a2 v = a2 (a1 (a2 u)) ∧ a1 (a1 (a2 u)) = a2 (a2 u)
instance (u v : M) : Decidable (P10 u v) := by unfold P10; infer_instance
def P11 (u v : M) : Prop := tg u = 2 ∧ tg v = 2 ∧ tg (a2 u) = 2
instance (u v : M) : Decidable (P11 u v) := by unfold P11; infer_instance
def P12 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2
instance (u v : M) : Decidable (P12 u v) := by unfold P12; infer_instance
def op (u v : M) : M :=
  let p1 := if hs1 : msr (a2 (a1 (a1 u))) (a2 v) < msr u v then op (a2 (a1 (a1 u))) (a2 v) else J u v
  let p2 := if hs2 : msr (a2 (a2 (a1 u))) (v) < msr u v then op (a2 (a2 (a1 u))) (v) else J u v
  let p3 := if hs3 : msr (a2 (a1 u)) (a2 (a1 (a1 (a1 u)))) < msr u v then op (a2 (a1 u)) (a2 (a1 (a1 (a1 u)))) else J u v
  let p4 := if hs4 : msr (a2 (a1 u)) (a2 (a2 (a1 u))) < msr u v then op (a2 (a1 u)) (a2 (a2 (a1 u))) else J u v
  let p5 := if hs5 : msr (a2 u) (a1 v) < msr u v then op (a2 u) (a1 v) else J u v
  let p6 := if hs6 : msr (a2 (a2 u)) (a2 v) < msr u v then op (a2 (a2 u)) (a2 v) else J u v
  let p7 := if hs7 : msr (a1 (a2 v)) (a1 v) < msr u v then op (a1 (a2 v)) (a1 v) else J u v
  let p8 := if hs8 : msr (p7) (a1 (a2 v)) < msr u v then op (p7) (a1 (a2 v)) else J u v
  if P1 u v then a2 (a1 u)
  else if P2 u v then a2 (a1 u)
  else if P3 u v ∧ msr (a2 (a1 (a1 u))) (a2 v) < msr u v ∧ a1 (a1 (a1 u)) = p1 then a2 (a1 u)
  else if P4 u v then a2 (a1 u)
  else if P5 u v ∧ msr (a2 (a2 (a1 u))) (v) < msr u v ∧ a1 (a2 (a1 u)) = p2 then a2 (a1 u)
  else if P6 u v ∧ msr (a2 (a1 u)) (a2 (a1 (a1 (a1 u)))) < msr u v ∧ v = p3 then a2 (a1 u)
  else if P7 u v then a2 (a1 u)
  else if P8 u v ∧ msr (a2 (a1 u)) (a2 (a2 (a1 u))) < msr u v ∧ v = p4 then a2 (a1 u)
  else if P9 u v ∧ msr (a2 u) (a1 v) < msr u v ∧ a1 u = p5 then a1 v
  else if P10 u v ∧ msr (a2 u) (a1 v) < msr u v ∧ a1 u = p5 then a1 v
  else if P11 u v ∧ msr (a2 u) (a1 v) < msr u v ∧ msr (a2 (a2 u)) (a2 v) < msr u v ∧ a1 u = p5 ∧ a1 (a2 u) = p6 then a1 v
  else if P12 u v ∧ msr (a1 (a2 v)) (a1 v) < msr u v ∧ msr (p7) (a1 (a2 v)) < msr u v ∧ u = p8 then a1 v
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


def inst : Magma M := { op := op }

def Pre (u v : M) : Prop := P1 u v ∨ P2 u v ∨ P3 u v ∨ P4 u v ∨ P5 u v ∨ P6 u v ∨ P7 u v ∨ P8 u v ∨ P9 u v ∨ P10 u v ∨ P11 u v ∨ P12 u v

theorem op_free {u v : M} (h : ¬ Pre u v) : op u v = J u v := by
  rw [op.eq_1]; simp only [Pre, not_or] at h; simp [h]
def topRule (u v : M) : Nat :=
  let p1 := if msr (a2 (a1 (a1 u))) (a2 v) < msr u v then op (a2 (a1 (a1 u))) (a2 v) else M.J u v
  let p2 := if msr (a2 (a2 (a1 u))) (v) < msr u v then op (a2 (a2 (a1 u))) (v) else M.J u v
  let p3 := if msr (a2 (a1 u)) (a2 (a1 (a1 (a1 u)))) < msr u v then op (a2 (a1 u)) (a2 (a1 (a1 (a1 u)))) else M.J u v
  let p4 := if msr (a2 (a1 u)) (a2 (a2 (a1 u))) < msr u v then op (a2 (a1 u)) (a2 (a2 (a1 u))) else M.J u v
  let p5 := if msr (a2 u) (a1 v) < msr u v then op (a2 u) (a1 v) else M.J u v
  let p6 := if msr (a2 (a2 u)) (a2 v) < msr u v then op (a2 (a2 u)) (a2 v) else M.J u v
  let p7 := if msr (a1 (a2 v)) (a1 v) < msr u v then op (a1 (a2 v)) (a1 v) else M.J u v
  let p8 := if msr (p7) (a1 (a2 v)) < msr u v then op (p7) (a1 (a2 v)) else M.J u v
  if P1 u v then 1
  else if P2 u v then 2
  else if P3 u v ∧ msr (a2 (a1 (a1 u))) (a2 v) < msr u v ∧ a1 (a1 (a1 u)) = p1 then 3
  else if P4 u v then 4
  else if P5 u v ∧ msr (a2 (a2 (a1 u))) (v) < msr u v ∧ a1 (a2 (a1 u)) = p2 then 5
  else if P6 u v ∧ msr (a2 (a1 u)) (a2 (a1 (a1 (a1 u)))) < msr u v ∧ v = p3 then 6
  else if P7 u v then 7
  else if P8 u v ∧ msr (a2 (a1 u)) (a2 (a2 (a1 u))) < msr u v ∧ v = p4 then 8
  else if P9 u v ∧ msr (a2 u) (a1 v) < msr u v ∧ a1 u = p5 then 9
  else if P10 u v ∧ msr (a2 u) (a1 v) < msr u v ∧ a1 u = p5 then 10
  else if P11 u v ∧ msr (a2 u) (a1 v) < msr u v ∧ msr (a2 (a2 u)) (a2 v) < msr u v ∧ a1 u = p5 ∧ a1 (a2 u) = p6 then 11
  else if P12 u v ∧ msr (a1 (a2 v)) (a1 v) < msr u v ∧ msr (p7) (a1 (a2 v)) < msr u v ∧ u = p8 then 12
  else 0

def E1 (x y : M) : M := M.J (M.J y x) y
def E2 (x y z : M) : M := M.J x (M.J y z)
def g (n : Nat) : M := M.g n
def dcl (u v : M) : Nat :=
  let r := op u v
  if r == M.J u v then 0 else if r == a2 (a1 u) then 1 else if r == a1 v then 2 else 3

def bs : List M := [g 0, g 1, M.J (g 0) (g 1)]
/-- (q,r) pairs whose product DECODES: q = E1 a b, r = E2 a b c -/
def dq : List (M × M) :=
  bs.flatMap (fun a => bs.flatMap (fun b => bs.map (fun c => (E1 a b, E2 a b c))))
/-- rule-9 shaped pair built ON TOP of a decoding (q,r): u = J (op q r) q, v = E2 r q w -/
def rp : List (M × M) :=
  dq.flatMap (fun qr => bs.map (fun w => (M.J (op qr.1 qr.2) qr.1, E2 qr.2 qr.1 w)))

#eval (dq.length, dq.countP (fun p => dcl p.1 p.2 != 0))            -- control: (q,r) decode
#eval (rp.length, rp.countP (fun p => dcl p.1 p.2 == 0),
       rp.countP (fun p => dcl p.1 p.2 == 1), rp.countP (fun p => dcl p.1 p.2 == 2))

/-- put an R-decoding pair (u,v) into each chain slot and test the law -/
def lawOK (x y z : M) : Bool := (op (op (op y x) y) (op x (op y z)) == x)
def cell (x y z : M) : (Nat × Nat × Nat × Nat) × Nat × Bool :=
  let A := op y x; let B := op y z; let V := op x B
  ((dcl y x, dcl A y, dcl y z, dcl x B), topRule (op A y) V, op (op A y) V == x)
def tally (ts : List (M × M × M)) : List (((Nat × Nat × Nat × Nat) × Nat × Bool) × Nat) :=
  ts.foldl (fun acc t => let c := cell t.1 t.2.1 t.2.2
    if acc.any (fun e => e.1 == c) then acc.map (fun e => if e.1 == c then (e.1, e.2+1) else e)
    else acc ++ [(c, 1)]) []

-- R-pair as (y,x)  => A R-decodes ;  as (y,z) => B R-decodes ;  as (x,B) via z
def fam_yx : List (M × M × M) := rp.flatMap (fun p => bs.map (fun r => (p.2, p.1, r)))
def fam_yz : List (M × M × M) := rp.flatMap (fun p => bs.map (fun r => (r, p.1, p.2)))
def fam_xB : List (M × M × M) := rp.flatMap (fun p => bs.map (fun r => (p.1, r, p.2)))
#eval (fam_yx.length, fam_yx.countP (fun t => !lawOK t.1 t.2.1 t.2.2), tally fam_yx)
#eval (fam_yz.length, fam_yz.countP (fun t => !lawOK t.1 t.2.1 t.2.2), tally fam_yz)
#eval (fam_xB.length, fam_xB.countP (fun t => !lawOK t.1 t.2.1 t.2.2), tally fam_xB)
