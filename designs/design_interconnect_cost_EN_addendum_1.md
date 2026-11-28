# Addendum 1 to design_interconnect_cost_EN.md

**Date:** 28 November 2026, a few hours after version 1 was committed.
**Status:** registered before the first cost of this study was computed. No
cost model has been evaluated on any subset, no store or printout exists, and
nothing here was chosen in the light of a result.

**Why it exists.** Version 1 was written before its own algebra was carried out.
Carrying it out, in order to write the run, found three declarations that do not
hold and one fact about the declared circuits that decides what the study can
measure. The three declarations are corrected here. The fact is stated here and
its consequence is left open, because it is a question of scope and not an error
to be repaired.

M1, the sizes, the values of g, the seeds, enumeration as the only ground truth,
rule D, the invariance gate, the one-in-five ambiguity bar, the prohibition on
fitted weights and section 8's account of what cannot be shown all stand
unchanged.

---

## 1 The error in M2

Section 2 declared M2 as the model in which "distance drops out and volume is
all that remains", gave it as the degree sum alone, and called the `+ 2·|S|`
term "a distance artefact".

That is backwards. Re-running the hop accounting of `hypercube_cost_probe.py`
on the four cases that matter reports both the number of amplitudes crossing a
node boundary and the hop distance they cross:

| gate | amplitudes moved | max hops | units |
|---|---|---|---|
| rotation on a global qubit | 64 | 1 | 2 |
| CNOT, target global | 32 | 1 | 1 |
| XX+YY, exactly one qubit global | 32 | 1 | 1 |
| XX+YY, both qubits global | 32 | **2** | 2 |

(n = 6, g = 2, so one unit is 2^(n−2) = 16 amplitude-hops.)

**The rotation's factor of two is volume, not distance.** It moves twice as many
amplitudes as a CNOT because a rotation mixes every amplitude pair along its
dimension while a CNOT touches only the half with its control set. Its distance
is one hop, like everything else in the table. A model that charges volume and
not distance therefore **keeps** the `+ 2·|S|` term in full.

**The one factor of two that is distance is the two-global exchange gate** — 32
amplitudes, two hops. That is the detour addendum 2 of the hypercube note
identified as repaying exactly the overlap an edge-counting model would have
saved, and it is why the objective is separable at all.

Version 1's M2 removed the only term that is not a distance artefact and kept
the only one that is.

## 2 M2, corrected, and what it does to the question

Volume charged, distance not:

    diagonal gate, any placement            0
    rotation on a global qubit              2
    CNOT, target global                     1
    CNOT, target local                      0
    XX+YY, exactly one qubit global         1
    XX+YY, both qubits global               1   <- was 2; the detour is distance

Write ch(v) for the M1 charge of qubit v — twice its rotation count, plus its
CNOT-target count, plus the number of exchange gates touching it — and P(S) for
the number of exchange gates with **both** qubits in S. Then

    cost_M1(S) = Σ over v in S of ch(v)
    cost_M2(S) = Σ over v in S of ch(v) − P(S)

The overlap M1's detour repaid is no longer repaid, so it survives as a
subtracted term. **M2 is therefore not separable**: a set of global qubits
adjacent to one another is cheaper than the same charges scattered apart.

**This inverts what version 1 expected of M2.** M2 is not the model under which
the rule trivially survives; it is the first and cleanest breaker of the proof's
premise, and it breaks it for one structural reason nameable in advance — a gate
that charges two global qubits at once. A circuit of diagonal gates,
single-qubit rotations and CNOTs has none, so P ≡ 0 and the cost stays
separable. **The discriminating property is the gate set, not the model.**

## 3 M3, with the two-dimensional exchange declared

M3 charges each crossing at the tier of the dimension it crosses: w = w_intra = 1
for a qubit in an intra-node slot, w = w_inter ∈ {4, 10, 25} otherwise, k = 2
slots, all as declared in version 1.

Version 1 left open what an exchange crossing two dimensions pays. **Declared:
one weighted hop per dimension, w(u) + w(v)** — a two-tier model is a distance
model, so the two hops the probe measures are charged separately, each at its
own link's tier. The alternative reading, one combined exchange at
max(w(u), w(v)), is **not** used.

That makes M3 separable by construction, since every charge then falls on one
qubit:

    cost_M3(S) = Σ over v in S of w(v)·ch(v)

**Which slots go to which qubits is the scheduler's choice, not the labelling's.**
Version 1's "lowest k global indices" would make the cost depend on qubit
numbering, which the invariance gate would then void — correctly, because an
index-based tier is the same ill-posedness addendum 5 of the cut-degeneracy note
was about. **Declared instead: the cost of a set is the minimum over assignments
of the k intra-node slots**, which is

    cost_M3(S) = w_inter·Σ ch(v) − (w_inter − 1)·(sum of the k largest ch in S)

and is invariant under relabelling.

## 4 M4, restricted so that it cannot go negative

Version 1 subtracted λ times "the number of two-global gates whose both qubits
lie in the intra-node class". A diagonal gate with two global qubits is such a
gate and charges nothing, so the term as written could subtract from zero.
**Declared: it counts only gates whose M3 charge is non-zero** — exchange gates,
and CNOTs whose target is global — with both qubits global and both in
intra-node slots. With λ ∈ {0.25, 0.5} and every counted gate charging at least
one unit, no cost falls below zero.

