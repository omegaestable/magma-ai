import JudgeProblem
set_option linter.unusedSimpArgs false
set_option linter.unusedVariables false
set_option warn.classDefReducibility false
inductive submission.M : Type where
 | E : submission.M
 | g : Nat→submission.M
 | P : submission.M→submission.M→submission.M
 | C : submission.M→submission.M
 deriving DecidableEq
namespace submission
open M
def tg : M→Nat
 | .E => 0
 | .g _ => 1
 | .P _ _ => 2
 | .C _ => 3
def a1 : M→M
 | .P x _ => x
 | .C x => x
 | t => t
def a2 : M→M
 | .P _ x => x
 | t => t
def sz : M→Nat
 | .E => 1
 | .g _ => 1
 | .P b0 b1 => sz b0+sz b1+1
 | .C b0 => sz b0+1
def op (u v : M) : M :=
 let m:=a1 v
 let p1:=if h1 : sz (a1 m)+sz (a2 m)<sz u+sz v then op (a1 m) (a2 m) else E
 let p2:=if h2 : sz u+sz (a2 m)<sz u+sz v then op u (a2 m) else E
 let p3:=if h3 : sz E+sz u<sz u+sz v then op E u else E
 let p4:=if h4 : sz u+sz m<sz u+sz v then op u m else E
 let p5:=if h5 : sz E+sz m<sz u+sz v then op E m else E
 if u=v then E
 else if tg v=3∧u≠E∧tg m=3∧a1 m=C u then E
 else if tg v=3∧tg m=2∧sz (a1 m)+sz (a2 m)<sz u+sz v ∧
   sz u+sz (a2 m)<sz u+sz v∧p1=m∧p2=a1 m then a2 m
 else if tg v=3∧u≠E∧sz E+sz u<sz u+sz v∧p3=m then u
 else if tg v=3∧m≠E∧sz u+sz m<sz u+sz v∧sz E+sz m<sz u+sz v∧p4=E then C p5
 else if v=E then C u
 else P u v
termination_by sz u+sz v
decreasing_by
 ·assumption
 ·assumption
 ·assumption
 ·assumption
 ·assumption
def inst : Magma M:={ op:=op }
def rhs : ¬ @EquationRHS M inst :=by
 intro h
 have:=h (g 0) E E
 revert this
 change ¬ g 0=op (op (op (op (op E E) E) (g 0)) (g 0)) E
 simp (config:={decide:=true}) [op.eq_1,sz,tg,a1,a2]
def L (t : M) : 1≤sz t :=by cases t <;> simp[sz] <;> omega
def SA1 (t : M) : sz (a1 t)≤sz t :=by cases t <;> simp[a1,sz] <;> omega
def Z (t : M) : sz (a2 t)≤sz t :=by cases t <;> simp[a2,sz] <;> omega
def T3 (t : M) (h : tg t=3) : t=C (a1 t) :=by cases t <;> simp_all[tg,a1]
def T2 (t : M) (h : tg t=2) : t=P (a1 t) (a2 t) :=by cases t <;> simp_all[tg,a1,a2]
@[simp] theorem szC (t : M) : sz (C t)=sz t+1:=rfl
@[simp] theorem szP (a b : M) : sz (P a b)=sz a+sz b+1:=rfl
@[simp] theorem a1C (t : M) : a1 (C t)=t:=rfl
@[simp] theorem a1P (a b : M) : a1 (P a b)=a:=rfl
@[simp] theorem a2P (a b : M) : a2 (P a b)=b:=rfl
@[simp] theorem tgC (t : M) : tg (C t)=3:=rfl
@[simp] theorem tgP (a b : M) : tg (P a b)=2:=rfl
@[simp] theorem tgE : tg E=0:=rfl
@[simp] theorem szE : sz E=1:=rfl
def oc (u v : M) : ∃ p1 p2 p3 p4 p5 : M,
  p1=(if h1 : sz (a1 (a1 v))+sz (a2 (a1 v))<sz u+sz v then op (a1 (a1 v)) (a2 (a1 v)) else E) ∧
  p2=(if h2 : sz u+sz (a2 (a1 v))<sz u+sz v then op u (a2 (a1 v)) else E) ∧
  p3=(if h3 : sz E+sz u<sz u+sz v then op E u else E) ∧
  p4=(if h4 : sz u+sz (a1 v)<sz u+sz v then op u (a1 v) else E) ∧
  p5=(if h5 : sz E+sz (a1 v)<sz u+sz v then op E (a1 v) else E) ∧
  op u v=(
 if u=v then E
 else if tg v=3∧u≠E∧tg (a1 v)=3∧a1 (a1 v)=C u then E
 else if tg v=3∧tg (a1 v)=2∧sz (a1 (a1 v))+sz (a2 (a1 v))<sz u+sz v ∧
   sz u+sz (a2 (a1 v))<sz u+sz v∧p1=a1 v∧p2=a1 (a1 v) then a2 (a1 v)
 else if tg v=3∧u≠E∧sz E+sz u<sz u+sz v∧p3=a1 v then u
 else if tg v=3∧a1 v≠E∧sz u+sz (a1 v)<sz u+sz v∧sz E+sz (a1 v)<sz u+sz v∧p4=E then C p5
 else if v=E then C u
 else P u v) :=
 ⟨_,_,_,_,_,rfl,rfl,rfl,rfl,rfl,op.eq_1 u v⟩
