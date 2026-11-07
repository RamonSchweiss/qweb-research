# Design note: re-checking a published gap claim — version 2

**Date:** 7 November 2026, registered after run 1 was declared void and before
any further searching.
**Supersedes:** version 1 of the same date for the purpose of future runs.
Version 1 is not altered and its run-1 report stands as committed.

**What carries over unchanged from version 1:** the claim under test (section
11 of "What the Computation Knows About Its Own Organisation"), the four-part
definition of a hit, the near-miss and miss definitions, the declared degenerate
subset, and the invalidating conditions. Those worked. Section 1 of the run-1
report confirms the classification rules were correct on both known cases.

**What failed and is replaced:** retrieval. The six queries were built from the
vocabulary of the claim and could not surface work that uses the vocabulary of
the fields the claim distinguishes itself from.

---

## 1 Three arms instead of one

**Arm A — the claim's own vocabulary.** The six queries of version 1, unchanged
and re-run. They are the direct test of the claim as written and they are kept
verbatim so that run 1 and run 2 are comparable on that arm.

**Arm B — the adjacent vocabulary, where the controls live.** New, and the
repair:

1. entanglement distribution scheduling outdated information quantum network
2. distributed quantum program runtime replanning node failure
3. intermediate representation distributed quantum static scheduling dynamic
4. quantum network scheduler partial information expected values
5. resource orchestration distributed quantum processors reconfiguration

**Arm C — the classical analogue.** Also new, and the arm that could change the
article rather than merely confirm it. The criterion the claim says is missing —
decide whether an *available* reorganisation is worth its cost — is a long-standing
question in classical distributed systems. If it exists there and has simply not
been carried over, the article's framing is wrong in an interesting way: not "no
one has this" but "this is standard elsewhere and nobody has brought it across".

6. process migration threshold when migration is not worth the cost
7. dynamic load balancing hysteresis rebalancing decision criterion
8. data rebalancing threshold distributed storage when to rebalance

**Arm C hits are not hits against the claim**, which is about the quantum
literature. They are recorded separately and reported as context. Mixing them
into the verdict would be answering a different question than the one asked.

## 2 Citation chasing, declared as part of the instrument

Keyword search alone demonstrably misses the controls. In addition to the three
arms:

- backward citations of both controls, screened by title;
- forward citations of both controls, screened by title;
- backward and forward citations of the time-aware partitioning work surfaced in
  run 1 (arXiv 2603.04126 and arXiv 2507.11707).

Screening depth: titles for all, abstracts for anything not clearly a miss, full
text for anything surviving that. Fixed now.

## 3 Date stratification

Run 1 returned almost nothing before 2024 while both controls are from 2023.
Each arm is therefore run twice: unrestricted, and restricted to material
published before January 2024. A protocol that cannot see the older literature
cannot test a claim about a field that began before 2024.

## 4 Controls, now of two kinds

**Retrieval controls — can the protocol find things?**

Both from version 1, unchanged, with their expected classifications confirmed
correct in run 1:

- arXiv 2307.06009, Fittipaldi, Giovanidis and Grosshans — expected **near
  miss**, network level.
- arXiv 2302.00267, InQuIR, Nishio and Wakizaka — expected **near miss**, names
  the gap rather than filling it.

**Both must be surfaced by arm B or by citation chasing.** If not, run 2 is void
on the same terms as run 1, and the repair failed.

**Classification control — can the rules say yes?**

Run 1 tested the rules only on near misses, so it never established that they
can recognise a hit. Naming a real expected hit is not possible: if one were
known, the claim would already be refuted. A constructed case is used instead,
written down now and classified before any searching:

> A distributed quantum compiler that, at each checkpoint, computes the current
> gate-optimal partition, compares its communication cost against the incumbent
> partition's, prices the qubit migrations required to move between them, and
> adopts the new partition only when the saving exceeds the migration cost by a
> stated margin. The margin and its justification are given in the paper.

**This is declared a HIT** under section 1 of version 1: it operates on the
partition (1), decides whether rather than where (2), that decision is its
primary role (3), and it is explicit enough to implement (4).

During classification, this case is passed through the rules alongside the real
candidates. If the rules do not return "hit" for it, the rules are defective and
the run is void for that reason instead.

## 5 Stopping condition, result-independent

Eight queries across three arms, each in two date strata, plus the declared
citation chasing, to the declared screening depths. Nothing is added because
nothing has been found. The run ends when the list is exhausted.

## 6 What each outcome means, decided now

Unchanged from version 1 for arms A and B: no hits with controls found means the
claim stands and gains a date; one or more hits means the article needs a dated
addendum naming the work; near misses only means the claim stands and narrows.

**New, for arm C.** If the criterion exists in classical distributed systems,
the claim in section 11 survives as written — it is a claim about quantum
systems — but the article's surrounding framing does not, and the addendum says
so. "Nobody has built this" and "this is routine one field over and nobody has
carried it across" are different statements, and the second is more useful to a
reader and less flattering to us.

**Void, again.** If the retrieval controls are still missed, the diagnosis in
the run-1 report was wrong and a third version would need a different theory of
why, not more queries.

## 7 What this still does not do

Scopus, Web of Science and IEEE Xplore remain unreachable from this environment.
This is not an exhaustive database survey and no report of it will be written as
though it were.
