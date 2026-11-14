"""Does the registered positive control of the QCNN bodyness study work?

Article: "What a Trainable Circuit Gives Away" (in progress)
Design:  designs/design_qcnn_bodyness_EN.md, registered 14 November 2026
         and its addendum 1, which this script is the evidence for.

WHY THIS EXISTS

The design registers two datasets. D1 is the benchmark under test: ground
states of the transverse-field Ising model, labelled by phase. D2 is the
positive control, a cluster-model family whose label was expected to need a
string order parameter longer than two sites, so that a classifier limited to
Pauli features of weight <= 2 MUST fail there. Without a control that fails,
"the classical arm matches the QCNN on D1" cannot be told apart from "this
comparison never shows anything".

This script checks the control before the study runs. It finds that D2 as
registered is vacuous: the weight <= 2 arm reaches the same score on D2 as on
D1, and a SINGLE local feature, the mean transverse magnetisation, is already
enough on both. The invalidating condition in the design could therefore
never have fired.

It then checks a replacement, R1, where the absence of low-weight information
is a property of the construction rather than an observation: the sign of a
cat state. For |psi_pm> = (|0..0> +- |1..1>)/sqrt(2), every proper subset of
the qubits has the SAME reduced density matrix in both classes, because the
cross term requires the complement to agree. So every Pauli expectation of
weight < n carries exactly zero information about the label. Random local Z
rotations are applied to give the dataset variety without creating any.

Both arms are run with a linear and a nonlinear classifier, because
"the features do not carry the label" and "logistic regression cannot extract
it from them" are different statements and the study must not confuse them.

THEN R1 FAILS TOO, AND THE REASON IS WORSE

R1 as written in addendum 1 used random local Z rotations for variety. Those
are diagonal, so they randomise the relative phase of |1..1> against |0..0>:
the state becomes (|0..0> + exp(i*Phi) |1..1>)/sqrt(2) with Phi the sum of the
angles, and +-exp(i*Phi) with Phi uniform has the SAME distribution for both
signs. The two classes are then identical as distributions and no arm can
separate them, the QCNN included. The witness in addendum 1 only worked
because it was handed the angles, which no classifier has.

A control nobody can pass is not a control. The first probe asked whether the
classical arms fail; it did not ask whether anything succeeds. That omission
is the finding of addendum 2, and the requirement that follows from it is
recorded there: a positive control needs its own demonstration of being
passable.

R1 version 2 uses local Y rotations instead. They are not diagonal, so they
vary the low-weight marginals - the control is no longer degenerate - and
they leave the relative phase alone, so a fixed global observable can still
see the sign. The amplitude is swept here so that the choice is made on a
stated criterion rather than on the study's own results.

WHAT THIS DOES NOT DO

It measures no QCNN. It says nothing about the study's actual question. It
only establishes which datasets the comparison is able to separate at all.

Runtime about four minutes. Output: calculations/qcnn_control_probe_output.txt
"""
import numpy as np
from itertools import combinations
from scipy.sparse import identity, kron, csr_matrix
from scipy.sparse.linalg import eigsh
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import cross_val_score

SEED = 20261114
SIZES = (6, 8)
N_STATES = 100          # per sweep, before the critical window is dropped
CRIT_WINDOW = 0.08      # fraction of the parameter range dropped either side
FOLDS = 5

I2 = csr_matrix(np.eye(2))
PAULI = {
    "X": csr_matrix(np.array([[0, 1], [1, 0]], dtype=complex)),
    "Y": csr_matrix(np.array([[0, -1j], [1j, 0]], dtype=complex)),
    "Z": csr_matrix(np.array([[1, 0], [0, -1]], dtype=complex)),
}


def op_on(n, where):
    """Kronecker product over n sites; `where` maps site index -> 'X'/'Y'/'Z'."""
    out = None
    for i in range(n):
        m = PAULI[where[i]] if i in where else I2
        out = m if out is None else kron(out, m, format="csr")
    return out


