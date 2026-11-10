# Does the partitioner find the stable cut? — report

**10 November 2026. Ramon Schweiss, QWeb © Research.**
Protocol: `designs/design_findability_EN_v2.md`, registered before this run.
Measurement: `calculations/findability.py`.

---

## The short answer

**Findability is not a problem for the published claim.** A partitioner of the
kind the DQC literature uses reaches the exact minimum balanced gate cut in all
21 published graphs, and at every size up to n = 24 — at a budget of twenty
restarts. The worry the merker raised was legitimate, and the answer is no, with
the budget stated, because the budget is where the answer lives.

Two findings came out that were not the question, and one of them is the more
useful result.

---

## 1 The published configuration, n = 10, m = 15, the same 21 graphs

| arm | hits | different member of the optimal set | misses | worst gap | mean gap |
|---|---|---|---|---|---|
| Kernighan–Lin | 21/21 | 5 | 0 | 0 | 0.00 |
| stochastic greedy | 21/21 | 6 | 0 | 0 | 0.00 |
| METIS | 21/21 | 0 | 0 | 0 | 0.00 |
| spectral | 17/21 | 4 | 4 | 2 | 0.24 |
| greedy growth | 10/21 | 1 | 11 | 4 | 0.95 |
| random balanced | 1/21 | 1 | 20 | 8 | 4.33 |

Optimal set size: 1 to 8, median 1. Gaps are counts of remote two-qubit gates,
so granularity is exactly 1 and a zero is a true zero rather than a floor
effect.

**H1 — "the gap is zero in the large majority at n = 10" — is confirmed for
Kernighan–Lin, stochastic greedy and METIS, and refuted for spectral and
greedy growth.** Spectral's mean gap of 0.24 has a bootstrap interval of
0.05–0.48 and greedy's 0.95 an interval of 0.52–1.48, so both are resolved
nonzero, not unresolved.

The "different member" column is the degenerate-subset rule of §7 doing its
work. Kernighan–Lin returned a *different* member of the optimal set in 5 of 21
graphs. Those are hits — the cut cost is optimal — but the partition is not the
same one, which matters for migration cost and not at all for the cut. Counted
as misses, they would have produced a 16-of-21 result and a wrong conclusion.

## 2 The size sweep, density 1.5, mean gap in remote gates

| n | KL | spectral | greedy | stoch. greedy | METIS | random |
|---|---|---|---|---|---|---|
| 10 | 0.00 | 0.24 | 0.95 | 0.00 | 0.00 | 4.57 |
| 12 | 0.00 | 0.33 | 1.52 | 0.00 | 0.05 | 6.19 |
| 14 | 0.00 | 0.62 | 1.57 | 0.29 | 0.00 | 7.05 |
| 16 | 0.00 | 1.29 | 1.76 | 0.19 | 0.00 | 7.76 |
| 18 | 0.00 | 0.48 | 2.19 | 0.52 | 0.00 | 9.57 |
| 20 | 0.00 | 0.71 | 2.38 | 0.38 | 0.00 ᵇ | 10.33 |
| 22 | 0.00 | 1.24 | 3.10 | 0.67 | 0.00 ᵇ | 12.29 |
| 24 | 0.00 | 1.10 | 2.48 | 0.86 | 0.00 ᵇ | 14.24 |

ᵇ some METIS answer was not balanced — see §4.

**H2 — "the mean gap grows with n" — is refuted for Kernighan–Lin and METIS and
confirmed for the other three.** Kernighan–Lin is at exactly zero over the whole
reachable range. Spectral goes 0.24 → 1.10, greedy 0.95 → 2.48, stochastic
greedy 0.00 → 0.86, all resolved nonzero at n = 24.

## 3 Why this null is worth anything — and the budget

A null from an instrument that never detects anything is indistinguishable from
a broken instrument. This one has a positive control it was not designed to
have: **the same machinery, on the same graphs, resolved nonzero gaps in three
other arms.** Spectral, greedy and random all produce resolved misses, so the
Kernighan–Lin zero is a measurement and not an absence of measurement.

That was not registered as a control and is recorded here as luck rather than
design.

**Measured after the registered run, prompted by the result and therefore
post-hoc:** with **one** restart instead of twenty, Kernighan–Lin misses the
optimum in **2 of 21 graphs at n = 18**. So the zero in §2 is a property of the
budget, not of the algorithm. §4 of the protocol said a gap is a property of the
heuristic *and* what it was allowed to spend; this is that sentence with a number
behind it. Any use of the §2 table has to carry "at twenty restarts" with it.

A bookkeeping check was run before any of this was believed: `cut()` agrees with
the enumeration it is compared against on every tested partition, and every
Kernighan–Lin answer was located in the enumerated set at exactly its reported
cost. Zero mismatches. The orbit script failed on precisely this kind of
mismatch on 5 November, which is why the check exists.

