import JudgeProblem
inductive submission.M : Type where
 | g : Nat→submission.M
 | J : submission.M→submission.M→submission.M
 deriving DecidableEq
namespace submission
open M
def tg : M→Nat
 | .g _ => 1
 | .J _ _ => 2
def a1 : M→M
 | .J x _ => x
 | t => t
def a2 : M→M
 | .J _ x => x
 | t => t
def sz : M→Nat
 | .g _ => 1
 | .J b0 b1 => sz b0+sz b1+1
def T (u : M) : sz (a1 u)≤sz u :=by cases u <;> simp[a1,sz] <;> omega
def O (u : M) : sz (a2 u)≤sz u :=by cases u <;> simp[a2,sz] <;> omega
def I (t : M) (h : tg t=2) : ∃ b0 b1,t=M.J b0 b1 :=by cases t <;> simp_all[tg]
def tg_g (t : M) (h : tg t≠2) : ∃ n,t=M.g n :=by cases t <;> simp_all[tg]
def sz_tg (t : M) (h : tg t=2) : sz t=sz (a1 t)+sz (a2 t)+1 :=by obtain⟨a,b,rfl⟩:=I _ h; simp[sz,a1,a2]
@[simp] theorem tg_g_eq (n : Nat) : tg (M.g n)=1:=rfl
@[simp] theorem tg_J_eq (b0 b1 : M) : tg (M.J b0 b1)=2:=rfl
@[simp] theorem a1_J_eq (b0 b1 : M) : a1 (M.J b0 b1)=b0:=rfl
@[simp] theorem a2_J_eq (b0 b1 : M) : a2 (M.J b0 b1)=b1:=rfl
@[simp] theorem a1_g_eq (n : Nat) : a1 (M.g n)=M.g n:=rfl
@[simp] theorem a2_g_eq (n : Nat) : a2 (M.g n)=M.g n:=rfl
def W (u v : M) : Nat:=max (sz u) (sz v)*max (sz u) (sz v)+sz u+sz v
def N {a b u v : M} (h : max (sz a) (sz b)<max (sz u) (sz v)) : W a b<W u v :=by
 unfold W
 have h1 : sz a+sz b≤2*max (sz a) (sz b) :=by omega
 have h2 : (max (sz a) (sz b)+1)*(max (sz a) (sz b)+1)≤max (sz u) (sz v)*max (sz u) (sz v):=Nat.mul_le_mul h h
 simp only[Nat.mul_succ,Nat.succ_mul] at h2
 omega
