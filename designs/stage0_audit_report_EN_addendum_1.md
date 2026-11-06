# Addendum 1 to "Stage 0: the archival feasibility audit, carried out and reported"

**Date:** 6 November 2026.
**Status:** the report of 5 November is not altered; it stands as committed, with
its errors in it. Everything below is additional and dated, which is what its
own closing line requires.

**Occasioned by** Daniel Hug (qubit-lab.ch), who was sent the report on
5 November, checked three of its claims against the code and the archive, and
found two of them wrong.

**What changes:** two factual statements in the report, and the closing
observation of its section 8, which was the part most likely to be quoted.
**What does not change:** the four verdicts and the stopping decision.

---

## A1.1 Source 1: the `NotImplementedError` does not exist

**What the report said.** Section 2 gave two grounds for failing source 1. The
second was that `IBMBackend.properties(refresh, datetime)` raises
`NotImplementedError` when `datetime` is specified on IBM Quantum Compute, so
the documented route to historical calibration records does not return them. The
report noted that the platform guide says the opposite, declared the API
reference operative, and recorded the contradiction.

**What is actually the case.** Daniel reported that the call returns historical
calibrations on an ordinary IBM account, for `ibm_fez` back to November 2024,
and that he could not find the raise in the code. Checked against
`qiskit_ibm_runtime/ibm_backend.py` on `main`: the string
`NotImplementedError` occurs **exactly once in the whole file**, on line 359,
inside the docstring's `Raises:` section. There is no `raise NotImplementedError`
anywhere. The `datetime` branch validates the type, converts to UTC, and passes
straight through to `self._api_client.backend_properties(..., datetime=datetime)`
— and then carries an explicit `if datetime: # Don't cache result`, which is a
line written by someone who expected the historical path to work.

The docstring is stale. The API reference page the report cited is a rendering of
that docstring. **Historical calibration retrieval works.**

**What it does to the verdict: nothing.** Section 2's first ground stands
unaltered — source 1 supplies no experimental outcomes at all, so it yields no
matched pairs, and F1 still fails on its count. The stopping decision is
unchanged.

**What it does to the reasoning, which matters more.** Faced with a
documentation contradiction, the report declared the API reference operative and
congratulated itself: *"the contradiction is recorded rather than resolved in the
programme's favour."* That sentence was the mistake. A conservative reading is
not an accurate one, and the question was not which page to believe — it was what
the code does, which was available to read and was not read. The report had
access to the repository and used a rendered docstring instead.

The lesson is specific enough to be worth stating: **when documentation
contradicts itself about behaviour, the resolution is the implementation, not the
more cautious page.** Choosing caution over verification feels like rigour and
is not.

## A1.2 Source 2: the calibration timestamps are published after all

**What the report said.** Section 3 stated that the Zenodo dataset publishes no
timestamps, on the evidence of the documented field lists of `index.csv` and
`info.json`. Section 6 named the inside of `calibration.json` as the one open
check and said the environment could not reach zenodo.org.

**What is in the archive.** Daniel looked. `calibration.json` is the ordinary
`backend_properties` format, carrying `last_update_date` for the record **and a
date per measured property** — precisely the distinction section 2 of the design
note required the audit to record. So the *calibration* timestamp is published.

**The run timestamp is not.** No file carries an execution time, and the job
directories are anonymised.

**So section 3's summary sentence is wrong as written** — "the documented field
lists contain no date" was true of those two files and became "no published
timestamps," which overstates it. The correct statement: the calibration half of
each pair is timestamped, the run half is not.

**What it does to the verdicts: nothing.** A matched pair is defined in section 2
of the design note as requiring **both** timestamps. With the run time absent,
the count of matched pairs is still zero, F2 and F4 are unchanged, and F3 fails
on its third condition for reasons that have nothing to do with dates.

## A1.3 And the material for τ is in that archive

Daniel's unexpected finding, and the useful one. On `ibm_kingston` the 155
snapshots fall across **twelve distinct calibrations over about five weeks**.