## 4 METIS leaves the balanced class — the more useful finding

> **Revised 10 November 2026 by addendum 1.** The last paragraph of this section
> said METIS "stops solving the stated problem". The extension to n = 26 and
> n = 28 shows that is too strong: every unbalanced answer at every size is off
> by **exactly one vertex**, and the share does not grow with n — 0.24, 0.38,
> 0.19, 0.45, 0.10. Read §4 together with
> `findability_report_addendum_1.md`, which carries the corrected statement.

| n | unbalanced in | smaller side |
|---|---|---|
| 10–18 | 0 of 21 | — |
| 20 | 5 of 21 | 9 |
| 22 | 8 of 21 | 10 |
| 24 | 4 of 21 | 11 |

METIS works to an imbalance tolerance rather than to exact balance. From n = 20
it starts returning partitions that are not balanced bipartitions at all, in up
to 8 of 21 graphs.

Those answers are excluded from the gap column rather than reported as negative
gaps, because an unbalanced cut minimises over a larger set and can be smaller
than the balanced optimum. Comparing the two would have made METIS look better
than the optimum, which is a sign of a mismatched objective and not of a good
partitioner.

The substantive point is not about the tool. The two-QPU cost model assumes two
processors of equal size, so a 10/12 split is not a cheaper answer to the
question — it is an answer to a different question, about hardware nobody said
they had. **The partitioner the DQC literature reaches for first stops solving
the stated problem at exactly the sizes where exact ground truth runs out.** That
is a bad place for an instrument to change its objective quietly, because past
n ≈ 26 nobody can check it by enumeration.

## 5 How flattering is a random balanced baseline?

| n | optimum | random balanced | random excess |
|---|---|---|---|
| 10 | 3.86 | 8.43 | +119 % |
| 12 | 4.00 | 10.19 | +155 % |
| 14 | 4.33 | 11.38 | +163 % |
| 16 | 4.81 | 12.57 | +161 % |
| 18 | 4.62 | 14.19 | +207 % |
| 20 | 5.10 | 15.43 | +203 % |
| 22 | 5.00 | 17.29 | +246 % |
| 24 | 5.33 | 19.57 | +267 % |

arXiv 2605.01974 evaluates seven partitioners — random, greedy, stochastic
greedy, Fiduccia–Mattheyses, KaHyPar, Zoltan PHG and an evolutionary
algorithm — across 6,508 circuits, and normalises all of it against a random
balanced assignment.

On these graphs that baseline sits 119 % to 267 % above the optimum. So a
partitioner measured against it has between twice and nearly four times the room
it would have against the optimum. And the headroom **grows with n**: a result
that reports improving performance with size, measured this way, is partly
reporting the baseline getting worse.

This is not a criticism of that paper's measurements, which are not what this
measured. It is the observation that the choice of reference point is a
modelling decision, and that this one is not listed among its limitations.

## 6 H3′ — the layer question, and the reproduction

The published script reproduces exactly in this environment:

- changes of the exact minimum gate cut over 24 layers, all 21 graphs: **0**;
- memQ's windowed partitioner: one partition for all windows in **21 of 21**
  QAOA graphs;
- control, QFT n = 10, windows of 5 gates: **3 distinct partitions, 2 changes
  over 11 windows**;
- following the information-optimal cut costs **+22 %** remote ZZ gates, and
  the fixed gate cut averages 3.86 per layer — the same 3.86 this study measures
  as the mean optimum at n = 10.

**H3′ is confirmed.** The QAOA zero is a property of the circuit family: the
same partitioner that never moves on QAOA repartitions a QFT twice. So the
published "21 of 21" is correct and is not a stability measurement, exactly as
the script already said in its finding (1).

## 7 What this does not settle

- **Nothing above n = 24.** Exact ground truth stops there in this environment,
  and §4 shows METIS changing behaviour at n = 20, which is the worst possible
  place for the check to end.
- **The layer question with a heuristic.** Only memQ's partition count was
  measured on QFT, not a per-layer heuristic gap. On QAOA the question is
  vacuous by construction, which is why version 1 of the protocol was wrong.
- **One density and two QPUs.** All of this is at 1.5 edges per qubit and k = 2.
- **The choice within the optimal set does vary** — 5 of 21 for KL — and this
  study says nothing about what that costs a scheduler. `cut_degeneracy.py`
  measures that quantity; the two have not been put together.
- **Seven families and three seeds is 21 graphs**, not a survey of graphs. The
  community family is built with the fewest bridges that keep it connected,
  which is the most favourable case for a clean cut, and it is the family where
  every arm succeeds.
