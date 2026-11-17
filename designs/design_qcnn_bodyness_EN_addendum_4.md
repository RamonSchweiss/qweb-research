# Addendum 4 to design_qcnn_bodyness_EN.md

**16–17 November 2026.** Every section but A4.5 was written on 16 November;
A4.5 waited for a measurement that finished at 22:10 that evening and was
written the next morning. The note of 14 November and addenda 1 to 3 are left
standing unedited. Every decision in this addendum was taken **after** the
first run and with its numbers in view. That is the opposite of the condition
addenda 1 to 3 were written under, and it is the reason the run was committed
first: `calculations/qcnn_bodyness_scores_n8_n10.json`, `report_n8_n10.txt`
and `main_run_n8_n10.log` went into the repository on 16 November, before a
line of this was written, so the numbers stood publicly before anything
reacted to them.

What that commit date does and does not establish is worth stating, because
it is easy to claim more. It establishes that the registration came after the
numbers and that the numbers were not adjusted to fit it. It does **not**
establish that no analysis happened in between. A good deal did, and it is
reported below.

Evidence committed with this addendum, in `designs/`:
`opt_probe_d2_output.txt`, `mixing_needed_output.txt`,
`perm_null_cond4_output.txt`. The script that produces the last of those, and
the two stores it reads, go beside the assembly pieces in
`calculations/qcnn_pieces/`, where the collection run's glob cannot reach a
seven-hour measurement: `perm_null_cond4.py`, `perm_null_cond4.json`,
`perm_null_cond4_first_attempt_n8.json`. The printout re-computes its observed
column from the committed `calculations/qcnn_bodyness_scores_n8_n10.json`
rather than quoting it, so a changed run changes the printout.

---

## A4.1 Section 6 was right, and it cost the study its result

The run of 15/16 November declares itself void. Two of the four invalidating
conditions fired; this section is about the first and A4.5 about the fourth,
and either alone is enough. Condition 1 fired: H2 requires the bodyness-2 arm to be separated from the QCNN on D2 and
to fall below it, and the verdict on D2 is **not evaluable** at both sizes,
because the QCNN arm's noise floor on the control is three times the limit of
§6.

| group | QCNN | b1 | b2 | b4 | floor | verdict |
|---|---|---|---|---|---|---|
| D1 n = 8 | 0.8801 | 0.9980 | 0.9982 | — | 0.0291 | separated |
| D1 n = 10 | 0.9064 | 0.9985 | 0.9985 | — | 0.0221 | separated |
| D1w n = 8 | 0.9738 | 1.0000 | 1.0000 | — | 0.0352 | separated |
| D2 n = 8 | 0.8730 | 0.5278 | 0.5317 | 0.5205 | **0.1814** | not evaluable |
| D2 n = 10 | 0.8716 | 0.5180 | 0.5115 | 0.5003 | **0.1694** | not evaluable |

The point estimates on D2 are unambiguous and they point exactly where H2
expects: the classical arms sit 0.34 to 0.36 below the QCNN. §6 overrides
them, in the words registered on 14 November — *not evaluable regardless of
the point estimates*. No statement about D1 may be made from this run.

**What that costs is the whole result.** On D1 the bodyness-2 arm is not
bounded against the QCNN, as H1 — the hypothesis the note itself named as the
convenient one — predicted. It is separated from it and sits **above** it, in
every one of the forty D1 draws, at both sizes, with H3 going the same way
and the gap exceeding the QCNN's own spread by four to one. That is a
stronger and less comfortable finding than H1 would have been, and §8
condition 1 forbids reporting it as a finding at all.

This addendum does not relax that. The rule was registered to stop exactly
this trade, and a rule that bends when it becomes expensive was never a rule.

## A4.2 What the control's distribution actually is, and which test says so

The floor on D2 is not a wide spread. It is a **two-point** distribution: the
QCNN either solves the control exactly or does not solve it at all.

At n = 8, over 100 starts in 20 draws:

| | starts | mean | sd |
|---|---|---|---|
| upper mode | 74 | 1.0000 | 0.0000 |
| lower mode | 26 | 0.5115 | 0.0275 |
| **between** | **0** | | |

