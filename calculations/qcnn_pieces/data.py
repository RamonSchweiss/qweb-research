"""The two datasets of design_qcnn_bodyness_EN.md section 4, as amended.

D1  Transverse-field Ising ground states, exact diagonalisation, the field
    swept across the critical point, labelled by phase. The dataset the
    reproduced claim is about.

D2  R1 version 2 of addendum 2, A2.3: the sign of a cat state with a local
    RY(alpha_j) per site, alpha_j uniform on (-alpha, alpha) independent of
    the label, alpha = 0.4.

One decision D1 needs that the note does not make. "Swept across the critical
point" leaves open whether the sweep includes the neighbourhood of h = 1. At
finite n the transition is rounded over a width that scales as 1/n (the 1D
Ising correlation-length exponent is 1), and inside that window the two
phases' ground states overlap so strongly that no arm can separate them. That
puts a common error floor under every arm at once, which compresses the
differences between them and so makes H1 -- the convenient hypothesis --
easier to satisfy; it also raises the noise floor, which can void a verdict
outright.

Decided 15 November 2026: the primary D1 keeps the whole sweep,

    h uniform on (0, 2), label = [h > 1],

because D1 is the dataset the claim is about and A1.7 protects it as
registered. A cleaned-up D1 would be a friendlier benchmark than the one
being reproduced. The window variant is run beside it as a declared
sensitivity check at n = 8 only -- window = 2.0 excludes |h - 1| < 2/n -- with
the expected direction stated in advance: removing the window should WIDEN
the differences between arms. If a verdict moves, the printout says so.

"""
import numpy as np
import prim

ALPHA = 0.4             # addendum 2, A2.5
WINDOW_C = 0.0          # primary D1: nothing excluded. 2.0 is the
                        # sensitivity variant of n = 8 (see above).
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
        H = prim.h_tfim(n, hk)
        assert np.count_nonzero(H.imag.data) == 0, "TFIM term is not real"
        Hr = H.real
        g = prim.ground(Hr).real
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
        v = prim.cat_ry(n, 1 if y[k] else -1, al[k])
        assert np.max(np.abs(v.imag)) < 1e-12
        psi[k] = v.real
    return psi, y, al


def split(psi, y, draw_seed, n, m_train=M_TRAIN, m_test=M_TEST):
    """One shuffled split per draw. Every arm gets the same one."""
    rng = np.random.default_rng((draw_seed, n, 99))
    idx = rng.permutation(len(y))
    tr, te = idx[:m_train], idx[m_train:m_train + m_test]
    return (psi[tr], y[tr]), (psi[te], y[te])
