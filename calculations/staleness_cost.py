"""
EO-2: what does it cost to keep an organisation that has gone stale?

The programme agreed with V. Ramamurthy. Everything so far was measured on
circuits fully known at compile time, and there the gate structure decides the
communication cost and never moves (gate_vs_state_partition.py). This script
builds the one class where that is not true:

    a CONSTRUCTED test class - mid-circuit measurement, branch, and a
    different interaction structure afterwards, so the future gate structure
    is not knowable when the first partition is chosen.

Whether such two-qubit branching is common in real workloads is a separate
question, and the answer is probably no. The class is constructed to create
the condition cleanly, not to represent practice.

THE CIRCUIT
  Three phases of eight layers. At the end of a phase one qubit is measured,
  and the outcome selects the interaction graph of the next phase. Every
  outcome path is run and weighted by its Born probability, so nothing is
  sampled.

ONE CURRENCY
  Every planner pays in ebits, and only in ebits:

    remote two-qubit gate   1 ebit   (a ZZ whose ends sit on different QPUs)
    qubit migration         1 ebit   (a qubit teleported to the other QPU)

THE PLANNERS, all acting on information L layers old, L being network latency
  static        choose one balanced partition, never migrate. It knows the
                program text and minimises the expected remote-gate count.
  gate          repartition to the gate optimum of the graph it has learned
                about. The strongest realistic competitor, and the one that
                needs no information about the state at all.
  information   repartition whenever the information-optimal cut moves.
  viability     repartition only when the current cut has become more than
                the tolerance worse than the information optimum - that is,
                when its horizon has expired.
  optimum       full hindsight, no latency, exact by dynamic programming over
                all balanced assignments. Not a planner; the floor.

Findings : (1) in this class staleness is expensive, and that is new. Keeping
               the initial partition costs 102 % more ebits than the floor when
               each branch changes the community structure, and 32 % more when
               the graphs merely churn. Where the branches change nothing, it
               costs exactly 0 %. In the static circuits of the earlier scripts
               it cost nothing at all, so C_stale becomes large exactly where
               the future stops being knowable;
           (2) what exploits it is the gate planner, not the information
               planner. Once the branch outcome is known the future gate
               structure is known with it, and repartitioning to the gate
               optimum reaches the floor. Chasing the information-optimal cut
               instead is worse than doing nothing at all - 110 against 105
               ebits in the first regime, 225 against 147 in the third -
               because the information cut is not what execution pays for;
           (3) the viability rule beats the chase-every-move rule by roughly
               a tenth, and both lose to staying put. Using the information as
               a TRIGGER instead, with the gate structure deciding where to
               move, matches the gate planner to within a few percent but
               never beats it. On this evidence the information adds nothing
               the gate structure has not already said;
           (4) latency is what removes the advantage, and there is a
               break-even latency L* at which reorganising stops paying:
               about 7 layers in the first regime and about 4 in the third;
           (5) L* does NOT track H_v. Pooled across regimes the two rank
               together at +0.73, but that is a between-regime effect: inside
               the regimes the correlations are +0.60 and -0.77, and the
               median ratio L*/H_v is 0.60 in one and 1.44 in the other. The
               same pooling trap as in horizon_early_signal.py section 8.

Reading  : the adaptive class does produce a real cost of staleness, which the
           static circuits never did. But the quantity that decides when to
           reorganise is the gate structure the branch reveals, not the
           information horizon, and the latency boundary does not follow H_v.
           On the evidence here, H_v remains a descriptor of the computation
           rather than a control variable for the scheduler.

Caveats  : ten qubits, two QPUs, three phases, one tolerance, six programs per
           regime, balanced bipartitions only. The planners are simple rules,
           not optimised policies; a cleverer information planner may exist.
           Migration is priced at one ebit per qubit moved and remote gates at
           one ebit each, with no fidelity model, as agreed.

Runtime : about ten seconds.
"""
import sys, pathlib, itertools
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import partition_topology as pt

N, W, PHASES = 10, 8, 3            # qubits, layers per phase, phases
GAMMA, BETA = 0.5, 0.4
SEEDS = range(6)
LATENCIES = [0, 1, 2, 4, 6, 8]
PARTS = pt.partitions(N)
PARTS_I = PARTS.astype(int)
_MOVE = None


# ------------------------------------------------------------- the circuit
def block_graph(n, m, blocks, rng, bridges=2):
    """m edges, nearly all of them inside the two given blocks."""
    inside = [(a, b) for blk in blocks for a, b in itertools.combinations(sorted(blk), 2)]
    across = [(a, b) for a in blocks[0] for b in blocks[1]]
    rng.shuffle(inside); rng.shuffle(across)
    return [tuple(e) for e in across[:bridges]] + [tuple(e) for e in inside[:m - bridges]]

def layer(psi, edges):
    for a, b in edges: psi = pt.zz(psi, a, b, GAMMA, N)
    for q in range(N): psi = pt.rx(psi, q, BETA, N)
    return psi

