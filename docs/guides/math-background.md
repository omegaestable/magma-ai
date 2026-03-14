# Math Background

This note summarizes the mathematical setting of the repository using the project paper in [../paper/source](../paper/source).

## 1. Magmas And Equational Laws

A magma is a set $M$ equipped with a single binary operation $\diamond : M \times M \to M$. Nothing else is assumed. In particular, associativity, commutativity, identity elements, and inverses are all optional and must be justified law by law.

An equational law is a formal identity built from variables and the binary operation. Examples:

- `x = x`
- `x = y`
- `x \diamond y = y \diamond x`
- `x \diamond (y \diamond z) = (x \diamond y) \diamond z`

The repository numbers these laws according to the Equational Theories Project convention. Four especially important laws are:

- Eq1: `x = x`
- Eq2: `x = y`
- Eq43: `x \diamond y = y \diamond x`
- Eq4512: `x \diamond (y \diamond z) = (x \diamond y) \diamond z`

Eq1 is the maximal law in the implication preorder, and Eq2 is the minimal one: every law implies Eq1, and Eq2 implies every law.

## 2. What Implication Means

If $E_1$ and $E_2$ are laws, then

$$
E_1 \models E_2
$$

means: every magma satisfying $E_1$ also satisfies $E_2$.

This is the central binary classification problem used in the challenge. The repository studies the question at two levels:

- mathematically, by searching for proofs and counterexamples;
- operationally, by building a compact cheatsheet that helps a model answer correctly.

## 3. Why This Is Nontrivial

The project paper emphasizes two important facts.

First, implication between equational laws is rich enough to capture many familiar algebraic structures and many unfamiliar ones. Even very small laws can behave in subtle ways.

Second, Birkhoff completeness gives a rewriting perspective for positive implication, but the general implication problem is undecidable. That is why the full project required a mix of ideas rather than a single uniform decision procedure.

## 4. Scale Of The Underlying Project

From the paper:

- 4694 laws of order at most 4 were studied.
- This yields 22,028,942 non-reflexive implication questions.
- The larger Equational Theories Project organized these laws into 1415 equivalence classes.
- The largest equivalence class contains 1496 laws equivalent to Eq2.

The dense matrix stored in this repository records the resolved implication relation over ordered pairs.

## 5. Core Mathematical Techniques

The paper reports that positive implications were established mainly through:

- direct rewriting and specialization;
- duality and transitivity;
- finite-magma arguments for the finite implication relation;
- automated theorem provers such as Vampire, Prover9, Mace4, Z3, and egg-based tooling;
- eventual formal verification in Lean.

False implications were often refuted using:

- explicit small finite magmas;
- linear models of the form $x \diamond y = ax + by$;
- translation-invariant models;
- twisting semigroups and other syntactic invariants;
- greedy constructions and modified base magmas.

This is the right mental model for the repository: no single trick dominates the whole problem space.

## 6. Why The Cheatsheet Exists

The competition narrows the broader mathematics problem down to a compressed reasoning artifact. Instead of submitting a solver or the full implication graph, participants submit a text cheatsheet that an evaluation model can consult.

So the task in this repo is not to replace mathematics with prompting. It is to compress good mathematics into a short, robust reference.

## 7. What Counts As A Good Signal

The repository uses structural signals such as:

- number of variables;
- variable repetition pattern;
- operation count;
- term depth;
- easy specialization checks;
- quick counterexamples over tiny magmas.

These are useful heuristics and useful distillation ingredients. But the paper’s lesson is that heuristics alone are not the mathematics. They help prioritize or compress; they do not replace proof or counterexample analysis.

## 8. How The Repo Uses The Paper

The paper under [../paper/source](../paper/source) provides the repository’s mathematical framing:

- the formal notion of a magma and free magma;
- the implication preorder and duality symmetry;
- the mix of proof and refutation techniques used at scale;
- the distinction between formal verification and exploratory automation.

If you are updating the cheatsheet or evaluation logic, the safest workflow is:

1. check whether the claim is supported by the paper, code, or reproducible local data;
2. decide whether it is valid submission-time content or only research-time support;
3. compress only the stable part into the cheatsheet.