"""
Is the triggered planner's advantage real, and does it survive a noise model?

The two checks V. Ramamurthy asked for after EO-3 (drift_cost.py), where the
one operational use of the information horizon appeared: at the fastest drift,
a planner that uses the information only to decide WHEN to reorganise beat the
gate planner by refusing moves rather than by choosing better ones.

CHECK 1 - does that advantage sit on one finely tuned setting?
  Sweep the three knobs that could be carrying it: the tolerance that defines
  when an organisation counts as expired, the drift rate, and the price of a
  migration relative to a remote gate. Twelve programs per cell, zero latency.

CHECK 2 - does it survive when staleness has a physical consequence?
  Every network operation is given a finite fidelity: a remote two-qubit gate
  and a migrated qubit each carry a 2 % chance of a random Pauli error on the
  qubits involved. Local gates are left noiseless on purpose, so that what is
  being measured is the damage done by talking across the cut and nothing else.
  The end of the circuit is compared with the noiseless run, over trajectories.
  This is the deliberate one-off fidelity run, not an attempt to rescue
  anything: if it does not change the conclusion, the conclusion stands.

Findings : (1) the advantage is not an artefact of the tolerance. From 2 % to
               20 % the triggered planner stays at or below the gate planner's
               cost at every drift rate that has drift worth refusing, and a
               looser tolerance makes it stronger rather than weaker: at 20 %
               it costs 135.1 ebits against the gate planner's 152.6 and wins
               in 11 of 12 programs;
           (2) it is a property of the DRIFT RATE. At one rewiring every four
               layers the two planners are identical - there is nothing to
               refuse. At one every two layers the advantage is small (131.4
               against 133.8, 4 of 12). At one and 1.5 per layer it is clear
               (146.8 against 152.6 and 145.9 against 148.4, both 8 of 12);
           (3) it scales with the price of a migration, as it must, since what
               it buys is a refused move. At half price the gap is 2.0 ebits,
               at the standard price 5.8, at double price 13.5;
           (4) noise does not change the ranking, and - the honest part - it
               does not add to it either. With 0.5 % error on every remote gate
               and every migration, the triggered planner ends with the highest
               fidelity (0.296) and the information planner with the lowest
               (0.154). But the measured fidelities track (1 - eps) raised to
               the number of error chances almost exactly, which is what this
               model must give: on a scrambled state one Pauli error already
               destroys the overlap, so fidelity restates the count of network
               operations. Measured values sit slightly above the prediction,
               most for the planner that migrates most, which hints that where
               an error lands matters a little - not enough to reorder anything.

Reading  : the brake survives both checks. It is bounded - it needs drift fast
           enough to be worth refusing and migrations that cost something - and
           inside those bounds it holds across tolerances, prices and under
           noise. Fidelity neither strengthens nor weakens it, which by the
           agreed rule is the point to stop.

Runtime : about two minutes, most of it the trajectories.
"""
import sys, pathlib
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import partition_topology as pt
from staleness_cost import (N, PARTS, PARTS_I, layer, cross_all, move_matrix,
                            info_best, info_excess)
from drift_cost import drifting_program, best_static, LAYERS

SEEDS = range(12)
TOLERANCES = [0.02, 0.05, 0.10, 0.20]
RATES = [0.25, 0.5, 1.0, 1.5]
PRICES = [0.5, 1.0, 2.0]
EPS, TRAJECTORIES = 0.005, 40         # error per network operation, samples


# ------------------------------------------------------- planners, parametrised
def make_planners(tol):
    def static(t, k, path, L): return k
    def gate(t, k, path, L):
        s = t - L
        return int(cross_all(path["edges"][s]).argmin()) if s >= 0 else k
    def information(t, k, path, L):
        s = t - L
        return info_best(path["snaps"][s]) if s >= 0 else k
    def viability(t, k, path, L):
        s = t - L
        if s < 0: return k
        return info_best(path["snaps"][s]) if info_excess(path["snaps"][s], k) > tol else k
    def triggered(t, k, path, L):
        s = t - L
        if s < 0 or info_excess(path["snaps"][s], k) <= tol: return k
        return int(cross_all(path["edges"][s]).argmin())
    return [("static", static), ("gate", gate), ("information", information),
            ("viability", viability), ("triggered", triggered)]

def trace(path, planner, L, start):
    """Per layer: the assignment in force and the qubits migrated into it."""
    k, out = start, []
    for t, E in enumerate(path["edges"]):
        k_new = planner(t, k, path, L)
        moved = [q for q in range(N) if PARTS_I[k, q] != PARTS_I[k_new, q]]
        k = k_new
        remote = [(a, b) for a, b in E if PARTS_I[k, a] != PARTS_I[k, b]]
        out.append((remote, moved))
    return out

def ebits(tr, price=1.0):
    return sum(len(r) + price*len(m) for r, m in tr)


