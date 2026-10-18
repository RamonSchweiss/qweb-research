# Addendum 1 to the design note "Periodicity of the routed circuit and the stability of the cut"

**Date:** 18 October 2026.
**Status:** written before the first computation, as the original note requires. The original
note (`design_routed_partition_orbit_EN.md`) is not altered by this addendum; its text stands
as committed. Everything below is additional and dated.

**Why this addendum exists.** The original note left two quantities to Daniel Hug, named them
as open, and said the measurement could not proceed without them: the routing regime of his
scheme (section 7) and the cost of his return swaps (hypothesis H3). He answered both in
correspondence of 18 October 2026, before any computation had been run here. This addendum
records what his answers change, so that the record is fixed before the first result exists.

---

## A1.1 The condition in section 7 has occurred

Section 7 named a router with lookahead as the thing that would invalidate the periodicity
argument. That is the actual situation: Qiskit (SABRE) and TKET, at the compiler levels used
in his study, route the whole circuit and optimise across layer boundaries, including through
barriers. For that regime the map layout → layout is not well defined per layer and the
periodicity argument does not apply.

The consequence prescribed in section 7 is therefore in force, not hypothetical: this
measurement describes **layer-by-layer block routing only**, and that limit is stated in the
first paragraph of the report, not at the end. It is not a limitation discovered afterwards;
it was written down before the answer was known.

## A1.2 Three configurations, not two

The correspondence maps the free orbit onto the freely routed ladder. That mapping is wrong,
and the distinction matters for H3. There are three configurations:

1. **Free routing with lookahead** — the whole circuit in one pass. (His main ladder.)
2. **Block per layer, no return network** — each layer routed from the layout current at that
   point, the exit layout carried forward. (This measurement.)
3. **Block per layer with a return network** — as (2), with the inverse permutation appended
   so that every layer starts from the same layout, forcing d = 1. (His periodicity arm.)

Configurations (2) and (3) differ in exactly one thing: whether the return is paid for.
Configuration (1) is a different regime. H3 compares (2) against (3). It does not compare
anything against (1), and no number from (1) enters it.

## A1.3 The return-swap figures, recorded before the first run

Reported by Daniel Hug, 18 October 2026. Fourteen qubits, a dense portfolio layer of 91 ZZ
terms plus mixer — a complete interaction graph, since C(14,2) = 91 — at the strongest
compiler settings (Qiskit O3, TKET full). Return swaps per layer, Qiskit / TKET:

| Topology | Return swaps per layer |
|---|---|
| Heavy-hex (ibm_kingston map, free placement) | 67 / 28 |
| 4×4 grid, 14 sites | 22 / 22 |
| Chain of 14 | 85 / 61 |

The chain figure approaches the full reversal, n(n−1)/2 = 91.

As an overhead on free routing (p = 3/5/7 pooled, p−1 return networks, two-qubit gates):
heavy-hex +43 % / +37 %, grid +7 % / +19 %, chain +61 % / +63 %. In depth considerably more,
because the return network on the line runs sequentially: chain +148 % to +172 %.

**Provenance and caveat, as given.** SWAP counted as 3 CX, no cancellation across the block
boundary, approximate token swapping. These are therefore conservative upper bounds.

**Comparability.** These figures are at fourteen qubits on a complete interaction graph. The
grid in section 5 of the original note is ten and twelve qubits on twenty-one problem graphs.
The figures establish the magnitude of the return cost; they cannot be subtracted from numbers
produced on a different grid. A1.4 addresses this.

## A1.4 One comparison cell added to the grid

Added, before any computation, so that H3 has one like-for-like comparison:

- n = 14, complete interaction graph (91 ZZ terms plus mixer)
- topologies: heavy-hex, 4×4 grid, line — the three measured above
- five router seeds, as elsewhere
- balanced bipartitions enumerated exhaustively: C(14,7)/2 = 1716, so still exact

The grid of section 5 is otherwise unchanged. This cell is added for comparability with an
existing external measurement, not because a result looked interesting — no result exists yet.
The prohibition in section 6 on adding graphs, topologies or seeds **after the first look at
the numbers** is unaffected and remains in force.

## A1.5 H4, registered before the first run

**H4 — on the line, period two is free.** Conjecture: the exit permutation of a
block-routed complete layer on a line is the reversal. The reversal is an involution, so
applying the block twice returns the initial layout: t = 0 and d = 2, with no return swaps at
all. If so, the free orbit beats the enforced d = 1 on the line by the entire overhead
recorded in A1.3 — +61 % / +63 % in two-qubit gates and +148 % to +172 % in depth.

*Null results, named in advance:* the exit permutation is not an involution; or d > 2; or the
additional crossing gates accumulated over the two layers exceed the return cost after all. Any
of these refutes H4, and the refutation is the result.

*Source.* This conjecture is Daniel Hug's, stated in correspondence of 18 October 2026 and
explicitly not measured by him. It is registered here, before the first computation, so that
its outcome cannot be chosen after the numbers are seen. The topology on which it applies is
the one on which his own scheme is most expensive, which is a reason to be more careful with it
rather than less.

## A1.6 What this addendum does not change

p_max = 64 and the stopping rule of section 6. The controls of section 4, including all-to-all
first as a pipeline check. The statistical floor of section 5, reporting in counts with
within-family numbers. The limits of section 8. The requirement that any further change be a
dated addendum, of which this is the first.

H1, H2 and H3 stand as written. H3 is now answerable, with the comparison defined in A1.2 and
the figures in A1.3.
