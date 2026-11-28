# Design note: what the degree-sequence rule assumes about the network

**Date:** 28 November 2026.
**Status:** registered before the measurement it governs. Version 1.

**The question.** `design_hypercube_global_qubits_EN.md` proved that for a state
vector distributed over nodes, with the node address as the global bit pattern,
the cost of a set *S* of global qubits is

    cost(S) = Σ over v in S of deg(v) + 2·|S|

in units of 2^(n−2) amplitude hops, with in-degree for the oriented CNOT
family — and that because this objective is linear and separable, the
lowest-degree rule is not a heuristic but **exactly optimal**. That was
verified on 378 cells and against 397,152 subsets with zero deviations.

Every word of it rests on one cost model: a hypercube interconnect in which an
amplitude crossing a node boundary costs one hop, independent of which boundary.
**No real machine is built that way.** This note registers what happens to the
result when the cost model is replaced by models that resemble machines that
exist.

**Why it matters now.** The published state of the art in this family is a
50-qubit state-vector simulation on 4096 nodes and 16,384 GH200 superchips of
the JUPITER Booster. That work reports a case study in which swapping two
registers of an adder cut the runtime from 1996 to 1193 seconds, attributed
solely to reduced communication, and states that a systematic method for
choosing the relabelling is beyond its scope and planned for future
investigation. The closed form above is a candidate for that method. Whether it
survives the network of such a machine is the question here, and it is not
answered by the proof, because the proof is about a different network.

---

## 1 What is already proved, and is therefore not re-derived

- the closed form and its exact optimality **under the hypercube hop model**;
- the hop measurements the model rests on: a diagonal gate is free, a
  single-qubit rotation on a global qubit costs 2, a CNOT costs 1 with a global
  target and nothing with only a global control, an XX+YY exchange costs 1 with
  one global qubit and 2 with both;
- that the detour at multi-global exchange gates repays exactly the overlap a
  naive argument hopes to save, which is what makes the objective separable;
- that the optimum is degenerate for the XY family and not for the oriented
  CNOT family.

None of that is in question. What is in question is its reach.

## 2 Declared cost models

Four, all fixed here, before any run. Each takes a circuit and a set *S* of
global qubits and returns a cost. **No weight in any of them is fitted to data
at any point** — see section 6.

**M1, the reference.** The hypercube hop model of the earlier note, unchanged,
so that every later figure has something to be compared against.

**M2, uniform bandwidth.** On a network with near-uniform bisection bandwidth —
a fat tree, or a dragonfly with its groups busy — a pairwise exchange along one
logical hypercube dimension moves the same volume whichever dimension it is.
Distance drops out and volume is all that remains:

    cost_M2(S) = Σ over v in S of deg(v)

The `+ 2·|S|` term of M1 is a distance artefact and disappears. **The objective
stays separable**, so the rule should stay exactly optimal while the formula
changes. That is a prediction, and section 4 registers it as one.

**M3, two tiers.** A real node holds several accelerators. An exchange between
accelerators inside a node crosses a fast link; an exchange between nodes
crosses the network. The global qubits therefore split into a cheap class and
an expensive one, by index:

    cost_M3(S) = Σ over v in S of w(v)·deg(v),  w(v) ∈ {w_intra, w_inter}

with the lowest *k* global indices intra-node. **Declared, not fitted:**
k = 2 (four accelerators per node, as on the machine quoted above),
w_intra = 1, and w_inter ∈ {4, 10, 25} as a declared grid spanning plausible
bandwidth ratios. A weighted objective is still separable, so the rule should
generalise to *lowest weighted degree* — which would be a stronger result than
the original, not a weaker one.

**M4, the separability breaker.** M1 to M3 all assign a cost per qubit. A real
implementation need not: if an exchange that touches two global qubits at once
can be fused when both are intra-node and not otherwise, the cost carries a term
in *pairs*:

    cost_M4(S) = cost_M3(S) − λ · (number of two-global gates whose both
                 qubits lie in the intra-node class)

with λ ∈ {0.25, 0.5} declared. **This model is deliberately constructed to
break the premise of the proof.** It is registered because a model that can only
confirm the result is not a test of it.

## 3 Ground truth, and the unit

**Enumeration only.** For each circuit and each (n, g) the cost of **every**
subset of size g is computed under every model, and the optimum is the minimum
over that enumeration. No heuristic result is ever used as the optimum. The
enumeration ceiling is checked in section 7 before the run.

**The unit** is one communicating gate: the granularity of every quantity below
is g = 1 and is declared here rather than estimated from a sample. A loss of
less than one communicating gate is not a loss anyone can pay.

## 4 Registered hypotheses

**H1 — separability survives tiering.** Under M3, at every size, every g and
every w_inter in the declared grid, the set chosen by the lowest-weighted-degree
rule is cost-optimal in **every** cell. Registered as an exact claim and not as
a tendency: a single counterexample refutes it.

