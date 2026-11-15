# Addendum 3 to design_qcnn_bodyness_EN.md

**15 November 2026.** The note of 14 November and addenda 1 and 2 are left
standing unedited. This addendum registers the implementation decisions the
note left open, before any score exists. Each one of them can move a verdict,
which is why it is dated here rather than explained afterwards.

Evidence for sections A3.7 and A3.8: `calculations/qcnn_bodyness_build.txt`,
committed with this addendum.

---

## A3.1 The depth is ⌈log₂ n⌉, and the leftover qubit is carried

The note names the depth `L = log₂ n`. That is not an integer at n = 10 or
n = 12, which are two of the three registered sizes. The circuit built is
**⌈log₂ n⌉** layers, and where a layer has an odd number of active qubits the
leftover qubit is **carried through unchanged** to the next layer rather than
dropped or paired with a wrap-around neighbour.

| n | active qubits per layer | layers | parameters |
|---|---|---|---|
| 8 | 8 → 4 → 2 → 1 | 3 | 19 |
| 10 | 10 → 5 → 3 → 2 → 1 | 4 | 25 |
| 12 | 12 → 6 → 3 → 2 → 1 | 4 | 25 |

This is not bookkeeping. The Pesah et al. variance bound is polynomial
**because** the depth is logarithmic — the bound carries a factor
50^−(L−ℓ+1), and a constant or linear depth leaves the regime that argument
covers. ⌈log₂ n⌉ keeps the scaling the study's premise rests on. The leftover
qubit is carried rather than wrapped around because wrap-around pairing would
give the circuit a connectivity the architecture does not claim, and the
study is about this architecture and not a convenient neighbour of it.

## A3.2 The QCNN's per-draw score is the mean over its starts

Within a draw the QCNN trains from five random starts. §5 declares its spread
over starts and draws together. It does not say which of the five numbers
enters the comparison.

Registered: the **mean over the five starts**, not the best of them. Two
reasons, both stated before any score exists.

The best of five is what a practitioner reports after the fact, not what one
training run gives. Comparing a best-of-five arm against a deterministic
solver compares two procedures, not two models.

And the best of five would **raise** the QCNN arm, which makes H1 — the
convenient hypothesis — *harder* to satisfy. Choosing it would flatter the
study's own scepticism. That is the same defect as choosing what flatters its
claim; a defect does not become sound by running against one's own interest.

The five per-start scores are kept and printed. H3 reads them.

## A3.3 How the noise floor of §6 is measured

§6 gives the floor the last word: where the arms cannot be separated the
result is bounded above by the measured noise floor, and a floor above 0.05
makes the verdict *not evaluable* whatever the point estimates say. The note
does not define the statistic. Registered now:

> For each arm, the floor is the half-width of the 95 per cent percentile
> bootstrap interval of that arm's mean score, resampling **draws**; for an
> arm with random starts, the larger of that and the mean within-draw
> standard deviation across starts. The floor of a comparison is the larger
> of its two arms' floors.

One statistic for both kinds of arm, on the scale of a difference, so it can
be read against a difference and against the 0.05 limit with no conversion.
The maximum of the two rather than a pooled figure, because a comparison
cannot resolve below its noisier arm.

The definition cuts both ways, and that is the reason to fix it in advance: a
wider floor makes "not separated" easier to reach, which helps H1, and at the
same time brings the floor closer to the 0.05 limit that voids the verdict
altogether. Neither direction is safe to choose after seeing the scores.

## A3.4 The training budget, and the criterion that fixes the step count

§9 registers draws, starts and sizes. m_test = 200 follows from the
granularity declaration of §5. **m_train, the loss, the optimiser and the
number of gradient steps appear nowhere in the note**, and all four move the
QCNN's score.

Registered: m_train = 200, drawn in the same draw as the 200 test states and
**shared by every arm** — the QCNN and the classical arms see the same states,
the same labels and the same split, per draw. Giving the cheap arms more
states would be a different comparison.

The cost is the **linear** one §3 names, not a logistic loss:

> C = −(1/m) Σᵢ sᵢ ⟨Z⟩ᵢ at the readout qubit, with sᵢ = ±1 from the label.

Full-batch gradient descent, step size 0.1, identical for every start and
every size. A logistic loss was written first and discarded: §3 registers a
linear cost, and swapping the objective after registration would be a change
of arm dressed as an implementation detail.

The step count is **not chosen, it is measured**. The criterion was declared
before the measurement:

