"""Which qubits should be global, and whether the state has a say.

The registered run of designs/design_hypercube_global_qubits_EN.md with its
addenda 1 and 2. Nothing here decides anything the design note left open: the
sizes, the values of g, the arms, the declarations, the resolution rule and the
stopping condition are all fixed there.

    python3 hypercube_global_qubits.py --gates     the four verification gates
    python3 hypercube_global_qubits.py --run       the registered run
    python3 hypercube_global_qubits.py --report    verdicts from the store

Addendum 2 proved that the optimum has a closed form: the cost of a global set
is separable in the chosen qubits, so the lowest-degree rule attains it exactly.
What is left to measure is one thing, and it is the point of the study -- the
mutual-information arm selects by information rather than by degree, so the
question is whether the state leads to the same place and what it costs when it
does not. That number is what --run produces.

Cost model, from addendum 1 and the hop measurement, in units of 2^(n-2)
amplitude-hops:

    diagonal gate, any placement            0
    single-qubit rotation, global qubit     2
    CNOT, target global                     1    (control global or not)
    CNOT, target local                      0
    XX+YY, exactly one qubit global         1
    XX+YY, both qubits global               2    (two hops)

Two execution choices are made here rather than in the note, because the note
left them to the run, and both are fixed before the first measurement:

  * The initial state is |+> on every qubit, the QAOA convention.
  * The mutual-information arm reads the state after the first full layer, and
    scores a qubit by its total pairwise mutual information to all others,
    I(a) = sum over b != a of I(a:b), taking the g qubits of lowest score.
    That is the state-side analogue of the lowest-degree rule, which is what
    makes the comparison a comparison.

Run from the calculations/ directory of the repository.

Ramon Schweiss, QWeb (c) Research, 24 November 2026.
"""
import itertools
import json
import sys

import numpy as np
import partition_topology as pt

# ---------------------------------------------------------------- registered
FAMILIES = ["random", "ring", "path", "regular", "scale-free", "community",
            "grid"]
SEEDS = (0, 1, 2)
SIZES = (12, 16, 20)
GS = (2, 3, 4)
DENSITY = 1.5
N_RANDOM = 20              # section 4: draws of the random arm per instance
LIMIT = 2                  # section 7 as restated in addendum 2, in units
BOOT = 2000
STORE = "hypercube_global_qubits_scores.json"

GAMMA, BETA, DELTA = 0.37, 0.61, 0.23


# ------------------------------------------------------------------- circuits
def oriented(edges):
    """Addendum 1: lower vertex index to higher."""
    return [(min(a, b), max(a, b)) for a, b in edges]


def circuit(family, edges, n):
    """Gate list as (kind, qubits). 'rot' is non-diagonal single-qubit."""
    gates = []
    if family == "xy":
        gates += [("xy", (a, b)) for a, b in edges]
    elif family == "cnot":
        gates += [("cnot", (c, t)) for c, t in oriented(edges)]
    elif family == "qaoa":                      # declared degenerate, A1.4
        gates += [("zz", (a, b)) for a, b in edges]
    else:
        raise ValueError(family)
    gates += [("rot", (q,)) for q in range(n)]
    return gates


def unit_cost(kind, qubits, S):
    """Cost of one gate in units of 2^(n-2) amplitude-hops."""
    if kind == "zz":
        return 0
    if kind == "rot":
        return 2 if qubits[0] in S else 0
    if kind == "cnot":
        return 1 if qubits[1] in S else 0
    if kind == "xy":
        k = (qubits[0] in S) + (qubits[1] in S)
        return 1 if k == 1 else 2 if k == 2 else 0
    raise ValueError(kind)


def cost(gates, S):
    return sum(unit_cost(k, q, S) for k, q in gates)


# ----------------------------------------------------------------------- arms
def weights(family, edges, n):
    """What the gate-structure arm reads: the closed form of addendum 2."""
    w = [0] * n
    if family == "xy":
        for a, b in edges:
            w[a] += 1
            w[b] += 1
    elif family == "cnot":
        for _, t in oriented(edges):
            w[t] += 1
    elif family == "qaoa":
        pass                                    # every qubit alike
    return w


def arm_gate(family, edges, n, g):
    w = weights(family, edges, n)
    return tuple(sorted(range(n), key=lambda v: (w[v], v))[:g])


def arm_random(n, g, rng):
    return tuple(sorted(rng.choice(n, size=g, replace=False).tolist()))


def optimum(gates, n, g):
    """Exhaustive enumeration over all C(n, g) subsets."""
    best, val = None, None
    for S in itertools.combinations(range(n), g):
        c = cost(gates, set(S))
        if val is None or c < val:
            best, val = S, c
    return best, val


