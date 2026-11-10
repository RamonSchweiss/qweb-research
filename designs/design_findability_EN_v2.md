# Does the partitioner find the stable cut?

**Design note, version 2. Revised 10 November 2026, still before any run.**
Ramon Schweiss, QWeb © Research.

Version 1 was registered earlier today with two scope items open (its §11).
Both are now in hand — `calculations/partition_topology.py` and
`calculations/gate_vs_state_partition.py` — and reading them invalidates the
primary hypothesis of version 1. That is recorded here before anything has been
run, which is the only reason the registration was worth doing.

---

## 1 What version 1 got wrong, and why

Version 1 made H3 the hypothesis an article would rest on: *in at least some
graphs the heuristic's chosen partition leaves the optimal set at some layer
while the exact optimum does not move.*

**H3 is vacuous on the circuits the published claim was measured on.** In
`gate_vs_state_partition.py`, the gate layers of a QAOA circuit are built as

```python
return [list(edges) for _ in range(p)]
```

— every layer applies the same gates. Verified here directly: all 24 layers are
the identical edge list. So every layer's gate-interaction graph is the same
graph, and neither the exact optimum nor any heuristic has anything to move.
The same holds for the Trotter circuit in `partition_topology.py`, which also
applies one ZZ per edge per step.

The consequence for the published claim must be stated plainly, because it is
not a weakening by a critic but what the script itself says in its finding (1):
for QAOA, *"the gate cut does not move in 21 of 21 graphs"* is a property of the
circuit family, not an empirical finding about partition stability. The script
is explicit — the zero is *"a property of QAOA, not of the tool"* — and it
earned that by running memQ's windowed partitioner as a control, which keeps one
partition for all windows in 21 of 21 QAOA graphs and **does** repartition a
QFT.

So version 1's primary question was aimed at something that cannot vary. Had it
been run, it would have returned a clean, publishable-looking zero with no
content — the same failure mode as the vacuous OBJECTIVE registered in
`design_cut_degeneracy_EN.md` on 4 November, caught one step earlier this time.

## 2 The question, restated

**Primary, Q1: on the gate cut, does a real partitioner find the optimum?**

For QAOA the gate-interaction graph of a layer is the problem graph itself, so
the exact minimum gate cut is the graph's minimum balanced cut, and
`partition_topology.partitions` / `cut_costs` compute it by full enumeration.
Ground truth therefore exists, and the question is simply whether a partitioner
of the kind the DQC literature uses reaches it, and by how much it misses when
it does not.

This is the right objective and not a convenient one. Finding (3) of
`gate_vs_state_partition.py` establishes that following the
information-optimal cut costs **22 % more remote two-qubit gates per layer**
than the fixed gate cut — necessarily, since the gate cut is the minimum of
exactly that quantity. For a circuit known in advance, the gate cut is what
execution pays. Measuring findability on the information graph instead would be
measuring the wrong objective carefully, so that arm is **dropped**, with this
as the reason.

**Secondary, Q2: the layer dimension, where it exists.** Kept only as a control,
on a circuit whose layers differ. QFT is the available case, since memQ
repartitions it. If that control cannot be run, it is reported as not run.

## 3 Why this is not already answered — checked 10 November 2026

- **arXiv 2310.03942**, qubit and gate graph partitioning for DQC, applies
  **METIS** and reports no comparison against an exact optimum.
- **arXiv 2605.01974**, on the distortion of partitioning performance by random
  quantum circuits, comes closest: 6,508 circuits, k ∈ {2…10} QPUs, seven
  partitioners — random, greedy, stochastic greedy, Fiduccia–Mattheyses,
  KaHyPar, Zoltan PHG, evolutionary. But its results are **normalised against a
  random balanced assignment**, not against an optimum, and it runs no layer
  analysis.

One observation for the eventual article, dated here: a random balanced
assignment is a baseline against which every partitioner looks good. Choosing it
is a modelling decision of exactly the kind that moves a comparison point, and
it is not listed as a limitation.

## 4 The heuristic set, fixed in advance

Chosen to match what the DQC literature uses:

1. **Kernighan–Lin**, swap-based, balanced by construction, with restarts from
   random balanced starts.
2. **Spectral**, Fiedler vector of the Laplacian split at the median, balanced
   by construction. Deterministic, so one run.
3. **Greedy growth** and **stochastic greedy**, the same restart budget as KL.
4. **METIS**, via `pymetis`, which installed in this environment on
   10 November 2026.
5. **A random balanced assignment**, added to this list on 10 November 2026
   before the run, as a baseline rather than a heuristic. It affects none of the
   hypotheses in §8. The reason for adding it is §3: arXiv 2605.01974 normalises
   its results against exactly this, so measuring it against the same exact
   optimum says how flattering that baseline is. Without it, the observation in
   §3 would be an assertion.

Every arm reports its restart budget. A gap quoted without the budget is not a
measurement, because a gap is a property of the heuristic *and* of what it was
allowed to spend.

