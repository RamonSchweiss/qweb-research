"""Everything behind qcnn_bodyness.py: states, features, circuit, arms, verdicts.

A module, not a script. qcnn_bodyness.py is the script.

Assembled from seven checked pieces. The layers, and what each was checked
against, are in designs/design_qcnn_bodyness_EN_addendum_3.md section A3.6.
The slow reference is included deliberately: the fast path is only as
trustworthy as the check against it, and that check cannot be repeated from a
file that does not contain both sides.

  primitives      Pauli strings, the TFIM Hamiltonian, exact ground states,
                  cat states, reduced density matrices, the two feature
                  routes
  reference       the circuit and its adjoint gradient, written for clarity,
                  one start at a time, complex arithmetic
  fast path       the same thing in real arithmetic, batched over starts,
                  with the gradient contracted into inner products rather
                  than materialised; 2.7x to 4.0x faster and verified against
                  the reference to 1.3e-15
  datasets        D1 (transverse-field Ising ground states, labelled by
                  phase) and D2 (R1 version 2 of addendum 2: the sign of a
                  cat state under local RY)
  arms            the QCNN trainer and the classical bodyness-k classifiers
  verdicts        the resolution rule of section 6 and the four verdicts,
                  which never include "equivalent"
"""

import numpy as np
from itertools import combinations, product
from scipy.sparse import identity, kron, csr_matrix
from scipy.sparse.linalg import eigsh
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.metrics.pairwise import rbf_kernel
from sklearn.model_selection import GridSearchCV



# ==========================================================================
# primitives: states, Hamiltonians, features
# ==========================================================================

I2 = csr_matrix(np.eye(2))

P = {"X": csr_matrix(np.array([[0, 1], [1, 0]], dtype=complex)),
     "Y": csr_matrix(np.array([[0, -1j], [1j, 0]], dtype=complex)),
     "Z": csr_matrix(np.array([[1, 0], [0, -1]], dtype=complex))}

PD = {k: v.toarray() for k, v in P.items()}

def op_on(n, where):
    out = None
    for i in range(n):
        m = P[where[i]] if i in where else I2
        out = m if out is None else kron(out, m, format="csr")
    return out

def h_tfim(n, h):
    H = csr_matrix((2 ** n, 2 ** n), dtype=complex)
    for i in range(n - 1):
        H = H - op_on(n, {i: "Z", i + 1: "Z"})
    for i in range(n):
        H = H - h * op_on(n, {i: "X"})
    return H

def ground(H, seed=0):
    """Exact ground state, with the solver's starting vector under control.

    eigsh hands ARPACK a random starting vector when none is given, and that
    stream is not numpy's global one: two calls on the same matrix differed
    element-wise by 3.2e-14, and np.random.seed before them changed nothing.
    The deviation is far too small to move a classification, but a figure
    this repository promises to reproduce may not rest on a stream nobody
    seeded -- that is the defect design_cut_degeneracy_EN_addendum_4.md was
    written about. v0 is therefore fixed from a declared seed, and the
    datasets are bit-identical between runs.
    """
    v0 = np.random.default_rng(seed).normal(size=H.shape[0])
    w, v = eigsh(H, k=1, which="SA", maxiter=100000, v0=v0)
    psi = v[:, 0]
    return (psi / np.linalg.norm(psi)).astype(complex)

def cat_ry(n, sign, alphas):
    v = np.zeros(2 ** n, dtype=complex)
    v[0] = 1 / np.sqrt(2)
    v[-1] = sign / np.sqrt(2)
    U = np.array([[1.0]], dtype=complex)
    for a in alphas:
        c, s = np.cos(a / 2), np.sin(a / 2)
        U = np.kron(U, np.array([[c, -s], [s, c]], dtype=complex))
    return U @ v

def rho2_batch(psi, n, i, j):
    """Reduced 2-qubit density matrices on sites (i, j) for a batch.

    psi has shape (B, 2**n), qubit 0 is the most significant bit.
    Returns (B, 4, 4).
    """
    B = psi.shape[0]
    a, b = min(i, j), max(i, j)
    # split the 2**n axis into (left, 2, mid, 2, right)
    left = 2 ** a
    mid = 2 ** (b - a - 1)
    right = 2 ** (n - b - 1)
    t = psi.reshape(B, left, 2, mid, 2, right)
    # move the two physical axes to the front of the trace-out axes
    t = np.transpose(t, (0, 2, 4, 1, 3, 5)).reshape(B, 4, left * mid * right)
    rho = np.einsum("bik,bjk->bij", t, t.conj())
    if i > j:                                    # swap the two sites back
        rho = rho.reshape(B, 2, 2, 2, 2).transpose(0, 2, 1, 4, 3).reshape(B, 4, 4)
    return rho

