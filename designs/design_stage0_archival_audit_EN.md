# Design note: Stage 0, an archival feasibility audit for the calibration-age programme

**Status:** PROPOSED, version 4, 30 October 2026. Version 1 was written on
21 October before any archive had been searched; version 2 incorporated
Venkateswaran Ramamurthy's comments of 24 October; version 3 answered his
questions of 25 October about what F3 and F4 require; this version closes the
gap his reservation of 30 October exposed in F3. Still **not in
force**. It
comes into force when both authors have agreed it and it has been committed,
which must happen before the formal audit begins. The note is being revised
rather than amended precisely because nothing has been committed yet; once it
is, nothing in it changes except in a dated addendum.

**What changed in version 4.** Section 2 now declares a **model class**, and
F3's third condition is judged against that class and no other. The reason is
that the first two conditions of F3 are read off a record — the data is there
or it is not — while "identified rather than merely consistent" is a property
of a record *against a model*. Until the model was named, that condition was
not assessable before the search, and worse, the class could have been chosen
afterwards to suit what was found. Section 7 now treats such a substitution as
an invalidating condition. The bar is neither raised nor lowered by this; it is
made measurable.

**What changed in version 3.** Section 2 now defines an **age bin** and a
**repeat**, so that F4's "three repeats at comparable τ" means something
checkable. F3 now states what the observations must *support*, not only what
they must *be*, and carries the rationale for its threshold. No bar has moved.
The changes make two bars precise; they do not make either easier to meet, and
in the case of F3 they make it harder.

**What changed in version 2.** Section 2.5 is new: it records that exploratory
reconnaissance took place before the note was in force, and fixes how that is
handled. Section 5 now separates exploratory source identification from the
formal audit and defines the freeze. F2 and F4 now require informative
comparisons rather than sufficient counts, through the definition of a
comparison set in section 2.

**Why Stage 0 exists.** The question behind the programme is whether the *age*
of a noise model contributes measurable predictive error — not whether a model
and a device disagree, which they always do. Stage 1 would measure that. Stage 0
asks only whether the published record can carry such a measurement at all,
before any device time is sought.

This is a feasibility assessment. It presumes neither that drift exists nor that
any effect of it is measurable.

---

## 1 What Stage 0 answers, and what it does not

**It answers:** can experimental outcomes be paired with calibration records
whose age, backend, workload and relevant configuration are known well enough
to test whether predictive error changes with calibration age?

**It does not answer:** whether predictive error does change with calibration
age. No such effect is computed during Stage 0. Section 4 makes that a rule
rather than an intention.

## 2 Definitions

**Calibration age τ.** The interval between the timestamp of the calibration
record a prediction was built from and the timestamp of the experimental run it
is compared against. τ is a property of a pair, not of a record.

Where a source distinguishes the timestamp of a calibration *update* from the
timestamps of individual property *benchmarks*, the audit records both and
states which one it used. The two can differ, and a τ computed from the wrong
one is not a τ.

**Matched pair.** An experimental outcome and a calibration record for which all
of the following are recoverable from the published material: backend identity,
both timestamps, the circuit or workload, and the configuration relevant to the
prediction.

**Comparison set.** A group of matched pairs that differ in τ and agree on
everything the audit can check: the same backend, the same workload class, and
the same declared backend version or architecture. A declared change of version
or coupling map ends a comparison set and begins another.

This definition carries the whole anti-confounding requirement. Thirty matched
pairs spread over thirty different configurations are thirty single cases, and
τ would be confounded with backend, workload and hardware change. The bars below
are therefore stated over comparison sets, not over the raw count of pairs.

**Age bin.** The observed range of τ within a comparison set, divided into equal
intervals on a logarithmic scale. The rule is fixed here; the boundaries follow
from it mechanically once the range is known, and are not chosen. A logarithmic
division is used because F4 asks for a span of an order of magnitude, and equal
linear intervals over such a span would put almost every pair in the last bin.

