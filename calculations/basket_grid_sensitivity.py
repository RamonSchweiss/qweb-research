"""Does a 16-point grid decide a crossover shift? It fixes the sign, not the size.

A method check, not a result of QWeb Research. It concerns a published
measurement by Daniel Hug (qubit-lab.ch): classical Monte Carlo against
low-depth quantum amplitude estimation, pricing a one-year call on a 50/50
basket of two correlated shares, strike 100, volatilities 28% and 58%, on an
8-qubit grid of 16 x 16 = 256 joint scenarios. The crossover below which
classical Monte Carlo is ahead was reported at about 7,000 oracle calls at
correlation 0.5, and at about 10,000 at correlation 0.

Why the question was asked. The height of the classical error curve is fixed by
one number, the coefficient of variation of the payoff, since the relative
standard error of a Monte Carlo estimate is CV / sqrt(n). Removing the
correlation shifts that curve by the ratio of the two CVs, and the direction of
the shift is part of where the classical and quantum curves meet. On 27 October
2026, before the correlation run, this script found that the published
parameters did not determine that direction: grid constructions reproducing both
reported reference prices disagreed on the sign.

What the disclosure settled. On 31 October the author published the
construction: 16 points per share, evenly spaced in log-price, truncated at
+-3.5 sigma, weighted by the normal density at the nodes and renormalised;
drift and discounting 3%, Ito-corrected; correlation applied in standard-normal
space. Two findings, and the second matters more than the first.

  1. The sign does flip, and this script locates where. Within the truncation
     family the CV shift crosses zero near +-3.9 sigma, which is why the
     author's +-3.5 falls while +-4 to +-5 rise. The earlier caveat was
     correct.

  2. The sign is irrelevant. Across every truncation from +-3 to +-5 the shift
     stays under 1.4% in magnitude. Pushed through the author's own fitted
     slopes, the largest of them moves the crossover by about 3%; even
     equal-probability bins, which do not reproduce the reference prices, give
     about 11%. The observed move was 43%. No grid choice in this family can
     account for it, so the author's conclusion -- that the quantum side moved,
     through a 13% smaller amplitude -- holds independently of the grid.

The same conversion shows that cause to be sufficient rather than merely
plausible: a 13.35% smaller amplitude, taken through the fitted slopes, predicts
a crossover move of about +42% against the +43% reported.

Reproduction. This script gets 16.2650 and 14.0695 against the reported 16.2244
and 14.0586, and a CV shift of -0.41% against the reported -0.46%. The residual
quarter of a percent is most likely in how the +-3.5 sigma range is taken
relative to the drift; it does not affect any conclusion above.

Assumption behind the crossover conversion. It takes the two fitted power laws
to hold near the crossing with only their constants changing. That is enough for
an order-of-magnitude bound and not enough for a precise crossover location,
which is why the numbers above are stated as bounds and a check.

What this is not. It does not reproduce the quantum arm. The amplification
schedule is not recoverable from the published summary, so the quantum constant
is taken from the author's reported amplitude rather than computed here.

Standard library only, by design. No arguments; prints its own conclusion.

Ramon Schweiss, QWeb (c) Research. First version 27 October 2026; resolved
against the disclosed construction 31 October 2026.
"""

import math
from statistics import NormalDist

# --- the instance, as published and then disclosed -------------------------

S0 = 100.0           # initial price, both shares
K = 100.0            # strike
T = 1.0              # one year
V1, V2 = 0.28, 0.58  # volatilities
R = 0.03             # drift and discounting, disclosed 31 October
N = 16               # grid points per share: 16 x 16 = 256 = 8 qubits
DISCLOSED_SPAN = 3.5  # truncation in sigma, disclosed 31 October

REPORTED_PRICE = {0.5: 16.2244, 0.0: 14.0586}   # grid expectations
REPORTED_CV_SHIFT = -0.0046                     # -0.46%
REPORTED_SLOPES = (0.44, 0.86)                  # classical, amplitude estimation
REPORTED_CROSSOVER = (7000, 10000)              # oracle calls, rho 0.5 -> 0
REPORTED_AMPLITUDE_DROP = 0.1335                # 1 - 14.0586 / 16.2244

_ND = NormalDist()


# --- grid constructions ----------------------------------------------------

def nodes(kind, span=None):
    """Return (z, w): N standard-normal nodes with probability weights.

    "trunc" spaces nodes evenly over [-span, +span] and weights them by the
    normal density, renormalised. This is the disclosed construction.
    "equiprob" puts a node at the midpoint of each of N equal-probability bins
    and weights them equally. The two differ in how much tail the finite grid
    keeps, and that is what the sign of the CV shift turns on.
    """
    if kind == "equiprob":
        return ([_ND.inv_cdf((i + 0.5) / N) for i in range(N)], [1.0 / N] * N)

    z = [-span + 2.0 * span * i / (N - 1) for i in range(N)]
    p = [_ND.pdf(zi) for zi in z]
    s = sum(p)
    return z, [pi / s for pi in p]


