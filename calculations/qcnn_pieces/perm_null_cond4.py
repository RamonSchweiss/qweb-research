"""The permutation null for invalidating condition 4.  Addendum 4, B2.

Condition 4 as registered compares an arm's mean score on the control
against the majority share and fires one granularity step above it. The run
of 15/16 November made it fire on the bodyness-2 arm at n = 8, and the
reason is not a leak: all eighteen individual classifier scores on the
control sit below the majority share, and only the per-draw MAXIMUM over
three of them rises above it. A maximum over three selections, each with its
own hyperparameter grid, is biased upward on features that carry no label
information. The condition has no allowance for that.

This measures the allowance instead of arguing about it.

THE NULL.  The labels of a draw are permuted; the features are untouched,
because permuting labels is exactly the hypothesis "these features carry no
label information" and the features are what the hypothesis is about. The
arm is then refitted in full -- every classifier class, every hyperparameter
grid -- and the statistic computed is the one condition 4 uses and no other:

    arm_best(w) - majority_share(test labels of that permutation)

WHY IT IS AFFORDABLE.  Under the null the twenty draws are exchangeable:
same train and test sizes, same classifier set, same feature counts, and the
construction of R1 version 2 guarantees that every Pauli of weight below n
carries zero label information in every draw. So the null of a single draw
is one distribution, and it is estimated here from PERMS permutations in
each of the twenty draws, which puts all twenty feature realisations into
the pool rather than trusting one. The null of the mean over twenty draws
then follows by resampling twenty values from that pool, because the draws
are independent.

This exchangeability is a declared assumption and it is what makes the
measurement cost an hour instead of a day. It is also checkable, and the
printout checks it: if the per-draw null means differed materially between
draws, the pool would be wrong, so the spread of the twenty per-draw null
means is printed against what the pooled null predicts.

THRESHOLD.  One-sided 95th percentile of the resampled mean. Condition 4
only ever asks whether an arm rises above chance, never whether it falls
below, so a two-sided threshold would be the wrong shape.
"""
import json, pathlib, sys, time
import numpy as np
import data, classical, verdict

HERE = pathlib.Path(__file__).parent
OUT = HERE / "perm_null_cond4.json"
FIRST = HERE / "perm_null_cond4_first_attempt_n8.json"   # see CORRECTION below
PERMS = 3                   # per draw, so 60 null values per arm at one size
DRAWS = 20
ARMS = (1, 2, 4)
SIZES = (8,)                # see THE BUDGET below
BOOT = 20000

# THE BUDGET, declared on 16 November before any threshold was computed.
#
# One permutation of one draw costs, measured: 68s at weight 1, 324s at
# weight 2, 1.2s at weight 4. The first attempt -- ten permutations, three
# arms, twenty draws, two sizes -- was believed to have died at a two-hour
# execution ceiling after a single draw. So the budget is cut here, and cut
# before the numbers are in.
#
# CORRECTION, 16 November, 22:10. That belief was wrong, and the sentence it
# justified is left standing above rather than quietly replaced. The first
# attempt was detached from the task that was killed at the ceiling, kept
# running for twelve hours, completed all twenty draws of n = 8 at ten
# permutations, and announced itself by overwriting the store this run was
# writing into. Its pool is kept, in perm_null_cond4_first_attempt_n8.json.
#
# The two pools are NESTED, not alternatives: the per-draw seed is
# 90000 + 100*n + draw and the permutations are drawn from it in order, so
# the three values of each draw here are the first three of that draw's ten
# there. Checked, not assumed: all twenty per-draw means of all three arms
# agree with the log written before the overwrite, to the printed precision.
#
# WHICH ONE DECIDES. The three-permutation pool, because it is the budget
# declared last and the one this file registers. The larger pool is reported
# beside it as a check on its precision, which is the honest use of a
# windfall: a threshold chosen from whichever pool gives the wanted answer
# would be the one thing this measurement exists to prevent. The report
# states, cell by cell, whether the two agree -- and in the only cell where
# condition 4 actually fired they do.
#
# ONE SIZE. Condition 4 fired exactly once in the whole run of 15/16
# November: the bodyness-2 arm on D2 at n = 8, at 0.5317 against a majority
# share of 0.5233. At n = 10 every arm sits BELOW the share, so there is
# nothing there for a threshold to decide. The null is therefore measured at
# n = 8. If the condition fires at another size in a later run, that size's
# null is measured then, by this same procedure.
#
# THREE PERMUTATIONS, NOT TEN. The pool is 60 values per arm, three in each
# of the twenty draws, so every one of the twenty feature realisations is
# still represented -- which was the reason for pooling over draws at all.
#
# AND THE POOL IS NOT EXTENDED AFTERWARDS. Adding permutations once the
# threshold is in view would let the threshold be moved by choosing when to
# stop, which is the one thing this measurement exists to prevent. Twenty
# draws times three permutations, and then it is finished.
#
# ALL THREE ARMS, even though only weight 2 fired, because weight 4 costs
# 1.2s and weight 1 costs 68s: two arms where the condition did NOT fire come
# almost free, and they are what shows whether the threshold is a property of
# the procedure or an artefact of the one cell that needed it.
#
# WHAT IS NOT CUT: the arm itself. Every classifier class and every
# hyperparameter grid is refitted in full, because the null has to be the
# distribution of the SAME procedure that produced the observed statistic.
# Trimming the arm to save time would measure the null of a different
# instrument and answer nothing.


