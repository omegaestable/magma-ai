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
theorem sz_tg (t : M) (h : tg t = 2) : sz t = sz (a1 t) + sz (a2 t) + 1 := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a1, a2]
@[simp] theorem tg_J_eq (b0 b1 : M) : tg (M.J b0 b1) = 2 := rfl
@[simp] theorem a1_J_eq (b0 b1 : M) : a1 (M.J b0 b1) = b0 := rfl
@[simp] theorem a2_J_eq (b0 b1 : M) : a2 (M.J b0 b1) = b1 := rfl
theorem sz_pos (t : M) : 1 ≤ sz t := by cases t <;> simp [sz] <;> omega
@[simp] theorem sz_J (a b : M) : sz (J a b) = sz a + sz b + 1 := rfl
theorem sz_a1_lt {t : M} (h : tg t = 2) : sz (a1 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a1]; have := sz_pos b; omega
theorem sz_a2_lt {t : M} (h : tg t = 2) : sz (a2 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a2]; have := sz_pos a; omega
theorem szJ {a b c : M} (h : J a b = c) : sz c = sz a + sz b + 1 := by rw [← h]; rfl
theorem J_a12 {t : M} (h : tg t = 2) : t = J (a1 t) (a2 t) := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; rfl
def msr (u v : M) : Nat := max (sz u) (sz v) * max (sz u) (sz v) + sz u + sz v
theorem msr_lt_of_max_lt {a b u v : M} (h : max (sz a) (sz b) < max (sz u) (sz v)) : msr a b < msr u v := by
  unfold msr
  have h1 : sz a + sz b ≤ 2 * max (sz a) (sz b) := by omega
  have h2 : (max (sz a) (sz b) + 1) * (max (sz a) (sz b) + 1) ≤ max (sz u) (sz v) * max (sz u) (sz v) := Nat.mul_le_mul h h
  simp only [Nat.mul_succ, Nat.succ_mul] at h2
  omega
theorem msr_lt_of_max_eq {a b u v : M} (h : max (sz a) (sz b) = max (sz u) (sz v)) (h2 : sz a + sz b < sz u + sz v) : msr a b < msr u v := by
  unfold msr; rw [h]; omega
theorem msr_lt_r {u b v : M} (h : sz b < sz v) : msr u b < msr u v := by
  have hm : max (sz u) (sz b) ≤ max (sz u) (sz v) := by omega
  rcases Nat.lt_or_eq_of_le hm with hlt | heq
  · exact msr_lt_of_max_lt hlt
  · exact msr_lt_of_max_eq heq (by omega)
theorem msr_lt_both {a b u v : M} (ha : sz a < max (sz u) (sz v)) (hb : sz b < max (sz u) (sz v)) : msr a b < msr u v :=
  msr_lt_of_max_lt (by omega)

def Sh (v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ a1 v = a2 (a2 v)
instance (v : M) : Decidable (Sh v) := by unfold Sh; infer_instance

def op (u v : M) : M :=
  let p1 := if hs1 : msr (a1 u) (a2 u) < msr u v then op (a1 u) (a2 u) else J u v
  let p2 := if hs2 : msr (a2 u) (a1 v) < msr u v then op (a2 u) (a1 v) else J u v
  let p3 := if hs3 : msr (a1 (a1 (a2 v))) (a1 v) < msr u v then op (a1 (a1 (a2 v))) (a1 v) else J u v
  let p4 := if hs4 : msr u (a1 (a1 (a1 (a2 v)))) < msr u v then op u (a1 (a1 (a1 (a2 v)))) else J u v
  let p5 := if hs5 : msr u (a2 (a1 (a2 v))) < msr u v then op u (a2 (a1 (a2 v))) else J u v
  let p6 := if hs6 : msr (J (a2 (a1 (a2 v))) (a1 (a2 v))) (a1 v) < msr u v then op (J (a2 (a1 (a2 v))) (a1 (a2 v))) (a1 v) else J u v
  let p7 := if hs7 : msr u (a1 (a2 v)) < msr u v then op u (a1 (a2 v)) else J u v
  let p8 := if hs8 : msr p7 (a1 v) < msr u v then op p7 (a1 v) else J u v
  if Sh v ∧ tg u = 2 ∧ p1 = u ∧ p2 = a1 (a2 v) then a2 u
  else if Sh v ∧ tg (a1 (a2 v)) = 2 ∧ a2 (a1 (a2 v)) = a1 v ∧ p3 = a1 (a2 v) ∧ Sh (a1 (a1 (a2 v))) ∧ p4 = a1 (a2 (a1 (a1 (a2 v)))) then a1 (a1 (a2 v))
  else if Sh v ∧ tg (a1 (a2 v)) = 2 ∧ p5 = a1 (a1 (a2 v)) ∧ p6 = a1 (a2 v) then J (a2 (a1 (a2 v))) (a1 (a2 v))
  else if Sh v ∧ p7 ≠ J u (a1 (a2 v)) ∧ p8 = a1 (a2 v) then p7
  else J u v
termination_by msr u v
decreasing_by all_goals assumption

def inst : Magma M := { op := op }

theorem op_nSh {u v : M} (h : ¬ Sh v) : op u v = J u v := by
  rw [op.eq_1]; simp [h]

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 1) (g 0) (g 2)
  revert this
  change ¬ g 1 = op (op (g 0) (op (op (g 1) (g 1)) (g 0))) (op (g 2) (g 2))
  simp (config := {decide := true}) [op_nSh, Sh]

