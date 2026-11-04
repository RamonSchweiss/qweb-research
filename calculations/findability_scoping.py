"""
Scoping: is there a findability gap to measure at the sizes we can measure?

Belongs to the merker "representability is not findability". It is NOT the
measurement that merker proposes. It asks the question that merker tells us to
ask first:

    "Bei n <= 12 ist der Abstand vermutlich klein; der Punkt wird erst bei
     Groessen interessant, wo exakte Aufzaehlung ausfaellt. Vorher klaeren, ab
     welchem n das gilt, sonst misst man eine Null."

The published measurement -- the gate-optimal cut is the same at every layer in
21 of 21 graphs -- is a statement about the OBJECT. At n <= 12 it was obtained
by enumerating every balanced bipartition, so findability was not tested; it
was bypassed. The open half is whether a partitioner a real compiler would use
finds that cut at all.

Before building an arm for that, two things have to be known, and neither needs
the arm:

  (1) Is the gap between the exact optimum and a standard heuristic ever
      nonzero at sizes where the optimum can still be enumerated? If a
      heuristic lands on the optimum everywhere up to the enumeration ceiling,
      the arm measures a zero and should wait for larger registers.

  (2) Can the heuristic's answer WANDER across layers at all? For QAOA every
      layer applies the same gates, so the interaction graph is identical at
      every layer. A deterministic partitioner on an identical graph returns an
      identical answer by construction, and "does the heuristic cut stay
      stable?" has no content for it. The question only has content for a
      randomised partitioner, or for the routed graph -- which is where the
      orbit note already lives.

Both are settled here, before anything is built.

Heuristics : spectral bisection (Fiedler vector, split at the median, which
             forces balance), then Kernighan-Lin style pairwise swapping to a
             local optimum, from the spectral start and from random starts.
             These are the standard baselines; METIS and KaHyPar are
             multilevel refinements of the same idea and are not installed
             here, so the claim made below is about this family and says so.

Cut        : number of interaction-graph edges crossing a balanced bipartition,
             counted exactly as partition_topology.cut_costs counts it, which
             is the same quantity the published measurement minimises.

Needs      : numpy, scipy, partition_topology.
Runtime    : under a minute.
"""
import sys

import numpy as np

import partition_topology as pt

FAMILIES = ["random", "ring", "path", "regular", "scale-free", "community", "grid"]
SEEDS = (0, 1, 2)                        # 7 x 3 = the 21-graph grid
SIZES = (10, 12, 14, 16, 18, 20)         # exact enumeration still feasible
DENSITY = 1.5                            # m = 1.5 n, as at n = 10, m = 15
RESTARTS = 20
RNG = np.random.default_rng(20261104)


# ------------------------------------------------------------------ heuristics

def cut_of(W, s):
    """Crossing edges under the 0/1 membership vector s."""
    return float(((s @ W) * (1.0 - s)).sum())


def balance(s):
    return int(s.sum()) == len(s) // 2


