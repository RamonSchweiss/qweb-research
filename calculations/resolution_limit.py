"""
A resolution limit that works, applied to the two comparisons that broke the
last one.

Belongs to designs/design_resolution_limit_EN.md, version 2, registered
5 November 2026 before this ran. Nothing here was chosen after seeing output:
the granularity, the bounds, the unit of analysis, B, the level and u_min are
all in section 2 and section 4 of that note.

What broke. On 4 November a resolution limit was written into
design_cut_degeneracy_EN.md section 6 as "the mean within-family range of the
measured figure across the three graph seeds". On 5 November it came out
undefined at three of six sizes, because most families held fewer than two
usable graphs, and 0.00 at two more, because the measured quantity sat on its
floor of one swap. A quantity with no room to vary has no spread, and a
precision estimate built from its spread reports perfect precision for the
wrong reason.

What replaces it. Two limits instead of one, because sampling resolution and
instrument granularity are different things with different causes:

  T1  granularity : |d| >= g, where g is the smallest nonzero difference the
                    quantity can take BY DEFINITION. For migration cost between
                    two balanced bipartitions, g = 2: the count of qubits that
                    change side is even, so one swap is the smallest step.
                    Declared, never estimated from a sample.
  T2  sampling    : a percentile bootstrap interval for d, resampling the
                    DECLARED UNIT with replacement, excludes zero. B = 2000,
                    95 per cent, two-sided. The unit is the graph, because the
                    claims generalise over graphs. The failed version took
                    families as the unit and graphs as replicates inside them,
                    which is why it died when the usable set shrank.

Both must pass for a difference to be RESOLVED. Two further verdicts the failed
version did not have:

  BOUNDED       : both arms within one step of the SAME bound, so the
                  difference has no room to be anything but small. T2 is not
                  quoted.
  NOT EVALUABLE : fewer than u_min = 5 units. Kept strictly apart from
                  UNRESOLVED: unresolved means the data spoke and said the
                  difference is small, not evaluable means they did not speak.

Applied to : the warm-start comparison of addendum 2 section A2.3, and the
             diameter-against-realised comparison of addendum 1 section A1.2.
             Both are existing datasets; this is a re-evaluation under a
             declared rule and not a new measurement.

Pipeline   : both datasets are recomputed here rather than parsed from the old
             printouts, so each module's RNG is re-seeded and its loop order
             reproduced. Figures printed on 4 and 5 November are hard-coded
             below and checked. A mismatch aborts: a re-evaluation of numbers
             that have not been reproduced is worth nothing.

Needs      : numpy, scipy, partition_topology, cut_degeneracy,
             cut_degeneracy_warmstart, findability_scoping.
Runtime    : a few minutes, dominated by recomputing the two datasets.
"""
import sys

import numpy as np

import cut_degeneracy as cd
import cut_degeneracy_warmstart as ws

SIZES = cd.SIZES
FAMILIES = cd.FAMILIES
SEEDS = cd.SEEDS

# --- the rule's constants, from sections 2 and 4 of the note -----------------
G_MIGRATION = 2.0          # qubits that change side is even; one swap is a step
U_MIN = 5                  # units below which nothing is evaluable
B = 2000                   # bootstrap resamples
LEVEL = 0.95               # two-sided percentile interval
BOOT_RNG = np.random.default_rng(20261105)

# --- what the two runs printed, checked before anything is re-evaluated ------
PUBLISHED_A23 = {14: (7, 2.00, 2.81), 16: (10, 2.60, 4.07),
                 18: (3, 2.67, 3.84), 20: (8, 2.50, 4.19),
                 10: (3, 2.00, 2.00), 12: (3, 2.00, 2.00)}
# Order is (units, arm a, arm b) as the dataset functions return them, which for
# A1.2 is (realised, diameter) and NOT the printed column order of A1.2's table.
# The first version of this line held the printed order, the reproduction check
# fired on all six sizes with the means swapped, and the row counts matching
# exactly is what showed the data were fine and the bookkeeping was not.
PUBLISHED_A12 = {10: (9, 1.69, 2.89), 12: (9, 2.32, 4.00),
                 14: (12, 2.42, 4.67), 16: (15, 3.15, 6.53),
                 18: (10, 3.28, 6.00), 20: (12, 3.73, 7.50)}


# ------------------------------------------------------------------- the rule