theorem op_cases (u v : M) : ∃ p1 p2 p3 p4 p5 p6 p7 p8 : M,
    p1 = (if hs1 : msr (a1 u) (a2 u) < msr u v then op (a1 u) (a2 u) else J u v) ∧
    p2 = (if hs2 : msr (a2 u) (a1 v) < msr u v then op (a2 u) (a1 v) else J u v) ∧
    p3 = (if hs3 : msr (a1 (a1 (a2 v))) (a1 v) < msr u v then op (a1 (a1 (a2 v))) (a1 v) else J u v) ∧
    p4 = (if hs4 : msr u (a1 (a1 (a1 (a2 v)))) < msr u v then op u (a1 (a1 (a1 (a2 v)))) else J u v) ∧
    p5 = (if hs5 : msr u (a2 (a1 (a2 v))) < msr u v then op u (a2 (a1 (a2 v))) else J u v) ∧
    p6 = (if hs6 : msr (J (a2 (a1 (a2 v))) (a1 (a2 v))) (a1 v) < msr u v then op (J (a2 (a1 (a2 v))) (a1 (a2 v))) (a1 v) else J u v) ∧
    p7 = (if hs7 : msr u (a1 (a2 v)) < msr u v then op u (a1 (a2 v)) else J u v) ∧
    p8 = (if hs8 : msr p7 (a1 v) < msr u v then op p7 (a1 v) else J u v) ∧
    op u v = (
  if Sh v ∧ tg u = 2 ∧ p1 = u ∧ p2 = a1 (a2 v) then a2 u
  else if Sh v ∧ tg (a1 (a2 v)) = 2 ∧ a2 (a1 (a2 v)) = a1 v ∧ p3 = a1 (a2 v) ∧ Sh (a1 (a1 (a2 v))) ∧ p4 = a1 (a2 (a1 (a1 (a2 v)))) then a1 (a1 (a2 v))
  else if Sh v ∧ tg (a1 (a2 v)) = 2 ∧ p5 = a1 (a1 (a2 v)) ∧ p6 = a1 (a2 v) then J (a2 (a1 (a2 v))) (a1 (a2 v))
  else if Sh v ∧ p7 ≠ J u (a1 (a2 v)) ∧ p8 = a1 (a2 v) then p7
  else J u v) :=
  ⟨_, _, _, _, _, _, _, _, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, op.eq_1 u v⟩

/-- Enc a w : w encodes a, i.e. w = J w1 (J (op a w1) w1). -/
def Enc (a w : M) : Prop := Sh w ∧ op a (a1 w) = a1 (a2 w)
/-- RF u x : u = op y x for some y. -/
def RF (u x : M) : Prop := (tg u = 2 ∧ a2 u = x ∧ op (a1 u) (a2 u) = u) ∨ Enc u x

theorem Sh_sz {v : M} (h : Sh v) : sz v = sz (a1 v) + sz (a1 (a2 v)) + sz (a1 v) + 2 := by
  obtain ⟨h1, h2, h3⟩ := h
  have := sz_tg v h1; have := sz_tg _ h2; rw [← h3] at *; omega
theorem g1 {u v : M} (h : tg u = 2) : msr (a1 u) (a2 u) < msr u v :=
  msr_lt_both (by have := sz_a1_lt h; omega) (by have := sz_a2_lt h; omega)