def msr_lt_of_max_eq {a b u v : M} (h : max (sz a) (sz b)=max (sz u) (sz v)) (h2 : sz a+sz b<sz u+sz v) : W a b<W u v :=by unfold W; rw[h]; omega
def Y (u v : M) : Prop:=tg v=2∧tg (a1 v)=2∧u=a1 (a1 v)∧tg (a2 (a1 v))=2∧tg (a1 (a2 (a1 v)))=2∧a2 (a1 (a2 (a1 v)))=a2 (a2 (a1 v))∧a2 (a1 (a2 (a1 v)))=a2 v
instance (u v : M) : Decidable (Y u v) :=by unfold Y; infer_instance
def R (u v : M) : Prop:=tg v=2∧tg (a2 v)=2∧tg (a1 (a2 v))=2
instance (u v : M) : Decidable (R u v) :=by unfold R; infer_instance
def D (u v : M) : Prop:=tg v=2∧tg (a2 v)=2∧tg (a2 (a2 v))=2∧tg (a1 (a2 (a2 v)))=2
instance (u v : M) : Decidable (D u v) :=by unfold D; infer_instance
def op (u v : M) : M :=
 let p1:=if hs1 : W (a1 (a1 (a2 v))) (a2 v)<W u v then op (a1 (a1 (a2 v))) (a2 v) else J u v
 let p2:=if hs2 : W (p1) (a2 v)<W u v then op (p1) (a2 v) else J u v
 let p3:=if hs3 : W (u) (p2)<W u v then op (u) (p2) else J u v
 let p4:=if hs4 : W (a1 (a1 (a2 (a2 v)))) (a2 (a2 v))<W u v then op (a1 (a1 (a2 (a2 v)))) (a2 (a2 v)) else J u v
 let p5:=if hs5 : W (p4) (a2 (a2 v))<W u v then op (p4) (a2 (a2 v)) else J u v
 let p6:=if hs6 : W (a1 (a2 v)) (p5)<W u v then op (a1 (a2 v)) (p5) else J u v
 let p7:=if hs7 : W (u) (p6)<W u v then op (u) (p6) else J u v
 let p8:=if hs8 : W (u) (J (p7) (p5))<W u v then op (u) (J (p7) (p5)) else J u v
 let p9:=if hs9 : W (p8) (a2 v)<W u v then op (p8) (a2 v) else J u v
 let p10:=if hs10 : W (p9) (a2 v)<W u v then op (p9) (a2 v) else J u v
 let p11:=if hs11 : W (u) (p10)<W u v then op (u) (p10) else J u v
 if Y u v then a1 (a1 (a2 (a1 v)))
 else if R u v∧W (a1 (a1 (a2 v))) (a2 v)<W u v∧W (p1) (a2 v)<W u v∧W (u) (p2)<W u v∧a1 v=p3 then a1 (a1 (a2 v))
 else if D u v∧W (a1 (a1 (a2 (a2 v)))) (a2 (a2 v))<W u v∧W (p4) (a2 (a2 v))<W u v∧W (a1 (a2 v)) (p5)<W u v∧W (u) (p6)<W u v∧W (u) (J (p7) (p5))<W u v∧W (p8) (a2 v)<W u v∧W (p9) (a2 v)<W u v∧W (u) (p10)<W u v∧a1 v=p11 then p8
 else J u v
termination_by W u v
decreasing_by
 ·assumption
 ·assumption
 ·assumption
 ·assumption
 ·assumption
 ·assumption
 ·assumption
 ·assumption
 ·assumption
 ·assumption
 ·assumption
def inst : Magma M:={ op:=fun a b => op b a }
def Pre (u v : M) : Prop:=Y u v∨R u v∨D u v
def op_free {u v : M} (h : ¬ Pre u v) : op u v=J u v :=by rw[op.eq_1]; simp only[Pre,not_or] at h; simp[h]
def rhs : ¬ @EquationRHS M inst :=by
 intro h
 have:=h (g 2) (g 0) (g 1)
 revert this
 change ¬ g 2=op (g 1) (op (g 2) (op (g 2) (op (g 1) (op (g 0) (g 0)))))
 simp (config:={decide:=true}) [op.eq_1,sz,Y,R,D]
def Z (t : M) : 1≤sz t :=by cases t <;> simp[sz] <;> omega
def L {t : M} (h : tg t=2) : sz (a1 t)<sz t :=by obtain⟨a,b,rfl⟩:=I _ h; simp[sz,a1]; have:=Z b; omega
def H {t : M} (h : tg t=2) : sz (a2 t)<sz t :=by obtain⟨a,b,rfl⟩:=I _ h; simp[sz,a2]; have:=Z a; omega
def V {a b u v : M} (h : W a b<W u v) : max (sz a) (sz b)≤max (sz u) (sz v) :=by
 apply Classical.byContradiction; intro hc
 have:=N (a:=u) (b:=v) (u:=a) (v:=b) (by omega)
 omega
