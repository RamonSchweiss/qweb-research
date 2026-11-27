# Addendum 2 to design_migration_cost_EN.md

**27 November 2026, after the run.** The note and addendum 1 are left standing
unedited. This addendum records what the registered run returned, and declares
one of its own hypotheses mis-specified.

Store and printout: `calculations/migration_cost_store.json`,
`calculations/migration_cost_output.txt`, both committed with the code that
produced them.

---

## A2.1 The grid held, and the pinning worked

350 graphs, five sizes, seven families, ten seeds. No invalidating condition
fired. In particular **the relabelling gate never reported a moved incumbent**:
on every graph that rules E and P pinned, twenty seeded permutations returned
the same partition. That is the repair of addendum 5 of
`design_cut_degeneracy_EN.md` working as intended.

      n     graphs   D=1   D>1   ambiguous   incumbent optimal   usable (sec 4)
      12       70     42    28       3              48               19
      14       70     28    42       5              40               25
      16       70     33    37      10              32               28
      18       70     36    34       2              46               22
      20       70     23    47       5              40               25

25 of 350 graphs were ambiguous — 13 under rule P because the minimum-cut split
was not unique, 12 under rule E because the eigenvector was not determined. The
highest share at any size is 10 of 70 at n = 16, which is below the one-in-five
bar of section 6, so the heuristic arm stayed evaluable everywhere.

Worth recording beside it: **the share of graphs with a unique optimum falls as
the register grows**, from 42 of 70 at n = 12 to 23 of 70 at n = 20. Degeneracy
is not a curiosity of small registers.

## A2.2 H1 holds, and it is the number the ledger was missing

**M is at least one granularity step on every single graph with D > 1, at every
size.** Not on half of them, which is what was registered — on all 188 of them.

      n      graphs with D>1    M >= 2    median M    max M
      12            28           28/28       3.33      4.67
      14            42           42/42       3.33      6.00
      16            37           37/37       4.71      8.00
      18            34           34/34       3.83      6.67
      20            47           47/47       4.35      6.67

So the migration line of the ledger has a figure: **a re-solve that does not
prefer the assignment already in place costs a median of three to five ebits at
twelve to twenty qubits, and never less than one swap.** Against zero for an
incumbent-preferring tie-break, which is arithmetic and was declared as
arithmetic before the run.

## A2.3 H2 is unresolved, and the two tests disagree on purpose

Median *M* rises from 3.33 at n = 12 to 4.35 at n = 20, a difference of +1.02
with a 95 per cent interval of [+0.40, +2.33].

The interval excludes zero. The difference is **below one granularity step**.
T2 passes, T1 fails, and the registered rule calls that **unresolved** rather
than support. It is the right call and it is worth stating why: half an ebit is
not a thing anyone can pay. The direction is there in every intermediate size
as well, and a larger grid may well resolve it. This run does not.

## A2.4 H3 is mis-specified, and is therefore not evaluable

H3 asked whether the ordering of the families by *M* is the same at every size.
The run says the ordering moves, and that answer carries no information,
because the hypothesis has no resolution rule in it.

On the three families that qualify at every size, the whole spread of the
medians is:

      n=12   ring 3.60 > regular 2.70 > random 2.67      spread 0.93
      n=14   ring 4.00 > regular 3.64 > random 3.47      spread 0.53
      n=16   ring 4.67 > regular 4.53 > random 3.71      spread 0.96
      n=18   ring 4.00 > random 3.67 > regular 3.62      spread 0.38
      n=20   random 4.25 > regular 4.00 > ring 4.00      spread 0.25

Every spread is below the granularity step of 2 that section 2 of the note
declares for this currency. The ordering that "moves" at n = 18 and n = 20
moves by 0.05 and 0.25 ebits. At the resolution of the currency these families
have the same *M*, and asking which is larger is asking a question the unit
cannot answer.

**Two defects, not one.** First, H3 compares an ordering without requiring that
the ordering be resolvable; the resolution rule of section 7 is applied to every
other quantity in the note and not to this one. Second, the note says "the four
families that contribute at least five graphs" without saying what to do when
that set differs between sizes — it did differ, five, six, five, four and six
families, with only three common to all. Both were visible in the note before
the run and neither was caught.

H3 is reported as **not evaluable**, and the printed "FAILS" of section 4 of the
run is superseded by this paragraph. No replacement hypothesis is registered
here from the same data; whether *M* depends on the family is a question for a
grid designed to resolve differences of this size, and that is a separate
registration.

This is the fourth mis-specified registered item in this programme in three
weeks, and the first in a note written specifically to avoid the previous one's
faults. It was written this morning. The pattern holds: the errors are in the
scaffolding, not in the measurements, and pre-registration does not remove them
— it fixes the date on which they become visible.

## A2.5 H4 and H5 point the same way and neither resolves

      n     units   warm   cold      d        95% interval      verdict
      12      19    3.05   3.47   +0.42    [+0.00, +0.95]    unresolved
      14      25    3.36   3.76   +0.40    [-0.08, +0.96]    unresolved
      16      28    3.79   4.36   +0.57    [-0.29, +1.36]    unresolved
      18      22    4.09   4.27   +0.18    [-0.64, +1.09]    unresolved
      20      25    2.88   4.16   +1.28    [+0.56, +2.08]    unresolved

H5, conditioned as A2.3 of the earlier note was, runs from +0.62 to +1.52 and
is unresolved at every size too. The warm route is cheaper in direction at all
five sizes in both readings, and the difference never reaches one swap.

That the conditioned comparison is consistently larger than the unconditioned
one is what a selection effect looks like: conditioning on both routes reaching
the optimum removes the cases where the warm route owes a further migration,
and those are the expensive ones. A2.3 of the earlier note reported only the
conditioned figure. It would have been reporting the flattering half.

## A2.6 What stands, in one line each

- **H1 holds**, on all 188 graphs with a degenerate optimum. The ledger has its
  figure: three to five ebits per re-solve, never below two.
- **H2 unresolved**: direction yes, resolution no.
- **H3 not evaluable**, and mis-specified, as recorded above.
- **H4 and H5 unresolved** at every size, same direction throughout.
- **The pinned incumbent held** under every sampled relabelling, which is the
  one thing in this note that had already failed once.
