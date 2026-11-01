# Design note: what a balanced cut costs an amplification iteration

**Status:** PROPOSED, version 2, 1 November 2026. **Not in force.** Version 1
was written earlier the same day and its central hypothesis was refuted before
the note was committed; section 2 records it. The note comes into force when it
has been agreed and committed, which must happen before the measurement in
section 6 is run. Once committed, nothing in it changes except in a dated
addendum.

**What changed in version 2.** The theoretical objective is inverted. Version 1
held that routing an amplification iteration makes every iteration cross every
balanced cut at a cost that does not fall as the partitioner improves. That is
false for the decomposition the note itself declared, and the arithmetic in
section 3 shows why. What remains to be measured is a routing question rather
than a structural one. The invalidating condition in section 8 has also been
corrected: version 1 carried over a condition about router lookahead from the
orbit design note, which does not apply to a single block, and replaces it with
the condition that does.

**Form.** A theoretical objective with an experimental objective under it,
carrying the three fields agreed with Venkateswaran Ramamurthy on 30 October: a
declared degenerate subset, a declared invalidating condition, and a stopping
condition evaluable without knowing the result.

---

## 1 Why the note exists at all

The diffusion operator of amplitude amplification is

    D = 2|s><s| - I,     |s> = H^n |0>

a reflection about a state in which every qubit participates. Read as an
operator it has no proper subset of the register it leaves alone, which makes
it the natural candidate for the workload that cannot be partitioned: in a
machine of several modules, every iteration would cross every cut.

That reading is what this note set out to measure. It is wrong, and the reason
it is wrong is worth more than the hypothesis was.

## 2 The hypothesis that was refuted

Recorded verbatim from version 1, written by Ramon Schweiss on 1 November 2026
and refuted the same day, before this note was in force:

> In a machine of several modules, routing one amplification iteration as a
> block makes every iteration cross every balanced cut, and the cost of the
> crossing does not fall as the partitioner improves. Amplitude amplification
> would then be the limiting case of circuit partitioning — the workload for
> which splitting is most expensive, and expensive for a structural reason
> rather than a contingent one.

It is left standing here rather than deleted. A design note that quietly
replaces its own hypothesis is a design note nobody can check.

## 3 What refuted it: arithmetic, not a measurement

This section is deterministic computation on a declared circuit. There are no
seeds, no selection, and no stopping rule, so it needed no registration — the
same standing as the periodicity argument in the orbit design note. It was
computed on 1 November 2026 and the script is named in section 10.

**The circuit.** The multi-controlled Z is built as an explicit V-chain of
Toffoli gates over n-2 ancillae, each Toffoli written out as its standard
six-CX form. A diffusion over n data qubits therefore occupies P = 2n-2
physical qubits and carries 12(n-2)+1 two-qubit gates. The construction was
verified against its definition: the circuit equals 2|s><s| - I to within
1e-16, up to a global phase of -1, with ancilla leakage below 1e-16.

**The interaction graph is not complete, and its cut is constant.** Minimum cut
is over balanced bipartitions of the P physical qubits, exhaustively
enumerated.

      n    P   2q gates   distinct pairs   min balanced cut   crossing fraction
      4    6         25         7 / 15                    8               0.320
      6   10         49        13 / 45                    8               0.163
      8   14         73        19 / 91                    8               0.110
     10   18         97        25 / 153                   8               0.082
     12   22        121        31 / 231                   8               0.066

The cut is eight gates at every size tested. The V-chain is a ladder; cutting
it in the middle severs one triangle, and that is the whole cost. The crossing
fraction therefore falls as 1/n, where a complete interaction graph would hold
near P/(2(P-1)), that is near 0.53 at these sizes.

**The operator was read instead of the circuit.** The hypothesis is a statement
about D. The routed cost is a property of a decomposition of D, and every
decomposition in use is a chain. The chain does the partitioner's work before
the partitioner is asked.

## 4 The same operator without ancillae, where the hypothesis holds

The multi-controlled Z synthesised with no ancillae, on n qubits, same
operator:

      n    P   2q gates   distinct pairs   min balanced cut   crossing fraction
      4    4         14         6 / 6                     8               0.571
      6    6         82        15 / 15                   48               0.585
      8    8        170        28 / 28                   96               0.565
     10   10        290        45 / 45                  160               0.552
     12   12        442        66 / 66                  240               0.543

Here the interaction graph **is** complete at every size, and the crossing
fraction sits on the complete-graph floor. Version 1's hypothesis is correct
for this decomposition and false for the one in use.

Gate count is the reason nobody uses it: roughly 3n^2 against the V-chain's
12n, a factor of 3.7 at n = 12 and growing. It is not exponential; an earlier
guess that it would be was wrong and is corrected here.

**The exchange rate.** At n = 12, ten ancillae turn 240 crossings into eight:
about 23 crossings saved per ancilla. The ancillae are spent to reduce gate
count, and they buy the cheap cut as a side effect. The field's choice of
decomposition already encodes the answer to the question version 1 asked.

## 5 The ledger entry this produces

A nonlocal CX costs one ebit and two classical bits. With the V-chain, a
distributed amplification iteration costs **eight ebits**, independent of
register size, and a full run costs eight times the iteration count:

       n              N   iterations   ebits per run
      16         65,536          201           1,608
      20      1,048,576          804           6,432
      30  1,073,741,824       25,735         205,880

Bounded, computable before the run, and growing with the algorithm's own
iteration count rather than with the register. The oracle is not counted; see
section 9.

## 6 The theoretical objective, as it now stands

Eight crossings per iteration is the *logical* minimum under free placement. A
router that does not know where the module boundary lies has to realise it.

