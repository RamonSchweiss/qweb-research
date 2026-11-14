# Addendum 1 to the QCNN bodyness design note

**14 November 2026, the same day as registration, before any measurement of
the study itself.**
The original note is not edited. Two defects were found while implementing
it, one by measurement and one by reading. The main run does not start until
the first is repaired.

Evidence: `calculations/qcnn_control_probe.py` and its printout. Every number
below comes from that script.

---

## A1.1 The registered positive control is vacuous

D2 was registered as the dataset on which the bodyness-2 classifier **must**
fail, so that agreement on D1 could be distinguished from a comparison that
never shows anything. It does not fail. It does not even come close.

At n = 8, 84 states per sweep, five-fold cross-validation:

| dataset | weight ≤ 1 | weight ≤ 2 | mean ⟨Xᵢ⟩ alone |
|---|---|---|---|
| D1 TFIM, the benchmark under test | 0.963 / 1.000 | 1.000 / 1.000 | 0.950 |
| D2 cluster, the registered control | 0.975 / 1.000 | 1.000 / 1.000 | 0.950 |

Two numbers per cell: linear classifier, then nonlinear. At n = 6 the picture
is the same, 0.950 / 1.000 and 0.988 / 1.000 on both datasets, with the single
feature at 0.925 on both.

D2 is not harder than D1 for any arm in this study. **One** local feature, the
mean transverse magnetisation, classifies both at 0.925 to 0.950.

## A1.2 Why it is vacuous

The two phases of the registered cluster family sit at different transverse
field strengths, so their ground states differ in local magnetisation. The
string order parameter is what **characterises** the cluster phase; it is not
what is needed to **classify** these particular states.

The design conflated those two. "The phase is topologically characterised by a
long observable" does not imply "the states cannot be told apart locally", and
the note asserted the second while only having grounds for the first.

This is case 1 of the eight in "What a Verdict Assumes", repeating: an
objective found vacuous as written, while implementing it. It was caught only
because the design required a positive control at all — the requirement forced
the check that the control itself needs.

## A1.3 Consequence for the study

Invalidating condition 1 of the design cannot fire. Therefore:

> The main run does not start. Any D1 result obtained with D2 as the control
> would be uninterpretable, because "the classical arm matches the QCNN" and
> "this comparison separates nothing" would look identical.

## A1.4 A second defect, found by reading rather than measuring

The design registers logistic regression as the classical arm. But the claim
under test — that the benchmark's states are classifiable from low-bodyness
**information** — is about what the weight ≤ k subspace contains, not about
what a linear model can extract from it. Those are different statements, and
the probe shows the difference is not academic: on D1 at weight ≤ 1, the
linear arm reaches 0.963 and the nonlinear arm 1.000.

A gap measured with a linear arm alone could therefore be a property of
logistic regression rather than of the feature bodyness, and the study would
have reported it as the latter. Hypothesis H4 was meant to separate those two
and cannot do so if only one model class is ever run.

## A1.5 Proposed repair of the control: R1, the sign of a cat state

For |ψ±⟩ = (|0…0⟩ ± |1…1⟩)/√2, every **proper** subset S of the qubits has the
same reduced density matrix in both classes, because the cross term between
|0…0⟩ and |1…1⟩ requires the complement of S to agree. Hence every Pauli
expectation of weight below n carries exactly zero information about the
label. That is a property of the construction, not an observation about a
printout. Variety is supplied by a random local Z rotation per site, which
cannot create low-weight information because it is diagonal.

Measured, at n = 8, 120 states, majority class 0.508:

| arm | linear | nonlinear |
|---|---|---|
| weight ≤ 1, 24 features | 0.508 | 0.508 |
| weight ≤ 2, 276 features | 0.508 | 0.400 |

Both arms sit at the majority-class share, which is what chance looks like
here. The nonlinear arm at weight ≤ 2 lands **below** it, at 0.400, which is
overfitting on features that carry nothing — worth recording rather than
tidying away. The witness that does separate the classes is the de-rotated
⟨X^⊗ⁿ⟩, at +1.000 for one class and −1.000 for the other: a weight-n
observable, as the design's intent required and its dataset did not deliver.

A log-depth circuit can measure that witness — Hadamards followed by a CNOT
tree — so the QCNN arm is expected to succeed where the classical arms cannot.
That expectation is itself a registered hypothesis under A1.6 and not an
assumption.

## A1.6 Proposed amendments, not yet registered

1. **D2 is replaced by R1.** The cluster family is withdrawn as a control. It
   may be kept as a second instance of D1 — a second locally-easy benchmark —
   which is what the probe shows it to be, but it carries no control duty.
2. **Every classical arm is run with both a linear and a nonlinear
   classifier**, and the stronger of the two stands for "the features carry
   the label". The weaker one alone may never support a claim that they do
   not.
3. **New hypothesis H6**, registered here: on R1, the QCNN separates the
   classes while both classical arms remain at the majority-class share. If
   the QCNN also fails on R1, the comparison has no working positive control
   and the study stops rather than reporting D1.
4. The four declarations of §5, the resolution rule of §6, the remaining
   hypotheses of §7, the other invalidating conditions of §8 and the stopping
   condition of §9 are **unchanged**.

## A1.7 What this addendum does not do

It does not change the question. It does not touch D1, which is the dataset
the claim is about and which the probe leaves exactly as registered. And it
does not report any result of the study, because none has been measured.

Two of these amendments make the study harder to pass: R1 is a control that
can fail, and H6 gives it a way to stop the whole run. That is the direction a
correction after registration has to go in; a change that makes the result
easier to obtain would be a result dressed as a method.

## A1.8 Status

**Proposed, awaiting Ramon's decision.** Until the amendments are accepted,
the design of 14 November stands as registered and the study is blocked by
A1.3.
