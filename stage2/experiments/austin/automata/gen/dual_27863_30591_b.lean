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
theorem sA1 (u : M) : sz (a1 u) ≤ sz u := by cases u <;> simp [a1, sz] <;> omega
theorem sA2 (u : M) : sz (a2 u) ≤ sz u := by cases u <;> simp [a2, sz] <;> omega
theorem tJg (t : M) (h : tg t = 2) : ∃ b0 b1, t = M.J b0 b1 := by cases t <;> simp_all [tg]
theorem szT (t : M) (h : tg t = 2) : sz t = sz (a1 t) + sz (a2 t) + 1 := by
  obtain ⟨a, b, rfl⟩ := tJg _ h; simp [sz, a1, a2]
@[simp] theorem tg_J_eq (b0 b1 : M) : tg (M.J b0 b1) = 2 := rfl
@[simp] theorem aJ1 (b0 b1 : M) : a1 (M.J b0 b1) = b0 := rfl
@[simp] theorem aJ2 (b0 b1 : M) : a2 (M.J b0 b1) = b1 := rfl
theorem szP (t : M) : 1 ≤ sz t := by cases t <;> simp [sz] <;> omega
@[simp] theorem sJb (a b : M) : sz (J a b) = sz a + sz b + 1 := rfl
theorem s1L {t : M} (h : tg t = 2) : sz (a1 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tJg _ h; simp [sz, a1]; have := szP b; omega
theorem s2L {t : M} (h : tg t = 2) : sz (a2 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tJg _ h; simp [sz, a2]; have := szP a; omega
theorem sJz {a b c : M} (h : J a b = c) : sz c = sz a + sz b + 1 := by rw [← h]; rfl
theorem Ja2 {t : M} (h : tg t = 2) : t = J (a1 t) (a2 t) := by
  obtain ⟨a, b, rfl⟩ := tJg _ h; rfl
def msr (u v : M) : Nat := max (sz u) (sz v) * max (sz u) (sz v) + sz u + sz v
theorem mXL {a b u v : M} (h : max (sz a) (sz b) < max (sz u) (sz v)) : msr a b < msr u v := by
  unfold msr; have h1 : sz a + sz b ≤ 2 * max (sz a) (sz b) := by omega
  have h2 : (max (sz a) (sz b) + 1) * (max (sz a) (sz b) + 1) ≤ max (sz u) (sz v) * max (sz u) (sz v) := Nat.mul_le_mul h h; simp only [Nat.mul_succ, Nat.succ_mul] at h2; omega
theorem mXE {a b u v : M} (h : max (sz a) (sz b) = max (sz u) (sz v)) (h2 : sz a + sz b < sz u + sz v) : msr a b < msr u v := by
  unfold msr; rw [h]; omega
theorem mLr {u b v : M} (h : sz b < sz v) : msr u b < msr u v := by
  have hm : max (sz u) (sz b) ≤ max (sz u) (sz v) := by omega
  rcases Nat.lt_or_eq_of_le hm with dm | ak
  · exact mXL dm
  · exact mXE ak (by omega)
theorem mBt {a b u v : M} (ha : sz a < max (sz u) (sz v)) (hb : sz b < max (sz u) (sz v)) : msr a b < msr u v := mXL (by omega)

def Sh (v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ a1 v = a2 (a2 v)
instance (v : M) : Decidable (Sh v) := by unfold Sh; infer_instance

def op (u v : M) : M :=
  let p1 := if dj : msr (a1 u) (a2 u) < msr u v then op (a1 u) (a2 u) else J u v
  let p2 := if di : msr (a2 u) (a1 v) < msr u v then op (a2 u) (a1 v) else J u v
  let p3 := if dh : msr (a1 (a1 (a2 v))) (a1 v) < msr u v then op (a1 (a1 (a2 v))) (a1 v) else J u v
  let p4 := if dg : msr u (a1 (a1 (a1 (a2 v)))) < msr u v then op u (a1 (a1 (a1 (a2 v)))) else J u v
  let p5 := if df : msr u (a2 (a1 (a2 v))) < msr u v then op u (a2 (a1 (a2 v))) else J u v
  let p6 := if bd : msr (J (a2 (a1 (a2 v))) (a1 (a2 v))) (a1 v) < msr u v then op (J (a2 (a1 (a2 v))) (a1 (a2 v))) (a1 v) else J u v
  let p7 := if de : msr u (a1 (a2 v)) < msr u v then op u (a1 (a2 v)) else J u v
  let p8 := if bc : msr p7 (a1 v) < msr u v then op p7 (a1 v) else J u v
  if Sh v ∧ tg u = 2 ∧ p1 = u ∧ p2 = a1 (a2 v) then a2 u
  else if Sh v ∧ tg (a1 (a2 v)) = 2 ∧ a2 (a1 (a2 v)) = a1 v ∧ p3 = a1 (a2 v) ∧ Sh (a1 (a1 (a2 v))) ∧ p4 = a1 (a2 (a1 (a1 (a2 v)))) then a1 (a1 (a2 v))
  else if Sh v ∧ tg (a1 (a2 v)) = 2 ∧ p5 = a1 (a1 (a2 v)) ∧ p6 = a1 (a2 v) then J (a2 (a1 (a2 v))) (a1 (a2 v))
  else if Sh v ∧ p7 ≠ J u (a1 (a2 v)) ∧ p8 = a1 (a2 v) then p7
  else J u v
termination_by msr u v
decreasing_by all_goals assumption

def inst : Magma M := { op := fun a b => op b a }

theorem op_nSh {u v : M} (h : ¬ Sh v) : op u v = J u v := by
  rw [op.eq_1]; simp [h]

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 0) (g 0) (g 0)
  revert this
  change ¬ g 0 = op (g 0) (op (op (op (g 0) (op (g 0) (g 0))) (g 0)) (g 0))

theorem opC (u v : M) : ∃ p1 p2 p3 p4 p5 p6 p7 p8 : M,
    p1 = (if dj : msr (a1 u) (a2 u) < msr u v then op (a1 u) (a2 u) else J u v) ∧
    p2 = (if di : msr (a2 u) (a1 v) < msr u v then op (a2 u) (a1 v) else J u v) ∧
    p3 = (if dh : msr (a1 (a1 (a2 v))) (a1 v) < msr u v then op (a1 (a1 (a2 v))) (a1 v) else J u v) ∧
    p4 = (if dg : msr u (a1 (a1 (a1 (a2 v)))) < msr u v then op u (a1 (a1 (a1 (a2 v)))) else J u v) ∧
    p5 = (if df : msr u (a2 (a1 (a2 v))) < msr u v then op u (a2 (a1 (a2 v))) else J u v) ∧
    p6 = (if bd : msr (J (a2 (a1 (a2 v))) (a1 (a2 v))) (a1 v) < msr u v then op (J (a2 (a1 (a2 v))) (a1 (a2 v))) (a1 v) else J u v) ∧
    p7 = (if de : msr u (a1 (a2 v)) < msr u v then op u (a1 (a2 v)) else J u v) ∧
    p8 = (if bc : msr p7 (a1 v) < msr u v then op p7 (a1 v) else J u v) ∧
    op u v = (
  if Sh v ∧ tg u = 2 ∧ p1 = u ∧ p2 = a1 (a2 v) then a2 u
  else if Sh v ∧ tg (a1 (a2 v)) = 2 ∧ a2 (a1 (a2 v)) = a1 v ∧ p3 = a1 (a2 v) ∧ Sh (a1 (a1 (a2 v))) ∧ p4 = a1 (a2 (a1 (a1 (a2 v)))) then a1 (a1 (a2 v))
  else if Sh v ∧ tg (a1 (a2 v)) = 2 ∧ p5 = a1 (a1 (a2 v)) ∧ p6 = a1 (a2 v) then J (a2 (a1 (a2 v))) (a1 (a2 v))
  else if Sh v ∧ p7 ≠ J u (a1 (a2 v)) ∧ p8 = a1 (a2 v) then p7
  else J u v) := ⟨_, _, _, _, _, _, _, _, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, op.eq_1 u v⟩

def Enc (a w : M) : Prop := Sh w ∧ op a (a1 w) = a1 (a2 w)
def RF (u x : M) : Prop := (tg u = 2 ∧ a2 u = x ∧ op (a1 u) (a2 u) = u) ∨ Enc u x

theorem Sh_sz {v : M} (h : Sh v) : sz v = sz (a1 v) + sz (a1 (a2 v)) + sz (a1 v) + 2 := by
  obtain ⟨h1, h2, h3⟩ := h; have := szT v h1; have := szT _ h2; rw [← h3] at *; omega
theorem g1 {u v : M} (h : tg u = 2) : msr (a1 u) (a2 u) < msr u v := mBt (by have := s1L h; omega) (by have := s2L h; omega)
theorem g2 {u v : M} (hu : tg u = 2) (hv : Sh v) : msr (a2 u) (a1 v) < msr u v := mBt (by have := s2L hu; omega) (by have := s1L hv.1; omega)
theorem g3 {u v : M} (h : Sh v) : msr (a1 (a1 (a2 v))) (a1 v) < msr u v := mBt (by have := sA1 (a1 (a2 v)); have := s1L h.2.1; have := s2L h.1; omega) (by have := s1L h.1; omega)
theorem g4 {u v : M} (h : Sh v) : msr u (a1 (a1 (a1 (a2 v)))) < msr u v := mLr (by have := sA1 (a1 (a1 (a2 v))); have := sA1 (a1 (a2 v)); have := s1L h.2.1; have := s2L h.1; omega)
theorem g5 {u v : M} (h : Sh v) : msr u (a2 (a1 (a2 v))) < msr u v := mLr (by have := sA2 (a1 (a2 v)); have := s1L h.2.1; have := s2L h.1; omega)
theorem g7 {u v : M} (h : Sh v) : msr u (a1 (a2 v)) < msr u v := mLr (by have := s1L h.2.1; have := s2L h.1; omega)
theorem nJv {u v : M} (h : Sh v) (e : J u v = a1 (a2 v)) : False := by
  have := sJz e; have := s1L h.2.1; have := s2L h.1; omega

theorem SND (u v : M) (h : op u v ≠ J u v) : Enc (op u v) v ∧ RF u (op u v) := by
  obtain ⟨p1, p2, p3, p4, p5, p6, p7, p8, bt, bs, cb, ca, bz, az, bx, ay, cs⟩ := opC u v; rw [cs] at h ⊢; split
  · rename_i hg; obtain ⟨ab, ai, e1, e2⟩ := hg; rw [dif_pos (g1 ai)] at bt; rw [dif_pos (g2 ai ab)] at bs; subst bt; subst bs; exact ⟨⟨ab, e2⟩, Or.inl ⟨ai, rfl, e1⟩⟩
  · split
    · rename_i bf hg; obtain ⟨ab, bv, e0, e3, cp, e4⟩ := hg; rw [dif_pos (g3 ab)] at cb; rw [dif_pos (g4 ab)] at ca; subst cb; subst ca; exact ⟨⟨ab, e3⟩, Or.inr ⟨cp, e4⟩⟩
    · split
      · rename_i bf bn hg
        obtain ⟨ab, bv, e5, e6⟩ := hg; rw [dif_pos (g5 ab)] at bz; subst bz; by_cases bd : msr (J (a2 (a1 (a2 v))) (a1 (a2 v))) (a1 v) < msr u v
        · rw [dif_pos bd] at az; subst az; exact ⟨⟨ab, e6⟩, Or.inr ⟨⟨rfl, bv, rfl⟩, e5⟩⟩
        · rw [dif_neg bd] at az; subst az; exact (nJv ab e6).elim
      · split
        · rename_i bf bn cc hg
          obtain ⟨ab, e7, e8⟩ := hg; rw [dif_pos (g7 ab)] at bx; subst bx; by_cases bc : msr (op u (a1 (a2 v))) (a1 v) < msr u v
          · rw [dif_pos bc] at ay; subst ay; exact ⟨⟨ab, e8⟩, (SND u (a1 (a2 v)) e7).2⟩
          · rw [dif_neg bc] at ay; subst ay; exact (nJv ab e8).elim
        · rename_i bf bn cc cu; rw [if_neg bf, if_neg bn, if_neg cc, if_neg cu] at h; exact absurd rfl h
termination_by msr u v
decreasing_by exact g7 ab

theorem oD (a b : M) : op a b = J a b ∨ (Enc (op a b) b ∧ RF a (op a b)) := by
  by_cases h : op a b = J a b
  · exact Or.inl h
  · exact Or.inr (SND a b h)

theorem encA (n : Nat) : ∀ a w, sz w ≤ n → Enc a w → sz (a2 a) < sz w := by
  induction n with
  | zero => intro a w h _; have := szP w; omega
  | succ n ih =>
    intro a w hn dq; obtain ⟨ab, he⟩ := dq; have s1 := szT w ab.1; have s2 := szT _ ab.2.1; have s4 := sA2 a; rcases oD a (a1 w) with hf | ⟨-, cq⟩
    · rw [hf] at he; have := sJz he; omega
    · rcases cq with ⟨-, hx, -⟩ | aa
      · rw [hx, he]; omega
      · have := ih a (op a (a1 w)) (by rw [he]; omega) aa; rw [he] at this; omega
theorem eA1 {a w : M} (h : Enc a w) : sz (a2 a) < sz w := encA _ a w (Nat.le_refl _) h

theorem eB (a : M) : ¬ Enc a a := by
  intro h0; obtain ⟨ab, he⟩ := h0; have s1 := szT a ab.1; have s2 := szT _ ab.2.1; rcases oD a (a1 a) with hf | ⟨-, cq⟩
  · rw [hf] at he; have := sJz he; omega
  · rcases cq with ⟨-, hx, -⟩ | aa
    · rw [he] at hx; have := congrArg sz hx; omega
    · have := eA1 aa; rw [he] at this; omega

theorem opB (a b : M) : op a b ≠ b := by
  intro h; rcases oD a b with hf | ⟨he, -⟩
  · rw [hf] at h; have := sJz h; omega
  · rw [h] at he; exact eB b he

theorem Q (p : M) : op p (a2 p) ≠ a1 p := by
  intro h; have sp := sA1 p; rcases oD p (a2 p) with hf | ⟨he, hr⟩
  · rw [hf] at h; have := sJz h; omega
  · rw [h] at he hr
    rcases hr with ⟨-, hx, -⟩ | aa
    · rw [hx] at he; exact eB _ he
    · have hA := eA1 aa
      obtain ⟨⟨ci, co, dt⟩, aq⟩ := aa; obtain ⟨⟨ch, cn, ds⟩, be⟩ := he; have s1 := szT _ ci; have s1' := szT _ co; have s2 := szT _ ch; have s2' := szT _ cn; have F1 : sz (a2 p) < sz (a2 (a1 p)) := by
        rcases oD p (a1 (a1 p)) with hf | ⟨-, bi⟩
        · rw [hf] at aq; have := sJz aq; omega
        · rw [aq] at bi
          rcases bi with ⟨-, bb, -⟩ | ag
          · have := congrArg sz bb; omega
          · have := eA1 ag; omega
      have F2 : sz (a2 (a1 p)) < sz (a2 p) := by
        rcases oD (a1 p) (a1 (a2 p)) with hf | ⟨-, bi⟩
        · rw [hf] at be; have := sJz be; omega
        · rw [be] at bi
          rcases bi with ⟨-, bb, -⟩ | ag
          · have := congrArg sz bb; omega
          · have := eA1 ag; omega
      omega

theorem Q2 (u w : M) : op u w ≠ a2 w := by
  intro h; rcases oD u w with hf | ⟨he, -⟩
  · rw [hf] at h; have := sJz h; have := sA2 w; omega
  · rw [h] at he; obtain ⟨⟨-, -, ha⟩, ho⟩ := he; rw [ha] at ho; exact Q _ ho

theorem eD (n : Nat) : ∀ u w, sz w ≤ n → tg u = 2 → op u w ≠ op (a2 u) w := by
  induction n with
  | zero => intro u w h _ _; have := szP w; omega
  | succ n ih =>
    intro u w hn ai ak; have su := szT u ai; have := szP (a1 u); rcases oD u w with bl | ⟨an, bh⟩ <;> rcases oD (a2 u) w with bk | ⟨bm, bw⟩
    · rw [bl, bk] at ak; have := (M.J.inj ak).1; have := congrArg sz this; omega
    · rw [← ak, bl] at bm; have := eA1 bm; simp only [aJ2] at this; omega
    · rw [ak, bk] at an; have := eA1 an; simp only [aJ2] at this; omega
    · rw [ak] at an bh
      have hA := eA1 an; rcases bh with ⟨-, ao, -⟩ | ad <;> rcases bw with ⟨ch, ba, -⟩ | ac
      · rw [← ao] at ba; have := s2L ch; rw [ba] at this; omega
      · rw [← ao] at ac; exact eB _ ac
      · have := eA1 ad; have := s2L ch; rw [ba] at this; omega
      · obtain ⟨⟨-, ht, ha⟩, aq⟩ := ad; obtain ⟨-, be⟩ := ac; have s := szT _ ht; rw [← be] at aq; exact ih u (a1 (op (a2 u) w)) (by rw [ha]; omega) ai aq

theorem eF (n : Nat) : ∀ a b w, sz w ≤ n → Enc a b → op a w ≠ op b w := by
  induction n with
  | zero => intro a b w h _ _; have := szP w; omega
  | succ n ih =>
    intro a b w hn ck ak; have du := eA1 ck; rcases oD a w with bl | ⟨an, bh⟩ <;> rcases oD b w with bk | ⟨bm, bw⟩
    · rw [bl, bk] at ak; rw [(M.J.inj ak).1] at ck; exact eB _ ck
    · rw [← ak, bl] at bm; have := eA1 bm; simp only [aJ2] at this; omega
    · rw [ak, bk] at an; have := eA1 an; simp only [aJ2] at this; omega
    · rw [ak] at an bh
      have hA := eA1 an; obtain ⟨⟨bv, bu, aw⟩, ap⟩ := ck; have sb := szT b bv; have sb2 := szT _ bu; rcases bh with ⟨cx, ao, -⟩ | ad <;> rcases bw with ⟨dc, ba, -⟩ | ac
      · have sa := szT a cx
        have hc : sz (op b w) < sz a := by rw [← ao]; have := szP (a1 a); omega
        rw [ba] at aw ap sb2; rw [aw] at ap; rcases oD a (a2 (op b w)) with hf | ⟨-, hr⟩
        · rw [hf] at ap; have := sJz ap; omega
        · rw [ap] at hr
          rcases hr with ⟨-, hx, -⟩ | aa
          · rw [ao] at hx; have := congrArg sz hx; omega
          · have := eA1 aa; rw [ao] at this; omega
      · have := eA1 ac
        have sa := szT a cx; rw [ao] at sa; rcases oD a (a1 b) with hf | ⟨-, hr⟩
        · rw [hf] at ap; have := sJz ap; omega
        · rw [ap] at hr
          rcases hr with ⟨-, hx, -⟩ | aa
          · rw [ao] at hx; have := congrArg sz hx; omega
          · have := eA1 aa; rw [ao] at this; omega
      · obtain ⟨⟨-, -, bp⟩, -⟩ := ad; rw [ba] at aw ap; rw [aw, bp] at ap; exact Q2 _ _ ap
      · obtain ⟨⟨-, au, bp⟩, aq⟩ := ad; obtain ⟨-, be⟩ := ac; have s := szT _ au; rw [← be] at aq; exact ih a b (a1 (op b w)) (by rw [bp]; omega) ⟨⟨bv, bu, aw⟩, ap⟩ aq

theorem eC (n : Nat) : ∀ u x z, sz z ≤ n → tg u = 2 → Enc u x → op (a2 u) z = op x z → x = a2 u := by
  induction n with
  | zero => intro u x z h _ _ _; have := szP z; omega
  | succ n ih =>
    intro u x z hn ai bg ak; have cw := eA1 bg; have su := szT u ai; rcases oD (a2 u) z with bl | ⟨an, bh⟩ <;> rcases oD x z with bk | ⟨bm, bw⟩
    · rw [bl, bk] at ak; exact (M.J.inj ak).1.symm
    · rw [← ak, bl] at bm; have := eA1 bm; simp only [aJ2] at this; omega
    · rw [ak, bk] at an; have := eA1 an; simp only [aJ2] at this; omega
    · rw [ak] at an bh
      have hA := eA1 an; obtain ⟨⟨ax, aj, al⟩, ae⟩ := bg; have sx := szT x ax; have sx2 := szT _ aj; rcases bh with ⟨ci, ao, -⟩ | ad <;> rcases bw with ⟨-, ba, -⟩ | ac
      · exfalso
        have s1 := szT _ ci; rw [ao] at s1; rw [ba] at al ae sx2; rw [al] at ae; rcases oD u (a2 (op x z)) with hf | ⟨-, hr⟩
        · rw [hf] at ae; have := sJz ae; omega
        · rw [ae] at hr
          rcases hr with ⟨-, hx, -⟩ | aa
          · have := congrArg sz hx; omega
          · have := eA1 aa; omega
      · exfalso
        have s1 := szT _ ci; rw [ao] at s1; have := eA1 ac; rcases oD u (a1 x) with hf | ⟨-, hr⟩
        · rw [hf] at ae; have := sJz ae; omega
        · rw [ae] at hr
          rcases hr with ⟨-, hx, -⟩ | aa
          · have := congrArg sz hx; omega
          · have := eA1 aa; omega
      · exfalso; obtain ⟨⟨-, -, bp⟩, -⟩ := ad; rw [ba] at al ae; rw [al, bp] at ae; exact Q2 _ _ ae
      · obtain ⟨⟨-, au, bp⟩, aq⟩ := ad; obtain ⟨-, be⟩ := ac; have s := szT _ au; rw [← be] at aq; exact ih u x (a1 (op x z)) (by rw [bp]; omega) ai ⟨⟨ax, aj, al⟩, ae⟩ aq

theorem H2 (x z : M) : op (op x z) z = J (op x z) z := by
  apply Classical.byContradiction; intro ct; obtain ⟨ce, cr⟩ := SND (op x z) z ct; rcases oD x z with hf | ⟨av, -⟩
  · rw [hf] at cr ce
    rcases cr with ⟨-, hx, -⟩ | aa
    · simp only [aJ2] at hx; rw [← hx] at ce; exact eB _ ce
    · have h1 := eA1 aa; simp only [aJ2] at h1
      have h2 := eA1 ce; obtain ⟨⟨-, au, -⟩, ho⟩ := aa; have s := szT _ au; rcases oD (J x z) (a1 (op (J x z) z)) with bo | ⟨-, hr⟩
      · rw [bo] at ho; have := sJz ho; simp only [sJb] at this; omega
      · rw [ho] at hr
        rcases hr with ⟨-, bb, -⟩ | ag
        · simp only [aJ2] at bb; have := congrArg sz bb; omega
        · have := eA1 ag; simp only [aJ2] at this; omega
  · obtain ⟨-, bj⟩ := av
    obtain ⟨-, dl⟩ := ce; rw [← dl] at bj; rcases cr with ⟨br, ar, -⟩ | aa
    · rw [← ar] at bj; exact eD _ _ _ (Nat.le_refl _) br bj
    · exact eF _ _ _ _ (Nat.le_refl _) aa bj

theorem H1 (x z : M) : op z (J (op x z) z) = J z (J (op x z) z) := by
  apply Classical.byContradiction; intro ct; obtain ⟨⟨⟨-, db, cj⟩, -⟩, -⟩ := SND z (J (op x z) z) ct; simp only [aJ1, aJ2] at db cj; rcases oD x z with hf | ⟨⟨⟨-, -, cg⟩, bj⟩, -⟩
  · rw [hf] at cj; have := sJz cj; have := sA2 z; omega
  · rw [← cj] at cg bj; rw [cg] at bj; exact Q _ bj

theorem CMP (n : Nat) : ∀ u v x, msr u v < n → Enc x v → RF u x → op u v = x := by
  induction n with
  | zero => intro u v x h; omega
  | succ n ih =>
    intro u v x hn cy bg; obtain ⟨ab, ah⟩ := cy; have dr := Sh_sz ab; obtain ⟨p1, p2, p3, p4, p5, p6, p7, p8, bt, bs, cb, ca, bz, az, bx, ay, cs⟩ := opC u v; rw [dif_pos (g3 ab)] at cb; rw [dif_pos (g4 ab)] at ca; rw [dif_pos (g5 ab)] at bz; rw [dif_pos (g7 ab)] at bx; subst cb; subst ca; subst bz; subst bx; rw [cs]; split
    · rename_i hg
      obtain ⟨-, ai, e1, e2⟩ := hg; rw [dif_pos (g1 ai)] at bt; rw [dif_pos (g2 ai ab)] at bs; subst bt; subst bs; rcases bg with ⟨-, hx, -⟩ | aa
      · exact hx
      · rw [← ah] at e2; exact (eC _ u x (a1 v) (Nat.le_refl _) ai aa e2).symm
    · split
      · rename_i bf hg
        obtain ⟨-, br, bq, e3, dd, e4⟩ := hg; rcases oD x (a1 v) with hf | ⟨av, -⟩
        · rw [hf] at ah; rw [← ah]; rfl
        · rw [ah] at av; have := eA1 av; rw [bq] at this; omega
      · split
        · rename_i bf bn hg
          obtain ⟨-, br, e5, e6⟩ := hg; by_cases bd : msr (J (a2 (a1 (a2 v))) (a1 (a2 v))) (a1 v) < msr u v
          · rw [dif_pos bd] at az; subst az
            rcases oD x (a1 v) with hf | ⟨av, am⟩
            · rw [hf] at ah; rw [← ah] at e6; simp only [aJ2] at e6
              rcases oD (J (a1 v) (J x (a1 v))) (a1 v) with bo | ⟨cf, -⟩
              · rw [bo] at e6; have := sJz e6; simp only [sJb] at this; omega
              · rw [e6] at cf; have := eA1 cf; simp only [aJ2] at this; omega
            · rw [ah] at av am
              rcases am with ⟨ax, ar, -⟩ | ⟨⟨-, -, bq⟩, -⟩
              · rcases bg with ⟨ai, hx, -⟩ | ⟨⟨-, aj, al⟩, ae⟩
                · exfalso
                  have s1 := szT u ai; have s2 := szT x ax; have s3 := szT _ br; rw [ar] at s2; rw [hx] at s1; rcases oD u (a2 (a1 (a2 v))) with bo | ⟨-, bi⟩
                  · rw [bo] at e5; have := sJz e5; omega
                  · rw [e5] at bi
                    rcases bi with ⟨-, bb, -⟩ | ag
                    · rw [hx] at bb; have := congrArg sz bb; omega
                    · have := eA1 ag; rw [hx] at this; omega
                · rw [ar] at al; rw [Ja2 ax, al, ar]
              · rw [bq] at e5; exact (Q2 _ _ e5).elim
          · rw [dif_neg bd] at az; subst az; exact (nJv ab e6).elim
        · split
          · rename_i bf bn cc hg
            obtain ⟨-, e7, e8⟩ := hg; by_cases bc : msr (op u (a1 (a2 v))) (a1 v) < msr u v
            · rw [dif_pos bc] at ay; subst ay
              rcases oD x (a1 v) with hf | ⟨av, am⟩
              · rw [hf] at ah; rw [← ah] at e8 ⊢
                rcases oD (op u (J x (a1 v))) (a1 v) with bo | ⟨cf, -⟩
                · rw [bo] at e8; exact (M.J.inj e8).1
                · rw [e8] at cf; have := eA1 cf; simp only [aJ2] at this; omega
              · rw [ah] at av am
                obtain ⟨dp, dk⟩ := SND u (a1 (a2 v)) e7; rcases am with ⟨ax, ar, -⟩ | af
                · rcases bg with ⟨ai, hx, -⟩ | ⟨⟨-, aj, al⟩, ae⟩
                  · rcases dk with ⟨-, da, -⟩ | cd
                    · rw [← da]; exact hx
                    · have := eC _ u (op u (a1 (a2 v))) (a1 v) (Nat.le_refl _) ai cd (by rw [e8, ← ah, hx]); rw [this]; exact hx
                  · exfalso; obtain ⟨⟨-, -, bq⟩, -⟩ := dp; rw [ar] at al ae; rw [al, bq] at ae; exact Q2 _ _ ae
                · exact ih u (a1 (a2 v)) x (by have := g7 (u := u) ab; omega) af bg
            · rw [dif_neg bc] at ay; subst ay; exact (nJv ab e8).elim
          · rename_i bf bn cc cu
            exfalso; rcases bg with ⟨ai, hx, dn⟩ | ⟨⟨ax, aj, al⟩, ae⟩
            · apply bf
              refine ⟨ab, ai, ?_, ?_⟩
              · rw [bt, dif_pos (g1 ai)]; exact dn
              · rw [bs, dif_pos (g2 ai ab), hx]; exact ah
            · rcases oD x (a1 v) with hf | ⟨av, am⟩
              · rw [hf] at ah
                apply bn; refine ⟨ab, ?_, ?_, ?_, ?_, ?_⟩
                · rw [← ah]; rfl
                · rw [← ah]; rfl
                · rw [← ah]; simp only [aJ1]; exact hf
                · rw [← ah]; simp only [aJ1]; exact ⟨ax, aj, al⟩
                · rw [← ah]; simp only [aJ1, aJ2]; exact ae
              · rw [ah] at av am
                have dv := eA1 av; rcases am with ⟨cl, ar, -⟩ | af
                · apply cc
                  rw [ar] at al ae; rw [al] at ae; have cz : J (a2 (a1 (a2 v))) (a1 (a2 v)) = x := by rw [Ja2 cl, al, ar]
                  have bd : msr (J (a2 (a1 (a2 v))) (a1 (a2 v))) (a1 v) < msr u v := mBt (by simp only [sJb]; omega) (by have := s1L ab.1; omega); refine ⟨ab, ?_, ae, ?_⟩
                  · rw [← ar]; exact aj
                  · rw [az, dif_pos bd, cz]; exact ah
                · have cv : op u (a1 (a2 v)) = x := ih u (a1 (a2 v)) x (by have := g7 (u := u) ab; omega) af (Or.inr ⟨⟨ax, aj, al⟩, ae⟩)
                  apply cu; have cw := eA1 af; obtain ⟨⟨br, cm, bq⟩, -⟩ := af; have s1 := szT x ax; have s2 := szT _ aj; have s0 := szT _ br; have s3 := szT _ cm; rw [al] at s1; rw [bq] at s0; have bc : msr (op u (a1 (a2 v))) (a1 v) < msr u v := (by rw [cv]; exact mBt (by omega) (by have := s1L ab.1; omega)); refine ⟨ab, ?_, ?_⟩
                  · rw [cv]; intro h; rw [h] at cw; simp only [aJ2] at cw; omega
                  · rw [ay, dif_pos bc, cv]; exact ah

theorem law (x y z : M) : op (op (y) (x)) (op (z) (op (op (x) (z)) (z))) = x := by
  rw [H2, H1]; apply CMP (msr (op y x) (J z (J (op x z) z)) + 1) _ _ x (Nat.lt_succ_self _)
  · exact ⟨⟨rfl, rfl, rfl⟩, rfl⟩
  · by_cases h : op y x = J y x
    · left; rw [h]; exact ⟨rfl, rfl, by simp only [aJ1, aJ2]; exact h⟩
    · right; exact (SND y x h).1

theorem lhs : @EquationLHS M inst := by
  intro x y z
  first | exact (law x y z).symm | exact (law x z y).symm | exact (law y x z).symm | exact (law y z x).symm | exact (law z x y).symm | exact (law z y x).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