> The number of steps is the smallest multiple of ten at which the training
> score improves by less than one granularity step (0.005) over the final
> fifth of the run, measured at n = 12 on D1, and it is then used unchanged
> at every size and on both datasets.

**That criterion failed, and this is the record of it.** Measured at n = 12
on D1, 300 steps, five starts:

| step | mean training score | | step | mean training score |
|---|---|---|---|---|
| 40 | 0.8020 | | 150 | 0.9590 |
| 50 | 0.8050 | | 170 | 0.9700 |
| 110 | 0.8930 | | 200 | 0.9720 |
| 120 | 0.9050 | | 300 | 0.9750 |

The criterion returns **50**, because between steps 40 and 50 the score moves
by 0.003. The run then climbs from 0.805 to 0.975. One of the five starts
sits at 0.54 until step 110 and reaches 0.97 by step 170. The criterion fired
on a **plateau that was not convergence**, and had it stood, the QCNN arm
would have been scored seventeen points below what it reaches — a handicap on
the quantum arm, which makes H1, the convenient hypothesis, easier.

Being declared in advance did not make it a good criterion. A window inside
the run cannot tell a plateau from an end. It was amended twice, both times
before any study score, and both amendments were forced by applying it rather
than by thinking about it.

**First amendment: look at the remainder, not at a window.** That much is
above. It was not enough, for two reasons found in the next two runs.

**Second amendment: bound the range, not the rise.** "Improves by less than
0.005 for the remainder" is satisfied at *every local maximum*, because from
a peak nothing improves. Applied to a 2000-step run at n = 8 the rule
returned 300 — a spike the trace then fell back from. Had it stood, the QCNN
arm would have been read at 0.882 instead of its converged 0.874: an
**unearned advantage for the quantum arm**, the opposite direction to the
plateau defect and therefore not a bias of mine that runs one way, but a
criterion that was simply not a convergence test. Bounding the range of the
remainder returned 320.

**Third amendment: a guard against the edge of the run.** The amended rule
returned 290 of a 300-step run — arithmetically correct and epistemically
empty, since a count that lands at the end of the run only says the run was
too short to see convergence.

Registered, final form:

> The number of steps is the smallest multiple of ten such that the **range**
> of the mean training score over the **remainder of the measured run** is
> less than one granularity step (0.005), averaged over three draws at
> n = 12 on the primary D1, with the measured run length declared. If the
> count falls within one trace grid point of the run length, the **guard**
> fires: the run was too short and no step count is established. It is then
> used unchanged at every size and on both datasets.

This can only see as far as the run it is applied to, which is why the run
length is part of the declaration and not an implementation detail, and why
the guard exists at all. The printout reports the count, the run length and
the guard's state together, so a reader can see that convergence was
established rather than assumed.

### The optimiser: §3 is read narrowly

The trace above is plain gradient descent at step size 0.1 crawling through a
sixty-step plateau. A faster rule was proposed and is **not** used. The reason
is worth more than the rule.

§3 registers the arm as "trained by gradient descent on a linear cost". Two
readings are available. The **wide** one: what is bound is the cost and the
use of gradients, so Adam — a first-order method on the same linear cost — is
admissible. The **narrow** one: "gradient descent" names θ ← θ − η·g, and
another step rule is another arm.

The wide reading is this note read generously, and it is also the cheaper one.
How much cheaper is now measured: the narrow reading commits the study to
**about forty hours** of QCNN training (A3.8). Adam's step count at n = 12 was
never measured, because the rule was settled before the count was taken; at
n = 8 Adam converged in 100 steps against gradient descent's 320, and if that
ratio held, the wide reading would have cost roughly a third as much. So the
wide reading is both the generous reading of the note and, by something like
twenty-five hours, the convenient one. That combination of reasons is the
worst available. It is the *self-scoped* failure of "What a Verdict Assumes"
§04 — an instrument that sets its own scope, with the result falling in
favour of whoever set it. Adam was proposed after the cost was measured, not
before.

**Decided 15 November 2026: the narrow reading. Plain gradient descent.**

What that costs is measured rather than asserted — and the first figure put
to Ramon for this decision was the wrong one, which is recorded here because
the decision was taken while it stood. The grid was first run on the D1
variant that excludes a window of the field (A3.6), and there Adam reached a
mean training score of 0.9993 against gradient descent's 0.9893. That variant
was then demoted to a sensitivity check, so those are not the primary
figures. Re-run on the **primary D1**, three draws, each rule read at its own
converged length rather than at one point of a non-monotonic trace:

