import JudgeProblem
set_option linter.unusedSimpArgs false
set_option linter.unusedVariables false
set_option warn.classDefReducibility false

inductive submission.M : Type where
  | g : Nat → submission.M
  | J : submission.M → submission.M → submission.M
  | E : submission.M → submission.M → submission.M
  deriving DecidableEq

namespace submission
open M

def tg : M → Nat
  | .g _ => 1
  | .J _ _ => 2
  | .E _ _ => 3
def a1 : M → M
  | .J x _ => x
  | .E x _ => x
  | t => t
def a2 : M → M
  | .J _ x => x
  | .E _ x => x
  | t => t
def sz : M → Nat
  | .g _ => 1
  | .J b0 b1 => sz b0 + sz b1 + 1
  | .E b0 b1 => sz b0 + sz b1 + 1

@[simp] theorem tgg (n : Nat) : tg (g n) = 1 := rfl
@[simp] theorem tgJ (a b : M) : tg (J a b) = 2 := rfl
@[simp] theorem tgE (a b : M) : tg (E a b) = 3 := rfl
@[simp] theorem q1J (a b : M) : a1 (J a b) = a := rfl
@[simp] theorem q2J (a b : M) : a2 (J a b) = b := rfl
@[simp] theorem q1E (a b : M) : a1 (E a b) = a := rfl
@[simp] theorem q2E (a b : M) : a2 (E a b) = b := rfl
@[simp] theorem q1g (n : Nat) : a1 (g n) = g n := rfl
@[simp] theorem q2g (n : Nat) : a2 (g n) = g n := rfl
@[simp] theorem szg (n : Nat) : sz (g n) = 1 := rfl
@[simp] theorem szJ (a b : M) : sz (J a b) = sz a + sz b + 1 := rfl
@[simp] theorem szE (a b : M) : sz (E a b) = sz a + sz b + 1 := rfl

theorem szp (t : M) : 1 ≤ sz t := by cases t <;> simp [sz] <;> omega
theorem s1 (t : M) : sz (a1 t) ≤ sz t := by cases t <;> simp [a1, sz] <;> omega
theorem s2 (t : M) : sz (a2 t) ≤ sz t := by cases t <;> simp [a2, sz] <;> omega
theorem st (t : M) (h : tg t ≠ 1) : sz t = sz (a1 t) + sz (a2 t) + 1 := by
  cases t <;> simp_all [tg, a1, a2, sz]
theorem s1l (t : M) (h : tg t ≠ 1) : sz (a1 t) < sz t := by
  have := st t h; have := szp (a2 t); omega
theorem s2l (t : M) (h : tg t ≠ 1) : sz (a2 t) < sz t := by
  have := st t h; have := szp (a1 t); omega

def D (u v : M) : Prop :=
  (tg v = 2 ∧ a2 v = u ∧ tg (a1 v) = 3 ∧ a2 (a2 (a1 v)) = u) ∨
  (tg v = 2 ∧ a2 v = u ∧ tg (a1 v) = 2 ∧ tg (a2 (a1 v)) = 2 ∧ a2 (a2 (a1 v)) = u) ∨
  (tg v = 3 ∧ a2 v = u ∧ tg (a1 v) = 2) ∨
  (tg u ≠ 1 ∧ a1 (a1 u) = a2 u ∧ tg v = 2 ∧ a2 v = u ∧ a2 (a1 v) = a2 u)
instance (u v : M) : Decidable (D u v) := by unfold D; infer_instance
def Q (v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ a2 (a1 v) = a2 v
instance (v : M) : Decidable (Q v) := by unfold Q; infer_instance
def W (u v : M) : Prop := tg u ≠ 1 ∧ a1 (a1 u) = a2 u ∧ tg v = 2 ∧ a2 v = u
instance (u v : M) : Decidable (W u v) := by unfold W; infer_instance

def op (u v : M) : M :=
  let r := if h : sz (a2 (a2 u)) + sz (a2 u) < sz u + sz v then op (a2 (a2 u)) (a2 u) else u
  if D u v then a1 (a1 v)
  else if Q v then E u v
  else if W u v ∧ r = a1 v then a2 (a2 u)
  else J u v
termination_by sz u + sz v
decreasing_by exact h

def inst : Magma M := { op := op }

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 0) (g 0) (g 0)
  revert this
  change ¬ g 0 = op (op (g 0) (g 0)) (op (op (g 0) (op (g 0) (g 0))) (g 0))
  simp (config := {decide := true}) [op.eq_1, sz, D, Q, W]

theorem oc (u v : M) : ∃ r : M,
    r = (if h : sz (a2 (a2 u)) + sz (a2 u) < sz u + sz v then op (a2 (a2 u)) (a2 u) else u) ∧
    op u v = (
      if D u v then a1 (a1 v)
      else if Q v then E u v
      else if W u v ∧ r = a1 v then a2 (a2 u)
      else J u v) :=
  ⟨_, rfl, op.eq_1 u v⟩