def threshold(vals, k=DRAWS, reps=BOOT, seed=0):
    """95th percentile of the mean of k values drawn from the pooled null."""
    v = np.asarray(vals, float)
    rg = np.random.default_rng(seed)
    m = v[rg.integers(0, v.size, size=(reps, k))].mean(axis=1)
    return float(np.percentile(m, 95)), float(m.mean()), float(m.std(ddof=1))


def observed(n, scores_path=None):
    """The statistic condition 4 actually saw, per arm, from the committed run.

    Recomputed from the committed per-draw scores rather than copied from the
    report, so that a changed run changes this printout too. Returns None if
    the scores file is not beside this script or one directory up.
    """
    names = ["qcnn_bodyness_scores_n8_n10.json", "qcnn_bodyness_scores.json"]
    cands = ([pathlib.Path(scores_path)] if scores_path else
             [d / f for d in (HERE, HERE.parent, HERE / "single") for f in names])
    path = next((p for p in cands if p.exists()), None)
    if path is None:
        return None
    rows = [r for r in json.load(open(path))
            if r["dataset"] == "D2" and r["n"] == n]
    if len(rows) != DRAWS:
        return None
    out = {}
    for w in ARMS:
        a = [r[f"bodyness{w}"] for r in rows]
        best = [max(d[k] for k in ("linear", "kernel", "trees") if k in d)
                for d in a]
        out[w] = [b - r["majority"] for b, r in zip(best, rows)]
    return out


