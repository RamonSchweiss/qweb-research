# Addendum 2: extending the register range so the heavy-hex arm can speak

**Date:** 1 November 2026, written and committed **before** the rerun it
authorises. The note of the same day remains in force and is not altered.
Addendum 1 recorded the run under it; this changes one declared parameter for a
second run and says exactly which.

---

## 1 What Addendum 1 left open

The heavy-hex arm produced nothing. All eight sizes fell inside the degenerate
subset declared in section 9 of the note — three as trees, five because the
subgraph's diameter reached half its size. The grid arm decided, and withdrew.

## 2 The obvious repair does not work, and is recorded so that nobody retries it

The first thing to try is a larger host lattice, on the assumption that
heavy-hex(5) is simply too small. It is not the problem. Running the published
subgraph rule unchanged — breadth-first from every node, keep the induced
subgraph with the most edges, ties to the lowest start node — on three host
lattices gives identical diameters at every size up to P = 20:

      P    P/2    heavy-hex(5)   heavy-hex(7)   heavy-hex(9)
     12    6.0        6              6              6
     14    7.0        8              8              8
     16    8.0        9              9              9
     18    9.0       10             10             10
     20   10.0       11             11             11
     22   11.0       10             11             11
     24   12.0       11             12             12

Every entry up to P = 20 fails the rule, on every host. At P = 22 and 24 the
larger hosts are slightly **worse**, because the edge-maximal ball lands
differently. The degeneracy is a property of the heavy-hex lattice's local
geometry — degree at most three, with twelve-qubit rings — and not of the
lattice's extent.

This was proposed as the repair in conversation before it was checked. It is
recorded here as refuted rather than quietly dropped.

## 3 What actually gates the arm

The register range. Under the published rule on heavy-hex(5), the subgraph
passes the declared degeneracy test at **P = 22** (diameter 10 against 11) and
**P = 24** (diameter 11 against 12), and at no smaller size. The note declared n
from 4 to 11, that is P from 6 to 20, which stops one size short.

## 4 The change, and only this change

**Register sizes extended from n ≤ 11 to n ≤ 13**, that is P from 6 to 24. The
contrast sizes are extended from n ∈ {7, 9, 11} to n ∈ {7, 9, 11, 13} for the
same reason.

Unchanged: the decomposition, the subgraph generator and its host lattice, the
grid generator, the router and its heuristic, the trivial initial layout, the
five router seeds, the two degeneracy rules, the contrast families and their
density, the stopping condition of section 10, **and its threshold of 0.05**.
The threshold is not revisited now that it has bitten once.

**Why n = 13 and not further.** Balanced bipartitions are enumerated
exhaustively, and P = 24 gives 1,352,078 of them, about 250 MB. P = 26 would
give 5,200,300 and roughly a gigabyte, and heavy-hex(5) has not been checked
there. So n = 13 is the ceiling this design reaches, not a number chosen for
convenience.

## 5 What this buys, and what it does not

Heavy-hex gains two non-degenerate sizes, P = 22 and P = 24. The grid gains
one, P = 24, which is a 4 x 6 lattice of diameter 8; P = 22 is a 2 x 11 strip
of diameter 11 and remains degenerate by the same rule.

**Two sizes is thin, and this addendum says so rather than letting the table
imply otherwise.** Two sizes can show whether heavy-hex agrees with the grid's
measured factor of about 2.25. They cannot establish a trend in P for
heavy-hex, and the rerun must not be read as doing so.

## 6 The alternative considered and declined

Changing the tie-break — among balls with the most edges, take the one of
smallest diameter — would let heavy-hex pass from P = 18 upward, with diameter
8, giving four or five sizes instead of two. It is declined because the note
declared the generator to be literally the one already published in
`routed_partition_orbit.py`, and that identity is worth more than two extra
sizes: it is what makes this measurement's coupling maps the same objects as
the earlier one's.

It is held in reserve. If two sizes prove too thin to say anything, it becomes
a third addendum with its own date, and the loss of comparability is then
stated as the price.

## 7 Why this is not fishing for a favourable size

Extending a size range after a withdrawal is the kind of move that deserves
suspicion, so the constraints are written down.

**Addendum 1's verdict on the grid is final and is not reopened.** The
registered four sizes withdrew the objective, and that stands whatever the new
sizes show. The rerun reports the new grid size P = 24 **separately**, as an
addition, and does not merge it into the earlier count of nought out of four.

**The stopping condition and its threshold are unchanged**, so a new size can
only be retained or withdrawn by the rule that already produced a withdrawal.
Nothing has been loosened.

**The extension adds sizes to an arm that produced no verdict at all,** which
is a different thing from adding sizes to an arm whose verdict was unwelcome.
Had heavy-hex decided and withdrawn, this addendum would not exist.

## 8 What the rerun is for

One question: does heavy-hex agree with the grid that a cut-oblivious router
costs about a factor of two on the diffusion's cut? Agreement gives finding 3
of the planned article a second topology family. Disagreement is the more
interesting outcome and would make the factor a property of the coupling map
rather than of the router, which the article would then have to say.

Either way the arithmetic of sections 3 and 4 of the note is untouched, and so
is the withdrawal of section 6 on the grid.