def outcomes(psi, q):
    """Both results of measuring qubit q, with their Born weights."""
    t = psi.reshape([2] * N)
    for b in (0, 1):
        sl = [slice(None)] * N; sl[q] = b
        part = np.zeros_like(t); part[tuple(sl)] = t[tuple(sl)]
        p = float(np.vdot(part, part).real)
        if p > 1e-12:
            yield b, p, (part / np.sqrt(p)).reshape(-1)

def paths(graphs, branch_qubits):
    """Every outcome path: its weight, its per-layer graphs and information."""
    done = []
    def walk(psi, phase, weight, snaps, edges, hist):
        E = graphs[phase][hist[-1] if hist else 0]
        snaps, edges = list(snaps), list(edges)
        for _ in range(W):
            psi = layer(psi, E)
            snaps.append(pt.mutual(psi, N)); edges.append(E)
        if phase + 1 == PHASES:
            done.append(dict(w=weight, snaps=snaps, edges=edges, hist=hist)); return
        for b, p, nxt in outcomes(psi, branch_qubits[phase]):
            walk(nxt, phase + 1, weight * p, snaps, edges, hist + [b])
    walk(np.ones(2**N, dtype=complex) / np.sqrt(2**N), 0, 1.0, [], [], [])
    return done


# ------------------------------------------------------------- the currency
def cross_all(edges):
    """Remote two-qubit gates of every balanced assignment."""
    c = np.zeros(len(PARTS_I), dtype=int)
    for a, b in edges:
        c += (PARTS_I[:, a] != PARTS_I[:, b])
    return c

def move_matrix():
    global _MOVE
    if _MOVE is None:
        _MOVE = (PARTS_I[:, None, :] != PARTS_I[None, :, :]).sum(-1)
    return _MOVE

def info_best(W_):
    return int(pt.cut_costs(W_, PARTS).argmin())

def info_excess(W_, k):
    c = pt.cut_costs(W_, PARTS); b = c.min()
    return float((c[k] - b) / b) if b > 1e-12 else 0.0


# -------------------------------------------------------------- the planners
def p_static(t, k, path, L):
    return k

def p_gate(t, k, path, L):
    s = t - L
    return int(cross_all(path["edges"][s]).argmin()) if s >= 0 else k

def p_info(t, k, path, L):
    s = t - L
    return info_best(path["snaps"][s]) if s >= 0 else k

def p_viability(t, k, path, L):
    s = t - L
    if s < 0: return k
    return info_best(path["snaps"][s]) if info_excess(path["snaps"][s], k) > pt.TOL else k

def p_trigger(t, k, path, L):
    """Information decides WHEN to reorganise, gate structure decides WHERE."""
    s = t - L
    if s < 0: return k
    if info_excess(path["snaps"][s], k) <= pt.TOL: return k
    return int(cross_all(path["edges"][s]).argmin())

PLANNERS = [("static", p_static), ("gate", p_gate),
            ("information", p_info), ("viability", p_viability),
            ("triggered", p_trigger)]

def run(path, planner, L, start):
    """Ebits paid on one path: remote gates, migrations, number of switches."""
    k, remote, mig, switches = start, 0, 0, 0
    for t, E in enumerate(path["edges"]):
        k_new = planner(t, k, path, L)
        if k_new != k:
            mig += int(move_matrix()[k, k_new]); switches += 1; k = k_new
        remote += int(sum(1 for a, b in E if PARTS_I[k, a] != PARTS_I[k, b]))
    return remote, mig, switches

def floor_cost(path):
    """The true minimum with full hindsight, by dynamic programming."""
    M = move_matrix()
    cost = cross_all(path["edges"][0]).astype(float)
    for E in path["edges"][1:]:
        cost = (cost[:, None] + M).min(0) + cross_all(E)
    return float(cost.min())

def best_static(ps):
    """The fixed partition minimising the expected remote-gate count."""
    tot = np.zeros(len(PARTS_I))
    for p in ps:
        for E in p["edges"]:
            tot += p["w"] * cross_all(E)
    return int(tot.argmin())


# ------------------------------------------------------------------ the study
SAME  = [list(range(5)), list(range(5, 10))]
OTHER = [[0, 1, 2, 7, 8], [3, 4, 5, 6, 9]]

def instance(seed, regime):
    """One branching program.

    regime 0  the branch graphs share one community structure - the cut that
              is right at the start stays right, so nothing should reorganise;
    regime 1  the branches carry different community structures - one big
              change at each branch;
    regime 2  no community structure at all, a fresh random graph per branch -
              the gate optimum moves often and by little.
    """
    rng = np.random.default_rng(seed * 977 + regime)
    if regime == 2:
        g = lambda i: pt.make_graph("random", N, 15, seed * 31 + i)
        G = [[g(0)], [g(1), g(2)], [g(3), g(4)]]
    else:
        other = OTHER if regime == 1 else SAME
        G = [[block_graph(N, 15, SAME, rng)],
             [block_graph(N, 15, SAME, rng), block_graph(N, 15, other, rng)],
             [block_graph(N, 15, other, rng), block_graph(N, 15, SAME, rng)]]
    return paths(G, [3, 7])