def op_cases (u v : M) : ∃ p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 : M,
  p1=(if hs1 : W (a1 (a1 (a2 v))) (a2 v)<W u v then op (a1 (a1 (a2 v))) (a2 v) else J u v) ∧
  p2=(if hs2 : W (p1) (a2 v)<W u v then op (p1) (a2 v) else J u v) ∧
  p3=(if hs3 : W (u) (p2)<W u v then op (u) (p2) else J u v) ∧
  p4=(if hs4 : W (a1 (a1 (a2 (a2 v)))) (a2 (a2 v))<W u v then op (a1 (a1 (a2 (a2 v)))) (a2 (a2 v)) else J u v) ∧
  p5=(if hs5 : W (p4) (a2 (a2 v))<W u v then op (p4) (a2 (a2 v)) else J u v) ∧
  p6=(if hs6 : W (a1 (a2 v)) (p5)<W u v then op (a1 (a2 v)) (p5) else J u v) ∧
  p7=(if hs7 : W (u) (p6)<W u v then op (u) (p6) else J u v) ∧
  p8=(if hs8 : W (u) (J (p7) (p5))<W u v then op (u) (J (p7) (p5)) else J u v) ∧
  p9=(if hs9 : W (p8) (a2 v)<W u v then op (p8) (a2 v) else J u v) ∧
  p10=(if hs10 : W (p9) (a2 v)<W u v then op (p9) (a2 v) else J u v) ∧
  p11=(if hs11 : W (u) (p10)<W u v then op (u) (p10) else J u v) ∧
  op u v=(
 if Y u v then a1 (a1 (a2 (a1 v)))
 else if R u v∧W (a1 (a1 (a2 v))) (a2 v)<W u v∧W (p1) (a2 v)<W u v∧W (u) (p2)<W u v∧a1 v=p3 then a1 (a1 (a2 v))
 else if D u v∧W (a1 (a1 (a2 (a2 v)))) (a2 (a2 v))<W u v∧W (p4) (a2 (a2 v))<W u v∧W (a1 (a2 v)) (p5)<W u v∧W (u) (p6)<W u v∧W (u) (J (p7) (p5))<W u v∧W (p8) (a2 v)<W u v∧W (p9) (a2 v)<W u v∧W (u) (p10)<W u v∧a1 v=p11 then p8
 else J u v
  ) :=
 ⟨_,_,_,_,_,_,_,_,_,_,_,rfl,rfl,rfl,rfl,rfl,rfl,rfl,rfl,rfl,rfl,rfl,op.eq_1 u v⟩
def X (u v : M) : op u v=J u v∨(Y u v∧op u v=a1 (a1 (a2 (a1 v)))) ∨
  (tg v=2∧tg (a2 v)=2∧tg (a1 (a2 v))=2∧op u v=a1 (a1 (a2 v)) ∧
   W u (op (op (a1 (a1 (a2 v))) (a2 v)) (a2 v))<W u v ∧
   a1 v=op u (op (op (a1 (a1 (a2 v))) (a2 v)) (a2 v))) ∨
  (tg v=2∧∃ q,W u q<W u v∧op u v=op u q ∧
   W u (op (op (op u q) (a2 v)) (a2 v))<W u v ∧
   a1 v=op u (op (op (op u q) (a2 v)) (a2 v))) :=by
 obtain⟨p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,hp1,hp2,hp3,hp4,hp5,hp6,hp7,hp8,hp9,hp10,hp11,hop⟩:=op_cases u v
 rw[hop]
 split
 ·rename_i h; exact Or.inr (Or.inl ⟨h,rfl⟩)
 ·split
  ·rename_i h
   obtain⟨h2,g1,g2,g3,he⟩:=h
   rw[dif_pos g1] at hp1; subst hp1
   rw[dif_pos g2] at hp2; subst hp2
   rw[dif_pos g3] at hp3; subst hp3
   exact Or.inr (Or.inr (Or.inl ⟨h2.1,h2.2.1,h2.2.2,rfl,g3,he⟩))
  ·split
   ·rename_i h
    obtain⟨h3,g1,g2,g3,g4,g5,g6,g7,g8,he⟩:=h
    rw[dif_pos g1] at hp4; subst hp4
    rw[dif_pos g2] at hp5; subst hp5
    rw[dif_pos g3] at hp6; subst hp6
    rw[dif_pos g4] at hp7; subst hp7
    rw[dif_pos g5] at hp8; subst hp8
    rw[dif_pos g6] at hp9; subst hp9
    rw[dif_pos g7] at hp10; subst hp10
    rw[dif_pos g8] at hp11; subst hp11
    exact Or.inr (Or.inr (Or.inr ⟨h3.1,_,g5,rfl,g8,he⟩))
   ·exact Or.inl rfl
