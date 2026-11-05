# Stage 0: the archival feasibility audit, carried out and reported

**Date:** 5 November 2026.
**Governed by:** `designs/design_stage0_archival_audit_EN.md`, version 5, in
force since 4 November 2026. This report is the deliverable of its section 9.
**Authors:** Ramon Schweiss and Venkateswaran Ramamurthy.

**The finding, first.** None of the four feasibility criteria is met. F1 fails on
a count that no further examination of the listed sources can change. By the
stopping decision of section 6 of the note, the published record on the frozen
source list cannot carry the calibration-age question, and that is the result of
Stage 0 rather than a failure of it.

One check remains open and is named in section 5 below. It cannot change the
stopping decision, and the reason it cannot is stated there rather than asserted.

---

## 1 The dates, as the note requires them

| Event | Date |
|---|---|
| Note version 1, before any archive was searched | 21 October 2026 |
| Exploratory reconnaissance reported by V. Ramamurthy | 24 October 2026 |
| Note version 2, 3, 4 | 24, 25, 30 October 2026 |
| Freeze agreed and executed; note in force | 4 November 2026 |
| This audit | 5 November 2026 |

**The frozen source list**, closed on 4 November 2026 on the three leads of
section 2.5 and nothing else:

1. IBM Quantum's documented historical backend properties and downloadable
   calibration data.
2. The 2026 Zenodo dataset of raw repetition-code experiments on three IBM
   processors.
3. The published analysis of historical IBM backend properties for long-term
   dependability.

**Publication window:** 1 January 2019 to 4 November 2026.

## 2 Source 1 — IBM Quantum historical backend properties

**Identified as:** `qiskit-ibm-runtime`'s `IBMBackend.properties()` and the
calibration-data download on IBM Quantum Platform.

**What the documentation says.** `properties(refresh=False, datetime=None)`
documents the `datetime` argument as returning the `BackendProperties` "whose
timestamp is closest to, but older than, the specified datetime". The platform
guide states that historical backend properties can be retrieved this way. That
is why the lead looked viable.

**What the same documentation also says.** The API reference for the method
states that it raises `NotImplementedError` **if `datetime` is specified when
IBM Quantum Compute is used**. On the current platform the documented route to
historical calibration records therefore does not return them.

The two pages contradict each other. The API reference is the operative one, and
the contradiction is recorded here rather than resolved in the programme's
favour.

**The timestamp distinction the note asks for.** `BackendProperties` carries a
`last_update_date` for the record as a whole, and `qubit_property` and
`gate_property` each return "the value and the time it was measured". So the
distinction between a calibration *update* timestamp and individual property
*benchmark* timestamps, which section 2 of the note requires the audit to record,
does exist in the data model. It is recorded here, and it was not usable, for the
reason above.

**What this source contains and does not contain.** Calibration records, current
ones, downloadable as CSV from a QPU's information card without a paid plan.
**No experimental outcomes of any kind.** It is a calibration source, not a
source of paired material.

**Verdict: fails.** Two reasons, each sufficient. It supplies no experimental
runs, so it yields no matched pairs as section 2 defines them. And the historical
half of the lead is unavailable on the current platform by the API's own
statement.

## 3 Source 2 — the Zenodo repetition-code dataset

**Identified as:** Zenodo record 20768087, DOI 10.5281/zenodo.20768087,
"Calibration-Conditioned FiLM Decoders for Low-Latency Decoding of Quantum Error
Correction Evaluated on IBM Repetition-Code Experiments — Datasets", S. Stein,
Pacific Northwest National Laboratory. CC BY 4.0, 145.7 MB, no login.

**What it contains**, from the record page and `DESCRIPTION.txt`:

- 352 hardware snapshots on **ibm_kingston, ibm_pittsburgh and ibm_fez**,
  code distances d = 3, 5, 7, 9, 11, syndrome rounds r = 1 to 11, X and Z
  logical bases, several chains in parallel per snapshot.
- `bitstrings.json` — raw per-shot measurement records, "exactly as returned by
  the hardware".
- `circuit_state0.qasm`, `circuit_state1.qasm` — the transpiled circuits as
  executed.
- `calibration.json` — T1, T2, gate and readout error rates, coupling map, "the
  device calibration snapshot at execution time".
- `index.csv` fields: `path, backend, d, rounds, basis, logical_states,
  n_chains, shots`.
- `info.json` fields: `device, d, rounds, basis, states, shots, n_chains`.

**This is the strongest source on the list, and it fails on two things.**

**No published timestamps.** Neither documented field list contains a date or
time. The record states no period over which the 352 snapshots were collected.
τ is defined in section 2 as the interval between two timestamps; with neither
timestamp recoverable from the published description, τ cannot be computed and
the snapshots are not matched pairs as defined. Whether the archive itself
carries timestamps inside `calibration.json` is the open check of section 5.