Over both sizes: 149 of 200 starts at 1.000, 51 below 0.60, and **not one in
between**. The gap between the modes is 0.4885.

A floor statistic reports the width of that as noise, which is arithmetically
correct and descriptively wrong — nothing about the arm is noisy, and it is
not a measurement that came out imprecise. §5 and §6 are **not changed** for
this. What is registered instead is a test that recognises the shape, so that
a future run reports it as what it is rather than leaving a reader to infer
it from a large floor.

**Registered: the dip test** of Hartigan and Hartigan (1985), as implemented
in the `diptest` package, applied to the pooled starts of an arm-size group,
at p < 0.05.

Three candidates were measured, on **all five** arm-size groups and not only
on the one that raised the question, because a test chosen for separating D2
from D1 on this data would be the post-hoc tuning this study exists to avoid.
Two of the three fail, and the failures are the informative part:

| | D1 n=8 | D1 n=10 | D1w n=8 | D2 n=8 | D2 n=10 |
|---|---|---|---|---|---|
| dip test | p 0.293 | p 0.064 | p 0.525 | **p 0.0000** | **p 0.0000** |
| GMM BIC | 2 comp. | 1 comp. | 2 comp. | 2 comp. | 2 comp. |
| largest gap | 68 % | 10 % | 73 % | 80 % | 83 % |

**GMM BIC fails**: it calls D1 at n = 8 two-component on a 2 % component at
0.48 — two outlying starts — and D1w on a ceiling effect at 0.935 against
1.000. **The largest-gap criterion fails too**: D1 at n = 8 has a gap of 68 %
of its range and D1w 73 %, against D2's 80 %, so a threshold separating D2
would call D1 bimodal as well. That second one is recorded with some
reluctance: it is the criterion that would have been chosen by eye.

One honest qualification on the test that survives. D1 at n = 10 comes out at
p = 0.064, which is near the threshold rather than far from it. The dip test
separates these groups, but it does not separate them by a wide margin
everywhere, and a future run should not treat a p just above 0.05 as a clean
negative.

**And a limit of the test, found while using it.** On the E2 probe of A4.4,
with 15 starts per cell and a mixing fraction of 13 : 2, the dip test reports
*not bimodal* for cells whose distribution is the same two-point shape with
nothing in between. At that sample size and that mixing fraction it has no
power. The test is registered for the study's own sample — 100 starts per
group — and a verdict from it on a smaller one is not evidence of unimodality.

## A4.3 Why §5 is not changed, and what was measured before deciding that

The obvious response to A4.1 is to change how the QCNN's per-draw score or
its spread is computed, so that a two-point distribution with a stable
mixture is not reported as an imprecise measurement. That was put as the
decision and it was measured before it was taken. It does not survive the
measurement, in any of the five forms tried:

| group | current | sem | draws | two-level | literal |
|---|---|---|---|---|---|
| D1 n = 8 | 0.0291 | 0.0177 | 0.0177 | 0.0201 | 0.0250 |
| D1 n = 10 | 0.0221 | 0.0099 | 0.0086 | 0.0097 | 0.0250 |
| D1w n = 8 | 0.0352 | 0.0157 | 0.0139 | 0.0174 | 0.0150 |
| D2 n = 8 | **0.1814** | **0.0811** | 0.0445 | **0.0578** | **0.0900** |
| D2 n = 10 | **0.1694** | **0.0757** | **0.0563** | **0.0669** | **0.1050** |

At n = 10 **every** candidate exceeds 0.05. At n = 8 only "draws alone" falls
under it, and that candidate also weakens §6 on D1, where the floor would
drop from 0.029 to 0.018.

More decisively, the premise fails. The argument for rescoring is that a
two-point distribution with a **stable** mixing fraction has a reproducible
mean. Measured, as the variance of the per-draw mixing fraction against the
binomial variance for five starts:

| D1 n=8 | D1 n=10 | D1w | D2 n=8 | D2 n=10 |
|---|---|---|---|---|
| 0.97 | 0.97 | 1.01 | **1.21** | **1.67** |