def SUn (n : Nat) : ∀ u v : M,W u v<n→op u v≠J u v→sz u<sz v :=by
 induction n with
 | zero => intro u v h; omega
 | succ n ih =>
  intro u v hn hne
  have key : ∀ q : M,tg v=2→W u q<W u v→a1 v=op u q→sz u<sz v :=by
   intro q h1 hg he
   have hv:=L h1
   have hm:=V hg
   by_cases hf : op u q=J u q
   ·rw[hf] at he; have:=congrArg sz he; simp only[sz] at this; omega
   ·have:=ih u q (by omega) hf; omega
  rcases X u v with h | ⟨h1,-⟩ | ⟨h1,-,-,-,hg,he⟩ | ⟨h1,q,-,-,hg,he⟩
  ·exact absurd h hne
  ·have e1:=T (a1 v); have e2:=L h1.1; rw[h1.2.2.1]; omega
  ·exact key _ h1 hg he
  ·exact key _ h1 hg he
def Q {u v : M} (h : op u v≠J u v) : sz u<sz v:=SUn (W u v+1) u v (Nat.lt_succ_self _) h
def Wf {u v : M} (h : sz v≤sz u) : op u v=J u v :=by apply Classical.byContradiction; intro hc; have:=Q hc; omega
def oR1 {u v : M} (h : Y u v) : op u v=a1 (a1 (a2 (a1 v))) :=by
 obtain⟨p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,-,-,-,-,-,-,-,-,-,-,-,hop⟩:=op_cases u v
 rw[hop,if_pos h]
def E (u v : M) : op u v=J u v∨sz (op u v)<sz v :=by
 by_cases hne : op u v=J u v
 ·exact Or.inl hne
 ·right
  have hu:=Q hne
  rcases X u v with h | ⟨h1,he⟩ | ⟨h1,-,-,he,-,-⟩ | ⟨h1,q,-,he,hg,-⟩
  ·exact absurd h hne
  ·rw[he]
   have:=T (a1 (a2 (a1 v))); have:=T (a2 (a1 v)); have:=O (a1 v); have:=L h1.1
   omega
  ·rw[he]
   have:=T (a1 (a2 v)); have:=T (a2 v); have:=H h1
   omega
  ·rw[← he] at hg
   have hw:=H h1
   have hm:=V hg
   by_cases hy : op (op u v) (a2 v)=J (op u v) (a2 v)
   ·by_cases hx : op (J (op u v) (a2 v)) (a2 v)=J (J (op u v) (a2 v)) (a2 v)
    ·rw[hy,hx] at hm; simp only[sz] at hm; omega
    ·have:=Q hx; simp only[sz] at this; omega
   ·have:=Q hy; omega
def NFX {u v : M} (h : op u v=v) : False :=by
 rcases E u v with hf | hs
 ·rw[hf] at h; have:=congrArg sz h; simp only[sz] at this; have:=Z u; omega
 ·rw[h] at hs; exact Nat.lt_irrefl _ hs