**Calibration captured at execution time, by design.** Even granting timestamps,
each snapshot pairs a run with the calibration current at that moment, so the
native calibration age of every pair is approximately zero. The dataset was
built for calibration-conditioned decoding, where τ ≈ 0 is the point. Leverage
in τ could only come from **cross-pairing** — the outcomes of a later snapshot
against the calibration of an earlier one on the same backend — and that
requires exactly the timestamps the published description does not provide.

**Verdict: fails F1's timestamp clause, and therefore F2 and F4.** It passes the
first two conditions of F3 and fails the third, for the reason in section 4.

## 4 Source 3 — the dependability analysis

**A defect in the freeze, recorded before the verdict.** Section 2.5 records this
lead as a description — "published work analysing historical IBM backend
properties for long-term dependability" — and not as a citation. The audit
therefore had to decide what it refers to, and that decision was made after the
freeze. That is a real weakness in the freeze and it is recorded rather than
smoothed over.

**It happens not to matter, and that is lucky rather than good practice.** The
two works the description can plausibly denote are S. Dasgupta and T. Humble,
"Stability of Noisy Quantum Computing Devices" (arXiv:2105.09472) and "Impact of
unreliable devices on stability of quantum computations" (arXiv:2307.06833).
Both were examined.

**2105.09472.** Calibration records for *yorktown* from about March 2019 to
December 2020, 673 records; hardware runs on *toronto* on 11 December 2020. Raw
readouts are described as 1000×27 binary matrices but are not released. Results
are reported as histograms, Hellinger distances and means with spread. No
transpiled circuits. No data availability statement or repository for the
authors' own data. The toronto runs are not described as paired with calibration
records at specific timestamps.

**2307.06833.** Calibration records for *washington*, 1 January 2022 to 30 April
2023, aggregated **by month**. Outcome data is summary statistics only. No
transpiled circuits. The "experimental" verification is Qiskit simulation driven
by Monte Carlo samples from the monthly densities — no hardware execution
results are reported. No data availability statement.

**Verdict: fails, on either referent.** Neither releases outcome data, neither
provides transpiled circuits, and neither pairs outcomes with calibration records
at individual timestamps. The verdict does not depend on which work the lead
meant, which removes the consequence of the ambiguity without excusing it.

## 5 The four criteria, answered against their bars

**F1 — accessibility. NOT MET.**

Bar: at least **two** independent sources of paired material, publicly
accessible without an institutional login, machine-readable, with timestamps on
both the calibration record and the experimental run.

Count of sources on the frozen list that supply paired material at all: **one**
(source 2). Source 1 supplies no experimental outcomes; source 3 releases no
data. Against a bar of two, the list reaches one, and the timestamp clause then
fails on that one as well.

**This is the finding that no further examination can overturn**, and it is why
the open check below cannot change the outcome. Even if the Zenodo archive turns
out to carry timestamps throughout, the frozen list still holds one source of
paired material and not two. Adding a second would mean adding a source, which
section 5 of the note forbids after the freeze.

**F2 — matchability. NOT MET.**

Bar: at least **30** matched pairs over at least **two** backends, with at least
one **comparison set** of at least **15**.

Matched pairs identified: **zero**. Not for want of material — source 2 has 352
snapshots over three backends, far above the raw counts — but because a matched
pair requires both timestamps to be recoverable from the published material and
neither is. The raw counts would be ample; the definition is not satisfied.

**F3 — the fresh-fit arm. NOT MET.**

Bar: for at least **20** matched pairs, all three conditions present.

- Condition 1, outcome data at shot or per-circuit-distribution level:
  **present** in source 2, `bitstrings.json`, unprocessed.
- Condition 2, the circuit as executed after transpilation: **present** in
  source 2, as OpenQASM.
- Condition 3, enough distinct circuits within one comparison set to identify
  the **declared model class**: **absent**.

Condition 3 is the one the note said would bite, and it does. The declared class
carries a rate per qubit, a rate per **coupling-map edge**, and a readout rate
per qubit, for the backend concerned. A repetition code exercises a line
subgraph: CX gates along a chain of 2d−1 data and ancilla qubits, with
measurement on the ancillae. On a 127-qubit or larger device, several parallel
chains still touch a small, linear part of the coupling map and leave the
remaining edges untouched by any gate.

Such a record identifies a **smaller class** — Pauli rates on the chain's qubits
and edges, and readout on those qubits. Section 2 of the note states exactly what
to do here: record that it identifies the smaller class and count the pair as
failing F3, rather than lowering the class to fit the record. That is done.

Varying d, r and the logical basis adds circuits but not coverage: it lengthens
and repeats the same linear structure rather than probing a different part of
the device.

**F4 — leverage in τ. NOT MET.**

Bar: within at least one comparison set, τ spans at least **one order of
magnitude**, with at least **five** matched pairs in each of at least **three**
age bins, and at least **three repeats** from distinct experimental runs.