def W (u : M) : op u u=E :=by
 obtain⟨p1,p2,p3,p4,p5,-,-,-,-,-,hop⟩:=oc u u
 rw[hop,if_pos rfl]
def O {u : M} (h : u≠E) : op u E=C u :=by
 obtain⟨p1,p2,p3,p4,p5,-,-,-,-,-,hop⟩:=oc u E
 rw[hop,if_neg h]
 simp only[tgE]
 simp
def I {u v : M} (h1 : u≠v) (h2 : tg v≠3) (h3 : v≠E) : op u v=P u v :=by
 obtain⟨p1,p2,p3,p4,p5,-,-,-,-,-,hop⟩:=oc u v
 rw[hop,if_neg h1,if_neg (by simp[h2]),if_neg (by simp[h2]),if_neg (by simp[h2]),
  if_neg (by simp[h2]),if_neg h3]
def V (u m : M) : op u (C m) =
  (if u=C m then E
  else if u≠E∧tg m=3∧a1 m=C u then E
  else if tg m=2∧op (a1 m) (a2 m)=m∧op u (a2 m)=a1 m then a2 m
  else if u≠E∧op E u=m then u
  else if m≠E∧op u m=E then C (op E m)
  else P u (C m)) :=by
 obtain⟨p1,p2,p3,p4,p5,hp1,hp2,hp3,hp4,hp5,hop⟩:=oc u (C m)
 have e2 : sz u+sz (a2 (a1 (C m)))<sz u+sz (C m) :=by have:=Z m; simp; omega
 have e3 : sz E+sz u<sz u+sz (C m) :=by have:=L m; simp; omega
 have e4 : sz u+sz (a1 (C m))<sz u+sz (C m) :=by simp
 have e5 : sz E+sz (a1 (C m))<sz u+sz (C m) :=by have:=L u; simp; omega
 rw[dif_pos e2] at hp2; rw[dif_pos e3] at hp3; rw[dif_pos e4] at hp4; rw[dif_pos e5] at hp5
 simp only[a1C] at hp2 hp3 hp4 hp5
 subst hp2; subst hp3; subst hp4; subst hp5
 have E2 : (sz u+sz (a2 m)<sz u+sz (C m))=True:=eq_true e2
 have E3 : (sz E+sz u<sz u+sz (C m))=True:=eq_true e3
 have E4 : (sz u+sz m<sz u+sz (C m))=True:=eq_true e4
 have E5 : (sz E+sz m<sz u+sz (C m))=True:=eq_true e5
 by_cases hm : tg m=2
 ·have e1 : sz (a1 (a1 (C m)))+sz (a2 (a1 (C m)))<sz u+sz (C m) :=by have h:=congrArg sz (T2 m hm); have:=L u; simp at h ⊢; omega
  rw[dif_pos e1] at hp1; simp only[a1C] at hp1; subst hp1
  have E1 : (sz (a1 m)+sz (a2 m)<sz u+sz (C m))=True:=eq_true e1
  rw[hop]; simp only[a1C,tgC,E1,E2,E3,E4,E5,true_and,reduceCtorEq,false_and,if_false]
 ·have H2 : (tg m=2)=False:=eq_false hm
  rw[hop]; simp only[a1C,tgC,H2,E2,E3,E4,E5,true_and,false_and,if_false,
   reduceCtorEq]
