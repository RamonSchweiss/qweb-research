# Design note: which qubits should be global, and whether the state has a say

**Registered 23 November 2026, before the first computation.**
Ramon Schweiss, QWeb © Research. No measurement has been run against this
question. Any change made after the first run is a dated addendum; this text
is not edited.

---

## 1 The question behind the question, and whose it is

This one is mine, and it is old. The 1986 diploma thesis *Local and Global
Information in Distributed Systems* weighted the edges of a processor network
by read and write access frequency and used Kruskal's algorithm to partition
it. The weights were a statement about the workload; the partition was the
design decision they informed.

The quantum version of that network has been treated twice in QWeb, and the two
treatments have never been put against each other.

**The chosen topology.** "What a Node Actually Holds" distributes the amplitude
vector over a hypercube: the node address *is* the global bit string, each node
holds 2^(n−g) amplitudes, and a gate on a global qubit pairs amplitudes whose
global index differs in exactly one bit. The communication topology is not
selected — it follows from the indexing. `calculations/node_slices.py` and
`calculations/hypercube_vs_mps.py` are the arithmetic.

**The found topology.** Thread 2 of the QWeb architecture thesis weights an
interaction graph by entanglement entropy across a cut, and the partition is
read off the weights. `calculations/partition_information.py` and
`calculations/gate_vs_state_partition.py` are that line, carried out jointly
with V. Ramamurthy.

The open architectural question has been stated for months as: *does the
natural entanglement structure of a computation fit a hypercube, or does a
mismatch create detours?* Writing this note made it clear that the question as
posed cannot be answered, because it assumes a geometry the architecture does
not have. In a hypercube of this kind every exchange crosses exactly one edge.
There are no detours. There is one design decision, and it is which qubits are
global.

## 2 The question, as it can actually be asked

Given a structured circuit on n qubits, executed on 2^g hypercube nodes, does
choosing the global qubit set from the **state's** mutual information reduce
communication below choosing it from the **circuit's** gate structure alone —
within a declared resolution?

That is the 1986 question in its quantum form, and the two words in its title
are literal here rather than figurative: a qubit is local or global, and the
choice is the whole of the design freedom.

**Out of scope, named here so that it is not quietly imported later.** Whether
the hypercube is the right machine for a given state at all: that is the
crossover against a tensor-network representation at S ≈ 1.4, already measured
in `hypercube_vs_mps.py`, and it is a different question with a different
answer. Also out of scope: reassigning the global set during a run, noise, and
the compilation of individual gates.

## 3 The structural claim this study exists to test

The cost of one gate on a global qubit is 2^(n−1) amplitudes moved. That figure
depends on the length of the amplitude list and on nothing else — not on the
state, not on its entanglement, not on which global qubit it is.

If that holds, then the state cannot inform this decision. The cost of a global
set is a **count of gates touching it**, the problem is purely combinatorial,
and mutual information is entitled to no advantage over the gate structure that
produces it.

That is a prediction with a mechanism rather than a hypothesis fished from
data, and it is registered as such. It would also supply the *reason* for an
observation already in the repository: in `gate_vs_state_partition.py` the
gate-optimal cut never moved in QAOA, and following the information cut cost
more remote gates. That was measured and not explained.

## 4 Arms

All four select a set of g global qubits. They differ only in what they are
allowed to look at.

1. **Gate-structure arm.** Minimises the number of gates acting on the global
   set, computed from the circuit DAG alone. Compile-time information only.
2. **Mutual-information arm.** Selects by the pairwise mutual information
   I(a:b) = S(a) + S(b) − S(ab) of the state at a declared layer. Run-time
   information.
3. **Random arm.** Uniformly random g-subsets, 20 draws per instance. The
   negative control: a selection rule that is expected to be bad, included so
   that no arm is assumed adequate by construction.
4. **Exhaustive optimum.** All C(n, g) subsets enumerated, true minimum taken.
   This is the ground truth, not an arm, and it is what the other three are
   measured against.

## 5 Instances, sizes, and one subset declared degenerate in advance

**Family A, QAOA**, on the same 21 published graphs that `partition_topology.py`
and `findability.py` already use, so the instance set is shared with the
existing studies and its awkward members are already known.

**Family B, Trotter evolution of a 1D chain**, as the second family. Registered
now so that a result on QAOA alone cannot later be presented as a result about
structured circuits in general.

**Sizes n ∈ {12, 16, 20}. Global bits g ∈ {2, 3, 4}.**

