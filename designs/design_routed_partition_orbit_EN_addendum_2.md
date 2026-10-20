# Addendum 2 to the design note "Periodicity of the routed circuit and the stability of the cut"

**Date:** 20 October 2026.
**Status:** written after the first run and before any run of the replacement
control described here. The original note
(`design_routed_partition_orbit_EN.md`) and Addendum 1 are not altered; their
text stands as committed. Everything below is additional and dated.

**What this addendum does.** It records that the permutation control of section 4
came out degenerate, states why, and registers a replacement control together
with its decision rule and its null result. It does not revise any result of the
run of 20 October 2026, and it does not touch H1, H2, H3 or H4.

---

## A2.1 What happened

Section 4 registered a permutation control: "the same computation with a
sequence of random permutations of equal length in place of the router. If the
cut is constant there too, constancy says nothing about routing."

Run as written, on 21 problem graphs × 3 non-trivial topologies × 5 seeds, a
cycle was found in **0 of 105 runs on each topology**. Under random
permutations the orbit does not close within p_max = 64 at all.

The reason is arithmetic, not experimental. The layout space at ten qubits holds
10! ≈ 3.6 × 10⁶ elements, and a random walk on it repeats a visited layout
within 64 steps with probability of order 64²/(2 × 10!) ≈ 6 × 10⁻⁴. A control
built on cycle-constancy therefore cannot produce a cycle to be constant over,
and the comparison it was registered to make does not exist.

**Why this is not a result-dependent change.** The control failed mechanically:
it produced no cycles, and therefore no comparison of any kind, in either
direction. That fact is visible from the cycle counts alone, without reference
to H1, H2, H3 or H4 and without reference to which way any of them came out. The
replacement below is registered for that reason and for no other.

**What the degenerate control nevertheless shows.** Periodicity at these sizes
is a property of the router, not of permutation sequences in general. That is
worth reporting, and it is reported, but it is not the question section 4 asked.

## A2.2 The replacement control, registered here

**Matched-window constancy.** For every triple (problem graph, topology, router
seed) whose real run found a cycle of length d ≥ 2 with transient t:

1. Take the window length W = d and the transient t from that real run.
2. Run the permutation process from the identity layout for t + W layers,
   copying the **per-layer swap count** of the real run layer by layer, and
   choosing each swap uniformly at random among qubit pairs instead of by the
   router.
3. Ask whether the argmin balanced bipartition is constant over the last W
   layers — the same question, over a window of the same length, with the same
   number of swaps.
4. Five control seeds per triple, reported per seed and never averaged away.

The comparison is then between two rates measured on the same set of runs: how
often the router's cut is constant over its cycle, and how often a random arm
with the same swap budget is constant over a window of the same length.

Where the real run found no cycle within p_max there is no window to match, and
the control is reported as not applicable for that triple rather than given a
substitute window.

## A2.3 Decision rule, fixed before the run

Let *r* be the router's constancy rate over cycles with d ≥ 2, and *c* the
control's constancy rate over matched windows, both pooled and per topology.

- If *c* is within the seed-to-seed scatter of *r*, then constancy carries no
  information about routing, and every statement in the report that rests on the
  cut being constant has to be withdrawn. This is the null result, and it is the
  outcome that would cost the most.
- If *c* is clearly below *r*, constancy is a property of what the router does
  and the statements stand.
- Intermediate outcomes are reported as intermediate. No threshold is chosen
  after the numbers are seen, and the pooled and per-topology rates are always
  printed together.

## A2.4 What is not changed

p_max = 64 and the stopping rule of section 6. The all-to-all pipeline check and
the seed control of section 4. The statistical floor of section 5 and the
comparison cell of Addendum 1. The limits of section 8. H1, H2 and H3 as
written, and H4 as registered in Addendum 1.

The results of the run of 20 October 2026 stand as measured. In the report they
are published with the permutation control marked as unavailable for that run,
and the replacement control is reported separately once it has been run.
