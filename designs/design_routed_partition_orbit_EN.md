# Design note: periodicity of the routed circuit and the stability of the cut

**Status:** written before the first computation. Nothing in this note is to be changed
after the first run except in a dated addendum.

**Background.** The measurement "the gate-optimal cut never moves, in twenty-one of
twenty-one graphs" (`gate_vs_state_partition.py`) was computed on the **written**
interaction graph. Daniel Hug asked whether it survives routing. The answer conceded more
than the question asked: what is at risk is not only the identity of the cut but its
justification — in QAOA every layer applies the same gates, and routing destroys exactly
that layer periodicity, because swaps carry the qubit-to-physical mapping into the next
layer. His counter-proposal: force period one by routing each layer as a closed block
that returns to the initial mapping, paying in return swaps. The claim to be tested here:
periodicity re-establishes itself without return swaps, merely with a longer period.

---

## 1 Definitions

**Logical layer.** One QAOA layer: the complete set of ZZ gates of the problem graph plus
the mixer. Identical for every layer.

**Layout m.** A bijection from logical qubits to physical qubits.

**Routing map f.** Given a layout m and the fixed gate list of one layer, a deterministic
router with a fixed seed produces a routed block B(m) and an exit layout f(m).
**Critical assumption:** each layer is routed as a block from the layout current at that
point, with no lookahead across the layer boundary.

**Orbit.** m(0), m(1) = f(m(0)), m(2) = f(m(1)), … The layout space is finite and f maps
a finite set into itself, so there exist a transient t ≥ 0 and a period d ≥ 1 with
m(t+d) = m(t). This is arithmetic, not an empirical finding. What is measured are the
**values** of t and d.

**Routed interaction graph G(k).** A multigraph on the logical qubits, one edge per
two-qubit gate in B(m(k)) — ZZ gates **and** swaps — mapped back to logical labels.

**Gate cut.** The balanced bipartition of the logical qubits that minimises the number of
crossing two-qubit gates in G(k). For n ≤ 12 this is enumerated exhaustively (462
partitions at n = 12), hence exact and free of heuristics.

---

## 2 What is reported

Per triple (problem graph, topology, seed):

1. t and d
2. whether the argmin partition is constant over k = t … t+d−1 — and, separately, over
   the transient k = 0 … t−1
3. cut cost per layer, and the margin (best against second best) per layer
4. swap count per block
5. the number of **additional** crossing gates contributed by swaps alone

Pooled and within graph families, always in the same printout (Simpson check).

---

## 3 Hypotheses, with their null results named in advance

**H1 — the period is usefully small.** Expectation: d ≤ 4 for the topologies tested.
*Null result:* d is large, or no cycle is found within p_max. Then the periodicity is true
and useless, and that is precisely the finding.

**H2 — the gate-optimal cut is constant over the cycle.**
*Null result:* it moves. Then the twenty-one of twenty-one does not transfer to the routed
circuit, and that belongs in the body text of the article, not in a footnote. This null
result is the more interesting outcome, not the worse one.

**H3 — the free orbit is cheaper than enforced period one.** Expectation: the additional
crossing gates accumulated over d layers are fewer than the return-swap cost that Daniel's
scheme pays per layer.
*Null result:* enforcing is cheaper. Then his scheme is the right one and the free orbit
remains only a cheaper diagnostic. The return-swap figure has to come from him; until it
does, H3 is left open rather than answered.

---

## 4 Controls

**All-to-all as a pipeline check.** On complete coupling no swaps are inserted. Then t = 0
and d = 1 *must* come out, and the cut must equal the unrouted gate cut. If it does not,
the pipeline is broken and no result is valid. This control runs first.

**Seed control.** At least five router seeds per triple. If t, d or the constancy of the
cut depend on the seed, the result is a statement about the router and not about the
circuit. Reported per seed, not averaged.

**Permutation control.** The same computation with a sequence of **random** permutations
of equal length in place of the router. If the cut is constant there too, constancy says
nothing about routing.

**Transient kept apart from the cycle.** Cuts from the transient must not enter the cycle
statistics. The transient is the analogue of the dead layers in the Trotter measurement
and needs the same treatment: reported, not mixed in.

---

## 5 Statistical floor

For a fixed triple this is a **deterministic computation**, not a sample: t and d carry no
confidence intervals. The variation lives across graphs, topologies and seeds. Reporting is
therefore in counts ("k of N graphs"), and every statement spanning graph families carries
the within-family counts with it.

Minimum grid: **21 problem graphs** (the same ones as before, so the numbers stay
comparable) × **4 topologies** × **5 seeds**.

Topologies: heavy-hex, square grid, line, all-to-all (control). The line is the adversarial
case — the reversal permutation costs most there — and belongs in for exactly that reason.

---

## 6 Stopping rule

p_max = **64 layers** per run. If no cycle has appeared by then, "no cycle within 64" is
recorded and the run stops. p_max is **not** raised in order to find one.

The measurement is finished when the grid in section 5 is complete — not when a result
looks interesting. No further graphs, topologies or seeds are added after the first look at
the numbers.

---

## 7 What would invalidate the measurement

**A router with lookahead.** If the router routes the whole circuit in one pass it sees
across layer boundaries; then f is not a function of the layout alone and the periodicity
argument does not apply. The measurement would then describe only the regime of
layer-by-layer block routing, and that limit belongs in the first paragraph of the report,
not at the end.

**Stochastic routing.** Qiskit's SabreSwap is randomised. Fixing the seed makes it
deterministic for this purpose, but the result is then conditional on the seed — hence the
seed control, and hence no single seed is ever quoted.

---

## 8 What the measurement does not measure

Nothing about the quantum state. Nothing about calibration, drift or fidelity. Nothing
about machines of a useful size. It is a purely structural computation on routed gate
lists, at ten and twelve qubits, two processors, balanced bipartitions — the same limits as
the previous round, so that the numbers stay comparable.

In particular this is **not** part of the drift programme. It needs no hardware and can run
independently of it.

---

## 9 Deliverable

One script, `routed_partition_orbit.py`, beside `gate_vs_state_partition.py` in the
repository. One printout: a table per triple, with the pooled and the within-family summary
beneath it. If the printout contradicts a later text, the text is wrong.