The dataset was built so that each run sits beside the calibration current at
that moment, and the report treated that as the end of the matter. It is not:
with twelve calibrations spread over five weeks, cross-pairing a later run
against an earlier calibration would produce real leverage in τ. The only
missing piece is the run timestamp.

The README names the author as contact. That is a concrete and cheap route, and
it is named here rather than acted on, because adding a source to a frozen list
is not available and asking an author for a field is a Stage 1 move.

## A1.4 The late discovery, now checked rather than judged

Section 7 recorded the EPCL calibration record as a late discovery, not examined,
with the judgement that it did not appear to matter — written so that the
judgement could be disputed.

Daniel examined it and does not dispute it: it contains two
`backend_properties` files and no measurement results. The judgement is now a
check. The audit remains reported once, on the frozen list alone, and that is no
longer a matter of opinion.

## A1.5 The closing observation of section 8 was the real error

Section 8 ended with this:

> Nobody produces a dataset pairing runs with stale calibration as a by-product
> of other work; there is no reason to, unless calibration age is the question.

**That reasoning collapses once historical retrieval works, and A1.1 shows it
does.** Nobody has to pair anything. A published experiment needs only a dated
run, a transpiled circuit and shot-level outcomes; the calibration half of every
pair, at any age, can be fetched from the archive afterwards. The pairing is not
something an author must have intended — it is something a reader can construct.

This is Daniel's question, and the answer is yes.

**What it does not do is reopen Stage 0.** The frozen list holds three sources;
they fail, and they fail for reasons A1.1 and A1.2 leave standing. The list
cannot be extended after the freeze, and this addendum does not extend it.

**What it does is change the prognosis for a question stated afresh.** The report
implied that suitable material essentially does not exist because nobody would
produce it. The truer statement is narrower and more hopeful: suitable material
is any published dataset with a **run timestamp**, a transpiled circuit and
shot-level outcomes, on a backend whose history is still served. Whether such
datasets exist is an open question that this audit did not ask, because it was
asking about a frozen list of three.

## A1.6 The Stage 1 design, superseded

Section 8 proposed: one circuit family run repeatedly against a single frozen
calibration record over a widening interval. **Daniel's design is better and
replaces it.**

Run the circuit family once, at a known and recorded time. Then pair that one run
against a *ladder* of historical calibrations — one day old, one week, one month,
six months — fetched retroactively. τ varies while the run is held fixed, which
is the cleaner comparison, and no waiting is involved at all.

Two qualifications, both of which belong in whatever note registers it:

**One run gives one realisation per τ.** The prediction error at each age is then
confounded with the particular run. Several runs at different times, each with
its own ladder, are needed before τ can be separated from calendar time — the
same τ reached from different starting points.

**The ladder has a ceiling at the last hardware change.** Identifiability against
the declared model class needs the same qubits and the same coupling-map edges to
exist in both the calibration record and the run. A calibration from before a
relayout describes a device that is not the one that ran the circuit, and that
is a different failure from staleness. The ceiling is a property of each backend
and has to be found per backend, not assumed.

## A1.7 What stands

All four verdicts: F1 not met on a count, F2 not met with zero matched pairs, F3
not met on its third condition, F4 not met with no span in τ. The stopping
decision of section 6 of the design note, branch three: the published record on
the frozen list cannot carry the question, and that is the finding.

Two of the reasons given for those verdicts were wrong, and neither was
load-bearing. The report's own closing line asked for exactly this, and the
corrections come from the first external reader it was sent to.

---

**Source for A1.1:** `qiskit_ibm_runtime/ibm_backend.py`, `main` branch,
lines 333–386, retrieved 6 November 2026 —
https://github.com/Qiskit/qiskit-ibm-runtime/blob/main/qiskit_ibm_runtime/ibm_backend.py

**Source for A1.2, A1.3 and A1.4:** Daniel Hug, qubit-lab.ch, in correspondence,
6 November 2026, reporting an inspection of Zenodo record 20768087 and of Zenodo
record 22113018.
