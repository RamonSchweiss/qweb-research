# Design note: what a re-partition costs when it buys nothing

**Date:** 27 November 2026.
**Status:** registered before the measurement it governs. Version 1.

**The question.** The ledger of "What an Architecture Pays For" has five lines —
ebits, classical bits, transmitted qubits, remote gates, migration — and four of
them have numbers. Migration does not. This note registers the measurement that
is meant to give it one, and it is the measurement §15 of that article calls
specified and not yet run.

**Why a new note rather than another addendum.** `design_cut_degeneracy_EN.md`
asked whether a warm-started partitioner is cheaper than a cold one. That
objective was withdrawn outright in its addendum 2 on grounds that have nothing
to do with cost, and its addendum 2 said in as many words that if the cost
question is worth asking on its own it needs its own registration, which it did
not have. This is that registration. The earlier note is not revised, extended
or reopened.

---

## 1 What is already measured, and is therefore not registered here

**The optimum is degenerate, and the degeneracy is family-dependent.** Section 1
of the earlier note holds an exact enumeration over seven families and six
sizes: unique in the community family at every size, degenerate up to sixteen
times over in the regular family. That table is an enumeration and not a test;
it stands, and nothing here re-derives it.

**A re-partition can move four or more qubits while buying no crossing gate**,
at five of six sizes (A1.1, narrower than the hypothesis that was registered).

**The warm-start objective is withdrawn**, because the warm route reaches the
exact optimum less often than a cold restart at n = 12 (A2.2). This note does
not revisit that.

**The incumbent of that study was not well defined.** Addendum 5 of 27 November
measured it: relabelling the vertices changes the partition the heuristic
returns on 11 of 126 graphs. Section 5 below exists because of that finding,
and the hypotheses of section 4 are written knowing it.

## 2 Declared model class, and the currency

**The object.** Balanced bipartitions of the interaction graph as written, into
two parts, the cut counted as the number of crossing edges. Routing is not in
this note.

**Ground truth.** Exact enumeration of every balanced bipartition, feasible to
n = 20 (92,378 partitions). No heuristic result is ever used as the optimum.

**The currency.** One ebit per qubit moved between processors. Changing from a
balanced partition *P* to a balanced partition *Q* moves exactly the qubits
whose side differs, so the cost is the Hamming distance between the membership
vectors, minimised over the label symmetry. That distance is even, and at least
two whenever *P* ≠ *Q*. The granularity of every quantity below is therefore
**g = 2**, declared and never estimated from a sample.

**The optimal set.** For each graph, *O* is the set of exactly optimal balanced
bipartitions and *D* = |*O*|.

## 3 The primary quantity, which needs no heuristic at all

This is the change from the earlier note, and the reason this one can give the
ledger a number where that one could not.

A scheduler that re-solves the partitioning problem and does not prefer its
current assignment is handed an arbitrary member of *O*. The price of that
arbitrariness is the migration distance between the member it holds and the
member it is handed. Averaged over the pairs of *O*, that is a quantity of the
**graph**, computed by enumeration, with no heuristic, no eigensolver, no random
start and nothing to pin.

**M(G) = the mean pairwise migration distance within *O*.**

It is the cost per re-solve of not preferring the incumbent, and zero is what an
incumbent-preferring tie-break pays instead — that much is arithmetic, not a
measurement, and is stated here so that it is not later reported as a finding
(the earlier note's A1.4 made exactly that mistake and withdrew the objective as
vacuous).

**H1, registered.** *M* is at least one granularity step — two ebits — on at
least half of the graphs with *D* > 1, at every size from n = 12 to n = 20.

**H2, registered.** *M* rises with register size: the median of *M* over the
graphs with *D* > 1 at n = 20 exceeds the median at n = 12 by at least one
granularity step, resolved by the rule of section 7.

**H3, registered.** *M* is a property of the family rather than of the size: at
every size, the ordering of the four families that contribute at least five
graphs with *D* > 1 is the same. Registered in this restricted form because the
earlier note's H3 was posed over five to seven families and could not have been
falsified in the comfortable direction — a rank correlation over that many units
cannot separate 0.5 from zero, which A1.3 recorded. If fewer than four families
reach five graphs at any size, H3 is **not evaluable** at that size and is
reported so, not quietly dropped.

## 4 The secondary quantities, which do need a heuristic

These are the ones the earlier note tried to measure. They are kept because the
ledger wants what a real scheduler pays and not only what the enumeration says,
and they are secondary because they depend on the apparatus of section 5.

**H4, registered.** On graphs where the incumbent is not optimal, a refinement
warm-started at the incumbent reaches the optimum at a lower migration cost
from the incumbent than a cold restart does, **counted over every usable
graph** and not only over those where both routes arrive. A route that does not
reach the optimum is charged the migration to the partition it does return plus
the migration from there to the nearest optimal partition, because a scheduler
that must end at the optimum pays both.

This is the repair of A2.3's selection: that table counted only graphs where
both routes arrived, which conditions on success and makes the comparison a
statement about the graphs that happened to be easy for both.

