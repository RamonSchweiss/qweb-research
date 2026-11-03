# Addendum 4: the ledger was the wrong minimum, by a factor of eight

**Date:** 3 November 2026. The note remains in force and is not altered. This
records a correction to section 5 of the note and to section 8's invalidating
condition, both of which were wrong in the same way, and both of which were
found by a question from Daniel Hug (qubit-lab.ch) on the morning of
3 November.

**The question.** D is a projector minus the identity, so it is a product term
minus a product term, and that holds across every cut. Should a single
controlled block with one ebit not do, instead of paying for each crossing CX
separately?

It should. The verification is
`calculations/diffusion_controlled_block.py`, output in
`designs/diffusion_controlled_block_output.txt`.

---

## 1 The structural reason, which needs no measurement

|s⟩ = H^n|0⟩ is |+⟩^⊗n, a **product state**. Across any bipartition (A, B)
therefore

    |s⟩⟨s| = P_A ⊗ P_B,     D = 2·P_A⊗P_B − I_A⊗I_B

a sum of two product terms. The operator Schmidt rank of D across every cut is
two, at every register size and wherever the cut falls.

This was visible in the note from the first line and nobody looked at it,
least of all the author, who had just written an article about reading
operators instead of circuits.

## 2 The protocol, and what crosses

On each side, compute a local flag that is one exactly when that half is in
|+…+⟩. Apply a single controlled-Z between the two flags across the boundary.
Uncompute both flags locally. The flags are explicit V-chains over each side's
**own** ancillae, so every other gate has both its qubits on one side by
construction.

Checked on |s⟩ and on four random states orthogonal to it, at four register
sizes and three split positions each:

      n    split    max error     leak   phase   2q gates   crossing
      4      2|2      2.2e-15  1.2e-16   +1.00         25          1
      6      3|3      2.3e-15  9.2e-17   +1.00         73          1
      8      1|7      2.1e-15  7.2e-17   +1.00        135          1
      8      4|4      2.1e-15  5.8e-17   +1.00        121          1
     10      1|9      1.6e-15  4.6e-17   +1.00        183          1
     10      5|5      1.6e-15  3.8e-17   +1.00        169          1

The protocol is −D to within 3e-15 everywhere, the ancillae return clean, and
**one** operation crosses the boundary — not one per size, not one per split.
One.

## 3 What was wrong, and it was wrong twice over

**Section 5 priced the wrong minimum.** It gave eight ebits per iteration
"under free placement". That is the minimum over *placements of a particular
circuit* — the V-chain, cut in half. The quantity that matters across a module
boundary is the minimum over *implementations of the operator*, and the two are
not the same number. Addendum 3's routed figure of about nineteen has the same
defect, one layer further down.

**Section 8's invalidating condition was too weak.** It named a cut-aware
router as the thing this programme does not bound. That is not enough: a router
routes the circuit it is handed. What was missing is a cut-aware
*decomposition*, which does not route anything but writes the operator down
differently. Nothing in the note's declared instrument could have found it,
which is why no measurement did.

## 4 The ledger, corrected

One nonlocal CZ costs one ebit and two classical bits, which is the standard
protocol and is optimal for a nonlocal CNOT; CZ is CNOT up to local Hadamards.

       n   iterations   note, free   addendum 3, routed   controlled block
      16          201        1,608                3,819                201
      20          804        6,432               15,276                804
      30       25,735      205,880              488,965             25,735

A factor of eight against the note's own figure and about nineteen against the
routed one. Both overstated the cost.

## 5 What is not cheaper

The local work, and it is worth saying because the correction otherwise sounds
like something for nothing. Each side computes and uncomputes a chain over its
own half, so the two chains together exceed the single chain they replace:

      n    protocol    V-chain    ratio
      4          25         25     1.00
      6          73         49     1.49
      8         121         73     1.66
     10         169         97     1.74

The protocol is the more expensive circuit by up to three quarters again. What
collapses is the crossing count, and only that. The qubit count does not fall
either, since each side still needs its own ancillae.

## 6 The invalidating condition, walked into while correcting a number

The first version of the verification script handed the multi-controlled X to
Qiskit's synthesiser and transpiled the result. The synthesiser borrowed dirty
ancillae from the **other side of the boundary**, and between eleven and
seventy-one gates crossed instead of one. The numbers looked like a refutation
of the whole idea.

That is, word for word, the invalidating condition stated in section 8 of the
note: hand the multi-controlled Z to the transpiler and the measurement
describes the transpiler's synthesis policy rather than the declared circuit.
It was written down on 1 November and walked into on 3 November, while
correcting a different number.

It is recorded here for two reasons. The condition earned its place — it caught
a wrong result within minutes rather than after publication. And a correction
that itself needed correcting before it was an hour old is worth knowing about
when reading the one above.

## 7 What is still open

**Two modules only.** With k modules the flags must be combined along a chain
or a tree, crossing k−1 boundaries, and what each of those crossings costs is a
separate question. It is not answered here and is not guessed at: guessing is
how the figure this addendum corrects came about.

**The oracle**, as everywhere in this programme, is assumed and not counted.

**And the other direction remains untested.** This addendum shows the operator
admits a cheaper implementation across a link. It does not show that the
article's three findings about the *routed on-chip* cost are wrong, because
they are about a different question. Sections 3 and 4 of the note, and
addendum 3's factor of about 2.4, stand unaltered.

## 8 The shape of the error

The article "What the Operator Hides From the Partitioner" argues that the
operator's form misleads about the routed cost, and that one should read the
circuit. Across a link the reverse holds: the circuit's form misleads, and the
operator tells the truth, because one can see in it that |s⟩ factorises.

The same mistake, in the other direction, made while writing about the first
direction. Both belong in the article, and it is a better article for carrying
both.