theorem g2 {u v : M} (hu : tg u = 2) (hv : Sh v) : msr (a2 u) (a1 v) < msr u v :=
  msr_lt_both (by have := sz_a2_lt hu; omega) (by have := sz_a1_lt hv.1; omega)
theorem g3 {u v : M} (h : Sh v) : msr (a1 (a1 (a2 v))) (a1 v) < msr u v :=
  msr_lt_both (by have := sz_a1 (a1 (a2 v)); have := sz_a1_lt h.2.1; have := sz_a2_lt h.1; omega) (by have := sz_a1_lt h.1; omega)
theorem g4 {u v : M} (h : Sh v) : msr u (a1 (a1 (a1 (a2 v)))) < msr u v :=
  msr_lt_r (by have := sz_a1 (a1 (a1 (a2 v))); have := sz_a1 (a1 (a2 v)); have := sz_a1_lt h.2.1; have := sz_a2_lt h.1; omega)
theorem g5 {u v : M} (h : Sh v) : msr u (a2 (a1 (a2 v))) < msr u v :=
  msr_lt_r (by have := sz_a2 (a1 (a2 v)); have := sz_a1_lt h.2.1; have := sz_a2_lt h.1; omega)
theorem g7 {u v : M} (h : Sh v) : msr u (a1 (a2 v)) < msr u v :=
  msr_lt_r (by have := sz_a1_lt h.2.1; have := sz_a2_lt h.1; omega)
theorem nJv {u v : M} (h : Sh v) (e : J u v = a1 (a2 v)) : False := by
  have := szJ e; have := sz_a1_lt h.2.1; have := sz_a2_lt h.1; omega

/-- SOUNDNESS: a non-free product is a decoding. -/
theorem SND (u v : M) (h : op u v ≠ J u v) : Enc (op u v) v ∧ RF u (op u v) := by
  obtain ⟨p1, p2, p3, p4, p5, p6, p7, p8, hp1, hp2, hp3, hp4, hp5, hp6, hp7, hp8, hop⟩ := op_cases u v
  rw [hop] at h ⊢
  split
  · rename_i hg
    obtain ⟨hsh, htu, e1, e2⟩ := hg
    rw [dif_pos (g1 htu)] at hp1; rw [dif_pos (g2 htu hsh)] at hp2; subst hp1; subst hp2
    exact ⟨⟨hsh, e2⟩, Or.inl ⟨htu, rfl, e1⟩⟩
  · split
    · rename_i hg1 hg
      obtain ⟨hsh, htb, e0, e3, hshb, e4⟩ := hg
      rw [dif_pos (g3 hsh)] at hp3; rw [dif_pos (g4 hsh)] at hp4; subst hp3; subst hp4
      exact ⟨⟨hsh, e3⟩, Or.inr ⟨hshb, e4⟩⟩
    · split
      · rename_i hg1 hg2 hg
        obtain ⟨hsh, htb, e5, e6⟩ := hg
        rw [dif_pos (g5 hsh)] at hp5; subst hp5
        by_cases hs6 : msr (J (a2 (a1 (a2 v))) (a1 (a2 v))) (a1 v) < msr u v
        · rw [dif_pos hs6] at hp6; subst hp6
          exact ⟨⟨hsh, e6⟩, Or.inr ⟨⟨rfl, htb, rfl⟩, e5⟩⟩
        · rw [dif_neg hs6] at hp6; subst hp6; exact (nJv hsh e6).elim
      · split
        · rename_i hg1 hg2 hg3 hg
          obtain ⟨hsh, e7, e8⟩ := hg
          rw [dif_pos (g7 hsh)] at hp7; subst hp7
          by_cases hs8 : msr (op u (a1 (a2 v))) (a1 v) < msr u v
          · rw [dif_pos hs8] at hp8; subst hp8
            exact ⟨⟨hsh, e8⟩, (SND u (a1 (a2 v)) e7).2⟩
          · rw [dif_neg hs8] at hp8; subst hp8; exact (nJv hsh e8).elim
        · rename_i hg1 hg2 hg3 hg4
          rw [if_neg hg1, if_neg hg2, if_neg hg3, if_neg hg4] at h
          exact absurd rfl h
termination_by msr u v
decreasing_by exact g7 hsh

