# Gap-claim re-check, run 1: VOID

**Date:** 7 November 2026.
**Governed by:** `designs/design_gap_claim_recheck_EN.md`, version 1, registered
earlier the same day, before any searching.

**Outcome: the run is void.** Neither positive control was surfaced by the six
registered queries. Section 4 of the protocol fixed this consequence in advance:

> If the protocol fails to surface both, the run is void and is reported as
> void, not as a null result. A protocol that cannot find two papers known in
> advance to be findable has not tested anything.

**The gap claim in section 11 of the article is therefore neither supported nor
refuted by this run.** It stands exactly as it stood this morning, with a
survey from 18 September behind it and no re-check.

---

## 1 The controls are well formed, so the fault is the instrument's

Both were named in section 4 before searching, with their expected
classifications. Both were verified today against their arXiv records, and both
are real, findable and correctly described:

**arXiv 2307.06009** — "A Linear Algebraic Framework for Dynamic Scheduling Over
Memory-Equipped Quantum Networks", Fittipaldi, Giovanidis and Grosshans
(Sorbonne, CNRS, LIP6). Section IV-D names the stale information problem
directly: a centralised scheduler acts on information already outdated by the
time its decision reaches the nodes. Section IV-D4 introduces a Partially
Informed Quadratic Scheduler that substitutes expected values for the
unavailable quantities. **Expected classification: near miss, at network level.
Confirmed correct.**

**arXiv 2302.00267** — "InQuIR: Intermediate Representation for Interconnected
Quantum Computers", Nishio and Wakizaka. Section VIII states that InQuIR assumes
a statically scheduled program and that dynamic rescheduling may be needed when
a node fails or error rates rise. **Expected classification: near miss, names
the gap rather than filling it. Confirmed correct.**

So the classification rules of section 1 worked on the known cases. What failed
was retrieval.

## 2 Why the queries missed them, which is the useful part

The six queries were built from the vocabulary of the **claim**: partition,
repartition, migration, expiry, staleness, plan. The controls live in the
vocabulary of the **adjacent fields** the claim must be distinguished from:
entanglement distribution, scheduling policy, Lyapunov drift minimisation,
backlog; and intermediate representation, formal semantics, deadlock, static
verification.

**A query set built from a claim cannot see the neighbourhood the claim is
supposed to be distinguished from.** That is a general defect and not a slip in
wording. The gap claim says, in effect, "this is not the same as the adjacent
work" — and testing it requires retrieving the adjacent work, which uses other
words.

A second contributing cause: both controls are from 2023, and general web search
weights recent material heavily. Almost everything returned was from 2024 to
2026.

## 3 What the six queries did return, unclassified

Recorded as candidate material for a repaired protocol, and **deliberately not
classified**. Classifying them under a void run would be a verdict drawn from an
instrument already known to be insensitive.

- Efficient Time-Aware Partitioning of Quantum Circuits for Distributed Quantum
  Computing — arXiv 2603.04126
- Time-Aware Qubit Assignment and Circuit Optimization for Distributed Quantum
  Computing — arXiv 2507.11707
- Dynamic Distribution of Quantum Circuits with Minimum Circuit-Execution Time
- Towards Reproducible Evaluation of Distributed Quantum Circuit Partitioning
  Algorithms — arXiv 2608.27099
- A Modular, Topology-Aware Software Stack for Entanglement-Based Distributed
  Quantum Computing — arXiv 2609.15728
- SQARL: A Size-Agnostic Reinforcement Learning approach for Circuit Allocation
  in Distributed Quantum Architectures — arXiv 2605.27027
- Fidelity-Age-Aware Scheduling in Quantum Repeater Networks — arXiv 2602.09562
- Cisco Outshift, network-aware quantum compiler v2
- Optimizing Compilation for Distributed Quantum Computing via Clustering and
  Annealing — arXiv 2508.15267
- A Modular Quantum Network Architecture for Integrating Network Scheduling with
  Local Program Execution — arXiv 2503.12582

Query 3 returned mostly the declared degenerate subset of section 2 — tape
library partitions, data-pipeline staleness, round-robin time quanta — which is
the one part of the protocol that behaved exactly as written.

## 4 What a version 2 would have to change

Stated here as requirements. It is **not** registered by this document, and no
search is run against it until it is, because section 5 makes rewording a query
after seeing results an invalidating condition. Repairing an instrument inside
the run it failed is how a void result becomes a null one.

1. **Queries from the adjacent vocabulary, not only the claim's.** Entanglement
   scheduling, resource orchestration, intermediate representation, runtime
   replanning, network scheduling under outdated information.
2. **Citation chasing rather than keyword search alone.** Forward and backward
   citations from the two controls and from the time-aware partitioning work,
   which keyword search will not reach.
3. **A date-stratified arm**, so that pre-2024 material is not crowded out by
   recency weighting.
4. **More than two controls, including one expected hit if one can be
   constructed** — all four present controls and the whole run tests only
   sensitivity to near misses, never to hits. If no plausible expected hit can
   be named, that itself is worth recording before searching.

## 5 What this run is worth

It cost six queries and produced no information about the literature. It
produced one thing about the method: a null result from these queries would have
read as support for the gap claim, and it would have been worthless. Section 4
was written this morning and fired this afternoon.

The claim in section 11 of the article remains unverified since 18 September.
Nothing about the article changes today.