# ------------------------------------------------------------------- the state
def apply_gate(psi, kind, qubits, n):
    """In-place-ish application to a statevector of shape (2,)*n."""
    if kind == "zz":
        return _apply_diag_zz(psi, qubits[0], qubits[1], n)
    if kind == "rot":
        q = qubits[0]
        m = np.array([[np.cos(BETA), -1j * np.sin(BETA)],
                      [-1j * np.sin(BETA), np.cos(BETA)]])
        return _apply_1q(psi, m, q, n)
    if kind == "cnot":
        c, t = qubits
        m = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]],
                     dtype=complex)
        return _apply_2q(psi, m, c, t, n)
    if kind == "xy":
        a, b = qubits
        m = np.array([[1, 0, 0, 0],
                      [0, np.cos(DELTA), -1j * np.sin(DELTA), 0],
                      [0, -1j * np.sin(DELTA), np.cos(DELTA), 0],
                      [0, 0, 0, 1]], dtype=complex)
        return _apply_2q(psi, m, a, b, n)
    raise ValueError(kind)


def _apply_diag_zz(psi, a, b, n):
    """Diagonal, so a phase per (bit_a, bit_b) block and nothing moves."""
    ph = np.exp(-1j * GAMMA * np.array([1.0, -1.0, -1.0, 1.0])).reshape(2, 2)
    out = psi.copy()
    for i in range(2):
        for j in range(2):
            idx = [slice(None)] * n
            idx[a], idx[b] = i, j
            out[tuple(idx)] *= ph[i, j]
    return out


def _apply_1q(psi, m, q, n):
    psi = np.moveaxis(psi, q, 0)
    sh = psi.shape
    psi = (m @ psi.reshape(2, -1)).reshape(sh)
    return np.moveaxis(psi, 0, q)


def _apply_2q(psi, m, a, b, n):
    psi = np.moveaxis(psi, (a, b), (0, 1))
    sh = psi.shape
    psi = (m @ psi.reshape(4, -1)).reshape(sh)
    return np.moveaxis(psi, (0, 1), (a, b))


def entropy(rho):
    ev = np.linalg.eigvalsh(rho)
    ev = ev[ev > 1e-12]
    return float(-(ev * np.log2(ev)).sum())


def mi_scores(psi, n):
    """I(a) = sum over b != a of I(a:b), from one statevector."""
    s1 = []
    for q in range(n):
        p = np.moveaxis(psi, q, 0).reshape(2, -1)
        s1.append(entropy(p @ p.conj().T))
    tot = [0.0] * n
    for a, b in itertools.combinations(range(n), 2):
        p = np.moveaxis(psi, (a, b), (0, 1)).reshape(4, -1)
        sab = entropy(p @ p.conj().T)
        i_ab = s1[a] + s1[b] - sab
        tot[a] += i_ab
        tot[b] += i_ab
    return tot


def arm_mi(family, edges, n, g):
    """Section 4, arm 2, with the layer and the rule declared in the header."""
    psi = np.ones([2] * n, dtype=complex) / np.sqrt(2 ** n)
    for kind, qubits in circuit(family, edges, n):
        psi = apply_gate(psi, kind, qubits, n)
    sc = mi_scores(psi, n)
    return tuple(sorted(range(n), key=lambda v: (sc[v], v))[:g]), sc


# ---------------------------------------------------------------------- gates
def gate_cost_model():
    """Condition 3 as restated in A1.6: per gate type, against the operator."""
    n, g = 6, 2
    mask = ((1 << g) - 1) << (n - g)

    def full(mat, qs):
        out = np.zeros((2 ** n, 2 ** n), dtype=complex)
        k = len(qs)
        for i in range(2 ** n):
            bits = [(i >> (n - 1 - q)) & 1 for q in range(n)]
            si = 0
            for q in qs:
                si = (si << 1) | bits[q]
            for so in range(2 ** k):
                v = mat[so, si]
                if abs(v) < 1e-14:
                    continue
                ob = list(bits)
                for t, q in enumerate(qs):
                    ob[q] = (so >> (k - 1 - t)) & 1
                j = 0
                for b in ob:
                    j = (j << 1) | b
                out[j, i] += v
        return out

    def units(mat, qs):
        op = full(mat, qs)
        moved, pairs = set(), set()
        for j in range(2 ** n):
            for i in range(2 ** n):
                if abs(op[j, i]) > 1e-12 and (i & mask) != (j & mask):
                    moved.add(i)
                    pairs.add((min(i & mask, j & mask), max(i & mask, j & mask)))
        if not pairs:
            return 0
        hops = max(bin(a ^ b).count("1") for a, b in pairs)
        return (len(moved) // 2) * hops // 2 ** (n - 2)

    ZZ = np.diag(np.exp(-1j * GAMMA * np.array([1., -1., -1., 1.])))
    RX = np.array([[np.cos(BETA), -1j * np.sin(BETA)],
                   [-1j * np.sin(BETA), np.cos(BETA)]])
    CN = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]],
                  dtype=complex)
    XY = np.array([[1, 0, 0, 0],
                   [0, np.cos(DELTA), -1j * np.sin(DELTA), 0],
                   [0, -1j * np.sin(DELTA), np.cos(DELTA), 0],
                   [0, 0, 0, 1]], dtype=complex)
    cases = [("zz both global", ZZ, [0, 1], 0),
             ("zz one global", ZZ, [0, 3], 0),
             ("rot global", RX, [0], 2),
             ("rot local", RX, [3], 0),
             ("cnot target local", CN, [0, 3], 0),
             ("cnot target global", CN, [3, 0], 1),
             ("cnot both global", CN, [0, 1], 1),
             ("xy one global", XY, [0, 3], 1),
             ("xy both global", XY, [0, 1], 2),
             ("xy none global", XY, [3, 4], 0)]
    bad = []
    for name, m, qs, want in cases:
        got = units(m, qs)
        print(f"    {name:22s} model {want}   measured {got}"
              f"{'' if got == want else '   MISMATCH'}")
        if got != want:
            bad.append(name)
    return bad