**H2 — the ranking survives the loss of the distance term.** Under M2 the set
chosen by the plain lowest-degree rule is cost-optimal in every cell. This is
expected to follow from separability, and is registered separately so that an
implementation error in M2 cannot hide inside H1.

**H3 — M4 breaks it, and by a measurable amount.** Under M4 the
lowest-weighted-degree rule is **not** cost-optimal in at least one cell at
every size, and the median loss over the cells where it fails is at least one
communicating gate. Registered in this direction deliberately: M4 was built to
break the rule, so finding that it does not break it would be the more
interesting result, and that outcome must be reportable as such rather than
appearing as a failed hypothesis.

**H4 — the rule's advantage over a random choice grows with g under every
model.** Taken over from the earlier study, where the corresponding hypothesis
was mis-specified: it was registered there as a check on the cost model, and the
cost model already predicted the growth. Here it is registered as what it is —
a statement about the spread between a good and an arbitrary choice — with no
conclusion about any model attached to it.

## 5 The degree sequence can be ambiguous, and that is handled first

Addendum 5 of `design_cut_degeneracy_EN.md` of 27 November recorded an
instrument defect of exactly this shape: a rule whose starting object was not a
property of the problem. The incumbent there came from a Fiedler vector, and
relabelling the vertices changed it on 11 of 126 graphs.

**The same failure is available here.** Ties in the degree sequence make the
lowest-degree set non-unique, and nothing in the closed form says which tied
member to take. It is removed before any run, not afterwards:

**Rule D.** Let *T* be the set of subsets of size g attaining the minimum
(weighted) degree sum. If |*T*| = 1 the rule's choice is that set. If |*T*| > 1,
take the members of *T* of minimum cost under the model being evaluated; if that
is still not unique, the cell is **ambiguous** — excluded, counted, and reported
with its reason. Ambiguity is reported and never resolved by a choice.

**The invariance gate.** For every cell entering the measurement, twenty
relabellings of the circuit's qubits are drawn from a declared seed, the rule is
re-applied, and the chosen set is mapped back. If any relabelling yields a
different set, **the run is void**, not merely different — the same standing the
balance assertion has in the earlier notes. A relabelling under which rule D
reports ambiguity marks the cell ambiguous and the run continues; that line is
drawn here, in advance, as addendum 1 of the migration-cost note drew it.

If more than one cell in five is ambiguous at any size, that size is reported
**not evaluable** rather than measured on what survives.

## 6 Invalidating conditions

- **A weight fitted to the data.** Every weight in M3 and M4 is declared in
  section 2 or taken from a published machine specification, and none is chosen,
  tuned or narrowed after any cost has been computed. This is the condition most
  easily violated by good intentions, and a run in which it happens is void.
- **A cost model added after the run.** The four of section 2 are the four. A
  fifth model is a new note.
- **A heuristic optimum used as ground truth.** Enumeration only.
- **A relabelling that changes the rule's choice.** Section 5.
- **A figure that exists only as a literal.** Every run commits its store and
  its printout beside its code, in the same commit.

## 7 Result-independent stopping condition

- **register sizes** n = 16, 20, 24;
- **global qubit counts** g = 4, 8, 12 — spanning 16, 256 and 4096 nodes, the
  last being the node count of the published 50-qubit run;
- **circuit families**, five, declared: a QFT, a ripple-carry **adder** (the
  circuit of the published case study, included deliberately), a QAOA layer on
  a random 3-regular graph, a hardware-efficient layered ansatz, and a random
  circuit at depth 8;
- **seeds** 0 to 9 where a family is random, one instance otherwise;
- **enumeration check before the run:** the largest cell is C(24,12) = 2,704,156
  subsets; the whole grid is below 10^8 subset evaluations and runs in minutes.
  If any cell exceeds 10^7 subsets the cell is enumerated in blocks, never
  sampled.

No size, g, family or seed is added afterwards to settle a borderline case.

## 8 What this cannot show

**It is not a measurement on a machine.** Every figure here is a figure about a
model. A model that counts communicating gates ignores contention, ignores the
overlap of communication with computation that a real implementation uses, and
ignores the byte-level state encodings that make large registers fit at all.
What it can establish is whether the *structure* of the result — separability,
and with it the exact optimality of a degree rule — survives the step from a
hypercube to something shaped like a real network. That is a question about
mathematics, and it can be settled here. Whether the rule saves wall-clock time
on 4096 nodes cannot, and this note does not claim it.

**One topology family per model, and no routing.** No failure modes, no jitter,
no sharing of the machine with other jobs.

**And the obvious limit:** if H1 and H2 hold and H3 fails, the honest reading is
not that the rule works on real machines. It is that no model examined here was
able to break it — which is weaker, and is what will be written.