def h_tfim(n, h):
    """D1: -sum_i Z_i Z_{i+1} - h sum_i X_i, open chain."""
    H = csr_matrix((2 ** n, 2 ** n), dtype=complex)
    for i in range(n - 1):
        H = H - op_on(n, {i: "Z", i + 1: "Z"})
    for i in range(n):
        H = H - h * op_on(n, {i: "X"})
    return H


def h_cluster(n, lam):
    """D2 as registered: -(1-lam) sum Z_{i-1} X_i Z_{i+1} - lam sum X_i."""
    H = csr_matrix((2 ** n, 2 ** n), dtype=complex)
    for i in range(1, n - 1):
        H = H - (1 - lam) * op_on(n, {i - 1: "Z", i: "X", i + 1: "Z"})
    for i in range(n):
        H = H - lam * op_on(n, {i: "X"})
    return H


def ground_state(H, n):
    """Lowest eigenvector. Verified against dense diagonalisation at n = 6."""
    w, v = eigsh(H, k=1, which="SA", maxiter=100000)
    psi = v[:, 0]
    return psi / np.linalg.norm(psi)


def verify_ground_state(n=6):
    """Invalidating condition 3 of the design, in its smallest form.

    The sparse solver is checked against a dense one element by element, not
    by energy and not by norm: counting the right number of things is not the
    same as having the right things.
    """
    H = h_tfim(n, 0.7)
    psi = ground_state(H, n)
    w, v = np.linalg.eigh(H.toarray())
    ref = v[:, 0]
    ref = ref / np.linalg.norm(ref)
    if np.vdot(ref, psi).real < 0:                 # fix the global sign
        ref = -ref
    max_dev = np.max(np.abs(np.abs(psi) - np.abs(ref)))
    overlap = abs(np.vdot(ref, psi))
    print(f"GROUND-TRUTH GATE (n = {n}, h = 0.7)")
    print(f"  sparse vs dense, largest elementwise deviation : {max_dev:.3e}")
    print(f"  overlap                                        : {overlap:.12f}")
    ok = max_dev < 1e-8 and abs(overlap - 1) < 1e-10
    print(f"  gate: {'PASSED' if ok else 'FAILED'}")
    if not ok:
        raise SystemExit("ground-truth gate failed; nothing below is valid")
    print()
    return ok


def pauli_features(psi, n, max_weight):
    """Expectation values of every Pauli string of weight 1..max_weight."""
    out = []
    for w in range(1, max_weight + 1):
        for sites in combinations(range(n), w):
            for labels in np.ndindex(*([3] * w)):
                where = {s: "XYZ"[l] for s, l in zip(sites, labels)}
                out.append(float(np.real(np.conj(psi) @ (op_on(n, where) @ psi))))
    return np.array(out)


def scores(Xf, y):
    lin = cross_val_score(LogisticRegression(max_iter=5000), Xf, y,
                          cv=FOLDS).mean()
    nl = cross_val_score(HistGradientBoostingClassifier(max_iter=200,
                                                        random_state=SEED),
                         Xf, y, cv=FOLDS).mean()
    return lin, nl


def majority_share(y):
    return max(y.mean(), 1 - y.mean())


def sweep(name, h_of, lo, hi, crit, n):
    ps = np.linspace(lo, hi, N_STATES)
    ps = ps[np.abs(ps - crit) > CRIT_WINDOW * (hi - lo)]
    states = [ground_state(h_of(n, p), n) for p in ps]
    y = (ps > crit).astype(int)

    print(f"{name}, n = {n}, {len(ps)} states, "
          f"majority class {majority_share(y):.3f}")
    for k in (1, 2):
        Xf = np.array([pauli_features(s, n, k) for s in states])
        lin, nl = scores(Xf, y)
        print(f"    weight <= {k}: {Xf.shape[1]:5d} features   "
              f"linear {lin:.3f}   nonlinear {nl:.3f}")

    mx = np.array([[float(np.real(np.conj(s) @ (op_on(n, {i: 'X'}) @ s)))
                    for i in range(n)] for s in states])
    one = mx.mean(axis=1).reshape(-1, 1)
    lin, _ = scores(one, y)
    print(f"    mean <X_i> alone, ONE feature            "
          f"linear {lin:.3f}")
    print()


