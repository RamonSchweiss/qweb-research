"""
Would a distributed-quantum compiler ever see what the viability horizon sees?

Every distributed compiler we could find plans offline, from the circuit's
gate structure alone: which qubits interact, and how often. The viability
horizon H_v is defined on the STATE: how long the best balanced cut of the
mutual-information graph, chosen at layer 0, stays within 5 % of the best.

This script asks three questions about the two views on the same QAOA
circuits the horizon was measured on.

  1. Does a gate-based partitioner ever repartition a QAOA circuit?
  2. Does its fixed cut coincide with the state view's best cut, and for how long?
  3. What does following the state view cost in the currency that execution
     actually pays - remote two-qubit gates, i.e. EPR pairs?

The gate-based side is computed exactly here, without any extra package: the
minimum balanced cut of each layer's gate-interaction graph, found by
enumerating every balanced bipartition. If the open-source memQ compiler
(github.com/memQGit/dqc, arXiv 2609.15728) is installed, section 4 runs its
windowed partitioner on the same circuits as a cross-check; otherwise that
section is skipped and says so.

Findings : (1) no. In QAOA every layer applies the same gates, so every
               layer's interaction graph is identical and a gate-based
               partitioner has no reason to move anything. The exact gate
               cut does not change in a single layer of a single graph, and
               memQ's partitioner, one window per layer, keeps one partition
               for all windows in 21 of 21 graphs. The same partitioner does
               repartition a QFT, so the zero is a property of QAOA, not of
               the tool;
           (2) closer than the horizon suggests. The two cuts agree at layer 0
               in 15 of 21 graphs. Afterwards the fixed gate cut stays within
               about 7 % of the information optimum (median over seeds) in
               random, path, regular and grid graphs, and moves 12-17 % away
               in ring graphs and up to 50 % in scale-free graphs. So a
               partition that is "no longer viable" at the 5 % tolerance is
               often only a little worse, and how much worse depends on the
               family more than on the horizon;
           (3) this is the uncomfortable part. Following the information-best
               cut instead costs 22 % MORE remote gates per layer than the
               fixed gate cut, before any cost of moving qubits - necessarily
               more, since the gate cut is the minimum of exactly that
               quantity. For executing a known circuit, the gate cut is the
               right cost and the planning limit measures a different
               objective.

What this does NOT settle : where the information structure IS the right cost.
               Candidates, none tested here: circuits that are not known in
               advance (mid-circuit measurement, classical feedback, adaptive
               algorithms), where a planner has only estimates of the state;
               simulation and circuit cutting, whose cost grows with the
               entanglement across the cut; link noise that damages
               correlations across the cut more than local ones.

Runtime : about twenty seconds, including the memQ cross-check.
"""
import sys, pathlib, logging, tempfile
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import partition_topology as pt

N, M, P = 10, 15, 24                 # ten qubits, density 1.5, 24 layers
GAMMA, BETA = 0.5, 0.4               # as in partition_topology.qaoa
SEEDS = range(3)
FAMILIES = ["random", "ring", "path", "regular", "scale-free", "community", "grid"]
PROBE = [0, 5, 10, 20]               # layers at which the gate cut is compared


# ------------------------------------------------ gate side, computed exactly
def gate_layers(edges, p):
    """The two-qubit gates of each QAOA layer: one ZZ rotation per edge.
    Written out layer by layer so that the identity of the layers is
    computed below rather than assumed."""
    return [list(edges) for _ in range(p)]

def gate_weights(gates, n):
    W = np.zeros((n, n))
    for a, b in gates:
        W[a, b] += 1; W[b, a] += 1
    return W

def gate_cut_costs(gates, n):
    """Remote two-qubit gates of every balanced bipartition for one layer.
    Each remote ZZ costs one EPR pair (one cat-entanglement)."""
    return pt.cut_costs(gate_weights(gates, n), pt.partitions(n))


# --------------------------------------------------------------- the survey
def survey():
    rows = []
    for fam in FAMILIES:
        for seed in SEEDS:
            E = pt.make_graph(fam, N, M, seed)
            if E is None:
                continue
            layers = gate_layers(E, P)
            g_costs = np.array([gate_cut_costs(g, N) for g in layers])
            g_best = g_costs.argmin(1)                   # gate partition per layer
            ties = int((g_costs[0] == g_costs[0].min()).sum())

            snaps = pt.qaoa(N, E, P, GAMMA, BETA)
            i_costs, i_best = pt.cost_table(snaps, N)
            hv, censored = pt.h_start(i_costs, i_best)

            k = int(g_best[0])                           # the fixed gate cut
            excess = (i_costs[:, k] - i_best) / i_best   # its information excess
            i_arg = i_costs.argmin(1)
            # remote gates per layer if one followed the information optimum
            follow = g_costs[np.arange(P), i_arg]
            rows.append(dict(fam=fam, seed=seed, E=E,
                             changes=int((g_best[1:] != g_best[:-1]).sum()),
                             ties=ties, hv=hv, cens=censored,
                             agree0=bool(i_arg[0] == k),
                             excess=excess,
                             gate_min=float(g_costs[0].min()),
                             follow=float(follow.mean())))
    return rows