def feature_spec(n, max_weight):
    """List of (sites, labels) for every Pauli string of weight 1..max_weight."""
    spec = []
    for w in range(1, max_weight + 1):
        for sites in combinations(range(n), w):
            for lab in np.ndindex(*([3] * w)):
                spec.append((sites, tuple("XYZ"[l] for l in lab)))
    return spec

def features_batch(psi, n, max_weight=2):
    """All Pauli expectations of weight <= max_weight, from the 2-qubit marginals.

    Returns (B, F) in the order of feature_spec(n, max_weight).
    """
    assert max_weight == 2, "built for weight 2; higher weights need bigger marginals"
    B = psi.shape[0]
    rho = {}
    for i, j in combinations(range(n), 2):
        rho[(i, j)] = rho2_batch(psi, n, i, j)
    out = []
    for sites, labs in feature_spec(n, max_weight):
        if len(sites) == 1:
            i = sites[0]
            j = 0 if i != 0 else 1
            r = rho[(min(i, j), max(i, j))]
            O = np.kron(PD[labs[0]], np.eye(2)) if i < j else np.kron(np.eye(2), PD[labs[0]])
        else:
            i, j = sites
            r = rho[(i, j)]
            O = np.kron(PD[labs[0]], PD[labs[1]])
        out.append(np.real(np.einsum("bij,ji->b", r, O)))
    return np.stack(out, axis=1)

def features_slow(psi, n, max_weight=2):
    """The slow way: one sparse matvec per Pauli string per state."""
    out = []
    for s in psi:
        row = []
        for sites, labs in feature_spec(n, max_weight):
            where = {q: l for q, l in zip(sites, labs)}
            row.append(float(np.real(np.conj(s) @ (op_on(n, where) @ s))))
        out.append(row)
    return np.array(out)



# ==========================================================================
# the slow reference circuit and its adjoint gradient
# ==========================================================================

def _ry(t):
    c, s = np.cos(t / 2), np.sin(t / 2)
    return np.array([[c, -s], [s, c]], dtype=complex)

def _dry(t):
    c, s = np.cos(t / 2), np.sin(t / 2)
    return 0.5 * np.array([[-s, -c], [c, -s]], dtype=complex)

CZ = np.diag([1.0, 1.0, 1.0, -1.0]).astype(complex).reshape(2, 2, 2, 2)

def apply1(psi, n, q, U):
    """U (2x2) on qubit q of a batch psi (B, 2**n). Qubit 0 is most significant."""
    B = psi.shape[0]
    left, right = 2 ** q, 2 ** (n - q - 1)
    t = psi.reshape(B, left, 2, right)
    return np.einsum("ij,bljr->blir", U, t, optimize=True).reshape(B, 2 ** n)

def apply2(psi, n, a, b, U):
    """U[out_a, out_b, in_a, in_b] on qubits (a, b) of a batch psi (B, 2**n)."""
    B = psi.shape[0]
    lo, hi = min(a, b), max(a, b)
    L, M, R = 2 ** lo, 2 ** (hi - lo - 1), 2 ** (n - hi - 1)
    t = psi.reshape(B, L, 2, M, 2, R)
    if a < b:                      # in_a sits on the lo axis, in_b on the hi axis
        out = np.einsum("pqij,zlimjr->zlpmqr", U, t, optimize=True)
    else:                          # the other way round
        out = np.einsum("pqij,zljmir->zlqmpr", U, t, optimize=True)
    return out.reshape(B, 2 ** n)

def _cry(phi, deriv=False):
    """Controlled RY as U[out_c, out_t, in_c, in_t]. Control fires on |1>."""
    U = np.zeros((2, 2, 2, 2), dtype=complex)
    if not deriv:
        U[0, 0, 0, 0] = U[0, 1, 0, 1] = 1.0
    R = _dry(phi) if deriv else _ry(phi)
    U[1, :, 1, :] = R
    return U

