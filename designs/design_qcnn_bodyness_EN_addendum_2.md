# Addendum 2 to the QCNN bodyness design note

**14 November 2026, after addendum 1 of the same day and still before any
measurement of the study itself.**
Neither the original note nor addendum 1 is edited. Addendum 1 proposed a
replacement control. This addendum withdraws it, because it does not work
either, and the reason is worse than the first one.

Evidence: `calculations/qcnn_control_probe.py` and its printout.

---

## A2.1 R1 as proposed is impossible, not hard

R1 was the sign of a cat state, with random local **Z** rotations for variety.
Those rotations are diagonal, so they do not leave the state alone where it
matters. Writing Φ for the sum of the angles, the state is

> (|0…0⟩ ± e^{iΦ} |1…1⟩)/√2 up to a global phase,

and ±e^{iΦ} with Φ uniform on [0, 2π) has **the same distribution for both
signs**. The two classes are therefore identical as ensembles.

Measured, n = 6, 2000 states, with the observable an arm can actually form —
⟨X^⊗ⁿ⟩ without the angles:

| class | mean | sd | range |
|---|---|---|---|
| + | +0.0449 | 0.7127 | −1.000 … +1.000 |
| − | −0.0066 | 0.7211 | −1.000 … +1.000 |

And the effective relative phase, over eight bins:

- class +: 119 106 127 126 103 107 130 155
- class −: 151 108 126 133 141 125 125 118

Both flat. No arm can separate these classes — not a bodyness classifier, and
not the QCNN. Hypothesis H6 of addendum 1 would have failed by construction,
and the study would have stopped for a reason that had nothing to do with its
question.

The witness in A1.5 reached ±1.000 only because it was handed the rotation
angles and undid them first. A classifier is not handed them. I printed a
number that no arm in the study could ever compute and read it as evidence
that the control worked.

## A2.2 Why the first probe did not catch it, and the rule that follows

The probe of addendum 1 asked one question: do the classical arms fail on the
control? They did, so the control looked sound. It never asked whether
**anything** passes.

> A control nobody can pass is not a control. A positive control therefore
> needs its own demonstration — not that the arms under suspicion fail on it,
> but that some arm succeeds on it.

That is registered here as a standing requirement, and it is the same shape as
the rule case 8 produced in "What a Verdict Assumes": anyone publishing a null
owes a demonstration that the same instrument measured something other than
null. This is that rule applied to the demonstration itself. One level up, and
I missed it one level up.

## A2.3 R1 version 2

Same construction, local **Y** rotations instead of Z: RY(α_j) per site, with
α_j drawn uniformly from (−α, α) independently of the label.

Y rotations are not diagonal. Two things follow, and they are the two the
control needs:

- they **vary the low-weight marginals**, so the classical arms see a dataset
  that actually differs from sample to sample, which the Z version did not
  provide at all — under Z rotations every feature vector was identical;
- they **leave the relative phase alone**, so a fixed global observable can
  still see the sign without knowing the angles.

## A2.4 Measured

n = 8, 120 states per amplitude, five-fold cross-validation, weight ≤ 2
features:

| α | witness ⟨X^⊗⁸⟩, + | witness, − | largest feature sd | linear | nonlinear | majority |
|---|---|---|---|---|---|---|
| 0.0 | +1.000 (0.000) | −1.000 (0.000) | 0.0000 | 0.508 | 0.508 | 0.508 |
| 0.2 | +0.944 (0.017) | −0.945 (0.014) | 0.1248 | 0.483 | 0.533 | 0.525 |
| 0.4 | +0.806 (0.046) | −0.822 (0.056) | 0.2256 | 0.558 | 0.550 | 0.508 |
| 0.8 | +0.412 (0.111) | −0.444 (0.123) | 0.4092 | 0.467 | 0.408 | 0.525 |

At n = 6 the same pattern holds, with the witness at ±0.845 / ±0.851 at
α = 0.4 and the arms at 0.475 and 0.525 against a majority share of 0.533.

## A2.5 The amplitude is chosen now, and on what criterion

**α = 0.4**, declared here, before the study runs.

The criterion, stated rather than fitted: the amplitude must be large enough
that the low-weight features genuinely vary, and small enough that the
weight-n witness still separates the classes by a wide margin. At α = 0.4 the
largest feature standard deviation is 0.2256 — real variation — while the
witness means differ by 1.63 with a within-class spread near 0.05, about
thirty standard deviations. At α = 0 the features do not vary at all, which
makes the control degenerate. At α = 0.8 the witness has fallen to ±0.43 and
the margin is shrinking.

This choice is made on probe data. That is permitted because it is made
before the study's own measurement and against a criterion written down with
it; it would not be permitted afterwards. Loosening a rule before the data is
a correction, after it is a result dressed as a method.

## A2.6 A number that did not reproduce

An earlier unseeded run of the same sweep gave the linear arm 0.658 at
α = 0.2, n = 8, against a majority share of 0.525, and I was about to record
that as a leak the amplitude choice avoids. Under the seed in the committed
script the same cell reads 0.483.

It was noise. At 120 states a five-fold score moves by several points, which
is precisely why the study declares the dataset draw as its unit of analysis
and bootstraps over twenty of them. The episode is recorded because an
unreproduced number that happens to support one's own design is the easiest
kind to keep.

## A2.7 Registered amendments

1. **R1 version 1 is withdrawn.** The control is R1 version 2 as in A2.3,
   with α = 0.4.
2. **A standing requirement is added:** every positive control in this study
   must come with a demonstration that some arm passes it, measured, before
   the control may support any claim about the arms that fail it.
3. Amendments 2, 3 and 4 of addendum 1 — both classifier classes on every
   classical arm, hypothesis H6, and the unchanged declarations — **stand**.
4. H6 is restated against the new control: on R1 v2 at α = 0.4, the QCNN
   separates the classes while both classical arms remain at the
   majority-class share. The witness measurement in A2.4 shows the task is
   possible; H6 asks whether the QCNN performs it.

## A2.8 Status

Two defects in two addenda in one afternoon, both in my own design, both
before any measurement of the study. Neither was found by reading the
literature and neither by running the study — both were found by trying to
build the instrument.

The design of 14 November, as amended by addendum 1 points 2–4 and this
addendum, is the version the measurement script is written against.
