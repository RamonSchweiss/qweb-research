# Addendum 1 to findability_report.md — n = 26 and n = 28

**10 November 2026. Ramon Schweiss, QWeb © Research.**
Protocol: `designs/design_findability_EN_v2_addendum_1.md`, written before this
run and stating plainly that this arm breaks the registered stopping condition
of version 2.
Measurement: `calculations/findability_large.py`.

The registered grid n = 10…24 is unchanged and keeps the verdicts it already
has. Everything below is a post-hoc extension and is reported separately.

---

## 1 The gate caught a defect in the new ground truth, on its first use

§3 of the protocol made this arm conditional on the vectorised enumeration
agreeing *exactly* with `partition_topology` on every size where both run. It
did not. The minima disagreed in 9 to 15 of 21 graphs at every single size.

The cause was in the new code: it put the **selected** vertices on side True,
where `partition_topology.partitions` puts vertex 0 and the selected vertices on
side False. The result was n/2 − 1 vertices on one side — not balanced
bipartitions at all, so not the comparison class, so a smaller minimum.

What makes this worth recording is what the gate would have missed. The
**partition counts were exact at every size** — 126, 462, 1,716, 6,435, 24,310,
92,378, 352,716, 1,352,078, all matching C(n, n/2)/2. A check that counted the
objects would have passed it. Only the cross-check against the slow
implementation caught it.

*Counting the right number of things is not the same as having the right
things.*

After the fix the gate passed on all eight sizes and all 21 graphs each, zero
mismatches, and the arm proceeded.

## 2 The result the extension was run for, and it is the weaker branch

| n | unbalanced | of | share | smaller side | deficit |
|---|---|---|---|---|---|
| 20 | 5 | 21 | 0.24 | 9 | 1 |
| 22 | 8 | 21 | 0.38 | 10 | 1 |
| 24 | 4 | 21 | 0.19 | 11 | 1 |
| 26 | 9 | 20 | 0.45 | 12 | 1 |
| 28 | 2 | 20 | 0.10 | 13 | 1 |

**The share is not monotonic in n.** §6 of the protocol named this branch in
advance, so the weaker statement is the one that gets made: over the measured
range the unbalanced share wanders between 0.10 and 0.45, the worst observed
case is 9 of 20 graphs at n = 26, and that is not a point on a curve.

**And the deficit is exactly one vertex, at every size, in every case.** The
smaller side is 9, 10, 11, 12, 13 — that is n/2 − 1 throughout. METIS never
returns a badly unbalanced partition here. It returns one that is off by one.

That corrects §4 of the main report, which said METIS "stops solving the stated
problem". It does not. It solves the problem to within one vertex, and that one
vertex is enough to make its cut incomparable with the balanced optimum, because
an (n/2 − 1, n/2 + 1) split minimises over a strictly larger set. The
engineering consequence is narrower and more interesting than the sentence I
wrote: whether an off-by-one split is usable depends on whether one of the two
processors has a spare register. If both are full it is not executable at all;
if one is not, it is a legitimately cheaper answer to a slightly different
question.

## 3 The other arms at the new sizes

mean gap in remote gates:

| n | KL | spectral | greedy | stoch. greedy | METIS | random |
|---|---|---|---|---|---|---|
| 26 | 0.00 | 1.50 | 2.80 | 0.70 | 0.00 | 14.90 |
| 28 | 0.00 | 0.90 | 3.40 | 0.80 | 0.00 | 16.10 |

hits, and zero-gap answers that are a different member of the optimal set:

| arm | n = 26 | n = 28 | different member, 26 / 28 |
|---|---|---|---|
| Kernighan–Lin | 20/20 | 20/20 | 12 / 8 |
| stochastic greedy | 13/20 | 13/20 | 3 / 4 |
| METIS (balanced answers only) | 11/11 | 18/18 | 0 / 0 |
| spectral | 6/20 | 7/20 | 2 / 3 |
| greedy growth | 5/20 | 4/20 | 0 / 1 |
| random balanced | 0/20 | 0/20 | 0 / 0 |

**Kernighan–Lin holds exactly zero through n = 28** — twenty restarts, every
graph, five sizes beyond where the registered sweep stopped. The main finding of
the study survives the extension.

One thing worth following up and not followed up here: Kernighan–Lin lands on a
**different member** of the optimal set in 12 of 20 graphs at n = 26, against 5
of 21 at n = 10. The cut cost is optimal either way, so this is not a quality
result — but which member it picks is what a scheduler pays migration for, and
that share is rising with n. `cut_degeneracy.py` measures that currency; the two
have still not been put together.

## 4 The random baseline keeps getting more flattering

| n | optimum | random balanced | random excess |
|---|---|---|---|
| 24 | 5.33 | 19.57 | +267 % |
| 26 | 5.75 | 20.65 | +259 % |
| 28 | 5.60 | 21.70 | +288 % |

Over the whole measured range, n = 10 to n = 28, the baseline that arXiv
2605.01974 normalises seven partitioners against moves from +119 % to +288 %
above the optimum. That trend is the one monotone thing in this study.

## 5 One graph is missing at both new sizes

**20 of 21, not 21.** `partition_topology.make_graph` returns None for
`scale-free` seed 2 at n = 26 and at n = 28: in twenty-five attempts it produced
no connected graph with exactly m edges. All 21 exist at every size up to n = 24.

The absence is not neutral. Scale-free is the family where the published script
found the largest information excess — 52 % at layer 10 — and the family where
spectral and greedy do worst. Every n = 26 and n = 28 figure above is therefore
computed over a set missing its most awkward member, and the METIS share at
those two sizes is over 20 graphs while the three earlier sizes are over 21.
Comparing 9/20 with 8/21 as though they were the same denominator is a mistake
this note exists to prevent.

## 6 What this does not settle

- **Nothing above n = 28.** The horizon moved by two sizes; it did not go away.
  C(30, 15)/2 is 77,558,760 partitions and 2.3 GB as packed booleans, and the
  protocol declared n = 28 the ceiling before the run rather than discovering it
  during one.
- **Why the share is not monotonic.** Five points, one density, one tool
  version, and the graph set changes between n = 24 and n = 26. Any of those
  could carry it.
- **Whether an off-by-one split costs anything.** That depends on register
  occupancy, which this study does not model.