def AFn (n : Nat) : ∀ z c y a : M,W z (op (op c y) y)<n →
  op z (op (op c y) y)=J a y→False :=by
 induction n with
 | zero => intro z c y a h _; omega
 | succ n ih =>
  intro z c y a hn he
  have hd : op z (op (op c y) y)≠J z (op (op c y) y) :=by
   intro hf
   have h1:=congrArg a2 (hf.symm.trans he)
   simp only[a2_J_eq] at h1
   exact NFX h1
  have hsz:=(E z (op (op c y) y)).resolve_left hd
  rw[he] at hsz
  simp only[sz] at hsz
  rcases E (op c y) y with hC | hC
  ·rw[hC] at hsz he hd hn
   simp only[sz] at hsz
   rcases E c y with hK | hK
   ·rw[hK] at he hd hn
    rcases X z (J (J c y) y) with h | ⟨h1,-⟩ | ⟨-,-,-,hr,-,-⟩ | ⟨-,q,-,-,hg,hgu⟩
    ·exact hd h
    ·obtain⟨-,-,-,h4,-,-,h7⟩:=h1
     simp only[a1_J_eq,a2_J_eq] at h4 h7
     have:=L h4; have:=O (a1 y); have:=congrArg sz h7; omega
    ·rw[hr] at he
     simp only[a1_J_eq,a2_J_eq] at he
     have:=congrArg sz he
     simp only[sz] at this
     have:=T (a1 y); have:=T y; omega
    ·simp only[a1_J_eq,a2_J_eq] at hg hgu
     exact ih z (op z q) y c (by omega) hgu.symm
   ·rcases X z (J (op c y) y) with h | ⟨-,hr⟩ | ⟨-,-,-,hr,-,-⟩ | ⟨-,q,-,-,-,hgu⟩
    ·exact hd h
    ·rw[hr] at he
     simp only[a1_J_eq,a2_J_eq] at he
     have:=congrArg sz he
     simp only[sz] at this
     have:=T (a1 (a2 (op c y))); have:=T (a2 (op c y))
     have:=O (op c y); omega
    ·rw[hr] at he
     simp only[a1_J_eq,a2_J_eq] at he
     have:=congrArg sz he
     simp only[sz] at this
     have:=T (a1 y); have:=T y; omega
    ·
     sorry
  ·omega
def AFm {z c y a : M} (he : op z (op (op c y) y)=J a y) : False :=
 AFn (W z (op (op c y) y)+1) z c y a (Nat.lt_succ_self _) he
def Afree (x y z : M) : op z (J (J x y) y)=J z (J (J x y) y) :=by
 rcases X z (J (J x y) y) with h | ⟨h1,-⟩ | ⟨-,-,-,-,-,he⟩ | ⟨-,q,-,-,-,he⟩
 ·exact h
 ·exfalso
  obtain⟨-,-,-,h4,-,-,h7⟩:=h1
  simp only[a1_J_eq,a2_J_eq] at h4 h7
  have:=L h4; have:=O (a1 y); have:=congrArg sz h7; omega
 ·exact absurd he (fun hh => AFm (by simp only[a1_J_eq,a2_J_eq] at hh; exact hh.symm))
 ·exact absurd he (fun hh => AFm (by simp only[a1_J_eq,a2_J_eq] at hh; exact hh.symm))
def SFc {x y z : M} (hxx : x=J z (op (op x y) y))
  (hop : op x y=J z (op (op x y) y)) : False :=by
 have hox : op x y=x:=hop.trans hxx.symm
 rw[hox,hox] at hxx
 have:=congrArg sz hxx
 simp only[sz] at this
 have:=Z z; omega
def SFb {x y z : M} (hQ : sz (op (op x y) y)<sz y)
  (hA : a1 (a1 y)=J z (op (op x y) y)) (hop : op x y=J z (op (op x y) y)) : False :=by
 rcases E x y with hf | hf
 ·rw[hf] at hop hQ
  have e4:=congrArg a2 hop
  simp only[a2_J_eq] at e4
  rw[← e4] at hQ; omega
 ·rcases X x y with h2 | ⟨g2,-⟩ | ⟨-,-,-,-,-,gg⟩ | ⟨-,q2,-,-,-,gg⟩
  ·have:=congrArg sz h2
   simp only[sz] at this
   have:=Z x; omega
  ·exact SFc (g2.2.2.1.trans hA) hop
  ·rcases E x (op (op (a1 (a1 (a2 y))) (a2 y)) (a2 y)) with hf2 | hf2
   ·rw[hf2] at gg
    have hb:=congrArg a1 gg
    simp only[a1_J_eq] at hb
    exact SFc (hb.symm.trans hA) hop
   ·sorry
  ·rcases E x (op (op (op x q2) (a2 y)) (a2 y)) with hf2 | hf2
   ·rw[hf2] at gg
    have hb:=congrArg a1 gg
    simp only[a1_J_eq] at hb
    exact SFc (hb.symm.trans hA) hop
   ·sorry
