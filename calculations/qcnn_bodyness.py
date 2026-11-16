"""What the standard QCNN benchmark can distinguish.

Measures the study registered in designs/design_qcnn_bodyness_EN.md of
14 November 2026 and its addenda 1, 2 and 3. Reproduces, at a size one
person can run, the second half of the claim of Bermejo, Braccia, Rudolph,
Holmes, Cincio and Cerezo (arXiv:2408.12739): that the datasets QCNNs are
benchmarked on are locally easy, so the benchmark cannot distinguish a model
that needs a quantum computer from one that does not. The claim is theirs;
this is a reproduction and is cited that way.

    python qcnn_bodyness.py --check              gates only, about a minute
    python qcnn_bodyness.py --run D1 8           one dataset, one size
    python qcnn_bodyness.py --run D1 12 0 5      one dataset, size, draw slice
    python qcnn_bodyness.py --report             verdicts from what is stored

The full registered run is 20 draws x 3 sizes x 2 datasets and takes hours,
so it is not part of run_all.py; --check is. Each --run appends per-draw
scores to qcnn_bodyness_scores.json and can be resumed. --report reads that
file and applies the resolution rule; it never recomputes a score, so the
verdicts can be re-derived from the stored numbers by anyone.

Nothing here chooses anything the design left open. Every such decision is
registered in addendum 3 and only read from here.
"""
import json, sys, time, pathlib
import numpy as np

import qcnn_bodyness_core as core

HERE = pathlib.Path(__file__).parent
STORE = HERE / "qcnn_bodyness_scores.json"

SIZES = (8, 10, 12)
DRAWS = 20                 # section 9, the stopping condition
STARTS = 5                 # section 9
RULE, LR = "gd", 0.30      # A3.4: section 3 read narrowly, step size from the grid
STEPS = 500                # A3.4 amended; MEASURED at n = 12, not chosen
ARMS_D1 = (1, 2)           # bodyness-4 runs on the control only (section 3)
ARMS_D2 = (1, 2, 4)

# D1w is D1 with the field window of A3.6 excluded. It is a declared
# sensitivity check at n = 8 only, not a third dataset of the study, and no
# hypothesis is read off it.
DATASETS = {"D1": lambda n, d: core.d1(n, d),
            "D2": lambda n, d: core.d2(n, d),
            "D1w": lambda n, d: core.d1(n, d, window=2.0)}
SENSITIVITY = {"D1w": 8}


# ------------------------------------------------------------------ the gates
def gate_ground_truth(n=8, m=6):
    """Section 8, condition 3: exact ground states against an independent
    slower construction, element by element and not by norm or by count."""
    from numpy.linalg import eigh
    rng = np.random.default_rng(1)
    worst = 0.0
    for h in rng.uniform(0.2, 1.8, size=m):
        Hs = core.h_tfim(n, h)
        assert np.count_nonzero(Hs.imag.data) == 0
        Hr = Hs.real
        fast = core.ground(Hr).real
        w, v = eigh(Hr.toarray())                      # dense, independent
        slow = v[:, 0]
        for a in (fast, slow):
            a *= np.sign(a[int(np.argmax(np.abs(a)))])
        worst = max(worst, float(np.abs(fast - slow).max()))
    return worst


def gate_features(n=7, m=3, max_weight=4):
    """The feature route against one sparse matrix-vector product per string."""
    rng = np.random.default_rng(2)
    psi = rng.normal(size=(m, 2 ** n))
    psi /= np.linalg.norm(psi, axis=1, keepdims=True)
    f = core.features(psi, n, max_weight)
    g = np.array([core.features_slow(p[None].astype(complex), n, max_weight)[0]
                  for p in psi])
    return float(np.abs(f - g).max())


def gate_control_construction(n=8, m=40):
    """R1 v2 carries no label information below weight n. Same angles, sign
    flipped: every feature must agree. The witness must not."""
    rng = np.random.default_rng(3)
    al = rng.uniform(-core.ALPHA, core.ALPHA, size=(m, n))
    plus = np.array([core.cat_ry(n, +1, a).real for a in al])
    minus = np.array([core.cat_ry(n, -1, a).real for a in al])
    fp = core.features(plus, n, 2)
    fm = core.features(minus, n, 2)
    W = core.op_on(n, {i: "X" for i in range(n)}).real
    wp = float(np.mean([p @ (W @ p) for p in plus]))
    wm = float(np.mean([p @ (W @ p) for p in minus]))
    return float(np.abs(fp - fm).max()), abs(wp - wm)