def build(n):
    """Ops and parameter count. Op forms:
         ("ry", q, p)                single-qubit RY with parameter p
         ("cz", a, b)                no parameter
         ("cry", control, target, p) controlled RY with parameter p
    """
    active = list(range(n))
    ops, p = [], 0
    while len(active) > 1:
        pairs = [(active[i], active[i + 1]) for i in range(0, len(active) - 1, 2)]
        leftover = active[len(pairs) * 2:]
        c0, c1, c2, c3, k0, k1 = p, p + 1, p + 2, p + 3, p + 4, p + 5
        p += 6
        for a, b in pairs:                                  # convolution
            ops += [("ry", a, c0), ("ry", b, c1), ("cz", a, b),
                    ("ry", a, c2), ("ry", b, c3)]
        for a, b in pairs:                                  # coherent pooling
            ops += [("cry", b, a, k0), ("ry", a, k1)]
        active = [a for a, _ in pairs] + leftover
    ops.append(("ry", active[0], p))
    return ops, p + 1, active[0]

def _apply(psi, n, op, theta, dagger=False, deriv=False):
    kind = op[0]
    if kind == "ry":
        _, q, p = op
        U = _dry(theta[p]) if deriv else _ry(theta[p])
        if dagger:
            U = U.conj().T
        return apply1(psi, n, q, U)
    if kind == "cz":
        _, a, b = op
        return apply2(psi, n, a, b, CZ)                      # real, self-inverse
    _, c, t, p = op
    U = _cry(theta[p], deriv=deriv)
    if dagger:
        U = U.conj().transpose(2, 3, 0, 1)
    return apply2(psi, n, c, t, U)

def forward(psi0, n, ops, theta):
    psi = psi0
    for op in ops:
        psi = _apply(psi, n, op, theta)
    return psi

def expect_z(psi, n, q):
    B = psi.shape[0]
    left, right = 2 ** q, 2 ** (n - q - 1)
    t = psi.reshape(B, left, 2, right)
    w = np.abs(t) ** 2
    return (w[:, :, 0, :].sum(axis=(1, 2)) - w[:, :, 1, :].sum(axis=(1, 2)))

def apply_z(psi, n, q):
    B = psi.shape[0]
    left, right = 2 ** q, 2 ** (n - q - 1)
    t = psi.reshape(B, left, 2, right).copy()
    t[:, :, 1, :] *= -1.0
    return t.reshape(B, 2 ** n)

def grad(psi0, n, ops, theta, out_q, coeff):
    """Gradient of sum_s coeff[s] * <Z_out>_s, adjoint method.

    Returns (value_per_sample, gradient) with gradient.shape == theta.shape.
    """
    psi = forward(psi0, n, ops, theta)
    f = expect_z(psi, n, out_q)
    lam = apply_z(psi, n, out_q) * coeff[:, None]
    g = np.zeros_like(theta)
    for op in reversed(ops):
        psi = _apply(psi, n, op, theta, dagger=True)
        if op[0] != "cz":
            p = op[-1]
            d = _apply(psi, n, op, theta, deriv=True)
            g[p] += 2.0 * np.real(np.sum(np.conj(lam) * d))
        lam = _apply(lam, n, op, theta, dagger=True)
    return f, g

def gradient_gate(n=6, B=4, seed=11, tol=1e-7):
    """Invalidating condition 3 in its gradient form: analytic against a slower
    implementation, element by element, not against a norm or a count."""
    rng = np.random.default_rng(seed)
    ops, npar, out_q = build(n)
    theta = rng.uniform(-np.pi, np.pi, size=npar)
    psi0 = rng.normal(size=(B, 2 ** n)) + 1j * rng.normal(size=(B, 2 ** n))
    psi0 /= np.linalg.norm(psi0, axis=1, keepdims=True)
    coeff = rng.normal(size=B)

    _, g = grad(psi0, n, ops, theta, out_q, coeff)

    fd = np.zeros_like(theta)
    eps = 1e-6
    for k in range(npar):
        tp, tm = theta.copy(), theta.copy()
        tp[k] += eps
        tm[k] -= eps
        fp = float(coeff @ expect_z(forward(psi0, n, ops, tp), n, out_q))
        fm = float(coeff @ expect_z(forward(psi0, n, ops, tm), n, out_q))
        fd[k] = (fp - fm) / (2 * eps)
    dev = float(np.max(np.abs(g - fd)))
    return dev, dev < tol, npar



# ==========================================================================
# the fast path: real arithmetic, batched, contracted gradient
# ==========================================================================

def ry_r(t):
    c, s = np.cos(t / 2), np.sin(t / 2)
    return np.array([[c, -s], [s, c]])

def dry_r(t):
    c, s = np.cos(t / 2), np.sin(t / 2)
    return 0.5 * np.array([[-s, -c], [c, -s]])