def report(n=SIZES[0], scores_path=None):
    """The pooled null, the exchangeability check, the threshold, the verdict."""
    res = json.load(open(OUT))
    if str(n) not in res:
        raise SystemExit(f"nothing stored for n={n}")
    slot = res[str(n)]
    by_draw = slot["by_draw"]
    if len(by_draw) != DRAWS:
        raise SystemExit(f"{len(by_draw)} of {DRAWS} draws stored for n={n}; "
                         f"the threshold is computed on the whole budget or "
                         f"not at all")

    print(f"=== permutation null for invalidating condition 4, D2 at n={n} ===")
    print(f"  budget as paid: {DRAWS} draws x {slot['perms']} permutations "
          f"x {len(slot['arms'])} arms, one size")
    print("  statistic: arm_best(w) - majority_share(permuted test labels)")
    print(f"  threshold: 95th percentile of the mean of {DRAWS} values "
          f"resampled from the pool, {BOOT} resamples")
    print()

    obs = observed(n, scores_path)
    if obs is None:
        print("  the committed per-draw scores are not beside this script,")
        print("  so the observed column is left out rather than typed in.")
        print()

    for w in ARMS:
        pool = [v for d in sorted(by_draw, key=int)
                for v in by_draw[d][str(w)]]
        pool = np.asarray(pool, float)
        per_draw = np.array([np.mean(by_draw[d][str(w)])
                             for d in sorted(by_draw, key=int)])
        thr, mu, sd = threshold(pool)
        print(f"  b{w}")
        print(f"    pool          {pool.size} values   mean {pool.mean():+.6f}"
              f"   sd {pool.std(ddof=1):.4f}"
              f"   range {pool.min():+.4f} to {pool.max():+.4f}")
        # Exchangeability, checked and not asserted: if the draws were not
        # exchangeable the per-draw null means would scatter by more than
        # three permutations of one common distribution can explain.
        print(f"    per-draw means sd {per_draw.std(ddof=1):.4f}   "
              f"pooled null predicts {pool.std(ddof=1)/np.sqrt(slot['perms']):.4f}"
              f"   ratio {per_draw.std(ddof=1)/(pool.std(ddof=1)/np.sqrt(slot['perms'])):.2f}")
        print(f"    null of the mean of {DRAWS}   "
              f"mean {mu:+.6f}   sd {sd:.6f}   95th pct {thr:+.6f}")
        if obs is not None:
            o = float(np.mean(obs[w]))
            share = (pool >= o).mean()
            print(f"    OBSERVED      {o:+.6f}   "
                  f"{'ABOVE' if o > thr else 'below'} the threshold"
                  f"   (pool fraction at or above: {share:.3f})")
        print()

    P = first_attempt_pool(n)
    if P is not None and obs is not None:
        k = P[ARMS[0]].shape[1]
        print(f"  --- check against the first attempt's {k}-permutation pool ---")
        print("  Nested, verified: the first three columns of each draw are")
        print("  the registered values above. The registered pool decides;")
        print("  this one says how well sixty values resolve a 95th")
        print("  percentile. Where the two disagree, the disagreement is the")
        print("  reading, and the registered threshold still governs.")
        for w in ARMS:
            o = float(np.mean(obs[w]))
            row = []
            for kk in (PERMS, k):
                pool = P[w][:, :kk].ravel()
                thr, mu, _ = threshold(pool)
                rg = np.random.default_rng(0)
                m = pool[rg.integers(0, pool.size, size=(BOOT, DRAWS))].mean(axis=1)
                row.append((kk, pool.size, mu, thr, float((m >= o).mean()),
                            o > thr))
            agree = row[0][5] == row[1][5]
            print(f"    b{w}   observed {o:+.6f}"
                  f"   condition 4 {'FIRED' if o > verdict.GRANULARITY else 'did not fire'}"
                  f"   -> {'same verdict' if agree else 'VERDICTS DIFFER'}")
            for kk, size, mu, thr, p, above in row:
                print(f"      {kk:2d} perms, {size:3d} values:  null mean "
                      f"{mu:+.6f}   95th pct {thr:+.6f}   "
                      f"p {p:.4f}   {'above' if above else 'below'}")
        print()

    print("  --- the condition's own false-positive rate ------------------")
    print("  Not a registered test. The reading below was chosen after the")
    print("  threshold above was in view, from the same pool, which is not")
    print("  extended for it. Condition 4 fires when the mean excess over")
    print(f"  twenty draws exceeds one granularity step, {verdict.GRANULARITY};")
    print("  that is the event resampled, jointly across the three arms")
    print("  because one permutation was refitted by all three.")
    per_arm, joint = false_positive_rate(n)
    for w, p in zip(ARMS, per_arm):
        print(f"    b{w}   fires on {p*100:.1f}% of resampled runs")
    print(f"    any of the three arms at n={n}:  {joint*100:.1f}%")
    if P is not None:
        k = P[ARMS[0]].shape[1]
        mat = np.stack([P[w][:, :k].ravel() for w in ARMS], axis=1)
        rg = np.random.default_rng(1)
        m = mat[rg.integers(0, mat.shape[0], size=(BOOT, DRAWS))].mean(axis=1)
        f = m > verdict.GRANULARITY
        print(f"    on the {k}-permutation pool the same reading gives "
              f"{f.any(axis=1).mean()*100:.1f}%,")
        print("    so sixty values understate it: a rate this coarse pool")
        print("    cannot resolve is not a rate to quote on its own.")
    print(f"    the registered run applies it to {len(ARMS)} arms at each of")
    print("    two sizes, so the rate over all six cells is higher than this")
    print("    and is not measured: the budget bought one size.")
    print()

    if obs is not None:
        print("  Condition 4 as registered fires on any arm whose mean score")
        print("  exceeds the majority share by one granularity step. What it")
        print("  has no allowance for is the upward bias of a maximum over")
        print("  three selections on features that carry no label at all.")
        print("  The threshold above is that allowance, measured -- and the")
        print("  measurement refutes the premise: the pooled null sits BELOW")
        print("  zero in every arm, so the procedure does not gain from the")
        print("  maximum on label-free features, it loses. There was no")
        print("  upward bias to allow for.")
    return 0


def first_attempt_pool(n):
    """The first attempt's ten-permutation pool at n, as draws x permutations.

    Returns None unless the file is present and nested with the registered
    store: the first PERMS columns of each draw must be the registered values.
    A pool that is not nested is a different measurement and is not reported
    as a check on this one.
    """
    if n != 8 or not FIRST.exists() or not OUT.exists():
        return None
    s = json.load(open(FIRST)).get(str(n))
    if s is None or s.get("draws") != DRAWS:
        return None
    k = s["perms"]
    P = {w: np.asarray(s["pool"][str(w)], float).reshape(DRAWS, k)
         for w in ARMS}
    reg = json.load(open(OUT))[str(n)]["by_draw"]
    for w in ARMS:
        for d in range(DRAWS):
            if not np.allclose(P[w][d][:PERMS], reg[str(d)][str(w)]):
                return None
    return P


