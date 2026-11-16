"""Verdict machinery for design_qcnn_bodyness_EN.md, sections 5, 6 and 8.

Nothing here knows what the arms are or which hypothesis is convenient. It
takes per-draw scores and returns one of four verdicts, in the words the note
registered: separated, bounded, unresolved, not evaluable.

The three rules it enforces, from the note:

  granularity   1/m_test = 0.005 at m_test = 200, by definition of a count
                over a test set. A difference below it is not a difference.
  unit          the dataset draw. The bootstrap resamples draws, never states.
  minimum       below 5 usable draws the verdict is "not evaluable", which is
                not "unresolved" and not "equivalent".

And the trap section 6 exists to block: there is no verdict "equivalent". Two
arms that cannot be told apart are reported as bounded above by the measured
noise floor, with the floor printed beside them, and if that floor exceeds
0.05 the verdict is "not evaluable" whatever the point estimates say.
"""
import numpy as np

GRANULARITY = 0.005          # 1 / m_test, m_test = 200
FLOOR_LIMIT = 0.05           # section 6: above this, not evaluable
MIN_UNITS = 5                # section 5
BOOT = 10000
VERDICTS = ("separated", "bounded", "unresolved", "not evaluable")


def _boot_interval(x, rng, reps=BOOT, lo=2.5, hi=97.5):
    """Percentile bootstrap of the mean, resampling the unit of analysis."""
    k = len(x)
    idx = rng.integers(0, k, size=(reps, k))
    means = np.asarray(x)[idx].mean(axis=1)
    return float(np.percentile(means, lo)), float(np.percentile(means, hi))


def arm_spread(per_draw, per_start=None, rng=None):
    """The measured noise floor of one arm, on the scale of a difference.

    Declared per arm, as section 5 requires: for an arm with random starts,
    the spread is over starts and draws together; for a deterministic solver
    it is over draws alone. Both reduce to the same statistic -- the half
    width of the 95 per cent percentile interval of the arm's own mean score
    -- so that a floor can be compared against a difference and against the
    0.05 limit of section 6 without converting units.

    per_draw   one score per draw (for a started arm: the mean over starts)
    per_start  (draws, starts) scores, or None for a deterministic arm
    """
    rng = rng or np.random.default_rng(0)
    lo, hi = _boot_interval(per_draw, rng)
    floor = (hi - lo) / 2
    if per_start is None:
        return floor, {"source": "draws", "draw_half_width": floor}
    s = np.asarray(per_start, float)
    within = float(np.mean(s.std(axis=1, ddof=1))) if s.shape[1] > 1 else 0.0
    return max(floor, within), {"source": "starts and draws",
                                "draw_half_width": floor,
                                "mean_within_draw_sd": within}


def compare(a_draw, b_draw, a_floor, b_floor, seed=0):
    """One comparison, one verdict. a minus b, both indexed by draw.

    A draw counts as usable only if both arms produced a score for it; the
    note's minimum-units rule is applied to that count and not to the larger
    of the two.
    """
    a, b = np.asarray(a_draw, float), np.asarray(b_draw, float)
    ok = np.isfinite(a) & np.isfinite(b)
    k = int(ok.sum())
    floor = float(max(a_floor, b_floor))
    out = {"units": k, "floor": floor, "d": None, "interval": None,
           "t_granularity": None, "t_interval": None}

    if k < MIN_UNITS:
        out["verdict"] = "not evaluable"
        out["why"] = f"{k} usable draws, below the registered minimum of {MIN_UNITS}"
        return out

    d = a[ok] - b[ok]
    out["d"] = float(d.mean())
    lo, hi = _boot_interval(d, np.random.default_rng(seed))
    out["interval"] = (lo, hi)
    out["t_granularity"] = bool(abs(out["d"]) >= GRANULARITY)
    out["t_interval"] = bool(lo > 0 or hi < 0)

    if floor > FLOOR_LIMIT:
        out["verdict"] = "not evaluable"
        out["why"] = (f"noise floor {floor:.3f} exceeds {FLOOR_LIMIT:.2f}; "
                      "section 6 overrides the point estimates")
        return out

    if out["t_granularity"] and out["t_interval"]:
        out["verdict"] = "separated"
        out["why"] = (f"difference {out['d']:+.3f} is at least one granularity "
                      f"step and the interval excludes zero")
        return out

    if not out["t_interval"]:
        out["verdict"] = "bounded"
        out["why"] = (f"not separated; bounded above by the measured floor "
                      f"{floor:.3f}")
        return out

    out["verdict"] = "unresolved"
    out["why"] = (f"interval excludes zero but the difference {out['d']:+.3f} "
                  f"is below one granularity step of {GRANULARITY}")
    return out


def majority_share(y):
    y = np.asarray(y)
    return float(max((y == v).mean() for v in np.unique(y)))


def invalidating(h2_verdict, h2_direction, qcnn_d1_scores, d1_floor_share,
                 ground_truth_deviation, gt_tolerance=1e-10):
    """Section 8. Each condition voids the run, and each is checked, not assumed.

    Returns a list of strings. Empty means the run stands.
    """
    bad = []
    if not (h2_verdict == "separated" and h2_direction < 0):
        bad.append(
            "1. The positive control fails. H2 requires the bodyness-2 arm to "
            f"be separated from the QCNN on D2 and to fall below it; got "
            f"{h2_verdict} with direction {h2_direction:+.3f}. No statement "
            "about D1 may be made from this run.")
    q = np.asarray(qcnn_d1_scores, float)
    q = q[np.isfinite(q)]
    if q.size and q.mean() <= d1_floor_share + GRANULARITY:
        bad.append(
            f"2. The QCNN does not train. Its mean D1 score {q.mean():.3f} sits "
            f"at the majority-class floor {d1_floor_share:.3f}. There is no "
            "trained model to compare against; the run is void, not a tie.")
    if not (ground_truth_deviation <= gt_tolerance):
        bad.append(
            f"3. The ground truth is not verified. Largest element-wise "
            f"deviation against the independent construction is "
            f"{ground_truth_deviation:.2e}, above {gt_tolerance:.0e}.")
    return bad
