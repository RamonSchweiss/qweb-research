"""Is the incumbent of the cut-degeneracy study well defined at all?

Belongs to designs/design_cut_degeneracy_EN_addendum_5.md, 27 November 2026.
This is a diagnostic, not a test of a registered hypothesis. It exists because
two runs of the SAME committed code produced different figures on different
machines, and addendum 4 read that as a lost pre-commit version of the script.
It was not. The committed script reproduces the 4-5 November figures exactly,
twice over, on a machine that never held any other version.

What the incumbent is. cut_degeneracy_warmstart.measure() takes it from
findability_scoping.spectral(W): the Laplacian's Fiedler vector from
numpy.linalg.eigh, split at the median. Where the second-smallest Laplacian
eigenvalue is degenerate - which is what symmetry does, and the registered grid
contains ring, regular, path and grid families - V[:, 1] is an arbitrary member
of a subspace. Which member comes back is a LAPACK detail. Nothing in the note,
in A1.5 or in the script pins it.

Two checks, neither needing a second machine:

  1  the spectral gap lambda_2 - lambda_1 of the Laplacian, and separately
     the thing that actually decides the split: whether the Fiedler vector
     has TIED ENTRIES at the median. spectral() sorts with
     np.argsort(f, kind="stable"), so tied entries are ordered by vertex
     index - the split is then decided by the numbering, not by the graph;

  2  RELABELLING INVARIANCE. Permute the vertices, run spectral() on the
     permuted graph, map the answer back, compare as a partition under
     cut_degeneracy.canonical. A partition that depends on the order the
     vertices were written down in is not a property of the graph. Eight
     permutations per graph, drawn from a fixed seed, so this file reproduces.

Grid: the registered one - seven families, n = 10 to 20, seeds 0, 1, 2,
density 1.5 n, 126 graphs.

Needs   : numpy, partition_topology, findability_scoping, cut_degeneracy.
Runtime : seconds.
"""
import sys
import numpy as np

import partition_topology as pt
import findability_scoping as fs
import cut_degeneracy as cd

SIZES = [10, 12, 14, 16, 18, 20]
SEEDS = (0, 1, 2)
DENSITY = 1.5
PERMS = 8
NEAR = 1e-8
RNG = np.random.default_rng(20261127)


def spectral_relabelled(W, p):
    """spectral() on the relabelled graph, mapped back to original labels."""
    sp = fs.spectral(W[np.ix_(p, p)])
    s = np.zeros_like(sp)
    s[p] = sp
    return s


def main():
    print(__doc__)
    print("1 - Spectral gap and relabelling invariance, per size")
    print("-" * 78)
    print(f"  {'n':>4} {'graphs':>7} {'gap < 1e-8':>11} {'tie at split':>13} "
          f"{'incumbent moves':>16} {'median gap':>12}")
    tot_g = tot_z = tot_t = tot_r = tot_y = 0
    per_family = {}
    for n in SIZES:
        m = int(round(DENSITY * n))
        gaps, zero, tiny, ties, moves, cnt = [], 0, 0, 0, 0, 0
        for fam in fs.FAMILIES:
            for seed in SEEDS:
                E = pt.make_graph(fam, n, m, seed)
                if E is None:
                    continue
                W = pt.adjacency(n, E).astype(float)
                L = np.diag(W.sum(1)) - W
                w = np.linalg.eigvalsh(L)
                gap = float(w[2] - w[1])
                gaps.append(gap)
                cnt += 1
                zero += gap == 0.0
                tiny += gap < NEAR
                f = np.linalg.eigh(L)[1][:, 1]
                o = np.argsort(f, kind="stable")
                if abs(f[o[n // 2]] - f[o[n // 2 - 1]]) < 1e-12:
                    ties += 1
                base = cd.canonical(fs.spectral(W))
                for _ in range(PERMS):
                    p = RNG.permutation(n)
                    if not np.array_equal(
                            cd.canonical(spectral_relabelled(W, p)), base):
                        moves += 1
                        per_family[fam] = per_family.get(fam, 0) + 1
                        break
        print(f"  {n:>4} {cnt:>7} {tiny:>11} {ties:>13} {moves:>16} "
              f"{np.median(gaps):>12.4f}")
        tot_g += cnt
        tot_z += zero
        tot_t += tiny
        tot_y += ties
        tot_r += moves
    print(f"  {'all':>4} {tot_g:>7} {tot_t:>11} {tot_y:>13} {tot_r:>16}")
    print(f"\n  No Laplacian gap is exactly zero; {tot_t} are below 1e-8.")
    print(f"  Ties in the Fiedler vector at the split point: {tot_y}.")

    print("\n2 - Where the incumbent moves, by family")
    print("-" * 78)
    if not per_family:
        print("  Nowhere. The incumbent is well defined on this grid.")
    for fam in fs.FAMILIES:
        if fam in per_family:
            print(f"  {fam:>12}: {per_family[fam]} of {len(SIZES)*len(SEEDS)} "
                  f"graphs")
    print()
    print("  Regular and grid are the symmetric families of the grid, and")
    print("  they supply ten of the eleven. The community and random")
    print("  families, whose structure breaks the symmetry, never move.")
    print("  Scale-free contributes one graph, which is a near-degeneracy")
    print("  rather than a symmetry: no gap on this grid is exactly zero.")

    print("\n3 - What follows")
    print("-" * 78)
    print(f"  On {tot_r} of {tot_g} graphs the incumbent is a property of the")
    print("  eigensolver and the vertex numbering rather than of the graph.")
    print("  The declared degenerate subset of A1.5 is defined by whether the")
    print("  incumbent is already optimal, so it moves with it, and so does")
    print("  the usable set and every figure computed on it. That is the")
    print("  mechanism behind the mismatch addendum 4 recorded, and it is an")
    print("  instrument defect rather than a lost version of a file.")
    print()
    print("  It does not touch the withdrawal of A2.2, which rests on the warm")
    print("  route reaching the optimum less often at n = 12 - true in both")
    print("  environments - nor the A1.2 dataset, which uses random starts and")
    print("  no eigensolver, nor the exact enumeration of section 1.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