| rule | converged training score | steps to get there |
|---|---|---|
| gradient descent, 0.3 | 0.8740 | 320 |
| Adam, 0.03 | 0.8697 | 100 |

The difference is **0.0043, below the declared granularity of 0.005**. By
this study's own resolution rule the two step rules achieve the same thing,
and the narrow reading costs no training score at all — only compute. That is
a stronger basis for the decision than the figure it was taken on, and it is
the opposite of the direction a wrong figure usually moves a decision, so it
is said plainly rather than quietly corrected.

Both readings at one fixed point of the trace would have said otherwise: at
exactly 300 steps gradient descent reads 0.8820 against Adam's 0.8730, a gap
of nine thousandths that is an artefact of where the trace was cut. That is
the same error the convergence criterion made above, in miniature.

The same comparison at n = 12 is reported in the printout rather than
asserted here. If the gap there is substantial, that is a *substantive*
objection to the narrow reading and is taken up in a dated addendum — not a
cost objection.

### The step size is fixed by the grid, not by taste

The step size is not fixed by §3 under either reading, so it is measured, on
the same criterion:

> The step size is the one that reaches the higher **training** score at the
> measured run length, over a declared grid, because under-training the QCNN
> arm makes H1 easier. No test score enters this choice. On a tie the smaller
> step size wins.

Grid {0.01, 0.03, 0.1, 0.3}, at n = 8 on D1, three draws, 300 steps, five
starts. The measured values are in the committed printout.

One result of that grid belongs here rather than in a printout: **0.1 — the
step size this addendum registered a few paragraphs above, before the grid was
run — is not even the best setting of its own rule.** On the primary D1 at
n = 8 it reached 0.8467 against 0.8820 at 0.3, and the worst cell of the grid,
0.01, reached 0.7247 — sixteen points below what the same circuit on the same
data reaches. A step size written down without a grid behind it is a free
parameter set by taste, and in this study a free parameter set by taste is one
more thing that can run in one direction without anyone noticing.

Registered: **plain gradient descent on the linear cost of §3, at step size
0.3, the setting the grid selects on the primary D1.**

### The step count, measured

The amended criterion was then applied at n = 12 on the primary D1, plain
gradient descent at 0.3, five starts, **three draws over a declared run
length of 1000 steps**:

| step | draw 0 | draw 1 | draw 2 | mean |
|---|---|---|---|---|
| 20 | 0.874 | 0.835 | 0.855 | 0.8547 |
| 100 | 0.910 | 0.918 | 0.879 | 0.9023 |
| 200 | 0.913 | 0.941 | 0.890 | 0.9147 |
| 320 | 0.917 | 0.940 | 0.898 | 0.9183 |
| 480 | 0.917 | 0.948 | 0.902 | 0.9223 |
| **500** | 0.917 | 0.961 | 0.902 | **0.9267** |
| 520 | 0.917 | 0.965 | 0.902 | 0.9280 |
| 600 | 0.918 | 0.949 | 0.903 | 0.9233 |
| 1000 | 0.919 | 0.949 | 0.906 | 0.9247 |

**Registered: 500 steps**, used unchanged at every size and on both datasets.
The guard clause is clear — the count sits 500 steps inside the measured run,
not against its edge.

Two things about that number are stated rather than left to be noticed.

**It is a close call.** The criterion bounds the range of the remainder by one
granularity step: from 480 the range is 0.0057, from 500 it is 0.0047 against
a threshold of 0.005. The count hangs on three ten-thousandths. Three draws
with one late-flipping start are not an instrument that resolves finer, and
the honest reading is that the criterion licenses 500 rather than that 500 is
exact.

**It does not matter at the study's resolution, and that is the point.** From
500 to 1000 the mean moves by 0.0020, under the granularity of 0.005, so
every count from 500 onward gives the same answer and 500 is merely the
cheapest the criterion allows. What would have mattered is stopping earlier:
at 320 — the value the n = 8 run would have suggested — the mean is 0.9183
against 0.9267, a gap of 0.0084, which is 1.7 granularity steps of
under-training handed to the QCNN arm and therefore to H1. The extra ten
hours of compute buy exactly that.

## A3.5 H4 is refuted by the repaired control, before the run

This is the third defect found in this design by building the instrument, and
it is of one kind with the first two: a hypothesis carried forward unchanged
when the thing it refers to was replaced.