def cat_state(n, sign, phases):
    """(|0..0> + sign |1..1>)/sqrt(2), then exp(-i theta_j Z_j / 2) per site."""
    v = np.zeros(2 ** n, dtype=complex)
    v[0] = 1 / np.sqrt(2)
    v[-1] = sign / np.sqrt(2)
    idx = np.arange(2 ** n)
    diag = np.ones(2 ** n, dtype=complex)
    for j, th in enumerate(phases):
        bit = (idx >> (n - 1 - j)) & 1
        diag *= np.exp(-1j * th / 2 * np.where(bit == 0, 1.0, -1.0))
    return diag * v


def derotated_global_x(psi, n, phases):
    """<X^(xn)> after undoing the local Z rotations: the weight-n witness."""
    idx = np.arange(2 ** n)
    diag = np.ones(2 ** n, dtype=complex)
    for j, th in enumerate(phases):
        bit = (idx >> (n - 1 - j)) & 1
        diag *= np.exp(+1j * th / 2 * np.where(bit == 0, 1.0, -1.0))
    p = diag * psi
    return float(np.real(np.conj(p) @ (op_on(n, {i: "X" for i in range(n)}) @ p)))


def control_r1(n, m=120):
    rng = np.random.default_rng(SEED)
    signs = rng.choice([-1.0, 1.0], size=m)
    phase_sets = rng.uniform(0, 2 * np.pi, size=(m, n))
    states = [cat_state(n, s, ph) for s, ph in zip(signs, phase_sets)]
    y = (signs > 0).astype(int)

    ref = np.array([derotated_global_x(s, n, ph)
                    for s, ph in zip(states, phase_sets)])
    print(f"R1  cat-state sign (proposed), n = {n}, {m} states, "
          f"majority class {majority_share(y):.3f}")
    print(f"    witness: de-rotated <X^(x{n})> = "
          f"{ref[y == 1].mean():+.3f} for +, {ref[y == 0].mean():+.3f} for -")
    for k in (1, 2):
        Xf = np.array([pauli_features(s, n, k) for s in states])
        lin, nl = scores(Xf, y)
        print(f"    weight <= {k}: {Xf.shape[1]:5d} features   "
              f"linear {lin:.3f}   nonlinear {nl:.3f}")
    print()


def cat_state_ry(n, sign, alphas):
    """R1 version 2: (|0..0> + sign |1..1>)/sqrt(2), then RY(alpha_j) per site."""
    v = np.zeros(2 ** n, dtype=complex)
    v[0] = 1 / np.sqrt(2)
    v[-1] = sign / np.sqrt(2)
    U = np.array([[1.0]], dtype=complex)
    for a in alphas:
        c, s = np.cos(a / 2), np.sin(a / 2)
        U = np.kron(U, np.array([[c, -s], [s, c]], dtype=complex))
    return U @ v


def r1_v1_is_impossible(n=6, m=2000):
    """Addendum 2: without the angles in hand, the classes coincide."""
    rng = np.random.default_rng(SEED)
    Xn = op_on(n, {i: "X" for i in range(n)})
    signs = rng.choice([-1.0, 1.0], size=m)
    ph = rng.uniform(0, 2 * np.pi, size=(m, n))
    vals = np.array([float(np.real(np.conj(s) @ (Xn @ s)))
                     for s in (cat_state(n, sg, p)
                               for sg, p in zip(signs, ph))])
    print(f"R1 v1 (addendum 1), n = {n}, {m} states")
    print(f"    <X^(x{n})> WITHOUT de-rotation, which is all an arm can see:")
    for lab, nm in ((1.0, "+"), (-1.0, "-")):
        v = vals[signs == lab]
        print(f"      class {nm}: mean {v.mean():+.4f}  sd {v.std():.4f}  "
              f"range {v.min():+.3f} .. {v.max():+.3f}")
    eff = (ph.sum(axis=1) + np.where(signs > 0, 0.0, np.pi)) % (2 * np.pi)
    for lab, nm in ((1.0, "+"), (-1.0, "-")):
        h, _ = np.histogram(eff[signs == lab], bins=8, range=(0, 2 * np.pi))
        print(f"      class {nm}: relative phase over 8 bins {h}")
    print("    Both flat: identical as distributions. Impossible, not hard.")
    print()