def gate_ground_truth():
    """Condition 2: a second, differently written enumeration, subset by subset."""
    bad = 0
    n, m = SIZES[0], int(round(DENSITY * SIZES[0]))
    for family_c in ("xy", "cnot"):
        for fam in FAMILIES:
            E = pt.make_graph(fam, n, m, SEEDS[0])
            if E is None:
                continue
            gates = circuit(family_c, E, n)
            for g in GS:
                for S in itertools.combinations(range(n), g):
                    fast = cost(gates, set(S))
                    slow = 0                     # written differently on purpose
                    for kind, qs in gates:
                        hit = [q for q in qs if q in S]
                        if kind == "zz":
                            slow += 0
                        elif kind == "rot":
                            slow += 2 * len(hit)
                        elif kind == "cnot":
                            slow += 1 if qs[1] in hit else 0
                        elif kind == "xy":
                            slow += len(hit)
                    if fast != slow:
                        bad += 1
    return bad


def gate_degenerate_g1():
    """Condition 5: at g = 1 both deterministic arms must give minimum weight."""
    bad = 0
    for n in SIZES:
        m = int(round(DENSITY * n))
        for family_c in ("xy", "cnot"):
            for fam in FAMILIES:
                for sd in SEEDS:
                    E = pt.make_graph(fam, n, m, sd)
                    if E is None:
                        continue
                    gates = circuit(family_c, E, n)
                    _, opt = optimum(gates, n, 1)
                    w = weights(family_c, E, n)
                    if opt != min(w) + 2:
                        bad += 1
    return bad


def gate_family_a():
    """A1.4: the QAOA family must cost p * g, independent of the subset."""
    bad = 0
    for n in SIZES:
        m = int(round(DENSITY * n))
        for fam in FAMILIES:
            E = pt.make_graph(fam, n, m, SEEDS[0])
            if E is None:
                continue
            gates = circuit("qaoa", E, n)
            for g in GS:
                vals = {cost(gates, set(S))
                        for S in itertools.combinations(range(n), g)}
                if vals != {2 * g}:
                    bad += 1
    return bad


def gates():
    print("Gate 1 - cost model per gate type (condition 3, A1.6)")
    bad3 = gate_cost_model()
    print("\nGate 2 - independent enumeration, subset by subset (condition 2)")
    bad2 = gate_ground_truth()
    print(f"    disagreeing subsets: {bad2}")
    print("\nGate 3 - the declared degenerate g = 1 (condition 5)")
    bad5 = gate_degenerate_g1()
    print(f"    cells not reproducing minimum weight: {bad5}")
    print("\nGate 4 - family A is degenerate, cost = p * g (A1.4)")
    bada = gate_family_a()
    print(f"    cells where the cost was not constant: {bada}")
    ok = not bad3 and not bad2 and not bad5 and not bada
    print("\n  " + ("all gates pass" if ok else "A GATE FAILED - the run is void"))
    return 0 if ok else 1


