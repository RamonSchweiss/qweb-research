# Does the partitioner find the stable cut?

**Design note, version 1. Registered 10 November 2026, before any run.**
Ramon Schweiss, QWeb © Research.

---

## 1 The question, and why it is not the published one

The published measurement says: in 21 of 21 problem graphs the exact minimum
gate cut is the same at the first layer and at the last.

That is a statement about the **object**. It says where the optimal cut lies and
that it stays there. It does not say that a real partitioner finds that cut, and
it does not say that a real partitioner's answer is stable across the layers.
The script that produced it enumerates every balanced bipartition exactly — 462
of them at n = 12 — so findability is not tested there. It is bypassed.

Two separate questions follow, and only the second is interesting.

- **Q1, quality.** Does a heuristic partitioner reach the exact optimum, and
  when it misses, by how much?
- **Q2, stability.** Does the heuristic's **chosen partition** move across
  layers in graphs where the optimal cut does not move?

Q2 is the one that matters. If the heuristic's answer wanders while the optimum
stands, the instability is a property of the partitioner and not of the
circuit — and it is invisible to anyone who only measures the optimum. That is
a different engineering problem with a different fix, and it is exactly the
separation the permutation control in
`designs/design_routed_partition_orbit_EN.md` performs for the router.

Daniel Hug's sentence is the frame: *the gap between what a model class can
represent and what its search reliably finds cuts both ways.* Here the "model
class" is the set of balanced bipartitions, which represents the optimum
trivially, and the search is a partitioner.

## 2 What the literature already answers — checked 10 November 2026

Two works were read before this design was fixed, to avoid measuring something
already published.

- **arXiv 2310.03942**, qubit and gate graph partitioning for DQC, applies
  **METIS** and reports no comparison against an exact optimum.
- **arXiv 2605.01974**, on the distortion of partitioning performance by random
  quantum circuits, is much closer: 6,508 circuits, k ∈ {2…10} QPUs, and seven
  partitioners — random, greedy, stochastic greedy, Fiduccia–Mattheyses,
  KaHyPar, Zoltan PHG and an evolutionary algorithm. It reports cut cost,
  scaling, strategy rankings and variability. But its results are **normalised
  against a random balanced assignment**, not against an optimum, and it does
  not test whether a heuristic partition moves across layers.

So neither question is answered. One observation about the second paper belongs
in the eventual article rather than here, but is recorded now so that it is
dated: a random balanced assignment is a baseline against which every
partitioner looks good. Choosing it is a modelling decision of exactly the kind
that moves a comparison point, and it is not stated as a limitation.

## 3 The heuristic set, fixed in advance

Chosen to match what the DQC literature actually uses, not what is convenient
here:

1. **Kernighan–Lin / Fiduccia–Mattheyses.** Already implemented as `kl()` in
   `calculations/cut_degeneracy.py`, with the balance assertion added on
   4 November after the defect described in section 6.
2. **Spectral.** Fiedler vector of the Laplacian, split at the median to keep
   the halves balanced. numpy only.
3. **Greedy**, and **stochastic greedy** with the same restart budget as KL.
4. **METIS**, via `pymetis`, if it installs in this environment. If it does
   not, that is recorded in the report as a declared absence. It is not quietly
   dropped and no substitute is called METIS.

Every arm reports its restart budget. A heuristic gap is a property of the
heuristic **and its budget**, and a gap quoted without the budget is not a
measurement.

## 4 Ground truth, and the capability horizon

Ground truth is exact enumeration of every balanced bipartition. **No heuristic
result is ever used as the optimum.** That is an invalidating condition, carried
over from the orbit note.

The horizon was measured on 10 November 2026, before this design was fixed, on
a graph family not used in the published work and with no heuristic involved —
so the probe cannot have biased what follows. Naive enumeration, one graph,
density 1.5:

| n | balanced bipartitions | seconds | complete |
|---|---|---|---|
| 12 | 462 | 0.01 | yes |
| 16 | 6,435 | 0.14 | yes |
| 20 | 92,378 | 2.04 | yes |
| 22 | 352,716 | 9.11 | yes |
| 24 | 1,352,078 | 38.25 | yes |
| 26 | 5,200,300 | — | needs a vectorised form |
| 28 | 20,058,300 | — | 0.56 GB as packed booleans |
| 30 | 77,558,760 | — | out of reach here |

