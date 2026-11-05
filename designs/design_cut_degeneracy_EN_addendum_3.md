# Addendum 3 to the design note "How many cuts are equally good, and what it costs to change between them"

**Date:** 5 November 2026.
**Status:** neither the note nor Addenda 1 and 2 are altered; all three stand as
committed. Everything below is additional and dated.

**What this does.** It records that one verdict in Addendum 1, section A1.2, was
a false negative, and that section 6 of the note — the resolution limit — is
superseded for all future use in this strand.

---

## A3.1 A1.2's n = 18 verdict is withdrawn and replaced

Addendum 1 section A1.2 reported, for the comparison of the diameter of the
optimal set against the distance two independent runs actually land apart:

> the margin exceeds it at n = 14, 16 and 20 and does not at n = 10, 12 and 18

The n = 18 half of that is wrong. Re-evaluated under the resolution limit of
`design_resolution_limit_EN.md`, the difference of +2.72 lies in a 95 per cent
bootstrap interval of [+2.07, +3.23] over the ten units, and exceeds one
granularity step. It is **resolved**.

      n     realised    diameter        d    95% interval      old      new
     10         1.69        2.89    +1.19    [+0.95, +1.47]    unres.   unres.
     12         2.32        4.00    +1.68    [+1.21, +2.20]    unres.   unres.
     14         2.42        4.67    +2.25    [+1.76, +2.76]    resolved resolved
     16         3.15        6.53    +3.38    [+2.74, +4.09]    resolved resolved
     18         3.28        6.00    +2.72    [+2.07, +3.23]    unres.   RESOLVED
     20         3.73        7.50    +3.77    [+2.91, +4.49]    resolved resolved

Five of six verdicts are unchanged. The calculation reproduced every figure of
A1.2 before re-evaluating any of them, and the reproduction check is in the
printout.

**So H2's direction is now resolved at four sizes of six rather than three.**
The underlying statement of A1.2 does not change: the distance two independent
randomised runs land apart is smaller than the diameter of the optimal set. What
changes is how much of the grid can say so.

## A3.2 Why the old verdict was wrong

Section 6 of the note defined the limit as the mean within-family range of the
measured figure across the three graph seeds. That measures how much the figure
varies **between graphs**, which is a property of the graphs, not of how
precisely this sample estimates a mean difference — and with three seeds per
family it is a noisy estimate of even that. At n = 18 it came out at 3.21 and
swallowed a difference that a bootstrap over the units localises nowhere near
zero.

The same defect produced `nan` at three sizes and a false zero at two in
Addendum 2, section A2.4. This is its third failure mode: a false negative.

## A3.3 Section 6 of the note is superseded

For every future use in this strand, the resolution limit is the one registered
in `design_resolution_limit_EN.md`: a declared granularity tested against the
difference, a percentile bootstrap over a declared unit of analysis, per-arm
bounds, and the two further verdicts *bounded* and *not evaluable* kept apart
from *unresolved*.

The note itself is not revised, in keeping with its own header: it is in force
and changes only in dated addenda. This is that addendum. Where section 6 and
the new note disagree, the new note governs, and the reason is recorded in
A3.2 rather than left to the reader.

## A3.4 What is not changed

A1.1's refutation of H1 at n = 10, which rested on a count and not on a
resolution. A1.3's refutation of H3, which rested on a rank correlation over
five or six families and on the observation that such a sample cannot separate
0.5 from zero — an argument the new limit supports rather than overturns.
A1.4's withdrawal of the original objective as vacuous. A2.2's withdrawal of the
replacement objective, which rested on reach rates and not on cost. The
degeneracy enumeration of section 1 of the note, which is exact.

A2.3's cost table, re-evaluated under the new limit, resolves nothing at any
size: not evaluable at three, bounded at one, and below one granularity step at
the two with enough units. That confirms A2.2's withdrawal from a second
direction and is recorded in Addendum 1 to the resolution-limit note.