def horizon(ps):
    """H_v of the information structure, weighted over the outcome paths."""
    out = 0.0
    for p in ps:
        costs, best = pt.cost_table(p["snaps"], N)
        out += p["w"] * pt.h_start(costs, best)[0]
    return out

def study(regime, label):
    print(f"\n  {label}")
    rows = {name: {L: [0.0, 0.0, 0.0] for L in LATENCIES} for name, _ in PLANNERS}
    stat = flo = hv = 0.0
    for seed in SEEDS:
        ps = instance(seed, regime)
        k0 = best_static(ps)
        hv += horizon(ps) / len(SEEDS)
        flo += sum(p["w"] * floor_cost(p) for p in ps) / len(SEEDS)
        for name, planner in PLANNERS:
            for L in LATENCIES:
                for p in ps:
                    r, m, s = run(p, planner, L, k0)
                    acc = rows[name][L]
                    acc[0] += p["w"] * r / len(SEEDS)
                    acc[1] += p["w"] * m / len(SEEDS)
                    acc[2] += p["w"] * s / len(SEEDS)
        stat += sum(p["w"] * run(p, p_static, 0, k0)[0] for p in ps) / len(SEEDS)
    print(f"    information horizon H_v of these circuits: {hv:.1f} layers")
    print(f"    staying put costs {stat:.1f} ebits; the floor with full hindsight is {flo:.1f}")
    print(f"    so C_stale = {stat - flo:.1f} ebits, {100*(stat/flo - 1):.0f} % above the floor\n")
    print("    planner        " + "".join(f"  L={L:<2d}" for L in LATENCIES)
          + "     (total ebits; migrations in brackets)")
    for name, _ in PLANNERS:
        line = f"    {name:12s} "
        for L in LATENCIES:
            r, m, s = rows[name][L]
            line += f" {r+m:5.1f}"
        print(line + "   " + " ".join(f"({rows[name][L][1]:.0f})" for L in LATENCIES))
    return rows, stat, flo, hv


def break_even(ps, k0, grid=range(0, 15)):
    """The latency at which reorganising stops paying, by linear interpolation."""
    stat = sum(p["w"] * run(p, p_static, 0, k0)[0] for p in ps)
    tot = []
    for L in grid:
        t = sum(p["w"] * sum(run(p, p_gate, L, k0)[:2]) for p in ps)
        tot.append(t)
    for i in range(1, len(tot)):
        if tot[i] >= stat > tot[i-1]:
            f = (stat - tot[i-1]) / (tot[i] - tot[i-1])
            return float(list(grid)[i-1] + f)
    return float("nan") if tot[0] >= stat else float(list(grid)[-1])

def boundary():
    """Per program: the information horizon against the break-even latency."""
    from scipy.stats import spearmanr
    print("\n  Where does reorganising stop paying, and does H_v know it?\n")
    print("    regime                         program   H_v    break-even L")
    xs, ys = [], []
    for regime, label in ((1, "one large change per branch"),
                          (2, "many small changes        "),
                          (0, "no real change            ")):
        for seed in SEEDS:
            ps = instance(seed, regime)
            k0 = best_static(ps)
            h, L = horizon(ps), break_even(ps, k0)
            print(f"    {label}        {seed}     {h:5.1f}     {L:6.2f}")
            if np.isfinite(L) and regime != 0:
                xs.append(h); ys.append(L)
    xs, ys = np.array(xs), np.array(ys)
    print(f"\n    pooled over the two regimes where reorganising pays at all:"
          f" rank correlation {spearmanr(xs, ys)[0]:+.2f} ({len(xs)} programs)")
    print("    BUT inside each regime separately, which is the only fair test:")
    n = len(list(SEEDS))
    for i, name in ((0, "one large change per branch"), (n, "many small changes        ")):
        h, l = xs[i:i+n], ys[i:i+n]
        print(f"      {name}   rho {spearmanr(h, l)[0]:+.2f}"
              f"   median L*/H_v {np.median(l/h):.2f}")
    print("    The pooled number is a between-regime effect, not a per-program law;")
    print("    the two regimes disagree in sign. L* does not track H_v here.")

def main():
    print("EO-2: a constructed class in which the future gate structure is unknown")
    print(f"n = {N}, {PHASES} phases of {W} layers, two QPUs, "
          f"{len(list(SEEDS))} programs per setting, all outcome paths weighted")
    study(1, "one large change at each branch (different community structure)")
    study(0, "no real change (the branches share one community structure)")
    study(2, "many small changes (random graphs, no community structure)")
    boundary()
    print("\n  Staleness is expensive here, which it was not in the static circuits.")
    print("  What exploits it is the gate structure the branch reveals, not the")
    print("  information horizon; and the latency at which reorganising stops")
    print("  paying does not follow H_v. H_v stays a descriptor, not a control.")


if __name__ == "__main__":
    main()