def SFa {x y z : M} (ht : tg y=2) (hA : a1 (a1 y)=J z (op (op x y) y)) : False :=by
 have e1 : sz (a1 (a1 y))<sz y :=by have:=T (a1 y); have:=L ht; omega
 have e2:=congrArg sz hA
 simp only[sz] at e2
 rcases E (op x y) y with hQ | hQ
 ·have e3:=congrArg sz hQ
  simp only[sz] at e3
  have:=Z (op x y); have:=Z z; omega
 ·rcases X (op x y) y with h | ⟨g1,-⟩ | ⟨-,-,-,-,-,gg⟩ | ⟨-,q,-,-,-,gg⟩
  ·have e3:=congrArg sz h
   simp only[sz] at e3
   have:=Z (op x y); have:=Z z; omega
  ·exact SFb hQ hA (g1.2.2.1.trans hA)
  ·rcases E (op x y) (op (op (a1 (a1 (a2 y))) (a2 y)) (a2 y)) with hf | hf
   ·rw[hf] at gg
    have hb:=congrArg a1 gg
    simp only[a1_J_eq] at hb
    exact SFb hQ hA (hb.symm.trans hA)
   ·sorry
  ·rcases E (op x y) (op (op (op (op x y) q) (a2 y)) (a2 y)) with hf | hf
   ·rw[hf] at gg
    have hb:=congrArg a1 gg
    simp only[a1_J_eq] at hb
    exact SFb hQ hA (hb.symm.trans hA)
   ·sorry
def K (x y z : M) : op (J z (op (op x y) y)) y=J (J z (op (op x y) y)) y :=by
 rcases X (J z (op (op x y) y)) y with h | ⟨h1,-⟩ | ⟨h1,-,-,-,-,he⟩ | ⟨h1,q,-,-,-,he⟩
 ·exact h
 ·exact (SFa h1.1 h1.2.2.1.symm).elim
 ·exfalso
  rcases E (J z (op (op x y) y)) (op (op (a1 (a1 (a2 y))) (a2 y)) (a2 y)) with hf | hf
  ·rw[hf] at he
   have h':=congrArg a1 he
   simp only[a1_J_eq] at h'
   exact SFa h1 h'
  ·sorry
 ·exfalso
  rcases E (J z (op (op x y) y))
   (op (op (op (J z (op (op x y) y)) q) (a2 y)) (a2 y)) with hf | hf
  ·rw[hf] at he
   have h':=congrArg a1 he
   simp only[a1_J_eq] at h'
   exact SFa h1 h'
  ·sorry
def G {a b c d : M} (h1 : sz a<sz d) (h2 : sz b<sz d) :
  max (sz a) (sz b)<max (sz c) (sz d) :=by rw[Nat.max_def,Nat.max_def]; split <;> split <;> omega
def oR2 {u v : M} (h1 : ¬ Y u v) (h2 : R u v)
  (g1 : W (a1 (a1 (a2 v))) (a2 v)<W u v)
  (g2 : W (op (a1 (a1 (a2 v))) (a2 v)) (a2 v)<W u v)
  (g3 : W u (op (op (a1 (a1 (a2 v))) (a2 v)) (a2 v))<W u v)
  (he : a1 v=op u (op (op (a1 (a1 (a2 v))) (a2 v)) (a2 v))) : op u v=a1 (a1 (a2 v)) :=by
 obtain⟨p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,hp1,hp2,hp3,-,-,-,-,-,-,-,-,hop⟩:=op_cases u v
 rw[dif_pos g1] at hp1; subst hp1
 rw[dif_pos g2] at hp2; subst hp2
 rw[dif_pos g3] at hp3; subst hp3
 rw[hop,if_neg h1,if_pos ⟨h2,g1,g2,g3,he⟩]