def ry_mats(th, deriv=False):
    f = dry_r if deriv else ry_r
    return np.stack([f(t) for t in th])

def _axes(n, q):
    return 2 ** q, 2 ** (n - q - 1)

def ap1(psi, n, q, U):
    """In place. psi (S, B, 2**n) real, U (S, 2, 2) real."""
    S = psi.shape[0]
    L, R = _axes(n, q)
    t = psi.reshape(S, -1, L, 2, R)
    sh = (S, 1, 1, 1)
    a, b = t[:, :, :, 0, :], t[:, :, :, 1, :]
    new0 = U[:, 0, 0].reshape(sh) * a + U[:, 0, 1].reshape(sh) * b
    t[:, :, :, 1, :] = U[:, 1, 0].reshape(sh) * a + U[:, 1, 1].reshape(sh) * b
    t[:, :, :, 0, :] = new0
    return psi

def ap_cz(psi, n, a, b):
    S = psi.shape[0]
    lo, hi = min(a, b), max(a, b)
    L, M, R = 2 ** lo, 2 ** (hi - lo - 1), 2 ** (n - hi - 1)
    t = psi.reshape(S, -1, L, 2, M, 2, R)
    t[:, :, :, 1, :, 1, :] *= -1.0
    return psi

def _ctrl_view(psi, n, c, tq):
    """View of the control-1 block with the TARGET axis at index 3.

    The reshape puts the lower-numbered qubit at axis 3 and the higher at
    axis 5, so which of the two is the control decides whether an axis swap
    is needed. Getting this wrong is silent, so it is checked against the
    reference implementation rather than reasoned about twice.
    """
    S = psi.shape[0]
    lo, hi = min(c, tq), max(c, tq)
    L, M, R = 2 ** lo, 2 ** (hi - lo - 1), 2 ** (n - hi - 1)
    t = psi.reshape(S, -1, L, 2, M, 2, R)
    if c < tq:                      # control at lo, target at hi
        return t[:, :, :, 1].swapaxes(3, 4)          # (S,B,L,2,M,R)
    return t[:, :, :, :, :, 1]                       # (S,B,L,2,M,R)

def ap_cry(psi, n, c, tq, U):
    """In place, controlled on |1> of qubit c, RY on qubit tq."""
    S = psi.shape[0]
    v = _ctrl_view(psi, n, c, tq)
    sh = (S, 1, 1, 1, 1)
    a, b = v[:, :, :, 0], v[:, :, :, 1]
    new0 = U[:, 0, 0].reshape(sh) * a + U[:, 0, 1].reshape(sh) * b
    v[:, :, :, 1] = U[:, 1, 0].reshape(sh) * a + U[:, 1, 1].reshape(sh) * b
    v[:, :, :, 0] = new0
    return psi

def _dot(a, b):
    """Sum of a*b over every axis but the first."""
    idx = "s" + "abcdefgh"[:a.ndim - 1]
    return np.einsum(f"{idx},{idx}->s", a, b, optimize=True)

def _M(psi, lam, n, q, ctrl=None):
    """M[s,i,j] = sum over everything else of lam_i * psi_j on qubit q.

    With ctrl given, both are restricted to the control-1 block of that qubit.
    No copy and no temporary: four inner products over the arrays as they are.
    """
    if ctrl is None:
        S = psi.shape[0]
        L, R = _axes(n, q)
        tp = psi.reshape(S, -1, L, 2, R)
        tl = lam.reshape(S, -1, L, 2, R)
        ax = 3
    else:
        tp = _ctrl_view(psi, n, ctrl, q)
        tl = _ctrl_view(lam, n, ctrl, q)
        S, ax = tp.shape[0], 3
    M = np.empty((S, 2, 2))
    for i in range(2):
        li = np.take(tl, i, axis=ax)
        for j in range(2):
            M[:, i, j] = _dot(li, np.take(tp, j, axis=ax))
    return M

def fwd(psi0, n, ops, theta):
    psi = psi0.copy()
    for op in ops:
        if op[0] == "cz":
            ap_cz(psi, n, op[1], op[2])
        elif op[0] == "ry":
            ap1(psi, n, op[1], ry_mats(theta[:, op[2]]))
        else:
            ap_cry(psi, n, op[1], op[2], ry_mats(theta[:, op[3]]))
    return psi

