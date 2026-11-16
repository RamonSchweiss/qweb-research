"""Primitives: TFIM ground states, cat states, two-qubit marginals, features.

Everything here is checked against a slower reference below.
"""
import numpy as np
from itertools import combinations
from scipy.sparse import identity, kron, csr_matrix
from scipy.sparse.linalg import eigsh

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


# ---------------------------------------------------------------- marginals
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


# ---------------------------------------------------------------- reference
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