theorem opD (a b : M) : op a b = J a b ∨ (Enc (op a b) b ∧ RF a (op a b)) := by
  by_cases h : op a b = J a b
  · exact Or.inl h
  · exact Or.inr (SND a b h)

/-- A: the encoded term's payload is smaller than the encoding. -/
theorem encA (n : Nat) : ∀ a w, sz w ≤ n → Enc a w → sz (a2 a) < sz w := by
  induction n with
  | zero => intro a w h _; have := sz_pos w; omega
  | succ n ih =>
    intro a w hn he0
    obtain ⟨hsh, he⟩ := he0
    have s1 := sz_tg w hsh.1
    have s2 := sz_tg _ hsh.2.1
    have s4 := sz_a2 a
    rcases opD a (a1 w) with hf | ⟨-, hrf⟩
    · rw [hf] at he; have := szJ he; omega
    · rcases hrf with ⟨-, hx, -⟩ | henc
      · rw [hx, he]; omega
      · have := ih a (op a (a1 w)) (by rw [he]; omega) henc
        rw [he] at this; omega
theorem encA' {a w : M} (h : Enc a w) : sz (a2 a) < sz w := encA _ a w (Nat.le_refl _) h

theorem encB (a : M) : ¬ Enc a a := by
  intro h0
  obtain ⟨hsh, he⟩ := h0
  have s1 := sz_tg a hsh.1
  have s2 := sz_tg _ hsh.2.1
  rcases opD a (a1 a) with hf | ⟨-, hrf⟩
  · rw [hf] at he; have := szJ he; omega
  · rcases hrf with ⟨-, hx, -⟩ | henc
    · rw [he] at hx; have := congrArg sz hx; omega
    · have := encA' henc; rw [he] at this; omega

theorem opB (a b : M) : op a b ≠ b := by
  intro h
  rcases opD a b with hf | ⟨he, -⟩
  · rw [hf] at h; have := szJ h; omega
  · rw [h] at he; exact encB b he

theorem Q (p : M) : op p (a2 p) ≠ a1 p := by
  intro h
  have sp := sz_a1 p
  rcases opD p (a2 p) with hf | ⟨he, hr⟩
  · rw [hf] at h; have := szJ h; omega
  · rw [h] at he hr
    rcases hr with ⟨-, hx, -⟩ | henc
    · rw [hx] at he; exact encB _ he
    · have hA := encA' henc
      obtain ⟨⟨ht1, ht1', ha1⟩, ho1⟩ := henc
      obtain ⟨⟨ht2, ht2', ha2⟩, ho2⟩ := he
      have s1 := sz_tg _ ht1; have s1' := sz_tg _ ht1'; have s2 := sz_tg _ ht2; have s2' := sz_tg _ ht2'
      have F1 : sz (a2 p) < sz (a2 (a1 p)) := by
        rcases opD p (a1 (a1 p)) with hf | ⟨-, hr'⟩
        · rw [hf] at ho1; have := szJ ho1; omega
        · rw [ho1] at hr'
          rcases hr' with ⟨-, hx', -⟩ | henc'
          · have := congrArg sz hx'; omega
          · have := encA' henc'; omega
      have F2 : sz (a2 (a1 p)) < sz (a2 p) := by
        rcases opD (a1 p) (a1 (a2 p)) with hf | ⟨-, hr'⟩
        · rw [hf] at ho2; have := szJ ho2; omega
        · rw [ho2] at hr'
          rcases hr' with ⟨-, hx', -⟩ | henc'
          · have := congrArg sz hx'; omega
          · have := encA' henc'; omega
      omega

theorem Q2 (u w : M) : op u w ≠ a2 w := by
  intro h
  rcases opD u w with hf | ⟨he, -⟩
  · rw [hf] at h; have := szJ h; have := sz_a2 w; omega
  · rw [h] at he; obtain ⟨⟨-, -, ha⟩, ho⟩ := he; rw [ha] at ho; exact Q _ ho