def gate_reproducible(n=8, m=20):
    """The same draw, built twice, must be bit-identical.

    This gate exists because of design_cut_degeneracy_EN_addendum_4.md: a
    registered figure set could not be reproduced from the repository, and
    one of the four explanations checked was an uncontrolled random stream.
    It was not that one -- but the stream here was uncontrolled, and nothing
    in the apparatus would have said so. eigsh hands ARPACK a random starting
    vector when none is given, outside numpy's global stream: two calls on
    the same matrix differed by 3.2e-14. Far too little to move a
    classification, and not the point.
    """
    a, ya, ha = core.d1(n, 0, m=m)
    b, yb, hb = core.d1(n, 0, m=m)
    c, yc, _ = core.d2(n, 0, m=m)
    d, yd, _ = core.d2(n, 0, m=m)
    same = (np.array_equal(ya, yb) and np.array_equal(ha, hb)
            and np.array_equal(yc, yd))
    return float(max(np.abs(a - b).max(), np.abs(c - d).max())), same


def gate_one_draw():
    """One complete draw at the smallest size, every arm actually called.

    Why this gate exists. The five gates below check numbers against slower
    routes, and every one of them passed on an assembled file whose import
    list had silently lost two names. The study then died on its first draw
    with a NameError, after half an hour of building datasets. A gate suite
    that never calls an arm cannot see a missing arm.

    So this one runs the whole per-draw path once -- QCNN training and all
    three classical model classes, linear, kernel and trees -- at n = 4 with
    two starts and three steps. It is about twenty seconds and checks nothing
    numerical. It only establishes that each arm runs and returns a score in
    [0, 1], which is exactly what the other gates cannot establish.
    """
    n, m = 4, 24
    psi, y, _ = core.d2(n, 0, m=2 * m)
    (xtr, ytr), (xte, yte) = core.split(psi, y, 0, n, m_train=m, m_test=m)
    ops, npar, out_q = core.build(n)
    per_start, _, _ = core.train(n, ops, npar, out_q, (xtr, ytr),
                                    (xte, yte), starts=2, steps=3, seed=0,
                                    optimiser=RULE, lr=LR)
    Ftr = core.features(xtr, n, 2)
    Fte = core.features(xte, n, 2)
    arm = core.arm_scores(Ftr, ytr, Fte, yte, trees=True)
    classes = [k for k in ("linear", "kernel", "trees") if k in arm]
    vals = [float(np.mean(per_start))] + [arm[k] for k in classes]
    return classes, all(0.0 <= v <= 1.0 for v in vals)


def checks():
    print("Gates. Each is a condition of section 8 or a route this script "
          "replaces a slower one with.\n")
    t = time.time()
    classes, g0 = gate_one_draw()
    print(f"  one whole draw runs, arms called: QCNN + "
          f"{' + '.join(classes)}{'':<14}{'ok' if g0 else 'FAILED'}")
    g1 = gate_ground_truth()
    print(f"  ground states against a dense diagonalisation, element-wise   "
          f"{g1:.2e}")
    g2 = gate_features()
    print(f"  weight<=4 features against one matvec per Pauli string        "
          f"{g2:.2e}")
    g3, wit = gate_control_construction()
    print(f"  R1 v2: weight<=2 features, same angles, sign flipped          "
          f"{g3:.2e}")
    print(f"  R1 v2: the weight-n witness, which must separate              "
          f"{wit:.4f}")
    g4, same = gate_reproducible()
    print(f"  the same draw built twice, element-wise                       "
          f"{g4:.2e}   labels and fields identical: {same}")
    ok = (g0 and len(classes) == 3
          and g1 < 1e-8 and g2 < 1e-10 and g3 < 1e-10 and wit > 0.5
          and g4 == 0.0 and same)
    print(f"\n  {'all gates pass' if ok else 'A GATE FAILED'}   [{time.time()-t:.0f}s]")
    return ok


