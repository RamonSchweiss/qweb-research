"""The QCNN arm: training and scoring, as registered.

Cost, from section 3 of the note and A3.4 of addendum 3:

    C = -(1/m) sum_i s_i <Z>_i      s_i = +1 / -1 from the label

which is linear in the readout, so its gradient coefficient is the constant
-s_i/m and never depends on the current prediction. Prediction is the sign of
<Z> at the readout qubit; the score is the share correct on held-out states.

All starts of one draw are trained together in one batched call, which is
what makes the registered budget affordable (A3.7).
"""
import numpy as np
import real


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
        zz, gg = real.grads(np.repeat(psi[lo:hi][None], S, axis=0), n, ops,
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