# -------------------------------------------------------------- check 1: sweep
def sweep():
    print("\n1. Does the advantage sit on one setting?  (twelve programs per cell,"
          " latency 0)\n")
    print("   totals in ebits, and how often the triggered planner beats the gate planner\n")
    print("   tolerance   rate  static   gate  triggered   trigger wins")
    for tol in TOLERANCES:
        for rate in RATES:
            tot = dict(static=0.0, gate=0.0, triggered=0.0); wins = 0
            for seed in SEEDS:
                ps = drifting_program(seed, rate)
                k0 = best_static(ps)
                cur = {}
                for name, pl in make_planners(tol):
                    if name in tot:
                        cur[name] = sum(ebits(trace(p, pl, 0, k0)) for p in ps)
                        tot[name] += cur[name] / len(list(SEEDS))
                wins += cur["triggered"] < cur["gate"]
            print(f"   {100*tol:5.0f} %   {rate:4.2f}  {tot['static']:6.1f} {tot['gate']:6.1f}"
                  f"    {tot['triggered']:6.1f}      {wins:2d} of {len(list(SEEDS))}")
        print()

def price_sweep():
    print("2. How much does the price of a migration matter?  (tolerance 5 %)\n")
    print("   price of one migration   rate   gate  triggered   difference")
    for price in PRICES:
        for rate in (1.0, 1.5):
            g = t_ = 0.0
            for seed in SEEDS:
                ps = drifting_program(seed, rate)
                k0 = best_static(ps)
                pls = dict(make_planners(0.05))
                g += sum(ebits(trace(p, pls["gate"], 0, k0), price) for p in ps) / len(list(SEEDS))
                t_ += sum(ebits(trace(p, pls["triggered"], 0, k0), price) for p in ps) / len(list(SEEDS))
            print(f"   {price:20.1f} ebits  {rate:4.2f} {g:6.1f}     {t_:6.1f}"
                  f"      {g - t_:+6.1f}")
        print()


# --------------------------------------------------------- check 2: fidelity
def pauli(psi, q, which):
    t = np.moveaxis(psi.reshape([2]*N), q, 0).copy()
    if which == 0:                       # X
        t = t[::-1]
    elif which == 1:                     # Y
        t = t[::-1] * np.array([-1j, 1j]).reshape(2, *([1]*(N-1)))
    else:                                # Z
        t = t * np.array([1, -1]).reshape(2, *([1]*(N-1)))
    return np.moveaxis(t, 0, q).reshape(-1)

def trajectory(path, tr, rng):
    """Run the circuit again, with errors wherever the network was used."""
    psi = np.ones(2**N, dtype=complex) / np.sqrt(2**N)
    for (remote, moved), E in zip(tr, path["edges"]):
        psi = layer(psi, E)
        for a, b in remote:                       # a remote gate consumes an EPR pair
            for q in (a, b):
                if rng.random() < EPS:
                    psi = pauli(psi, q, int(rng.integers(3)))
        for q in moved:                           # a migration is a teleportation
            if rng.random() < EPS:
                psi = pauli(psi, q, int(rng.integers(3)))
    return psi

def fidelity_run(rate=1.0, tol=0.05):
    print(f"3. With noise on every network operation"
          f"  ({100*EPS:.1f} % per remote gate and per migration,"
          f" {TRAJECTORIES} trajectories)\n")
    rng = np.random.default_rng(11)
    names = [n for n, _ in make_planners(tol)]
    fid = {n: 0.0 for n in names}; cost = {n: 0.0 for n in names}
    ops = {n: 0.0 for n in names}
    for seed in SEEDS:
        ps = drifting_program(seed, rate)
        k0 = best_static(ps)
        for p in ps:
            ideal = np.ones(2**N, dtype=complex) / np.sqrt(2**N)
            for E in p["edges"]:
                ideal = layer(ideal, E)
            for name, pl in make_planners(tol):
                tr = trace(p, pl, 0, k0)
                cost[name] += ebits(tr) / len(list(SEEDS))
                ops[name] += sum(2*len(r) + len(m) for r, m in tr) / len(list(SEEDS))
                f = [abs(np.vdot(ideal, trajectory(p, tr, rng)))**2
                     for _ in range(TRAJECTORIES)]
                fid[name] += float(np.mean(f)) / len(list(SEEDS))
    print("   planner        ebits   error chances   fidelity   (1-eps)^chances")
    for n in names:
        print(f"   {n:12s} {cost[n]:7.1f} {ops[n]:13.1f}      {fid[n]:6.3f}"
              f"          {(1-EPS)**ops[n]:6.3f}")
    best_c = min(cost, key=cost.get); best_f = max(fid, key=fid.get)
    print(f"\n   cheapest in ebits: {best_c};  highest fidelity: {best_f};"
          f"  {'same planner' if best_c == best_f else 'they differ'}")
    print("   Measured fidelity tracks (1-eps) to the power of the number of error")
    print("   chances, which is what this noise model has to give: on a scrambled")
    print("   state a single Pauli error already destroys the overlap, so fidelity")
    print("   restates the count of network operations rather than adding to it.")


def main():
    print("Robustness of the one place where the information horizon earns something")
    print(f"n = {N}, {LAYERS} layers, two QPUs, drift with no announcing event")
    sweep()
    price_sweep()
    fidelity_run()
    print("\n  The brake survives: it needs fast drift and migrations that cost")
    print("  something, and inside those bounds it holds under a different price")
    print("  and under noise.")


if __name__ == "__main__":
    main()
