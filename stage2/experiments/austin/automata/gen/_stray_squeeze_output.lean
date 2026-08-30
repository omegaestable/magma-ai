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
def O (u : M) : sz (a1 u)≤sz u :=by cases u <;> simp[a1,sz] <;> omega
def X (u : M) : sz (a2 u)≤sz u :=by cases u <;> simp[a2,sz] <;> omega
def tg_J (t : M) (h : tg t=2) : ∃ b0 b1,t=M.J b0 b1 :=by cases t <;> simp_all[tg]
def tg_g (t : M) (h : tg t≠2) : ∃ n,t=M.g n :=by cases t <;> simp_all[tg]
def sz_tg (t : M) (h : tg t=2) : sz t=sz (a1 t)+sz (a2 t)+1 :=by obtain⟨a,b,rfl⟩:=tg_J _ h; simp[sz,a1,a2]
@[simp] theorem tg_g_eq (n : Nat) : tg (M.g n)=1:=rfl
@[simp] theorem tg_J_eq (b0 b1 : M) : tg (M.J b0 b1)=2:=rfl
@[simp] theorem a1_J_eq (b0 b1 : M) : a1 (M.J b0 b1)=b0:=rfl
@[simp] theorem a2_J_eq (b0 b1 : M) : a2 (M.J b0 b1)=b1:=rfl
@[simp] theorem a1_g_eq (n : Nat) : a1 (M.g n)=M.g n:=rfl
@[simp] theorem a2_g_eq (n : Nat) : a2 (M.g n)=M.g n:=rfl
/-- the recursion measure: lexicographic (max size,total size),packed into one Nat -/
def T (u v : M) : Nat:=max (sz u) (sz v)*max (sz u) (sz v)+sz u+sz v
def msr_lt_of_max_lt {a b u v : M} (h : max (sz a) (sz b)<max (sz u) (sz v)) : T a b<T u v :=by
 unfold T
 have h1 : sz a+sz b≤2*max (sz a) (sz b) :=by omega
 have h2 : (max (sz a) (sz b)+1)*(max (sz a) (sz b)+1)≤max (sz u) (sz v)*max (sz u) (sz v):=Nat.mul_le_mul h h
 simp only[Nat.mul_succ,Nat.succ_mul] at h2
 omega
