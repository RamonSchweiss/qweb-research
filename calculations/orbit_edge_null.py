"""
A tighter null for the matched-window control of the routed-partition orbit.

Belongs to designs/design_routed_partition_orbit_EN.md, addendum 3. It carries
out the tightening that the run of 20 October 2026 promised in its own printout
and left undone:

    "the random arm draws its swaps uniformly over all qubit pairs, while the
     router may only use edges of the coupling map. The random arm therefore
     scrambles harder than the hardware could, so the gap measured above is an
     UPPER bound on the router's advantage. A tighter null -- random swaps
     restricted to coupling edges -- would narrow it. The direction of the
     result does not depend on this; the size of the margin does. Tightening it
     would be a further dated addendum and has not been done."

The defect ran in our favour, which is the reason to close it rather than leave
it. An arm allowed moves the hardware cannot make loses the comparison for a
reason that has nothing to do with routing, and the published margin inherits
that.

What runs here : both nulls, side by side, on one set of real runs.
                 Arm A is the published one, swaps drawn uniformly over all
                 qubit pairs. Arm B is the tightened one, swaps drawn uniformly
                 over the undirected edges of the coupling map -- the only
                 swaps a router could have chosen. Everything else is held
                 fixed: the same problem graphs, the same router seeds, the
                 same per-layer swap budget, the same window length W = d, the
                 same control seeds, the same question.

Decision rule : unchanged from addendum 2 and applied to BOTH arms. If a
                control rate lies within the seed-to-seed scatter of the router
                rate, constancy carries no information about routing on that
                topology and every claim resting on it is withdrawn. No
                threshold is chosen after the numbers are seen.

                Arm B can only raise the control rate, so this measurement can
                withdraw claims that arm A left standing. It cannot add any.
                That asymmetry is the point: the tightening is registered
                knowing it can only cost.

Reproduction  : arm A must reproduce the per-seed shares printed on
                20 October. They are hard-coded below and checked. A mismatch
                means this script is not measuring the same thing as the
                published run, and nothing below it is valid.

Needs    : numpy, qiskit, partition_topology, routed_partition_orbit. Without
           qiskit this says so and exits, the same way routed_partition_orbit
           does. It used to raise NameError instead: that module guards its own
           entry point but not its topology(), and nothing here checked before
           calling it.
Runtime  : several minutes, dominated by re-routing the real orbits.
"""
import sys

import numpy as np

import routed_partition_orbit as rpo
import partition_topology as pt

TOPOLOGIES = ["heavy-hex", "grid", "line"]      # all-to-all has no run with d >= 2
CTRL_SEEDS = range(5)

# What the run of 20 October 2026 printed for arm A. Checked, not trusted.
PUBLISHED = {
    "heavy-hex": {"runs": 68, "router_hits": 44,
                  "arm_a": [0.12, 0.07, 0.09, 0.06, 0.07]},
    "grid":      {"runs": 30, "router_hits": 9,
                  "arm_a": [0.20, 0.10, 0.13, 0.13, 0.13]},
    "line":      {"runs": 40, "router_hits": 23,
                  "arm_a": [0.05, 0.07, 0.07, 0.07, 0.07]},
}


# --------------------------------------------------------------- the tighter arm

def coupling_edges(cm):
    """The undirected edges of a CouplingMap, deduplicated.

    `topology` adds both directions for heavy-hex and leaves the qiskit
    constructors to do as they do, so the directed list is not a move set.
    """
    return sorted({tuple(sorted(map(int, e))) for e in cm.get_edges()})


def permutation_window_edges(n, edges, cm_edges, swap_counts, t, W, seed, S):
    """Arm B: rpo.permutation_window with the move set restricted to cm_edges.

    Line for line the published control, with one substitution: the pair (a, b)
    is drawn from the coupling map instead of from all qubit pairs. a and b are
    PHYSICAL qubits, which is what a swap acts on and what the coupling map
    constrains; the logical labels they carry come from `at`.
    """
    rng = np.random.default_rng(seed)
    base = [tuple(sorted(e)) for e in edges]
    lay = tuple(range(n))
    args = []
    for k in range(t + W):
        nsw = swap_counts[k] if k < len(swap_counts) else swap_counts[-1]
        at = {ph: lg for lg, ph in enumerate(lay)}
        inter = list(base)
        for _ in range(nsw):
            a, b = cm_edges[int(rng.integers(len(cm_edges)))]
            la, lb = at[a], at[b]
            inter.append((la, lb) if la < lb else (lb, la))
            at[a], at[b] = at[b], at[a]
        args.append(rpo.best_cut(n, inter, S)[0])
        lay = tuple(ph for _lg, ph in sorted((lg, ph) for ph, lg in at.items()))
    return len(set(args[t:])) == 1


def verdict(mean, scatter):
    lo, hi = min(scatter), max(scatter)
    if lo <= mean <= hi:
        return "WITHIN the router scatter - constancy carries no information"
    return "below the router scatter" if mean < lo else "ABOVE the router scatter"


# ---------------------------------------------------------------------- report