def G {t : M} (h : tg t=3) : ∃ s,t=C s :=by cases t <;> simp_all[tg]
def G2 {t : M} (h : tg t=2) : ∃ a b,t=P a b :=by cases t <;> simp_all[tg]
def T {u v : M} (h : op u v=E) :
  u=v∨(u≠E∧tg v=3∧tg (a1 v)=3∧a1 (a1 v)=C u) :=by
 by_cases huv : u=v
 ·exact Or.inl huv
 refine Or.inr ?_
 by_cases hv : tg v=3
 ·obtain⟨m,rfl⟩:=G hv
  rw[V,if_neg huv] at h
  split at h
  ·rename_i k; exact⟨k.1,rfl,k.2.1,k.2.2⟩
  split at h
  ·exfalso; rename_i k
   obtain⟨k1,k2,-⟩:=k
   obtain⟨a,b,rfl⟩:=G2 k1
   simp only[a1P,a2P] at h k2
   subst h
   by_cases ha : a=E
   ·subst ha; rw[W] at k2; exact absurd k2 (by simp)
   ·rw[O ha] at k2; exact absurd k2 (by simp)
  split at h
  ·exfalso; rename_i k; exact k.1 h
  split at h
  ·exact absurd h (by simp)
  ·exact absurd h (by simp)
 ·exfalso
  by_cases hE : v=E
  ·subst hE
   by_cases hu : u=E
   ·exact huv (hu.trans rfl)
   ·rw[O hu] at h; exact absurd h (by simp)
  ·rw[I huv hv hE] at h; exact absurd h (by simp)
def Q (n : Nat) : ∀ u v : M,sz v≤n→sz u≤sz (op u v)+sz v :=by
 induction n with
 | zero => intro u v hn; have:=L v; omega
 | succ n ih =>
  intro u v hn
  by_cases hv : tg v=3
  ·obtain⟨m,rfl⟩:=G hv
   simp only[szC] at hn
   rw[V]
   split
   ·rename_i k; have:=congrArg sz k; simp only[szC,szE] at this ⊢; omega
   split
   ·rename_i k
    have h1:=congrArg sz (T3 m k.2.1)
    have h2:=congrArg sz k.2.2
    simp only[szC,szE] at h1 h2 ⊢; omega
   split
   ·rename_i k
    obtain⟨k1,-,k3⟩:=k
    have hb:=ih u (a2 m) (by have:=Z m; omega)
    rw[k3] at hb
    have h1:=congrArg sz (T2 m k1)
    have h2:=Z m
    simp only[szC,szP] at h1 ⊢; omega
   split
   ·simp only[szC]; omega
   split
   ·rename_i k
    have hb:=ih u m (by omega)
    rw[k.2] at hb
    simp only[szC,szE] at hb ⊢; omega
   ·simp only[szC,szP]; omega
  ·by_cases hE : v=E
   ·subst hE
    by_cases hu : u=E
    ·subst hu; rw[W]; simp only[szE]; omega
    ·rw[O hu]; simp only[szC,szE]; omega
   ·by_cases huv : u=v
    ·subst huv; rw[W]; simp only[szE]; omega
    ·rw[I huv hv hE]; simp only[szP]; omega
def R (u v : M) : sz u≤sz (op u v)+sz v:=Q (sz v) u v (Nat.le_refl _)
def D (n : Nat) : ∀ u v : M,sz v≤n→op u v=v→v=E :=by
 induction n with
 | zero => intro u v hn _; exfalso; have:=L v; omega
 | succ n ih =>
  intro u v hn h
  by_cases hv : tg v=3
  ·exfalso
   obtain⟨m,rfl⟩:=G hv
   simp only[szC] at hn
   by_cases h1 : u=C m
   ·subst h1; rw[W] at h; exact absurd h (by simp)
   rw[V,if_neg h1] at h
   split at h
   ·exact absurd h (by simp)
   split at h
   ·rename_i k
    obtain⟨k1,-,-⟩:=k
    have e1:=congrArg sz (T2 m k1)
    have e2:=congrArg sz h
    simp only[szC,szP] at e1 e2; omega
   split at h
   ·exact h1 h
   split at h
   ·rename_i k
    have : op E m=m :=by have:=congrArg a1 h; simpa using this
    exact k.1 (ih E m (by omega) this)
   ·exact absurd h (by simp)
  ·by_cases hE : v=E
   ·exact hE
   by_cases huv : u=v
   ·subst huv; rw[W] at h; exact h.symm
   ·rw[I huv hv hE] at h
    exfalso; have:=congrArg sz h; simp only[szP] at this; have:=L u; omega
