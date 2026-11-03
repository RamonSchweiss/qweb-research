# Addendum 3 to the design note "Periodicity of the routed circuit and the stability of the cut"

**Date:** 3 November 2026.
**Status:** carries out the tightening that the run of 20 October 2026 promised
in its own printout and left undone. The original note
(`design_routed_partition_orbit_EN.md`) and Addenda 1 and 2 are not altered;
their text stands as committed. Everything below is additional and dated.

**What this addendum does.** It replaces the move set of the matched-window
control with the one a router actually has, re-runs the comparison alongside the
published arm, and reports what changed. It does not revise any result of the
run of 20 October, and it does not touch H1, H2, H3 or H4.

The calculation is `calculations/orbit_edge_null.py`, output in
`designs/orbit_edge_null_output.txt`.

---

## A3.1 What was promised, and why it had to be kept

The printout of 20 October stated the defect itself:

> the random arm draws its swaps uniformly over all qubit pairs, while the
> router may only use edges of the coupling map. The random arm therefore
> scrambles harder than the hardware could, so the gap measured above is an
> UPPER bound on the router's advantage. A tighter null — random swaps
> restricted to coupling edges — would narrow it. The direction of the result
> does not depend on this; the size of the margin does. Tightening it would be
> a further dated addendum and has not been done.

An arm permitted moves the hardware cannot make loses the comparison partly for
a reason that has nothing to do with routing, and the published margin inherits
that. The defect ran in our favour, which is the reason to close it rather than
leave it declared. A caveat that only ever costs the other side is not a
caveat; it is a discount.

The tightening can only raise the control rate, so it can only withdraw claims
that the published arm left standing. It cannot add any. It was run knowing
that.

## A3.2 The tightened arm

Arm A is the published control: each swap drawn uniformly over all qubit pairs.
Arm B substitutes one line — each swap drawn uniformly over the undirected
edges of the coupling map, which is the only move a router could have chosen.
Everything else is held fixed: the same twenty-one problem graphs, the same
router seeds, the same per-layer swap budget copied from the real run, the same
window length *W = d*, the same five control seeds, the same question.

At ten qubits the move set shrinks sharply. Heavy-hex and the line have nine
coupling edges, the grid thirteen, against forty-five qubit pairs — a move set
one fifth to under a third the size.

## A3.3 Reproduction, checked before anything else

A tightening measured against a figure that has not been reproduced is worth
nothing. The script hard-codes the per-seed shares printed on 20 October and
checks arm A against them; a mismatch aborts the run.

Arm A reproduces the router rate, the run count and all five per-seed shares to
the printed digits on all three topologies.

## A3.4 What came out

      topology    router   scatter        arm A   arm B    verdict A      verdict B
      heavy-hex     0.65   0.47 - 0.77     0.08    0.10    below          below
      grid          0.30   0.12 - 0.67     0.14    0.16    WITHIN         WITHIN
      line          0.57   0.30 - 1.00     0.07    0.10    below          below
      pooled        0.55                   0.10    0.12

Margins, router minus control: +0.56 → +0.55 on heavy-hex, +0.16 → +0.14 on the
grid, +0.50 → +0.48 on the line.

**No verdict moves.** The grid was already the null outcome on 20 October and
stays it: constancy carries no information about routing there, and every claim
resting on it was withdrawn then and remains withdrawn. Heavy-hex and the line
stay clearly below the router's seed-to-seed scatter.

## A3.5 The difference is below what this sample can resolve, and that is the finding

Arm B's means exceed arm A's by 0.02, 0.02 and 0.03. It would be easy to report
that as a measured effect of the tightening. It is not one.

Arm B's per-seed shares are **more scattered** than arm A's, because a walk
confined to nine or thirteen edges explores a far smaller space and its outcome
depends more on the seed: 0.04 to 0.16 on heavy-hex and 0.03 to 0.20 on the
line, against 0.06 to 0.12 and 0.05 to 0.07 under arm A. With five control
seeds, a difference of two or three points between the two arms sits well
inside that spread.

So the honest statement is not "the tightening raises the control rate by two
points". It is: **the tightening changes the control rate by no amount this
sample can resolve, and changes no verdict.** The mechanism was real, declared
and worth closing. Its measured size is not separable from noise here, and
reporting it as a number would be reading an agreement — or a small
disagreement — to more digits than the data carries.

This is the same discipline the diffusion work arrived at on 3 November from a
different direction, and it applies to our own result first.

## A3.6 What the margin now is, stated precisely

The move-set defect is closed. One defect in the same direction is not.

Arm B copies the **number** of swaps per layer from the real run but not their
**placement**: a router chooses swaps that are mutually compatible within a
layer, while this arm may draw the same edge twice in one layer and waste the
budget. That still lets the null differ from any schedule a router could
produce, and it runs in the same direction as the defect just closed.

The margin is therefore **still an upper bound on the router's advantage, and a
considerably tighter one**. It is not a point estimate, and the 20 October
caveat is narrowed rather than removed. Closing the remaining one would require
drawing a matching per layer rather than a sequence of independent edges, and
would be a further dated addendum.

## A3.7 What is not changed

p_max = 64 and the stopping rule of section 6. The all-to-all pipeline check and
the seed control of section 4. The statistical floor of section 5 and the
comparison cell of Addendum 1. The limits of section 8. The decision rule of
A2.3, which was applied here unaltered and to both arms. H1, H2 and H3 as
written, and H4 as registered in Addendum 1.

The results of the run of 20 October 2026 stand as measured. The report now
carries both arms, and the upper-bound qualifier on the margin stays, narrowed
as A3.6 describes.