def _undo(psi, n, op, theta):
    if op[0] == "cz":
        return ap_cz(psi, n, op[1], op[2])
    if op[0] == "ry":
        return ap1(psi, n, op[1],
                   ry_mats(theta[:, op[2]]).transpose(0, 2, 1))
    return ap_cry(psi, n, op[1], op[2],
                  ry_mats(theta[:, op[3]]).transpose(0, 2, 1))

def ez(psi, n, q):
    S = psi.shape[0]
    L, R = _axes(n, q)
    w = psi.reshape(S, -1, L, 2, R) ** 2
    return w[:, :, :, 0, :].sum(axis=(2, 3)) - w[:, :, :, 1, :].sum(axis=(2, 3))

def grads(psi0, n, ops, theta, out_q, coeff):
    """coeff (S, B). Returns f (S, B) and g (S, npar)."""
    psi = fwd(psi0, n, ops, theta)
    f = ez(psi, n, out_q)
    S, B = psi.shape[0], psi.shape[1]
    L, R = _axes(n, out_q)
    lam = psi.reshape(S, B, L, 2, R) * coeff[:, :, None, None, None]
    lam = lam.copy()
    lam[:, :, :, 1, :] *= -1.0
    lam = lam.reshape(S, B, 2 ** n)
    psi = psi.copy()
    g = np.zeros_like(theta)
    for op in reversed(ops):
        _undo(psi, n, op, theta)
        if op[0] == "ry":
            dU = ry_mats(theta[:, op[2]], deriv=True)
            M = _M(psi, lam, n, op[1])
            g[:, op[2]] += 2.0 * np.einsum("sij,sij->s", dU, M)
        elif op[0] == "cry":
            dU = ry_mats(theta[:, op[3]], deriv=True)
            M = _M(psi, lam, n, op[2], ctrl=op[1])
            g[:, op[3]] += 2.0 * np.einsum("sij,sij->s", dU, M)
        _undo(lam, n, op, theta)
    return f, g



# ==========================================================================
# the two datasets
# ==========================================================================

ALPHA = 0.4             # addendum 2, A2.5

WINDOW_C = 0.0          # primary D1: nothing excluded. 2.0 is the

M_TRAIN = 200           # addendum 3, A3.4

M_TEST = 200            # section 5, fixes granularity at 1/200

def _fields(n, m, rng, window=None):
    w = WINDOW_C if window is None else window
    out = []
    while len(out) < m:
        h = rng.uniform(0.0, 2.0)
        if w == 0.0 or abs(h - 1.0) >= w / n:
            out.append(h)
    return np.array(out)

def d1(n, draw_seed, m=None, resid_tol=1e-8, window=None):
    """TFIM ground states and phase labels. Returns (states, labels, fields).

    The Hamiltonian is checked to be exactly real -- not nearly real -- and
    then diagonalised in real arithmetic, so no global phase arises to be
    divided out. Each ground state is checked by its own residual
    ||H psi - E psi||, which is what "the ground state is accurate" means;
    a small imaginary part or a unit norm would not establish it.
    """
    m = m or (M_TRAIN + M_TEST)
    rng = np.random.default_rng((draw_seed, n, 1))
    h = _fields(n, m, rng, window)
    psi = np.empty((m, 2 ** n))
    worst = 0.0
    for k, hk in enumerate(h):
        H = h_tfim(n, hk)
        assert np.count_nonzero(H.imag.data) == 0, "TFIM term is not real"
        Hr = H.real
        g = ground(Hr).real
        e = float(g @ (Hr @ g))
        r = float(np.linalg.norm(Hr @ g - e * g))
        worst = max(worst, r)
        psi[k] = g * np.sign(g[int(np.argmax(np.abs(g)))])
    assert worst <= resid_tol, f"largest ground-state residual {worst:.2e}"
    y = (h > 1.0).astype(int)
    return psi, y, h

def d2(n, draw_seed, m=None, alpha=ALPHA):
    """R1 v2: cat sign under local RY. Returns (states, labels, angles)."""
    m = m or (M_TRAIN + M_TEST)
    rng = np.random.default_rng((draw_seed, n, 2))
    y = rng.integers(0, 2, size=m)
    al = rng.uniform(-alpha, alpha, size=(m, n))
    psi = np.empty((m, 2 ** n))
    for k in range(m):
        v = cat_ry(n, 1 if y[k] else -1, al[k])
        assert np.max(np.abs(v.imag)) < 1e-12
        psi[k] = v.real
    return psi, y, al