**The objective: a cut-oblivious router on a realistic coupling map achieves a
crossing fraction close to the logical minimum, because the chain structure is
local enough that minimising total swaps also keeps the traffic off the cut.**

This is a routing claim, it could fail, and failing would be the more
interesting outcome: it would mean the cheap cut exists in the circuit and is
squandered in compilation, which is a statement about the stack rather than
about the algorithm.

## 7 The experimental objective

Compile the declared diffusion onto two coupling maps over a range of register
sizes and measure the crossing fraction of the routed circuit against the
logical minimum of eight.

**Declared topologies.** A heavy-hex subgraph and a square-grid subgraph,
generated by the rule already used in `routed_partition_orbit.py`, including its
choice of BFS start node maximising induced edges.

**Declared sizes.** n from 4 to 11, so P from 6 to 20. Balanced bipartitions are
enumerated exhaustively throughout, which is feasible at P = 20 and removes
sampling noise; version 1 declared sampling above P = 16 and no longer needs it.

**Declared router.** SABRE with the decay heuristic and a trivial initial
layout, R seeds per condition with R fixed before the run, median reported and
spread retained.

**The measured quantity.** The minimum, over balanced bipartitions of the
physical qubits, of the number of routed two-qubit gates acting on one qubit in
each half, divided by the total number of routed two-qubit gates. Inserted
swaps count: a swap carrying a pair across the cut is exactly the cost in
question.

**The contrast.** The same measurement on one QAOA layer over the `community`
and `regular` families of `partition_topology` at 1.5 edges per qubit. The
community family is built to split cleanly, which makes it the most favourable
case for a partitioner and therefore the strictest contrast available.

## 8 Declared invalidating condition

**A cut-aware router.** SABRE minimises total swaps, not swaps across a
declared boundary. A router told where the cut lies could trade total swaps for
fewer crossings. This measurement therefore describes a cut-oblivious router,
and it establishes no bound on what cut-aware routing could achieve. Quoting
the result as "the cost of partitioning" without that qualifier would be
describing the router and calling it the algorithm.

**A decomposition other than the declared one.** If the multi-controlled Z is
handed to the transpiler to synthesise, the measurement describes the
transpiler's synthesis policy rather than the declared circuit. Section 3 fixes
the decomposition, and a run departing from it is void rather than merely
different. Section 4 is the one permitted departure and is reported separately.

## 9 Declared degenerate subset, and the uncounted term

**Sizes with no interior.** Where the diameter of the P-node subgraph is
comparable to P itself, every circuit crosses every balanced cut whatever its
interaction graph, and the crossing fraction says nothing about the operator.
These sizes are reported and excluded from any trend.

**Subgraphs that are trees.** A heavy-hex ball around a corner node induces a
tree, in which every edge is a cut edge. The start-node rule is meant to avoid
this; any case where it occurs anyway is reported separately.

**The oracle, which is not counted.** The oracle is assumed, as the
amplification literature assumes it. If its own interaction graph were dense
and dominated the iteration, the diffusion's crossing fraction would be a
correct measurement of a minor term. This is a scope limit and not an
approximation, and it is the same uncounted layer as the encoding stage in "The
Layer That Nobody Trains".

## 10 Stopping condition, evaluable without the result

At each size and on each topology, let r be the routed crossing fraction's
median over seeds, m the logical minimum fraction (eight divided by the routed
gate count), and s the seed spread. **The objective in section 6 is retained at
that size only if r - m < max(s, 0.05).** Where it is not, the objective is
withdrawn at that size and the withdrawal reported with the numbers.

This compares a median against a quantity computed from the circuit alone,
against a within-condition spread, size by size. It needs no fitted trend and
no knowledge of which way anything moves.

The threshold of 0.05 is declared here and is not a power calculation. It is the
fraction below which a crossing cost would be a rounding error against the
eight-ebit ledger entry of section 5, and if it is wrong the argument against it
should be about that ledger.

## 11 The stopping decision

- **Retained everywhere:** the cheap cut survives compilation. Amplitude
  amplification distributes at eight ebits per iteration on real coupling maps,
  and section 5 is an engineering number rather than a bound.
- **Retained on one topology, withdrawn on the other:** the result is a
  statement about that topology, named. This is what the orbit measurement
  produced, and it is a result rather than a failure.
- **Withdrawn widely:** the cheap cut exists in the circuit and is lost in
  routing. That is a finding about the compiler, it is more interesting than the
  alternative, and it is published as such.

No threshold is adjusted after the run. An outcome close to one is reported as
close to it and treated as a withdrawal.

## 12 What none of this establishes

Nothing about distributing the search *problem*. Qiu et al. (*Theoretical
Computer Science*, 2024) and its exact and generalised successors decompose the
oracle function into subfunctions on fewer input bits and run a smaller instance
on each. That partitions the problem rather than the register and needs no
quantum link at all. Whether their total query count over all subfunctions
preserves the quadratic advantage is a separate question, not settled here, and
their published comparison is per subfunction.

Nothing about whether amplitude amplification is worth distributing. Nothing
about any particular machine: the coupling maps are generated families, not
devices. And nothing about the oracle.

## 13 Deliverable

Two scripts in `calculations/`. The first carries section 3 and section 4 —
the circuit, its verification against 2|s><s| - I, and the two interaction
graphs with their cuts — and is deterministic. The second carries section 7,
imports `partition_topology` rather than reimplementing it so that the contrast
graphs are identical to those already published, and prints the declared
decomposition, the seed count, the degenerate sizes with their reason, the
crossing fractions with their spreads, the stopping condition evaluated size by
size, and the decision that follows.

Published whichever way it comes out. If the measurement contradicts a later
text, the text is wrong.