**Repeat.** Two or more matched pairs in the same age bin of the same comparison
set, drawn from **distinct experimental runs**. Two pairs built from one run
against one calibration record are one observation counted twice, not a repeat.
Repeats are what allow sampling variation to be told apart from an age effect;
without the distinctness requirement they do not.

**Fresh fit.** A noise model fitted to the observations of the same experimental
record, rather than to the calibration snapshot. The comparison between the
original calibration-based prediction and a fresh fit is what separates
staleness from model incompleteness: a gap that survives a fresh fit is not an
age effect.

A fresh fit is only meaningful if the record **identifies** the model rather
than merely being consistent with it. Twenty records of one circuit constrain
far less than five records of four different circuits, however many shots each
carries. F3 therefore asks for identifiability and not only for raw data.

**Declared model class.** Identifiability is meaningless without saying of
what. The class is fixed here, before the search: independent Pauli error
channels, with a rate per qubit for single-qubit operations, a rate per
coupling-map edge for two-qubit operations, and a readout-error rate per qubit.
This is the class that published calibration records parameterise, which is why
it and not a richer one is the subject of the question.

Identifiability in F3 means identifiability of *this* class's parameters for the
backend concerned, and of no other class. Where a record would identify only a
smaller class — a single averaged gate error rather than per-edge rates, say —
the audit records that it identifies the smaller class and counts the pair as
failing F3, rather than quietly lowering the class to fit the record.

The class is declared rather than derived. It is the right class for the
question only to the extent that calibration records describe devices this way;
if Stage 1 later needs a richer class, that is a finding about the class and
belongs in Stage 1's own note, not in a revision of this one.

## 2.5 Exploratory reconnaissance, recorded

Before this note was in force, Venkateswaran Ramamurthy carried out an initial
exploratory search and reported three leads. They are recorded here with their
status stated by him and not softened:

1. IBM Quantum's documented historical backend properties and downloadable
   calibration data, which distinguish calibration-update timestamps from
   individual property-benchmark timestamps.
2. A 2026 Zenodo dataset of raw repetition-code experiments on three IBM
   processors, with calibration data captured at execution time.
3. Published work analysing historical IBM backend properties for long-term
   dependability, as a route to further candidate records.

**None of these has been verified against any of the four bars.** They are
candidate entries for the source list and nothing more. Recording them here does
not pre-qualify them, and the audit must reach a verdict on each of them by the
same route and against the same bars as on any source found later.

The reason for writing this down rather than absorbing it quietly is that a
search which happened before the rules were fixed is exactly the kind of thing
that later looks like the rules were fitted to what was found. The dates are
therefore on the record: version 1 on 21 October, the reconnaissance reported on
24 October, the freeze and the formal audit still ahead.

## 3 The four feasibility criteria, with their bars

Each is answered yes or no against a bar fixed here, before the formal search.

**F1 — accessibility.** At least **two independent sources** of paired material,
publicly accessible without an institutional login, machine-readable, with
timestamps on both the calibration record and the experimental run.

**F2 — matchability.** At least **thirty matched pairs** as defined in section 2,
spread over at least **two backends** — and at least one **comparison set** of at
least **fifteen** of those pairs. The second clause is what makes the first
informative.

**F3 — the fresh-fit arm.** For at least **twenty** matched pairs, all three of
the following are present in the published material:

1. *Outcome data* at the level of shots or of per-circuit outcome
   distributions — not a reported summary statistic, and not a quantity that
   has already been fitted.
2. *The circuit as executed*, after transpilation, since a noise model attaches
   to physical operations and not to the logical program.
3. *Enough distinct circuits within one comparison set* that the parameters of
   the **declared model class** of section 2 are identified rather than merely
   consistent. Since that class carries per-qubit and per-edge parameters, a
   single circuit repeated cannot fix them. Identifiability is judged against
   the declared class and against no other.

Condition 3 is the one that makes F3 bite. The first two ask what the record
contains; the third asks what it can answer. The first two are read off the
record. The third is a property of the record against a named model, which is
why section 2 names it in advance.

