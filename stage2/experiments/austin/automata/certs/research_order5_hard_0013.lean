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
  | .g _ => 0
  | .J _ _ => 1

def a1 : M → M
  | .J x _ => x
  | t => t

def a2 : M → M
  | .J _ x => x
  | t => t

def sz : M → Nat
  | .g _ => 1
  | .J b0 b1 => sz b0 + sz b1 + 1

def op (u v : M) : M :=
  if tg v = 1 ∧ u = (a1 v) ∧ tg (a2 v) = 1 ∧ u = (a1 (a2 v)) ∧ tg (a2 (a2 v)) = 1 ∧ u = (a1 (a2 (a2 v))) ∧ u = (a2 (a2 (a2 v))) then (M.J u (M.J u (M.J u (M.J u u)))) else if tg v = 1 ∧ u = (a1 v) ∧ tg (a2 v) = 1 ∧ tg (a2 (a2 v)) = 1 ∧ u = (a1 (a2 (a2 v))) then (a1 (a2 v)) else M.J u v

def inst : Magma M := { op := op }

theorem eqf (a b : M) (h : sz a ≠ sz b) : (a = b) = False := eq_false (fun e => h (congrArg sz e))

theorem tg_g (t : M) (h : tg t = 0) : ∃ n, t = M.g n := by cases t <;> simp_all [tg]
theorem tg_J (t : M) (h : tg t = 1) : ∃ b0 b1, t = M.J b0 b1 := by cases t <;> simp_all [tg]
theorem tg_range (t : M) : tg t < 2 := by cases t <;> simp [tg]
@[simp] theorem tg_g_eq (n : Nat) : tg (M.g n) = 0 := rfl
@[simp] theorem tg_J_eq (b0 b1 : M) : tg (M.J b0 b1) = 1 := rfl
@[simp] theorem a1_J_eq (b0 b1 : M) : a1 (M.J b0 b1) = b0 := rfl
@[simp] theorem a2_J_eq (b0 b1 : M) : a2 (M.J b0 b1) = b1 := rfl

theorem law (x y z : M) : (op y (op y (op x (op y (op z y))))) = x := by
 by_cases h3 : tg y = 1
 ·
  obtain ⟨v1, v2, rfl⟩ := tg_J _ h3
  by_cases h6 : tg v2 = 1
  ·
   obtain ⟨v4, v5, rfl⟩ := tg_J _ h6
   by_cases h9 : tg v5 = 1
   ·
    obtain ⟨v7, v8, rfl⟩ := tg_J _ h9
    by_cases h10 : z = v1
    ·
     subst z
     by_cases h11 : v1 = v4
     ·
      subst v1
      by_cases h12 : v4 = v7
      ·
       subst v4
       by_cases h13 : v7 = v8
       ·
        subst v7
        by_cases h14 : x = (J v8 (J v8 (J v8 v8)))
        ·
         subst x
         simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *]
        ·
         simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h14]
       ·
        by_cases h17 : tg v7 = 1
        ·
         obtain ⟨v15, v16, rfl⟩ := tg_J _ h17
         by_cases h20 : tg v16 = 1
         ·
          obtain ⟨v18, v19, rfl⟩ := tg_J _ h20
          by_cases h23 : tg v19 = 1
          ·
           obtain ⟨v21, v22, rfl⟩ := tg_J _ h23
           by_cases h24 : x = (J (J v15 (J v18 (J v21 v22))) (J (J v15 (J v18 (J v21 v22))) (J (J v15 (J v18 (J v21 v22))) v8)))
           ·
            subst x
            simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h13]
           ·
            simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h13, Ne.symm h24]
          ·
           by_cases h25 : x = (J (J v15 (J v18 v19)) (J (J v15 (J v18 v19)) (J (J v15 (J v18 v19)) v8)))
           ·
            subst x
            simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h13]
           ·
            simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h13, Ne.symm h25]
         ·
          by_cases h26 : (J (J v15 v16) (J (J v15 v16) (J (J v15 v16) v8))) = x
          ·
           subst x
           simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h13]
          ·
           simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h13, Ne.symm h26]
        ·
         by_cases h27 : (J v7 (J v7 (J v7 v8))) = x
         ·
          subst x
          simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h13]
         ·
          simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h13, Ne.symm h27]
      ·
       by_cases h28 : x = (J v4 (J v4 (J v7 v8)))
       ·
        subst x
        simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h12]
       ·
        simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h12, Ne.symm h28]
     ·
      by_cases h29 : v1 = v7
      ·
       subst v1
       by_cases h32 : tg v4 = 1
       ·
        obtain ⟨v30, v31, rfl⟩ := tg_J _ h32
        by_cases h35 : tg v31 = 1
        ·
         obtain ⟨v33, v34, rfl⟩ := tg_J _ h35
         by_cases h38 : tg v34 = 1
         ·
          obtain ⟨v36, v37, rfl⟩ := tg_J _ h38
          by_cases h39 : x = (J v7 (J (J v30 (J v33 (J v36 v37))) (J v7 v8)))
          ·
           subst x
           simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h11]
          ·
           simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h11, Ne.symm h39]
         ·
          by_cases h40 : x = (J v7 (J (J v30 (J v33 v34)) (J v7 v8)))
          ·
           subst x
           simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h11]
          ·
           simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h11, Ne.symm h40]
        ·
         by_cases h41 : (J v7 (J (J v30 v31) (J v7 v8))) = x
         ·
          subst x
          simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h11]
         ·
          simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h11, Ne.symm h41]
       ·
        by_cases h42 : (J v7 (J v4 (J v7 v8))) = x
        ·
         subst x
         simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h11]
        ·
         simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h11, Ne.symm h42]
      ·
       by_cases h43 : x = (J v1 (J v4 (J v7 v8)))
       ·
        subst x
        simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h11, Ne.symm h29]
       ·
        simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h11, Ne.symm h29, Ne.symm h43]
    ·
     by_cases h44 : (J v1 (J v4 (J v7 v8))) = z
     ·
      subst z
      by_cases h45 : x = (J v1 (J v4 (J v7 v8)))
      ·
       subst x
       simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h10]
      ·
       simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h10, Ne.symm h45]
     ·
      by_cases h46 : x = (J v1 (J v4 (J v7 v8)))
      ·
       subst x
       simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h10, Ne.symm h44]
      ·
       simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h10, Ne.symm h44, Ne.symm h46]
   ·
    by_cases h47 : (J v1 (J v4 v5)) = z
    ·
     subst z
     by_cases h48 : x = (J v1 (J v4 v5))
     ·
      subst x
      simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *]
     ·
      simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h48]
    ·
     by_cases h49 : x = (J v1 (J v4 v5))
     ·
      subst x
      simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h47]
     ·
      simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h47, Ne.symm h49]
  ·
   by_cases h50 : x = (J v1 v2)
   ·
    subst x
    by_cases h51 : (J v1 v2) = z
    ·
     subst z
     simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *]
    ·
     simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h51]
   ·
    simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h50]
 ·
  by_cases h52 : y = x
  ·
   subst y
   by_cases h53 : x = z
   ·
    subst x
    simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *]
   ·
    simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h53]
  ·
   simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h52]

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
