"""
routed_partition_orbit.py — periodicity of the routed circuit and the stability
of the gate-optimal cut.

Implements the pre-registered design note

    designs/design_routed_partition_orbit_EN.md          (2026-10-16)
    designs/design_routed_partition_orbit_EN_addendum_1  (2026-10-18)

and nothing beyond it. Where the note left a choice open, the choice made here
is printed with the results rather than buried in the code.

WHAT THIS MEASURES, AND THE LIMIT THAT CAME FIRST
-------------------------------------------------
Each QAOA layer is routed as a closed block starting from the layout current at
that point, with no lookahead across the layer boundary. Routing one layer is
then a map f of the finite layout space into itself, so the orbit
m, f(m), f(f(m)), ... is eventually periodic with some transient t and period d.
This is arithmetic. What is measured are the values of t and d, and whether the
gate-optimal cut is constant over the cycle.

Section 7 of the design note named the condition that would make this argument
inapplicable: a router that sees across layer boundaries. Addendum 1 records
that the condition holds for Qiskit's SABRE and for TKET at their standard
compiler levels, which route the whole circuit at once. This measurement
therefore describes LAYER-BY-LAYER BLOCK ROUTING ONLY and says nothing about
those defaults. That limit was written down before the answer was known.

Run with no arguments. Needs numpy, qiskit, and partition_topology.py from
calculations/ (imported, not reimplemented, so that the problem graphs are
identical to those of gate_vs_state_partition.py rather than merely similar).
"""

import itertools
import os
import sys
import time
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
for cand in (os.path.join(HERE, "..", "calculations"), HERE):
    if os.path.isfile(os.path.join(cand, "partition_topology.py")):
        sys.path.insert(0, os.path.abspath(cand))
        break
import partition_topology as pt                                   # noqa: E402

try:                                                              # noqa: E402
    import qiskit
    from qiskit import QuantumCircuit
    from qiskit.transpiler import CouplingMap, Layout, PassManager
    from qiskit.transpiler.passes import (
        ApplyLayout, EnlargeWithAncilla, FullAncillaAllocation, SabreSwap,
        SetLayout)
except ImportError:                       # same convention as the memQ
    qiskit = None                         # cross-check in gate_vs_state_partition.py

# ----------------------------------------------------------------- the grid
FAMILIES = ["random", "ring", "path", "regular", "scale-free", "community", "grid"]
GRAPH_SEEDS = range(3)                 # the 21 graphs of gate_vs_state_partition.py
N, M = 10, 15                          # ... which are ten qubits, fifteen edges
ROUTER_SEEDS = range(5)                # section 4, seed control
P_MAX = 64                             # section 6, stopping rule, never raised
TOPOLOGIES = ["heavy-hex", "grid", "line", "all-to-all"]

# addendum 1, A1.4: one comparison cell, so that Daniel Hug's return-swap
# figures can be compared like for like instead of merely in magnitude
CELL_N = 14
CELL_TOPOLOGIES = ["heavy-hex", "grid-4x4", "line"]


# ------------------------------------------------------------- topologies
def heavy_hex_subgraph(n):
    """
    Connected n-node induced subgraph of the heavy-hex lattice.

    A breadth-first ball from node 0 lands in a corner of the lattice and comes
    out a tree, which would make this topology a second copy of the line. The
    start node is therefore chosen deterministically: breadth-first from every
    node in turn, keep the induced subgraph with the most edges, ties going to
    the lowest start node. That picks up the rings the lattice actually has.
    """
    big = CouplingMap.from_heavy_hex(5)
    adj = defaultdict(set)
    for a, b in big.get_edges():
        adj[a].add(b)
        adj[b].add(a)
    nodes = sorted(adj)

    best = None
    for start in nodes:
        seen, order, queue = {start}, [start], [start]
        while queue and len(order) < n:
            v = queue.pop(0)
            for w in sorted(adj[v]):
                if w not in seen and len(order) < n:
                    seen.add(w)
                    order.append(w)
                    queue.append(w)
        if len(order) < n:
            continue
        idx = {v: i for i, v in enumerate(order)}
        e = sorted({tuple(sorted((idx[a], idx[b])))
                    for a, b in big.get_edges() if a in idx and b in idx})
        if best is None or len(e) > len(best):
            best = e
    if best is None:
        raise RuntimeError(f"heavy-hex lattice too small for {n} nodes")
    return best


