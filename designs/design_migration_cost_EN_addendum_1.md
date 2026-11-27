# Addendum 1 to design_migration_cost_EN.md

**27 November 2026, before the run it governs.** The note of this morning is
left standing unedited. This addendum declares three things the note left to the
implementation, which is where the last study's trouble came from: a rule that
is decided while coding is a rule nobody registered.

---

## A1.1 Rule P needs a tolerance, and here it is

Rule P speaks of ties in the Fiedler vector "across the median". In exact
arithmetic a tie is an equality. In floating point it is a decision, and
whoever makes it chooses the incumbent.

**Declared: ε = 1e-9.** Two entries of the Fiedler vector count as tied when
they differ by at most 1e-9 in absolute value. The vector is normalised, so on
registers of twelve to twenty qubits its entries are of order 0.1 to 0.3 and
this is seven to eight orders of magnitude below them: far above the rounding
of a single `eigh` call and far below any separation that the graph itself
produces.

The tolerance cuts both ways and that is the point. Too small and genuine
symmetry is read as a strict ordering, which is how the previous study silently
took its incumbent from the vertex numbering. Too large and distinct splits are
pooled into a spurious tie, and the graph is then reported ambiguous when it was
not. Both failures are now at a declared number rather than at a default.

## A1.2 Rule P needs a ceiling, and here it is

Where many entries tie, the set *T* of consistent balanced splits can be large:
if every entry ties, *T* is every balanced bipartition, which at n = 20 is
92,378 and at larger registers worse. The rule as written would enumerate it.

**Declared: T_max = 200,000.** A graph whose *T* exceeds it is **ambiguous**
under rule P and is excluded and counted, with that reason named in the report.
The ceiling is above the whole enumeration at every size in this note, so on
this grid it can only be reached by a graph whose Fiedler vector is constant —
which rule E will almost always have excluded first. It is declared so that the
one case where it is not cannot be settled at the keyboard.

## A1.3 The relabelling gate has two outcomes, not one

Section 8 declares that a sampled relabelling which moves the incumbent **voids
the run**. Running the check revealed a case the sentence does not cover: under
a relabelling, rules E and P may pin nothing at all.

These are different events and they deserve different consequences.

- **The incumbent moves to a different partition.** The quantity is not a
  property of the graph. This is the registered condition, and it stands: the
  **run is void**.
- **Rules E or P no longer pin anything.** The rules disagree across
  labellings, which is the ambiguity they exist to report. The **graph** is
  ambiguous, excluded and counted; the run continues.

Reading the second as the first would void a run over a borderline graph that
the apparatus has already handled correctly, and would make the measurement
impossible for the symmetric families it is most interested in. Reading the
first as the second would be the far worse error: it would quietly keep a
quantity that is not a property of the graph, which is the whole defect
addendum 5 of `design_cut_degeneracy_EN.md` was written about. The line is
drawn here, in advance, and the run reports both counts separately.

The one-in-five bar of section 6 applies to the ambiguous total however it
arises: at any size where more than a fifth of the graphs are excluded as
ambiguous, the heuristic arm is **not evaluable** at that size.

## A1.4 What is not changed

No hypothesis, no size, no seed, no family, no restart count, no verdict rule,
no currency, and nothing in section 3 — which is the primary quantity and
touches none of this, because it has no incumbent, no eigensolver and no
tolerance in it at all.