On D1 the mixture is exactly binomial. On the control it is overdispersed:
the mixing fraction itself moves from draw to draw by more than five
Bernoulli trials explain, so the mixture mean is not reproducible either.

**More starts are not available**, and this is a registration fact rather
than a cost one. §9 reads: *20 dataset draws, 5 random starts per draw ... and
no draw, start or size is added afterwards*, and addendum 1 confirms §9
unchanged. A variance decomposition was computed anyway, and is recorded here
so that nobody repeats it as a proposal: at n = 10 the irreducible part of
the floor — the between-draw term, which no number of starts touches — is
0.042, or 84 % of the §6 limit on its own.

So the correct reading of the first run is that it is void, and that is a
measured outcome rather than a choice between options.

## A4.4 Whether a different optimiser could rescue the control, and what the narrow reading costs

A3.4 settled two different things, and only one of them by measurement: the
**rule** is plain gradient descent because §3 is read narrowly, which is a
textual commitment; the **step size** 0.30 was selected by a declared
criterion over a declared grid — the pair reaching the higher *training*
score at the measured run length, no test score entering the choice.

That selection was run on the primary D1 only, and its result was then used
on the control without ever being selected there. Closing that gap is an
execution of the registered design, not a change to it, and it is closed
here: the same grid, the same two rules, the same three draws, the same 300
steps, on D2.

**The gap closes without a defect.** On the control the criterion picks step
size **0.30** — the same value selected on D1. The run used what the
registered criterion picks on the control too.

The second half is the figure A3.4 says the addendum owes: *what the narrow
reading costs in training score rather than an assurance that it costs
little*. It was produced for D1 and not for the control. Both, now:

| | gd at its best | Adam at its best | difference |
|---|---|---|---|
| D1, primary | **0.8820** (0.30) | 0.8730 | **−0.0090** |
| D2, control | 0.8160 (0.30) | **0.9413** (0.10) | **+0.1253** |

On the dataset the study is about, the narrow reading of §3 costs nothing —
it is also the better-training rule. On the control it costs 0.1253 in
training score. These are training scores, so this is not a statement about
generalisation.

That asymmetry is itself evidence about the control. R1 version 2 is where
the optimisation is hard, which places its difficulty in the loss landscape
rather than in the information its states carry. The construction check is
unaffected and still passes: every Pauli of weight below n carries label
information 6.7e-16, against a weight-n witness separating by 1.6455.

**And no optimiser rescues evaluability.** Adam does not change the shape —
across the eight probe cells, 119 of 120 starts are either at the solution or
far below it, with one in between — but it does raise the mixing fraction,
from 9 of 15 to 13 of 15. How high would it have to go? Applying the
**registered** floor statistic to simulated draws of the same shape, with the
two modes taken from the stored run:

| mixing fraction | floor |
|---|---|
| 0.740 (observed) | 0.1893 — model reproduces the measured 0.1814 |
| 0.867 (Adam's best) | 0.1204 |
| 0.900 | 0.0939 |
| **0.950** | **0.0461 — first value under the limit** |

Adam at its best is still at more than twice the limit. The floor falls as
√(p(1−p)), which is nearly flat across the whole range either rule reaches.
The control would have to be solved in essentially every start, not merely in
more of them.

**A switch to Adam does not follow and is not made.** The rule is the narrow
reading of §3; a training score cannot amend a reading. Had Adam removed the
two-point shape, the conclusion would have been that the step size selected
on D1 was wrong for the control by the design's own criterion — a fourth
instrument defect — and the repair would have been to select per dataset
under A3.4, not to change the rule. Neither applies: the step size is
confirmed and the shape survives.

## A4.5 Invalidating condition 4 and its permutation null

Condition 4 fired once in the whole run: the bodyness-2 arm on D2 at n = 8, at
0.531750 against a majority share of 0.523250, a margin of **+0.008500**
against a trigger of one granularity step, 0.005. The bodyness-1 arm at the
same size is at **+0.004500**, half a thousandth under firing. At n = 10 every
arm sits below the share.

Every one of the **sixteen** individual classifier scores on the control sits
below the majority share — sixteen and not eighteen, because the weight-4 arm
runs without the tree class at both sizes (A3.5). Only the per-draw
**maximum** over three of them rises above it. The premise of the measurement
was that a maximum over three selections, each with its own hyperparameter
grid, is biased upward on features carrying no label information, and that
condition 4 as registered has no allowance for that bias.

**The budget, declared before any threshold was computed**, in the docstring
of `calculations/qcnn_pieces/perm_null_cond4.py`: n = 8 only, because the
condition fired exactly once; three permutations in each of the twenty draws,
so sixty null values per arm; all three arms, because two arms where nothing
fired come almost free and show whether the threshold is a property of the
procedure; the pool is not extended after the threshold is in view; and the
arm is refitted in full, every classifier class and every hyperparameter grid,
because the null must be the distribution of the same procedure that produced
the observed statistic. Labels are permuted and features left untouched, since
permuting labels is exactly the hypothesis the construction asserts.

### The premise is refuted

The pooled null mean is **negative in every arm**: −0.008667 at weight 1,
−0.006583 at weight 2, −0.017167 at weight 4. On features that carry no label
information the procedure does not gain from taking a maximum over three
selections, it loses: the generalisation penalty of three fitted models
outweighs the selection bias of the maximum over them. There was no upward
bias for the condition to make an allowance for, and the measurement that was
built to excuse the firing does the opposite.

### The threshold, and what it says

The registered threshold is the one-sided 95th percentile of the mean of
twenty values resampled from the pool, 20 000 resamples. Condition 4 only ever
asks whether an arm rises above chance, so a two-sided threshold would be the
wrong shape.

| arm | observed | 95th pct | one-sided p | against the threshold |
|---|---|---|---|---|
| b1 | +0.004500 | +0.000250 | 0.0038 | above |
| b2 | +0.008500 | +0.005500 | 0.0189 | **above** |
| b4 | −0.002750 | −0.002500 | 0.0529 | below |

So the firing is not explained by the null. The run stays void on condition 4,
and the condition is not amended for this run.

Exchangeability was declared as an assumption and is checked rather than
asserted: the twenty per-draw null means scatter by 1.15 to 1.21 times what
the pooled null predicts, a mild overdispersion consistent with each draw
carrying its own test-majority share, and not enough to make the pool wrong.

### A correction, and two nested pools

The budget above says the first attempt — ten permutations, two sizes — "died
at a two-hour execution ceiling after a single draw". **That was false, and
the sentence is left standing in the script with a dated correction under it
rather than quietly replaced.** The first attempt had been detached from the
task that was killed at the ceiling. It ran for twelve hours, completed all
twenty draws of n = 8 at ten permutations, and announced itself by overwriting
the store the three-permutation run was writing into. Its pool is kept, in
`calculations/qcnn_pieces/perm_null_cond4_first_attempt_n8.json`.

The two pools are **nested, not alternatives**. The per-draw seed is
90000 + 100·n + draw and depends on nothing else, so the three values of each
draw in the registered pool are the first three of that draw's ten in the
larger one. Checked and not assumed: all twenty per-draw means of all three
arms agree with the log written before the overwrite.

The registered pool decides, because it is the budget declared last and the
one the script registers. A threshold picked from whichever pool gave the
wanted answer would be the one thing this measurement exists to prevent. The
larger pool is reported beside it as a check on precision:

| arm | condition 4 | 3 permutations | 10 permutations | |
|---|---|---|---|---|
| b1 | did not fire | above, p 0.0038 | below, p 0.1151 | verdicts differ |
| b2 | **fired** | above, p 0.0189 | above, p 0.0374 | same verdict |
| b4 | did not fire | below, p 0.0529 | below, p 0.1373 | same verdict |

In the only cell where the condition actually fired the two agree, so no
verdict in this study depends on which pool is used. Where they disagree, b1,
the condition never triggered, and the disagreement is a statement about sixty
values rather than about the data: a 95th percentile is not resolvable from a
pool that coarse. The budget was cut on a cost claim that turned out to be
false; the cut cost no verdict, and it was unnecessary.

### A reading that is not a registered test

Chosen after the threshold was in view, from the same pool, which is not
extended for it, and reported as a diagnosis of the condition rather than as a
result about the data. Resampled jointly across the three arms, because one
permutation was refitted by all three.

Condition 4 fires when the mean excess over twenty draws exceeds one
granularity step. On labels that carry nothing, some arm at n = 8 exceeds it in
**17.5 %** of resampled runs on the ten-permutation pool (5.8 % on the sixty
values, which understate it). The registered run applies the condition to
three arms at each of two sizes, so the rate over all six cells is higher than
this and is not measured: the budget bought one size.

The trigger sits at 0.005. The sampling noise of the quantity it triggers on
has a standard deviation of 0.0075. **The condition fires inside its own
noise**, and a condition that voids a run roughly one time in six on
label-free features is not a check on the instrument, it is a coin with a
narrow bias. That is a defect of the registered text and not of this run's
data, and it is not repaired here: the trigger may not be moved after it has
fired, by the same rule that keeps §5 unchanged in A4.3. It is registered in
A4.9 as a requirement on the next registration, where a threshold calibrated
against a null of this kind replaces a fixed granularity step.

## A4.6 Condition 1 is checked at every size — registered now, applied after the budget

§8 condition 1 is implemented against H2 at n = 8 only. It is registered here
that it must be evaluated at **every size**, since a positive control that
fails at one size and not another is a different situation from one that
fails everywhere, and the registered text does not say which size decides.

**It is not applied to the code yet, deliberately.** §9's budget covers
n ∈ {8, 10, 12} and D-i keeps n = 12, so the run is not finished. Changing
the instrument between n = 10 and n = 12 would mean the three sizes were not
measured by the same one, which is worse than either endpoint. The committed
module therefore stays bit-identical to the one that produced the n = 8 and
n = 10 results — the md5 sums are in the commit of 16 November that repaired
it — and the change is applied once the registered budget is complete.

On this run it changes nothing: D2 is not evaluable at both sizes with the
direction negative at both, so condition 1 fires at both.

## A4.7 The repair, the sixth gate and the assembly check

Registered as conditions of the instrument rather than as incidents.

The committed module is **assembled** from seven checked pieces. On 15
November the assembly dropped two imports; the file parsed, five gates
passed, and all five overnight chunks died at draw 0 hours later. Three
repairs followed, and each is now a standing requirement:

1. The assembly collects imports from the sources instead of carrying a
   hand-written list, and refuses to write anything out if `pyflakes` finds an
   undefined name.
2. The gate suite includes a **complete draw at the smallest size with every
   arm actually called**. The five older gates all passed on the broken file;
   a gate suite that never calls an arm cannot see a missing arm.
3. The chunk runner reads its exit code immediately rather than after a
   command substitution has reset it.

Added on 16 November: `calculations/qcnn_assembly_check.py`, which
re-assembles in a temporary directory and compares both outputs against the
committed files. It runs in the fast collection pass. The pieces live in a
subdirectory because the collection run executes everything directly in
`calculations/` and the assembly writes files whose names are the names of
committed ones; the check now also refuses to run while a stray copy of the
assembly sits where the collection run could reach it.

## A4.8 The control is withdrawn, and what the next one must pass

R1 version 2 is **withdrawn as unusable** as a positive control for this
architecture, at these sizes, under this cost function.

It is the third control of this study to fail, and the first to fail in a way
nothing in the design could see. The first was classified at 1.000 by the arm
it was built to defeat. The second made the two classes identical as
ensembles. Both failures are failures of **construction**, and the design had
a check for construction. R1 version 2 passes that check — 6.7e-16 — and
fails at something no document asked about: whether the registered quantum
arm reliably **trains** on it.

**Registered for any future control: a trainability gate.** A positive
control is accepted only if the registered arm, at its registered rule, step
size, step count and start count, solves it in a share of starts high enough
that the arm's floor stays under the §6 limit. A4.4 gives the number for this
architecture: the mixing fraction must exceed 0.95, and a candidate at 0.87
is not close.

The consequence for this registration is **E1**: the void is accepted and
reported. The question the note asks is not answered by this run and cannot
be rescued into an answer by it.

A replacement control run under this registration was considered and
**rejected on grounds of selection**, not of cost. The D1 numbers are now
known, and a control designed in the knowledge that making it work would
unlock a strong publishable result is a control chosen under a selection
effect that no reader could distinguish from intent. If the question is to be
answered, it is answered by a **new registration** that runs D1 again, with
this run demoted to a pilot. That is a separate study and is not registered
here.

## A4.9 Registered amendments

Points 1, 2, 5, 6 and 8 are registrations the first run forced. Points 3, 4
and 7 were Ramon's, taken on 16 November after the measurements above were put
to him.

1. **§5 and §6 are unchanged.** Every candidate rescoring was measured and
   none survives; the premise that the control's mixture is stable is refuted
   at 1.21 and 1.67 against binomial (A4.3).
2. **The dip test is the registered bimodality test**, at p < 0.05 on the
   pooled starts of an arm-size group, with the two rejected candidates and
   the test's power limit recorded (A4.2).
3. **E1: the void is accepted and reported**, and the control R1 version 2 is
   withdrawn. A replacement under this registration is rejected on grounds of
   selection (A4.8).
4. **Condition 1 is evaluated at every size**, registered now and applied to
   the code only after the registered budget of §9 is complete (A4.6).
5. **Condition 4 gains a permutation threshold**, with the budget declared
   before the numbers (A4.5). The threshold does not excuse the firing, and
   the condition is not amended for this run.
6. **A positive control must pass a trainability gate**, not only a
   construction check (A4.8).
7. **D-i: the registered budget is completed**, n = 12 included, although the
   run is void. Stopping early would itself be a decision taken from the
   result, which is what §9 exists to prevent.
8. **A future registration replaces condition 4's fixed trigger with a
   calibrated one.** Measured on labels that carry nothing, the registered
   trigger of one granularity step fires on some arm in 17.5 % of runs at a
   single size, against a sampling standard deviation of 0.0075 for the
   quantity it triggers on. The trigger is not moved here — it has already
   fired, and moving a threshold after it has fired is what §5 is kept
   unchanged to prevent (A4.5).

Nothing in the note or in addenda 1 to 3 is deleted or edited. Of the changes
above, those that move the study move it against its own convenience: a
hypothesis that came out strongly in the unexpected direction stays
unreportable, a rescoring that would have made the run evaluable is rejected
on measurement, a control is withdrawn rather than replaced, a null built to
excuse a fired condition refutes its own premise instead, and a 30-hour run
that cannot change the verdict is completed rather than cancelled.

## A4.10 What this addendum cost to find

Defects found on 16 November, all by measuring or by building rather than by
reading:

| found by | what | direction |
|---|---|---|
| measuring before deciding | the rescoring of §5 fails in all five forms, and its premise is refuted | against the convenient option |
| measuring all five groups | two of three bimodality tests call D1 bimodal as well; one of them is the one I would have chosen by eye | against my own judgement |
| reading §9 | more starts were never available; a variance table had been computed for an option the registration forbids | wasted work, recorded |
| running A3.4 on the control | the step size was selected on D1 and used on D2 — gap closed, no defect found | neutral |
| re-reading addendum 3 | it cites a committed printout of the step-size grid that was never committed | against the record |
| counting | "eighteen individual classifier scores" is sixteen; the weight-4 arm has no tree class | against the record |
| building the assembly check | `pyflakes` missing makes the assembly report a clean check it never performed | a gate that cannot fail |
| building the assembly check | the assembly's input shared a name with the committed file that is its output, so the first check compared a file with itself | a check that cannot fail |
| running the check on Windows | it called a line-ending convention a drifted file | a check that cries wolf |
| running the check after upload | a stray copy of the assembly in `calculations/`, which the collection run would have executed over two committed files | caught by accident, now checked |
| running the null to the end | the premise of the measurement is refuted — the selection bias it was built to make an allowance for is negative in every arm | against my own hypothesis |
| the first attempt overwriting the store | it had not died at the execution ceiling, so a budget was cut on a cost claim that was false | against the record |
| reading the null a second way | condition 4's trigger sits inside the sampling noise of the quantity it triggers on, and voids a run on label-free labels about one time in six | a condition that cries wolf |
