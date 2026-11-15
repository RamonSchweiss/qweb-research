# Addendum 4 to design_cut_degeneracy_EN.md

**15 November 2026.** The note of 4 November and addenda 1, 2 and 3 are left
standing unedited. This addendum records that the warm-start figures of A2.3
cannot be reproduced from the repository, establishes why, and says which
later statements rest on them.

Evidence: `calculations/cut_degeneracy_warmstart_output.txt`, committed with
this addendum, and the reproduction gate in `calculations/resolution_limit.py`.

---

## A4.1 What fired

`resolution_limit.py` recomputes both of its source datasets and checks them
against the figures those runs printed, before re-evaluating anything. On
15 November that gate fired on **all six sizes** of the A2.3 warm-start
dataset. The A1.2 dataset reproduced exactly at every size.

| n | held in the gate | produced by the committed code |
|---|---|---|
| 10 | 3 rows, 2.00 / 2.00 | 4 rows, 2.50 / 2.50 |
| 12 | 3 rows, 2.00 / 2.00 | 2 rows, 2.00 / 2.00 |
| 14 | 7 rows, 2.00 / 2.81 | 7 rows, 2.00 / 2.87 |
| 16 | 10 rows, 2.60 / 4.07 | 7 rows, 2.86 / 3.88 |
| 18 | 3 rows, 2.67 / 3.84 | 3 rows, 2.67 / 3.62 |
| 20 | 8 rows, 2.50 / 4.19 | 7 rows, 2.57 / 4.47 |

The columns are (warm, cold) mean migration cost over the usable pairs. The
right-hand column is reproducible three ways: running
`cut_degeneracy_warmstart.py` on its own, replaying it through
`resolution_limit.py`, and doing either twice.

## A4.2 What it is not

Four explanations were checked and eliminated, in this order.

**Not the environment.** Same machine, same Python, numpy and scipy as the
original run, with no updates in between.

**Not the code.** `cut_degeneracy_warmstart.py`, `findability_scoping.py` and
`cut_degeneracy.py` each show one commit in their history — the one that
created them. Nothing was edited after 5 November.

**Not an uncontrolled random stream.** Two consecutive runs produced
byte-identical output. An unseeded stream would have wandered.

**Not the replay.** `resolution_limit.dataset_a23()` loops `for n` →
`for family` → `for seed`, which is `cut_degeneracy_warmstart.main()` line for
line, with the same seed, and the two filters match. Run on its own the script
produces the same six rows the replay produces.

## A4.3 What it is

The only explanation left: **the run of 4–5 November was made with code that
changed before it was first committed.** The repository never held the version
that produced those figures, which is why no file history shows anything. The
change happened before the first commit, where history cannot reach.

One detail supports it. Of the six row counts the gate held, two — 10 at
n = 16 and 8 at n = 20 — are the **usable** counts from section 1 of that
script's printout rather than the **pairs** counts from section 3. Two match
section 3. Two match neither column. The figures were assembled partly from
the wrong column and partly from a run that no longer exists.

## A4.4 How far it reaches

Further than the table. Addendum 3, section A3.4, records that A2.3's cost
table was re-evaluated under the new resolution limit and

> resolves nothing at any size: not evaluable at three, bounded at one, and
> below one granularity step at the two with enough units.

That re-evaluation ran on 5 November, which means the gate passed then — on
the figures above, left column. So **that breakdown, and the corresponding
entry in addendum 1 to `design_resolution_limit_EN.md`, rest on data the
repository cannot reproduce.** Both are superseded pending a re-run against
the committed figures. This addendum does not predict what that re-run
returns; the row counts and both means move at four of six sizes, and three of
those sizes have fewer than the five units the rule needs, so the breakdown
can shift.

## A4.5 What stands

**The withdrawal of the registered objective.** A1.5 withdraws it outright if
the warm route reaches the optimum less often than the cold route at any size.
On the committed code that happens at n = 12, warm 0.40 against cold 0.66. The
ground is unchanged and so is the withdrawal — which is the substantive
conclusion of the whole strand.

**Addendum 3's own finding.** A3.1 corrects A1.2's n = 18 verdict from
unresolved to resolved. That rests on the A1.2 dataset, which reproduces
exactly at every size. It is untouched by any of this.

**A1.1, A1.3, A1.4, A2.2 and the exact degeneracy enumeration**, as addendum 3
already lists under A3.4.

## A4.6 Three repairs, and a declaration

1. `calculations/cut_degeneracy_warmstart_output.txt` is committed. Until
   today these figures existed only as literals inside the script that checks
   them — a claim, where this repository promises a calculation.
2. `PUBLISHED_A23` in `resolution_limit.py` is set to the committed code's
   figures, with the superseded values kept beside them in a comment rather
   than deleted.
3. This addendum, dated, with every earlier text untouched.

And the declaration this episode adds to the four of
`design_resolution_limit_EN.md` §7 and the positive control that case 8 of
"What a Verdict Assumes" added:

> A run whose figures will later be checked must commit its printout at the
> same time as the code that produced it. A figure that exists only as a
> literal inside a checking script cannot be checked. It can only be agreed
> with.

The gate was right, and nothing else in the apparatus would have caught this.
Granularity, bounds, unit of analysis, minimum units and the positive control
all ask whether a measurement can answer its question. This was a gap between
a run and the record of the run, and only a reproduction check looks there.
