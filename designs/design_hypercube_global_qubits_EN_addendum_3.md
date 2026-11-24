# Addendum 3 to design_hypercube_global_qubits_EN.md

**24 November 2026, after the registered run and with all of its numbers in
view.** The note and addenda 1 and 2 are left standing unedited.

The run is in the repository before this text: `calculations/
hypercube_global_qubits.py`, its store of 378 instances, the gate log and the
evaluation were committed first, so the numbers stood publicly before anything
reacted to them.

---

## A3.1 Two execution choices, on the record

The note left two details to the run. Both were fixed in the script header
before the first measurement and are recorded here so that they are registered
rather than merely documented:

- The initial state is |+⟩ on every qubit, the QAOA convention.
- The mutual-information arm reads the state **after the first full layer**, and
  scores a qubit by its total pairwise mutual information to all others,
  I(a) = Σ_{b≠a} I(a:b), taking the g qubits of lowest score. That is the
  state-side analogue of the lowest-degree rule, which is what makes the
  comparison a comparison rather than two different questions.

## A3.2 The gates

All four passed before any number was produced.

- **Condition 3** (A1.6), the cost model per gate type against the operator:
  ten placements, ten agreements, no mismatch.
- **Condition 2**, the independent second enumeration, subset by subset and not
  by count: 0 disagreeing subsets.
- **Condition 5**, the declared degenerate g = 1: 0 cells failing to reproduce
  minimum weight.
- **A1.4**, family A degenerate: 0 cells where the QAOA cost was not constant
  at p·g. The emptiness of the selection question on QAOA is now measured and
  not only derived.

## A3.3 The closed form, and the positive control

The lowest-degree arm attains the enumerated optimum in **378 of 378**
instances. Addendum 2's proof holds everywhere it was registered to be tested.

The random arm is **separated** from the optimum on both families, sitting
3.543 units above it on the XX+YY family (interval [3.262, 3.838]) and 3.281 on
the CNOT family ([3.103, 3.472]). H2 holds: the comparison can tell selection
rules apart, so a null result elsewhere is a result and not a blind spot.

## A3.4 The finding splits by family

| circuit | n | g | same set | at optimum | mean loss | spread | verdict |
|---|---|---|---|---|---|---|---|
| xy | 12 | 2 / 3 / 4 | 8 / 6 / 10 | 21 / 21 / 21 | 0.000 | 0.00 | bounded by 0.00 |
| xy | 16 | 2 / 3 / 4 | 8 / 3 / 8 | 21 / 21 / 21 | 0.000 | 0.00 | bounded by 0.00 |
| xy | 20 | 2 / 3 / 4 | 4 / 3 / 3 | 21 / 21 / 21 | 0.000 | 0.00 | bounded by 0.00 |
| cnot | 12 | 2 / 3 / 4 | 16 / 11 / 8 | 16 / 11 / 8 | 0.238 / 0.476 / 0.952 | 0.19 / 0.19 / 0.40 | separated |
| cnot | 16 | 2 / 3 / 4 | 18 / 10 / 6 | 18 / 10 / 6 | 0.143 / 0.619 / 1.048 | 0.14 / 0.29 / 0.33 | bounded by 0.14; separated; separated |
| cnot | 20 | 2 / 3 / 4 | 19 / 15 / 11 | 19 / 15 / 11 | 0.095 / 0.286 / 0.810 | 0.12 / 0.19 / 0.38 | bounded by 0.12; separated; separated |

Each cell holds 21 instances. "Same set" counts instances where the
information arm chose the same global set as the lowest-degree arm; "at
optimum" counts instances where its choice cost the optimum.

**On the undirected family the optimum is degenerate, and the state lands on
another member of it for free.** Mean loss is 0.000 in all nine cells, while
the chosen set agrees in fewer than half of the instances and the agreement
falls with register size: 8, 6 and 10 of 21 at n = 12 against 4, 3 and 3 at
n = 20.

**On the directed family the optimum is not degenerate.** "Same set" and "at
optimum" coincide instance for instance in every cell, so every disagreement is
paid for, and the payment grows with g. Seven of nine cells are separated; the
two exceptions are g = 2 at the larger sizes, bounded below the registered
limit of two units.

So the state does not beat the circuit structure — addendum 2 proved it cannot
— but it does something the note did not anticipate: **it leads somewhere else,
and whether that is free depends on whether the architecture's cost is
symmetric or directed.**

## A3.5 H5 is mis-specified, and is recorded rather than dropped

H5 reads: the difference between arms does not grow with g at fixed n, and if
it does grow, the combinatorial account of §3 is incomplete.

The difference does grow, on the CNOT family, at every size. But §3 is not
incomplete; it predicts the growth. The loss is the gap between the sum of the
chosen in-degrees and the sum of the g smallest, so a mis-ranking costs more
terms as g rises. **The antecedent of H5 is met and its registered consequent
does not follow.** The hypothesis was wrong about what its own model implies.

The implication is not retro-fitted, and H5 is not rewritten into something it
would have passed. It is recorded as a mis-specified hypothesis, in the sense
"What a Verdict Assumes" gave the word, and the account of §3 stands.

For the record, this is the third registered item in two weeks to turn out
mis-specified: invalidating condition 4 of the QCNN study, whose trigger sat
inside the sampling noise of the statistic it tested; condition 1 of the same
study, evaluated globally where it was registered per size; and now H5 here.
Three different kinds of error in three different places, all of them in the
scaffolding rather than in a measurement. That pattern is worth a paragraph
somewhere, and it is not this document's job.

## A3.6 An observation, flagged as an observation

The falling share of agreement on the undirected family has the same shape as
the findability addendum's finding for Kernighan–Lin, which holds the exact
optimum while landing on a different member of the optimal cut set in 5 of 21
graphs at n = 10 and 12 of 20 at n = 26.

Two unrelated measurements, the same figure: a rule that is optimal in cost
while drifting in choice, and drifting more as the register grows. Whether the
mechanism is the same is not established here and this addendum does not claim
it is. It does make the degeneracy experiment proposed to V. Ramamurthy on
23 November more interesting than it was when it was proposed, because which
member gets chosen is exactly what a scheduler pays migration for.

## A3.7 What the run does not settle

- **Why the undirected optimum is degenerate and the directed one is not.** The
  asymmetry is measured; its structural account is not written down.
- **Anything beyond two circuit families and three sizes.** The budget was 189
  instances per family and nothing was added.
- **Anything about the distributed execution model.** A2.6 bounds this result to
  the amplitude-distributed case, and the run does not cross that boundary.
- **Whether the information arm's rule is the best state-side rule.** One rule
  was declared in A3.1 and measured. Another might lose less, and finding that
  out would be a new registration rather than a re-reading of this one.