theorem Dv {u v : M} (h : D u v) : a2 v = u := by
  rcases h with h|h|h|h
  · exact h.2.1
  · exact h.2.1
  · exact h.2.1
  · exact h.2.2.2.1
theorem Dt {u v : M} (h : D u v) : tg v ≠ 1 := by
  rcases h with h|h|h|h
  · rw [h.1]; omega
  · rw [h.1]; omega
  · rw [h.1]; omega
  · rw [h.2.2.1]; omega
theorem Wv {u v : M} (h : W u v) : a2 v = u := h.2.2.2
theorem Wt {u v : M} (h : W u v) : tg v ≠ 1 := by rw [h.2.2.1]; omega

theorem gt {u v : M} (h : W u v) : sz (a2 (a2 u)) + sz (a2 u) < sz u + sz v := by
  have e1 := s2 (a2 u)
  have e2 := s2l u h.1
  have e3 := s2l v (Wt h)
  rw [h.2.2.2] at e3
  omega

theorem QD {u v : M} (hq : Q v) : ¬ D u v := by
  intro h
  rcases h with h|h|h|h
  · have e := h.2.2.1; rw [hq.2.1] at e; omega
  · have e : a2 (a1 v) = u := by rw [hq.2.2]; exact h.2.1
    have t := h.2.2.2.1
    have p := h.2.2.2.2
    rw [e] at t p
    have := s2l u (by rw [t]; omega)
    rw [p] at this; omega
  · have e := h.1; rw [hq.1] at e; omega
  · have e : a2 (a1 v) = u := by rw [hq.2.2]; exact h.2.2.2.1
    have p := h.2.2.2.2
    rw [e] at p
    have := s2l u h.1
    rw [← p] at this; omega

theorem DE {u v : M} (h : D u v) : op u v = a1 (a1 v) := by
  obtain ⟨r, -, hop⟩ := oc u v; rw [hop, if_pos h]

theorem QEE {v : M} (hq : Q v) (u : M) : op u v = E u v := by
  obtain ⟨r, -, hop⟩ := oc u v; rw [hop, if_neg (QD hq), if_pos hq]

theorem F0 {u v : M} (h1 : ¬ D u v) (h3 : ¬ Q v) (h2 : ¬ W u v) : op u v = J u v := by
  obtain ⟨r, -, hop⟩ := oc u v
  rw [hop, if_neg h1, if_neg h3, if_neg (fun k => h2 k.1)]

theorem FR {u v : M} (h3 : ¬ Q v) (h : a2 v ≠ u) : op u v = J u v :=
  F0 (fun k => h (Dv k)) h3 (fun k => h (Wv k))

theorem WE {u v : M} (h1 : ¬ D u v) (h3 : ¬ Q v) (h : W u v)
    (h2 : op (a2 (a2 u)) (a2 u) = a1 v) : op u v = a2 (a2 u) := by
  obtain ⟨r, hr, hop⟩ := oc u v
  rw [dif_pos (gt h)] at hr
  subst hr
  rw [hop, if_neg h1, if_neg h3, if_pos ⟨h, h2⟩]

theorem TR (u v : M) : op u v = J u v ∨ (Q v ∧ op u v = E u v) ∨ (D u v ∧ op u v = a1 (a1 v))
    ∨ (W u v ∧ op (a2 (a2 u)) (a2 u) = a1 v ∧ op u v = a2 (a2 u)) := by
  by_cases h1 : D u v
  · exact Or.inr (Or.inr (Or.inl ⟨h1, DE h1⟩))
  · by_cases h3 : Q v
    · exact Or.inr (Or.inl ⟨h3, QEE h3 u⟩)
    · by_cases h2 : W u v
      · obtain ⟨r, hr, hop⟩ := oc u v
        rw [dif_pos (gt h2)] at hr
        subst hr
        by_cases h4 : op (a2 (a2 u)) (a2 u) = a1 v
        · refine Or.inr (Or.inr (Or.inr ⟨h2, h4, ?_⟩))
          rw [hop, if_neg h1, if_neg h3, if_pos ⟨h2, h4⟩]
        · left; rw [hop, if_neg h1, if_neg h3, if_neg (fun k => h4 k.2)]
      · left; exact F0 h1 h3 h2

