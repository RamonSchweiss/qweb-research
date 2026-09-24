"""
EO-3: the same question without a bit to announce the change.

In EO-2 the future structure was revealed by a mid-circuit measurement, and the
planner that used that one classical bit beat every planner that reasoned about
the state. One bit is the cheapest thing a network can carry, so that contest
was never close.

This script removes the bit. Nothing announces anything: the interaction
structure DRIFTS. Every so often one edge of the interaction graph is rewired -
a coupling fades out, another comes up - so the graph at layer 20 is a slowly
transformed version of the graph at layer 0, and no event marks the change.

Everything else is unchanged from staleness_cost.py: two QPUs, ten qubits,
balanced partitions, and one currency, ebits, at one ebit per remote two-qubit
gate and one per qubit migrated. The planners are the same five, each acting on
information L layers old.

The point of the class: a drifting structure is what hardware does, not what a
program does. There is no branch to label, so a planner can only react to what
it observes - the gates it has seen, or the information structure of the state.
If the information horizon is ever a control variable rather than a descriptor,
this is where it has to show.

Findings : (1) drift produces a cost of staleness too, and it grows with the
               drift rate. Keeping the first partition costs 5 %, 18 % and 41 %
               above the floor at one rewiring every ten, three and one layers.
               No announcement is needed for staleness to be expensive;
           (2) the gate planner still collects most of it, and still needs no
               state information: 118.6 ebits against 132.0 for staying put at
               the middle rate, beating it in 10 of 12 programs. At the slowest
               rate there is almost nothing to collect (3 of 12);
           (3) the information planners lose everywhere, and not narrowly.
               Chasing the information-optimal cut costs 189 to 222 ebits where
               staying put costs 110 to 161. The viability rule recovers about
               a tenth of that and still ends far behind;
           (4) at the FASTEST drift the gate planner over-reacts. It pays 51
               migrations chasing every rewiring and beats staying put in only
               7 of 12 programs. There the triggered planner - information
               decides WHEN, gate structure decides WHERE - is the best of the
               five: 146.8 ebits against 152.6 for the gate planner and 160.9
               for staying put, and it wins in 8 of 12 programs. This is the
               first and so far only place in three classes where the
               information signal earns anything;
           (5) the break-even latency still does not follow H_v. Within the
               three drift rates the rank correlations are +0.87 (over the
               three programs that have a break-even point at all), -0.45 and
               +0.34; pooled it is -0.17.

Reading  : what the horizon buys is a brake, not a steering wheel. It is of no
           use in deciding where the computation should be cut - the gate list
           decides that, in every class we have measured - but when the
           structure churns faster than reorganisation can pay for itself, an
           information-based expiry test stops a gate-driven planner from
           chasing noise. That is a narrower claim than the one we set out
           with, and unlike the others it is supported.

Runtime : about five seconds.
"""
import sys, pathlib, itertools
import numpy as np
from scipy.stats import spearmanr

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import partition_topology as pt
from staleness_cost import (N, GAMMA, BETA, PARTS, PARTS_I, layer, cross_all,
                            move_matrix, info_best, info_excess, run, floor_cost,
                            p_static, p_gate, p_info, p_viability, p_trigger)

LAYERS, M = 24, 15
SEEDS = range(12)
LATENCIES = [0, 1, 2, 4, 6, 8]
RATES = [(0.1, "one rewiring every ten layers"),
         (0.33, "one rewiring every three layers"),
         (1.0, "one rewiring every layer")]
PLANNERS = [("static", p_static), ("gate", p_gate), ("information", p_info),
            ("viability", p_viability), ("triggered", p_trigger)]


def drifting_program(seed, rate):
    """One run: the graph rewires as it goes, and nothing announces it."""
    rng = np.random.default_rng(seed * 613 + int(rate * 1000))
    pool = list(itertools.combinations(range(N), 2))
    active = [pool[i] for i in rng.choice(len(pool), M, replace=False)]
    psi = np.ones(2**N, dtype=complex) / np.sqrt(2**N)
    snaps, edges = [], []
    carry = 0.0
    for _ in range(LAYERS):
        carry += rate
        while carry >= 1.0:                      # rewire one edge
            carry -= 1.0
            out = int(rng.integers(len(active)))
            free = [e for e in pool if e not in active]
            active = active[:out] + active[out+1:] + [free[int(rng.integers(len(free)))]]
        E = list(active)
        psi = layer(psi, E)
        snaps.append(pt.mutual(psi, N)); edges.append(E)
    return [dict(w=1.0, snaps=snaps, edges=edges)]