# -------------------------------------------------------------------- one draw
def one_draw(ds, n, draw):
    psi, y, _ = DATASETS[ds](n, draw)
    (xtr, ytr), (xte, yte) = core.split(psi, y, draw, n)
    rec = {"dataset": ds, "n": n, "draw": draw,
           "majority": core.majority_share(yte)}

    ops, npar, out_q = core.build(n)
    per_start, _, _ = core.train(n, ops, npar, out_q, (xtr, ytr), (xte, yte),
                                    starts=STARTS, steps=STEPS, seed=1000 + draw,
                                    optimiser=RULE, lr=LR)
    rec["qcnn_starts"] = [float(v) for v in per_start]
    rec["qcnn"] = float(np.mean(per_start))          # A3.2: the mean, not the best

    for w in (ARMS_D2 if ds == "D2" else ARMS_D1):
        Ftr = core.features(xtr, n, w)
        Fte = core.features(xte, n, w)
        # trees only where they are affordable; see core.arm_scores
        rec[f"bodyness{w}"] = core.arm_scores(Ftr, ytr, Fte, yte,
                                                   trees=(w < 4))
    return rec


def run(ds, n, lo=0, hi=DRAWS):
    recs = load()
    done = {(r["dataset"], r["n"], r["draw"]) for r in recs}
    t0 = time.time()
    for draw in range(lo, hi):
        if (ds, n, draw) in done:
            print(f"  {ds} n={n} draw {draw}: already stored", flush=True)
            continue
        t = time.time()
        rec = one_draw(ds, n, draw)
        recs.append(rec)
        save(recs)
        arms = "  ".join(f"b{w} {core.arm_best(rec[f'bodyness{w}']):.3f}"
                         for w in (ARMS_D2 if ds == "D2" else ARMS_D1))
        print(f"  {ds} n={n} draw {draw:2d}: qcnn {rec['qcnn']:.3f}  {arms}"
              f"   majority {rec['majority']:.3f}   [{time.time()-t:.0f}s]", flush=True)
    print(f"\n  {ds} n={n}: draws {lo}..{hi-1} in {time.time()-t0:.0f}s")


def load():
    return json.loads(STORE.read_text()) if STORE.exists() else []


def save(recs):
    STORE.write_text(json.dumps(recs, indent=1))


# ----------------------------------------------------------------- the verdicts
def best(rec, w):
    return core.arm_best(rec[f"bodyness{w}"])


def report():
    recs = load()
    if not recs:
        print("Nothing stored. Run --run first.")
        return 1
    print(__doc__.split("\n\n")[0])
    print(f"\nStored: {len(recs)} draws. Granularity {core.GRANULARITY}, "
          f"floor limit {core.FLOOR_LIMIT}, minimum "
          f"{core.MIN_UNITS} usable draws, {core.BOOT} bootstrap "
          f"resamples of the draw.\n")

    table, floors = {}, {}
    for ds in ("D1", "D2"):
        arms = ARMS_D2 if ds == "D2" else ARMS_D1
        for n in SIZES:
            rs = sorted([r for r in recs if r["dataset"] == ds and r["n"] == n],
                        key=lambda r: r["draw"])
            if not rs:
                continue
            q = np.array([r["qcnn"] for r in rs])
            qs = np.array([r["qcnn_starts"] for r in rs])
            fq, dq = core.arm_spread(q, qs)
            table[(ds, n)] = {"draws": len(rs), "qcnn": q, "starts": qs,
                              "majority": np.array([r["majority"] for r in rs])}
            floors[(ds, n, "qcnn")] = fq
            for w in arms:
                b = np.array([best(r, w) for r in rs])
                table[(ds, n)][f"b{w}"] = b
                floors[(ds, n, f"b{w}")] = core.arm_spread(b)[0]

    for ds in ("D1", "D2"):
        arms = ARMS_D1 if ds == "D1" else ARMS_D2
        print(f"=== {ds} " + "=" * 62)
        for n in SIZES:
            if (ds, n) not in table:
                continue
            t = table[(ds, n)]
            print(f"\n  n = {n}, {t['draws']} draws, majority share "
                  f"{t['majority'].mean():.3f}")
            print(f"    qcnn   {t['qcnn'].mean():.4f}   floor "
                  f"{floors[(ds,n,'qcnn')]:.4f}   "
                  f"within-draw sd over starts "
                  f"{t['starts'].std(axis=1, ddof=1).mean():.4f}")
            for w in arms:
                print(f"    b{w}     {t[f'b{w}'].mean():.4f}   floor "
                      f"{floors[(ds,n,f'b{w}')]:.4f}")
            for w in arms:
                r = core.compare(t[f"b{w}"], t["qcnn"],
                                    floors[(ds, n, f"b{w}")],
                                    floors[(ds, n, "qcnn")])
                iv = ("—" if r["interval"] is None
                      else f"[{r['interval'][0]:+.3f}, {r['interval'][1]:+.3f}]")
                d = "—" if r["d"] is None else f"{r['d']:+.4f}"
                print(f"    b{w} minus qcnn: d {d}  {iv}  floor "
                      f"{r['floor']:.4f}  ->  {r['verdict'].upper()}")
                print(f"        {r['why']}")
        print()
    hypotheses(table, floors)
    return 0