H4 reads: *on D2, the bodyness-4 classifier closes a substantial part of the
gap that the bodyness-2 classifier shows — that is, the gap is a property of
the feature bodyness and not of logistic regression as a model class.* It was
written against the cluster family, whose string order parameter runs over a
bounded number of sites, so weight-4 features could in principle reach it.
Addendum 1 replaced D2 with R1 and addendum 2 with R1 v2, and A1.6 point 4
carried the remaining hypotheses over as **unchanged**. H4 was among them.

Under R1 v2 it cannot hold. Local RY rotations commute with the partial trace
over the complement of any subset, so for every **proper** subset S the
reduced state is identical in both classes, and every Pauli expectation of
weight below n carries exactly zero information about the label — the
argument of A1.5, which the repair of A2.3 preserves rather than weakens.
Weight 4 is below n at all three sizes. Measured at n = 8, α = 0.4, five
draws:

| features compared between the two labels | largest difference |
|---|---|
| all 276 of weight ≤ 2 | 6.7e-16 |
| 120 random strings of weight 3 and 4 | 4.4e-16 |
| the weight-8 witness ⟨X^⊗8⟩ | **1.5487**, by design |

So **H4 is refuted before the study runs, analytically and not by
measurement.** Running it would be a demonstration, not a test.

### H4 is not struck. It is reported.

Decided 15 November 2026: **H4 stays in the hypothesis list**, with the
verdict *refuted by construction, before the run* and the measurement above
beside it. It is not deleted.

The reason is the discipline this strand already applies everywhere else. The
notes are not edited; they change only in dated addenda, and "withdrawn" has
meant *superseded* rather than *deleted* throughout — section 6 of
`design_cut_degeneracy_EN.md` is superseded for all future use and its text
still stands. If H4 vanished from the list, a reader could no longer tell
whether it went because it could not hold or because it was inconvenient.
Left in place with its refutation recorded, the whole arc is visible and the
reader judges it.

There is a second reason, which only became clear while checking it. H4's
failure is itself a result: it shows that R1 v2 holds **every** arm below
weight n at the majority share, at any weight and not only at weight 2. That
is stronger than A1.5 claimed, and the repair of A2.3 preserved it rather
than weakening it. It is a finding about the quality of the control, not an
embarrassment.

### What H4 can no longer do, something else now does

1. **The bodyness-4 arm becomes a leak check.** It still runs on D2, and its
   score must sit at the majority-class share. If it does not, something in
   the pipeline is carrying the label into the features, and that is a defect
   in the instrument, not a finding about bodyness. Added to §8 as a fourth
   invalidating condition:

   > **4. A low-bodyness arm beats chance on the control.** If any arm
   > restricted to features of weight below n scores above the majority-class
   > share on D2 by more than one granularity step, the run is void. The
   > construction guarantees those features carry no label information; a
   > score above chance means the implementation does not match the
   > construction.

   This is strictly stronger than H4 was. H4 could only have been confirmed
   or not; the leak check can void the whole run. H4's own verdict is
   reported beside it, as decided above.

2. **One regularisation procedure for every classical arm**, in every
   classifier class: strength chosen by cross-validation **inside the
   training set alone**, over the same declared grid for every arm, in every
   fold. The test set is never touched by that choice. This matters most on
   D1, where the bodyness-2 arm has 630 features at n = 12 against 200
   training states, and where an unregularised fit would make H1 — the
   convenient hypothesis — easier for a reason that has nothing to do with
   bodyness.

3. **A third model class.** A1.6 point 2 asks for a linear and a nonlinear
   class and lets the stronger stand. The tree ensemble the registered probe
   used does not scale in the number of features: one fit on 7,458 features
   is 141 s, which is **79 hours** over the registered budget at weight 4.
   An RBF-kernel SVM costs **0.1 minutes** for the whole budget at every
   size, because its cost is in the number of rows and not of columns — and
   in this regime, 200 rows against tens of thousands of columns, it is also
   the stronger nonlinear classifier. Both reasons point the same way and
   neither is hidden behind the other.

   So: three classes — L2 logistic regression, RBF-kernel SVM, and the tree
   ensemble where it is affordable, which is weight ≤ 2. At weight 4 the tree
   class is dropped and the printout records the restriction beside the
   score. Since weight 4 is now only a leak check, and a leak check wants the
   strongest classifier available, the kernel class serves it better than the
   trees would have.

   Adding a class strengthens the classical side, which makes H5 harder and
   H1 easier. Both directions at once, and unavoidable: point 2 exists
   precisely to stop the study concluding "the features do not carry the
   label" when the truth is "this classifier could not extract it", so the
   registered policy is to give the classical arms their best shot.

   One check the classes needed and nearly did not get: the first test of
   them put the label in an XOR of two features among 300, which nobody can
   find from 200 rows, so all three sat at chance and the test established
   nothing. On a task that discriminates — an XOR of two of ten features —
   the linear class sits at 0.455 and the two nonlinear ones at 0.820 and
   0.980, while on a linearly separable task all three reach 0.91 to 0.93.
   Only then does "the stronger class stands" mean anything.