theorem NF (u v : M) : op u v = J u v ∨ (Q v ∧ op u v = E u v)
    ∨ (tg v ≠ 1 ∧ a2 v = u ∧ sz (op u v) < sz v) := by
  rcases TR u v with h | h | ⟨h1, h2⟩ | ⟨h1, -, h2⟩
  · exact Or.inl h
  · exact Or.inr (Or.inl h)
  · refine Or.inr (Or.inr ⟨Dt h1, Dv h1, ?_⟩)
    rw [h2]; have := s1 (a1 v); have := s1l v (Dt h1); omega
  · refine Or.inr (Or.inr ⟨Wt h1, Wv h1, ?_⟩)
    rw [h2]
    have e1 := s2 (a2 u); have e2 := s2 u
    have e3 := s2l v (Wt h1); rw [Wv h1] at e3; omega

theorem d1 {u v : M} (h1 : tg v = 2) (h2 : a2 v = u) (h3 : tg (a1 v) = 3)
    (h4 : a2 (a2 (a1 v)) = u) : D u v := Or.inl ⟨h1, h2, h3, h4⟩
theorem d4 {u v : M} (h1 : tg v = 2) (h2 : a2 v = u) (h3 : tg (a1 v) = 2)
    (h4 : tg (a2 (a1 v)) = 2) (h5 : a2 (a2 (a1 v)) = u) : D u v :=
  Or.inr (Or.inl ⟨h1, h2, h3, h4, h5⟩)
theorem d3 {u v : M} (h1 : tg v = 3) (h2 : a2 v = u) (h3 : tg (a1 v) = 2) : D u v :=
  Or.inr (Or.inr (Or.inl ⟨h1, h2, h3⟩))
theorem d5 {u v : M} (h1 : tg u ≠ 1) (h2 : a1 (a1 u) = a2 u) (h3 : tg v = 2) (h4 : a2 v = u)
    (h5 : a2 (a1 v) = a2 u) : D u v := Or.inr (Or.inr (Or.inr ⟨h1, h2, h3, h4, h5⟩))

/-- nothing fires on an `E`-term whose head is itself an `E`-term -/
theorem FE (u a b : M) (h : tg a ≠ 2) : op u (E a b) = J u (E a b) := by
  refine F0 (fun k => ?_) (fun k => ?_) (fun k => ?_)
  · rcases k with k|k|k|k
    · exact absurd k.1 (by simp)
    · exact absurd k.1 (by simp)
    · exact h (by simpa using k.2.2)
    · exact absurd k.2.2.1 (by simp)
  · exact absurd k.1 (by simp)
  · exact absurd k.2.2.1 (by simp)

/-- `a1` of any product is bounded by one of the two arguments -/
theorem A1L (u v : M) : sz (a1 (op u v)) ≤ sz u ∨ sz (a1 (op u v)) < sz v := by
  rcases NF u v with h | ⟨-, h⟩ | ⟨-, -, h⟩
  · left; rw [h]; simp
  · left; rw [h]; simp
  · right; have := s1 (op u v); omega