def hypotheses(table, floors):
    print("=== Registered hypotheses " + "=" * 47)

    def v(ds, n, w):
        t, f = table.get((ds, n)), floors
        if t is None or f"b{w}" not in t:
            return None
        return core.compare(t[f"b{w}"], t["qcnn"], f[(ds, n, f"b{w}")],
                               f[(ds, n, "qcnn")])

    for tag, ds, w, want in (("H1", "D1", 2, "bounded"),
                             ("H2", "D2", 2, "separated"),
                             ("H5", "D1", 1, "separated")):
        line = []
        for n in SIZES:
            r = v(ds, n, w)
            line.append("—" if r is None else f"n={n}: {r['verdict']}")
        print(f"  {tag}  b{w} against the QCNN on {ds}, expecting "
              f"{want:10s} {'   '.join(line)}")

    # H4 is reported, not deleted (addendum 3, A3.5). Its verdict was settled
    # before the run and by construction, which is why it carries a
    # measurement and not a comparison.
    g3, wit = gate_control_construction()
    print(f"\n  H4  b4 closes part of the gap on D2, expecting      "
          f"REFUTED BY CONSTRUCTION")
    print(f"        Local RY commutes with the partial trace over the "
          f"complement, so")
    print(f"        every proper subset has the same reduced state in both "
          f"classes and")
    print(f"        every Pauli of weight below n carries zero label "
          f"information.")
    print(f"        Measured: same angles, sign flipped, largest difference "
          f"over all")
    print(f"        weight<=2 features {g3:.1e}; the weight-n witness "
          f"separates by {wit:.4f}.")
    print(f"        Weight 4 is below n at every size, so the arm cannot "
          f"close a gap.")
    print(f"        What it does instead is condition 4 below.")

    print("\n  H3  the QCNN's own spread over starts against the b2 gap, on D1")
    for n in SIZES:
        t = table.get(("D1", n))
        if t is None or "b2" not in t:
            continue
        spread = t["starts"].std(axis=1, ddof=1).mean()
        gap = abs(t["b2"].mean() - t["qcnn"].mean())
        print(f"        n={n}: spread {spread:.4f} against gap {gap:.4f}  ->  "
              f"{'spread exceeds the gap' if spread > gap else 'gap exceeds the spread'}")

    print("\n=== Invalidating conditions, section 8 and addendum 3 " + "=" * 19)
    bad = []
    r2 = v("D2", 8, 2)
    d2dir = None
    if r2 and r2["d"] is not None:
        d2dir = r2["d"]
    t1 = table.get(("D1", 8))
    bad += core.invalidating(
        r2["verdict"] if r2 else "not evaluable",
        d2dir if d2dir is not None else 0.0,
        t1["qcnn"] if t1 is not None else np.array([]),
        float(t1["majority"].mean()) if t1 is not None else 0.5,
        gate_ground_truth() if "--gates" in sys.argv else 0.0)

    for n in SIZES:
        t = table.get(("D2", n))
        if t is None:
            continue
        for w in ARMS_D2:
            if f"b{w}" not in t:
                continue
            over = t[f"b{w}"].mean() - t["majority"].mean()
            if over > core.GRANULARITY:
                bad.append(
                    f"4. A low-bodyness arm beats chance on the control: b{w} "
                    f"at n={n} scores {t[f'b{w}'].mean():.4f} against a "
                    f"majority share of {t['majority'].mean():.4f}. The "
                    f"construction guarantees weight<n carries no label "
                    f"information, so this is a leak in the instrument.")
    if bad:
        for b in bad:
            print(f"  VOID  {b}")
    else:
        print("  None fired. The run stands.")


if __name__ == "__main__":
    t_all = time.time()
    a = sys.argv[1:]
    code = 0
    if not a or "--check" in a:
        code = 0 if checks() else 1
    elif a[0] == "--run":
        ds, n = a[1], int(a[2])
        lo = int(a[3]) if len(a) > 3 else 0
        hi = int(a[4]) if len(a) > 4 else DRAWS
        run(ds, n, lo, hi)
    elif a[0] == "--report":
        code = report()
    else:
        print(__doc__)
        code = 2
    print(f"\n[{time.time()-t_all:.0f}s]")
    sys.exit(code)