4. **An exact shortcut for the linear class.** For L2 logistic regression the
   optimum lies in the span of the training rows, so a fit on 46,665 features
   is identical to a fit on at most 200 columns of the Gram factorisation.
   Checked: decision values agree to 1e-14 at every grid value — provided
   p > m. Below that a weakly regularised fit is ill-conditioned enough that
   the two parameterisations halt at different points (measured: 1.1 apart at
   p = 60 against m = 120, with identical scores), so the rule is p > m and
   the gate checks the agreement at the shapes actually used. It is an
   identity, not a dimension reduction.

| n | weight ≤ 1 | weight ≤ 2 | weight ≤ 4 |
|---|---|---|---|
| 8 | 24 | 276 | 7,458 |
| 10 | 30 | 435 | 20,685 |
| 12 | 36 | 630 | 46,665 |

3. **A capacity-control arm was considered and dropped.** The idea was a
   fifth arm with bodyness-4's feature count and bodyness-2's information, to
   separate a capacity effect from a bodyness effect. It is unnecessary: on
   D2 nothing below weight n closes any gap, and on D1 the comparison is
   scored on held-out states, which is what controls for capacity. It is
   recorded here because it was considered, and because dropping an arm after
   registration needs a reason that is not its cost — this one has no bearing
   on H1 in either direction.

## A3.6 The field window of D1, and why it stays in

§4 says the field is "swept across the critical point" and does not say
whether the sweep includes the neighbourhood of h = 1. At finite n the
transition is rounded over a width scaling as 1/n — the 1D Ising
correlation-length exponent is 1 — and inside that window the two phases'
ground states overlap so strongly that no arm can separate them.

That is not neutral. A common error floor under every arm at once compresses
the differences between them, which makes H1 — the convenient hypothesis —
easier to satisfy, and it raises the noise floor, which can push a verdict to
*not evaluable* on its own. Excluding the window would be the sharper
measurement.

**Decided 15 November 2026: the primary D1 keeps the whole sweep.** h uniform
on (0, 2), label = [h > 1], nothing excluded.

D1 is the dataset the claim is about, and A1.7 states that addendum 1 leaves
it exactly as registered. A cleaned-up D1 would be a friendlier benchmark
than the one being reproduced, and a reproduction of a claim about a
benchmark may not quietly improve the benchmark.

The window is run beside it as a **declared sensitivity check at n = 8
only**, excluding |h − 1| < 2/n, with the expected direction stated before
the run:

> Removing the window should **widen** the differences between arms. If it
> does not, or if a verdict moves, the printout reports it rather than
> resolving it by preference.

Only n = 8, because running both variants at every size doubles the QCNN
budget, and n = 8 is the cheapest size at which the question is answerable at
all. The printout says it is one size and not evidence for the other two.

One thing this decision cost, recorded because the alternative was tempting:
every measurement made on 15 November before it — the optimiser grid at n = 8
and a first step-count run at n = 12 — had been made on the windowed variant.
They were re-run on the primary D1. That they already existed is not an
argument for the windowed variant, and it was not allowed to become one.

### How large the effect is, measured

The re-run gives the size of it directly, because the same configuration ran
on both. At n = 8, three draws, 300 steps, gradient descent at 0.3:

| D1 variant | mean training score |
|---|---|
| windowed, the critical region excluded | 0.9893 |
| primary, the whole sweep | 0.8820 |

**Eleven points.** That is the common error floor the ambiguous states put
under the arm, and it is twenty times the 0.005 granularity the verdicts are
read against. The prediction above was that the window compresses the
*differences* between arms. What the measurement shows first is that it lifts
the *level* of every arm at once — the same cause, and the one that would
have been easy to report as a better result.

It also sets where the verdicts live: the ceiling of this task on the
registered D1 is near 0.88, not near 1.0. A reader who expects scores close
to unity should know why they are not.

## A3.7 What has been verified, and against what

The simulator is built in layers, each checked against the layer below rather
than against itself:

| what | checked against | largest deviation |
|---|---|---|
| weight-≤2 features from 2-qubit marginals | one sparse matrix–vector product per Pauli string | 2e-16 |
| gate layer, reference implementation | dense 2ⁿ × 2ⁿ construction of the same circuit | 1.1e-14 |
| adjoint gradient | central finite differences | 4e-10 |
| batched implementation | reference implementation | 1.4e-15 |
| real-arithmetic implementation | reference implementation, value **and** gradient, n = 4…10 | 1.3e-15 |

§8's third invalidating condition demands that exact ground states agree with
an independent slower construction element by element and not by norm or by
count. The first two rows are that check for the feature path and for the
circuit; the ground-state check itself runs inside the study and is printed
with it.

One rejected option is recorded because it was measured rather than guessed:
single precision throughout buys a factor 1.3 in speed for a relative
gradient error of 1.3e-6. It is not used.

### A random stream nobody had seeded

The ground-state gate was run three times during the build and returned
3.68e-13, then 6.80e-13, then 9.37e-13. `eigsh` hands ARPACK a random
starting vector when none is given, and that stream is **not** numpy's global
one: two calls on the same matrix differed element-wise by 3.2e-14, and
`np.random.seed` before them changed nothing.

Three decimal places of a convergence residual is far too little to move a
classification, and that is not the point. A figure this repository promises
to reproduce may not rest on a stream nobody seeded — which is the defect
`design_cut_degeneracy_EN_addendum_4.md` was written about, and one of the
four explanations eliminated there. It was not that one in the warm-start
case. It was this one here, and nothing in the apparatus would have said so:
the gate compares against a dense diagonalisation and passes at any of those
three values.

The starting vector is now fixed from a declared seed. The same draw built
twice is bit-identical — states, fields and labels — and that equality is
itself a gate, so a future change that reintroduces an unseeded stream fails
the check run rather than surviving in a printout. The ground-state gate now
returns 9.37e-13 every time.

This is the sixth declaration of the strand doing its work. A run whose
figures will later be checked must commit its printout with the code; a
printout that cannot be produced twice is not a printout, and only a gate
that compares a run against itself looks there.

## A3.8 What the registered budget costs, and what was not done to reduce it

Measured on two cores, 200 training states, 40 steps, five starts per draw;
the registered budget is 20 draws × 3 sizes × 2 datasets.

| n | complex path | real path | factor |
|---|---|---|---|
| 8 | 31.6 s | 11.8 s | 2.69 |
| 10 | 153.8 s | 54.4 s | 2.83 |
| 12 | 1360.0 s | 339.2 s | 4.01 |
| **whole study at 40 steps** | **17.2 h** | **4.5 h** | |

The figures are per draw of five starts at 40 steps and scale linearly in the
step count A3.4 fixes; the registered budget at that count is at the end of
this section, after a third speed-up that this table predates. Both speed-ups behind the factor are **exact**:

- **Real arithmetic throughout.** Every gate in the circuit is real — RY, CZ
  and controlled-RY — the TFIM Hamiltonian is real symmetric, and R1 version 2
  is built from RY rotations (addendum 2, A2.3). No amplitude in this study is
  ever complex, so carrying an imaginary part was carrying zeros.
- **A gradient that is never materialised.** The adjoint derivative of one
  gate is contracted into four inner products, 2 Re Σᵢⱼ (dU)ᵢⱼ Mᵢⱼ with
  Mᵢⱼ = Σ λᵢ ψⱼ, instead of forming dU|ψ⟩ once per parameter per step.

Neither changes a number, and both were verified against the complex
reference before being used — the fifth row of A3.7.

### A third speed-up, and a constant that nearly flips

The gate layer at n = 12 is **bandwidth-bound, not flop-bound**: five starts
by 200 states by 2¹² amplitudes is a 33 MB array, far past any cache. Summing
the gradient in blocks of states changes the loop order and nothing else — the
gradient is a sum over states, so blocking is exact up to the order of the
floating-point summation. Verified: relative gradient deviation 4.6e-15,
readout bit-identical, and end-to-end through the trainer the same scores with
8.9e-15 parameter deviation after sixty steps.

Seconds per step, full batch against blocked, at the registered five starts
and 200 states. **Three rounds are given rather than one**, because this is a
shared machine and a timing quoted to three digits from a single round would
be a precision the measurement does not have:

| n | batch array | full batch | blocked | gain from blocking |
|---|---|---|---|---|
| 8 | 2.05 MB | 0.297 / 0.273 | 0.318 / 0.305 | **0.93 / 0.90** — blocking *costs* 7 to 12 % |
| 10 | 8.19 MB | 1.334 / 1.183 | 1.126 / 1.170 | 1.18 / 1.01 |
| 12 | 32.77 MB | 9.511 / 7.866 / 10.383 | 5.510 / 5.363 / 6.093 | 1.73 / 1.47 / 1.70 |

The rule is declared, not tuned per size: block where the batch array exceeds
8 MB, and then to 4 MB.

At n = 12 the gain is large and survives every round. At n = 8 blocking
reliably costs, and the rule correctly does not apply it. **At n = 10 the
honest statement is that blocking is not demonstrably better** — 1.18 in one
round and 1.01 in the next, which is the spread of the machine, not an
effect. The rule blocks there, and that is defended only as *not worse*, not
as faster.

**The constant is fragile, and a reader should see it.** At n = 10 the array
is 8.19 MB against a threshold of 8 MB — a margin of 2.4 per cent, so a
threshold set three per cent higher would flip the decision at that size. The
measurement above is why that flip costs nothing either way. An earlier
version of this code asserted in its own documentation that the batch *fits*
at n = 10 and is therefore not blocked; that was simply false, and
re-measuring for this section is what found it.

### The registered budget

At the 500 steps A3.4 fixes, 20 draws × 2 datasets per size, plus the n = 8
sensitivity check of A3.6:

| | QCNN arm |
|---|---|
| n = 8 | 1.5 – 1.7 h |
| n = 10 | 6.3 – 6.6 h |
| n = 12 | 29.8 – 33.9 h |
| D1w at n = 8 (A3.6) | ≈ 0.8 h |
| classical arms, all sizes | ≈ 0.3 h |
| dataset construction | ≈ 0.5 h |
| **total** | **39 – 44 h** |

A range, for the reason given above: the two rounds that produced it came out
at 37.7 and 41.9 hours for the QCNN arm. Anyone planning against this should
plan for the upper end.

The classical arms are measured, not assumed: one D2 draw at n = 12, all
three weights, is 16.7 s — of which the weight-4 arm is 6.2 s of feature
extraction over 46,665 columns and 1.0 s of fitting, the Gram identity of
A3.5 having reduced the fit to 200 columns. Without blocking at n = 12 the
same study would be some 53 to 58 hours.

One warning for anyone who re-times this. Timing the gate layer on **complex**
input doubles the bytes moved and therefore the step time, and so overstates
the whole budget by about a factor two; the first re-measurement made for
this section did exactly that and reported 74 hours. The states of this study
are real, for the reason given above.

**No approximation was taken.** Fewer draws, smaller training batches and
fewer gradient steps were each considered and rejected. Every one of them
either widens an interval or weakens the QCNN arm, and both make H1 — the
convenient hypothesis — easier to satisfy. A cost reduction that makes the
convenient hypothesis easier is the defect this whole strand is about, and it
is not available here merely because the alternative is a long run.

## A3.9 Registered amendments

Points 1 to 3 and 6 to 8 were decisions the note left open and are registered
here. Points 4, 5 and 9 were Ramon's, taken on 15 November 2026 after the
measurements below were put to him; where he decided against the cheaper
option, the cost is recorded beside the decision rather than in a footnote.

1. Depth is ⌈log₂ n⌉ with the leftover qubit carried (A3.1).
2. The QCNN's per-draw score is the mean over its five starts, not the best
   (A3.2).
3. The §6 noise floor is the statistic of A3.3.
4. **§3 is read narrowly: plain gradient descent, not Adam** (A3.4). The step
   size comes from a declared grid on the primary D1, and the measured cost
   of the narrow reading is reported at both n = 8 and n = 12.
5. **H4 stays in the hypothesis list**, reported as refuted by construction
   rather than deleted (A3.5), and a fourth invalidating condition — the leak
   check — is added to §8.
6. m_train = 200, shared by every arm; the linear cost of §3; step count
   fixed by the **amended** criterion of A3.4, the original having fired on a
   plateau.
7. Three classifier classes for every classical arm, one regularisation
   procedure across all of them, the tree class dropped at weight 4 as
   unaffordable, and the Gram identity used for the linear class where p > m
   (A3.5).
8. The ground-state solver's starting vector is fixed from a declared seed,
   and bit-identity of a rebuilt draw is itself a gate (A3.7).
9. **The primary D1 keeps the whole field sweep**; the window is a declared
   sensitivity check at n = 8 only (A3.6).