def U {u v : M} (h : op u v=v) : v=E:=D (sz v) u v (Nat.le_refl _) h
def Y (t : M) : op E t=E∨op E t=P E t ∨
  (tg t=3∧tg (a1 t)=2∧op E t=a2 (a1 t)∧op E (a2 (a1 t))=a1 (a1 t)) :=by
 by_cases hv : tg t=3
 ·obtain⟨m,rfl⟩:=G hv
  rw[V]
  split
  ·rename_i k; exact absurd k (by simp)
  split
  ·rename_i k; exact absurd rfl k.1
  split
  ·rename_i k; exact Or.inr (Or.inr ⟨rfl,k.1,rfl,k.2.2⟩)
  split
  ·rename_i k; exact absurd rfl k.1
  split
  ·rename_i k
   exfalso
   rcases T k.2 with h | ⟨h1,-⟩
   ·exact k.1 h.symm
   ·exact h1 rfl
  ·exact Or.inr (Or.inl rfl)
 ·by_cases hE : t=E
  ·subst hE; exact Or.inl (W E)
  ·exact Or.inr (Or.inl (I (fun q => hE q.symm) hv hE))
def H (y m : M) : op y (C m)=E ∨
  (op y (C m)=a2 m∧tg m=2∧op (a1 m) (a2 m)=m∧op y (a2 m)=a1 m) ∨
  (op y (C m)=y∧y≠E∧op E y=m) ∨
  (op y (C m)=C (op E m)∧m≠E∧op y m=E)∨op y (C m)=P y (C m) :=by
 rw[V]
 split
 ·exact Or.inl rfl
 split
 ·exact Or.inl rfl
 split
 ·rename_i k; exact Or.inr (Or.inl ⟨rfl,k.1,k.2.1,k.2.2⟩)
 split
 ·rename_i k; exact Or.inr (Or.inr (Or.inl ⟨rfl,k.1,k.2⟩))
 split
 ·rename_i k; exact Or.inr (Or.inr (Or.inr (Or.inl ⟨rfl,k.1,k.2⟩)))
 ·exact Or.inr (Or.inr (Or.inr (Or.inr rfl)))
def NB {y q m : M} (h1 : tg m=3) (h2 : tg (a1 m)=3) (h3 : sz q+2≤sz m)
  (h4 : q≠E) : op y (C m)≠q :=by
 intro hq
 have s1:=congrArg sz (T3 m h1)
 simp only[szC] at s1
 rcases H y m with h | ⟨-,k1,-,-⟩ | ⟨hr,k1,k2⟩ | ⟨hr,k1,k2⟩ | hr
 ·exact h4 (hq.symm.trans h)
 ·omega
 ·rw[hr.symm.trans hq] at k2
  rcases Y q with e | e | ⟨e1,-,e3,-⟩
  ·rw[e] at k2; rw[← k2] at h1; exact absurd h1 (by simp)
  ·rw[e] at k2; rw[← k2] at h1; exact absurd h1 (by simp)
  ·rw[e3] at k2
   have:=congrArg sz k2
   have b1:=Z (a1 q); have b2:=SA1 q
   omega
 ·rw[hq] at hr
  have sq:=congrArg sz hr
  simp only[szC] at sq
  rcases Y m with e | e | ⟨-,e2,-,-⟩
  ·rcases T e with j | ⟨j1,-,-,-⟩
   ·rw[← j] at h1; exact absurd h1 (by simp)
   ·exact j1 rfl
  ·rw[e] at sq; simp only[szP,szE] at sq; omega
  ·rw[e2] at h2; exact absurd h2 (by simp)
 ·rw[hq] at hr
  have:=congrArg sz hr
  simp only[szP,szC] at this
  have:=L y
  omega