The sizes are spaced by four rather than by two so that H5 has a lever arm to
measure; three sizes two apart are three views of nearly the same machine. The
upper end is set by the instance set and not by compute: all 21 graphs exist up
to n = 24, while from n = 26 the scale-free graph at seed 2 is missing, and
comparing a share over 20 graphs with a share over 21 is the mistake the
findability addendum exists to prevent. At n = 20 the denominator is the same
in every cell.

The values of g hold the ratio g/n inside the range the architecture is
actually described in: "What a Node Actually Holds" scales to 40 qubits on
1024 nodes, so g/n = 0.25. This grid runs from 4/12 = 0.33 to 2/20 = 0.10, with
3/12 and 4/16 sitting on the quoted ratio.

Every cell is exhaustively enumerable — C(20, 4) = 4845 — so the ground truth
is exact everywhere and findability is not at issue in this study. Compute is
not the binding constraint anywhere in this design: the largest state vector is
2^20 amplitudes, and the mutual information depends on the circuit and the size
but not on g, so it is computed once per (graph, size) and reused across the
three values of g.

**The degenerate subset, declared now: g = 1.** With a single global qubit the
cost of a set is exactly that qubit's degree in the circuit graph, the optimum
is the minimum degree, and both selection rules find it without doing anything.
There is no overlap term — and the overlap term is the whole of the
combinatorial content here, since two global qubits sharing a gate save that
gate, which is why the optimum is *not* simply "the g qubits of lowest degree".

g = 1 is therefore run, reported separately, and excluded from every verdict.
Its purpose is to show that the pipeline reproduces an answer that is known
before the run. If it does not, the pipeline is wrong and nothing else in the
study can be read.

## 6 The four declarations

Stated without reference to the architecture, so that they travel.

**Granularity.** The cost is a count of gates acting on the global set. The
smallest nonzero difference is therefore one gate. Below one gate there is no
difference to report, whatever a mean says.

**Bounds, per arm.** The floor of an arm's cost is the exhaustive optimum of
that instance, not zero. The ceiling is the number of gates in the circuit. The
spread floor is declared separately per arm: the random arm's spread is
measured over its own draws as well as over instances, the two deterministic
arms' over instances alone.

**Unit of analysis, and the comparison is paired.** The unit is the instance —
one graph, at one size, at one g. Arms are compared **instance by instance**,
and the quantity carried through the statistics is the paired difference, not
the difference of two means. An unpaired comparison would put the variation
between graphs into the noise, where it would swamp the effect being looked
for; paired, the measurement is of what the choice of arm costs on *that*
instance. A bootstrap resamples instances, not gates.

**Minimum units.** Below 5 usable instances in a cell, the verdict for that
cell is **not evaluable**, not "unresolved" and not "equivalent".

## 7 The resolution rule

The comparison reports one of four verdicts per cell: **separated**,
**bounded**, **unresolved**, **not evaluable**. They are kept apart in the
printout and never merged. A verdict of "equivalent" is not available at all.

> Where two arms cannot be separated, the result is reported as **bounded above
> by** the measured spread of their paired difference, with that spread printed
> next to it. If the spread exceeds **2 gates**, the verdict is **not
> evaluable** regardless of the point estimates.

**That limit of 2 gates is a judgement, not a derivation, and it is recorded as
one so that a reader can disagree with it specifically.** The reasoning: a
selection rule that cannot be told from another to within two gates cannot
inform a design decision at the scale where a hypercube is used at all, where
circuits carry thousands of gates. A reader who thinks the right limit is one
gate, or five, should say so against this paragraph, before the numbers.

The trap this rule exists to block is the same one as in the QCNN study: H1
below is the convenient hypothesis, and it is satisfiable by a large spread. An
arm that cannot be told apart from another because the measurement is coarse is
not an arm that performs equally.

## 8 Registered hypotheses

- **H1.** The mutual-information arm is not separated from the gate-structure
  arm, and the bound is below 2 gates. **This is the convenient one**, it
  continues an existing QWeb finding, and it is named as convenient for that
  reason.
- **H2.** The random arm is separated from the gate-structure arm and sits
  above it. The positive control.
- **H3.** The gate-structure arm reaches the exhaustive optimum in a majority
  of instances.
- **H4.** The cost of a given global set is the same for every initial state of
  the same circuit. Expected to be **true by construction**, and registered
  anyway so that the construction is checked rather than assumed.
- **H5.** Whatever difference exists between arms does not grow with g at fixed
  n. If it does grow, the combinatorial account in §3 is incomplete and the
  study says so.