def verdict(a, b, g, bounds, u_min=U_MIN, b_reps=B, level=LEVEL):
    """Compare two arms, unit by unit. a and b are equal-length per-unit arrays.

    Returns (verdict, d, ci_low, ci_high, t1, note). The order of the checks is
    the order declared in section 4: no data first, then a difference with no
    room to exist, then the granularity test, then the sampling test.
    """
    a, b = np.asarray(a, float), np.asarray(b, float)
    n = len(a)
    if n != len(b):
        raise AssertionError("arms must be paired unit by unit")
    d = float(np.mean(b - a))
    t1 = abs(d) >= g

    if n < u_min:
        return "not evaluable", d, None, None, t1, f"{n} units < {u_min}"

    # Bounds are declared PER ARM, because two arms of one comparison need not
    # be the same quantity. Version 2 of the note declared one pair for both
    # datasets: floor 2, correct for a migration between two distinct
    # partitions, wrong for a MEAN pairwise distance within a set, which is 0
    # when every run returns the same partition. That misdeclaration produced a
    # spurious "bounded" at n=10 in the first run of this script, and it is
    # recorded in addendum 1 to the note rather than quietly fixed.
    #
    # A comparison is bounded only where the DIFFERENCE has no room: both arms
    # within one step of a bound they SHARE.
    (alo, ahi), (blo, bhi) = bounds
    ma, mb = float(np.mean(a)), float(np.mean(b))
    for name, ba, bb in (("floor", alo, blo), ("ceiling", ahi, bhi)):
        if ba == bb and abs(ma - ba) < g and abs(mb - bb) < g:
            return ("bounded", d, None, None, t1,
                    f"both arms within one step of the shared {name}")

    idx = BOOT_RNG.integers(0, n, size=(b_reps, n))
    boots = (b[idx] - a[idx]).mean(axis=1)
    alpha = (1.0 - level) / 2.0
    clo, chi = (float(np.quantile(boots, alpha)),
                float(np.quantile(boots, 1.0 - alpha)))
    t2 = not (clo <= 0.0 <= chi)

    if t1 and t2:
        return "resolved", d, clo, chi, t1, ""
    if not t1 and t2:
        return "unresolved", d, clo, chi, t1, "below one granularity step"
    if t1 and not t2:
        return "unresolved", d, clo, chi, t1, "interval includes zero"
    return "unresolved", d, clo, chi, t1, "fails both tests"


# ----------------------------------------------------------- the two datasets

def dataset_a23():
    """Addendum 2, A2.3: warm against cold migration cost, per usable graph."""
    ws.RNG = np.random.default_rng(20261105)      # reproduce the run's stream
    out = {}
    for n in SIZES:
        rows = []
        for f in FAMILIES:
            for sd in SEEDS:
                r = ws.measure(n, f, sd)
                if r is None or r["degenerate"]:
                    continue
                if r["warm_hits"] and r["cold_cost"] is not None:
                    rows.append((r["warm_cost"], r["cold_cost"]))
        out[n] = rows
    return out


def dataset_a12():
    """Addendum 1, A1.2: diameter against realised distance, per graph D > 1."""
    cd.RNG = np.random.default_rng(20261104)      # reproduce the run's stream
    out = {}
    for n in SIZES:
        rows = []
        for f in FAMILIES:
            for sd in SEEDS:
                r = cd.measure(n, f, sd)
                if r is None or r["D"] <= 1 or r["realised"] is None:
                    continue
                rows.append((r["realised"], r["diam"]))
        out[n] = rows
    return out


def check(name, rows_by_n, published):
    """Reproduce the printed figures before re-evaluating anything."""
    bad = []
    for n, rows in rows_by_n.items():
        if n not in published:
            continue
        cnt, m_first, m_second = published[n]
        if not rows:
            bad.append((n, "no rows"))
            continue
        a = float(np.mean([r[0] for r in rows]))
        b = float(np.mean([r[1] for r in rows]))
        if (len(rows) != cnt or abs(a - m_first) > 0.005
                or abs(b - m_second) > 0.005):
            bad.append((n, f"{len(rows)} rows, {a:.2f} / {b:.2f} vs "
                           f"{cnt} rows, {m_first:.2f} / {m_second:.2f}"))
    if bad:
        print(f"  REPRODUCTION FAILED for {name}:")
        for n, why in bad:
            print(f"     n={n}: {why}")
        return False
    print(f"  {name}: all sizes reproduce the printed figures.")
    return True


# ---------------------------------------------------------------------- report