def main():
    print(__doc__)

    # routed_partition_orbit binds CouplingMap only inside its guarded import
    # and uses it unguarded in topology(). Run as a script it checks this flag
    # and reports; imported, nobody did, so the first call raised NameError.
    if rpo.qiskit is None:
        print("  qiskit is not installed - this measurement is skipped.")
        print("  To run it:  pip install qiskit")
        return 0

    N, M = rpo.N, rpo.M
    S = pt.partitions(N)
    graphs = [(f, s, pt.make_graph(f, N, M, s))
              for f in rpo.FAMILIES for s in rpo.GRAPH_SEEDS]
    graphs = [(f, s, E) for f, s, E in graphs if E is not None]
    by_key = {(f, s): E for f, s, E in graphs}
    print(f"{len(graphs)} problem graphs, {N} qubits, {M} edges -- the same set "
          f"as the run of 20 October.\n")

    pooled = {"router": [], "a": [], "b": []}
    mismatch = []

    for name in TOPOLOGIES:
        cm, desc = rpo.topology(name, N)
        cme = coupling_edges(cm)

        real = {}
        for f, s, E in graphs:
            for rs in rpo.ROUTER_SEEDS:
                t, d, recs = rpo.orbit(N, E, cm, rs)
                if d is None or d < 2:
                    continue
                a = rpo.analyse(N, t, d, recs, S)
                real[(f, s, rs)] = (t, d, [r["swaps"] for r in recs],
                                    bool(a["cycle_constant"]))
        keys = sorted(real)
        if not keys:
            print(f"   {name}: no run with d >= 2, control not applicable\n")
            continue

        hits_r = sum(real[k][3] for k in keys)
        r = hits_r / len(keys)
        per_rseed = {}
        for k in keys:
            per_rseed.setdefault(k[2], []).append(real[k][3])
        scatter = sorted(sum(v) / len(v) for v in per_rseed.values())

        arm_a, arm_b = [], []
        for cseed in CTRL_SEEDS:
            seed = 9000 + 97 * cseed
            ha = hb = 0
            for k in keys:
                t, d, sc, _ = real[k]
                E = by_key[(k[0], k[1])]
                ha += rpo.permutation_window(N, E, sc, t, d, seed, S)
                hb += permutation_window_edges(N, E, cme, sc, t, d, seed, S)
            arm_a.append(ha / len(keys))
            arm_b.append(hb / len(keys))

        ma, mb = float(np.mean(arm_a)), float(np.mean(arm_b))
        pub = PUBLISHED[name]

        print(f"   {name}  ({desc})")
        print(f"   {len(cme)} undirected coupling edges, "
              f"against {N * (N - 1) // 2} qubit pairs: a move set "
              f"{len(cme) / (N * (N - 1) / 2):.0%} the size.")
        print(f"      router   constant in {hits_r} of {len(keys)} = {r:.2f}"
              f"   (per router seed: {', '.join(f'{x:.2f}' for x in scatter)})")
        print(f"      arm A    {', '.join(f'{x:.2f}' for x in arm_a)}"
              f"   mean {ma:.2f}   {verdict(ma, scatter)}")
        print(f"      arm B    {', '.join(f'{x:.2f}' for x in arm_b)}"
              f"   mean {mb:.2f}   {verdict(mb, scatter)}")

        ok = (len(keys) == pub["runs"] and hits_r == pub["router_hits"]
              and all(abs(x - y) < 0.005 for x, y in zip(arm_a, pub["arm_a"])))
        if ok:
            print("      reproduction of 20 October: arm A and the router rate "
                  "match to the printed digits.")
        else:
            mismatch.append(name)
            print(f"      REPRODUCTION FAILED. published: {pub['runs']} runs, "
                  f"{pub['router_hits']} router hits, arm A {pub['arm_a']}.")

        moved = verdict(ma, scatter) != verdict(mb, scatter)
        print(f"      the tightening {'CHANGES' if moved else 'does not change'}"
              f" the verdict on this topology.")
        print(f"      margin router - control: {r - ma:+.2f} under arm A, "
              f"{r - mb:+.2f} under arm B.\n")

        pooled["router"].append((hits_r, len(keys)))
        pooled["a"].append(ma)
        pooled["b"].append(mb)

    if mismatch:
        print("=" * 78)
        print(f"  Arm A does not reproduce the published run on: "
              f"{', '.join(mismatch)}.")
        print("  Nothing above is a valid tightening of anything, because the")
        print("  thing it is being compared against has not been reproduced.")
        return 1

    rp = sum(h for h, _ in pooled["router"]) / sum(k for _, k in pooled["router"])
    print("=" * 78)
    print(f"  pooled: router {rp:.2f}, arm A {np.mean(pooled['a']):.2f}, "
          f"arm B {np.mean(pooled['b']):.2f}")
    print()
    print("  Arm B is the honest null: every swap in it is a swap the router")
    print("  could have made. Where it still falls clearly below the router")
    print("  rate, constancy is a property of what the router does. Where it")
    print("  rises into the router's scatter, the claims resting on constancy")
    print("  for that topology are withdrawn, by the rule fixed in advance.")
    print()
    print("  What remains untightened: the number of swaps per layer is copied")
    print("  from the real run, but their PLACEMENT in the layer is not, and a")
    print("  router chooses swaps that are mutually compatible within a layer")
    print("  while this arm may draw the same edge twice. That is a further")
    print("  limit, stated here rather than closed, and it runs in the same")
    print("  direction as the one closed above.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