Observed span of τ: **none measurable, and approximately zero by construction**.
Source 2 captures calibration at execution time for every snapshot. There is no
comparison set, because there are no matched pairs, and there would be no span
even if there were. Age bins were not computed; the rule of section 2 derives
them mechanically from an observed range, and no range exists.

## 6 The open check, and why it does not change the decision

**What is open.** Whether `calibration.json` inside the Zenodo archive carries a
`last_update_date` or per-property benchmark times, and whether any file records
when each snapshot was executed. The published description lists neither, but a
description is not the archive. The three files that would settle it are
`README.md` and the per-job `calibration.json` and `info.json` inside the three
`.tar.gz` archives.

**Why it was not closed here.** The sandbox this audit ran in cannot reach
zenodo.org; the request is refused at the proxy. The check needs a download
outside it.

**What it could change.** If the timestamps are there, source 2 becomes a source
of matched pairs, F2's counts become reachable by cross-pairing, and F4 becomes
an open question rather than a settled no. F3 would still fail on condition 3,
for a reason that has nothing to do with timestamps.

**What it cannot change.** F1 requires two independent sources of paired
material. The frozen list contains one. That is arithmetic, not evidence, and no
file inside the archive bears on it.

**Therefore the stopping decision below stands either way**, and the check is
worth doing for the record and for Stage 1's benefit rather than to settle
Stage 0.

## 7 Late discoveries, recorded and not used

Section 5 of the note requires that a source found during the audit be recorded
as a late discovery and not join the list, and that the audit be reported twice
if it appears to matter.

**One candidate appeared.** Zenodo record 22113018, "IBM Berlin Device
Calibration Data for Error Per Circuit Layer (EPCL) Experiments", surfaced in the
search that located source 2. It has **not** been examined and is **not** on the
list.

**It does not appear to matter**, on the face of it and for a reason independent
of its contents: a second source would have to supply paired material with
timestamps to move F1 from one to two, and F3's condition 3 would still have to
be met by a circuit family that probes per-edge structure. Being a calibration
dataset by title, it is more likely to resemble source 1 than source 2.

Because it does not appear to matter, the audit is reported once, on the frozen
list alone. That judgement is recorded here so that it can be disputed. If anyone
holds that it does matter, the remedy named by the note is to report the audit
twice, and this paragraph is where that disagreement starts.

## 8 The stopping decision

Section 6 of the note fixed three branches before the search. The third applies:

> **F1 or F2 not met:** the archive cannot carry the question. That is the
> finding, it is published as such, and the programme either seeks device time
> for a question stated afresh or is set down.

F1 and F2 are both not met. The published record on the frozen source list
cannot carry a measurement of whether the age of a noise model contributes
measurable predictive error.

**What this does not say.** It does not say that calibration age has no effect.
It does not say the effect is small. Stage 0 never asked that; it asked whether
the published record could be used to find out, and the answer is no. Nothing
about drift has been measured, confirmed or refuted here.

**What follows, as the note's own words put it:** a demanding criterion that the
archive fails is not a problem with the criterion, it is the finding. The
programme now either states the question afresh and seeks device time for it, or
is set down. That decision belongs to both authors and is not taken in this
document.

**One observation for whoever states it afresh.** The reason the strongest source
on the list fails is instructive rather than accidental. A dataset built for
calibration-conditioned decoding captures calibration at execution time, because
τ ≈ 0 is what its own question needs. Datasets that pair runs with *stale*
calibration are not a by-product of other work; nobody has a reason to build one
unless calibration age is the question. If Stage 1 seeks device time, the
cheapest design is probably not a new experiment but a schedule: the same circuit
family run repeatedly against one frozen calibration record over a widening
interval, with the circuit family chosen so that it probes per-edge structure
rather than a line.

---

**If this report contradicts a later text, the report is wrong and should be
corrected in a dated addendum, not quietly.** That is section 9 of the note, and
it applies to this document as much as to any other.

## Sources examined

- IBM Quantum, `IBMBackend` API reference (`properties`, `target_history`):
  https://quantum.cloud.ibm.com/docs/en/api/qiskit-ibm-runtime/ibm-backend
- IBM Quantum, "View backend details":
  https://quantum.cloud.ibm.com/docs/en/guides/qpu-information
- IBM Quantum, `BackendProperties` model reference:
  https://quantum.cloud.ibm.com/docs/en/api/qiskit-ibm-runtime/models-backend-properties
- S. Stein, Zenodo record 20768087 (dataset and `DESCRIPTION.txt`):
  https://zenodo.org/records/20768087
- S. Dasgupta and T. Humble, "Stability of Noisy Quantum Computing Devices":
  https://arxiv.org/pdf/2105.09472
- S. Dasgupta and T. Humble, "Impact of unreliable devices on stability of
  quantum computations": https://arxiv.org/pdf/2307.06833
- Recorded as a late discovery, not examined, not on the list: Zenodo record
  22113018, https://zenodo.org/records/22113018