def X {t : M} (h : tg t=3) : sz t=sz (a1 t)+1 :=by have:=congrArg sz (T3 t h); simp only[szC] at this; omega
def N {t : M} (h : tg t=2) : sz t=sz (a1 t)+sz (a2 t)+1 :=by have:=congrArg sz (T2 t h); simp only[szP] at this; omega
def EB {y b : M} (h : op y b=E) :
  y=b∨(y≠E∧tg b=3∧a1 (a1 b)=C y∧sz b=sz y+3) :=by
 rcases T h with j | ⟨j1,j2,j3,j4⟩
 ·exact Or.inl j
 ·refine Or.inr ⟨j1,j2,j4,?_⟩
  have s1:=X j2
  have s2:=X j3
  have s3:=congrArg sz j4
  simp only[szC] at s3; omega
def NE2 {y b : M} (h : op E y=b) (hb : tg b=3) : sz b≤sz y :=by
 rcases Y y with e | e | ⟨-,-,e3,-⟩
 ·rw[e] at h; rw[← h] at hb; exact absurd hb (by simp)
 ·rw[e] at h; rw[← h] at hb; exact absurd hb (by simp)
 ·rw[e3] at h
  have:=congrArg sz h
  have b1:=Z (a1 y); have b2:=SA1 y; omega
def TOP5 {y b : M} (hb : b≠E) (h : op y b=E) : op y (C b)=C (op E b) :=by
 have HB:=EB h
 rw[V]
 rw[if_neg (by
  intro j
  have s:=congrArg sz j
  simp only[szC] at s
  rcases HB with i | ⟨-,-,-,i4⟩
  ·rw[i] at s; omega
  ·omega)]
 rw[if_neg (by
  rintro⟨-,j2,j3⟩
  have s1:=X j2
  have s2:=congrArg sz j3
  simp only[szC] at s2
  rcases HB with i | ⟨-,-,-,i4⟩
  ·have:=congrArg sz i; omega
  ·omega)]
 rw[if_neg (by
  rintro⟨j1,-,j3⟩
  have n1:=R y (a2 b)
  rw[j3] at n1
  have s1:=N j1
  rcases HB with i | ⟨-,i2,-,-⟩
  ·rw[i] at n1; omega
  ·rw[j1] at i2; exact absurd i2 (by simp))]
 rw[if_neg (by
  rintro⟨j1,j2⟩
  rcases HB with i | ⟨-,i2,-,i4⟩
  ·rw[i] at j2; exact j1 (i.trans (U j2))
  ·have:=NE2 j2 i2; omega)]
 rw[if_pos ⟨hb,h⟩]
def TOP4 {y b : M} (hy : y≠E) (h : op E y=b) : op y (C b)=y :=by
 rcases Y y with e | e | ⟨e1,e2,e3,-⟩
 ·exfalso
  rw[e] at h; subst h
  rcases T e with c | ⟨c1,-,-,-⟩
  ·exact hy c.symm
  ·exact c1 rfl
 ·rw[e] at h; subst h
  rw[V]
  rw[if_neg (by intro j; have:=congrArg sz j; simp only[szC,szP,szE] at this; omega)]
  rw[if_neg (by rintro⟨-,j2,-⟩; exact absurd j2 (by simp))]
  rw[if_pos ⟨rfl,by simp only[a1P,a2P]; exact e,by simp only[a1P,a2P]; exact W y⟩]
  rfl
 ·have hbe : b=a2 (a1 y):=h.symm.trans e3
  have hb3 : sz b≤sz (a1 y) :=by rw[hbe]; exact Z (a1 y)
  have hy1 : sz y=sz (a1 y)+1:=X e1
  rw[V]
  rw[if_neg (by
   intro j
   rw[j] at e2 hbe
   simp only[a1C] at e2 hbe
   have s1:=N e2
   have s2:=congrArg sz hbe
   have s3:=L (a1 b)
   omega)]
  rw[if_neg (by
   rintro⟨-,j2,j3⟩
   have s1:=X j2
   have s2:=congrArg sz j3
   simp only[szC] at s2; omega)]
  rw[if_neg (by
   rintro⟨j1,-,j3⟩
   have n1:=R y (a2 b)
   rw[j3] at n1
   have s1:=N j1; omega)]
  rw[if_pos ⟨hy,h⟩]
