# Design note: how many cuts are equally good, and what it costs to change between them

**Date:** 4 November 2026.
**Status:** registered before the measurement it governs. Version 1.

**The question.** The published measurement says the gate-optimal cut does not
move: in twenty-one of twenty-one problem graphs the exact minimum gate cut is
the same at the first layer and at the last. That is a statement about the cut
*cost*. It says nothing about how many partitions achieve that cost. If several
do, then "the optimal cut" is not one object, and a scheduler that re-runs its
partitioner can be handed a different assignment of qubits to processors at
identical cost — paying migrations for nothing.

This note registers the measurement of that cost. It does not revise any
published result.

---

## 1 What is already measured, and is therefore not registered here

A scoping calculation was run on 4 November 2026
(`calculations/findability_scoping.py`) to decide whether anything here was
worth building. It was not pre-registered and does not pretend to be. It tested
no hypothesis; it enumerated. Its numbers are reported as what they are, and
the hypotheses in section 3 are written in full knowledge of them, which is
stated rather than hidden.

**The findability gap is real but small, and in the wrong place.** Spectral
bisection misses the exact optimum on 4 to 13 of 21 graphs at n = 10 to 20,
by 1 to 4 crossing edges. With pairwise refinement, 1 to 3 of 21, by 1 to 2.
With twenty random starts, 0 of 21 up to n = 18 and 1 of 21 at n = 20. A
partitioner with any search budget finds the optimum at every size where the
optimum can be enumerated. The arm the merker proposed — does a heuristic find
the stable cut — would therefore measure one or two edges for single-shot
methods and nothing for multi-start ones, and becomes interesting only above
the enumeration ceiling, where there is no ground truth to compare against.
That arm is not built.

**The optimum is degenerate, and the degeneracy is family-dependent.** Counting
every optimal balanced bipartition exactly, averaged over three seeds:

      family           n=10     n=12     n=14     n=16     n=18     n=20
      random            1.7      2.0      4.3      5.0      4.7      6.0
      ring              2.7      3.3      3.0      4.0      2.0      5.3
      path              1.0      1.7      1.3      2.7      5.7      2.3
      regular           3.7     11.7     13.3     16.3      9.7      5.0
      scale-free        3.0      2.7      5.7      4.7      2.3      7.3
      community         1.0      1.0      1.0      1.0      1.0      1.0
      grid              2.7      1.0      1.3      2.0      1.0      4.3

In the community family the optimum is unique at every size tested. In the
regular family it is degenerate many times over, which is what symmetry does.
A pooled average of these two situations describes neither, and section 4 makes
pooling an invalidating condition rather than a stylistic preference.

## 2 Declared model class, and the currency

**The object.** Balanced bipartitions of the interaction graph **as written**,
into two parts, with the cut counted as the number of crossing edges — the same
quantity the published measurement minimises. Routing is not in this note; that
question lives in `design_routed_partition_orbit_EN.md`.

**Ground truth.** Exact enumeration of every balanced bipartition, which is
feasible to n = 20 (92,378 partitions). No heuristic result is ever used as the
optimum. Where the ceiling is exceeded, this note has nothing to say.

**The currency.** One ebit per qubit moved between processors, which is the
price `staleness_cost.py` already uses for a teleported qubit. Changing from
partition *P* to partition *Q*, both balanced, moves exactly the qubits whose
side differs, so the migration cost is the Hamming distance between the two
membership vectors, minimised over the label symmetry. Both being balanced, that
distance is even and at least two whenever *P* ≠ *Q*.

**The quantity this note is about.** For each graph, the set *O* of
exactly-optimal partitions, its size *D* = |*O*|, and the migration distances
within *O*. The diameter of *O* is the worst a scheduler could pay for a
re-partition that buys zero crossing gates.

Identifiability, as in the Stage 0 note, is judged against this class and no
other. Substituting the class after the measurement is an invalidating
condition, not a refinement.

## 3 Hypotheses, registered now

