# Design note: a resolution limit that works, for agreements as well as results

**Date:** 5 November 2026. Version 2, registered before the method is applied to
anything. The note is revised rather than amended because nothing has been
committed yet; once it is, nothing changes except in a dated addendum.

**What changed in version 2, and it was caught while writing the code.**
Version 1's *bounded* clause fired when **either** arm's mean lay within one
granularity step of a bound. That is wrongly reasoned. A floor makes *that arm's
own spread* uninformative, but T2 bootstraps the **difference** across units,
not one arm, and the difference keeps varying as long as the other arm does. The
comparison is uninformative only when the difference itself is pinned by the
bounds — that is, when **both** arms sit within one step of the **same** bound.
Section 4 now says that.

This change was made before the method was applied to anything, and the
consequence was foreseeable: under version 1 every size of the warm-start
comparison would have been reported *bounded*, and under version 2 only the
sizes where both arms rest on the floor will be. That is recorded here rather
than left for someone to notice, because a rule relaxed by its author one step
ahead of the data is exactly the move this safeguard exists to prevent. The
defence is that the argument is about the mechanism — what a bootstrap of a
difference is and is not sensitive to — and not about any verdict; and that the
change makes the rule **stricter** where it matters, since two floored arms now
return *bounded* rather than the *unresolved* that version 1 would have given
them.

**Why this note exists.** On 3 November a resolution limit for *agreements* was
proposed as a fourth safeguard alongside the three this programme already uses.
On 4 November it was written into
`design_cut_degeneracy_EN.md` section 6. On 5 November it failed at its first
real use, recorded in that note's Addendum 2, section A2.4: undefined at three
of six sizes and a false zero at two more. The idea was right and the
implementation was not, and a safeguard that returns nothing or a false zero
while sounding principled is worse than having none.

**What was actually wrong.** The failed version tried to read one limit where
there are two. Sampling resolution — how precisely this sample estimates a
difference — and instrument granularity — the smallest difference the quantity
can take at all — are different quantities with different causes. The failed
version estimated granularity from spread, so when the measured quantity sat on
its own floor and had no room to vary, it reported perfect precision.

This note separates them and registers both, together with a third outcome the
failed version did not have.

---

## 1 What the safeguard is for

Three safeguards already guard against a *result* being misread: a declared
degenerate subset, a declared invalidating condition, and a result-independent
stopping condition. This one guards against a *confirmation* being misread.

The need is not hypothetical in this programme. Two inferences have failed in
exactly this shape, both recorded: a sensitivity reconstructed from published
figures that matched to three digits while being built on the wrong error
scaling, where two independent errors cancelled to produce the match; and a
structural property inferred from an agreement a sample could not have resolved.
An agreement is the dangerous direction, because a disagreement prompts a check
and an agreement does not.

## 2 The two limits, declared separately

**Granularity g.** The smallest nonzero difference the measured quantity can
take, by its own definition. This is a property of the definition and not of any
data, so it is written down before any run and cannot be read off a sample.

**Bounds [lo, hi].** The attainable minimum and maximum of the quantity, also by
definition.

*Worked example, for the quantity this will first be applied to.* Migration cost
is the number of qubits that change side between two balanced bipartitions,
minimised over the two labellings. Both partitions being balanced, the count is
even, so g = 2. Two distinct partitions differ by at least one swap, so the floor
for distinct partitions is 2, and the ceiling is n/2. All four numbers follow
from the definition in `design_cut_degeneracy_EN.md` section 2 and none from a
measurement.

**Unit of analysis u.** The thing the claim generalises over. The spread is taken
across units and across nothing else. This is the clause the failed version
lacked: it took graph families as the unit and graphs as replicates within them,
so when the usable set shrank and most families held fewer than two graphs there
was no spread to take. If a claim is about graphs, the unit is graphs.

## 3 The rule

A difference *d* between two arms is **resolved** only if it passes both tests.

**T1 — the granularity test.** |*d*| ≥ *g*. A difference smaller than one step
of the instrument is not a difference, however many units support it.