def NM {y m : M} (hm : m≠E) : op y (C m)≠m :=by
 intro hq
 rcases H y m with e | ⟨e,k1,-,-⟩ | ⟨e,k1,k2⟩ | ⟨e,k1,-⟩ | e
 ·exact hm (hq.symm.trans e)
 ·rw[hq] at e
  have:=N k1; have:=Z m
  have:=congrArg sz e; omega
 ·rw[hq] at e
  subst e
  exact k1 (U k2)
 ·rw[hq] at e
  have s1 : tg m=3 :=by rw[e]; simp
  have s2 : a1 m=op E m :=by have:=congrArg a1 e; simpa using this
  have s3:=congrArg sz e
  simp only[szC] at s3
  rcases Y m with i | i | ⟨-,i2,i3,-⟩
  ·rcases T i with c | ⟨c1,-,-,-⟩
   ·exact hm c.symm
   ·exact c1 rfl
  ·rw[i] at s3; simp only[szP,szE] at s3; omega
  ·rw[i3] at s2
   have:=N i2
   have:=congrArg sz s2
   have:=Z (a1 m); omega
 ·rw[hq] at e
  have:=congrArg sz e
  simp only[szP,szC] at this
  have:=L y; omega
def CC {y m : M} (h1 : tg m=2) (h2 : op (a1 m) (a2 m)=m)
  (h3 : op (op y (C m)) (a2 m)=a1 m) : y=C m∨(a1 m=E∧op y (a2 m)=E) :=by
 rcases H y m with e | ⟨e,-,-,k3⟩ | ⟨e,k1,k2⟩ | ⟨e,k1,k2⟩ | e
 ·rcases T e with c | ⟨-,-,c3,-⟩
  ·exact Or.inl c
  ·exfalso; simp only[a1C,h1] at c3; exact absurd c3 (by simp)
 ·rw[e,W] at h3
  exact Or.inr ⟨h3.symm,k3.trans h3.symm⟩
 ·rw[e] at h3
  rcases Y y with i | i | ⟨i1,-,i3,-⟩
  ·exfalso; rw[i] at k2; rw[← k2] at h1; exact absurd h1 (by simp)
  ·rw[i] at k2
   refine Or.inr ⟨by rw[← k2]; simp,?_⟩
   rw[h3,← k2]; simp
  ·exfalso
   rw[i3] at k2
   have n1:=R y (a2 m)
   rw[h3] at n1
   have:=N h1
   have:=congrArg sz k2
   have:=X i1
   have:=Z (a1 y); omega
 ·exfalso
  rw[e] at h3
  have n1:=R (C (op E m)) (a2 m)
  rw[h3] at n1
  simp only[szC] at n1
  have s1:=N h1
  rcases T k2 with c | ⟨-,c2,-,-⟩
  ·subst c
   rcases Y y with i | i | ⟨i1,-,-,-⟩
   ·rcases T i with d | ⟨d1,-,-,-⟩
    ·exact k1 d.symm
    ·exact d1 rfl
   ·rw[i] at n1; simp only[szP,szE] at n1; omega
   ·rw[h1] at i1; exact absurd i1 (by simp)
  ·rw[h1] at c2; exact absurd c2 (by simp)
 ·exfalso
  rw[e] at h3
  have n1:=R (P y (C m)) (a2 m)
  rw[h3] at n1
  simp only[szP,szC] at n1
  have:=N h1
  have:=L y; omega
def CD {y m : M} (h1 : op y (C m)≠E) (h2 : op E (op y (C m))=m) :
  op y (op y (C m))=E :=by
 rcases H y m with e | ⟨e,k1,-,k3⟩ | ⟨e,-,-⟩ | ⟨e,k1,k2⟩ | e
 ·exact absurd e h1
 ·rw[e] at h2 ⊢
  rw[k3]
  rcases Y (a2 m) with i | i | ⟨i1,-,i3,-⟩
  ·rw[i] at h2; rw[← h2] at k1; exact absurd k1 (by simp)
  ·rw[i] at h2; rw[← h2]; simp
  ·exfalso
   rw[i3] at h2
   have:=congrArg sz h2
   have:=N k1
   have:=X i1
   have:=Z (a1 (a2 m)); omega
 ·rw[e]; exact W y
 ·exfalso
  rw[e] at h2
  rcases Y (C (op E m)) with i | i | ⟨-,i2,i3,i4⟩
  ·rw[i] at h2; exact k1 h2.symm
  ·rw[i] at h2
   have s1:=congrArg sz h2
   simp only[szP,szC,szE] at s1
   rcases Y m with j | j | ⟨j1,-,-,-⟩
   ·rcases T j with d | ⟨d1,-,-,-⟩
    ·rw[← d] at h2; exact absurd h2.symm (by simp)
    ·exact d1 rfl
   ·rw[j] at s1; simp only[szP,szE] at s1; omega
   ·rw[← h2] at j1; exact absurd j1 (by simp)
  ·simp only[a1C] at i2 i3 i4
   rw[i3] at h2
   have s1:=congrArg sz h2
   have s2:=N i2
   rcases Y m with j | j | ⟨j1,-,j3,-⟩
   ·rw[j] at i2; exact absurd i2 (by simp)
   ·rw[j] at i4; simp only[a1P,a2P] at i4; rw[j] at i4; exact absurd i4 (by simp)
   ·rw[j3] at s1 s2
    have:=X j1
    have:=Z (a1 m)
    have:=Z (a2 (a1 m)); omega
 ·exfalso
  rw[e] at h2
  rcases Y (P y (C m)) with i | i | ⟨i1,-,-,-⟩
  ·rcases T i with c | ⟨c1,-,-,-⟩
   ·exact absurd c (by simp)
   ·exact c1 rfl
  ·rw[i] at h2
   have:=congrArg sz h2
   simp only[szP,szC,szE] at this
   have:=L y; omega
  ·exact absurd i1 (by simp)
