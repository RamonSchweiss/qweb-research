# Addendum 1 to the design note on the cut cost of an amplification iteration

**Date:** 1 November 2026. The note came into force earlier the same day and is
not altered by this addendum; everything below is a record of the run and its
verdict under the conditions the note fixed.

**The run.** `calculations/routed_diffusion_cut.py`, output preserved in
`routed_diffusion_cut_output.txt`. SABRE with the decay heuristic, trivial
initial layout, the five seeds declared in the script, n from 4 to 11 and
therefore P from 6 to 20, on the two declared coupling-map families.

---

## 1 The heavy-hex arm is void, by the note's own rule

All eight sizes fall inside the degenerate subset declared in section 9: three
as trees, where every edge is a cut edge, and five because the subgraph's
diameter reaches half its size, so there is no interior in which traffic could
stay. Heavy-hex therefore decides nothing here.

The rule was fixed before the run and it fired on everything. That is the entry:
induced subgraphs of heavy-hex(5) at P of 20 or fewer are too small to carry
this measurement.

**What would fix it, and what fixing it requires.** A larger host lattice —
heavy-hex(7) or beyond — would give subgraphs with an interior at these sizes.
That is a change to the instrument. It goes in a dated addendum of its own,
agreed before any rerun, and not into a quiet adjustment of the generator. A
degeneracy rule that is relaxed after it has fired is not a degeneracy rule.

## 2 The objective is withdrawn on the grid

Four non-degenerate sizes, and the stopping condition of section 10 fails at
every one of them. r is the median routed crossing fraction, m the logical
minimum fraction of 8 divided by the routed gate count, and the condition is
r - m < max(spread, 0.05).

      n    P   routed gates   routed cut      r       m     r-m   spread
      7   12             89           15  0.172   0.090  +0.083    0.056
      9   16            120           18  0.155   0.067  +0.089    0.080
     10   18            153           21  0.136   0.052  +0.084    0.064
     11   20            150           18  0.120   0.053  +0.067    0.041

The margins are narrow — at P = 20 the gap is 0.067 against a threshold of
0.05 — and a narrow withdrawal is still a withdrawal. Section 6's objective,
that a cut-oblivious router lands close to the logical minimum, does not hold
at the declared threshold.

## 3 What the withdrawal does and does not mean

It does not mean the cheap cut is squandered. The routed crossing is 15, 18, 21
and 18 gates against the logical eight: **a factor of 1.9 to 2.6, mean 2.25,
and flat across the four sizes.** The crossing fraction still falls with size,
from 0.172 to 0.120, so the 1/n behaviour established in section 3 survives
compilation. It is displaced, not destroyed.

The honest statement of the result is therefore narrower and more useful than
either the objective or its negation: **a cut-oblivious router costs about a
factor of two on the diffusion's cut, and the factor does not grow with the
register.**

The threshold of 0.05 was declared for a reason given in section 10 — the point
below which a crossing cost is a rounding error against the ledger — and it is
not adjusted now that it has bitten. A result close to a threshold is reported
as close to it.

## 4 The ledger entry of section 5 is corrected

Section 5 priced a distributed amplification iteration at eight ebits, which is
the logical minimum under free placement. On a grid with this router it is
about 18.

       n   iterations   at 8 per iteration   at 18 per iteration
      16          201                1,608                 3,618
      20          804                6,432                14,472
      30       25,735              205,880               463,230

**This is an extrapolation of the factor and not a measurement at those
sizes.** The factor 2.25 is measured at P up to 20, which corresponds to eleven
data qubits; a 16-qubit Grover needs P = 30, outside the measured range. What is
measured is that the factor is flat from P = 12 to P = 20. Whether it stays flat
beyond that is not established here.

## 5 The contrast inverts the original hypothesis a second time

Reported for context, as section 7 declared, and not part of the stopping
condition. At P = 20 on the grid:

      community QAOA layer     0.035
      the diffusion            0.120
      regular QAOA layer       0.156

The diffusion sits **between** two ordinary sparse workloads. A 3-regular graph
is more expensive to cut than the operator that version 1 of this note called
the limiting case of circuit partitioning. The community family, built to split
cleanly, is three times cheaper.

Version 1's hypothesis was refuted at the logical level in section 3. This
refutes the weaker version of it that might have survived — that the diffusion
is at least unusually expensive among real workloads. It is not. It is in the
middle of the field.

## 6 What stands after this addendum

- The arithmetic of sections 3 and 4 is unaffected: the V-chain's logical
  minimum balanced cut is eight gates at every size, and the ancilla-free
  synthesis has a complete interaction graph.
- The routing objective of section 6 is **withdrawn** on the grid and
  **undecided** on heavy-hex.
- What replaces it is a measured factor rather than a claim: about 2.25, flat
  over the sizes tested, on one router at one heuristic.
- The ledger entry is 18 ebits per iteration on a grid with SABRE, 8 under free
  placement, and the gap between them is a statement about compilation.

## 7 What this still does not establish

A cut-aware router. SABRE minimises total swaps and not swaps across a
boundary, so the factor of 2.25 is an upper bound on what a router told about
the module boundary would cost, and no bound at all on what it could achieve.
This is the invalidating condition of section 8 and it applies to every number
above.

One router, one heuristic, one initial layout. Two coupling-map families of
which one produced nothing. And the oracle remains uncounted.

## 8 Consequence for the article

The planned article "What the Operator Hides From the Partitioner" now has
three findings rather than one, and the third is the only one that needed a
measurement:

1. The operator's form says the workload cannot be partitioned. Its standard
   decomposition says otherwise, at a constant eight gates.
2. The ancilla-free synthesis, which nobody uses, is where the operator's form
   tells the truth — so the field's choice of decomposition already answered
   the question.
3. Compilation costs a factor of about two on top of the logical minimum, and
   even then the diffusion is cheaper to cut than a 3-regular graph.

The title still holds. What the operator hides from the partitioner is that the
partitioner's work has already been done.
