import JudgeProblem

def submission : Goal := by
  intro G _ h
  have hlem0 : ∀ a b c d : G, (a ◇ ((b ◇ ((d ◇ (c ◇ a)) ◇ b)) ◇ (c ◇ a))) = a := by
    intro a b c d
    exact (congrArg (fun t => (a ◇ ((b ◇ ((d ◇ (c ◇ a)) ◇ b)) ◇ t))) (h (c ◇ a) b d)).trans (((h a (b ◇ ((d ◇ (c ◇ a)) ◇ b)) c).symm))
  have hlem1 : ∀ a b c d : G, ((c ◇ ((d ◇ a) ◇ c)) ◇ (b ◇ (a ◇ b))) = (c ◇ ((d ◇ a) ◇ c)) := by
    intro a b c d
    exact (congrArg (fun t => ((c ◇ ((d ◇ a) ◇ c)) ◇ (b ◇ (t ◇ b)))) (h a c d)).trans (((h (c ◇ ((d ◇ a) ◇ c)) b a).symm))
  have hlem2 : ∀ a b c d e : G, ((d ◇ (a ◇ d)) ◇ (b ◇ ((c ◇ ((e ◇ a) ◇ c)) ◇ b))) = (d ◇ (a ◇ d)) := by
    intro a b c d e
    exact (congrArg (fun t => ((d ◇ (a ◇ d)) ◇ (b ◇ (t ◇ b)))) ((hlem1 a d c e).symm)).trans (((h (d ◇ (a ◇ d)) b (c ◇ ((e ◇ a) ◇ c))).symm))
  have hlem3 : ∀ a b c d : G, (b ◇ (((c ◇ (a ◇ c)) ◇ (b ◇ ((d ◇ a) ◇ b))) ◇ ((d ◇ a) ◇ b))) = b := by
    intro a b c d
    exact (congrArg (fun t => (b ◇ (((c ◇ (a ◇ c)) ◇ t) ◇ ((d ◇ a) ◇ b)))) ((hlem1 a c b d).symm)).trans ((hlem0 b (c ◇ (a ◇ c)) (d ◇ a) b))
  have hlem4 : ∀ a b c d : G, (((d ◇ a) ◇ c) ◇ ((b ◇ (a ◇ b)) ◇ (c ◇ ((d ◇ a) ◇ c)))) = ((d ◇ a) ◇ c) := by
    intro a b c d
    exact (congrArg (fun t => (((d ◇ a) ◇ c) ◇ ((b ◇ (t ◇ b)) ◇ (c ◇ ((d ◇ a) ◇ c))))) (h a c d)).trans ((hlem0 ((d ◇ a) ◇ c) b c a))
  have hlem5 : ∀ a b c d e : G, ((a ◇ d) ◇ ((b ◇ ((c ◇ ((e ◇ a) ◇ c)) ◇ b)) ◇ (d ◇ (a ◇ d)))) = (a ◇ d) := by
    intro a b c d e
    exact (congrArg (fun t => ((a ◇ d) ◇ ((b ◇ (t ◇ b)) ◇ (d ◇ (a ◇ d))))) ((hlem1 a d c e).symm)).trans ((hlem0 (a ◇ d) b d (c ◇ ((e ◇ a) ◇ c))))
  have hlem6 : ∀ a b c d e : G, ((c ◇ (a ◇ c)) ◇ ((d ◇ (a ◇ d)) ◇ (b ◇ ((e ◇ a) ◇ b)))) = (c ◇ (a ◇ c)) := by
    intro a b c d e
    exact (congrArg (fun t => ((c ◇ (a ◇ c)) ◇ ((d ◇ (a ◇ d)) ◇ t))) ((hlem1 a d b e).symm)).trans ((hlem2 a (d ◇ (a ◇ d)) b c e))
  have hlem7 : ∀ a b c d e : G, ((a ◇ d) ◇ (((c ◇ (a ◇ c)) ◇ (b ◇ ((e ◇ a) ◇ b))) ◇ (d ◇ (a ◇ d)))) = (a ◇ d) := by
    intro a b c d e
    exact (congrArg (fun t => ((a ◇ d) ◇ (((c ◇ (a ◇ c)) ◇ t) ◇ (d ◇ (a ◇ d))))) ((hlem1 a c b e).symm)).trans ((hlem5 a (c ◇ (a ◇ c)) b d e))
  have hlem8 : ∀ a b c d : G, ((b ◇ ((c ◇ ((d ◇ a) ◇ a)) ◇ b)) ◇ (a ◇ ((d ◇ a) ◇ a))) = (b ◇ ((c ◇ ((d ◇ a) ◇ a)) ◇ b)) := by
    intro a b c d
    exact (congrArg (fun t => ((b ◇ ((c ◇ ((d ◇ a) ◇ a)) ◇ b)) ◇ t)) ((hlem1 a ((d ◇ a) ◇ a) a d).symm)).trans ((hlem1 ((d ◇ a) ◇ a) (a ◇ ((d ◇ a) ◇ a)) b c))
  have hlem9 : ∀ a b c d e : G, ((a ◇ ((d ◇ a) ◇ a)) ◇ (b ◇ ((c ◇ ((e ◇ ((d ◇ a) ◇ a)) ◇ c)) ◇ b))) = (a ◇ ((d ◇ a) ◇ a)) := by
    intro a b c d e
    exact (congrArg (fun t => ((a ◇ ((d ◇ a) ◇ a)) ◇ (b ◇ (t ◇ b)))) ((hlem8 a c e d).symm)).trans (((h (a ◇ ((d ◇ a) ◇ a)) b (c ◇ ((e ◇ ((d ◇ a) ◇ a)) ◇ c))).symm))
  have hlem10 : ∀ a b c d : G, ((a ◇ ((d ◇ a) ◇ a)) ◇ ((a ◇ ((d ◇ a) ◇ a)) ◇ (b ◇ ((c ◇ ((d ◇ a) ◇ a)) ◇ b)))) = (a ◇ ((d ◇ a) ◇ a)) := by
    intro a b c d
    exact (congrArg (fun t => ((a ◇ ((d ◇ a) ◇ a)) ◇ ((a ◇ ((d ◇ a) ◇ a)) ◇ t))) ((hlem8 a b c d).symm)).trans ((hlem9 a (a ◇ ((d ◇ a) ◇ a)) b d c))
  have hlem11 : ∀ a b c : G, ((a ◇ ((c ◇ a) ◇ a)) ◇ ((a ◇ ((c ◇ a) ◇ a)) ◇ ((b ◇ (a ◇ b)) ◇ (a ◇ ((c ◇ a) ◇ a))))) = (a ◇ ((c ◇ a) ◇ a)) := by
    intro a b c
    exact (congrArg (fun t => ((a ◇ ((c ◇ a) ◇ a)) ◇ ((a ◇ ((c ◇ a) ◇ a)) ◇ ((b ◇ (a ◇ b)) ◇ t)))) ((hlem1 a b a c).symm)).trans ((hlem10 a (b ◇ (a ◇ b)) a c))
  have hlem12 : ∀ a b : G, ((a ◇ ((b ◇ b) ◇ a)) ◇ (b ◇ ((b ◇ b) ◇ b))) = (a ◇ ((b ◇ b) ◇ a)) := by
    intro a b
    exact (congrArg (fun t => ((a ◇ ((b ◇ b) ◇ a)) ◇ t)) ((hlem11 b b b).symm)).trans ((hlem6 (b ◇ b) (b ◇ ((b ◇ b) ◇ b)) a b b))
  have hlem13 : ∀ a b : G, (((b ◇ b) ◇ a) ◇ ((b ◇ ((b ◇ b) ◇ b)) ◇ (a ◇ ((b ◇ b) ◇ a)))) = ((b ◇ b) ◇ a) := by
    intro a b
    exact (congrArg (fun t => (((b ◇ b) ◇ a) ◇ (t ◇ (a ◇ ((b ◇ b) ◇ a))))) ((hlem11 b b b).symm)).trans ((hlem7 (b ◇ b) (b ◇ ((b ◇ b) ◇ b)) b a b))
  have hlem14 : ∀ a : G, (((a ◇ a) ◇ a) ◇ (a ◇ ((a ◇ a) ◇ a))) = ((a ◇ a) ◇ a) := by
    intro a
    exact (congrArg (fun t => (((a ◇ a) ◇ a) ◇ t)) ((hlem12 a a).symm)).trans ((hlem13 a a))
  have hlem15 : ∀ a b c : G, (a ◇ ((((b ◇ b) ◇ b) ◇ (a ◇ ((c ◇ b) ◇ a))) ◇ ((c ◇ b) ◇ a))) = a := by
    intro a b c
    exact (congrArg (fun t => (a ◇ ((t ◇ (a ◇ ((c ◇ b) ◇ a))) ◇ ((c ◇ b) ◇ a)))) ((hlem14 b).symm)).trans ((hlem3 b a ((b ◇ b) ◇ b) c))
  have hlem16 : ∀ a b c : G, (((c ◇ b) ◇ a) ◇ (((b ◇ b) ◇ b) ◇ (a ◇ ((c ◇ b) ◇ a)))) = ((c ◇ b) ◇ a) := by
    intro a b c
    exact (congrArg (fun t => (((c ◇ b) ◇ a) ◇ (t ◇ (a ◇ ((c ◇ b) ◇ a))))) ((hlem14 b).symm)).trans ((hlem4 b ((b ◇ b) ◇ b) a c))
  have hlem17 : ∀ a : G, (((a ◇ a) ◇ a) ◇ ((a ◇ a) ◇ a)) = ((a ◇ a) ◇ a) := by
    intro a
    exact (congrArg (fun t => (((a ◇ a) ◇ a) ◇ t)) ((hlem14 a).symm)).trans ((hlem16 a a a))
  have hlem18 : ∀ a : G, (a ◇ ((a ◇ a) ◇ a)) = a := by
    intro a
    exact (congrArg (fun t => (a ◇ t)) ((hlem17 a).symm)).trans ((congrArg (fun t => (a ◇ (t ◇ ((a ◇ a) ◇ a)))) ((hlem14 a).symm)).trans ((hlem15 a a a)))
  have hlem19 : ∀ a : G, (a ◇ a) = a := by
    intro a
    exact (congrArg (fun t => (a ◇ t)) ((hlem18 a).symm)).trans (((h a a a).symm))
  have hlem20 : ∀ a b : G, (a ◇ (b ◇ a)) = a := by
    intro a b
    exact (congrArg (fun t => (a ◇ t)) ((hlem19 (b ◇ a)).symm)).trans ((congrArg (fun t => (a ◇ (t ◇ (b ◇ a)))) ((hlem18 (b ◇ a)).symm)).trans ((hlem0 a (b ◇ a) b (b ◇ a))))
  have hlem21 : ∀ a b : G, (b ◇ a) = b := by
    intro a b
    exact (congrArg (fun t => (b ◇ t)) ((hlem20 a b).symm)).trans ((congrArg (fun t => (b ◇ (a ◇ (t ◇ a)))) ((hlem19 b).symm)).trans (((h b a b).symm)))
  intro x y
  exact ((hlem21 y x).symm)