**H1. A re-partition can be expensive while buying nothing.** Among graphs with
*D* > 1, the diameter of *O* is at least four qubits — eight ebits of migration
at zero gate benefit — for at least half of them, at every size from n = 10 to
n = 20.

**H2. The realised cost is well below the diameter.** The distance between the
optimal partitions two independent randomised runs actually return is smaller
than the diameter of *O*, because a refinement started at random does not
sample *O* uniformly. Registered because the diameter is the easy number to
quote and is likely to overstate what a scheduler meets.

**H3. The structure follows the family, not the size.** The ordering of families
by diameter matches their ordering by *D*, and does so at every size. The
community family contributes nothing to either, being entirely degenerate in the
sense of section 4.

**The objective.** An incumbent-preferring tie-break — among all exactly
optimal partitions, return the one nearest the current assignment — reduces the
realised migration cost of H2 to zero without giving up a single crossing gate.
If it does, a partitioner that is told the current assignment is strictly better
than one that is not, at no cost in the quantity it optimises, and the
conclusion of the published article ("a scheduler needs an expiry test, not an
optimiser") gains a second, cheaper instrument alongside it.

## 4 Declared degenerate subset

**Graphs with *D* = 1.** Where the optimum is unique, no re-partition can move
anything and every quantity in section 3 is vacuous. On the scoping evidence the
whole community family is expected to fall here, and parts of path and grid. The
subset is named now, before the run, and is reported separately and never pooled
with the rest. A result that consists of a large subset contributing zeros is
reported as such.

**Pooling across families is itself the degeneracy to avoid.** Section 02 of the
published article records a Simpson's paradox created by pooling symmetric graph
families with their chorded relatives: a negative correlation appeared that
exists inside no single group. The same pooling here mixes *D* = 1 with *D* = 16.
Every number in the report is printed per family, and the pooled figure is
printed only beside them, never alone.

## 5 Declared invalidating conditions

**A heuristic that leaves the balanced class.** The first version of the scoping
script's refinement computed the two sides once per sweep and then mutated the
membership inside the loops, so later swaps moved qubits that had already moved.
It left the balanced class entirely — partitions with two of ten qubits on one
side, with cuts *below* the balanced optimum because they were not balanced at
all — and reported "0 of 21 misses", which is a heuristic winning by leaving the
class it is judged in. Balance is now asserted on the way out of the routine. Any
run in which that assertion fires is void rather than merely different.

**A heuristic optimum used as ground truth.** If *O* is taken from a heuristic
rather than from enumeration, every quantity in section 3 describes the
heuristic's search and not the graph. Enumeration only, to n = 20.

**A changed currency.** Pricing migration by anything other than one ebit per
qubit moved changes H1's threshold. The price is fixed here and a run that
departs from it is reported separately.

## 6 Result-independent stopping condition

Fixed before any run and evaluable without knowing which way anything points:
sizes n = 10, 12, 14, 16, 18, 20; density m = 1.5 n; the seven families of the
published grid with seeds 0, 1, 2; twenty random starts per graph for H2. No
size, seed or restart count is added afterwards to settle a borderline case.

**A resolution limit, for agreements as well as results.** Alongside the above,
the report declares the smallest difference in migration cost that twenty starts
on twenty-one graphs can separate, taken as the seed-to-seed spread. A difference
smaller than that is reported as **unresolved**, not as an effect and not as a
confirmation — including when it agrees with a hypothesis above. Two inferences
in this programme have already been wrong in exactly that way, matching a figure
to three digits from a sample that could not resolve three digits, and in one of
them two errors cancelled to produce the match.

An outcome close to the withdrawal boundary of the objective is reported as close
to it and treated as a withdrawal.

## 7 What is not measured here

Two parts only. Balanced bipartitions only. One density. The interaction graph as
written, so nothing here says anything about what routing does — and the orbit
note shows routing changes the picture. Registers above n = 20 are outside the
enumeration ceiling and outside this note. METIS, KaHyPar and other multilevel
partitioners are not tested; the heuristic family here is spectral bisection with
pairwise refinement, and every statement about heuristics is a statement about
that family.

The oracle, as everywhere in this programme, is assumed and not counted.