def grid_edges(rows, cols, keep):
    """Row-major rows x cols grid, restricted to the first `keep` sites."""
    e = []
    for i in range(rows):
        for j in range(cols):
            v = i * cols + j
            if j + 1 < cols:
                e.append((v, v + 1))
            if i + 1 < rows:
                e.append((v, v + cols))
    return sorted({tuple(sorted(p)) for p in e if p[0] < keep and p[1] < keep})


def topology(name, n):
    """Return (CouplingMap, description) for a named topology at n qubits."""
    if name == "all-to-all":
        return CouplingMap.from_full(n), f"complete graph on {n}"
    if name == "line":
        return CouplingMap.from_line(n), f"path of {n}"
    if name == "heavy-hex":
        e = heavy_hex_subgraph(n)
        rings = len(e) - n + 1
        note = (" -- A TREE: the rings of the heavy-hex lattice have twelve "
                "qubits, so no induced subgraph this small can contain one"
                if rings == 0 else f", {rings} independent ring(s)")
        return (CouplingMap([list(x) for x in e] + [list(reversed(x)) for x in e]),
                f"{n}-node subgraph of heavy-hex(5), {len(e)} edges{note}")
    if name == "grid":
        r = max(x for x in range(1, int(n ** 0.5) + 1) if n % x == 0)
        e = grid_edges(r, n // r, n)
        return (CouplingMap([list(x) for x in e] + [list(reversed(x)) for x in e]),
                f"{r}x{n // r} grid, {len(e)} edges")
    if name == "grid-4x4":
        e = grid_edges(4, 4, n)
        return (CouplingMap([list(x) for x in e] + [list(reversed(x)) for x in e]),
                f"4x4 grid, first {n} sites, {len(e)} edges")
    raise ValueError(name)


# ------------------------------------------------------------- the map f
def layer_circuit(n, edges):
    """One QAOA layer. Only the two-qubit gates matter for routing; the mixer
    is single-qubit and is never routed."""
    qc = QuantumCircuit(n)
    for a, b in edges:
        qc.rzz(0.5, a, b)
    return qc


def route_block(n, edges, cm, layout, seed):
    """
    Route one layer as a closed block from `layout` (layout[logical] = physical).

    Returns (exit_layout, interaction_edges, n_swaps, n_zz_crossing_pairs)
    where interaction_edges are LOGICAL pairs, one per two-qubit gate in the
    routed block -- ZZ gates and swaps alike -- and the fourth value lists the
    same for the ZZ gates alone, so that the contribution of swaps can be
    separated (section 2, item 5).
    """
    qc = layer_circuit(n, edges)
    init = Layout({qc.qubits[lg]: ph for lg, ph in enumerate(layout)})
    pm = PassManager([
        SetLayout(init),
        FullAncillaAllocation(cm), EnlargeWithAncilla(), ApplyLayout(),
        SabreSwap(cm, heuristic="decay", seed=seed, trials=1),
    ])
    out = pm.run(qc)

    at = {ph: lg for lg, ph in enumerate(layout)}        # physical -> logical
    inter, zz_only, nsw = [], [], 0
    for inst in out.data:
        if len(inst.qubits) != 2:
            continue
        a = out.find_bit(inst.qubits[0]).index
        b = out.find_bit(inst.qubits[1]).index
        la, lb = at[a], at[b]
        pair = (la, lb) if la < lb else (lb, la)
        inter.append(pair)
        if inst.operation.name == "swap":
            at[a], at[b] = at[b], at[a]                  # edge first, then swap
            nsw += 1
        else:
            zz_only.append(pair)
    exit_layout = tuple(ph for _lg, ph in sorted((lg, ph) for ph, lg in at.items()))
    assert sorted(exit_layout) == list(range(n)), "exit layout is not a bijection"
    return exit_layout, inter, nsw, zz_only


# ------------------------------------------------------------- the cut
def weights(n, pairs):
    w = np.zeros((n, n))
    for a, b in pairs:
        w[a, b] += 1.0
        w[b, a] += 1.0
    return w


def best_cut(n, pairs, S):
    """Exhaustive balanced bipartition. Returns (argmin index, cost, margin,
    number of partitions sharing the minimum)."""
    c = pt.cut_costs(weights(n, pairs), S)
    k = int(np.argmin(c))
    lo = c[k]
    ties = int(np.sum(c <= lo + 1e-9))
    second = np.sort(c)[ties] if ties < len(c) else lo
    return k, float(lo), float(second - lo), ties


# ------------------------------------------------------------- the orbit
def orbit(n, edges, cm, seed, p_max=P_MAX):
    """Iterate f from the identity layout until a layout repeats.
    Returns (t, d, per-layer records) or (None, None, records) if no cycle
    appears within p_max. p_max is never raised to find one."""
    lay = tuple(range(n))
    seen = {lay: 0}
    recs = []
    for k in range(p_max):
        nxt, inter, nsw, zz = route_block(n, edges, cm, lay, seed)
        recs.append({"layout": lay, "inter": inter, "swaps": nsw, "zz": zz})
        if nxt in seen:
            return seen[nxt], k + 1 - seen[nxt], recs
        seen[nxt] = k + 1
        lay = nxt
    return None, None, recs


def permutation_orbit(n, edges, swap_counts, seed, p_max=P_MAX):
    """
    Section 4, permutation control.

    The ZZ gates of a layer always sit on the same LOGICAL pairs whatever the
    layout, so the whole variation of the routed interaction graph comes from
    the swaps. The control therefore replaces the router's chosen swaps with
    random transpositions of the same count per layer -- "a sequence of random
    permutations of equal length in place of the router" -- and asks the same
    question of the result. If the cut is constant here too, constancy says
    nothing about routing.
    """
    rng = np.random.default_rng(seed)
    base = [tuple(sorted(e)) for e in edges]
    lay = tuple(range(n))
    seen = {lay: 0}
    recs = []
    for k in range(p_max):
        nsw = swap_counts[k % len(swap_counts)]
        at = {ph: lg for lg, ph in enumerate(lay)}
        inter = list(base)
        for _ in range(nsw):
            a, b = rng.choice(n, size=2, replace=False)
            la, lb = at[int(a)], at[int(b)]
            inter.append((la, lb) if la < lb else (lb, la))
            at[int(a)], at[int(b)] = at[int(b)], at[int(a)]
        recs.append({"layout": lay, "inter": inter, "swaps": nsw, "zz": base})
        nxt = tuple(ph for _lg, ph in sorted((lg, ph) for ph, lg in at.items()))
        if nxt in seen:
            return seen[nxt], k + 1 - seen[nxt], recs
        seen[nxt] = k + 1
        lay = nxt
    return None, None, recs


# ------------------------------------------------------------- reporting
def analyse(n, t, d, recs, S):
    """Cut statistics over the cycle and, separately, over the transient."""
    cuts = [best_cut(n, r["inter"], S) for r in recs]
    zz_cuts = [best_cut(n, r["zz"], S) if r["zz"] is not None else None
               for r in recs]
    out = {"t": t, "d": d, "layers": len(recs),
           "swaps_mean": float(np.mean([r["swaps"] for r in recs]))}
    if t is None:
        out["cycle_constant"] = None
        out["transient_constant"] = None
        out["cost_mean"] = float(np.mean([c[1] for c in cuts]))
        out["margin_mean"] = float(np.mean([c[2] for c in cuts]))
        out["swap_extra"] = None
        return out
    cyc = cuts[t:t + d]
    tra = cuts[:t]
    out["cycle_constant"] = len({c[0] for c in cyc}) == 1
    out["transient_constant"] = (len({c[0] for c in tra}) == 1) if tra else None
    out["cost_mean"] = float(np.mean([c[1] for c in cyc]))
    out["margin_mean"] = float(np.mean([c[2] for c in cyc]))
    out["ties_mean"] = float(np.mean([c[3] for c in cyc]))
    extra = [cuts[i][1] - zz_cuts[i][1] for i in range(t, t + d)
             if zz_cuts[i] is not None]
    out["swap_extra"] = float(np.mean(extra)) if extra else None
    return out


def banner(txt):
    print()
    print(txt)
    print("-" * len(txt))


def main():
    t0 = time.time()
    if qiskit is None:
        print("routed_partition_orbit.py")
        print("  qiskit is not installed - this measurement is skipped.")
        print("  To run it:  pip install qiskit")
        return 0
    print(f"routed_partition_orbit.py   qiskit {qiskit.__version__}, "
          f"numpy {np.__version__}, python {sys.version.split()[0]}")
    print("router: SabreSwap(heuristic='decay', trials=1), one layer per block, "
          "no lookahead across the boundary")
    print("design: designs/design_routed_partition_orbit_EN.md + addendum 1. "
          f"p_max = {P_MAX}, never raised.")
    print()
    print("LIMIT, stated first as section 7 requires: this measures "
          "layer-by-layer block routing only.")
    print("Qiskit SABRE and TKET at their standard levels route the whole "
          "circuit with lookahead; for")
    print("that regime the map layout -> layout is not well defined per layer "
          "and none of this applies.")

    S10 = pt.partitions(N)
    graphs = [(f, s, pt.make_graph(f, N, M, s))
              for f in FAMILIES for s in GRAPH_SEEDS]
    graphs = [(f, s, E) for f, s, E in graphs if E is not None]
    print(f"\n{len(graphs)} problem graphs, {N} qubits, {M} edges, "
          f"from partition_topology.make_graph -- the same set as "
          f"gate_vs_state_partition.py")

    # ---------------------------------------------------------------- 1
    banner("Control 1  all-to-all: the pipeline check, run first")
    print("On complete coupling no swaps are inserted, so t = 0 and d = 1 must")
    print("come out and the cut must equal the unrouted gate cut. If not, the")
    print("pipeline is broken and no result below is valid.")
    cm, desc = topology("all-to-all", N)
    bad = 0
    for f, s, E in graphs:
        t, d, recs = orbit(N, E, cm, 0, p_max=3)
        k_routed, _, _, _ = best_cut(N, recs[0]["inter"], S10)
        k_plain, _, _, _ = best_cut(N, [tuple(sorted(e)) for e in E], S10)
        if not (t == 0 and d == 1 and recs[0]["swaps"] == 0 and k_routed == k_plain):
            bad += 1
            print(f"   FAIL {f}/{s}: t={t} d={d} swaps={recs[0]['swaps']} "
                  f"cut {k_routed} vs {k_plain}")
    if bad:
        print(f"\n   {bad} of {len(graphs)} failed. Stopping: nothing below would be valid.")
        return 1
    print(f"   passed on all {len(graphs)} graphs ({desc})")

    # ---------------------------------------------------------------- 2
    banner("The grid  21 graphs x 4 topologies x 5 router seeds")
    swaps, allrows = {}, {}
    for name in TOPOLOGIES:
        cm, desc = topology(name, N)
        print(f"\n   {name}  ({desc})")
        print("   graph              seed   t    d   cycle cut   transient cut"
              "   swaps/layer   cut cost   margin   swaps add")
        rows = []
        for f, s, E in graphs:
            for rs in ROUTER_SEEDS:
                t, d, recs = orbit(N, E, cm, rs)
                a = analyse(N, t, d, recs, S10)
                a["family"], a["gseed"], a["rseed"] = f, s, rs
                rows.append(a)
                cc = ("-" if a["cycle_constant"] is None
                      else ("constant" if a["cycle_constant"] else "MOVES"))
                tc = ("-" if a["transient_constant"] is None
                      else ("constant" if a["transient_constant"] else "moves"))
                ex = "-" if a["swap_extra"] is None else f"{a['swap_extra']:8.2f}"
                print(f"   {f:12s} {s:4d} {rs:6d} "
                      f"{'-' if t is None else t:>4} {'-' if d is None else d:>4}"
                      f"   {cc:9s}   {tc:9s}   {a['swaps_mean']:9.2f}"
                      f"   {a['cost_mean']:8.2f} {a['margin_mean']:8.2f} {ex}")
                swaps[(name, f, s, rs)] = [r["swaps"] for r in recs]
        summarise(name, rows)
        allrows[name] = rows

    # ---------------------------------------------------------------- 3
    banner("Control 2  random permutations in place of the router")
    print("The ZZ gates of a layer sit on the same logical pairs whatever the")
    print("layout, so the whole variation of the interaction graph comes from")
    print("the swaps. This control keeps the per-layer swap COUNT of the real")
    print("run and chooses the swaps at random instead. If the cut is constant")
    print("here too, constancy says nothing about routing.")
    for name in TOPOLOGIES:
        rows = []
        for f, s, E in graphs:
            for rs in ROUTER_SEEDS:
                sc = swaps.get((name, f, s, rs))
                if not sc:
                    continue
                t, d, recs = permutation_orbit(N, E, sc, 1000 + rs)
                a = analyse(N, t, d, recs, S10)
                a["family"], a["gseed"], a["rseed"] = f, s, rs
                rows.append(a)
        cyc = [r for r in rows if r["d"] is not None]
        const = sum(1 for r in cyc if r["cycle_constant"])
        print(f"\n   {name}: cycle in {len(cyc)} of {len(rows)}; "
              f"cut constant over the cycle in {const} of {len(cyc)}")
        nontrivial(cyc, "   ")
        real = [r for r in allrows[name] if r["d"] is not None and r["d"] >= 2]
        rc = sum(1 for r in real if r["cycle_constant"])
        print(f"   router, same split: constant in {rc} of {len(real)}")

    # ---------------------------------------------------------------- 4
    banner(f"Addendum 1, A1.4  comparison cell at n = {CELL_N}")
    print("A complete interaction graph on fourteen qubits -- 91 ZZ terms, since")
    print("C(14,2) = 91 -- on the three topologies Daniel Hug measured, so that")
    print("his return-swap figures can be set beside these like for like.")
    cellE = [tuple(sorted(p)) for p in itertools.combinations(range(CELL_N), 2)]
    Scell = pt.partitions(CELL_N)
    print(f"   {len(cellE)} edges, {Scell.shape[0]} balanced bipartitions "
          f"enumerated exhaustively")
    # Daniel Hug, correspondence of 18 October 2026: return swaps per layer,
    # Qiskit / TKET, conservative upper bounds (SWAP = 3 CX, no cancellation
    # across the block boundary, approximate token swapping).
    HIS = {"heavy-hex": (67, 28), "grid-4x4": (22, 22), "line": (85, 61)}
    print()
    print("   topology    seed    t    d   cycle cut   swaps/layer   "
          "swaps add   his return swaps/layer")
    cell_rows = defaultdict(list)
    for name in CELL_TOPOLOGIES:
        cm, desc = topology(name, CELL_N)
        for rs in ROUTER_SEEDS:
            t, d, recs = orbit(CELL_N, cellE, cm, rs)
            a = analyse(CELL_N, t, d, recs, Scell)
            cell_rows[name].append((a, recs))
            cc = ("-" if a["cycle_constant"] is None
                  else ("constant" if a["cycle_constant"] else "MOVES"))
            ex = "-" if a["swap_extra"] is None else f"{a['swap_extra']:8.2f}"
            q, tk = HIS[name]
            print(f"   {name:11s} {rs:4d} {'-' if t is None else t:>4} "
                  f"{'-' if d is None else d:>4}   {cc:9s}   "
                  f"{a['swaps_mean']:9.2f}   {ex}   {q:6d} / {tk}")
        print(f"      ({desc})")

    # ------------------------------------------------------------ H3, H4
    banner("H3  is the free orbit cheaper than enforced period one?")
    print("Enforcing d = 1 buys layer periodicity with a return network every")
    print("layer. The free orbit gets periodicity after t layers and keeps it")
    print("over d, paying nothing extra for it. So H3 turns on d, not on gate")
    print("counts: if d is small the free orbit is cheaper by exactly the")
    print("return-swap cost, and if d is large the periodicity is useless.")
    print()
    for name in CELL_TOPOLOGIES:
        ds = [a["d"] for a, _ in cell_rows[name] if a["d"] is not None]
        q, tk = HIS[name]
        if ds:
            print(f"   {name:11s} d over 5 seeds: {ds}   "
                  f"enforced pays {q} (Qiskit) / {tk} (TKET) return swaps per layer")
        else:
            print(f"   {name:11s} no cycle within p_max -- H3 not answered here")

    banner("H4  on the line, is period two free?  (registered before the run)")
    print("Daniel Hug's conjecture, stated in correspondence of 18 October 2026")
    print("and explicitly not measured by him: the exit permutation of a")
    print("block-routed complete layer on a line is the reversal, which is an")
    print("involution, so t = 0 and d = 2 with no return swaps at all.")
    print()
    rev = tuple(range(CELL_N - 1, -1, -1))
    for a, recs in cell_rows["line"]:
        first_exit = recs[1]["layout"] if len(recs) > 1 else None
        print(f"   seed: t = {a['t']}, d = {a['d']}, "
              f"exit of layer 0 is the reversal: {first_exit == rev}")
    ds = [a["d"] for a, _ in cell_rows["line"] if a["d"] is not None]
    ts = [a["t"] for a, _ in cell_rows["line"] if a["t"] is not None]
    if ds and set(ds) == {2} and set(ts) == {0}:
        print("\n   H4 HOLDS as stated: t = 0 and d = 2 on every seed.")
    else:
        print(f"\n   H4 REFUTED as stated. t values {sorted(set(ts))}, "
              f"d values {sorted(set(ds))}; the registered null result was "
              f"'the exit permutation is not an involution, or d > 2'.")

    print(f"\ntotal wall clock {time.time() - t0:.0f} s")
    return 0


def summarise(name, rows):
    cyc = [r for r in rows if r["d"] is not None]
    print(f"   -- {name}: cycle found in {len(cyc)} of {len(rows)} runs", end="")
    if cyc:
        ds = [r["d"] for r in cyc]
        ts = [r["t"] for r in cyc]
        const = sum(1 for r in cyc if r["cycle_constant"])
        print(f"; d min/median/max {min(ds)}/{int(np.median(ds))}/{max(ds)}"
              f"; t min/median/max {min(ts)}/{int(np.median(ts))}/{max(ts)}"
              f"; cut constant over the cycle in {const} of {len(cyc)}")
    else:
        print()
    byfam = defaultdict(list)
    for r in cyc:
        byfam[r["family"]].append(r)
    for f in sorted(byfam):
        rs = byfam[f]
        print(f"      {f:12s} {len(rs):2d} runs, d median "
              f"{int(np.median([r['d'] for r in rs])):3d}, cut constant in "
              f"{sum(1 for r in rs if r['cycle_constant'])} of {len(rs)}")
    nontrivial(cyc, "      ")


def nontrivial(cyc, pad=""):
    """
    The constancy figure above is the one section 2 of the design note asks
    for. It is inflated wherever d = 1, because a one-layer cycle is constant
    by definition and the question has no content there. This split was added
    after the first look at the numbers and is printed BESIDE the registered
    figure, never instead of it: section 6 forbids adding data after that look,
    not disclosing a further breakdown of the data already taken.
    """
    d1 = [r for r in cyc if r["d"] == 1]
    d2 = [r for r in cyc if r["d"] >= 2]
    c = sum(1 for r in d2 if r["cycle_constant"])
    print(f"{pad}of those, {len(d1)} have d = 1 (constant by definition). "
          f"Among the {len(d2)} runs with d >= 2, the cut is constant in {c} "
          f"and moves in {len(d2) - c}.")
    return len(d2), c


if __name__ == "__main__":
    sys.exit(main())
