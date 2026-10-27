"""Does a 16-point grid decide the sign of a crossover shift?

A method check, not a result of QWeb Research. It concerns a published
measurement by Daniel Hug (qubit-lab.ch): classical Monte Carlo against
low-depth quantum amplitude estimation, pricing a one-year call on a 50/50
basket of two correlated shares, strike 100, volatilities 28% and 58%,
correlation 0.5, on an 8-qubit grid of 16 x 16 = 256 joint scenarios. His
reported figures: exact expectation on the grid 16.2244 at correlation 0.5,
14.06 at correlation 0, and a crossover at about 7,000 oracle calls below
which classical Monte Carlo is ahead.

The question this script asks. The height of the classical error curve is
fixed by one number: the coefficient of variation of the payoff, since the
relative standard error of a Monte Carlo estimate is CV / sqrt(n). Moving the
correlation from 0.5 to 0 therefore shifts that curve by the ratio of the two
CVs, and the direction of the shift is part of where the two curves cross.

The finding. The published parameters do not determine that direction. Three
grid constructions that reproduce BOTH reference prices to within about 0.1
disagree on the sign: under a wide truncation the CV rises when the
correlation is removed, under equal-probability bins it falls. The shift is a
few percent in every case. The grid construction is therefore not a detail of
presentation here; it can decide the sign of the effect being measured.

What this is not. It does not reproduce the quantum arm, and it says nothing
about the amplitude-estimation constant, which depends on the amplification
schedule and is not recoverable from the published summary. It settles the
classical half of the crossover only.

Standard library only, by design. No arguments; prints a table.

Ramon Schweiss, QWeb (c) Research, 27 October 2026.
"""

import math
from statistics import NormalDist

# --- the instance, as published -------------------------------------------

S0 = 100.0          # initial price, both shares (assumed; not published)
K = 100.0           # strike
T = 1.0             # one year
V1, V2 = 0.28, 0.58  # volatilities
N = 16              # grid points per asset: 16 x 16 = 256 = 8 qubits

TARGET = {0.5: 16.2244, 0.0: 14.06}   # Daniel Hug's grid expectations
TOLERANCE = 0.15                      # total absolute miss across both

_ND = NormalDist()


# --- the three grid constructions -----------------------------------------

def nodes(kind, span):
    """Return (z, w): N standard-normal nodes and their probability weights.

    "equiprob" places a node at the midpoint of each of N equal-probability
    bins and weights them equally. "trunc" spaces nodes evenly over
    [-span, +span] and weights them by the normal density, renormalised. The
    two differ in how much of the tail the finite grid keeps, and that is
    exactly what the sign of the CV shift turns out to depend on.
    """
    if kind == "equiprob":
        z = [_ND.inv_cdf((i + 0.5) / N) for i in range(N)]
        w = [1.0 / N] * N
        return z, w

    z = [-span + 2.0 * span * i / (N - 1) for i in range(N)]
    p = [_ND.pdf(zi) for zi in z]
    s = sum(p)
    return z, [pi / s for pi in p]


# --- pricing on the grid ---------------------------------------------------

def price(kind, span, rho, r):
    """Exact expectation and payoff CV on the grid.

    The second asset is correlated in standard-normal space, Y2 = rho * Z1 +
    sqrt(1 - rho^2) * Z2, so that the marginals are unchanged as rho moves.
    Each share follows the usual risk-neutral lognormal with the Ito
    correction, S = S0 * exp((r - sigma^2 / 2) T + sigma sqrt(T) Z).
    """
    z, w = nodes(kind, span)
    root = math.sqrt(T)
    c = math.sqrt(1.0 - rho * rho)

    e1 = e2 = 0.0
    for i, z1 in enumerate(z):
        s1 = S0 * math.exp((r - 0.5 * V1 * V1) * T + V1 * root * z1)
        for j, z2 in enumerate(z):
            y2 = rho * z1 + c * z2
            s2 = S0 * math.exp((r - 0.5 * V2 * V2) * T + V2 * root * y2)
            pay = 0.5 * (s1 + s2) - K
            if pay <= 0.0:
                continue
            p = w[i] * w[j]
            e1 += p * pay
            e2 += p * pay * pay

    var = max(e2 - e1 * e1, 0.0)
    return e1, math.sqrt(var) / e1          # expectation, CV


# --- search for constructions consistent with the published prices --------

def candidates():
    """Every (construction, r) whose two prices match TARGET within TOLERANCE."""
    grids = [("equiprob", None)] + [("trunc", s / 2.0) for s in range(4, 11)]
    out = []
    for kind, span in grids:
        for r_bp in range(0, 6):                 # 0% to 5% in whole percent
            r = r_bp / 100.0
            e_hi, cv_hi = price(kind, span, 0.5, r)
            e_lo, cv_lo = price(kind, span, 0.0, r)
            miss = abs(e_hi - TARGET[0.5]) + abs(e_lo - TARGET[0.0])
            if miss <= TOLERANCE:
                out.append((miss, kind, span, r, e_hi, e_lo, cv_hi, cv_lo))
    out.sort()
    return out


def main():
    rows = candidates()

    print(__doc__.strip().splitlines()[0])
    print()
    print(f"target: {TARGET[0.5]} at rho=0.5, {TARGET[0.0]} at rho=0; "
          f"accepting a total miss of {TOLERANCE}")
    print()
    head = (f"{'grid':>14} {'r':>5} {'E(.5)':>8} {'E(0)':>8} "
            f"{'CV(.5)':>8} {'CV(0)':>8} {'shift':>8} {'sign':>6}")
    print(head)
    print("-" * len(head))

    signs = set()
    for miss, kind, span, r, e_hi, e_lo, cv_hi, cv_lo in rows:
        tag = kind if span is None else f"trunc+-{span:g}"
        shift = cv_lo / cv_hi - 1.0
        sign = "up" if shift > 0 else "down"
        signs.add(sign)
        print(f"{tag:>14} {r:5.2f} {e_hi:8.4f} {e_lo:8.4f} "
              f"{cv_hi:8.4f} {cv_lo:8.4f} {shift:+8.2%} {sign:>6}")

    print()
    if not rows:
        print("No construction matched. Widen TOLERANCE or the search.")
    elif len(signs) > 1:
        print(f"{len(rows)} constructions match the published prices and they "
              f"disagree on the sign.")
        print("The classical curve moves up under some and down under others, "
              "so the direction")
        print("of the crossover shift is not determined by the published "
              "parameters alone.")
    else:
        print(f"All {len(rows)} matching constructions agree: the CV moves "
              f"{signs.pop()} at rho=0.")
        print("The direction is then determined, and the magnitude is the "
              "ratio printed above.")

    print()
    print("CV is what sets the classical curve's height: relative standard "
          "error is CV/sqrt(n).")
    print("The quantum arm is not modelled here.")


if __name__ == "__main__":
    main()
