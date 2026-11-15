# Addendum 2 to design_resolution_limit_EN.md

**15 November 2026.** Version 2 of the note and addendum 1 are left standing
unedited. This addendum records the first re-evaluation of the warm-start
comparison on data the repository can reproduce, and supersedes the entry
addendum 1 made for it.

Why it was needed: `design_cut_degeneracy_EN_addendum_4.md`. The figures the
reproduction gate held for that comparison came from a version of
`cut_degeneracy_warmstart.py` that was never committed. They have been
replaced by the committed version's, and the re-evaluation below is the first
one whose inputs can be reproduced from this repository.

Printout: `calculations/resolution_limit_output.txt`, committed with this
addendum.

---

## 1 The gate passes

Both source datasets now reproduce at every size. The warm-start comparison
(registered in `design_cut_degeneracy_EN_addendum_1.md` A1.5, reported in
addendum 2 A2.3) re-evaluates as:

| n | units | warm | cold | d | T1 | 95% interval | verdict |
|---|---|---|---|---|---|---|---|
| 10 | 4 | 2.50 | 2.50 | +0.00 | no | — | not evaluable |
| 12 | 2 | 2.00 | 2.00 | +0.00 | no | — | not evaluable |
| 14 | 7 | 2.00 | 2.87 | +0.87 | no | — | bounded |
| 16 | 7 | 2.86 | 3.88 | +1.02 | no | — | bounded |
| 18 | 3 | 2.67 | 3.62 | +0.95 | no | — | not evaluable |
| 20 | 7 | 2.57 | 4.47 | +1.90 | no | [+0.55, +3.43] | unresolved |

## 2 What moved against the record of 5 November

Addendum 3 to `design_cut_degeneracy_EN.md`, section A3.4, recorded the
earlier re-evaluation as

> not evaluable at three, bounded at one, and below one granularity step at
> the two with enough units.

On reproducible data it is **not evaluable at three, bounded at two, and below
one granularity step at one.** The three sizes with too few units are the same
three — 10, 12 and 18. One size moved from unresolved to bounded: n = 16, where
both arms now lie within one granularity step of the shared floor of two
qubits, which they did not under the old figures.

**The statement that rests on it is unchanged.** Nothing in the warm-start
comparison resolves at any size, under either dataset. That was the point of
the entry in addendum 1, and it survives.

## 3 A1.2 is confirmed, including the correction

The diameter-against-realised comparison reproduces exactly and returns the
verdicts addendum 3 A3.1 reported: resolved at n = 14, 16, 18 and 20,
unresolved at n = 10 and 12. The one difference against A1.2 as published is
still n = 18, unresolved there and resolved here, with d = +2.72 and an
interval of [+2.06, +3.21].

That correction was never in doubt — the A1.2 dataset reproduced at every size
throughout — but it is now recorded with a committed printout behind it rather
than with literals alone.

## 4 One case worth naming: n = 20

At n = 20 the two tests disagree, and the printout says so rather than
averaging over it. The bootstrap interval is [+0.55, +3.43], which excludes
zero, so T2 passes: the sample localises the difference away from zero. T1
fails: the mean difference of +1.90 is below one granularity step of two
qubits.

Both are honest and neither overrides the other by accident. The order of the
checks was declared in section 4 of the note before any of this ran, and the
verdict it produces — *unresolved, below one granularity step* — says exactly
what happened: the difference is distinguishable from zero and smaller than
the smallest difference the quantity can take. A mean of an even-integer
quantity can sit between two attainable values, and reporting it as resolved
would read a step into the data that no single graph could have shown.

## 5 Status

This addendum supersedes the warm-start entry of addendum 1 and the A2.3
breakdown of `design_cut_degeneracy_EN_addendum_4.md` A4.4, which left it
pending. Nothing else in either note changes.