def msr_lt_of_max_eq {a b u v : M} (h : max (sz a) (sz b)=max (sz u) (sz v)) (h2 : sz a+sz b<sz u+sz v) : T a b<T u v :=by unfold T; rw[h]; omega
def P1 (u v : M) : Prop:=tg v=2∧tg (a1 (a2 v))=2∧a1 (a1 (a2 v))=u
instance (u v : M) : Decidable (P1 u v) :=by unfold P1; infer_instance
def U (u v : M) : Prop:=tg v=2∧tg (a1 (a2 v))=2∧a1 (a1 (a2 v))=u
instance (u v : M) : Decidable (U u v) :=by unfold U; infer_instance
def P3 (u v : M) : Prop:=tg v=2
instance (u v : M) : Decidable (P3 u v) :=by unfold P3; infer_instance
def P4 (u v : M) : Prop:=tg v=2∧tg (a1 v)=2
instance (u v : M) : Decidable (P4 u v) :=by unfold P4; infer_instance
def P5 (u v : M) : Prop:=tg v=2∧tg (a1 v)=2
instance (u v : M) : Decidable (P5 u v) :=by unfold P5; infer_instance
def P6 (u v : M) : Prop:=tg v=2∧tg (a1 v)=2
instance (u v : M) : Decidable (P6 u v) :=by unfold P6; infer_instance
def P7 (u v : M) : Prop:=tg v=2∧tg u=2∧tg (a2 u)=2∧a2 v=a1 u∧tg (a1 v)=2∧a2 (a1 v)=u∧tg (a1 (a1 v))=2∧a1 (a1 (a1 v))=u
instance (u v : M) : Decidable (P7 u v) :=by unfold P7; infer_instance
def op (u v : M) : M :=
 let p1:=if hs1 : T (a1 (a2 v)) (u)<T u v then op (a1 (a2 v)) (u) else J u v
 let p2:=if hs2 : T (u) (a2 (a1 (a2 v)))<T u v then op (u) (a2 (a1 (a2 v))) else J u v
 let p3:=if hs3 : T (a1 (a2 (a1 (a2 v)))) (a1 v)<T u v then op (a1 (a2 (a1 (a2 v)))) (a1 v) else J u v
 let p4:=if hs4 : T (a2 (a2 (a1 v))) (a1 v)<T u v then op (a2 (a2 (a1 v))) (a1 v) else J u v
 let p5:=if hs5 : T (a1 (a2 v)) (a1 v)<T u v then op (a1 (a2 v)) (a1 v) else J u v
 let p6:=if hs6 : T (u) (J (a1 (a2 v)) (a1 v))<T u v then op (u) (J (a1 (a2 v)) (a1 v)) else J u v
 let p7:=if hs7 : T (u) (a1 (a1 v))<T u v then op (u) (a1 (a1 v)) else J u v
 let p8:=if hs8 : T (a1 (a1 (a1 v))) (a1 v)<T u v then op (a1 (a1 (a1 v))) (a1 v) else J u v
 let p9:=if hs9 : T (a2 (a2 u)) (u)<T u v then op (a2 (a2 u)) (u) else J u v
 let p10:=if hs10 : T (a2 (a2 u)) (a1 v)<T u v then op (a2 (a2 u)) (a1 v) else J u v
 let p11:=if hs11 : T (a1 (a1 v)) (u)<T u v then op (a1 (a1 v)) (u) else J u v
 let p12:=if hs12 : T (u) (a2 (a1 (a1 v)))<T u v then op (u) (a2 (a1 (a1 v))) else J u v
 let p13:=if hs13 : T (a1 (a2 (a1 (a1 v)))) (a2 (a2 u))<T u v then op (a1 (a2 (a1 (a1 v)))) (a2 (a2 u)) else J u v
 if P1 u v∧T (a1 (a2 v)) (u)<T u v∧T (u) (a2 (a1 (a2 v)))<T u v∧T (a1 (a2 (a1 (a2 v)))) (a1 v)<T u v∧a2 v=p1∧a1 (a2 v)=p2∧a2 (a1 (a2 v))=p3 then a1 v
 else if U u v∧T (a1 (a2 v)) (u)<T u v∧T (u) (a2 (a1 (a2 v)))<T u v∧T (a2 (a2 (a1 v))) (a1 v)<T u v∧a2 v=p1∧a1 (a2 v)=p2∧a2 (a1 (a2 v))=p4 then a1 v
 else if P3 u v∧T (a1 (a2 v)) (u)<T u v∧T (a1 (a2 v)) (a1 v)<T u v∧T (u) (J (a1 (a2 v)) (a1 v))<T u v∧a2 v=p1∧J (a1 (a2 v)) (a1 v)=p5∧a1 (a2 v)=p6 then a1 v
 else if P4 u v∧T (a1 (a2 v)) (u)<T u v∧T (u) (a1 (a1 v))<T u v∧T (a1 (a1 (a1 v))) (a1 v)<T u v∧a2 v=p1∧a1 (a2 v)=p7∧a1 (a1 v)=p8 then a1 v
 else if P5 u v∧T (a1 (a2 v)) (u)<T u v∧T (u) (a1 (a1 v))<T u v∧T (a2 (a2 (a1 v))) (a1 v)<T u v∧a2 v=p1∧a1 (a2 v)=p7∧a1 (a1 v)=p4 then a1 v
 else if P6 u v∧T (a2 (a2 u)) (u)<T u v∧T (u) (a1 (a1 v))<T u v∧T (a2 (a2 (a1 v))) (a1 v)<T u v∧a2 v=p9∧a2 (a2 u)=p7∧a1 (a1 v)=p4 then a1 v
 else if P7 u v∧T (a2 (a2 u)) (u)<T u v∧T (a2 (a2 u)) (a1 v)<T u v∧T (a1 (a1 v)) (u)<T u v∧T (u) (a2 (a1 (a1 v)))<T u v∧T (a1 (a2 (a1 (a1 v)))) (a2 (a2 u))<T u v∧a2 v=p9∧J (a2 (a2 u)) (a1 v)=p10∧a1 v=p11∧a1 (a1 v)=p12∧a2 (a1 (a1 v))=p13 then a1 v
 else J u v
termination_by T u v
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
 ·assumption
 ·assumption