theorem encD (n : Nat) : ∀ u w, sz w ≤ n → tg u = 2 → op u w ≠ op (a2 u) w := by
  induction n with
  | zero => intro u w h _ _; have := sz_pos w; omega
  | succ n ih =>
    intro u w hn htu heq
    have su := sz_tg u htu
    have := sz_pos (a1 u)
    rcases opD u w with hf1 | ⟨he1, hr1⟩ <;> rcases opD (a2 u) w with hf2 | ⟨he2, hr2⟩
    · rw [hf1, hf2] at heq; have := (M.J.inj heq).1; have := congrArg sz this; omega
    · rw [← heq, hf1] at he2; have := encA' he2; simp only [a2_J_eq] at this; omega
    · rw [heq, hf2] at he1; have := encA' he1; simp only [a2_J_eq] at this; omega
    · rw [heq] at he1 hr1
      have hA := encA' he1
      rcases hr1 with ⟨-, hx1, -⟩ | henc1 <;> rcases hr2 with ⟨ht2, hx2, -⟩ | henc2
      · rw [← hx1] at hx2; have := sz_a2_lt ht2; rw [hx2] at this; omega
      · rw [← hx1] at henc2; exact encB _ henc2
      · have := encA' henc1; have := sz_a2_lt ht2; rw [hx2] at this; omega
      · obtain ⟨⟨-, ht, ha⟩, ho1⟩ := henc1
        obtain ⟨-, ho2⟩ := henc2
        have s := sz_tg _ ht
        rw [← ho2] at ho1
        exact ih u (a1 (op (a2 u) w)) (by rw [ha]; omega) htu ho1

theorem encF (n : Nat) : ∀ a b w, sz w ≤ n → Enc a b → op a w ≠ op b w := by
  induction n with
  | zero => intro a b w h _ _; have := sz_pos w; omega
  | succ n ih =>
    intro a b w hn hab heq
    have hAb := encA' hab
    rcases opD a w with hf1 | ⟨he1, hr1⟩ <;> rcases opD b w with hf2 | ⟨he2, hr2⟩
    · rw [hf1, hf2] at heq; rw [(M.J.inj heq).1] at hab; exact encB _ hab
    · rw [← heq, hf1] at he2; have := encA' he2; simp only [a2_J_eq] at this; omega
    · rw [heq, hf2] at he1; have := encA' he1; simp only [a2_J_eq] at this; omega
    · rw [heq] at he1 hr1
      have hA := encA' he1
      obtain ⟨⟨htb, htb2, hab2⟩, hob⟩ := hab
      have sb := sz_tg b htb; have sb2 := sz_tg _ htb2
      rcases hr1 with ⟨hta, hx1, -⟩ | henc1 <;> rcases hr2 with ⟨htb', hx2, -⟩ | henc2
      · have sa := sz_tg a hta
        have hc : sz (op b w) < sz a := by rw [← hx1]; have := sz_pos (a1 a); omega
        rw [hx2] at hab2 hob sb2; rw [hab2] at hob
        rcases opD a (a2 (op b w)) with hf | ⟨-, hr⟩
        · rw [hf] at hob; have := szJ hob; omega
        · rw [hob] at hr
          rcases hr with ⟨-, hx, -⟩ | henc
          · rw [hx1] at hx; have := congrArg sz hx; omega
          · have := encA' henc; rw [hx1] at this; omega
      · have := encA' henc2
        have sa := sz_tg a hta
        rw [hx1] at sa
        rcases opD a (a1 b) with hf | ⟨-, hr⟩
        · rw [hf] at hob; have := szJ hob; omega
        · rw [hob] at hr
          rcases hr with ⟨-, hx, -⟩ | henc
          · rw [hx1] at hx; have := congrArg sz hx; omega
          · have := encA' henc; rw [hx1] at this; omega
      · obtain ⟨⟨-, -, hac⟩, -⟩ := henc1
        rw [hx2] at hab2 hob; rw [hab2, hac] at hob
        exact Q2 _ _ hob
      · obtain ⟨⟨-, htc2, hac⟩, ho1⟩ := henc1
        obtain ⟨-, ho2⟩ := henc2
        have s := sz_tg _ htc2
        rw [← ho2] at ho1
        exact ih a b (a1 (op b w)) (by rw [hac]; omega) ⟨⟨htb, htb2, hab2⟩, hob⟩ ho1