def memq_crosscheck(rows):
    """Run memQ's windowed interaction partitioner, one window per layer."""
    try:
        from memq_dqc.partition import Partitioner
        from memq_dqc.assets import network_path, circuit_path
    except ImportError:
        print("  memq_dqc is not installed - cross-check skipped.")
        print("  To run it:  pip install git+https://github.com/memQGit/dqc")
        return
    logging.disable(logging.CRITICAL)
    net = str(network_path(f"{N}_qubits/n2_pair_a2a"))

    def qasm(edges):
        L = ["OPENQASM 3.0;", 'include "stdgates.inc";',
             f"bit[{N}] c;", f"qubit[{N}] q;"]
        L += [f"h q[{i}];" for i in range(N)]
        for _ in range(P):
            for a, b in edges:
                L += [f"cx q[{a}], q[{b}];", f"rz({2*GAMMA}) q[{b}];",
                      f"cx q[{a}], q[{b}];"]
            L += [f"rx({2*BETA}) q[{i}];" for i in range(N)]
        L += [f"c[{i}] = measure q[{i}];" for i in range(N)]
        return "\n".join(L) + "\n"

    def run(path, window):
        part = Partitioner(net, str(path), algo="interaction",
                           algo_kwargs={"window_length": window})
        part.run()
        keys = []
        for assign in part._algorithm.schedule:
            side = [frozenset(v) for v in assign.values() if 0 in v][0]
            keys.append(side)
        return len(set(keys)), sum(a != b for a, b in zip(keys, keys[1:])), len(keys)

    kept = 0
    with tempfile.TemporaryDirectory() as tmp:
        for r in rows:
            path = pathlib.Path(tmp) / f"{r['fam']}_{r['seed']}.qasm"
            path.write_text(qasm(r["E"]))
            distinct, changes, windows = run(path, 2 * len(r["E"]))  # 2 CX per ZZ
            kept += (distinct == 1)
    print(f"  QAOA, one window per layer: one partition for all windows "
          f"in {kept} of {len(rows)} graphs")
    d, c, w = run(circuit_path("qft_n10"), 5)
    print(f"  control, QFT n=10, windows of 5 gates: {d} distinct partitions, "
          f"{c} changes over {w} windows")


def main():
    rows = survey()

    print(f"QAOA, n={N}, m={M}, {P} layers, two QPUs; "
          f"{len(rows)} graphs in {len(FAMILIES)} families\n")

    print("1. Does the gate cut ever change?")
    print(f"   changes of the exact minimum gate cut over {P} layers, all graphs: "
          f"{sum(r['changes'] for r in rows)}")
    print("   H_v of the same graphs (state view), min / median / max: "
          f"{min(r['hv'] for r in rows)} / {int(np.median([r['hv'] for r in rows]))}"
          f" / {max(r['hv'] for r in rows)}\n")

    print("2. How far is the fixed gate cut from the information optimum?")
    print("   family       agree at 0   gate-cut ties   excess over best at layer "
          + "  ".join(f"{L:>4d}" for L in PROBE) + "     H_v")
    for fam in FAMILIES:
        sub = [r for r in rows if r["fam"] == fam]
        if not sub:
            continue
        ex = np.median([[r["excess"][L] for L in PROBE] for r in sub], axis=0)
        print(f"   {fam:11s}  {sum(r['agree0'] for r in sub)} of {len(sub)}"
              f"        {int(np.median([r['ties'] for r in sub])):5d}          "
              + "".join(f"{100*e:5.1f}%" for e in ex)
              + f"   {int(np.median([r['hv'] for r in sub])):5d}")
    print("   (medians over seeds; ties = balanced cuts sharing the minimum gate count)\n")

    print("3. What does following the information optimum cost in EPR pairs?")
    gm = np.mean([r["gate_min"] for r in rows])
    fo = np.mean([r["follow"] for r in rows])
    print(f"   remote ZZ gates per layer, fixed gate cut:            {gm:5.2f}")
    print(f"   remote ZZ gates per layer, following the information: {fo:5.2f}"
          f"   (+{100*(fo/gm-1):.0f} %, before any cost of moving qubits)\n")

    print("4. Cross-check with an existing distributed compiler (memQ DQC)")
    memq_crosscheck(rows)

    print("\n  For a circuit known in advance, the gate cut is the right cost and")
    print("  the information cut is not. The planning limit needs a setting in")
    print("  which the information structure is what execution pays for.")


if __name__ == "__main__":
    main()
