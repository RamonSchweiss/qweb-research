# Addendum 5 to design_cut_degeneracy_EN.md

**27 November 2026.** The note of 4 November and addenda 1, 2, 3 and 4 are left
standing unedited. This addendum withdraws the *diagnosis* of addendum 4,
establishes the real cause with a measurement that needs no second machine, and
suspends the one gate that cannot work until the cause is removed.

Evidence: `calculations/incumbent_wellposed.py` and its committed output,
both added with this addendum; the amended `calculations/resolution_limit.py`.

---

## A5.1 What the repair run found

Addendum 4 left a repair owed: re-run A2.3 against the committed code and
re-evaluate the breakdown of A3.4 on whatever comes back. That run was made
today, on a machine that has never held any version of this repository other
than the committed one.

**The committed `cut_degeneracy_warmstart.py` reproduces the figures of
4–5 November exactly.** Usable graphs 4, 6, 9, 13, 6, 9 — A2.1's table. Reach
rates 0.75, 0.50, 0.78, 0.77, 0.50, 0.89 — A2.2's table. Cost pairs 3, 3, 7,
10, 3, 8 with means 2.00/2.00, 2.00/2.00, 2.00/2.81, 2.60/4.07, 2.67/3.84,
2.50/4.19 — A2.3's table, to the last digit. Two consecutive runs are
byte-identical.

**The figures that do not reproduce today are the ones from 15 November** — the
set that A4.6 wrote into `PUBLISHED_A23` as "the committed code's figures", and
that `cut_degeneracy_warmstart_output.txt` holds. The reproduction gate fires
again, in the opposite direction.

## A5.2 A4.3's diagnosis is withdrawn

A4.3 concluded:

> The only explanation left: **the run of 4–5 November was made with code that
> changed before it was first committed.**

That cannot be right. The committed script produces those figures, here, twice,
on a machine where no uncommitted version has ever existed. The explanation was
the only one left of the four A4.2 examined, and the list was short by one.

A4.2 is not reproached for this. It checked environment, code, random stream and
replay **on one machine**, correctly, and found all four innocent there. The
fifth possibility — that the quantity itself is not determined by the graph —
cannot be seen from a single machine at all. It took a second one to make it
visible and a third kind of check to prove it.

## A5.3 What it actually is, measured

`cut_degeneracy_warmstart.measure()` takes the incumbent from
`findability_scoping.spectral(W)`: the Laplacian's Fiedler vector from
`numpy.linalg.eigh`, split at the median with
`np.argsort(f, kind="stable")`. Two things in that line are decided by
something other than the graph.

**The tie-break in the sort.** Where the Fiedler vector has equal entries
either side of the median, a stable sort orders them by **vertex index**. The
split is then a function of the order the vertices were written down in. On the
registered grid that happens on **8 of 126 graphs**.

**The choice inside a near-degenerate eigenspace.** Where the second and third
Laplacian eigenvalues are numerically indistinguishable, `eigh` returns an
arbitrary member of the subspace, and which one is a LAPACK detail that moves
with the library. On this grid no gap is exactly zero; **4 of 126** are below
1e-8.

The direct test needs neither a second machine nor a second library: **permute
the vertices, run `spectral()` on the permuted graph, map the answer back.** A
partition that is a property of the graph cannot change. It changes on
**11 of the 126 graphs** — eight from the sort, three from the eigenspace:

      family        incumbent moves under relabelling
      regular                      6 of 18
      grid                         4 of 18
      scale-free                   1 of 18
      random, ring, path, community    0

The two symmetric families supply ten of the eleven, which is what symmetry does
to a Laplacian spectrum and to a Fiedler vector's entries alike.

## A5.4 How far it reaches

A1.5 defines the declared degenerate subset by whether the incumbent is already
optimal. The incumbent moves, so the subset moves, so the usable set moves, so
every figure computed on it moves — row counts and both means, at four of six
sizes, which is exactly the shape A4.1 recorded.

This does not make any of those figures *wrong*. It makes them properties of a
machine and a vertex numbering rather than of the graphs they are supposed to
describe, which is worse, because a wrong figure can be corrected and this one
cannot be quoted at all.

## A5.5 Two repairs

1. **The A2.3 gate is suspended.** `PUBLISHED_A23` is set to `None`, with both
   observed sets kept beside it in a comment and the reason stated. Holding
   either set would assert that one of them is the reproducible one, and
   neither is. The re-evaluation of A2.3 is reported as **not evaluable** at
   every size, with the reason printed — not because the sample is small, but
   because the object it is measured from is not well defined.
2. **`incumbent_wellposed.py` and its printout are committed together**, as the
   declaration of A4.6 requires.

The A1.2 gate is untouched and still passes: that dataset uses random starts and
no eigensolver. Its re-evaluation returns exactly the verdicts of A3.1,
including the n = 18 correction from unresolved to resolved.

## A5.6 What stands

**The withdrawal of A2.2**, which is the substantive conclusion of the strand.
It rests on the warm route reaching the optimum less often than the cold one at
n = 12: 0.50 against 0.65 here, 0.40 against 0.66 on 15 November. Both
environments, same verdict.

**The A1.2 dataset, A3.1's correction, the exact degeneracy enumeration of
section 1, A1.1's narrower claim at five of six sizes, A1.3 and A1.4.** None of
them passes through `spectral()`.

**A4's own finding**, which is not the diagnosis but the declaration: a figure
that exists only as a literal inside a checking script cannot be checked. That
stands, and is why this addendum commits a printout alongside its code.

Nothing published on the site is affected. Nothing from this note has been
published, and the keystone article says of this strand only that the
experiment is specified and not yet run — which, after today, is more exactly
true than when it was written.

## A5.7 What the next registration must contain

The cost question still has no registration of its own; A2.3 said so and it is
still true. Whatever registers it must first make the object it measures from
well defined:

- **A pinned incumbent.** The selection inside the eigenspace and the tie-break
  at the median are both declared, or the incumbent is taken from a rule that
  does not have ties to break. Declared before the run, like every other rule
  in this note.
- **A relabelling gate as an invalidating condition**, in the form section 5 of
  the note already uses for balance: a run in which a sampled relabelling
  changes the incumbent is **void**, not merely different. The check is cheap —
  eight permutations per graph, seconds for the whole grid.

## A5.8 The count, and the declaration

A2.5 counted four findings about this note's own instruments and none about
partitioning. Addendum 4 added a fifth. This is the sixth, and it is the first
that was invisible to every check the apparatus had, because all of them ask
whether a measurement can answer its question and none of them asks whether the
thing being measured is a property of the object at all.

> A measurement is only as well defined as the objects it starts from. Before a
> quantity is registered, the starting points must be invariant under the
> relabellings the problem itself is invariant under — and a run that cannot
> demonstrate that is void rather than different. A library call is not a
> definition.