theorem encC (n : Nat) : ∀ u x z, sz z ≤ n → tg u = 2 → Enc u x → op (a2 u) z = op x z → x = a2 u := by
  induction n with
  | zero => intro u x z h _ _ _; have := sz_pos z; omega
  | succ n ih =>
    intro u x z hn htu hux heq
    have hAx := encA' hux
    have su := sz_tg u htu
    rcases opD (a2 u) z with hf1 | ⟨he1, hr1⟩ <;> rcases opD x z with hf2 | ⟨he2, hr2⟩
    · rw [hf1, hf2] at heq; exact (M.J.inj heq).1.symm
    · rw [← heq, hf1] at he2; have := encA' he2; simp only [a2_J_eq] at this; omega
    · rw [heq, hf2] at he1; have := encA' he1; simp only [a2_J_eq] at this; omega
    · rw [heq] at he1 hr1
      have hA := encA' he1
      obtain ⟨⟨htx, htx2, hxx⟩, hox⟩ := hux
      have sx := sz_tg x htx; have sx2 := sz_tg _ htx2
      rcases hr1 with ⟨ht1, hx1, -⟩ | henc1 <;> rcases hr2 with ⟨-, hx2, -⟩ | henc2
      · exfalso
        have s1 := sz_tg _ ht1
        rw [hx1] at s1; rw [hx2] at hxx hox sx2; rw [hxx] at hox
        rcases opD u (a2 (op x z)) with hf | ⟨-, hr⟩
        · rw [hf] at hox; have := szJ hox; omega
        · rw [hox] at hr
          rcases hr with ⟨-, hx, -⟩ | henc
          · have := congrArg sz hx; omega
          · have := encA' henc; omega
      · exfalso
        have s1 := sz_tg _ ht1; rw [hx1] at s1
        have := encA' henc2
        rcases opD u (a1 x) with hf | ⟨-, hr⟩
        · rw [hf] at hox; have := szJ hox; omega
        · rw [hox] at hr
          rcases hr with ⟨-, hx, -⟩ | henc
          · have := congrArg sz hx; omega
          · have := encA' henc; omega
      · exfalso
        obtain ⟨⟨-, -, hac⟩, -⟩ := henc1
        rw [hx2] at hxx hox; rw [hxx, hac] at hox
        exact Q2 _ _ hox
      · obtain ⟨⟨-, htc2, hac⟩, ho1⟩ := henc1
        obtain ⟨-, ho2⟩ := henc2
        have s := sz_tg _ htc2
        rw [← ho2] at ho1
        exact ih u x (a1 (op x z)) (by rw [hac]; omega) htu ⟨⟨htx, htx2, hxx⟩, hox⟩ ho1