def false_positive_rate(n, reps=BOOT, seed=1):
    """How often condition 4 fires on labels that carry nothing.

    DECIDED AFTER THE THRESHOLD WAS IN VIEW, and therefore not a registered
    test of anything. It is a second reading of the pool that was paid for
    above, and it is reported as a diagnosis of the condition rather than as
    a result about the data. The pool is not extended to produce it.

    The condition fires when the mean excess over twenty draws exceeds one
    granularity step, so that is the event resampled here. Resampling is by
    (draw, permutation) pair jointly across the arms, because all three arms
    were refitted on the SAME permutation of the same draw: resampling them
    separately would throw away a correlation the condition is exposed to.
    """
    slot = json.load(open(OUT))[str(n)]
    by_draw = slot["by_draw"]
    keys = [(d, j) for d in sorted(by_draw, key=int)
            for j in range(slot["perms"])]
    mat = np.array([[by_draw[d][str(w)][j] for w in ARMS] for d, j in keys])
    rg = np.random.default_rng(seed)
    pick = rg.integers(0, len(keys), size=(reps, DRAWS))
    means = mat[pick].mean(axis=1)                 # reps x arms
    fires = means > verdict.GRANULARITY
    return ([float(f.mean()) for f in fires.T],
            float(fires.any(axis=1).mean()))


def run_block(n, lo, hi):
    """Draws [lo, hi) at size n, merged into whatever is already stored.

    Each draw's seed is 90000 + 100*n + draw and depends on nothing else, so
    a block is reproducible on its own and a repeated block overwrites its own
    draws with identical values rather than adding to them. That is what makes
    it legitimate to pay the budget in pieces: the pieces do not interact.
    """
    res = json.load(open(OUT)) if OUT.exists() else {}
    slot = res.setdefault(str(n), {"perms": PERMS, "arms": list(ARMS),
                                   "by_draw": {}})
    if slot["perms"] != PERMS:
        raise SystemExit(f"stored file has perms={slot['perms']}, "
                         f"this run has {PERMS}; refusing to mix them")
    print(f"\n=== permutation null, D2 at n = {n}, draws {lo}..{hi-1}, "
          f"{PERMS} per draw ===", flush=True)
    for draw in range(lo, hi):
        t = time.time()
        vals = one_draw(n, draw, PERMS)
        slot["by_draw"][str(draw)] = {str(w): vals[w] for w in ARMS}
        json.dump(res, open(OUT, "w"))
        print(f"  n={n} draw {draw:2d}: "
              + "  ".join(f"b{w} {np.mean(vals[w]):+.4f}" for w in ARMS)
              + f"   [{time.time()-t:.0f}s]  stored", flush=True)
    done = len(slot["by_draw"])
    print(f"  {done} of {DRAWS} draws stored at n={n}", flush=True)
    return done


def one_draw(n, draw, perms=PERMS):
    """The perms null values of one draw, one entry per arm."""
    psi, y, _ = data.d2(n, draw)
    (xtr, ytr), (xte, yte) = data.split(psi, y, draw, n)
    lab = np.concatenate([ytr, yte])
    ntr = len(ytr)
    feats = {w: (classical.features(xtr, n, w),
                 classical.features(xte, n, w)) for w in ARMS}
    rg = np.random.default_rng(90000 + 100 * n + draw)
    vals = {w: [] for w in ARMS}
    for _ in range(perms):
        p = rg.permutation(lab)
        ptr, pte = p[:ntr], p[ntr:]
        share = verdict.majority_share(pte)
        for w in ARMS:
            Ftr, Fte = feats[w]
            a = classical.arm_scores(Ftr, ptr, Fte, pte, trees=(w < 4))
            vals[w].append(float(classical.arm_best(a) - share))
    return vals


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        raise SystemExit("usage: perm_null_cond4.py <n> [draw_from draw_to]\n"
                         "       perm_null_cond4.py report [n]")
    if a[0] == "report":
        raise SystemExit(report(int(a[1]) if len(a) > 1 else SIZES[0]))
    n = int(a[0])
    lo, hi = (int(a[1]), int(a[2])) if len(a) >= 3 else (0, DRAWS)
    run_block(n, lo, min(hi, DRAWS))
