# Addendum 2 to the design note "How many cuts are equally good, and what it costs to change between them"

**Date:** 5 November 2026, after the run of the objective registered in
Addendum 1, section A1.5.
**Status:** neither the note nor Addendum 1 is altered; both stand as
committed. Everything below is additional and dated.

**Summary.** The replacement objective is withdrawn outright, by the withdrawal
condition fixed for it before the run. The cost comparison it was built around
points the registered way but is moot, and the instrument that was supposed to
decide whether it pointed far enough did not work. That instrument defect is
the third in this note's short life and the most useful thing in this addendum.

The calculation is `calculations/cut_degeneracy_warmstart.py`, output in
`designs/cut_degeneracy_warmstart_output.txt`.

---

## A2.1 The declared degenerate subset is most of the grid

Declared in A1.5 before the run: graphs on which spectral bisection already
returns an optimal partition contribute nothing, because there the incumbent is
the destination.

      n    graphs    degenerate    usable    share usable
     10        21            17         4            0.19
     12        21            15         6            0.29
     14        21            12         9            0.43
     16        21             8        13            0.62
     18        21            15         6            0.29
     20        21            12         9            0.43

Between four and thirteen graphs per size survive the subset. Section 4 of the
note required that a result consisting largely of zeros say so, and it does:
**on 81 per cent of the grid at n = 10 there is no question to ask.** Everything
below rests on the remainder.

## A2.2 The objective is withdrawn outright

A1.5 fixed this: *if the warm route reaches the optimum less often, it is
withdrawn outright, because a cheaper route to a worse cut is not the claim.*

      n    usable    warm reaches    cold per start    warm >= cold
     10         4            0.75              0.56    yes
     12         6            0.50              0.65    NO
     14         9            0.78              0.61    yes
     16        13            0.77              0.57    yes
     18         6            0.50              0.39    yes
     20         9            0.89              0.38    yes

At n = 12 the warm route reaches the exact optimum on half the usable graphs
where an individual cold start reaches it on 0.65 of its attempts. The condition
fires. **The objective is withdrawn.**

It is withdrawn on one size out of six, and it is not restated to exclude that
size. The same rule was applied to H1 in A1.1 yesterday, which failed at n = 10
and was likewise recorded as refuted rather than narrowed afterwards. A
withdrawal condition that only fires when it is convenient is not a withdrawal
condition.

## A2.3 The cost comparison, which the withdrawal makes moot

Recorded because it was measured, and marked for what it is.

      n    pairs    warm    cold     diff    resolution    verdict
     10        3    2.00    2.00    +0.00           nan    no spread
     12        3    2.00    2.00    +0.00           nan    no spread
     14        7    2.00    2.81    +0.81          0.00    warm cheaper
     16       10    2.60    4.07    +1.47          1.33    warm cheaper
     18        3    2.67    3.84    +1.18           nan    no spread
     20        8    2.50    4.19    +1.69          0.00    warm cheaper

Counted only where both routes reach the exact optimum, since comparing the
price of arriving somewhere worse is not the registered comparison.

The direction is the registered one wherever the figures separate at all, and at
the two largest sizes the gap is one and a half to one and three quarter ebits.
**That is not a result of this programme.** The objective it belonged to was
withdrawn in A2.2 on independent grounds, and a withdrawn objective does not
get its cost table promoted to a finding because the numbers came out the
preferred way. If the cost question is worth asking on its own, it needs its own
registration, which it does not have.

## A2.4 The resolution limit did not work here, and that is the finding

Section 6 of the note defined the resolution limit as the mean within-family
range of the measured figure across the three graph seeds. Applied here, it fails
in two different ways at once.

**Undefined at three of six sizes.** With three to seven usable pairs spread over
seven families, most families contribute fewer than two graphs, so there is no
within-family range to take. The limit comes out as `nan` and the rule has
nothing to evaluate.

**Zero at two sizes, for the wrong reason.** At n = 14 and n = 20 the limit
evaluates to 0.00, and the rule therefore declares the difference resolved. But
the spread is zero because the warm cost sits on its **floor**: two qubits is the
smallest possible nonzero migration, one swap, and almost every warm run lands
there. A quantity pinned at its floor has no spread, and a measure of precision
built from its spread reports perfect precision for a reason that has nothing to
do with how precise the sample is.

So of six sizes, the resolution rule was undefined at three and misleading at
two. It worked at exactly one, n = 16, where thirteen usable graphs gave several
families two or more entries and the warm cost was not floored.

**This matters beyond this addendum.** The resolution limit was registered in the
note on 4 November and proposed to V. Ramamurthy on 3 November as a fourth
safeguard alongside the three. The idea stands — an agreement read to more digits
than the data carries is worth nothing — but **this implementation of it does
not**, and a safeguard that returns `nan` or a false zero is worse than none,
because it decides and sounds principled while doing it.

What a working version needs, stated so that the next note can register it
rather than invent it under pressure: a spread taken over something that remains
populated when the usable set shrinks, which the within-family range does not;
and an explicit floor check, so that a quantity resting on its smallest possible
value is reported as floored rather than as precisely measured.

## A2.5 The count of defects, kept honestly

This note was registered on 4 November. In two days it has produced four
findings about its own instruments and none about partitioning:

1. The original objective was vacuous — its outcome fixed before any run
   (A1.4).
2. H3 was unfalsifiable in the comfortable direction — a rank correlation over
   five or six families cannot separate 0.5 from zero (A1.3).
3. The refinement routine left the balanced class and reported a comfortable
   result, in the scoping script (section 5 of the note).
4. The resolution limit is undefined or floored at five of six sizes (A2.4).

Against that: the degeneracy enumeration of section 1 of the note, which is
exact and stands, and H1's underlying claim at five of six sizes.

Four instrument defects in two days is not a good ratio, and the note is not
pretending otherwise. Three of the four were caught by rules written down before
the runs, which is the only reason they are findings rather than published
claims.

## A2.6 What stands

The degeneracy table of section 1 of the note: the exact optimum is unique in
the community family at every size tested and degenerate up to sixteen times
over in the regular family. The currency, the ground truth and the bounds of
sections 2 and 7. A1.1's narrower claim, that a re-partition can move four or
more qubits while buying no crossing gate, at five of six sizes.

Nothing published on the site is affected, because nothing from this note has
been published.
