# Design note: re-checking a published gap claim

**Date:** 7 November 2026. Version 1, registered before any searching.

**What is under test.** Section 11 of "What the Computation Knows About Its Own
Organisation" states, live on the site:

> Among the systems we examined, we found no explicit plan-expiry criterion of
> this form. Existing systems include time-aware and adaptive partitioning
> approaches — memQ's compiler, Cisco's prototype, the time-aware partitioners
> in the literature — but among those we examined we found no explicit criterion
> whose primary role is to decide whether an available reorganisation is worth
> paying for. That is a gap.

**Why it needs re-checking, and the reason is not merely that time has passed.**
The literature survey behind that sentence was carried out on 18 September 2026.
It was run against the question as it then stood: how much global *state*
information a planner needs and how fast that information goes stale. The
article subsequently narrowed the claim to something else — a criterion whose
primary role is to decide whether an *available* reorganisation is worth its
price. **The survey was never run against the claim it is now supporting.**

That the claim has also had seven weeks to be overtaken is a second and lesser
reason.

**Why this is registered rather than just done.** "No such work exists" is a
verdict, and a literature search is the instrument that produces it. An
instrument that returns nothing is indistinguishable from an instrument that
cannot find anything, unless it is shown to be capable of finding something.
Section 4 is where that is dealt with, and it is the part of this note that
matters.

---

## 1 The claim, made precise before searching

A **hit** is a published system, method or criterion that satisfies all four:

1. It operates on the **partition** of a computation across processors or
   modules — which qubits sit where — and not merely on the scheduling of
   entanglement, the routing of gates, or the allocation of network resources.
2. It decides **whether to reorganise**, not where to reorganise to. A method
   that computes a better partition is not a hit; a method that decides whether
   an available better partition is worth adopting is.
3. That decision is its **primary role**, not a by-product of a cost model or a
   threshold buried in a heuristic.
4. It is **explicit** — stated as a criterion a reader could implement, rather
   than inferred from the behaviour of a system.

A **near miss** satisfies 1 and 2 but not 3 or 4, or satisfies 2, 3 and 4 at a
different level of the stack (network scheduling, entanglement distribution,
memory management). Near misses are recorded with the reason, and a run that
produces only near misses leaves the claim standing but narrows it further.

Everything else is a **miss** and is not listed.

## 2 Declared degenerate subset

Work that uses the vocabulary for a different object, which this field's
terminology makes common:

- "Partitioning" of datasets, feature spaces or training batches in quantum
  machine learning.
- "Staleness" in the sense of cache coherence, gradient staleness in distributed
  training, or data freshness in streaming systems.
- "Expiry" of entanglement due to decoherence, which is a physical lifetime and
  not a planning criterion.

These are excluded by definition, before the search, rather than discarded by
judgement afterwards.

## 3 Sources, queries and window

**Sources.** arXiv (quant-ph, cs.DC, cs.ET), and general web search for
conference and journal material not on arXiv. **Declared limitation:** Scopus,
Web of Science and IEEE Xplore are not reachable from this environment, so this
is not an exhaustive database survey and the report will say so in those words.

**Queries**, fixed now and not added to after results are seen:

1. distributed quantum computing dynamic repartitioning criterion
2. quantum circuit partition when to repartition cost of migration
3. quantum program partition expiry criterion stale
4. distributed quantum compiler repartition threshold decide
5. qubit allocation reorganisation worth the cost distributed quantum
6. plan expiry criterion quantum scheduler staleness

**Window.** Two arms, both run.

- *Broad arm:* no date limit. The published claim is unqualified in time, so the
  whole field is in scope, and this is the arm that tests the claim as written.
- *New arm:* 18 September 2026 to 7 November 2026, to catch what the earlier
  survey could not have seen.

**Screening depth.** The first 20 results per query, judged on title and
abstract, then full text for anything not clearly a miss. Fixed now.

## 4 The positive control, which decides whether a null result means anything

A search returning nothing is worthless unless the protocol can be shown to
return something. Two items are named **now**, before searching, as controls.
Both are known to exist and both should be found:

- **arXiv 2307.06009**, "A Linear Algebraic Framework for Dynamic Scheduling
  Over Memory-Equipped Quantum Networks", which explicitly treats the stale
  information problem and proposes a partially informed scheduler. Expected
  classification: **near miss** — it is at network level, not at the level of
  the computation's partition.
- **arXiv 2302.00267**, InQuIR, whose outlook names the limitation that the
  approach assumes static planning and that dynamic replanning may be needed on
  real hardware. Expected classification: **near miss** — it names the gap
  rather than filling it.

**If the protocol fails to surface both, the run is void** and is reported as
void, not as a null result. A protocol that cannot find two papers known in
advance to be findable has not tested anything.

Their expected classifications are also written down now, so that the
classification rules of section 1 are tested on known cases before being applied
to unknown ones.

## 5 Declared invalidating conditions

- **The controls are not found.** The run is void (section 4).
- **A query is added, reworded or extended after results are seen.** The search
  then describes what was looked for after looking, and the report says so.
- **A hit is reclassified as a near miss, or a near miss as a miss, by
  reference to the claim's survival rather than to section 1.** Classification
  follows the written rules; where a case is genuinely ambiguous it is recorded
  as ambiguous and the claim is reported as unresolved for it.

## 6 Result-independent stopping condition

The six queries, in both arms, to the declared screening depth. No query is
added to settle a borderline case, and the search does not continue because
nothing has been found yet. When the list is exhausted, the run ends, whatever
it has or has not produced.

## 7 What each outcome means, decided now

**No hits, controls found.** The claim stands, and gains something it does not
currently have: a date and a stated protocol. The article's sentence can then
carry "re-checked on 7 November 2026 against the protocol in
`designs/design_gap_claim_recheck_EN.md`" rather than ageing silently.

**One or more hits.** The claim is wrong as published and the article needs a
dated addendum naming the work. The programme also gains a reference it should
have been citing, which is a better outcome than being right.

**Near misses only.** The claim stands but is narrowed by whatever the near
misses do cover, and the narrowing is written into the addendum. This is the
likeliest outcome on the evidence of the September survey and is not treated as
a disappointment.

**Controls not found.** Void. Reported as a failure of the instrument, and the
claim remains as it is — neither supported nor refuted by a run that could not
have refuted it.

## 8 What this does not do

It does not establish that no such criterion exists. It establishes what a
declared protocol, run against declared databases on a declared date, did and
did not find. The difference between those two statements is the whole point of
writing this down first.
