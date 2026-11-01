"""Which half of a crossover does the grid decide? The classical half, barely.

A method check, not a result of QWeb Research. It concerns a published
measurement by Daniel Hug (qubit-lab.ch): classical Monte Carlo against
low-depth quantum amplitude estimation, pricing a one-year call on a 50/50
basket of two correlated shares, strike 100, volatilities 28% and 58%, on an
8-qubit grid of 16 x 16 = 256 joint scenarios.

Three dated rounds, two of which corrected this script rather than the
measurement.

27 October. The height of the classical error curve is fixed by the
coefficient of variation of the payoff, since a Monte Carlo relative standard
error is CV / sqrt(n). Removing the correlation shifts that curve by the ratio
of the two CVs, and the direction of the shift is part of where the classical
and quantum curves meet. This script found that the published parameters did
not fix that direction: constructions reproducing both reference prices
disagreed on the sign.

31 October. The author published the construction - 16 points per share,
evenly spaced in log-price, truncated at +-3.5 sigma, density weights
renormalised, drift and discounting 3%, Ito-corrected, correlation in
standard-normal space - and this script reproduced it. The sign does flip
inside the truncation family, near +-3.9 sigma, so the October caveat was
correct. It was also nearly worthless: across +-3 to +-5 the shift stays under
1.4%, worth at most about 3% on the crossover, against a reported move of
43%.

1 November, and this is where the script was wrong twice.

  1. The exponent. It converted a smaller amplitude into a worse relative
     error as 1 / a. Amplitude estimation's relative error scales as
     1 / sqrt(a). With the right exponent a 13.35% smaller amplitude predicts
     about 7.4% more error and +20% on the crossover, not +42%.

  2. The agreement was two errors cancelling. The +42% matched a reported +43%
     to within a point. At 200 repetitions the author's own rerun puts the
     crossover at about 8,100 and 9,600, a move of +19% with a 90% interval of
     -12% to +52%; the +43% was rounding, and twenty repetitions could not
     resolve it. An agreement to one point looked decisive and carried
     nothing, which is the more useful finding of the exchange.

  3. "Grid-independent" was the wrong word, and only the classical half
     survives it. The author reports the crossover running from about 6,000 at
     +-3 sigma to about 24,000 at +-5 sigma - a factor of four - because the
     payoff scale sets the amplitude. The grid barely touches the classical
     constant and moves the quantum one a great deal.

What stands. Slope the method's, crossover the instance's. The cause of the
move is the smaller amplitude, at about half the size this script first
claimed, and the classical side cannot account for it on any grid in the
family. At 200 repetitions the interval still contains no movement at all, so
the cause is consistent with the measurement rather than demonstrated by it;
about 550 repetitions would put the lower bound above zero.

Reproduction. This script gets 16.2650 and 14.0695 against the reported
16.2244 and 14.0586, and a CV shift of -0.41% against the reported -0.46%. The
residual quarter of a percent is most likely in how the +-3.5 sigma range is
taken relative to the drift; it affects no conclusion here.

Assumption behind the crossover conversion. It takes the two fitted power laws
to hold near the crossing with only their constants changing. That is enough
for a bound and not enough for a location, which is why the numbers are stated
as bounds and the quantum side is taken from the author's reported amplitude
rather than modelled here.

Standard library only, by design. No arguments; prints its own conclusion.

Ramon Schweiss, QWeb (c) Research. 27 October 2026; resolved against the
disclosed construction 31 October; corrected 1 November.
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
REPORTED_AMPLITUDE_DROP = 0.1335                # 1 - 14.0586 / 16.2244

# Corrected 1 November at 200 repetitions. The earlier 7,000 -> 10,000 was
# rounding at twenty repetitions and is superseded, not merely refined.
REPORTED_CROSSOVER = (8100, 9600)
REPORTED_INTERVAL = (-0.12, 0.52)               # 90% on the crossover move
REPORTED_REPS = 200

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
    moves by (c_q / c_c) ** (1 / (s_q - s_c)).

    A CV shift scales c_c directly. A smaller amplitude scales c_q as
    1 / sqrt(a) and NOT as 1 / a: the estimator's absolute error on the
    amplitude carries a factor sqrt(a(1-a)), so dividing by a to get a
    relative error leaves one power of sqrt(a) in the denominator. This script
    used 1 / a until 1 November, which inflated the predicted move from +20%
    to +42%.
    """
    s_c, s_q = REPORTED_SLOPES
    c_c = 1.0 + cv_shift
    c_q = 1.0 / math.sqrt(1.0 - amplitude_drop)
    return (c_q / c_c) ** (1.0 / (s_q - s_c))