def control_r1_v2(n, amplitudes=(0.0, 0.2, 0.4, 0.8), m=120):
    rng = np.random.default_rng(SEED)
    Xn = op_on(n, {i: "X" for i in range(n)})
    for a in amplitudes:
        signs = rng.choice([-1.0, 1.0], size=m)
        al = rng.uniform(-a, a, size=(m, n))
        states = [cat_state_ry(n, s, aa) for s, aa in zip(signs, al)]
        y = (signs > 0).astype(int)
        w = np.array([float(np.real(np.conj(s) @ (Xn @ s))) for s in states])
        Xf = np.array([pauli_features(s, n, 2) for s in states])
        lin, nl = scores(Xf, y)
        print(f"R1 v2, n = {n}, alpha ~ U(-{a}, {a}), "
              f"majority class {majority_share(y):.3f}")
        print(f"    witness <X^(x{n})>: {w[y == 1].mean():+.3f} (sd "
              f"{w[y == 1].std():.3f}) for +,  {w[y == 0].mean():+.3f} (sd "
              f"{w[y == 0].std():.3f}) for -")
        print(f"    weight <= 2: largest feature sd {Xf.std(axis=0).max():.4f}"
              f"   linear {lin:.3f}   nonlinear {nl:.3f}")
    print()


def main():
    print(__doc__.split("WHY THIS EXISTS")[0].strip())
    print("=" * 72)
    print()
    verify_ground_state(6)

    print("THE REGISTERED DATASETS")
    print("-" * 72)
    for n in SIZES:
        sweep("D1  TFIM, the benchmark under test  ", h_tfim, 0.2, 1.8, 1.0, n)
        sweep("D2  cluster, the registered control ", h_cluster, 0.05, 0.95,
              0.5, n)

    print("THE CONTROL PROPOSED IN ADDENDUM 1, AND WHY IT ALSO FAILS")
    print("-" * 72)
    for n in SIZES:
        control_r1(n)
    r1_v1_is_impossible(6)

    print("THE CONTROL OF ADDENDUM 2")
    print("-" * 72)
    for n in SIZES:
        control_r1_v2(n)

    print("=" * 72)
    print("""READING

D2 is not harder than D1 for any arm in this study. At n = 8 both reach the
same score on both datasets, and one local feature - the mean transverse
magnetisation - is already enough on both. The two phases sit at different
transverse field strengths, so their ground states differ locally. The string
order parameter characterises the cluster phase; it is not what is needed to
classify these particular states. The design conflated the two.

Consequence: the positive control of the registered design cannot fire, so
the main run does not start. See addendum 1.

R1 v1 holds its arms at the majority-class share - but it holds everything
there. Without the rotation angles the two classes are the same distribution,
so the control is impossible rather than hard, and no arm could pass it. That
is addendum 2, and the rule it adds: a positive control must come with a
demonstration that something passes it.

R1 v2 separates the two questions. The weight-n witness separates the classes
by tens of standard deviations up to alpha = 0.4 and degrades at 0.8, while
the low-weight features vary more and more with alpha and never carry the
label: across both sizes and all four amplitudes the arms stay within a few
points of the majority-class share, in both directions.

Those few points are not a finding either way. At 120 states a five-fold
score wobbles by that much, which is exactly why the study declares the
dataset draw as its unit of analysis and bootstraps over twenty of them
rather than reading a single number. One earlier unseeded probe of this same
sweep produced 0.658 at alpha = 0.2, n = 8; under the seed above the same
cell reads 0.483. It was noise, and it is recorded here because an
unreproduced number that happens to support the design is the easiest kind
to keep.""")


if __name__ == "__main__":
    main()
