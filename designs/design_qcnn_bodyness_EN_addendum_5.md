# Addendum 5 to design_qcnn_bodyness_EN.md

**23 November 2026.** The note of 14 November and addenda 1 to 4 are left
standing unedited. The registered budget of §9 is complete, and everything
below is written with all of its numbers in view.

The data went into the repository before this text: the complete store
`calculations/qcnn_bodyness_scores_n8_n10_n12.json` and the evaluation
`calculations/qcnn_bodyness_report_n8_n10_n12.txt` were committed first, so the
numbers stood publicly before anything reacted to them. As in addendum 4, that
establishes the order and not that no analysis happened in between. A good deal
did, and it is reported here.

---

## A5.1 The budget is complete, and the run is still void

§9 registered 20 dataset draws, 5 random starts per draw for the QCNN, at
n ∈ {8, 10, 12}, on both D1 and D2, with the run stopping there whether or not
any hypothesis had resolved and with no draw, start or size added afterwards.
That budget is now exhausted exactly as written: 140 records, seven cells of
twenty draws each, no additions.

The table of A4.1, extended by the third size:

| group | QCNN | b1 | b2 | b4 | floor | verdict |
|---|---|---|---|---|---|---|
| D1 n = 8 | 0.8801 | 0.9980 | 0.9982 | — | 0.0291 | separated |
| D1 n = 10 | 0.9064 | 0.9985 | 0.9985 | — | 0.0221 | separated |
| D1 n = 12 | 0.9116 | 0.9990 | 0.9990 | — | 0.0372 | separated |
| D1w n = 8 | 0.9738 | 1.0000 | 1.0000 | — | 0.0352 | separated |
| D2 n = 8 | 0.8730 | 0.5278 | 0.5317 | 0.5205 | **0.1814** | not evaluable |
| D2 n = 10 | 0.8716 | 0.5180 | 0.5115 | 0.5003 | **0.1694** | not evaluable |
| D2 n = 12 | 0.8011 | 0.5180 | 0.5157 | 0.5087 | **0.2558** | not evaluable |

The third size behaves like the first two and more so. On D2 the floor is
0.2558 against the §6 limit of 0.05 — five times the limit, where n = 8 and
n = 10 were three times it — so §6 overrides the point estimates again, the
verdict is *not evaluable*, and condition 1 fires at n = 12 as well. A4.6
stated in advance that applying condition 1 per size would change nothing on
this run. It changed nothing at the size that had not yet been measured when
that was written.

On D1 the direction of A4.1 also holds at the third size: the bodyness-2 arm is
separated from the QCNN and sits **above** it, by +0.0874 with an interval of
[+0.075, +0.101], and in **20 of 20 draws** individually — as at n = 8 and
n = 10, where it is likewise 20 of 20. Sixty D1 draws, sixty times the same
direction. §8 condition 1 still forbids reporting that as a finding, and this
addendum does not relax it.

## A5.2 The two-point distribution of A4.2 holds at the third size

A4.2 reported that the floor on D2 is not a wide spread but a two-point
distribution: the QCNN either solves the control exactly or not at all. At
n = 12, over 100 starts in 20 draws:

| | starts | mean | sd |
|---|---|---|---|
| upper mode | 61 | 1.0000 | 0.0000 |
| lower mode | 39 | 0.4899 | 0.0276 |
| **between** | **0** | | |

Over all three sizes, 300 starts: **210 at exactly 1.000, 90 below 0.60, and
not one in between.** The upper mode is 74, 75 and 61 starts at the three
sizes, so what changes with register size is the share of starts that reach it,
not the two values it lies between.

That is also the whole of the drop in the D2 mean from 0.8716 at n = 10 to
0.8011 at n = 12. The reported score per draw is the mean over five starts, so
it is a weighted average of 1.000 and roughly 0.49; moving fourteen starts from
the upper mode to the lower moves the mean by the amount observed. **The circuit
does not get worse at the control. Fewer of its starts arrive.** Any reading of
the n = 12 mean as a statement about scaling would be a reading of the
optimiser's reliability, and the mean is the wrong summary statistic for a
distribution with nothing in the middle.

The comparison cell is D1, where the same optimiser reaches the upper region
almost always: 2, 0 and 1 start below 0.60 out of 100 at the three sizes. The
stalling is a property of the control dataset, not of the circuit alone.

