# Gap-claim re-check, run 2

**Date:** 7 November 2026.
**Governed by:** `designs/design_gap_claim_recheck_EN_v2.md`, registered the same
day after run 1 was declared void and before any further searching.

**Outcome.** The run is valid: both retrieval controls were surfaced, each as
the first result of a dedicated arm-B query, and the classification control
returns a hit as required.

**The claim of section 11 stands.** Arms A and B produced no hit. It is a claim
about the quantum literature and nothing found there contradicts it.

**The framing around the claim does not stand.** Arm C found the criterion, in
another field, with its own horizon concept, surveyed as routine. The article
says "That is a gap". The accurate statement is that it is a gap *in the quantum
literature* and not a gap in computing, and the article should name the work it
has been independently rediscovering.

---

## 1 Controls

**Retrieval.** Both found, and the run-1 diagnosis is confirmed: the controls
live in the adjacent vocabulary, not the claim's.

- arXiv 2302.00267, InQuIR — first result of arm-B query 3.
- arXiv 2307.06009, Fittipaldi, Giovanidis and Grosshans — first result of
  arm-B query 4.

Both classify as **near miss**, exactly as predicted before searching.

**Classification.** The constructed case of section 4 of version 2 — a compiler
that prices the migrations between incumbent and candidate partitions and adopts
the candidate only when the saving exceeds that price by a stated margin —
passes the four conditions of section 1 and returns **hit**. The rules can say
yes. Run 1 never established that.

## 2 Arms A and B: no hits

Classified in full:

- **arXiv 2605.11088**, "Tolerating Device Failure in Distributed Quantum
  Computing". Partition level, and it does reassign qubits across devices after
  a node failure. But there is no decision rule, threshold or cost comparison
  for whether a reassignment is worth its cost — swap-out is described as an
  infrequent operation and failures are handled automatically once detected.
  Satisfies condition 1 and not condition 2. **Miss.**
- **arXiv 2307.06009**. Names the stale information problem directly in section
  IV-D and proposes a Partially Informed Quadratic Scheduler that substitutes
  expected values for unavailable quantities. Network level: entanglement
  scheduling, backlogs, link losses. **Near miss.**
- **arXiv 2302.00267**. States that the representation assumes static
  scheduling and that dynamic rescheduling may be needed on failure or rising
  error rates. Names the gap, does not fill it. **Near miss.**

Screened on title and abstract and not pursued further, as misses on condition
1 or 2: the entanglement-request scheduling literature, the job- and
resource-scheduling work for multi-QPU systems, the time-aware partitioners, and
the orchestration frameworks. They compute placements or schedule entanglement;
none of them decides whether an available reorganisation is worth adopting.

## 3 Arm C: the criterion exists, one field over

**arXiv 2203.03501**, "To Migrate or not to Migrate: An Analysis of Operator
Migration in Distributed Stream Processing". A survey with a conceptual model
and an empirical study on Apache Flink and Siddhi.

Its section 4.2 gives a formal cost–benefit test:

- **Amortization time** — the horizon over which a placement is expected to
  remain good, and explicitly longer when the placement score is more stable.
- **Migration cost** — predicted output lost during downtime, as a fraction of
  the output expected over that amortization time.
- **Migration benefit** — the candidate host's placement score multiplied by one
  minus that cost.
- **Selection** — the highest penalised benefit wins, and the incumbent carries
  zero cost, so a move happens only when a candidate beats staying put.

That is the criterion section 11 of our article says is missing. It is in
another domain, so under section 1 of the protocol it is **not a hit against the
claim**, which is about quantum systems. Under section 6 of version 2 it is the
arm-C outcome that changes the article's framing.

**And the parallel is closer than a coincidence of topic.** The amortization
time is a horizon over which an organisation is expected to stay worth keeping,
and it lengthens with the stability of the placement. Our viability horizon is a
horizon over which an organisation stays within a tolerance, and it depends on
the structure of the interaction graph. The cost-penalised benefit is the
article's triggered planner: let the expiry decide when, let the structure
decide where. The article arrived at that shape from quantum measurements, and
distributed stream processing had it already.

Arm C also shows the decision is routine rather than exotic in that field:
threshold and periodic re-evaluation rules are described as the common practice
the survey is formalising, and the surrounding literature on migration
scheduling and placement cost models is substantial.

## 4 A shortfall against the registered protocol, and its direction

Section 2 of version 2 declared backward and forward citation chasing from both
controls and from the time-aware partitioning work. **That was performed only in
part**, by keyword proxy rather than by walking a citation graph, because no
citation-graph tool is reachable from this environment.

This is a deviation and is recorded as one. Its direction matters: incomplete
citation chasing can only cause work to be **missed**, never to be falsely
found. So it cannot have manufactured the arm-C finding, and it does weaken the
null result of arms A and B. **The claim's survival in this run is therefore
weaker evidence than a complete run would have given**, and the addendum should
say so rather than quote the result flat.

The limits of section 7 of version 2 also stand: Scopus, Web of Science and IEEE
Xplore are unreachable, so this is not an exhaustive database survey.

## 5 What should happen to the article

Section 11 currently reads, in part: "among those we examined we found no
explicit criterion whose primary role is to decide whether an available
reorganisation is worth paying for. That is a gap."

A dated addendum should record three things:

1. The claim was re-checked on 7 November 2026 against a registered protocol,
   after a first run was declared void by its own control, and no quantum work
   contradicting it was found.
2. The criterion exists in distributed stream processing, with
   arXiv 2203.03501 as the reference, including an amortization-time horizon
   that plays the role our viability horizon plays. The gap is in the quantum
   literature, not in computing.
3. The re-check's own limits: partial citation chasing, no subscription
   databases, screening depths as registered.

**This is a better position than the one the article is in now.** A reader from
stream processing would have found the omission unaided, and finding it
ourselves and citing it converts an oversight into a cross-field observation.
Whether it is written that way is for both authors: section 11 is in a
co-authored article and this is the joint strand.

## 6 What was not established

That no quantum criterion of this form exists. What was established is that a
registered protocol, with its retrieval sensitivity demonstrated on two controls
and its classification rules demonstrated on a constructed hit, run against the
declared sources on 7 November 2026, found none — with the shortfall of section
4 counted against that finding.