def split(psi, y, draw_seed, n, m_train=M_TRAIN, m_test=M_TEST):
    """One shuffled split per draw. Every arm gets the same one."""
    rng = np.random.default_rng((draw_seed, n, 99))
    idx = rng.permutation(len(y))
    tr, te = idx[:m_train], idx[m_train:m_train + m_test]
    return (psi[tr], y[tr]), (psi[te], y[te])



# ==========================================================================
# the QCNN arm
# ==========================================================================

CACHE_BYTES = 8e6   # block only when the batch array exceeds this

def block_size(starts, B, n):
    """How many states per block. Declared rule, not a tuned constant.

    Block only where the array does not fit, and then to the measured
    optimum. At the registered 5 starts and 200 states the batch array is
    2.05 MB at n = 8, 8.19 MB at n = 10 and 32.77 MB at n = 12, against
    CACHE_BYTES = 8 MB, so the rule leaves n = 8 unblocked and blocks the
    other two. Seconds per step, full batch against blocked, over the
    measurement rounds made for A3.8 -- several rounds, because this is a
    shared machine and one round does not support three digits:

        n =  8   0.297 / 0.273   vs   0.318 / 0.305   blocking COSTS 7-12 %
        n = 10   1.334 / 1.183   vs   1.126 / 1.170   gain 1.18 / 1.01
        n = 12   9.511 / 7.866 / 10.383  vs  5.510 / 5.363 / 6.093
                                                      gain 1.73 / 1.47 / 1.70

    At n = 12 the gain is large and survives every round, and at n = 8
    blocking reliably costs, so the rule is right to skip it there. At n = 10
    the two rounds disagree (1.18 against 1.01) and the honest statement is
    that blocking is NOT demonstrably better there -- the rule blocks, and
    that is defended as not worse, not as faster.

    One caveat that belongs in plain sight: at n = 10 the array is 8.19 MB
    against a threshold of 8 MB, a margin of 2.4 per cent, so a threshold set
    3 per cent higher would flip the decision at that size. The measurement
    above is why the flip costs nothing either way. An earlier version of
    this docstring claimed the batch FITS at n = 10 and is therefore not
    blocked. That was false -- 8.19 MB is past 8 MB and the rule does block
    there -- and re-measuring is what found it.
    """
    if starts * B * 2 ** n * 8 <= CACHE_BYTES:
        return B
    return 25

def _grad_chunked(psi, n, ops, theta, out_q, coeff, chunk):
    """Gradient and readout over a batch, in blocks of `chunk` states.

    The gradient is a sum over states, so blocking is exact; only the order
    of the floating-point summation changes. Measured against the full-batch
    computation: relative gradient deviation 4.6e-15 at n = 12, readout
    bit-identical.

    Why bother: at n = 12 the full batch is a 33 MB array, far past any
    cache, so the gate layer is bandwidth-bound and not flop-bound. The full
    batch measured 9.511 s per step and blocking to 4 MB measured 5.510 --
    a factor 1.7 for a change of loop order and nothing else. The gain
    appears between 200 and 100 states, exactly where the array stops
    fitting, and is flat below. A second measurement on a busier machine
    gave 7.866 against 5.363, a factor 1.47: the factor depends on what else
    is competing for memory bandwidth, its direction does not.

    One trap this harness fell into, recorded so it is not fallen into
    twice: timing this with complex input doubles the bytes and the step
    time, and so overstates the budget by about a factor two. The states of
    this study are real.
    """
    S, B = theta.shape[0], psi.shape[0]
    g = np.zeros_like(theta)
    z = np.empty((S, B))
    for lo in range(0, B, chunk):
        hi = min(lo + chunk, B)
        zz, gg = grads(np.repeat(psi[lo:hi][None], S, axis=0), n, ops,
                            theta, out_q, coeff[:, lo:hi])
        z[:, lo:hi] = zz
        g += gg
    return z, g