## A5.3 Condition 1 is now applied per size, as A4.6 registered

A4.6 registered that conditions 1 and 2 must be evaluated at every size, and
deliberately did not apply it to the code, so that the three sizes would be
measured by the same instrument. The budget is complete, so it is applied now.

The change is a loop over n ∈ {8, 10, 12} replacing a single call on n = 8.
Condition 3 is a property of the construction and is still checked once.
Condition 4 already looped over the sizes and is untouched. Nothing in the
measurement path changes: no training, no scoring, no floor limit, no
permutation pool, and no stored score is recomputed.
`calculations/qcnn_bodyness_core.py` stays bit-identical at md5
`5f6bef491fab0f47a0ef276bb75b838b`; `calculations/qcnn_bodyness.py` becomes
`2209ff361863af7a1cf351c7b0af3daa`.

**What the per-size view changes in the record, having changed nothing in the
verdict.** Condition 4 fires at **n = 8 only**. There the bodyness-2 arm
exceeds the majority share by 0.0084 — 0.5317 against 0.5233 — against a
granularity of 0.005. At n = 10 the arm sits below the majority share, and at
n = 12 the excess is 0.0007, inside one granularity step. The global check
reported one instance and gave no way to see that it was one instance at one
size. That does not make the leak smaller: A4.5 established that the excess at
n = 8 is real against a measured null, and the defect recorded there in
condition 4's own trigger is unaffected by where the condition is evaluated.
Condition 2 fires at no size; the QCNN trains.

## A5.4 A commit message of this morning was wrong, and is corrected

The commit that added the complete store stated that condition 1 fired because
a classical arm reaches 1.000 on D1. That is not what condition 1 tests, and
A4.1 had the mechanism right on 16 November. The correct account is the one in
A5.1: condition 1 fires because H2 cannot be resolved on D2, the control arm
reaching 1.000 on D1 being the separate refutation of H1.

A pushed commit message cannot be edited on the web interface, so the
correction is in the message of the following commit and here. The error was in
restating the record, not in the record.

## A5.5 The article moves from QML to QME, and keeps its title

The article was placed in QML on 14 November, beside "The Layer That Nobody
Trains". It is published in QME © Methodology instead, beside "What a Verdict
Assumes" and "What Moves the Baseline", because what the run produced is a
result about an instrument and not about an architecture.

The decision was taken on 23 November, **after** the budget was complete, and
is recorded here for that reason: a category chosen after the result is a
decision taken with the numbers in view, and it should be visible as one rather
than appear as a silent reassignment.

The title chosen on 14 November, "What a Trainable Circuit Gives Away", is
unchanged. It was chosen so as not to name the question after the expected
answer, and that is why it survives an answer that came out differently.

## A5.6 Provenance of the n = 12 block

All three sizes were computed in one Linux environment, so there is no
mixed-platform block to record against the note of 14 November.

The n = 12 block was interrupted. The compute environment was reclaimed on
18 November and the scripts, the store and the running log were lost with it.
The run was rebuilt from the public repository and from a copy of the store
that had been written out after every completed block, and it resumed on
21 November. **Both modules were checksum-verified against the values committed
on 16 November before a single further draw was computed**, so F1 — the freeze
on the measurement code until the registered budget is complete — is
demonstrably unbroken across the interruption rather than merely asserted. No
registered draw was recomputed; the only loss was the draw in flight.

The running log is therefore partial and begins at D2 draw 5.
`calculations/n12_run.log` is committed as such, with its gap named. Nothing
registered depends on it: every scored draw is in the store.

## A5.7 What this addendum does not settle

- **Why the starts split two ways at all.** A4.2 established the shape and A4.3
  the optimiser probe; the third size adds a point and no mechanism.
- **Why the upper mode shrinks with n.** Three sizes, one circuit family, one
  start count. 74, 75, 61 is not a curve.
- **Nothing about D1.** Condition 1 forbids it, at all three sizes, and the
  completed budget does not change that.
- **Condition 4's trigger stays where it was registered.** The defect recorded
  in A4.5 is now a defect measured at one size rather than at the run level.
  Moving the trigger after the budget would be setting a threshold from the
  result it fired on.
