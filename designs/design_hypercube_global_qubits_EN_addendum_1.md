# Addendum 1 to design_hypercube_global_qubits_EN.md

**23 November 2026, the same day as the note and before any measurement of the
study.** The note is left standing unedited. Everything below is a correction
to it, found by checking an assertion the note made instead of waiting for
invalidating condition 3 to check it during the run.

Evidence committed with this addendum, in `designs/`:
`hypercube_cost_probe.py` and `hypercube_cost_probe_output.txt`. The probe
builds each gate's full operator and reads its crossing structure off the
matrix. It simulates nothing and samples nothing.

---

## A1.1 Why this exists before the first run

§3 of the note asserts that a gate on a global qubit moves 2^(n−1) amplitudes
whatever the state, and builds the whole study on it. Condition 3 was written
to verify that during the run. Verifying it first cost twenty minutes, and the
assertion does not hold as stated. A study whose central claim is wrong in a
way discoverable before the first instance should not be run and then
corrected.

## A1.2 What the probe measures

n = 6 qubits, g = 2 global, so four nodes of sixteen amplitudes. For each gate
the full operator is built and every non-zero matrix element between two
indices with differing global bits is counted. "One way" is the traffic in one
direction, which is the figure §3 calls the cost of a gate.

| gate and placement | indices | one way | node pairs |
|---|---|---|---|
| ZZ(γ), both qubits global | 0 | 0 | 0 |
| ZZ(γ), one qubit global | 0 | 0 | 0 |
| ZZ(γ), no qubit global | 0 | 0 | 0 |
| RX(β) on a global qubit | 64 | **32** | 2 |
| RX(β) on a local qubit | 0 | 0 | 0 |
| CNOT, control global, target local | 0 | **0** | 0 |
| CNOT, control local, target global | 32 | 16 | 2 |
| CNOT, both global | 32 | **16** | 1 |
| XX+YY(δ), both global | 32 | 16 | 1 |
| XX+YY(δ), one global | 32 | 16 | 2 |
| XX+YY(δ), none global | 0 | 0 | 0 |

For reference at this size, 2^(n−1) = 32 and 2^(n−2) = 16.

## A1.3 Three corrections to §3

**A diagonal gate never costs anything, however many of its qubits are
global.** Each node multiplies its own slice in place, because it knows its own
global bits. Nothing crosses. The note treated "acts on a global qubit" as the
cost condition; the cost condition is **acting non-diagonally on a global
qubit**. Being global is not expensive. Being written to is.

**A controlled gate is asymmetric, and the deciding object is not the
interaction graph.** CNOT with the control global and the target local moves
nothing at all. With the target global it moves. The interaction graph is
undirected and cannot express that difference. What decides the cost is which
qubits are *written to* by non-diagonal operations — a directed quantity. This
is the correction with the furthest reach, because the entire partitioning line
in QWeb is built on the undirected interaction graph, and for this architecture
that object is the wrong one.

**The cost is not one figure.** A full single-qubit rotation on a global qubit
moves 2^(n−1). A controlled gate with a global target moves 2^(n−2), because
only the half of the register with control = 1 is touched. §3's "2^(n−1)
whatever" is true of one gate type and not of gates in general.

## A1.4 Family A as registered is degenerate by construction

QAOA, as §5 specifies it, consists of a cost layer exp(−iγ Σ Z_i Z_j) and a
mixer of single-qubit rotations on every qubit. The cost layer is diagonal, so
by A1.3 it is free — on any graph, at any size, for any choice of global set.
The mixer touches every qubit equally. The communication cost of a QAOA circuit
is therefore **p · g exchanges, independent of which qubits are global and
independent of the graph.**

The selection question is empty on family A. That is not a weak effect to be
measured; it is a constant, and no arm can beat another at it.

Family A is therefore **declared degenerate**, on the same footing as g = 1 in
§5: it is run, reported separately, carries no verdict, and exists to confirm
that the pipeline reproduces p · g on every instance. If it does not, the
pipeline is wrong.

**The §5 reasoning about overlap is withdrawn with it.** §5 argued that two
global qubits sharing a gate save that gate, and called this the combinatorial
content of the problem. In the corrected model there is no shared edge to save:
the cost is accumulated per non-diagonal action on a global qubit, and two
global qubits in one non-diagonal gate cost more rather than less. The arms
read a directed incidence count, not an undirected degree with a correction.

## A1.5 Two replacement families, on the same instance set

Both keep the 21 published graphs, the sizes n ∈ {12, 16, 20} and the values
g ∈ {2, 3, 4} exactly as registered, so the budget of §10 is unchanged at 189
instances per family.

**Family A′ — graph-structured XX+YY.** The same graphs, with the diagonal ZZ
coupling replaced by a non-diagonal XX+YY coupling on each edge, plus the same
mixer. Undirected, and the question is non-empty: a gate costs whenever either
of its qubits is global.

**Family B′ — oriented CNOT ladder.** The same graphs, each edge oriented by a
rule declared here — from the lower vertex index to the higher — with a CNOT
per oriented edge and single-qubit rotations between layers. Directed, so that
the asymmetry found in A1.3 is actually exercised: a qubit that is only ever a
control is free to make global, and a qubit that is written to often is
expensive.

The orientation rule is fixed now, before any measurement, because choosing it
afterwards would be choosing the instance set from the result.

## A1.6 Invalidating condition 3, restated

The condition is no longer "the count is 2^(n−1)". It is: for each gate type in
the families above, the amplitudes crossing a node boundary must equal the
value this addendum's model predicts — zero for diagonal gates and for a
controlled gate with a local target, 2^(n−1) for a single-qubit rotation on a
global qubit, 2^(n−2) for a controlled gate with a global target. Measured
against the operator, not assumed. If any gate type disagrees, the study is
void rather than interesting.

## A1.7 What this does to the hypotheses

**H1, H2, H5 stand unchanged.** They are statements about arms and do not
depend on which gates cost what.

**H3's expectation sharpens.** §8 expected the gate-structure arm to be close
to a degree rule corrected for overlap. It is instead close to a rule over
**directed non-diagonal incidences**: on family B′ the optimum should prefer
qubits that appear as controls and avoid qubits that are written to. That is a
sharper and more falsifiable expectation than the one it replaces, and it is
recorded before the first instance.

**H4 is partly settled already and still gets measured.** The probe shows the
crossing structure is a property of the operator and carries no reference to
the state, so state-independence holds for these gate types by construction.
The registered hypothesis stays, because what has been checked is eleven gate
placements at one size, not the circuits of the study at three sizes.

## A1.8 What does not change

The question in §2, the four arms in §4, the sizes and the values of g, the
four declarations in §6 including the paired comparison, the resolution rule
and its limit of two gates in §7, and the stopping condition in §10. The cost
unit remains a count of gates, now counted as non-diagonal actions on the
global set rather than as gates touching it.

## A1.9 For the record

This corrects a note registered earlier the same day, and it corrects it before
a single instance was measured. The note is not edited, this addendum is dated,
and the probe that found it is committed with it. The study has not yet
produced a number.
