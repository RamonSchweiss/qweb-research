# Design note: Stage 0, an archival feasibility audit for the calibration-age programme

**Status:** PROPOSED, version 2, 24 October 2026. Version 1 was written on
21 October before any archive had been searched; this version incorporates
Venkateswaran Ramamurthy's comments of 24 October. Still **not in force**. It
comes into force when both authors have agreed it and it has been committed,
which must happen before the formal audit begins. The note is being revised
rather than amended precisely because nothing has been committed yet; once it
is, nothing in it changes except in a dated addendum.

**What changed in version 2.** Section 2.5 is new: it records that exploratory
reconnaissance took place before the note was in force, and fixes how that is
handled. Section 5 now separates exploratory source identification from the
formal audit and defines the freeze. F2 and F4 now require informative
comparisons rather than sufficient counts, through the definition of a
comparison set in section 2. All four bars are otherwise unchanged from
version 1 and remain open for revision until the note is committed.

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

**Fresh fit.** A noise model fitted to the observations of the same experimental
record, rather than to the calibration snapshot. The comparison between the
original calibration-based prediction and a fresh fit is what separates
staleness from model incompleteness: a gap that survives a fresh fit is not an
age effect.

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

**F3 — the fresh-fit arm.** For at least **twenty** of those pairs, the material
needed to fit a model to the observations themselves is present — per-shot or
per-circuit outcome data, not only a reported summary statistic. This is the
criterion most likely to fail, because published work usually reports fitted
quantities rather than the observations behind them, and it is also the one
without which Stage 1 cannot distinguish staleness from incompleteness.

**F4 — leverage in τ.** Within at least one **comparison set**: calibration age
spans at least **one order of magnitude**, with at least **five matched pairs**
in each of at least **three** age bins, and at least **three repeats** at
comparable τ. Without repeats, sampling variation cannot be separated from an
age effect; without a comparison set, neither can a change of backend.

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
