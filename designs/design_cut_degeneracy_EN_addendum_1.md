# Addendum 1 to the design note "How many cuts are equally good, and what it costs to change between them"

**Date:** 4 November 2026, after the run registered in version 1 of the note.
**Status:** the note is not altered; its text, including its hypotheses as
written, stands as committed. Everything below is additional and dated.

**Summary.** Of three registered hypotheses, one is refuted as written, one
agrees in direction but is unresolved at half the sizes measured, and one is
refuted and was badly posed. The registered objective is withdrawn as vacuous,
and the defect is in the registration rather than in the data. A replacement
objective is registered here, before it is run.

The calculation is `calculations/cut_degeneracy.py`, output in
`designs/cut_degeneracy_output.txt`.

---

## A1.1 H1 is refuted as written

Registered: among graphs with *D* > 1, the diameter of the optimal set is at
least four qubits for at least half of them, **at every size from n = 10 to
n = 20**.

      n    graphs D>1    diam >= 4    share    H1
     10             9            4     0.44    fails
     12             9            6     0.67    holds
     14            12            9     0.75    holds
     16            15           14     0.93    holds
     18            10            8     0.80    holds
     20            12           10     0.83    holds

It fails at n = 10. The hypothesis said every size and it is therefore refuted,
and it is not restated to fit.

**What the data support, labelled as what it is.** From n = 12 upwards the share
runs 0.67 to 0.93 and rises with size, which is the pattern one would expect if
the optimal set grows with the register. That is a post-hoc observation about
six points, not a registered finding, and it is not quoted as one. If it is
worth anything it is worth registering separately and measuring on sizes this
run did not use.

So the underlying claim — that a re-partition can move four or more qubits while
buying not one crossing gate — is **established at five of six sizes and not at
the smallest**. That is a narrower statement than the one registered this
morning, and it is the one the run supports.

## A1.2 H2 agrees in direction and is unresolved at half the sizes

Registered: the distance between the optimal partitions two independent
randomised runs return is smaller than the diameter of the optimal set.

      n    mean diam    mean realised    ratio    margin    resolution
     10         2.89             1.69     0.59      1.20          1.50
     12         4.00             2.32     0.58      1.68          2.08
     14         4.67             2.42     0.52      2.25          1.09
     16         6.53             3.15     0.48      3.38          1.84
     18         6.00             3.28     0.55      2.72          3.21
     20         7.50             3.73     0.50      3.77          2.99

The direction is the registered one at all six sizes. By the resolution limit
declared in section 6 of the note — the mean within-family range of the realised
figure across the three graph seeds — the margin exceeds it at n = 14, 16 and 20
and does not at n = 10, 12 and 18.

**Reported, therefore: the direction holds, and the size of the effect is
resolved at three sizes of six.** Not "H2 confirmed".

**And the ratio must not be read as structure.** It runs 0.59, 0.58, 0.52, 0.48,
0.55, 0.50 — strikingly close to one half, and stable across a factor of two in
register size. That is exactly the shape this programme has twice been caught
by: the sample cannot separate 0.50 from 0.55, so the stability is consistent
with a constant one half and is not evidence for it. It is recorded as
unresolved. A run that could settle it would need more graph seeds, not more
restarts, because the spread that limits it is between graphs and not within
them.

## A1.3 H3 is refuted, and was badly posed

Registered: the ordering of families by diameter matches their ordering by *D*,
at every size.

      n    families used    Spearman rho
     10                5            0.60
     12                5            0.50
     14                6            0.77
     16                6           -0.31
     18                5            0.50
     20                6            0.37

Negative at n = 16, so the hypothesis is refuted as written.

**It should not have been registered in that form, and that is the more useful
finding.** With five or six families, a rank correlation of 0.5 is not separable
from zero — the instrument cannot resolve a moderate ordering agreement at all.
Every positive row above is therefore uninformative in the same way the negative
row is, and the hypothesis would have been unfalsifiable in the comfortable
direction: a rho of 0.6 would have been quoted as support for something this
sample cannot see.

This is the resolution limit of section 6 applied to a **hypothesis** rather
than to a result, and it is the third defect of my own registration found in one
day. The other two are in A1.4 and in section 5 of the note.

## A1.4 The registered objective is withdrawn as vacuous

Registered: an incumbent-preferring tie-break — among all exactly optimal
partitions, return the one nearest the current assignment — reduces the realised
migration cost to zero without giving up a crossing gate.

It does, and no run could have come out otherwise. If the incumbent is itself
optimal then the nearest optimal partition to it is itself, at distance zero.
The same holds for a refinement warm-started at the incumbent: pairwise swapping
accepts only strict improvements, so from an optimal partition it makes no move.

An objective whose outcome is fixed before the measurement is the failure these
notes exist to prevent. It is **withdrawn**, not confirmed, and the defect is in
the registration.

## A1.5 The replacement objective, registered here and not yet run

**The non-vacuous case is an incumbent that is not optimal.** The scoping run of
4 November showed this happens in 1 to 13 of 21 graphs depending on the
heuristic, so it is the common case rather than a corner.

**Registered objective.** Let the incumbent be the partition a single-shot
heuristic returns — spectral bisection, which the scoping run showed misses the
optimum on 4 to 13 of 21 graphs. Compare two ways of reaching the exact optimum
from there:

1. a refinement warm-started at the incumbent, and
2. a cold restart from a random start, as in H2.

The objective: the warm start reaches the optimum as often as the cold restart
does, and at strictly lower migration cost from the incumbent.

**Withdrawal condition, fixed now.** If the difference in migration cost between
the two routes is smaller than the resolution limit of section 6, measured the
same way, the objective is withdrawn as unresolved rather than reported as
either outcome. If the warm start reaches the optimum less often, it is withdrawn
outright, because a cheaper route to a worse cut is not the claim.

**Declared degenerate subset for this objective.** Graphs on which the
single-shot heuristic already returns an optimal partition: there the incumbent
is optimal, the question collapses into A1.4, and the case contributes nothing.
Named now, reported separately, never pooled.

**Declared invalidating condition.** Using spectral bisection's own cut as the
optimum, rather than the enumeration, would make the measurement describe the
heuristic. Enumeration only, to n = 20, as in section 2 of the note.

**Stopping condition.** The sizes, density, families, seeds and restart count of
section 6, unchanged. Nothing is added afterwards to settle a borderline case.

This objective is not measured in the run reported above. Measuring it in the
same run that found the defect would be choosing the question after seeing the
data.

## A1.6 What stands

The degeneracy table of section 1 of the note, which is an exact enumeration and
not a test of anything: the optimum is unique in the community family at every
size tested, and degenerate up to sixteen times over in the regular family. The
currency, the ground truth and the bounds of sections 2 and 7. Nothing published
on the site is affected, because nothing here has been published.
