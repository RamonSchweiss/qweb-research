"""The same circuit in real arithmetic, with the gradient contracted directly.

Two exact changes, neither an approximation:

  * every gate in this circuit is real - RY, CZ and controlled-RY all are - and
    so are the input states of both datasets: a transverse-field Ising
    Hamiltonian is a real symmetric matrix, and the cat states are built from
    RY. So the whole simulation runs in float64 instead of complex128. A real
    multiply is one operation where a complex multiply is six.

  * the backward pass never materialises dU|psi>. The gradient of one gate is
    2 Re <lam| dU |psi> = 2 Re sum_ij dU_ij M_ij with M_ij = sum <lam_i, psi_j>,
    which is four inner products over the untouched arrays. The previous
    version built a full copy of the state per parameter per step, which at
    n = 12 was 32 MB copied seventy times a step.

Checked against the complex reference in qcnn.py, which was checked against a
dense construction.
"""
import numpy as np
from qcnn import build


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