def inst : Magma M:={ op:=fun a b => op b a }
def Pre (u v : M) : Prop:=P1 u v∨U u v∨P3 u v∨P4 u v∨P5 u v∨P6 u v∨P7 u v
def op_free {u v : M} (h : ¬ Pre u v) : op u v=J u v :=by rw[op.eq_1]; simp only[Pre,not_or] at h; simp[h]
def rhs : ¬ @EquationRHS M inst :=by
 intro h
 have:=h (g 1) (g 0) (g 2)
 revert this
 change ¬ g 1=op (op (g 0) (op (g 2) (g 0))) (op (op (g 1) (g 1)) (g 0))
 simp (config:={decide:=true}) [op.eq_1,sz,P1,U,P3,P4,P5,P6,P7]
def N (t : M) : 1≤sz t :=by cases t <;> simp[sz] <;> omega
def E (a b : M) : sz (J a b)=sz a+sz b+1:=rfl
def sz_a1_lt {t : M} (h : tg t=2) : sz (a1 t)<sz t :=by obtain⟨a,b,rfl⟩:=tg_J _ h; simp[sz,a1]; have:=N b; omega
def sz_a2_lt {t : M} (h : tg t=2) : sz (a2 t)<sz t :=by obtain⟨a,b,rfl⟩:=tg_J _ h; simp[sz,a2]; have:=N a; omega
def V {c : Prop} [Decidable c] {a b u v : M} (h1 : a=J u v∨a=a1 v)
  (h2 : b=J u v∨b=a1 v) : (if c then a else b)=J u v∨(if c then a else b)=a1 v :=by
 by_cases h : c
 ·rw[if_pos h]; exact h1
 ·rw[if_neg h]; exact h2
def Wdig (u v : M) : op u v=J u v∨op u v=a1 v :=by
 rw[op.eq_1]
 exact V (Or.inr rfl) (V (Or.inr rfl) (V (Or.inr rfl) (V (Or.inr rfl) (V (Or.inr rfl) (V (Or.inr rfl) (V (Or.inr rfl) (Or.inl rfl)))))))
def Pdig {u v : M} (h : Pre u v) : tg v=2 :=by
 rcases h with h|h|h|h|h|h|h
 ·exact h.1
 ·exact h.1
 ·exact h
 ·exact h.1
 ·exact h.1
 ·exact h.1
 ·exact h.1
def R (u v : M) : op u v=J u v∨(tg v=2∧op u v=a1 v∧sz (op u v)<sz v) :=by
 by_cases h : Pre u v
 ·rcases Wdig u v with h1 | h1
  ·exact Or.inl h1
  ·have ht:=Pdig h
   exact Or.inr ⟨ht,h1,by rw[h1]; exact sz_a1_lt ht⟩
 ·exact Or.inl (op_free h)
def I {u v : M} (h : sz (op u v)<sz v) : op u v≠J u v :=by intro hc; rw[hc] at h; simp only[E] at h; have:=N u; omega
def G {c : Prop} [Decidable c] {a b u v : M} {Q : Prop} (h1 : c→Q) (h2 : b≠J u v→Q) :
  (if c then a else b)≠J u v→Q :=by
 by_cases h : c
 ·intro _; exact h1 h
 ·rw[if_neg h]; exact h2
def D {u v W : M} (he : a2 v=op W u) :
  (tg (a2 v)=2∧a2 (a2 v)=u)∨a2 v=a1 u :=by
 rcases Wdig W u with hf | hf
 ·rw[hf] at he; exact Or.inl ⟨by rw[he]; rfl,by rw[he]; rfl⟩
 ·exact Or.inr (he.trans hf)
def H {u v : M} (h : op u v≠J u v) :
  (tg (a2 v)=2∧a2 (a2 v)=u)∨a2 v=a1 u :=by
 rw[op.eq_1] at h
 revert h
 exact G
  (fun h => by have e:=h.2.2.2.2.1; rw[dif_pos (h.2.1)] at e; exact D e)
  (G
  (fun h => by have e:=h.2.2.2.2.1; rw[dif_pos (h.2.1)] at e; exact D e)
  (G
  (fun h => by have e:=h.2.2.2.2.1; rw[dif_pos (h.2.1)] at e; exact D e)
  (G
  (fun h => by have e:=h.2.2.2.2.1; rw[dif_pos (h.2.1)] at e; exact D e)
  (G
  (fun h => by have e:=h.2.2.2.2.1; rw[dif_pos (h.2.1)] at e; exact D e)
  (G
  (fun h => by have e:=h.2.2.2.2.1; rw[dif_pos (h.2.1)] at e; exact D e)
  (G
  (fun h => by have e:=h.2.2.2.2.2.2.1; rw[dif_pos (h.2.1)] at e; exact D e)
  ((fun hh => absurd rfl hh))))))))
