# Addendum 2 to design_hypercube_global_qubits_EN.md

**23 November 2026, before the study's first measurement run.** The note and
addendum 1 are left standing unedited.

Addendum 1 corrected the cost model and left one quantity unmeasured: how far
the traffic travels. Measuring it completed the model, and the completed model
turns out to answer the study's question analytically. This addendum reports
that, and reduces the registered run from a comparison to a verification plus
one measurement that remains worth making.

Evidence committed with this addendum, in `designs/`:
`hypercube_cost_probe.py` and `hypercube_cost_probe_output.txt` (extended with
hop distances), `hypercube_closed_form.py` and
`hypercube_closed_form_output.txt`.

---

## A2.1 Detours exist after all, and here is where

§1 of the note dismissed the detour question: in a hypercube every exchange
crosses exactly one edge, so there is nothing to detour around. That was
careless. It is true of a gate with one global qubit. It is false of a gate
with two.

The probe now reports, for each gate, the Hamming distance between the node
addresses that exchange — the number of hypercube edges the traffic crosses:

| gate and placement | one way | pairs | hops | units |
|---|---|---|---|---|
| ZZ(γ), any placement | 0 | 0 | 0 | **0** |
| RX(β) on a global qubit | 32 | 2 | 1 | **2** |
| RX(β) on a local qubit | 0 | 0 | 0 | **0** |
| CNOT, control global, target local | 0 | 0 | 0 | **0** |
| CNOT, control local, target global | 16 | 2 | 1 | **1** |
| CNOT, both global | 16 | 1 | 1 | **1** |
| XX+YY(δ), exactly one global | 16 | 2 | 1 | **1** |
| XX+YY(δ), both global | 16 | 1 | **2** | **2** |
| XX+YY(δ), none global | 0 | 0 | 0 | **0** |

n = 6, g = 2, so the unit 2^(n−2) = 16. "Units" is one-way traffic times hops.

An exchange-type gate with **both** qubits global moves amplitudes between two
nodes whose addresses differ in two bits. That is two hypercube edges, and it
is a detour in the only sense this architecture has one. A controlled gate with
both qubits global stays at one hop, because CNOT flips only the target bit and
leaves the control's address bit alone.

So the question the note dismissed has an answer: **detours occur exactly at
non-diagonal exchange gates with more than one global qubit, and they are hops
across hypercube dimensions rather than paths through a graph.**

## A2.2 The cost unit, restated

The note declared the unit as "a count of gates" with a granularity of one
gate. With the model complete, gates do not cost equally, so that unit no
longer names a quantity. The unit is now **amplitude-hops in units of
2^(n−2)**, that is one-way traffic times hop distance, as in the table above.
Granularity remains 1, and the resolution limit of §7 reads as **2 units**
rather than 2 gates. The limit is not loosened; the quantity it applies to is
named correctly.

## A2.3 The closed form, and why there is one

Writing the cost down per gate makes something visible that neither the note
nor addendum 1 saw.

For the XX+YY family the cost of a global set S is, summing the table over the
edges of the graph and adding the mixer,

    cost(S) = Σ over edges (a,b) of [ 1 if one endpoint in S, 2 if both ]
              + 2·|S|

and the bracket is simply |{a, b} ∩ S|. Summing that over all edges counts each
chosen qubit once per incident edge:

    **cost(S) = Σ over v in S of deg(v) + 2·|S|**

**The detour exactly pays for the overlap.** An undirected edge-counting model
would have said that two global qubits sharing an edge save that edge; the
second hop costs precisely that saving back. The two cancel, the objective
becomes linear and separable in the chosen qubits, and the greedy rule — take
the g qubits of lowest degree — is exactly optimal. There is nothing to search.

For the oriented CNOT family the same argument gives Σ in-degree over S, with
in-degree counted under the orientation declared in addendum 1.

**Verified rather than asserted.** `hypercube_closed_form.py` enumerates every
subset of every registered cell on the published instance set — seven families,
three seeds, density 1.5, n ∈ {12, 16, 20}, g ∈ {2, 3, 4}, both families:

- 378 cells,
- **397,152 subsets** checked against the identity,
- **0** subsets where cost(S) − 2|S| ≠ Σ deg(v),
- **0** cells where the lowest-degree rule failed to attain the enumerated
  optimum,
- worst miss: 0 units.

## A2.4 What this does to the registered hypotheses

**H1 and H3 are no longer hypotheses.** H3 said the gate-structure arm reaches
the optimum in a majority of instances; it reaches it in all of them, by a
proof, and the enumeration confirms the proof rather than testing the arm. H1
said the mutual-information arm does not beat the gate-structure arm; nothing
can beat an optimum. Reporting either as "confirmed" would be reporting a
theorem as a measurement, and the write-up will not do that. The expectation
recorded in §8 — that H3 might come out close to tautological — was right, and
for a sharper reason than the one given there.

**H2 remains a real check.** The random arm must be separated from the optimum
and sit above it. If it is not, the pipeline is not measuring what it claims
to, whatever the proof says.

**H4 is settled by the operator.** The crossing structure is a property of the
gate matrix and carries no reference to the state. It is still computed on the
study's circuits, as the note requires.

**H5 is answerable in closed form.** The optimum is the sum of the g smallest
degrees, so it grows with g, monotonically and at a rate the degree sequence
fixes. The measurement reports the rate rather than testing for one.

## A2.5 What is left to measure, and it is the point

One number, and it is the one that answers the question the study was built
around.

The mutual-information arm selects by information, not by degree. The optimum
is attained by degree alone. So the question is no longer *whether* the state
can beat the circuit structure — it provably cannot — but **whether the state
leads you to the same place, and what it costs when it does not.**

The run therefore reports, paired per instance: the share of instances on which
the information arm picks a lowest-degree set, and the units it loses when it
does not, with the resolution rule of §7 applied to that paired difference.

That is the 1986 question with an answer rather than a restatement. The same
mutual information predicts the circuit graph at a Spearman correlation of
about +0.83 in the partitioning line. Here it is given a decision for which the
circuit's degree sequence is sufficient, and the measurement is of how far a
good quantity leads you astray when it is the wrong quantity for the question.

## A2.6 The limit of the result, stated here so the article cannot overreach

This holds for the **amplitude-distributed** execution model: one state vector
spread over 2^g nodes, node address equal to the global bit string. It does not
transfer to the distributed model the QWeb architecture thesis is about, where
qubits live on separate machines and a remote gate is paid for in entanglement.
There the interaction graph is the right object and the state has plenty to
say — which is what the partitioning line measures.

Two execution models, the same words "local" and "global", opposite answers to
whether the state informs the decision. That contrast is the finding, and it is
larger than either half.

## A2.7 Budget and provenance

The stopping condition of §10 is unchanged: the same 21 graphs, sizes and
values of g, 189 instances per family. No instance, size or family is added.
What changes is what the run reports, not how much of it there is.

Two addenda on the day of registration, both before any measurement. The note
is not edited, both addenda are dated, and the two probes that produced them
are committed with them. The study still has no measured result.