def best_static(ps):
    """The fixed partition that is best for the graph the planner starts with."""
    return int(cross_all(ps[0]["edges"][0]).argmin())

def horizon(ps):
    costs, best = pt.cost_table(ps[0]["snaps"], N)
    return pt.h_start(costs, best)[0]

def break_even(ps, k0, grid=range(0, 16)):
    """Latency at which the gate planner stops beating the static one."""
    stat = sum(run(p, p_static, 0, k0)[0] for p in ps)
    tot = [sum(sum(run(p, p_gate, L, k0)[:2]) for p in ps) for L in grid]
    for i in range(1, len(tot)):
        if tot[i] >= stat > tot[i-1]:
            return float(list(grid)[i-1] + (stat - tot[i-1]) / (tot[i] - tot[i-1]))
    return float("nan")


def study(rate, label):
    print(f"\n  drift rate: {label}")
    tot = {name: {L: [0.0, 0.0] for L in LATENCIES} for name, _ in PLANNERS}
    stat = flo = hv = 0.0
    hs, ls = [], []
    wins = dict(gate=0, trig=0)
    for seed in SEEDS:
        ps = drifting_program(seed, rate)
        k0 = best_static(ps)
        hv += horizon(ps) / len(SEEDS)
        flo += sum(floor_cost(p) for p in ps) / len(SEEDS)
        stat += sum(run(p, p_static, 0, k0)[0] for p in ps) / len(SEEDS)
        hs.append(horizon(ps)); ls.append(break_even(ps, k0))
        s0 = sum(run(p, p_static, 0, k0)[0] for p in ps)
        g0 = sum(sum(run(p, p_gate, 0, k0)[:2]) for p in ps)
        t0 = sum(sum(run(p, p_trigger, 0, k0)[:2]) for p in ps)
        wins["gate"] += g0 < s0; wins["trig"] += t0 < g0
        for name, planner in PLANNERS:
            for L in LATENCIES:
                for p in ps:
                    r, m, _ = run(p, planner, L, k0)
                    tot[name][L][0] += r / len(SEEDS)
                    tot[name][L][1] += m / len(SEEDS)
    print(f"    H_v {hv:.1f} layers;  staying put {stat:.1f} ebits,"
          f"  floor {flo:.1f},  C_stale {stat-flo:.1f} ({100*(stat/flo-1):.0f} %)")
    print("    planner        " + "".join(f"  L={L:<2d}" for L in LATENCIES)
          + "      migrations at L=0")
    for name, _ in PLANNERS:
        line = f"    {name:12s} "
        for L in LATENCIES:
            r, m = tot[name][L]
            line += f" {r+m:5.1f}"
        print(line + f"        {tot[name][0][1]:5.1f}")
    print(f"    per program at L=0: the gate planner beats staying put in"
          f" {wins['gate']:2d} of {len(list(SEEDS))} programs,"
          f" the triggered planner beats the gate planner in {wins['trig']:2d}")
    ok = [(h, l) for h, l in zip(hs, ls) if np.isfinite(l)]
    if len(ok) > 2:
        h, l = zip(*ok)
        r = spearmanr(h, l)[0]
        print(f"    break-even latency: median {np.median(l):.1f} layers over the"
              f" {len(ok)} programs that have one, rank correlation with H_v"
              f" {r:+.2f}" if np.isfinite(r) else
              f"    break-even latency: median {np.median(l):.1f} layers"
              f" over {len(ok)} programs")
    return hs, ls


def main():
    print("EO-3: drifting interaction structure - nothing announces the change")
    print(f"n = {N}, {LAYERS} layers, {M} edges, two QPUs,"
          f" {len(list(SEEDS))} programs per drift rate")
    H, L = [], []
    for rate, label in RATES:
        hs, ls = study(rate, label)
        H += hs; L += ls
    ok = [(h, l) for h, l in zip(H, L) if np.isfinite(l)]
    if len(ok) > 2:
        h, l = zip(*ok)
        print(f"\n  pooled across drift rates: rank correlation of H_v with the"
              f" break-even latency {spearmanr(h, l)[0]:+.2f} ({len(ok)} programs)")
        print("  - which is again a between-regime effect; see the per-rate numbers above.")
    print("\n  No bit, and almost the same outcome: the planner that watches the")
    print("  gate list decides where to cut. The one thing the information signal")
    print("  buys is a brake - at the fastest drift it stops that planner from")
    print("  chasing every rewiring, and only there is it the best of the five.")


if __name__ == "__main__":
    main()