Declared consequence: **exact ground truth is available to n = 24** in the
per-graph budget this study can afford. n = 26 is a stretch arm and is run only
if a separate dated line is added to this note first. Nothing above n = 28 is
claimed, and the limit is a property of this environment, not of the question.

## 5 Resolution limit

Every comparison passes through `designs/design_resolution_limit_EN.md`
version 2 before a verdict is spoken.

Granularity here is exact and equal to 1: a cut is an integer count of edges, so
the smallest nonzero difference is one edge. A gap of zero is therefore a true
zero and not a floor effect — which is the one place in this study where the
granularity test is trivially satisfied. The bootstrap arm still applies to any
**mean** gap across graphs, with the unit of analysis declared as the graph, not
the run, and u_min = 5.

Bounds are declared per arm, as corrected on 5 November: the realised gap and
the optimal gap have different floors and may not share a bound.

## 6 Declared degenerate subset

`cut_degeneracy.py` already measures D, the exact number of balanced
bipartitions reaching the minimum cut. Where D > 1, "the partition moved" can
mean a move **between two equally optimal partitions**, which is not a failure
of the partitioner and must not be counted as one.

So Q2 is measured in two separated quantities:

- **movement inside the optimal set** — the heuristic's answer changes but the
  cut cost stays at the optimum. Measured as migration distance, the same
  currency as `cut_degeneracy.py`: one ebit per qubit moved, Hamming distance of
  the membership vectors minimised over which processor holds which side.
- **movement out of the optimal set** — the cut cost gets worse. This is the
  failure Q2 is about.

Reporting these two as one number would be the defect this note exists to
avoid.

## 7 Registered hypotheses

- **H1.** At n ≤ 12 the heuristic gap is zero in the large majority of graphs.
  *This is the merker's own warning, stated as a hypothesis so that confirming
  it counts as a result: if the gap is zero everywhere, the study is a null and
  is published as one.*
- **H2.** The gap grows with n over the measured range.
- **H3.** In at least some graphs the heuristic's chosen partition leaves the
  optimal set at some layer while the exact optimum does not move.

H3 is the hypothesis an article would rest on. H1 and H2 are its preconditions,
and they are reported whatever they show.

## 8 Invalidating conditions

The run is void if any of these occurs:

- a heuristic result is used as the optimum anywhere;
- a reported partition is not balanced. The defect of 4 November — stale A/B
  lists during a mutating sweep, producing partitions with 2 of 10 qubits and
  cuts below the balanced optimum, while reporting "0 of 21 misses" — stays in
  this note as the reason the balance assertion is not optional;
- layers are compared without holding the graph and the seed fixed;
- a gap is reported without its restart budget;
- movement inside the optimal set is reported together with movement out of it.

## 9 Result-independent stopping condition

Fixed now, and not to be changed by what the numbers show:

- sizes n ∈ {10, 12, 14, 16, 18, 20, 22, 24};
- the seven families and three seeds of `cut_degeneracy.py`;
- restarts fixed at 20, as registered there on 4 November and not raised;
- the layer sequence taken unchanged from the script behind the 21-of-21 claim.

The study stops when that grid is complete. No arm is extended because a result
looked promising, and none is cut short because it looked dull.

## 10 What each outcome means

- **H3 confirmed.** The 21-of-21 answers the object question; the partitioner
  question is separate and has a different answer. The article says both, and
  the published claim gains a stated limitation rather than losing its force.
- **H3 refuted.** The stability is a property of the problem and not of the
  measurement, and the 21-of-21 is stronger than it was claimed to be. That is
  reported with the same prominence.
- **H1 refuted** — a large gap already at n = 10 — means the heuristic set or
  its budget is mis-specified. Then the instrument is fixed and dated before
  anything is interpreted, and no conclusion about findability is drawn from
  that run.
- **All gaps zero at every size.** A null, published as a null, with the
  horizon of section 4 stated so that the next person knows at which n the
  question becomes answerable again.

## 11 Still to be fixed before the run

Two scope items cannot be set from this environment and are recorded here as
open, to be filled in by a dated line in this note **before any result is
seen**:

- the generator parameters of the seven graph families, which live in
  `calculations/partition_topology.py`;
- the layer construction behind the 21-of-21 claim, which lives in the script
  that produced it.

Until both are in hand, no run is started. Reconstructing either from memory
would produce a different graph set and a measurement that is not comparable
with the published claim — and a silent mismatch of that kind is precisely what
this week's corrections were about.
