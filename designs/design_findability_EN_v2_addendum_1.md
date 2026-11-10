# Addendum 1 to design_findability_EN_v2.md

**Written 10 November 2026, before the arm it describes is run.**
Ramon Schweiss, QWeb © Research.

---

## 1 This breaks the stopping condition, deliberately

§10 of version 2 says: *"No arm is extended because a result looked promising
and none is cut short because it looked dull."* This addendum extends an arm
because a result looked promising. That is a violation of the registered
stopping condition, and calling it anything else would be worse than committing
it.

So the terms are these.

- The registered grid — n ∈ {10 … 24} — is **reported unchanged**. H1 and H2
  keep the verdicts they already have on that grid. Nothing from this arm is
  folded back into them.
- The new sizes are reported in a **separate table**, labelled as a post-hoc
  extension, so that no reader can mistake them for part of the registered
  sweep.
- No hypothesis is added, removed or reworded. This arm tests nothing new; it
  extends the range of an existing measurement.

## 2 Why it is worth the violation

The main finding of the study is that METIS stops returning balanced partitions
from n = 20: 5 of 21 graphs at n = 20, 8 at n = 22, 4 at n = 24. Exact ground
truth stops at n = 24.

That leaves **three sizes of overlap** between the onset and the ceiling, and
the non-monotonic 5 → 8 → 4 cannot be read as a trend on three points. An
article resting on it would be resting on the same shape of evidence as the
truncation estimate in "What Moves the Baseline" — four points and no run
behind them — which I had to label an estimate two days ago.

Two more sizes make it five, which is still few, but it is the difference
between a trend and three numbers.

## 3 What changes technically, and what does not

**Does not change:** exact enumeration remains the only ground truth; no
heuristic result is ever used as the optimum; the balance assertion stays; the
degenerate subset is separated as in §7; the restart budget stays at twenty; the
resolution limit applies unchanged.

**Changes:** the enumeration is vectorised. Version 2 relied on
`partition_topology.partitions`, which builds a float64 matrix — 1.08 GB at
n = 26 and 4.49 GB at n = 28, which is why §5 declared n = 24 the ceiling. The
new form stores membership as packed booleans and accumulates the cut one edge
at a time:

```
cut = sum over edges (u,v) of  S[:, u] XOR S[:, v]
```

which needs 135 MB at n = 26 and 560 MB at n = 28.

**This is a new implementation of the ground truth, so it has to be verified
against the old one before it is trusted.** Required gate: on every size where
both run — n ∈ {10 … 24}, all 21 graphs — the vectorised minimum must equal the
`partition_topology` minimum exactly, and the partition count must match
C(n, n/2)/2. Any single mismatch voids this arm. A faster ground truth that
disagrees with the slow one is not a faster ground truth.

## 4 Scope, fixed now

- sizes n ∈ {26, 28}, density 1.5, so m = 39 and m = 42;
- the same seven families and three seeds — the same 21 graphs per size;
- n = 30 is **not** attempted. The probe of 10 November put it at 77,558,760
  partitions and 2.3 GB as packed booleans, and generating the index matrix
  alone would dominate the run. The ceiling for this arm is n = 28 and it is
  declared here rather than discovered during the run.

## 5 Abort conditions

The arm is abandoned, and reported as abandoned, if any of these occurs:

- the vectorised enumeration disagrees with `partition_topology` anywhere on
  n ≤ 24;
- the partition count does not match C(n, n/2)/2;
- a run exceeds the memory of this environment, in which case the size at which
  it failed is reported as the real ceiling;
- any heuristic returns an unbalanced partition outside the METIS arm.

## 6 What the two sizes can and cannot say

- **If METIS's unbalanced share keeps rising**, the article has a trend over
  five sizes and the finding is that the tool abandons the stated problem
  progressively as verification becomes impossible.
- **If it falls or wanders**, the honest statement is that the share is not
  monotonic over the measured range and that 8 of 21 at n = 22 is the worst
  observed case, not a point on a curve. That is a weaker article and it is the
  one that gets written.
- **Neither** says anything about n > 28. The horizon moves by two sizes; it
  does not go away.