H4 is reported, not withdrawn, and nothing in the note or in addenda 1 and 2
is deleted or edited. Of the changes above, those that move the study move it
in one direction: a hypothesis gains a condition that can void the run, a
classical arm gains a model class, a convergence criterion that stopped early
is replaced by one that stops late, and two readings that would have been
cheaper were declined.

## A3.10 What this addendum cost to write

Three defects in the registered design and eight in my own work, all found by
building the instrument rather than by reading or by running the study:

| found | what | direction |
|---|---|---|
| in the note | §3 registers a linear cost; a logistic one had been written | — |
| in the note | H4 cannot hold under the control that replaced D2 | — |
| in the note | "L = log₂ n" is not an integer at two of three sizes | — |
| in my work | the convergence criterion fired on a plateau, 17 points early | against the QCNN |
| in my work | the amended criterion bounded the rise, so it stopped at a local maximum | **for** the QCNN |
| in my work | the amended criterion returned a count at the edge of the run | neither |
| in my work | the step size I registered was not the best of its own rule | against the QCNN |
| in my work | the ground-state solver ran on a stream nobody had seeded | neither |
| in my work | the blocking rule's own documentation claimed the batch fits at n = 10 | neither |
| in my work | the budget was re-timed on complex input and overstated twofold | neither |
| in my work | the optimiser figures first put to Ramon came from the demoted D1 variant | neither |

The direction column is there because a list of one's own mistakes is worth
little if they all happen to point the same way. Two of these would have
handicapped the QCNN arm and so made H1 — the convenient hypothesis — easier;
one would have flattered it. The rest move no verdict and cost only compute
or credibility.

The unseeded solver is the one worth naming twice. It is the same class of
defect as the warm-start episode of `design_cut_degeneracy_EN_addendum_4.md`,
where an uncontrolled random stream was one of four explanations checked and
eliminated. It was not that one there. It was that one here — and the
apparatus would never have said so, because every gate compared the run
against something external and passed at any of the three values the stream
produced. Only a gate that compares a run against itself looks there, and
there was not one until today.

## A3.11 Status

**Addendum 1 is accepted as of 15 November 2026.** Its four amendments of
A1.6 — D2 withdrawn and replaced by R1, both a linear and a nonlinear
classifier in every classical arm, the new hypothesis H6, and the four
declarations of §5 left unchanged — stood as *proposed, not yet registered*,
and A1.3 blocked the main run until they were accepted: with the original
control in place, invalidating condition 1 could not fire, so no D1 result
would have been interpretable. Addendum 2 then replaced R1 with version 2 and
the measurement script was written against that design throughout.

**That block is lifted here.** The amendments are accepted, R1 version 2 is
the registered control, and condition 1 can fire — A3.7 records the gate that
shows it does, which is the standing rule that a positive control needs its
own demonstration that something passes it. Addendum 1 itself is not edited —
nothing in the note or in addenda 1 and 2 is — so this paragraph is where its
acceptance is recorded and dated.

Separately, the three questions this addendum left to Ramon rather than
deciding for him were put to him with the cost of each reading measured, and
he decided them on the same date: §3 read narrowly, H4 reported rather than
struck, and the primary D1 left whole with the field window demoted to a
sensitivity check. Those are points 4, 5 and 9 of A3.9.

**Addendum 3 is registered as of 15 November 2026**, before any score of the
study exists. Four files are committed together, and they are what "fixed"
means here:

| file | what it fixes |
|---|---|
| `designs/design_qcnn_bodyness_EN_addendum_3.md` | this document |
| `calculations/qcnn_bodyness_build.txt` | the printout A3.7 and A3.8 cite |
| `calculations/qcnn_bodyness_core.py` | simulator, datasets, arms, verdicts |
| `calculations/qcnn_bodyness.py` | the five gates and the run and report modes |

Run without arguments the script executes the gates and nothing else, which
is what the collective run of the repository calls; the study itself is
started by hand, one dataset and one size at a time, because it takes two
days. The README row and the slow-list entry follow in the next commit and
change no measurement.

**The main run begins after this commit**, and the resumable per-draw store
it writes to is empty at this point. Anyone who wants to check that the
instrument predates the data has both timestamps.

What the study is now permitted to produce: the four verdicts of §6 —
*separated*, *bounded*, *unresolved*, *not evaluable* — on H1, H2, H3, H5 and
H6, with H4 reported as refuted by construction. "Equivalent" remains
unavailable as a verdict, and a measured noise floor above 0.05 forces *not
evaluable* whatever the point estimates say.