def reps_to_exclude_zero(point, interval, reps):
    """How many repetitions would put the interval's lower bound at zero.

    The half-width of an interval on a ratio narrows as 1 / sqrt(reps), so the
    required count scales with the square of how much narrowing is needed.
    """
    half = (interval[1] - interval[0]) / 2.0
    return reps * (half / point) ** 2


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
        print(f"  {rho:5.2f} {p:11.4f} {REPORTED_PRICE[rho]:10.4f} "
              f"{p - REPORTED_PRICE[rho]:+8.4f}")
    shift = cv[0.0] / cv[0.5] - 1.0
    print(f"  CV {cv[0.5]:.4f} -> {cv[0.0]:.4f}, shift {shift:+.2%} "
          f"(reported {REPORTED_CV_SHIFT:+.2%})")

    print("\nWhere the sign of the CV shift flips, and what the classical side")
    print("would be worth on the crossover")
    head = (f"  {'grid':>14} {'CV(0.5)':>8} {'CV(0)':>8} {'shift':>8} "
            f"{'crossover':>10}")
    print(head)
    print("  " + "-" * (len(head) - 2))
    worst_fam = worst_out = 0.0
    rows = [("trunc", s) for s in (3.0, 3.25, 3.5, 3.75, 4.0, 4.5, 5.0)]
    rows.append(("equiprob", None))
    for kind, span in rows:
        g = nodes(kind, span)
        _, a = price(g, 0.5)
        _, b = price(g, 0.0)
        s = b / a - 1.0
        move = crossover_move(s) - 1.0
        if kind == "trunc":
            worst_fam = max(worst_fam, abs(move))
        else:
            worst_out = max(worst_out, abs(move))
        tag = kind if span is None else f"trunc+-{span:g}"
        print(f"  {tag:>14} {a:8.4f} {b:8.4f} {s:+8.2%} {move:+10.1%}")

    lo, hi = REPORTED_CROSSOVER
    observed = hi / lo - 1.0
    print("\nThe classical side is a sixth of the observed move at most.")
    print(f"  observed crossover move                {observed:+.0%}  "
          f"({lo:,} -> {hi:,} calls, {REPORTED_REPS} repetitions)")
    print(f"  largest in the disclosed trunc family  {worst_fam:+.0%}")
    print(f"  equal-probability bins, for contrast   {worst_out:+.0%}")
    print("  The equiprobable grid is outside the disclosed family and does")
    print("  not reproduce the reference prices at r=3%, so it bounds nothing")
    print("  here. It is kept because it is where the sign flips hardest. With")
    print("  the earlier +43% in the denominator this distinction did not")
    print("  matter; at +19% it does.")

    print("\nThe reported cause is the right size, at 1/sqrt(a).")
    only_q = crossover_move(0.0, REPORTED_AMPLITUDE_DROP) - 1.0
    both = crossover_move(shift, REPORTED_AMPLITUDE_DROP) - 1.0
    wrong = ((1.0 / (1.0 - REPORTED_AMPLITUDE_DROP)) / (1.0 + shift)) \
        ** (1.0 / (REPORTED_SLOPES[1] - REPORTED_SLOPES[0])) - 1.0
    print(f"  {REPORTED_AMPLITUDE_DROP:.2%} smaller amplitude alone "
          f"{only_q:+.0%}")
    print(f"  with the disclosed CV shift        {both:+.0%}")
    print(f"  observed                           {observed:+.0%}")
    print(f"  what this script said until 1 Nov, at 1/a   {wrong:+.0%}")

    print("\nAnd the observed move is not yet resolved.")
    il, ih = REPORTED_INTERVAL
    need = reps_to_exclude_zero(observed, REPORTED_INTERVAL, REPORTED_REPS)
    print(f"  90% interval at {REPORTED_REPS} repetitions   "
          f"{il:+.0%} to {ih:+.0%}")
    print(f"  contains no movement at all        {il < 0}")
    print(f"  repetitions to lift the lower bound to zero   about "
          f"{round(need / 50) * 50:,.0f}")

    print("\nConclusion: the grid construction fixes the sign of the classical")
    print("shift and not its size, and the classical side is worth a few per")
    print("cent of the crossover on any construction here. It does NOT follow")
    print("that the crossover is grid-independent: the author reports it")
    print("running from about 6,000 at +-3 sigma to about 24,000 at +-5 sigma,")
    print("because the payoff scale sets the amplitude. The grid barely touches")
    print("the classical constant and moves the quantum one by a factor of")
    print("four. Slope the method's, crossover the instance's - and the")
    print("instance includes the grid, through the quantum side.")


if __name__ == "__main__":
    main()
