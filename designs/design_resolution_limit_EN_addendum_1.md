# Addendum 1 to the design note "A resolution limit that works"

**Date:** 5 November 2026, after the first application of the method.
**Status:** the note is not altered; version 2 stands as committed. Everything
below is additional and dated.

The calculation is `calculations/resolution_limit.py`, output in
`designs/resolution_limit_output.txt`.

---

## A1.1 The four criteria of section 6

**(1) A verdict everywhere, never a blank.** Twelve comparisons, twelve
verdicts, no `nan`. The failed limit it replaces returned nothing at three of
six sizes.

**(2a) Not evaluable where the sample is too small.** The warm-start comparison
has three usable graphs at n = 10, 12 and 18, below the declared u_min of five,
and all three return *not evaluable* — distinct from *unresolved*, which is the
distinction the old rule lacked.

**(2b) Bounded where the difference has no room.** At n = 14 the warm arm
averages 2.00 and the cold arm 2.81, both within one swap of the shared floor of
one swap, and the comparison returns *bounded*. The old rule returned a
resolution limit of 0.00 there and declared the difference resolved.

**(3) Invariant under relabelling families.** The rule never reads a family
label; the unit is the graph. Satisfied by construction rather than by
measurement.

**(4) Against A1.2 as published.** Five of six sizes agree. One differs, and
A1.3 adjudicates it as section 6 requires.

## A1.2 A misdeclaration in version 2, found by criterion 4

**What was wrong.** Version 2 declared one pair of bounds for both datasets:
floor one swap, ceiling n/2. That is correct for a migration between two
distinct partitions, which is what both arms of the warm-start comparison are.
It is wrong for the *mean pairwise distance among the partitions the runs
reached*, which is **zero** whenever every run reaches the same one. The floor of
that quantity is 0, not 2.

**What it produced.** A spurious *bounded* verdict at n = 10 in A1.2, where the
realised mean of 1.69 was read as resting on a floor of 2 that it in fact sits
below. With the floor correctly declared at 0, the two arms share no bound, the
comparison is not bounded, and it returns *unresolved* — which agrees with A1.2
as published.

**What has been corrected.** Bounds are now declared **per arm**, because two
arms of one comparison need not be the same quantity, and a comparison is
bounded only where both arms lie within one step of a bound they **share**.

**Why this is a correction of fact and not a relaxation of a rule.** Section 2
of the note states that bounds are a property of the definition and not of any
data. The attainable minimum of a quantity is therefore not something a run can
inform, and declaring it wrongly is an error of fact. **But the correction
changed a verdict that had already been seen**, which makes the corrected run
weaker evidence than a pre-declared one, and it is labelled as such here rather
than presented as the first run.

## A1.3 The one disagreement, adjudicated

**n = 18 in A1.2.** The old rule called it *unresolved*; the new rule calls it
*resolved*, with d = +2.72 and a 95 per cent interval of [+2.07, +3.23].

**The new verdict is the right one, and the reason is the defect the new rule
was built to fix.** The old resolution limit was the mean within-family range of
the realised figure across three graph seeds. That quantity measures how much
the realised distance varies *between graphs*, which is a property of the graphs
and not of how precisely this sample estimates a mean difference. With three
seeds per family it is also a very noisy estimate of even that. At n = 18 it came
out at 3.21 and so swallowed a difference of 2.72 that a bootstrap over the ten
units localises to [+2.07, +3.23] — an interval that does not come close to
zero.

So **A1.2's n = 18 verdict was a false negative**, produced by the same
instrument defect that produced `nan` at three sizes and a false zero at two.
That correction belongs in the degeneracy note and is recorded there in a
dated addendum, not left in this one.

The difference also exceeds one granularity step, so the claim is not merely
statistically localised but large enough to be a difference at all. Both tests
pass, which is what *resolved* requires.

## A1.4 What the warm-start comparison now says

Nothing is resolved. Three sizes are not evaluable, one is bounded, and the two
with enough units — n = 16 and n = 20 — return *unresolved* because the mean
difference of 1.47 and 1.69 falls below one granularity step, even though both
bootstrap intervals exclude zero.

**This confirms A2.2's withdrawal from a second and independent direction.** The
objective was withdrawn because the warm route reached the optimum *less often*
at one size. Now the cost advantage it was supposed to possess does not resolve
either. Two different grounds, neither chosen after the fact.

## A1.5 An open question about T1, declared and deliberately not decided

T1 compares the **mean** difference against the granularity. A mean over ten
graphs is not confined to even integers, so one can argue that the granularity
constrains an individual measurement and not an average, and that 1.47 ebits is
a legitimate quantity being wrongly refused.

There is a defence of the rule as written: if the mean advantage is under one
swap, then on a typical graph the warm route saves either nothing or exactly one
move, and "the warm route is cheaper" overstates that. The granularity of the
*decision* is one swap.

**The question is recorded and not settled here, and the reason matters more
than the question.** It arose after the output was read. Section 5 of the note
fixes g, the bounds, the unit, B, the level and u_min before any application and
forbids changing them to settle a borderline case. This is not one step ahead of
the data, as the version 2 revision was; it is behind them. A rule that is
relaxed once its author has seen which way a borderline case fell is not a rule,
whatever the argument accompanying it.

If T1 should apply to per-unit differences rather than to their mean, that is a
revision to be registered in a dated version 3, before any further application,
and the warm-start comparison can then be re-evaluated under it with both
verdicts on the record.

## A1.6 What stands

The method satisfies criteria 1, 2a, 2b and 3 as declared, and criterion 4 with
one adjudicated disagreement in the new rule's favour. It carries one corrected
misdeclaration, labelled, and one open question about T1 that must not be
answered until it is registered.

It replaces section 6 of `design_cut_degeneracy_EN.md` for all future use in
that note's strand, and is available to the other strands without being part of
them.