**H5, registered.** The conditional comparison of A2.3 — cost over graphs where
both routes reach the optimum — points the same way as H4. Registered
separately so that the two cannot be conflated, and because agreement between a
conditioned and an unconditioned comparison is informative while a single
conditioned one is not.

## 5 The incumbent, pinned

The incumbent is the partition a single-shot heuristic returns. Addendum 5 of
the earlier note showed that as written this was not a property of the graph:
ties in the Fiedler vector at the median split are ordered by vertex index, and
a numerically indistinguishable eigenspace hands back an arbitrary member.
Both are removed here, before any run.

**Rule E — the eigenvector must be determined.** Let λ₁ ≤ λ₂ ≤ λ₃ be the three
smallest Laplacian eigenvalues. If (λ₃ − λ₂) / λ_max < τ with **τ = 1e-6**
declared here, the Fiedler vector is not determined by the graph, and the graph
is **ambiguous**: excluded, counted, and reported separately.

**Rule P — the split must be determined.** Let *T* be the set of balanced
splits consistent with the ordering of the Fiedler vector, which has more than
one member exactly when entries tie across the median. Take the members of *T*
of minimum cut. If that subset is a single partition under the label symmetry,
it is the incumbent. Otherwise the graph is **ambiguous** in the same sense:
excluded, counted, reported.

Both rules are defined without reference to the vertex numbering, so a graph
that passes them has an incumbent that is a property of the graph. Neither rule
resolves an ambiguity by choosing; ambiguity is reported, because choosing is
what put the earlier study where it is.

**The refinement** is pairwise swapping inside the balanced class, as in the
earlier note, with balance asserted on the way out.

## 6 Declared degenerate and excluded subsets

Named now, before the run, reported separately, never pooled.

- ***D* = 1.** No re-partition can move anything; *M* is zero by definition and
  the graph contributes nothing to section 3. The community family is expected
  here at every size on the earlier enumeration.
- **Incumbent already optimal.** Section 4 has no question to ask; the graph
  contributes to section 3 only.
- **Ambiguous under rule E or rule P.** Excluded from section 4 and counted. If
  more than one graph in five is excluded this way at any size, the heuristic
  arm is reported as **not evaluable** at that size rather than measured on what
  survives, because a sample selected by the failure of a tie-break is not a
  sample of graphs.

**Pooling across families is itself a declared error**, as in the earlier note:
section 02 of the published article records a Simpson's paradox created by
pooling symmetric families with their chorded relatives. Every number is printed
per family; the pooled figure is printed only beside them.

## 7 The resolution rule

The one registered in `design_resolution_limit_EN.md`, not the superseded rule
of the earlier note's section 6:

- **T1, granularity:** |d| ≥ g with g = 2, declared above.
- **T2, sampling:** a 95 per cent percentile bootstrap over the declared unit,
  B = 2000, excluding zero. **The unit is the graph.**
- **Bounded:** both arms within one step of the same bound.
- **Not evaluable:** fewer than u_min = 5 units, kept strictly apart from
  *unresolved*.

Both T1 and T2 must pass for **resolved**. A difference that agrees with a
hypothesis and fails either is reported as unresolved, not as support.

## 8 Invalidating conditions

**A relabelling that moves the incumbent.** For every graph entering section 4,
twenty permutations drawn from a declared seed are applied and the incumbent
recomputed. If any permutation returns a different partition, the **run is
void**, not merely different — the same standing the balance assertion has in
the earlier note. The check costs seconds for the whole grid.

**A heuristic optimum used as ground truth.** Enumeration only, to n = 20.

**A changed currency.** Anything other than one ebit per qubit moved changes
every threshold here.

**A heuristic that leaves the balanced class.** Balance asserted on exit; a run
in which the assertion fires is void.

**A figure that exists only as a literal.** Every run commits its printout
beside its code, in the same commit, as addendum 4 of the earlier note declared
after that rule was learned the hard way.

## 9 Result-independent stopping condition

Fixed before any run and evaluable without knowing which way anything points:

- **sizes** n = 12, 14, 16, 18, 20 — n = 10 is dropped because four fifths of
  the grid there fell into the declared degenerate subset of the earlier study;
- **density** m = 1.5 n;
- **families** the seven of the published grid;
- **seeds** 0 to 9, ten per family and size, where the earlier study had three.
  The limiting spread is between graphs and not within them, which A1.2
  recorded; more restarts would not have helped and more graphs will;
- **restarts** twenty per graph for the cold route.

That is 350 graphs, against 126. No size, seed, family or restart count is added
afterwards to settle a borderline case.

## 10 What this cannot show

Two parts only. Balanced bipartitions only. One density. The interaction graph
as written, so nothing here says anything about what routing does. Registers
above n = 20 are outside the enumeration ceiling and outside this note. One
heuristic family — spectral bisection with pairwise refinement — so every
statement in section 4 is a statement about that family and not about
partitioners in general; METIS and KaHyPar are not tested.

*M* is the price of re-solving without preferring the incumbent. It is not the
price of a layer: whether the optimal set itself changes between layers is not
established — the published measurement says the optimal cut *cost* is the same
at the first and last layer and says nothing about the set — and this note does
not assume it does or does not.

The oracle, as everywhere in this programme, is assumed and not counted.