def FIN {y x : M} (hf : op (op y x) x=P (op y x) x) :
  op y (op (op (op y x) x) E)=x :=by
 rw[hf,O (by simp)]
 rw[V]
 rw[if_neg (by
  intro j
  have n:=R y x
  have s:=congrArg sz j
  simp only[szC,szP] at s; omega)]
 rw[if_neg (by rintro⟨-,j2,-⟩; exact absurd j2 (by simp))]
 rw[if_pos ⟨rfl,by simp only[a1P,a2P]; exact hf,by simp only[a1P,a2P]⟩]
 rfl
def law (x y z : M) : op y (op (op (op y x) x) (op z z))=x :=by
 rw[W z]
 by_cases hxE : x=E
 ·subst hxE
  by_cases hyE : y=E
  ·subst hyE; simp only[W]
  ·rw[O hyE,O (show (C y : M)≠E by simp),O (show (C (C y) : M)≠E by simp),
    V,if_neg (by intro j; have:=congrArg sz j; simp only[szC] at this; omega),
    if_pos ⟨hyE,rfl,rfl⟩]
 ·by_cases hx3 : tg x=3
  ·obtain⟨m,rfl⟩:=G hx3
   rcases H (op y (C m)) m with hw | ⟨hw,k1,k2,k3⟩ | ⟨hw,k1,k2⟩ | ⟨hw,k1,k2⟩ | hw
   ·exfalso
    rcases T hw with c | ⟨c1,-,c3,c4⟩
    ·exact absurd (U c) (by simp)
    ·simp only[a1C] at c3 c4
     have s1:=X c3
     have s2:=congrArg sz c4
     simp only[szC] at s2
     exact NB c3 (by rw[c4]; simp) (by omega) c1 rfl
   ·have hb : a2 m≠E :=by
     intro j
     rw[j] at k2
     by_cases ja : a1 m=E
     ·rw[ja,W] at k2; rw[← k2] at k1; exact absurd k1 (by simp)
     ·rw[O ja] at k2; rw[← k2] at k1; exact absurd k1 (by simp)
    rw[hw,O hb]
    rcases CC k1 k2 k3 with hc | ⟨d1,d2⟩
    ·rw[hc] at k3 ⊢
     rw[W] at k3
     refine TOP4 (by simp) ?_
     rw[V,if_neg (by simp),if_neg (by rintro⟨j1,-,-⟩; exact j1 rfl),
      if_pos ⟨k1,k2,k3⟩]
    ·rw[TOP5 hb d2,← d1,k2]
   ·rw[hw,O k1,TOP5 k1 (CD k1 k2),k2]
   ·exfalso
    rcases T k2 with c | ⟨c1,c2,c3,c4⟩
    ·exact NM k1 c
    ·have s1:=X c2
     have s2:=X c3
     have s3:=congrArg sz c4
     simp only[szC] at s3
     exact NB c2 c3 (by omega) c1 rfl
   ·exact FIN hw
  ·exact FIN (I (fun j => hxE (U j)) hx3 hxE)
def lhs : @EquationLHS M inst :=by
 intro x y z
 exact (law x y z).symm
end submission
def submission : Goal :=
 Exists.intro submission.M (Exists.intro submission.inst
  (And.intro submission.lhs submission.rhs))