theorem H2 (x z : M) : op (op x z) z = J (op x z) z := by
  by_contra hne
  obtain ⟨hec, hrc⟩ := SND (op x z) z hne
  rcases opD x z with hf | ⟨heB, -⟩
  · rw [hf] at hrc hec
    rcases hrc with ⟨-, hx, -⟩ | henc
    · simp only [a2_J_eq] at hx; rw [← hx] at hec; exact encB _ hec
    · have h1 := encA' henc; simp only [a2_J_eq] at h1
      have h2 := encA' hec
      obtain ⟨⟨-, htc2, -⟩, ho⟩ := henc
      have s := sz_tg _ htc2
      rcases opD (J x z) (a1 (op (J x z) z)) with hf' | ⟨-, hr⟩
      · rw [hf'] at ho; have := szJ ho; simp only [sz_J] at this; omega
      · rw [ho] at hr
        rcases hr with ⟨-, hx', -⟩ | henc'
        · simp only [a2_J_eq] at hx'; have := congrArg sz hx'; omega
        · have := encA' henc'; simp only [a2_J_eq] at this; omega
  · obtain ⟨-, hoB⟩ := heB
    obtain ⟨-, hoc⟩ := hec
    rw [← hoc] at hoB
    rcases hrc with ⟨htB, hxB, -⟩ | henc
    · rw [← hxB] at hoB; exact encD _ _ _ (Nat.le_refl _) htB hoB
    · exact encF _ _ _ _ (Nat.le_refl _) henc hoB

theorem H1 (x z : M) : op z (J (op x z) z) = J z (J (op x z) z) := by
  by_contra hne
  obtain ⟨⟨⟨-, htz, haz⟩, -⟩, -⟩ := SND z (J (op x z) z) hne
  simp only [a1_J_eq, a2_J_eq] at htz haz
  rcases opD x z with hf | ⟨⟨⟨-, -, haz2⟩, hoB⟩, -⟩
  · rw [hf] at haz; have := szJ haz; have := sz_a2 z; omega
  · rw [← haz] at haz2 hoB; rw [haz2] at hoB
    exact Q _ hoB

/-- COMPLETENESS: every valid reading is found by the decoder. -/
theorem CMP (n : Nat) : ∀ u v x, msr u v < n → Enc x v → RF u x → op u v = x := by
  induction n with
  | zero => intro u v x h; omega
  | succ n ih =>
    intro u v x hn hxv hux
    obtain ⟨hsh, hxz⟩ := hxv
    have hsv := Sh_sz hsh
    obtain ⟨p1, p2, p3, p4, p5, p6, p7, p8, hp1, hp2, hp3, hp4, hp5, hp6, hp7, hp8, hop⟩ := op_cases u v
    rw [dif_pos (g3 hsh)] at hp3; rw [dif_pos (g4 hsh)] at hp4; rw [dif_pos (g5 hsh)] at hp5; rw [dif_pos (g7 hsh)] at hp7
    subst hp3; subst hp4; subst hp5; subst hp7
    rw [hop]
    split
    · rename_i hg
      obtain ⟨-, htu, e1, e2⟩ := hg
      rw [dif_pos (g1 htu)] at hp1; rw [dif_pos (g2 htu hsh)] at hp2; subst hp1; subst hp2
      rcases hux with ⟨-, hx, -⟩ | henc
      · exact hx
      · rw [← hxz] at e2
        exact (encC _ u x (a1 v) (Nat.le_refl _) htu henc e2).symm
    · split
      · rename_i hg1 hg
        obtain ⟨-, htB, haB, e3, hshB, e4⟩ := hg
        rcases opD x (a1 v) with hf | ⟨heB, -⟩
        · rw [hf] at hxz; rw [← hxz]; rfl
        · rw [hxz] at heB; have := encA' heB; rw [haB] at this; omega
      · split
        · rename_i hg1 hg2 hg
          obtain ⟨-, htB, e5, e6⟩ := hg
          by_cases hs6 : msr (J (a2 (a1 (a2 v))) (a1 (a2 v))) (a1 v) < msr u v
          · rw [dif_pos hs6] at hp6; subst hp6
            rcases opD x (a1 v) with hf | ⟨heB, hrxB⟩
            · rw [hf] at hxz; rw [← hxz] at e6; simp only [a2_J_eq] at e6
              rcases opD (J (a1 v) (J x (a1 v))) (a1 v) with hf' | ⟨he', -⟩
              · rw [hf'] at e6; have := szJ e6; simp only [sz_J] at this; omega
              · rw [e6] at he'; have := encA' he'; simp only [a2_J_eq] at this; omega
            · rw [hxz] at heB hrxB
              rcases hrxB with ⟨htx, hxB, -⟩ | ⟨⟨-, -, haB⟩, -⟩
              · rcases hux with ⟨htu, hx, -⟩ | ⟨⟨-, htx2, hxx⟩, hox⟩
                · exfalso
                  have s1 := sz_tg u htu; have s2 := sz_tg x htx; have s3 := sz_tg _ htB
                  rw [hxB] at s2; rw [hx] at s1
                  rcases opD u (a2 (a1 (a2 v))) with hf' | ⟨-, hr'⟩
                  · rw [hf'] at e5; have := szJ e5; omega
                  · rw [e5] at hr'
                    rcases hr' with ⟨-, hx', -⟩ | henc'
                    · rw [hx] at hx'; have := congrArg sz hx'; omega
                    · have := encA' henc'; rw [hx] at this; omega
                · rw [hxB] at hxx
                  rw [J_a12 htx, hxx, hxB]
              · rw [haB] at e5; exact (Q2 _ _ e5).elim
          · rw [dif_neg hs6] at hp6; subst hp6; exact (nJv hsh e6).elim
        · split
          · rename_i hg1 hg2 hg3 hg
            obtain ⟨-, e7, e8⟩ := hg
            by_cases hs8 : msr (op u (a1 (a2 v))) (a1 v) < msr u v
            · rw [dif_pos hs8] at hp8; subst hp8
              rcases opD x (a1 v) with hf | ⟨heB, hrxB⟩
              · rw [hf] at hxz; rw [← hxz] at e8 ⊢
                rcases opD (op u (J x (a1 v))) (a1 v) with hf' | ⟨he', -⟩
                · rw [hf'] at e8; exact (M.J.inj e8).1
                · rw [e8] at he'; have := encA' he'; simp only [a2_J_eq] at this; omega
              · rw [hxz] at heB hrxB
                obtain ⟨he7, hr7⟩ := SND u (a1 (a2 v)) e7
                rcases hrxB with ⟨htx, hxB, -⟩ | hencxB
                · rcases hux with ⟨htu, hx, -⟩ | ⟨⟨-, htx2, hxx⟩, hox⟩
                  · rcases hr7 with ⟨-, hx7, -⟩ | henc7
                    · rw [← hx7]; exact hx
                    · have := encC _ u (op u (a1 (a2 v))) (a1 v) (Nat.le_refl _) htu henc7 (by rw [e8, ← hxz, hx])
                      rw [this]; exact hx
                  · exfalso
                    obtain ⟨⟨-, -, haB⟩, -⟩ := he7
                    rw [hxB] at hxx hox; rw [hxx, haB] at hox
                    exact Q2 _ _ hox
                · exact ih u (a1 (a2 v)) x (by have := g7 (u := u) hsh; omega) hencxB hux
            · rw [dif_neg hs8] at hp8; subst hp8; exact (nJv hsh e8).elim
          · rename_i hg1 hg2 hg3 hg4
            exfalso
            rcases hux with ⟨htu, hx, hfu⟩ | ⟨⟨htx, htx2, hxx⟩, hox⟩
            · apply hg1
              refine ⟨hsh, htu, ?_, ?_⟩
              · rw [hp1, dif_pos (g1 htu)]; exact hfu
              · rw [hp2, dif_pos (g2 htu hsh), hx]; exact hxz
            · rcases opD x (a1 v) with hf | ⟨heB, hrxB⟩
              · rw [hf] at hxz
                apply hg2
                refine ⟨hsh, ?_, ?_, ?_, ?_, ?_⟩
                · rw [← hxz]; rfl
                · rw [← hxz]; rfl
                · rw [← hxz]; simp only [a1_J_eq]; exact hf
                · rw [← hxz]; simp only [a1_J_eq]; exact ⟨htx, htx2, hxx⟩
                · rw [← hxz]; simp only [a1_J_eq, a2_J_eq]; exact hox
              · rw [hxz] at heB hrxB
                have hAB := encA' heB
                rcases hrxB with ⟨htx', hxB, -⟩ | hencxB
                · apply hg3
                  rw [hxB] at hxx hox; rw [hxx] at hox
                  have hxJ : J (a2 (a1 (a2 v))) (a1 (a2 v)) = x := by rw [J_a12 htx', hxx, hxB]
                  have hs6 : msr (J (a2 (a1 (a2 v))) (a1 (a2 v))) (a1 v) < msr u v :=
                    msr_lt_both (by simp only [sz_J]; omega) (by have := sz_a1_lt hsh.1; omega)
                  refine ⟨hsh, ?_, hox, ?_⟩
                  · rw [← hxB]; exact htx2
                  · rw [hp6, dif_pos hs6, hxJ]; exact hxz
                · have hIH : op u (a1 (a2 v)) = x :=
                    ih u (a1 (a2 v)) x (by have := g7 (u := u) hsh; omega) hencxB ⟨⟨htx, htx2, hxx⟩, hox⟩
                  apply hg4
                  have hAx := encA' hencxB
                  obtain ⟨⟨htB, htB2, haB⟩, -⟩ := hencxB
                  have s1 := sz_tg x htx; have s2 := sz_tg _ htx2; have s0 := sz_tg _ htB; have s3 := sz_tg _ htB2
                  rw [hxx] at s1; rw [haB] at s0
                  have hs8 : msr (op u (a1 (a2 v))) (a1 v) < msr u v := by
                    rw [hIH]
                    exact msr_lt_both (by omega) (by have := sz_a1_lt hsh.1; omega)
                  refine ⟨hsh, ?_, ?_⟩
                  · rw [hIH]; intro h; rw [h] at hAx; simp only [a2_J_eq] at hAx; omega
                  · rw [hp8, dif_pos hs8, hIH]; exact hxz

/-- THE LAW: x = (y * x) * (z * ((x * z) * z)) -/
theorem law (x y z : M) : op (op (y) (x)) (op (z) (op (op (x) (z)) (z))) = x := by
  rw [H2, H1]
  apply CMP (msr (op y x) (J z (J (op x z) z)) + 1) _ _ x (Nat.lt_succ_self _)
  · exact ⟨⟨rfl, rfl, rfl⟩, rfl⟩
  · by_cases h : op y x = J y x
    · left; rw [h]; exact ⟨rfl, rfl, by simp only [a1_J_eq, a2_J_eq]; exact h⟩
    · right; exact (SND y x h).1

theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
