import JudgeProblem

def submission : Goal := by
  intro G _ h
  have hlem0 : ∀ a b c d : G, (((a ◇ c) ◇ ((b ◇ ((a ◇ c) ◇ d)) ◇ b)) ◇ a) = a := by
    intro a b c d
    exact (congrArg (fun t => ((t ◇ ((b ◇ ((a ◇ c) ◇ d)) ◇ b)) ◇ a)) (h (a ◇ c) b d)).trans (((h a ((b ◇ ((a ◇ c) ◇ d)) ◇ b) c).symm))
  have hlem1 : ∀ a b c d : G, (((b ◇ a) ◇ b) ◇ ((c ◇ (a ◇ d)) ◇ c)) = ((c ◇ (a ◇ d)) ◇ c) := by
    intro a b c d
    exact (congrArg (fun t => (((b ◇ t) ◇ b) ◇ ((c ◇ (a ◇ d)) ◇ c))) (h a c d)).trans (((h ((c ◇ (a ◇ d)) ◇ c) b a).symm))
  have hlem2 : ∀ a b c d e : G, (((b ◇ ((c ◇ (a ◇ e)) ◇ c)) ◇ b) ◇ ((d ◇ a) ◇ d)) = ((d ◇ a) ◇ d) := by
    intro a b c d e
    exact (congrArg (fun t => (((b ◇ t) ◇ b) ◇ ((d ◇ a) ◇ d))) ((hlem1 a d c e).symm)).trans (((h ((d ◇ a) ◇ d) b ((c ◇ (a ◇ e)) ◇ c)).symm))
  have hlem3 : ∀ a b c d : G, (((b ◇ (a ◇ d)) ◇ (((b ◇ (a ◇ d)) ◇ b) ◇ ((c ◇ a) ◇ c))) ◇ b) = b := by
    intro a b c d
    exact (congrArg (fun t => (((b ◇ (a ◇ d)) ◇ (t ◇ ((c ◇ a) ◇ c))) ◇ b)) ((hlem1 a c b d).symm)).trans ((hlem0 b ((c ◇ a) ◇ c) (a ◇ d) b))
  have hlem4 : ∀ a b c d : G, ((((c ◇ (a ◇ d)) ◇ c) ◇ ((b ◇ a) ◇ b)) ◇ (c ◇ (a ◇ d))) = (c ◇ (a ◇ d)) := by
    intro a b c d
    exact (congrArg (fun t => ((((c ◇ (a ◇ d)) ◇ c) ◇ ((b ◇ t) ◇ b)) ◇ (c ◇ (a ◇ d)))) (h a c d)).trans ((hlem0 (c ◇ (a ◇ d)) b c a))
  have hlem5 : ∀ a b c d e : G, ((((d ◇ a) ◇ d) ◇ ((b ◇ ((c ◇ (a ◇ e)) ◇ c)) ◇ b)) ◇ (d ◇ a)) = (d ◇ a) := by
    intro a b c d e
    exact (congrArg (fun t => ((((d ◇ a) ◇ d) ◇ ((b ◇ t) ◇ b)) ◇ (d ◇ a))) ((hlem1 a d c e).symm)).trans ((hlem0 (d ◇ a) b d ((c ◇ (a ◇ e)) ◇ c)))
  have hlem6 : ∀ a b c d e : G, ((((b ◇ (a ◇ e)) ◇ b) ◇ ((d ◇ a) ◇ d)) ◇ ((c ◇ a) ◇ c)) = ((c ◇ a) ◇ c) := by
    intro a b c d e
    exact (congrArg (fun t => ((t ◇ ((d ◇ a) ◇ d)) ◇ ((c ◇ a) ◇ c))) ((hlem1 a d b e).symm)).trans ((hlem2 a ((d ◇ a) ◇ d) b c e))
  have hlem7 : ∀ a b c d e : G, ((((d ◇ a) ◇ d) ◇ (((b ◇ (a ◇ e)) ◇ b) ◇ ((c ◇ a) ◇ c))) ◇ (d ◇ a)) = (d ◇ a) := by
    intro a b c d e
    exact (congrArg (fun t => ((((d ◇ a) ◇ d) ◇ (t ◇ ((c ◇ a) ◇ c))) ◇ (d ◇ a))) ((hlem1 a c b e).symm)).trans ((hlem5 a ((c ◇ a) ◇ c) b d e))
  have hlem8 : ∀ a b c d : G, (((b ◇ (b ◇ d)) ◇ b) ◇ ((a ◇ ((b ◇ (b ◇ d)) ◇ c)) ◇ a)) = ((a ◇ ((b ◇ (b ◇ d)) ◇ c)) ◇ a) := by
    intro a b c d
    exact (congrArg (fun t => (t ◇ ((a ◇ ((b ◇ (b ◇ d)) ◇ c)) ◇ a))) ((hlem1 b (b ◇ (b ◇ d)) b d).symm)).trans ((hlem1 (b ◇ (b ◇ d)) ((b ◇ (b ◇ d)) ◇ b) a c))
  have hlem9 : ∀ a b c d e : G, (((a ◇ ((c ◇ ((b ◇ (b ◇ d)) ◇ e)) ◇ c)) ◇ a) ◇ ((b ◇ (b ◇ d)) ◇ b)) = ((b ◇ (b ◇ d)) ◇ b) := by
    intro a b c d e
    exact (congrArg (fun t => (((a ◇ t) ◇ a) ◇ ((b ◇ (b ◇ d)) ◇ b))) ((hlem8 c b e d).symm)).trans (((h ((b ◇ (b ◇ d)) ◇ b) a ((c ◇ ((b ◇ (b ◇ d)) ◇ e)) ◇ c)).symm))
  have hlem10 : ∀ a b c d : G, ((((a ◇ ((b ◇ (b ◇ d)) ◇ c)) ◇ a) ◇ ((b ◇ (b ◇ d)) ◇ b)) ◇ ((b ◇ (b ◇ d)) ◇ b)) = ((b ◇ (b ◇ d)) ◇ b) := by
    intro a b c d
    exact (congrArg (fun t => ((t ◇ ((b ◇ (b ◇ d)) ◇ b)) ◇ ((b ◇ (b ◇ d)) ◇ b))) ((hlem8 a b c d).symm)).trans ((hlem9 ((b ◇ (b ◇ d)) ◇ b) b a d c))
  have hlem11 : ∀ a b c : G, (((((a ◇ (a ◇ c)) ◇ a) ◇ ((b ◇ a) ◇ b)) ◇ ((a ◇ (a ◇ c)) ◇ a)) ◇ ((a ◇ (a ◇ c)) ◇ a)) = ((a ◇ (a ◇ c)) ◇ a) := by
    intro a b c
    exact (congrArg (fun t => (((t ◇ ((b ◇ a) ◇ b)) ◇ ((a ◇ (a ◇ c)) ◇ a)) ◇ ((a ◇ (a ◇ c)) ◇ a))) ((hlem1 a b a c).symm)).trans ((hlem10 ((b ◇ a) ◇ b) a a c))
  have hlem12 : ∀ a b : G, (((b ◇ (b ◇ b)) ◇ b) ◇ ((a ◇ (b ◇ b)) ◇ a)) = ((a ◇ (b ◇ b)) ◇ a) := by
    intro a b
    exact (congrArg (fun t => (t ◇ ((a ◇ (b ◇ b)) ◇ a))) ((hlem11 b b b).symm)).trans ((hlem6 (b ◇ b) ((b ◇ (b ◇ b)) ◇ b) a b b))
  have hlem13 : ∀ a b : G, ((((a ◇ (b ◇ b)) ◇ a) ◇ ((b ◇ (b ◇ b)) ◇ b)) ◇ (a ◇ (b ◇ b))) = (a ◇ (b ◇ b)) := by
    intro a b
    exact (congrArg (fun t => ((((a ◇ (b ◇ b)) ◇ a) ◇ t) ◇ (a ◇ (b ◇ b)))) ((hlem11 b b b).symm)).trans ((hlem7 (b ◇ b) ((b ◇ (b ◇ b)) ◇ b) b a b))
  have hlem14 : ∀ a : G, (((a ◇ (a ◇ a)) ◇ a) ◇ (a ◇ (a ◇ a))) = (a ◇ (a ◇ a)) := by
    intro a
    exact (congrArg (fun t => (t ◇ (a ◇ (a ◇ a)))) ((hlem12 a a).symm)).trans ((hlem13 a a))
  have hlem15 : ∀ a b c : G, (((a ◇ (b ◇ c)) ◇ (((a ◇ (b ◇ c)) ◇ a) ◇ (b ◇ (b ◇ b)))) ◇ a) = a := by
    intro a b c
    exact (congrArg (fun t => (((a ◇ (b ◇ c)) ◇ (((a ◇ (b ◇ c)) ◇ a) ◇ t)) ◇ a)) ((hlem14 b).symm)).trans ((hlem3 b a (b ◇ (b ◇ b)) c))
  have hlem16 : ∀ a b c : G, ((((b ◇ (a ◇ c)) ◇ b) ◇ (a ◇ (a ◇ a))) ◇ (b ◇ (a ◇ c))) = (b ◇ (a ◇ c)) := by
    intro a b c
    exact (congrArg (fun t => ((((b ◇ (a ◇ c)) ◇ b) ◇ t) ◇ (b ◇ (a ◇ c)))) ((hlem14 a).symm)).trans ((hlem4 a (a ◇ (a ◇ a)) b c))
  have hlem17 : ∀ a : G, ((a ◇ (a ◇ a)) ◇ (a ◇ (a ◇ a))) = (a ◇ (a ◇ a)) := by
    intro a
    exact (congrArg (fun t => (t ◇ (a ◇ (a ◇ a)))) ((hlem14 a).symm)).trans ((hlem16 a a a))
  have hlem18 : ∀ a : G, ((a ◇ (a ◇ a)) ◇ a) = a := by
    intro a
    exact (congrArg (fun t => (t ◇ a)) ((hlem17 a).symm)).trans ((congrArg (fun t => (((a ◇ (a ◇ a)) ◇ t) ◇ a)) ((hlem14 a).symm)).trans ((hlem15 a a a)))
  have hlem19 : ∀ a : G, (a ◇ a) = a := by
    intro a
    exact (congrArg (fun t => (t ◇ a)) ((hlem18 a).symm)).trans (((h a a a).symm))
  have hlem20 : ∀ a b : G, ((a ◇ b) ◇ a) = a := by
    intro a b
    exact (congrArg (fun t => (t ◇ a)) ((hlem19 (a ◇ b)).symm)).trans ((congrArg (fun t => (((a ◇ b) ◇ t) ◇ a)) ((hlem18 (a ◇ b)).symm)).trans ((hlem0 a (a ◇ b) b (a ◇ b))))
  have hlem21 : ∀ a b : G, (a ◇ b) = b := by
    intro a b
    exact (congrArg (fun t => (t ◇ b)) ((hlem20 a b).symm)).trans ((congrArg (fun t => (((a ◇ t) ◇ a) ◇ b)) ((hlem19 b).symm)).trans (((h b a b).symm)))
  intro x y
  exact ((hlem21 y x).symm)