# --- pricing on the grid ---------------------------------------------------

def price(grid, rho):
    """Discounted expectation and payoff CV on the grid.

    The second share is correlated in standard-normal space as
    y2 = rho * z1 + sqrt(1 - rho^2) * z2, leaving the marginals unchanged as
    rho moves. Each share follows the risk-neutral lognormal with the Ito
    correction, S = S0 * exp((r - sigma^2 / 2) T + sigma sqrt(T) Z).
    """
    z, w = grid
    root = math.sqrt(T)
    c = math.sqrt(1.0 - rho * rho)

    e1 = e2 = 0.0
    for i, z1 in enumerate(z):
        s1 = S0 * math.exp((R - 0.5 * V1 * V1) * T + V1 * root * z1)
        for j, z2 in enumerate(z):
            y2 = rho * z1 + c * z2
            s2 = S0 * math.exp((R - 0.5 * V2 * V2) * T + V2 * root * y2)
            pay = 0.5 * (s1 + s2) - K
            if pay <= 0.0:
                continue
            p = w[i] * w[j]
            e1 += p * pay
            e2 += p * pay * pay

    cv = math.sqrt(max(e2 - e1 * e1, 0.0)) / e1
    return e1 * math.exp(-R * T), cv


def crossover_move(cv_shift, amplitude_drop=0.0):
    """Factor by which the crossover in oracle calls moves.

    The two error curves are c_c / n**s_c and c_q / n**s_q. Amplitude
    estimation overtakes where n**(s_q - s_c) = c_q / c_c, so the crossover
    moves by (c_q / c_c) ** (1 / (s_q - s_c)). A CV shift scales c_c; a smaller
    amplitude scales c_q, since the same absolute error is a larger relative
    one against a smaller expectation.
    """
    s_c, s_q = REPORTED_SLOPES
    c_c = 1.0 + cv_shift
    c_q = 1.0 / (1.0 - amplitude_drop)
    return (c_q / c_c) ** (1.0 / (s_q - s_c))


# --- report ----------------------------------------------------------------

def main():
    disclosed = nodes("trunc", DISCLOSED_SPAN)

    print("Reproducing the disclosed construction "
          f"(16 points per share, +-{DISCLOSED_SPAN} sigma, r={R:.0%}, Ito)")
    print(f"  {'rho':>5} {'reproduced':>11} {'reported':>10} {'miss':>8}")
    cv = {}
    for rho in (0.5, 0.0):
        p, c = price(disclosed, rho)
        cv[rho] = c
        miss = p - REPORTED_PRICE[rho]
        print(f"  {rho:5.2f} {p:11.4f} {REPORTED_PRICE[rho]:10.4f} "
              f"{miss:+8.4f}")
    shift = cv[0.0] / cv[0.5] - 1.0
    print(f"  CV {cv[0.5]:.4f} -> {cv[0.0]:.4f}, shift {shift:+.2%} "
          f"(reported {REPORTED_CV_SHIFT:+.2%})")

    print("\nWhere the sign of the CV shift flips, and what each would be worth")
    head = (f"  {'grid':>14} {'CV(0.5)':>8} {'CV(0)':>8} {'shift':>8} "
            f"{'crossover':>10}")
    print(head)
    print("  " + "-" * (len(head) - 2))
    worst = 0.0
    rows = [("trunc", s) for s in (3.0, 3.25, 3.5, 3.75, 4.0, 4.5, 5.0)]
    rows.append(("equiprob", None))
    for kind, span in rows:
        g = nodes(kind, span)
        _, a = price(g, 0.5)
        _, b = price(g, 0.0)
        s = b / a - 1.0
        move = crossover_move(s) - 1.0
        worst = max(worst, abs(move))
        tag = kind if span is None else f"trunc+-{span:g}"
        print(f"  {tag:>14} {a:8.4f} {b:8.4f} {s:+8.2%} {move:+10.1%}")

    print("\nThe classical side cannot account for the observed move.")
    lo, hi = REPORTED_CROSSOVER
    print(f"  observed crossover move           {hi / lo - 1:+.0%}  "
          f"({lo:,} -> {hi:,} oracle calls)")
    print(f"  largest any grid above would give {worst:+.0%}")

    print("\nThe reported cause is sufficient on its own.")
    only_q = crossover_move(0.0, REPORTED_AMPLITUDE_DROP) - 1.0
    both = crossover_move(shift, REPORTED_AMPLITUDE_DROP) - 1.0
    print(f"  {REPORTED_AMPLITUDE_DROP:.2%} smaller amplitude alone "
          f"{only_q:+.0%}")
    print(f"  with the disclosed CV shift        {both:+.0%}")
    print(f"  observed                           {hi / lo - 1:+.0%}")

    print("\nConclusion: the grid construction fixes the sign of the classical")
    print("shift and not its size. The size is what reaches the crossover, and")
    print("it is small on every construction here, so the conclusion that the")
    print("quantum side moved does not depend on the grid.")


if __name__ == "__main__":
    main()