def train(n, ops, npar, out_q, tr, te, starts=5, steps=40, seed=0,
          trace_every=0, optimiser="gd", lr=0.1,
          b1=0.9, b2=0.999, eps=1e-8, chunk=None):
    """One draw of the QCNN arm: `starts` random starts, trained together.

    Two step rules, both first-order on the linear cost of section 3:
    plain gradient descent, and Adam with the declared b1, b2, eps. Which
    one, and at which step size, is fixed by the criterion of addendum 3
    A3.4 as amended -- the pair that reaches the higher TRAINING score at
    the measured run length, because under-training the QCNN arm makes H1
    easier. No test score enters that choice.
    """
    psi_tr, y_tr = tr
    psi_te, y_te = te
    s_tr = np.where(y_tr > 0, 1.0, -1.0)
    s_te = np.where(y_te > 0, 1.0, -1.0)
    m = len(s_tr)
    rng = np.random.default_rng(seed)
    theta = rng.uniform(-np.pi, np.pi, size=(starts, npar))

    coeff = np.repeat((-s_tr / m)[None], starts, axis=0)
    chunk = chunk or block_size(starts, m, n)
    mt = np.zeros_like(theta)
    vt = np.zeros_like(theta)
    trace = []
    for t in range(steps):
        z, g = _grad_chunked(psi_tr, n, ops, theta, out_q, coeff, chunk)
        if optimiser == "gd":
            theta = theta - lr * g
        elif optimiser == "adam":
            mt = b1 * mt + (1 - b1) * g
            vt = b2 * vt + (1 - b2) * g * g
            mh = mt / (1 - b1 ** (t + 1))
            vh = vt / (1 - b2 ** (t + 1))
            theta = theta - lr * mh / (np.sqrt(vh) + eps)
        else:
            raise ValueError(optimiser)
        if trace_every and ((t + 1) % trace_every == 0 or t == 0):
            trace.append((t + 1, (np.sign(z) == s_tr).mean(axis=1).copy()))

    z_te, _ = _grad_chunked(psi_te, n, ops, theta, out_q,
                            np.zeros((starts, len(s_te))), chunk)
    per_start = (np.sign(z_te) == s_te).mean(axis=1)
    return per_start, theta, trace



# ==========================================================================
# the classical arms
# ==========================================================================

FOLDS = 5

C_GRID = [0.01, 0.1, 1.0, 10.0, 100.0]

L2_GRID = [0.0, 1.0]

GAMMA_MULT = [0.1, 1.0, 10.0, 100.0]   # multiples of 1/(p Var X)

SEED = 20261115

_P = {"I": np.eye(2), "X": np.array([[0, 1], [1, 0]], float),
      "Y": np.array([[0, -1j], [1j, 0]]), "Z": np.array([[1, 0], [0, -1]], float)}

def _kron_all(mats):
    out = np.array([[1.0 + 0j]])
    for m in mats:
        out = np.kron(out, m)
    return out

def _rho_k(psi, n, sites):
    """Reduced density matrices on `sites` for a batch of real states."""
    B = psi.shape[0]
    k = len(sites)
    t = psi.reshape((B,) + (2,) * n)
    t = np.moveaxis(t, [1 + s for s in sites], list(range(1, k + 1)))
    t = t.reshape(B, 2 ** k, 2 ** (n - k))
    return np.einsum("bik,bjk->bij", t, t, optimize=True)

def feature_names(n, max_weight):
    names = []
    for w in range(1, max_weight + 1):
        for sites in combinations(range(n), w):
            for labs in product("XYZ", repeat=w):
                names.append("".join(f"{l}{s}" for l, s in zip(labs, sites)))
    return names

def features(psi, n, max_weight):
    """All Pauli expectations of weight 1..max_weight. Shape (B, n_features)."""
    cols = []
    for w in range(1, max_weight + 1):
        paulis = [np.real_if_close(_kron_all([_P[l] for l in labs]))
                  for labs in product("XYZ", repeat=w)]
        Pst = np.stack(paulis)                      # (3^w, 2^w, 2^w)
        for sites in combinations(range(n), w):
            rho = _rho_k(psi, n, sites)
            cols.append(np.real(np.einsum("bij,pji->bp", rho, Pst,
                                          optimize=True)))
    return np.concatenate(cols, axis=1)

def gram_reduce(Xtr, Xte, eps=1e-10):
    """Replace p features by at most m columns, with no approximation.

    For L2-regularised logistic regression the optimum lies in the span of
    the training rows: w = X^T a. Then w.x_i = (K a)_i with K = X X^T, and
    ||w||^2 = a^T K a. Writing K = L L^T and b = L^T a gives w.x_i = (L b)_i
    and ||w||^2 = ||b||^2, so the problem is ordinary L2 logistic regression
    with L as the design matrix -- the same loss, the same penalty, the same
    optimum. Test rows map through w.x = b^T L^+ (X x).

    At n = 12 this turns 46,665 columns into 200. It is an identity, not a
    dimension reduction: the fit it produces is the fit on all the features,
    which is checked against the direct one in the build printout.

    Only the linear arm may use it. A tree ensemble is not a linear model in
    these features and its fit is not preserved by this map.

    And only where p > m. Below that there is nothing to gain, and a weakly
    regularised fit on fewer features than rows is ill-conditioned enough
    that the two parameterisations stop at different points -- same loss,
    same minimum, different place to halt. Measured: at p = 60 against
    m = 120 and C = 100 the decision values differ by 1.1 while the score is
    identical. At p > m, which is every arm this is used for, all five grid
    values agree to 1e-14. The rule is therefore p > m, and the gate in
    qcnn_bodyness.py checks the agreement at the shapes actually used.
    """
    K = Xtr @ Xtr.T
    w, V = np.linalg.eigh(K)
    keep = w > max(eps, w.max() * eps)
    L = V[:, keep] * np.sqrt(w[keep])
    Linv = (V[:, keep] / np.sqrt(w[keep])).T              # L^+ = (L^T L)^-1 L^T
    return L, (Xte @ Xtr.T) @ Linv.T