def mxl {a b c d : M} (h1 : sz a<sz d) (h2 : sz b<sz d) :
  max (sz a) (sz b)<max (sz c) (sz d) :=by rw[Nat.max_def,Nat.max_def]; split <;> split <;> omega
def K {A B u v : M} (h1 : sz A<sz v) (h2 : sz B<sz v) : T A B<T u v :=
 msr_lt_of_max_lt (mxl h1 h2)
def GM {A B u v : M} (h4 : max (sz A) (sz B)≤max (sz u) (sz v))
  (h3 : sz A+sz B<sz u+sz v) : T A B<T u v :=by unfold T; have:=Nat.mul_le_mul h4 h4; omega
def GS {A B u v : M} (h1 : sz A≤sz u) (h2 : sz B≤sz u) (h3 : sz A+sz B<sz u+sz v) :
  T A B<T u v :=
 GM (by rw[Nat.max_def,Nat.max_def]; split <;> split <;> omega) h3
def GU {A B u v : M} (h1 : sz A≤sz u) (h2 : sz B≤sz v) (h3 : sz A+sz B<sz u+sz v) :
  T A B<T u v :=
 GM (by rw[Nat.max_def,Nat.max_def]; split <;> split <;> omega) h3
def L {c : Prop} [Decidable c] {a b r : M} (h1 : a=r) (h2 : b=r) :
  (if c then a else b)=r :=by
 by_cases h : c
 ·rw[if_pos h]; exact h1
 ·rw[if_neg h]; exact h2
def c1 (x y z : M) (ha : op z x=J z x) (hb : op y (J z x)=J y (J z x))
  (hc : op (J y (J z x)) y=J (J y (J z x)) y) :
  op y (J x (J (J y (J z x)) y))=x :=by
 rw[op.eq_1]
 refine (if_pos ⟨⟨rfl,rfl,rfl⟩,?_,?_,?_,?_,?_,?_⟩).trans rfl
 ·exact K (by simp only[a1_J_eq,a2_J_eq,E]; omega) (by simp only[E]; omega)
 ·exact K (by simp only[E]; omega) (by simp only[a1_J_eq,a2_J_eq,E]; omega)
 ·exact K (by simp only[a1_J_eq,a2_J_eq,E]; omega) (by simp only[a1_J_eq,E]; omega)
 ·rw[dif_pos (K (by simp only[a1_J_eq,a2_J_eq,E]; omega) (by simp only[E]; omega))]
  exact hc.symm
 ·rw[dif_pos (K (by simp only[E]; omega) (by simp only[a1_J_eq,a2_J_eq,E]; omega))]
  exact hb.symm
 ·rw[dif_pos (K (by simp only[a1_J_eq,a2_J_eq,E]; omega) (by simp only[a1_J_eq,E]; omega))]
  exact ha.symm
def c3 (x y z : M) (ha : op z x=J z x) (hb : op y (J z x)=z)
  (hc : op z y=J z y) : op y (J x (J z y))=x :=by
 rw[op.eq_1]
 refine L rfl (L rfl ((if_pos ⟨rfl,?_,?_,?_,?_,?_,?_⟩).trans rfl))
 ·exact K (by simp only[a1_J_eq,a2_J_eq,E]; omega) (by simp only[E]; omega)
 ·exact K (by simp only[a1_J_eq,a2_J_eq,E]; omega) (by simp only[a1_J_eq,E]; omega)
 ·exact K (by simp only[E]; omega) (by simp only[a1_J_eq,a2_J_eq,E]; omega)
 ·rw[dif_pos (K (by simp only[a1_J_eq,a2_J_eq,E]; omega) (by simp only[E]; omega))]
  exact hc.symm
 ·rw[dif_pos (K (by simp only[a1_J_eq,a2_J_eq,E]; omega) (by simp only[a1_J_eq,E]; omega))]
  exact ha.symm
 ·rw[dif_pos (K (by simp only[E]; omega) (by simp only[a1_J_eq,a2_J_eq,E]; omega))]
  exact hb.symm
