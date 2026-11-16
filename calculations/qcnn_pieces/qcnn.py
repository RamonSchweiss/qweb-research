"""A QCNN with analytic gradients, and a gate that checks them.

Structure after Cong, Choi and Lukin (2019): per layer a convolution on
disjoint neighbouring pairs of the active qubits, then a pooling step that
halves the active set. Pooling is coherent - a controlled rotation with the
discarded qubit as control - so the whole circuit stays a unitary on the
statevector and no measurement has to be simulated mid-circuit.

Parameters are shared within a layer (translation invariance): four for the
convolution, two for the pooling, so six per layer.

Where the active count is odd, the leftover qubit is carried through the layer
untouched. Depth is therefore ceil(log2 n), which for n = 10 and 12 is not the
log2 n the design note names - see addendum 3 to that note.

Gradients are adjoint: one forward pass, one backward pass, all parameters at
once. The gate below checks them against central finite differences.
"""
import numpy as np

# ------------------------------------------------------------------ gates
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


# ------------------------------------------------------------------ circuit
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


def train(psi_tr, y_tr, n, steps=60, lr=0.1, seed=0):
    """Adam on the mean squared error of p = (1 + <Z>)/2 against the label.

    The recipe is not in the design note, which only says "trained by gradient
    descent on a linear cost". It is fixed here before the run: 60 steps,
    learning rate 0.1, full batch, parameters initialised uniformly in
    [-pi, pi]. Reported with the results rather than tuned against them.
    """
    rng = np.random.default_rng(seed)
    ops, npar, out_q = build(n)
    theta = rng.uniform(-np.pi, np.pi, size=npar)
    m = np.zeros(npar)
    v = np.zeros(npar)
    B = psi_tr.shape[0]
    b1, b2, eps = 0.9, 0.999, 1e-8
    for t in range(1, steps + 1):
        f = expect_z(forward(psi_tr, n, ops, theta), n, out_q)
        p = (1.0 + f) / 2.0
        coeff = (p - y_tr) / B
        _, g = grad(psi_tr, n, ops, theta, out_q, coeff)
        m = b1 * m + (1 - b1) * g
        v = b2 * v + (1 - b2) * g * g
        mh = m / (1 - b1 ** t)
        vh = v / (1 - b2 ** t)
        theta -= lr * mh / (np.sqrt(vh) + eps)
    return theta, ops, out_q


def accuracy(psi, y, n, ops, theta, out_q):
    f = expect_z(forward(psi, n, ops, theta), n, out_q)
    pred = (f < 0).astype(float)          # <Z> < 0 means more weight on |1>
    return float(np.mean(pred == y))