def arm_scores(Xtr, ytr, Xte, yte, trees=True):
    """One arm, three model classes.

    linear   L2 logistic regression, C over C_GRID by 5-fold CV inside the
             training set; through gram_reduce where p > m.
    kernel   RBF-kernel SVM, C over the same grid, gamma = 1/(p Var X).
             Precomputed Gram, so its cost is in m and not in p.
    trees    HistGradientBoosting as in the registered probe of addendum 2,
             l2_regularization over L2_GRID by the same folds.

    Addendum 1 point 2 asks for a linear and a nonlinear class and lets the
    stronger stand. The kernel class is the second nonlinear one, added
    because the tree ensemble does not scale in p: one fit on 7,458 features
    is 141 s, which is 79 hours over the registered budget at weight 4, while
    the kernel arm is 0.1 minutes at every size. Both reasons point the same
    way and neither is hidden behind the other: in this regime -- 200 rows
    against tens of thousands of columns -- a kernel method is also the
    stronger classifier, and at weight 4 the arm's only remaining job is to
    catch a leak, which wants the strongest classifier available.

    trees=False drops the tree class for that arm. It is set only where the
    tree class is unaffordable, which is weight 4, and the restriction is
    recorded in the printout beside the score rather than left implicit.
    """
    out = {"features": int(Xtr.shape[1])}
    if Xtr.shape[1] > Xtr.shape[0]:
        Ltr, Lte = gram_reduce(Xtr, Xte)
        out["gram_columns"] = int(Ltr.shape[1])
    else:
        Ltr, Lte = Xtr, Xte
    lin = GridSearchCV(LogisticRegression(max_iter=5000),
                       {"C": C_GRID}, cv=FOLDS, n_jobs=1).fit(Ltr, ytr)
    out["linear"] = float(lin.score(Lte, yte))
    out["C"] = lin.best_params_["C"]

    # gamma = 1/(p Var X) is sklearn's "scale", and at p = 46,665 it makes the
    # RBF kernel so flat that it is nearly linear -- the arm would stop being
    # a nonlinear class exactly where it is needed as one. So the width is
    # chosen on the same folds, over multiples of that scale, declared here.
    g0 = 1.0 / (Xtr.shape[1] * Xtr.var())
    bestk = (-1.0, None, None)
    for mult in GAMMA_MULT:
        Ktr = rbf_kernel(Xtr, Xtr, gamma=mult * g0)
        g = GridSearchCV(SVC(kernel="precomputed"), {"C": C_GRID}, cv=FOLDS,
                         n_jobs=1).fit(Ktr, ytr)
        if g.best_score_ > bestk[0]:
            bestk = (g.best_score_, g, mult)
    _, g, mult = bestk
    out["kernel"] = float(g.score(rbf_kernel(Xte, Xtr, gamma=mult * g0), yte))
    out["C_kernel"] = g.best_params_["C"]
    out["gamma_mult"] = mult

    if trees:
        nl = GridSearchCV(HistGradientBoostingClassifier(max_iter=200,
                                                         random_state=SEED),
                          {"l2_regularization": L2_GRID}, cv=FOLDS,
                          n_jobs=1).fit(Xtr, ytr)
        out["trees"] = float(nl.score(Xte, yte))
        out["l2"] = nl.best_params_["l2_regularization"]
    return out

def arm_best(a):
    """The strongest model class for this arm. Addendum 1, point 2: the
    stronger stands for 'the features carry the label'; the weaker one alone
    may never support a claim that they do not."""
    return max(a[k] for k in ("linear", "kernel", "trees") if k in a)



# ==========================================================================
# the resolution rule and the four verdicts
# ==========================================================================

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