def c2 (x y z : M) (htx : tg x=2) (hz : a2 (a2 x)=z) (ha : op z x=a1 x)
  (hb : op y (a1 x)=J y (a1 x)) (hc : op (J y (a1 x)) y=J (J y (a1 x)) y) :
  op y (J x (J (J y (a1 x)) y))=x :=by
 have s1:=sz_a1_lt htx
 rw[op.eq_1]
 refine L rfl ((if_pos ⟨⟨rfl,rfl,rfl⟩,?_,?_,?_,?_,?_,?_⟩).trans rfl)
 ·exact K (by simp only[a1_J_eq,a2_J_eq,E]; omega) (by simp only[E]; omega)
 ·exact K (by simp only[E]; omega) (by simp only[a1_J_eq,a2_J_eq,E]; omega)
 ·exact K (by simp only[a1_J_eq,a2_J_eq,E]; have:=X (a2 x); have:=X x; omega) (by simp only[a1_J_eq,E]; omega)
 ·rw[dif_pos (K (by simp only[a1_J_eq,a2_J_eq,E]; omega) (by simp only[E]; omega))]
  exact hc.symm
 ·rw[dif_pos (K (by simp only[E]; omega) (by simp only[a1_J_eq,a2_J_eq,E]; omega))]
  exact hb.symm
 ·rw[dif_pos (K (by simp only[a1_J_eq,a2_J_eq,E]; have:=X (a2 x); have:=X x; omega) (by simp only[a1_J_eq,E]; omega))]
  simp only[a1_J_eq,a2_J_eq]
  rw[hz]; exact ha.symm
def c4 (x y z : M) (htx : tg x=2) (hz : a2 (a2 x)=z) (ha : op z x=a1 x)
  (hb : op y (a1 x)=a1 (a1 x)) (hc : op (a1 (a1 x)) y=J (a1 (a1 x)) y) :
  op y (J x (J (a1 (a1 x)) y))=x :=by
 have s1:=sz_a1_lt htx
 have s2:=O (a1 x)
 rw[op.eq_1]
 refine L rfl (L rfl (L rfl (L rfl ((if_pos ⟨⟨rfl,htx⟩,?_,?_,?_,?_,?_,?_⟩).trans rfl))))
 ·exact K (by simp only[a1_J_eq,a2_J_eq,E]; omega) (by simp only[E]; omega)
 ·exact K (by simp only[E]; omega) (by simp only[a1_J_eq,a2_J_eq,E]; omega)
 ·exact K (by simp only[a1_J_eq,a2_J_eq,E]; have:=X (a2 x); have:=X x; omega) (by simp only[a1_J_eq,E]; omega)
 ·rw[dif_pos (K (by simp only[a1_J_eq,a2_J_eq,E]; omega) (by simp only[E]; omega))]
  exact hc.symm
 ·rw[dif_pos (K (by simp only[E]; omega) (by simp only[a1_J_eq,a2_J_eq,E]; omega))]
  simp only[a1_J_eq,a2_J_eq]; exact hb.symm
 ·rw[dif_pos (K (by simp only[a1_J_eq,a2_J_eq,E]; have:=X (a2 x); have:=X x; omega) (by simp only[a1_J_eq,E]; omega))]
  simp only[a1_J_eq,a2_J_eq]
  rw[hz]; exact ha.symm