H2 and H4 are the two that can embarrass the study. H2 fails if the instrument
cannot tell a deliberately bad rule from a good one; H4 fails if the cost model
in §3 is wrong, and then every other number here is about something else.

**One expectation about H3, written down now so that it cannot later read as an
excuse.** The gate-structure arm is close to "take the qubits of lowest degree,
corrected for overlap". On graphs whose degrees are nearly uniform, that
correction has little to bite on, and H3 may come out close to tautological —
the arm reaching the optimum because at that structure almost any sensible rule
would. The instance set is not uniform, and the expectation is therefore
specific: the gap between a degree-only rule and the true optimum should be
visible on the scale-free and clustered graphs and small on the regular ones.
If the result is a flat near-optimum everywhere, the finding is thin rather
than wrong, and it will be reported as thin.

## 9 Invalidating conditions

Any of these voids the run. They are written now so that they cannot be written
later.

1. **The positive control fails.** If the random arm is not separated from the
   gate-structure arm, the comparison cannot distinguish selection rules at
   all, and no statement about H1 may be made from it.
2. **The ground truth is not verified.** The enumeration of C(n, g) subsets
   must agree with an independent slower implementation at the smallest size,
   subset by subset and not by count. *Counting the right number of things is
   not the same as having the right things* — the gate that caught a real
   defect in `findability_large.py`, reused here deliberately.
3. **The cost model is not verified.** One small instance is simulated
   directly, and the amplitudes that change hands per global-qubit gate are
   counted. If that count is not exactly 2^(n−1), §3 is wrong and the study is
   void rather than interesting.
4. **The arms do not see the same thing.** The mutual-information arm must be
   computed from a state the circuit actually produces, at a layer declared
   before the run, with no quantity derived from the construction's own
   parameters. Handing an arm a parameter of the generator is a leak that has
   already happened once in this project, in the control probe of the QCNN
   study, and it is named here to make it harder to repeat.
5. **The degenerate subset does not come out as declared.** If g = 1 does not
   reproduce minimum degree for both deterministic arms on every instance, the
   pipeline is wrong and the rest of the run is void, not merely suspect.

## 10 Stopping condition, independent of the result

21 graphs × n ∈ {12, 16, 20} × g ∈ {2, 3, 4}, on both circuit families, with 20
random draws per instance for the random arm. That is 189 instances per family
and 378 in all, plus the 63 instances per family of the declared degenerate
g = 1, which are reported separately and carry no verdict.

The run stops there whether or not any hypothesis has resolved, and no
instance, size, g or family is added afterwards. If the result is unresolved at
that budget, "unresolved at 189 instances per family" is the finding.

## 11 What this cannot show

It cannot show that the hypercube is the right execution model; §2 puts that
out of scope and `hypercube_vs_mps.py` already answers a version of it. It
cannot say anything about noise, about real hardware, or about reassigning the
global set while a computation runs. It cannot generalise past two circuit
families, and both are structured on purpose — on random circuits the question
is known to be empty, since from depth four every cut carries nearly maximal
entanglement and every choice costs the same.

And if H1 holds, the result is a statement about **what an architecture makes
irrelevant**, not about mutual information being useless. The same quantity
predicts the circuit graph at a Spearman correlation of about +0.83 in the
partitioning line. A measure can be informative about a computation and still
have nothing to contribute to one particular decision about it. That
distinction must survive into the write-up.

---

**Sources fixed at registration**

- Schweiss, *Local and Global Information in Distributed Systems*, diploma
  thesis, TU München 1986. Cited as lineage, not as evidence: it supplies the
  shape of the question — weighted workload graph, chosen topology,
  communication cost — and none of its numbers.
- QWeb, *What a Node Actually Holds*. The hypercube distribution of the
  amplitude vector, the node-address indexing, the 2^(n−1) figure and the
  40-qubit / 1024-node scaling that sets g/n here.
  `calculations/node_slices.py`, `calculations/hypercube_vs_mps.py`.
- QWeb, *What the Computation Knows About Its Own Organisation*, with
  V. Ramamurthy. The information-weighted cut and the gate-based cut.
  `calculations/partition_information.py`,
  `calculations/gate_vs_state_partition.py`.
- QWeb, *What the Partitioner Stops Solving*, and its addendum 1. The 21-graph
  instance set, the ground-truth gate reused in condition 2, and the warning
  about comparing shares over different denominators that fixes the upper size
  here. `calculations/findability.py`, `calculations/findability_large.py`.
- QWeb, *What a Verdict Assumes*. The four verdicts, the declared granularity
  and the rule that "equivalent" is not available.