def report(title, rows_by_n, arm_a, arm_b, bounds_of):
    print(f"\n{title}")
    print("-" * 78)
    print(f"  {'n':>4} {'units':>6} {arm_a:>8} {arm_b:>8} {'d':>8} "
          f"{'T1':>4} {'95% interval':>18} {'verdict':>14}  why")
    seen = []
    for n in SIZES:
        rows = rows_by_n.get(n, [])
        if not rows:
            print(f"  {n:>4} {0:>6} {'-':>8} {'-':>8} {'-':>8} {'-':>4} "
                  f"{'-':>18} {'not evaluable':>14}  no rows")
            seen.append("not evaluable")
            continue
        a = [r[0] for r in rows]
        b = [r[1] for r in rows]
        v, d, clo, chi, t1, why = verdict(a, b, G_MIGRATION, bounds_of(n))
        ci = "-" if clo is None else f"[{clo:+.2f}, {chi:+.2f}]"
        print(f"  {n:>4} {len(rows):>6} {np.mean(a):>8.2f} {np.mean(b):>8.2f} "
              f"{d:>+8.2f} {'yes' if t1 else 'no':>4} {ci:>18} {v:>14}  {why}")
        seen.append(v)
    return seen


def main():
    print(__doc__)
    print("0 - Reproduction, before any re-evaluation")
    print("-" * 78)
    a23 = dataset_a23()
    a12 = dataset_a12()
    ok = check("A2.3 warm-start", a23, PUBLISHED_A23)
    ok &= check("A1.2 diameter", a12, PUBLISHED_A12)
    if not ok:
        print("\n  Stopping. Re-evaluating figures that have not been "
              "reproduced is worth nothing.")
        return 1

    # A2.3: both arms are migrations between two DISTINCT partitions - the
    # incumbent is non-optimal by construction and the route reaches the
    # optimum - so both floors are one swap.
    bounds_a23 = lambda n: ((2.0, n / 2.0), (2.0, n / 2.0))
    # A1.2: the diameter of a set with D > 1 is at least one swap, but the mean
    # pairwise distance among the partitions the runs reached is 0 whenever they
    # all reach the same one. Different quantities, different floors.
    bounds_a12 = lambda n: ((0.0, n / 2.0), (2.0, n / 2.0))

    v23 = report("1 - A2.3 re-evaluated: warm against cold migration cost",
                 a23, "warm", "cold", bounds_a23)
    v12 = report("2 - A1.2 re-evaluated: realised against diameter",
                 a12, "realised", "diameter", bounds_a12)

    print("\n\n3 - The four criteria of section 6 of the note")
    print("-" * 78)
    allv = v23 + v12
    blanks = [v for v in allv if v not in
              ("resolved", "unresolved", "bounded", "not evaluable")]
    print(f"  (1) one of four verdicts everywhere, never a blank: "
          f"{'yes' if not blanks else 'NO'} "
          f"({len(allv)} comparisons, {len(blanks)} blank)")
    small = [n for n in SIZES if 0 < len(a23.get(n, [])) < U_MIN]
    got = [v23[SIZES.index(n)] for n in small]
    print(f"  (2a) sizes with fewer than {U_MIN} units: "
          f"{small if small else 'none'} -> {got if got else '-'}")
    floored = [n for n in SIZES if v23[SIZES.index(n)] == "bounded"]
    print(f"  (2b) sizes where both arms rest on the floor: "
          f"{floored if floored else 'none'} -> bounded")
    print("  (3) family labels are not used by the rule at all: the unit is the")
    print("      graph, so relabelling families cannot change any verdict.")
    print("  (4) against A1.2 as published, which called n=14, 16 and 20")
    print("      resolved and n=10, 12 and 18 unresolved:")
    old = {10: "unresolved", 12: "unresolved", 14: "resolved",
           16: "resolved", 18: "unresolved", 20: "resolved"}
    for n in SIZES:
        new = v12[SIZES.index(n)]
        mark = "same" if new == old[n] else "DIFFERS"
        print(f"        n={n:>2}  old {old[n]:>11}   new {new:>14}   {mark}")

    print("\n" + "=" * 78)
    print("  What this does not do: it does not make a small sample")
    print("  informative, it is not a test of any hypothesis, and a resolved")
    print("  difference is not thereby an effect of a proposed mechanism. It")
    print("  also does not rescue a defective instrument - the orbit null arm")
    print("  that was allowed illegal moves was caught by a declared")
    print("  invalidating condition, and no resolution rule would have found")
    print("  it. This safeguard sits beside the other three and replaces none.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