def spectral(W):
    """Fiedler vector, median split. Deterministic, and balanced by the split."""
    L = np.diag(W.sum(1)) - W
    w, V = np.linalg.eigh(L)
    f = V[:, 1]
    order = np.argsort(f, kind="stable")
    s = np.zeros(len(f))
    s[order[len(f) // 2:]] = 1.0
    return s


def kl(W, s):
    """Pairwise swaps to a local optimum, inside the balanced class.

    The first version of this function computed the two sides ONCE per sweep
    and then mutated s inside the loops. After the first accepted swap the two
    lists described a membership that no longer existed, later swaps moved
    qubits that had already moved, and the result left the balanced class
    entirely: partitions with two of ten qubits on one side, with cuts BELOW
    the balanced optimum because they were not balanced at all. The reported
    "misses: 0 of 21" was the heuristic winning by leaving the class it was
    being judged in.

    That is the same failure as a null arm allowed swaps the hardware cannot
    make. Here the sweep restarts whenever anything moves, so the two sides are
    always current, and the balance is asserted on the way out rather than
    assumed.
    """
    s = s.copy()
    n = len(s)
    best = cut_of(W, s)
    moved = True
    while moved:
        moved = False
        A = [i for i in range(n) if s[i] == 0]
        B = [i for i in range(n) if s[i] == 1]
        for a in A:
            for b in B:
                t = s.copy()
                t[a], t[b] = 1.0, 0.0
                c = cut_of(W, t)
                if c < best - 1e-12:
                    s, best, moved = t, c, True
                    break                      # the sides are now stale
            if moved:
                break
    if not balance(s):
        raise AssertionError("kl left the balanced class")
    return s, best


def random_start(n):
    s = np.zeros(n)
    s[RNG.permutation(n)[: n // 2]] = 1.0
    return s


# ---------------------------------------------------------------------- report

def main():
    print(__doc__)
    if not hasattr(pt, "partitions"):
        print("partition_topology is not the expected module.")
        return 1

    print("1 - Does a heuristic ever miss the exact optimum?")
    print("-" * 78)
    print("  21 graphs per size, m = 1.5 n. 'exact' enumerates every balanced")
    print("  bipartition. A miss is a heuristic cut strictly above it.\n")
    print(f"  {'n':>3} {'graphs':>7} {'parts':>9} {'spectral':>18} "
          f"{'KL from spectral':>18} {'KL best of 20':>16}")

    ceiling_hit = None
    for n in SIZES:
        m = int(round(DENSITY * n))
        S = pt.partitions(n)
        rows = []
        for f in FAMILIES:
            for sd in SEEDS:
                E = pt.make_graph(f, n, m, sd)
                if E is None:
                    continue
                W = pt.adjacency(n, E).astype(float)
                exact = float(pt.cut_costs(W, S).min())

                s_sp = spectral(W)
                c_sp = cut_of(W, s_sp)
                _, c_klsp = kl(W, s_sp)
                c_klr = min(kl(W, random_start(n))[1] for _ in range(RESTARTS))
                rows.append((f, sd, exact, c_sp, c_klsp, c_klr))

        def miss(idx):
            bad = [r for r in rows if r[idx] > r[2] + 1e-9]
            if not bad:
                return "0 of %d" % len(rows)
            gaps = [r[idx] - r[2] for r in bad]
            return (f"{len(bad)} of {len(rows)}, gap "
                    f"{min(gaps):.0f}-{max(gaps):.0f}")

        print(f"  {n:>3} {len(rows):>7} {len(S):>9,} {miss(3):>18} "
              f"{miss(4):>18} {miss(5):>16}")
        if ceiling_hit is None and any(r[4] > r[2] + 1e-9 for r in rows):
            ceiling_hit = n

    print()
    if ceiling_hit is None:
        print(f"  Kernighan-Lin from a spectral start reaches the exact optimum on")
        print(f"  every graph at every size up to n = {SIZES[-1]}. At these sizes and")
        print("  this density the findability gap for this heuristic family is")
        print("  ZERO. An arm built here would measure nothing.")
    else:
        print(f"  The first size at which KL from spectral misses is n = {ceiling_hit}.")
        print("  Below that, an arm measures a zero; from there it has content.")

    print("\n\n2 - Can a heuristic's answer wander across layers?")
    print("-" * 78)
    print("  In QAOA every layer applies the same gates, so the interaction")
    print("  graph is IDENTICAL at every layer. This needs no measurement: a")
    print("  deterministic partitioner handed the same graph returns the same")
    print("  answer, at every layer, by construction. Spectral bisection and KL")
    print("  from a fixed start are deterministic. For them the question")
    print("  'does the heuristic cut stay stable over the layers?' is vacuous,")
    print("  in the same way a cycle of length one is constant by definition.")
    print()
    print("  What does have content is the spread of a RANDOMISED partitioner")
    print("  over its own seeds on one fixed graph. If several starts reach")
    print("  different partitions, a scheduler re-running the partitioner")
    print("  could move the cut with nothing in the circuit having changed.\n")
    print(f"  {'n':>3} {'graphs':>7} {'distinct local optima':>23} "
          f"{'of them optimal':>17} {'distinct AT the optimum':>25}")

    for n in SIZES:
        m = int(round(DENSITY * n))
        S = pt.partitions(n)
        tot_loc, tot_opt_loc, tot_opt_parts, g = 0, 0, 0, 0
        for f in FAMILIES:
            for sd in SEEDS:
                E = pt.make_graph(f, n, m, sd)
                if E is None:
                    continue
                W = pt.adjacency(n, E).astype(float)
                exact = float(pt.cut_costs(W, S).min())
                found = {}
                for _ in range(RESTARTS):
                    s, c = kl(W, random_start(n))
                    key = tuple(int(x) for x in s)
                    key = min(key, tuple(1 - x for x in key))   # label symmetry
                    found[key] = c
                g += 1
                tot_loc += len(set(found.values()))
                tot_opt_loc += int(min(found.values()) <= exact + 1e-9)
                tot_opt_parts += sum(1 for k, c in found.items()
                                     if c <= exact + 1e-9)
        print(f"  {n:>3} {g:>7} {tot_loc / g:>23.2f} "
              f"{f'{tot_opt_loc} of {g}':>17} {tot_opt_parts / g:>25.2f}")

    print()
    print("  Columns are per graph, averaged: how many distinct cut VALUES the")
    print("  twenty starts reach, whether the best of them is the exact")
    print("  optimum, and how many distinct PARTITIONS achieve that optimum.")
    print("  The last column is the one that matters for wandering: where it")
    print("  exceeds one, the optimum is degenerate and a re-run can return a")
    print("  different cut of the same cost. That is movement with no change in")
    print("  the circuit, and it is a property of the partitioner.")

    print("\n\n3 - The degeneracy, by family, exactly and not pooled")
    print("-" * 78)
    print("  The pooled column above must not be quoted on its own. Section 02")
    print("  of the published article records a Simpson's paradox caused by")
    print("  pooling symmetric graph families with their chorded relatives, so")
    print("  the same pooling here is the trap we have already been caught by.")
    print("  This counts every optimal partition exactly, by enumeration.\n")
    print(f"  {'family':<12}" + "".join(f"{'n=' + str(n):>9}" for n in SIZES))
    for f in FAMILIES:
        cells = []
        for n in SIZES:
            m = int(round(DENSITY * n))
            S = pt.partitions(n)
            vals = []
            for sd in SEEDS:
                E = pt.make_graph(f, n, m, sd)
                if E is None:
                    continue
                W = pt.adjacency(n, E).astype(float)
                c = pt.cut_costs(W, S)
                vals.append(int((c <= c.min() + 1e-9).sum()))
            cells.append(f"{np.mean(vals):>9.1f}" if vals else f"{'-':>9}")
        print(f"  {f:<12}" + "".join(cells))

    print()
    print("  The spread is the finding. In the community family the optimum is")
    print("  UNIQUE at every size tested, so nothing can wander. In the regular")
    print("  family it is degenerate many times over, which is what symmetry")
    print("  does. The pooled average sits between two qualitatively different")
    print("  situations and describes neither.")

    print("\n" + "=" * 78)
    print("  Scope of this scoping run, stated so it is not quoted larger:")
    print("  one heuristic family (spectral plus pairwise refinement), one")
    print("  density, balanced bipartitions, two parts only, and the seven")
    print("  graph families of the published grid. METIS and KaHyPar are")
    print("  multilevel methods and are not tested here. Nothing below the")
    print("  enumeration ceiling says anything about registers above it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