theorem CORE {x y z : M} (hq : ¬ Q y) (hty : tg y ≠ 1) (hzy : a2 y = z)
    (hsA : sz (op z y) < sz y)
    (hbad : a1 (a1 y) = a2 y → op (op z y) y = J (op z y) y → False)
    (hsd : a2 y = op z y → a1 (a1 y) = a2 y) :
    op y (op (op x (op (op z y) y)) y) = x := by
  have hzs : sz z < sz y := by rw [← hzy]; exact s2l y hty
  rcases NF (op z y) y with hB | ⟨hqy, -⟩ | ⟨-, hAy, hsB⟩
  · rw [hB]
    have hnQB : ¬ Q (J (op z y) y) := by
      intro k
      have e := k.2.2
      simp only [q1J, q2J] at e
      have := congrArg sz e
      have := s2 (op z y); omega
    rcases TR x (J (op z y) y) with hC | ⟨hqB, -⟩ | ⟨hdC, hC⟩ | ⟨hwC, -, hC⟩
    · rw [hC]
      have hD : op (J x (J (op z y) y)) y = J (J x (J (op z y) y)) y := by
        refine FR hq (fun k => ?_)
        have e := congrArg sz k
        simp only [szJ] at e
        have := s2 y; have := szp x; omega
      rw [hD]
      exact DE (d4 rfl rfl rfl rfl rfl)
    · exact absurd hqB hnQB
    · exfalso
      have hx : y = x := by have := Dv hdC; simpa using this
      rcases hdC with k|k|k|k
      · have e := k.2.2.2
        simp only [q1J] at e
        rw [← hx] at e
        have := congrArg sz e
        have := s2 (a2 (op z y)); have := s2 (op z y); omega
      · have e := k.2.2.2.2
        simp only [q1J] at e
        rw [← hx] at e
        have := congrArg sz e
        have := s2 (a2 (op z y)); have := s2 (op z y); omega
      · exact absurd k.1 (by simp)
      · exact hbad (by rw [← hx] at k; exact k.2.1) hB
    · exfalso
      have hx : y = x := by have := Wv hwC; simpa using this
      exact hbad (by rw [← hx] at hwC; exact hwC.2.1) hB
  · exact absurd hqy hq
  · have hA2 : op z y = z := hAy.symm.trans hzy
    have hyy : a1 (a1 y) = a2 y := hsd hAy
    rw [hA2, hA2]
    rcases NF x z with hC | ⟨-, hC⟩ | ⟨htz, hxz, hsC⟩
    · rw [hC]
      have hD : op (J x z) y = J (J x z) y := by
        refine FR hq (fun k => ?_)
        rw [hzy] at k
        have e := congrArg sz k
        simp only [szJ] at e
        have := szp x; omega
      rw [hD]
      exact DE (d5 hty hyy rfl rfl (by simpa using hzy.symm))
    · rw [hC]
      have hD : op (E x z) y = J (E x z) y := by
        refine FR hq (fun k => ?_)
        rw [hzy] at k
        have e := congrArg sz k
        simp only [szE] at e
        have := szp x; omega
      rw [hD]
      exact DE (d5 hty hyy rfl rfl (by simpa using hzy.symm))
    · have hne : a2 y ≠ op x z := by rw [hzy]; intro k; rw [← k] at hsC; omega
      have hD : op (op x z) y = J (op x z) y := FR hq hne
      rw [hD]
      have hs1 : sz (op x z) < sz y := by omega
      have hnD : ¬ D y (J (op x z) y) := by
        intro k
        rcases k with k|k|k|k
        · have e := k.2.2.2
          simp only [q1J] at e
          have := congrArg sz e
          have := s2 (a2 (op x z)); have := s2 (op x z); omega
        · have e := k.2.2.2.2
          simp only [q1J] at e
          have := congrArg sz e
          have := s2 (a2 (op x z)); have := s2 (op x z); omega
        · exact absurd k.1 (by simp)
        · have e := k.2.2.2.2
          simp only [q1J] at e
          rw [hzy] at e
          have := congrArg sz e
          have := s2 (op x z); omega
      have hnQ : ¬ Q (J (op x z) y) := by
        intro k
        have e := k.2.2
        simp only [q1J, q2J] at e
        have := congrArg sz e
        have := s2 (op x z); omega
      rw [WE hnD hnQ ⟨hty, hyy, rfl, rfl⟩ (by simp only [q1J, q2J]; rw [hzy, hxz])]
      rw [hzy, hxz]

/-- THE LAW: x = y * ((x * ((z * y) * y)) * y) -/
theorem law (x y z : M) : op (y) (op (op (x) (op (op (z) (y)) (y))) (y)) = x := by
  by_cases hq : Q y
  · rw [QEE hq z, QEE hq (E z y), FE x (E z y) y (by simp),
      QEE hq (J x (E (E z y) y))]
    exact DE (d3 rfl rfl rfl)
  · rcases TR z y with hA | ⟨hqy, -⟩ | ⟨hdA, hA⟩ | ⟨hwA, hrA, hA⟩
    · rw [hA]
      have hB : op (J z y) y = J (J z y) y := by
        refine FR hq (fun k => ?_)
        have e := congrArg sz k
        simp only [szJ] at e
        have := s2 y; have := szp z; omega
      rw [hB, QEE ⟨rfl, rfl, rfl⟩ x]
      have hD : op (E x (J (J z y) y)) y = J (E x (J (J z y) y)) y := by
        refine FR hq (fun k => ?_)
        have e := congrArg sz k
        simp only [szJ, szE] at e
        have := s2 y; have := szp x; have := szp z; omega
      rw [hD]
      exact DE (d1 rfl rfl rfl rfl)
    · exact absurd hqy hq
    · have hzy := Dv hdA
      have hty := Dt hdA
      refine CORE hq hty hzy ?_ ?_ ?_
      · rw [hA]; have := s1 (a1 y); have := s1l y hty; omega
      · intro h1 h2
        have hA2 : op z y = z := by rw [hA, h1]; exact hzy
        rw [hA2, hA2] at h2
        have := congrArg sz h2
        simp only [szJ] at this
        have := szp y; omega
      · intro h; exact (h.trans hA).symm
    · have hzy := Wv hwA
      have hty := Wt hwA
      have hzs : sz z < sz y := by rw [← hzy]; exact s2l y hty
      have hz2 : sz (a2 (a2 z)) ≤ sz (a2 z) := s2 (a2 z)
      have hz3 : sz (a2 z) < sz z := s2l z hwA.1
      refine CORE hq hty hzy ?_ ?_ ?_
      · rw [hA]; omega
      · intro h1 _
        rw [hzy] at h1
        rw [← hrA] at h1
        rcases A1L (a2 (a2 z)) (a2 z) with e | e <;> rw [h1] at e <;> omega
      · intro h
        exfalso
        rw [hzy, hA] at h
        have := congrArg sz h
        omega

theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