def U {x y z : M} (hy : tg y=2) (hay : tg (a1 y)=2) (hx : a1 (a1 y)=x)
  (hPs : sz (op x y)<sz y) (hQ : sz (a2 (a1 (op (op x y) y)))<sz y)
  (hAf : op z (op (op x y) y)=J z (op (op x y) y)) :
  op z (J (J z (op (op x y) y)) y)=x :=by
 have hxy : sz x≤sz y :=by rw[← hx]; have:=T (a1 y); have:=T y; omega
 have hs : sz (J (J z (op (op x y) y)) y)=sz z+sz (op (op x y) y)+sz y+2 :=by simp only[sz]; omega
 have g1 : W (a1 (a1 (a2 (J (J z (op (op x y) y)) y)))) (a2 (J (J z (op (op x y) y)) y)) <
   W z (J (J z (op (op x y) y)) y) :=by
  simp only[a1_J_eq,a2_J_eq,hx]
  exact N (G (by omega) (by omega))
 have g2 : W (op (a1 (a1 (a2 (J (J z (op (op x y) y)) y)))) (a2 (J (J z (op (op x y) y)) y)))
   (a2 (J (J z (op (op x y) y)) y))<W z (J (J z (op (op x y) y)) y) :=by
  simp only[a1_J_eq,a2_J_eq,hx]
  exact N (G (by omega) (by omega))
 have g3 : W z (op (op (a1 (a1 (a2 (J (J z (op (op x y) y)) y)))) (a2 (J (J z (op (op x y) y)) y)))
   (a2 (J (J z (op (op x y) y)) y)))<W z (J (J z (op (op x y) y)) y) :=by
  simp only[a1_J_eq,a2_J_eq,hx]
  exact N (G (by have:=Z y; have:=Z (op (op x y) y); omega)
   (by have:=Z y; have:=Z z; omega))
 have hn : ¬ Y z (J (J z (op (op x y) y)) y) :=by
  intro h
  obtain⟨-,-,-,-,-,-,h7⟩:=h
  simp only[a1_J_eq,a2_J_eq] at h7
  have:=congrArg sz h7; omega
 have hg : a1 (J (J z (op (op x y) y)) y) =
   op z (op (op (a1 (a1 (a2 (J (J z (op (op x y) y)) y)))) (a2 (J (J z (op (op x y) y)) y)))
    (a2 (J (J z (op (op x y) y)) y))) :=by simp only[a1_J_eq,a2_J_eq,hx]; exact hAf.symm
 have hr:=oR2 (u:=z) (v:=J (J z (op (op x y) y)) y) hn ⟨rfl,hy,hay⟩ g1 g2 g3 hg
 rw[hr]; simp only[a2_J_eq,hx]
def NPAq {x y z : M} (hqd : sz (op (op x y) y)<sz y) :
  ¬ Y z (J (op z (op (op x y) y)) y) :=by
 intro h
 obtain⟨-,h2,-,h4,h5,-,h7⟩:=h
 simp only[a1_J_eq,a2_J_eq] at h2 h4 h5 h7
 rcases E z (op (op x y) y) with hf | hf
 ·rw[hf] at h7
  simp only[a1_J_eq,a2_J_eq] at h7
  have:=congrArg sz h7
  have:=O (a1 (op (op x y) y)); have:=T (op (op x y) y)
  omega
 ·have e1:=H h2; have e2:=L h4; have e3:=H h5
  have e4:=congrArg sz h7
  omega
