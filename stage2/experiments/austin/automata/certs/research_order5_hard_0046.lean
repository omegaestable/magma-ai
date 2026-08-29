import JudgeProblem
set_option linter.unusedSimpArgs false
set_option linter.unusedVariables false
set_option warn.classDefReducibility false

inductive submission.M : Type where
  | S : submission.M → submission.M
  | g : Nat → submission.M
  | J : submission.M → submission.M → submission.M
  deriving DecidableEq

namespace submission
open M

def tg : M → Nat
  | .S _ => 0
  | .g _ => 1
  | .J _ _ => 2

def a1 : M → M
  | .S x => x
  | .J x _ => x
  | t => t

def a2 : M → M
  | .J _ x => x
  | t => t

def sz : M → Nat
  | .g _ => 1
  | .S b0 => sz b0 + 1
  | .J b0 b1 => sz b0 + sz b1 + 1

def op (u v : M) : M :=
  if u = v then (M.S u) else if tg u = 2 ∧ tg (a1 u) = 0 ∧ tg (a2 u) = 2 ∧ (a1 (a1 u)) = v then (a2 (a2 u)) else M.J u v

def inst : Magma M := { op := op }

theorem eqf (a b : M) (h : sz a ≠ sz b) : (a = b) = False := eq_false (fun e => h (congrArg sz e))

theorem tg_S (t : M) (h : tg t = 0) : ∃ b0, t = M.S b0 := by cases t <;> simp_all [tg]
theorem tg_g (t : M) (h : tg t = 1) : ∃ n, t = M.g n := by cases t <;> simp_all [tg]
theorem tg_J (t : M) (h : tg t = 2) : ∃ b0 b1, t = M.J b0 b1 := by cases t <;> simp_all [tg]
theorem tg_range (t : M) : tg t < 3 := by cases t <;> simp [tg]
@[simp] theorem tg_S_eq (b0 : M) : tg (M.S b0) = 0 := rfl
@[simp] theorem a1_S_eq (b0 : M) : a1 (M.S b0) = b0 := rfl
@[simp] theorem tg_g_eq (n : Nat) : tg (M.g n) = 1 := rfl
@[simp] theorem tg_J_eq (b0 b1 : M) : tg (M.J b0 b1) = 2 := rfl
@[simp] theorem a1_J_eq (b0 b1 : M) : a1 (M.J b0 b1) = b0 := rfl
@[simp] theorem a2_J_eq (b0 b1 : M) : a2 (M.J b0 b1) = b1 := rfl

theorem law (x y z : M) : (op (op (op y y) (op (op x z) x)) y) = x := by
 by_cases h1 : x = z
 ·
  subst x
  simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *]
 ·
  by_cases h4 : tg x = 2
  ·
   obtain ⟨v2, v3, rfl⟩ := tg_J _ h4
   by_cases h6 : tg v2 = 0
   ·
    obtain ⟨v5, rfl⟩ := tg_S _ h6
    by_cases h9 : tg v3 = 2
    ·
     obtain ⟨v7, v8, rfl⟩ := tg_J _ h9
     by_cases h10 : v5 = z
     ·
      subst v5
      by_cases h13 : tg v8 = 2
      ·
       obtain ⟨v11, v12, rfl⟩ := tg_J _ h13
       by_cases h15 : tg v11 = 0
       ·
        obtain ⟨v14, rfl⟩ := tg_S _ h15
        by_cases h18 : tg v12 = 2
        ·
         obtain ⟨v16, v17, rfl⟩ := tg_J _ h18
         simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h1]
        ·
         simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h1]
       ·
        simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h1]
      ·
       simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h1]
     ·
      simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h1, Ne.symm h10]
    ·
     simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h1]
   ·
    simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h1]
  ·
   by_cases h20 : tg x = 0
   ·
    obtain ⟨v19, rfl⟩ := tg_S _ h20
    by_cases h23 : tg z = 2
    ·
     obtain ⟨v21, v22, rfl⟩ := tg_J _ h23
     simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h1]
    ·
     simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h1]
   ·
    simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h1]

theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  exact absurd (h (M.g 0) (M.g 1) (M.g 2)) (by decide)

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