**METIS and the comparison class.** METIS does not guarantee an exactly balanced
bipartition; it works to an imbalance tolerance. An unbalanced cut is not
comparable to the balanced optimum — it can be smaller, because it is minimising
over a larger set. So METIS's balance is recorded with every result, and any
unbalanced answer is reported **outside the comparison class** rather than as a
negative gap. Quietly comparing the two would make METIS look better than the
optimum, which is a sign of a mismatched objective and not of a good
partitioner.

## 5 Ground truth and the capability horizon

Exact enumeration of every balanced bipartition. **No heuristic result is ever
used as the optimum** — an invalidating condition carried over from the orbit
note.

The horizon was measured on 10 November 2026 before version 1 was fixed, on a
graph family not used in the published work and with no heuristic involved:
naive enumeration is complete to n = 24 at about 38 s per graph; n = 26 needs a
vectorised form; n = 30 is out of reach here. `partition_topology.partitions`
caches its partition matrix, so the cache is cleared between sizes.

Declared: **exact ground truth to n = 24.** Nothing above is claimed.

## 6 Resolution limit

Every comparison passes `designs/design_resolution_limit_EN.md` version 2.

Granularity is exact and equals 1: a gate cut is an integer count of edges, so
the smallest nonzero gap is one remote gate. A gap of zero is therefore a true
zero and not a floor effect — the one place in this study where the granularity
test is trivially passed. The bootstrap arm still applies to any **mean** gap,
with the unit of analysis declared as the graph, u_min = 5, B = 2000, 95 %.
Bounds are declared per arm.

## 7 Declared degenerate subset

`gate_vs_state_partition.py` already records `ties`, the number of balanced cuts
sharing the minimum gate count. Where ties > 1 the optimum is a set, not a
point, and two consequences follow.

- A heuristic that returns *a different member of the optimal set* has not
  missed. It is reported as a hit, with the migration distance to the other
  members in the currency of `cut_degeneracy.py` — one ebit per qubit moved.
- Only a cut **cost** above the optimum counts as a miss.

Reporting these as one number would be the defect this note exists to prevent.

## 8 Registered hypotheses

- **H1.** At n = 10 the heuristic gap is zero in the large majority of the 21
  published graphs. *Stated as a hypothesis so that confirming it counts: if
  the gap is zero everywhere, this is a null and is published as one.*
- **H2.** The mean gap grows with n over n ∈ {10 … 24}.
- **H3′.** Replacing the vacuous H3: the QFT control shows a nonzero layer
  movement where QAOA shows none, so the 21-of-21 zero is a property of the
  circuit family and not of the partitioner. *This is already indicated by
  memQ's behaviour in the published script; the control re-establishes it inside
  this study or reports that it could not be run.*

## 9 Invalidating conditions

The run is void if any of these occurs:

- a heuristic result is used as the optimum anywhere;
- a reported partition is not balanced, except METIS results explicitly marked
  outside the comparison class. The defect of 4 November — stale A/B lists in a
  mutating sweep producing partitions with 2 of 10 qubits, and cuts below the
  balanced optimum, while reporting "0 of 21 misses" — is why the balance
  assertion is not optional;
- a gap is reported without its restart budget;
- a different member of the optimal set is counted as a miss;
- the layer question is reported for QAOA or Trotter as though it had been
  measured rather than being vacuous by construction.

## 10 Result-independent stopping condition

Fixed now and not to be changed by what the numbers show:

- the published configuration first: n = 10, m = 15, the seven families and
  three seeds of `gate_vs_state_partition.py` — the same 21 graphs;
- then the size sweep n ∈ {10, 12, 14, 16, 18, 20, 22, 24} at density 1.5, same
  families and seeds;
- restarts fixed at 20, as registered in `design_cut_degeneracy_EN.md` on
  4 November and not raised;
- the QFT control run once, or reported as not run.

The study stops there. No arm is extended because a result looked promising and
none is cut short because it looked dull.

## 11 What each outcome means

- **H1 confirmed and H2 confirmed.** The published 21-of-21 is safe at n = 10
  and the findability question has a size at which it starts to matter. That
  size is the article's contribution, because it tells the next person where
  exact ground truth stops being optional.
- **H1 refuted** — a gap already at n = 10 — is the strongest outcome and the
  most uncomfortable: it would mean the published claim describes a cut that a
  real partitioner does not reach, which the claim never asserted but a reader
  would assume.
- **H2 refuted.** Heuristics track the optimum over the whole reachable range,
  and the findability worry does not apply to graphs of this kind and size. A
  null, published as a null, with §5's horizon stated so the next person knows
  where the question becomes answerable again.
- **METIS outside the comparison class in most graphs.** Then the finding is
  about the objective rather than about the tool, and it belongs in the article
  as such: the partitioner the DQC literature reaches for first is not solving
  the balanced problem the cost model assumes.