*Rationale for twenty.* It is not a statistical power calculation and is not
presented as one. F4's minimum comparison set holds fifteen pairs — three age
bins of five. Twenty is that minimum plus a margin of five, so that the
fresh-fit arm can cover a whole comparison set rather than part of one, with a
little room for pairs that fail on inspection. If the number is wrong it is
wrong in that sense, and the argument against it should be about coverage, not
about significance.

**F4 — leverage in τ.** Within at least one **comparison set**: calibration age
spans at least **one order of magnitude**, with at least **five matched pairs**
in each of at least **three** age bins as defined in section 2, and at least
**three repeats**, also as defined there — pairs in the same bin from distinct
experimental runs. Without repeats, sampling variation cannot be separated from
an age effect; without a comparison set, neither can a change of backend.

A criterion that is met only by combining incommensurable sources is not met.

## 4 The rule that keeps the audit honest

**No effect is computed during Stage 0.** All four criteria are structural: they
ask what shape the data has, not what it says. Predictive error against τ is not
plotted, not fitted and not inspected, on any subset, until Stage 1 has been
designed and registered on the basis of the Stage 0 verdict alone.

The reason is plain. A go/no-go decision taken after seeing which way the effect
points is not a feasibility decision.

## 5 Sources: leads, freeze, audit — in that order

The three steps are kept separate and dated.

**Exploratory identification.** Leads may be collected from any route, including
the reconnaissance already recorded in section 2.5. This step has no bars and
reaches no verdicts.

**The freeze.** Both authors agree a source list and a publication window, write
them down, and date them. This note is committed at the same moment. Nothing is
added to the list afterwards.

**The audit.** Every source on the frozen list is examined and recorded with its
verdict, **the failures included**.

If a source outside the frozen list is discovered during the audit and appears
to matter, it is recorded as a late discovery and the audit is reported twice:
once on the frozen list alone, and once including it, with the difference
stated. It does not quietly join the list.

Searching an archive until something fits is the archival form of raising a
stopping rule to find a result. The freeze is what prevents it, and the freeze
is worth nothing if it happens after the qualifying sources are known.

## 6 The stopping decision, fixed before the search

- **All four met:** Stage 1 is designed as a bounded re-analysis of the archive,
  with its own design note registered before any computation. No device time is
  sought at this point.
- **F1 and F2 met, F3 or F4 not:** the archive establishes that the gap exists
  but cannot separate its causes or resolve τ. Stage 1 then requires fresh runs,
  and the note says so plainly rather than proceeding with what is available.
- **F1 or F2 not met:** the archive cannot carry the question. That is the
  finding, it is published as such, and the programme either seeks device time
  for a question stated afresh or is set down.

No bar is lowered after the search. An outcome close to a bar is reported as
close to the bar and treated as a failure of that bar.

## 7 What would invalidate the audit

**Looking at outcomes.** If predictive error against τ is examined before the
verdict is fixed, the verdict is void and the audit is reported as void.

**A freeze that is not a freeze.** If the source list is adjusted after any
source's verdict is known, the audit is reported as unfrozen and the adjustment
named.

**Unrecoverable provenance.** A pair whose timestamps or configuration must be
inferred rather than read is not a matched pair, however plausible the
inference.

**A model class substituted after the search.** If identifiability is judged
against any class other than the one declared in section 2, the audit is
reported as unfrozen and the substitution named. Lowering the class to fit the
records available is the same failure as lowering a bar, and is harder to see,
which is why it is written down here.

## 8 What Stage 0 does not establish

Nothing about drift. Nothing about any device. Nothing about whether the effect,
if it exists, is large enough to matter operationally. It establishes only
whether the published record can be made to answer the question, and at what
size.

It is also not a measurement of the archive's quality in general. It asks one
question of it.

## 9 Deliverable

One document: the recorded leads with their dates, the frozen source list with
the date it was frozen, every source examined with its verdict, the four
criteria answered yes or no against their bars, the counts and the comparison
sets behind each answer, and the stopping decision that follows. Published
whichever way it comes out.

If the audit contradicts a later text, the text is wrong.