With k = 2 one pair holds the intra-node slots, so

    cost_M4(S) = w_inter·Σ ch(v)
                 − max over pairs {a,b} ⊆ S of
                   [ (w_inter − 1)·(ch(a) + ch(b)) + λ·q(a,b) ]

where q(a,b) counts the charging gates acting on exactly that pair. The cost
depends on which pairs are present, so **M4 is not separable, and unlike M2 it
breaks separability for circuits with no exchange gate at all** — a CNOT between
two global qubits suffices. That is what M4 can show that M2 cannot, and it is
now the only thing claimed for it.

## 5 Degenerate cells are reported as degenerate, not as ambiguous

A family whose cost is constant over every subset of a given size under a given
model has no optimum to miss. Rule D would call every such cell ambiguous, and
the one-in-five bar would then void whole sizes over families that were never
measuring anything.

**Declared: a cell whose cost is constant across all subsets is reported
degenerate for that model.** It enters no hypothesis and no ambiguity count, and
is listed with its reason. This follows A1.4 of the hypercube study, which
declared the QAOA family degenerate in the same way and for the same reason.

## 6 What the declared circuits actually look like, measured

Before any cost model was evaluated, the charge vector of each of the five
families of section 7 was computed, because a flat charge vector means the rule
has nothing to choose and no loss can be measured on it. Counts per circuit:

| family | distinct ch values | ch range | exchange pairs | charging pairs | charge vector |
|---|---|---|---|---|---|
| QFT | 1 | 2…2 | 0 | 0 | flat |
| ripple-carry adder | 5 | 1…18 | 0 | 22 / 28 / 34 | varies |
| QAOA layer, 3-regular | 1 | 2…2 | 0 | 0 | flat |
| HEA, CNOT ladder | 1 | 9…9 | 0 | 16 / 20 / 24 | flat |
| random circuit, depth 8 | 5 / 6 / 7 | 16…22 | 24 / 22 / 30 | 42 / 49 / 56 | varies |

(Three numbers where they differ are n = 16, 20, 24. The HEA appears here
because section 7 declares one; version 1's §7 named four families plus the
random circuit, and the ladder is the fourth.)

**Three of the five are flat.** The QFT is Hadamards and diagonal controlled
phases; the QAOA layer is diagonal couplings and one mixer rotation each; the
HEA ring gives every qubit the same number of rotations and the same number of
ladder gates. In all three every qubit carries the same charge, so under M1 and
M3 every subset of a given size costs the same and the cells are degenerate by
section 5. They are kept as implementation controls: **a model under which any of
them is not flat has an implementation error and the run is void.**

That leaves the adder and the random circuit as the only two families on which a
loss can be measured. By section 2 they fall on opposite sides of the
discriminating property: the adder has no exchange gate, the random circuit has
both exchange gates and charging pairs.

**The addition of an XX+YY-ladder HEA, which an earlier draft of this addendum
proposed, is withdrawn.** Its charge vector is flat too — twelve for every qubit
at every size — so it would produce ambiguity under rule D and no measurable
loss. The reason for adding it does not hold.

## 7 The hypotheses, restated

Families split by gate set, not by result:

- **separable group** — QFT, adder, QAOA layer, HEA with a CNOT ladder.
- **exchange group** — the random circuit at depth 8.

**H1 (revised).** Under M3, at every size, every g and every w_inter, the rule
"take the g qubits of lowest ch, with the k largest of them in the intra-node
slots" is cost-optimal in **every** non-degenerate cell, in both groups. Section 3
derives this, so H1 is as much a check on the implementation as a claim; a
counterexample refutes it and means one of the two is wrong.

**H2 (revised; replaces version 1's H2 and takes over the role of its H3).**
Under M2, the lowest-charge rule is **not** cost-optimal in at least one cell at
every size in the exchange group, and the median loss over the failing cells is
at least one unit. A failure to break would mean the subtracted term never bites
on this grid, which is a result about the grid and must be reported as one.

**H3 (revised).** Under M4, the rule is not cost-optimal in at least one cell at
every size in the separable group.

**H4.** Unchanged.

## 8 A verification gate, added

Before any hypothesis is read, the implementation must reproduce the published
closed form exactly on the instance set of the hypercube study — for the XX+YY
family `Σ deg(v) + 2|S|`, for the oriented CNOT family the same with in-degree —
and corrected M2 must reproduce `Σ ch(v) − P(S)` on those instances, on every
cell and every subset. It must also find the QFT, the QAOA layer and the CNOT
ladder flat under M1, M2 and M3. **Any disagreement voids the run.**

## 9 One question is left open, deliberately

H3 is evaluable only on the adder, which is one circuit per register size and
therefore three cells per size — below the five-unit floor of
`design_resolution_limit_EN.md`. **As registered, H3 is not evaluable, and this
addendum does not repair that**, because widening the instance set is a decision
about the study's scope rather than a correction of an error, and a scope
decision taken while writing the run is the thing a registered design exists to
prevent. It is recorded here as open, and whatever is decided will be declared
before the run in its own addendum, not after it.