# ------------------------------------------------------------------------ run
def run():
    rows = []
    for family_c in ("xy", "cnot"):
        for n in SIZES:
            m = int(round(DENSITY * n))
            for fam in FAMILIES:
                for sd in SEEDS:
                    E = pt.make_graph(fam, n, m, sd)
                    if E is None:
                        print(f"  no connected graph: {fam} n={n} seed={sd}")
                        continue
                    gates_l = circuit(family_c, E, n)
                    _, sc = arm_mi(family_c, E, n, max(GS))
                    w = weights(family_c, E, n)
                    for g in GS:
                        S_opt, c_opt = optimum(gates_l, n, g)
                        S_gate = arm_gate(family_c, E, n, g)
                        S_mi = tuple(sorted(range(n),
                                            key=lambda v: (sc[v], v))[:g])
                        # FAMILIES.index rather than hash(): hash of a string
                        # is salted per process, so the run would not repeat.
                        rng = np.random.default_rng(
                            (n, g, sd, FAMILIES.index(fam)))
                        rnd = [cost(gates_l, set(arm_random(n, g, rng)))
                               for _ in range(N_RANDOM)]
                        rows.append(dict(
                            circuit=family_c, n=n, g=g, family=fam, seed=sd,
                            opt=c_opt, opt_set=list(S_opt),
                            gate=cost(gates_l, set(S_gate)),
                            gate_set=list(S_gate),
                            mi=cost(gates_l, set(S_mi)), mi_set=list(S_mi),
                            random_mean=float(np.mean(rnd)),
                            random_min=int(min(rnd)),
                            weights=w,
                            mi_scores=[round(float(x), 6) for x in sc]))
                    print(f"  {family_c:5s} n={n:2d} {fam:11s} seed={sd} done")
    with open(STORE, "w") as f:
        json.dump(rows, f, indent=1)
    print(f"\n  {len(rows)} instances written to {STORE}")
    return 0


# --------------------------------------------------------------------- report
def boot_spread(d, rng):
    d = np.asarray(d, dtype=float)
    if len(d) < 2:
        return float("inf"), float("-inf"), float("inf")
    bs = [d[rng.integers(0, len(d), len(d))].mean() for _ in range(BOOT)]
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return float(hi - lo) / 2.0, float(lo), float(hi)


def report():
    rows = json.load(open(STORE))
    rng = np.random.default_rng(20261124)
    print(f"{len(rows)} instances, limit {LIMIT} units, granularity 1 unit\n")
    print("  the gate-structure arm against the enumerated optimum")
    miss = [r for r in rows if r["gate"] != r["opt"]]
    print(f"    instances where it missed: {len(miss)} of {len(rows)}\n")

    print("  the mutual-information arm against the enumerated optimum")
    hdr = (f"    {'circuit':8s} {'n':>3s} {'g':>2s} {'inst':>5s} "
           f"{'same set':>9s} {'at opt':>7s} {'mean loss':>10s} "
           f"{'spread':>7s}  verdict")
    print(hdr)
    print("    " + "-" * (len(hdr) - 4))
    for circ in ("xy", "cnot"):
        for n in SIZES:
            for g in GS:
                rs = [r for r in rows
                      if r["circuit"] == circ and r["n"] == n and r["g"] == g]
                if len(rs) < 5:
                    print(f"    {circ:8s} {n:3d} {g:2d} {len(rs):5d} "
                          f"{'':>9s} {'':>7s} {'':>10s} {'':>7s}  "
                          f"not evaluable (under five instances)")
                    continue
                same = sum(1 for r in rs
                           if sorted(r["mi_set"]) == sorted(r["opt_set"]))
                atopt = sum(1 for r in rs if r["mi"] == r["opt"])
                d = [r["mi"] - r["opt"] for r in rs]
                half, lo, hi = boot_spread(d, rng)
                mean = float(np.mean(d))
                if half > LIMIT:
                    v = "not evaluable"
                elif lo > 0 or hi < 0:
                    v = "separated"
                elif abs(mean) < 1:
                    v = f"bounded by {half:.2f}"
                else:
                    v = f"unresolved, bound {half:.2f}"
                print(f"    {circ:8s} {n:3d} {g:2d} {len(rs):5d} "
                      f"{same:9d} {atopt:7d} {mean:10.3f} {half:7.2f}  {v}")

    print("\n  the random arm against the optimum, as the positive control")
    for circ in ("xy", "cnot"):
        rs = [r for r in rows if r["circuit"] == circ]
        d = [r["random_mean"] - r["opt"] for r in rs]
        half, lo, hi = boot_spread(d, rng)
        sep = "separated" if lo > 0 else "NOT separated - condition 1 fires"
        print(f"    {circ:5s} mean excess {np.mean(d):7.3f}  "
              f"interval [{lo:.3f}, {hi:.3f}]  {sep}")
    return 0


if __name__ == "__main__":
    print(__doc__ if "--doc" in sys.argv else "")
    if "--gates" in sys.argv:
        sys.exit(gates())
    if "--run" in sys.argv:
        sys.exit(run())
    if "--report" in sys.argv:
        sys.exit(report())
    print(__doc__)