**T2 — the sampling test.** A percentile bootstrap interval for *d*, resampling
the declared units with replacement, excludes zero. Declared in advance:
**B = 2000** resamples and a **95 per cent** two-sided interval.

**Both must pass.** T1 without T2 is a difference the sample cannot support; T2
without T1 is a confidently measured difference smaller than the instrument can
express.

## 4 The third and fourth outcomes, which the failed version did not have

**Bounded.** If **both** arms' means lie within one granularity step of the
**same** declared bound, the comparison is reported as **bounded** and T2 is not
quoted for it. There the difference itself has no room to be anything but small,
so neither a small difference nor an agreement carries information. One arm
alone resting on a bound does *not* make a comparison bounded: T2 resamples the
difference across units, and the difference still varies while the other arm
does. Version 1 of this note had that wrong, for the reason given in the header.

**Not evaluable.** If the number of units is below a declared minimum, the
comparison is reported as **not evaluable** — and this is kept strictly separate
from *unresolved*. Unresolved means the data were able to speak and said the
difference is small. Not evaluable means the data did not speak. The failed
version printed `nan` in the same column as its verdicts, which invites exactly
the conflation this distinction exists to prevent.

**The declared minimum is u_min = 5 units.** This is a convention and is not
presented as a power calculation. A percentile bootstrap over fewer than five
units resamples a space too small for its interval to carry information. If the
number is wrong it is wrong as a convention, and the argument against it should
be about the resample space and not about significance.

So every comparison returns exactly one of four verdicts — **resolved**,
**unresolved**, **bounded**, **not evaluable** — and never a blank.

## 5 Result independence, stated because it is the whole point

The rule is applied identically whether the difference favours a hypothesis or
contradicts it. g, the bounds, the unit, B, the level and u_min are fixed here,
before any application. None of them may be changed to settle a borderline case,
and a borderline case is reported as borderline.

**And the rule applies to agreements.** Where two arms agree, or differ by less
than g, or differ within a bootstrap interval that includes zero, the agreement
is reported as carrying no weight rather than as support. This is the clause the
whole note exists for.

## 6 What would count as this method working

Declared now, so that it is not decided after the output is read.

1. It returns one of the four verdicts for every comparison, and never a blank
   or a `nan`.
2. On the two known failure modes of 5 November it returns **not evaluable**
   where the usable set was too small, and **bounded** where the measured
   quantity sat on its floor — rather than *resolved*, which is what the failed
   version returned there.
3. It is invariant under relabelling of graph families, since families are no
   longer the unit.
4. Applied to Addendum 1 section A1.2, where the failed limit was at least
   well-behaved, it either agrees with that section's resolved-or-unresolved
   split or disagrees — and where it disagrees, this note's addendum says which
   verdict is right and why, rather than noting the difference and moving on.

**Criterion 2 is not a success criterion in the ordinary sense and is not
counted as one.** The rule was designed from the *mechanism* of the two
failures — a spread that empties, a quantity with no room to vary — and not from
the verdicts they produced. If it now returns *bounded* where the old rule
returned *resolved*, that is the intended behaviour of a different rule and not
evidence that the new one is correct.

## 7 What this does not do

It does not make a small sample informative, and it is not a statistical test of
a hypothesis. It reports whether a difference is large enough to be a difference
and whether the sample can tell. It says nothing about why a difference exists,
and a resolved difference is not thereby an effect of the mechanism anyone
proposed.

It also does not rescue a defective instrument. The orbit null arm of
3 November was allowed moves the hardware could not make; no resolution rule
would have caught that, and the declared invalidating condition is what did.
This safeguard sits beside the other three and replaces none of them.

## 8 Where it will be applied first

To the warm-start comparison of `design_cut_degeneracy_EN_addendum_2.md`
section A2.3, and to the diameter-against-realised comparison of Addendum 1
section A1.2. Both are existing datasets, so no new measurement is involved and
the application is a re-evaluation under a declared rule rather than a new
result.

The calculation will be `calculations/resolution_limit.py`, with its printout
alongside.
