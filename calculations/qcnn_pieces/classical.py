"""The classical arms: Pauli features of bounded bodyness, two model classes.

Features. Every Pauli string of weight 1..k, read off the k-site reduced
density matrices rather than by one matrix-vector product per string. The
two routes are checked against each other in the build printout; this one is
used because the slow one is unaffordable at weight 4.

Model classes. Addendum 1, point 2: every classical arm runs with a linear
and a nonlinear classifier, and the stronger of the two stands for "the
features carry the label". The weaker alone may never support a claim that
they do not. Same two classes, same declared grids, same folds, for every arm
and every size -- and the hyperparameter is chosen inside the TRAINING set
only (addendum 3, A3.5). The test set is never touched by that choice.
"""
import numpy as np
from itertools import combinations, product
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.metrics.pairwise import rbf_kernel
from sklearn.model_selection import GridSearchCV

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