def TOPg {x y z A : M} (hy : tg y=2) (hay : tg (a1 y)=2) (hx : a1 (a1 y)=x)
  (hPs : sz (op x y)<sz y) (hA : op z (op (op x y) y)=A) (hn : ¬ Y z (J A y))
  (hz : sz z<sz A+sz y) (hq : sz (op (op x y) y)<sz A+sz y) :
  op z (J A y)=x :=by
 have hxy : sz x≤sz y :=by rw[← hx]; have:=T (a1 y); have:=T y; omega
 have hs : sz (J A y)=sz A+sz y+1 :=by simp only[sz]
 have g1 : W (a1 (a1 (a2 (J A y)))) (a2 (J A y))<W z (J A y) :=by
  simp only[a1_J_eq,a2_J_eq,hx]
  exact N (G (by omega) (by omega))
 have g2 : W (op (a1 (a1 (a2 (J A y)))) (a2 (J A y))) (a2 (J A y))<W z (J A y) :=by
  simp only[a1_J_eq,a2_J_eq,hx]
  exact N (G (by omega) (by omega))
 have g3 : W z (op (op (a1 (a1 (a2 (J A y)))) (a2 (J A y))) (a2 (J A y)))<W z (J A y) :=by
  simp only[a1_J_eq,a2_J_eq,hx]
  exact N (G (by omega) (by omega))
 have hg : a1 (J A y) =
   op z (op (op (a1 (a1 (a2 (J A y)))) (a2 (J A y))) (a2 (J A y))) :=by simp only[a1_J_eq,a2_J_eq,hx]; exact hA.symm
 rw[oR2 (u:=z) (v:=J A y) hn ⟨rfl,hy,hay⟩ g1 g2 g3 hg]
 simp only[a2_J_eq,hx]
def NPAf {x y z : M} (hQ : sz (a2 (a1 (op (op x y) y)))<sz y)
  (hA : op z (op (op x y) y)=J z (op (op x y) y)) :
  ¬ Y z (J (op z (op (op x y) y)) y) :=by
 intro h
 obtain⟨-,-,-,-,-,-,h7⟩:=h
 simp only[a1_J_eq,a2_J_eq] at h7
 rw[hA] at h7
 simp only[a1_J_eq,a2_J_eq] at h7
 have:=congrArg sz h7
 omega
def SFg (x y z : M) :
  op (op z (op (op x y) y)) y=J (op z (op (op x y) y)) y :=by sorry
def AQd (x y z : M) (hP : op x y≠J x y) :
  op z (op (op x y) y)=J z (op (op x y) y)∨sz (op (op x y) y)<sz y :=by sorry
def law (x y z : M) : op (z) (op (op (z) (op (op (x) (y)) (y))) (y))=x :=by
 rw[SFg x y z]
 by_cases hP : op x y=J x y
 ·rw[show op (op x y) y=J (J x y) y by
   rw[hP]; exact Wf (by simp only[sz]; have:=Z x; omega),Afree x y z]
  exact oR1 ⟨rfl,rfl,rfl,rfl,rfl,rfl,rfl⟩
 ·have hPs:=(E x y).resolve_left hP
  have hQ : sz (a2 (a1 (op (op x y) y)))<sz y :=by
   rcases E (op x y) y with h | h
   ·rw[h]; simp only[a1_J_eq]; have:=O (op x y); omega
   ·have:=T (op (op x y) y); have:=O (a1 (op (op x y) y)); omega
  have hk : tg y=2∧tg (a1 y)=2∧a1 (a1 y)=x :=by sorry
  have hpa:=Z (op z (op (op x y) y))
  rcases AQd x y z hP with hA | hA
  ·have e:=congrArg sz hA
   simp only[sz] at e
   exact TOPg hk.1 hk.2.1 hk.2.2 hPs rfl (NPAf hQ hA) (by omega) (by omega)
  ·have hz : sz z<sz (op z (op (op x y) y))+sz y :=by
    rcases E z (op (op x y) y) with hf | hf
    ·have e:=congrArg sz hf; simp only[sz] at e; omega
    ·have hne : op z (op (op x y) y)≠J z (op (op x y) y) :=by intro hc; rw[hc] at hf; simp only[sz] at hf; have:=Z z; omega
     have:=Q hne; omega
   exact TOPg hk.1 hk.2.1 hk.2.2 hPs rfl (NPAq hA) hz (by omega)
def lhs : @EquationLHS M inst :=by
 intro x y z
 exact (law x y z).symm
end submission
def submission : Goal :=
 Exists.intro submission.M (Exists.intro submission.inst
  (And.intro submission.lhs submission.rhs))