def c6 (x y z : M) (htx : tg x=2) (hz1 : a2 (a2 x)=z) (hz2 : a2 (a2 y)=a1 (a1 x))
  (ha : op z x=a1 x) (hb : op y (a1 x)=a1 (a1 x)) (hc : op (a1 (a1 x)) y=a1 y) :
  op y (J x (a1 y))=x :=by
 have s1:=sz_a1_lt htx
 have s2:=O (a1 x)
 have s3 : sz (a2 (a2 y))=sz (a1 (a1 x)) :=by rw[hz2]
 have s4:=X (a2 y)
 have s5:=X y
 have s6:=N (a1 y)
 have s7:=X (a2 x)
 have s8:=X x
 have s9:=O x
 rw[op.eq_1]
 refine L rfl (L rfl (L rfl (L rfl (L rfl ((if_pos ⟨⟨rfl,htx⟩,?_,?_,?_,?_,?_,?_⟩).trans rfl)))))
 ·exact GS (by (try simp only[a1_J_eq,a2_J_eq,E]); omega) (by (try simp only[a1_J_eq,a2_J_eq,E]); omega) (by (try simp only[a1_J_eq,a2_J_eq,E]); omega)
 ·exact GU (by (try simp only[a1_J_eq,a2_J_eq,E]); omega) (by (try simp only[a1_J_eq,a2_J_eq,E]); omega) (by (try simp only[a1_J_eq,a2_J_eq,E]); omega)
 ·exact K (by (try simp only[a1_J_eq,a2_J_eq,E]); omega) (by (try simp only[a1_J_eq,a2_J_eq,E]); omega)
 ·rw[dif_pos (GS (by (try simp only[a1_J_eq,a2_J_eq,E]); omega) (by (try simp only[a1_J_eq,a2_J_eq,E]); omega) (by (try simp only[a1_J_eq,a2_J_eq,E]); omega))]
  simp only[a1_J_eq,a2_J_eq]; rw[hz2]; exact hc.symm
 ·rw[dif_pos (GU (by (try simp only[a1_J_eq,a2_J_eq,E]); omega) (by (try simp only[a1_J_eq,a2_J_eq,E]); omega) (by (try simp only[a1_J_eq,a2_J_eq,E]); omega))]
  simp only[a1_J_eq,a2_J_eq]; rw[hz2]; exact hb.symm
 ·rw[dif_pos (K (by (try simp only[a1_J_eq,a2_J_eq,E]); omega) (by (try simp only[a1_J_eq,a2_J_eq,E]); omega))]
  simp only[a1_J_eq,a2_J_eq]; rw[hz1]; exact ha.symm
def law (x y z : M) : op (y) (op (x) (op (op (y) (op (z) (x))) (y)))=x :=by
 rcases R x (op (op y (op z x)) y) with hd | ⟨-,hd,hsd⟩
 ·rw[hd]
  rcases R z x with ha | ⟨htx,ha,hsa⟩
  ·rw[ha]
   rcases R y (J z x) with hb | ⟨-,hb,hsb⟩
   ·rw[hb]
    rcases R (J y (J z x)) y with hc | ⟨hty,hc,hsc⟩
    ·rw[hc]; exact c1 x y z ha hb hc
    ·exfalso
     rcases H (I hsc) with⟨h1,h2⟩ | h2
     ·have e1:=X (a2 y); have e2:=X y
      have e3:=congrArg sz h2; simp only[E] at e3
      have:=N y; have:=N z; have:=N x; omega
     ·simp only[a1_J_eq] at h2
      have e:=sz_a2_lt hty; rw[h2] at e; omega
   ·rw[hb]; simp only[a1_J_eq] at hb ⊢
    rcases R z y with hc | ⟨hty,hc,hsc⟩
    ·rw[hc]; exact c3 x y z ha hb hc
    ·rw[hc]; sorry
  ·rw[ha]
   rcases R y (a1 x) with hb | ⟨-,hb,hsb⟩
   ·rw[hb]
    rcases R (J y (a1 x)) y with hc | ⟨hty,hc,hsc⟩
    ·rw[hc]
     rcases H (I hsa) with⟨-,hz⟩ | hz
     ·exact c2 x y z htx hz ha hb hc
     ·sorry
    ·exfalso
     rcases H (I hsc) with⟨h1,h2⟩ | h2
     ·have e1:=X (a2 y); have e2:=X y
      have e3:=congrArg sz h2; simp only[E] at e3
      have:=N y; have:=O x; have:=N x; omega
     ·simp only[a1_J_eq] at h2
      have e:=sz_a2_lt hty; rw[h2] at e; omega
   ·rw[hb]
    rcases R (a1 (a1 x)) y with hc | ⟨hty,hc,hsc⟩
    ·rw[hc]
     rcases H (I hsa) with⟨-,hz⟩ | hz
     ·exact c4 x y z htx hz ha hb hc
     ·sorry
    ·rw[hc]
     rcases H (I hsa) with⟨-,hz1⟩ | hz1
     ·rcases H (I hsc) with⟨-,hz2⟩ | hz2
      ·exact c6 x y z htx hz1 hz2 ha hb hc
      ·sorry
     ·sorry
 ·rw[hd]; sorry
def lhs : @EquationLHS M inst :=by
 intro x y z
 exact (law x y z).symm
end submission
def submission : Goal :=
 Exists.intro submission.M (Exists.intro submission.inst
  (And.intro submission.lhs submission.rhs))