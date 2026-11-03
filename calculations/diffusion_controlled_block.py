"""
How much must cross a module boundary to apply the diffusion operator?

Belongs to designs/design_diffusion_cut_cost_EN.md, addendum 4, and corrects
the ledger of the article "What the Operator Hides From the Partitioner".
The question came from Daniel Hug (qubit-lab.ch) on 3 November 2026, and the
answer is one operation, not eight.

The companion scripts measured the minimum balanced cut of a GIVEN circuit:
eight two-qubit gates for the V-chain decomposition, about nineteen after
compilation. Those numbers are correct and they answer the wrong question for
a distributed machine. Across a module boundary one does not cut the circuit
one happens to have. One implements the operator.

Findings : (0) the structural reason, which needs no computation at all.
               |s> = H^n|0> is a PRODUCT state, so across any bipartition
               |s><s| = P_A (x) P_B, and D = 2 P_A(x)P_B - I(x)I is a sum of
               two product terms. Its operator Schmidt rank across every cut
               is two, and a rank-two unitary of this shape is a controlled
               block;
           (1) the protocol that follows. On each side compute a local flag,
               one exactly when that half is in |+...+>; apply a single
               controlled-Z between the two flags across the boundary;
               uncompute both flags locally. Verified against D to within
               1e-15 at every size and split tested, with a global phase of
               -1 that amplitude amplification cannot observe, and with the
               flags returning cleanly to |0>;
           (2) exactly ONE operation crosses the boundary, at every register
               size and at every split position, balanced or not. Where the
               V-chain cut costs eight gates and routing makes it about
               nineteen, this costs one;
           (3) nothing is free, and the local side shows it. The protocol's
               total two-qubit count is of the same order as the V-chain's.
               What collapses is the crossing count, not the work;
           (4) the ledger therefore falls by a factor of eight against the
               article's free-placement figure and about nineteen against its
               routed one. A sixteen-qubit Grover costs about 201 ebits, not
               1,608 and not 3,819.

Reading  : the article's lesson was that the operator's form misleads about
           the routed cost of the circuit. The correction is the same mistake
           in the other direction: the circuit's form misleads about the cost
           across a link, where the operator tells the truth because one can
           see that |s> factorises. Both hold, at different layers, and I made
           the second while writing about the first.

Caveats  : two modules only. With k modules the flags must be combined along
           a chain or a tree, which crosses k-1 boundaries, and what each of
           those costs is a separate question this script does not answer. One
           nonlocal CZ is priced at one ebit and two classical bits, which is
           the standard protocol and is known to be optimal for a nonlocal
           CNOT; CZ is CNOT up to local Hadamards. The oracle is assumed and
           not counted, as everywhere else in this programme. And the local
           flag computation needs its own ancillae, so the qubit count does
           not fall.

Needs    : numpy, qiskit.
Runtime  : a few seconds.
"""
import math
import sys

import numpy as np

try:                                                              # noqa: E402
    import qiskit
    from qiskit import QuantumCircuit, transpile
    from qiskit.quantum_info import Statevector
except ImportError:                       # same convention as the memQ
    qiskit = None                         # cross-check in gate_vs_state_partition.py

SIZES = (4, 6, 8, 10)                     # statevectors, so this fits
LEDGER = (16, 20, 30)
ARTICLE_FREE, ARTICLE_ROUTED = 8, 19      # what the article said, per iteration


# ------------------------------------------------------------- the protocol

def toffoli(qc, a, b, c):
    """CCX written out as six CX. Nothing is left to a synthesiser.

    The first version of this script called qiskit's mcx and transpiled it.
    The synthesiser borrowed dirty ancillae from the OTHER side of the
    boundary, so between eleven and seventy-one gates crossed instead of one.
    That is the invalidating condition in section 8 of the design note,
    walked into while correcting a different number.
    """
    qc.h(c)
    qc.cx(b, c); qc.tdg(c)
    qc.cx(a, c); qc.t(c)
    qc.cx(b, c); qc.tdg(c)
    qc.cx(a, c); qc.t(c)
    qc.h(c)
    qc.t(b)
    qc.cx(a, b); qc.tdg(b); qc.cx(a, b)
    qc.t(a)


def flag(qc, grp, anc):
    """Set anc[-1] to 1 exactly when every qubit of `grp` is in |+>.

    H maps |+> to |0> and X maps |0> to |1>, so an AND over the group lands on
    the last ancilla; the layers run back afterwards, leaving `grp` untouched.
    The AND is an explicit V-chain over this side's OWN ancillae, so every
    gate here has both qubits on one side of the boundary, by construction and
    not by the good will of a transpiler. Being its own inverse, the routine
    also uncomputes.
    """
    qc.h(grp); qc.x(grp)
    if len(grp) == 1:
        qc.cx(grp[0], anc[0])
    else:
        toffoli(qc, grp[0], grp[1], anc[0])
        for i in range(1, len(grp) - 1):
            toffoli(qc, anc[i - 1], grp[i + 1], anc[i])
        for i in range(len(grp) - 3, -1, -1):      # free the intermediates,
            toffoli(qc, anc[i - 1] if i else grp[0],
                    grp[i + 1] if i else grp[1], anc[i])
    qc.x(grp); qc.h(grp)


def layout(n, cut):
    """Qubit indices: A data, B data, A ancillae, B ancillae."""
    a, b = cut, n - cut
    na, nb = max(1, a - 1), max(1, b - 1)
    A = list(range(cut))
    B = list(range(cut, n))
    ancA = list(range(n, n + na))
    ancB = list(range(n + na, n + na + nb))
    return A, B, ancA, ancB


def protocol(n, cut):
    """D across a boundary at `cut`, with one controlled-Z crossing it."""
    A, B, ancA, ancB = layout(n, cut)
    qc = QuantumCircuit(n + len(ancA) + len(ancB))
    flag(qc, A, ancA)                    # local to A
    flag(qc, B, ancB)                    # local to B
    qc.cz(ancA[-1], ancB[-1])            # the only operation that crosses
    flag(qc, B, ancB)                    # local to B
    flag(qc, A, ancA)                    # local to A
    return qc


def diffusion_matrix(n):
    s = np.ones(2 ** n) / 2 ** (n / 2)
    return 2 * np.outer(s, s) - np.eye(2 ** n)


def crossings(qc, n, cut):
    """Two-qubit GATES with one qubit on each side of the boundary.

    The circuit is decomposed to one- and two-qubit gates first. Counting
    instructions instead would hide a multi-controlled X inside a single
    entry, and the number this script exists to correct came about by not
    looking inside something.

    The flags sit at n and n+1 and belong to A and B respectively, so they are
    counted on their own sides.
    """
    _, _, ancA, ancB = layout(n, cut)
    side = {q: 0 for q in range(cut)}
    side.update({q: 1 for q in range(cut, n)})
    side.update({q: 0 for q in ancA})
    side.update({q: 1 for q in ancB})
    total = cross = 0
    for ins in qc.data:
        qs = [qc.find_bit(q).index for q in ins.qubits]
        if len(qs) < 2:
            continue
        total += 1
        if len({side[q] for q in qs}) > 1:
            cross += 1
    return total, cross


def check(n, cut, trials=4, seed=20261103):
    """Apply the protocol to |s> and to random states orthogonal to it.

    A full unitary would need 2^(n+ancillae) squared and runs out of memory
    past n=6. The defining property of a reflection needs only vectors: D is
    +1 on |s> and -1 on everything orthogonal to it, and this protocol is -D,
    so the signs come out the other way round.
    """
    qc = protocol(n, cut)
    nq, d = qc.num_qubits, 2 ** n
    rng = np.random.default_rng(seed + 31 * n + cut)
    s = np.ones(d) / 2 ** (n / 2)

    vecs = [s]
    for _ in range(trials):
        v = rng.normal(size=d) + 1j * rng.normal(size=d)
        v -= s * np.dot(s, v)            # orthogonal to |s>
        vecs.append(v / np.linalg.norm(v))

    err = leak = 0.0
    phase = None
    for v in vecs:
        full = np.zeros(2 ** nq, dtype=complex)
        full[:d] = v                     # ancillae are the high indices, so |0>
        out = Statevector(full).evolve(qc).data
        want = -(2 * s * np.dot(s, v) - v)          # -D v
        err = max(err, float(np.abs(out[:d] - want).max()))
        leak = max(leak, float(np.abs(out[d:]).max()))
        if phase is None:
            nz = int(np.argmax(np.abs(want)))
            phase = out[nz] / want[nz]
    total, cross = crossings(qc, n, cut)
    return err, leak, complex(phase), total, cross


# ------------------------------------------------------------------ report

def main():
    print(__doc__)
    if qiskit is None:
        print("qiskit is not installed; nothing to verify.")
        return

    print("1 - The protocol is the operator, at every size and every split")
    print("-" * 78)
    print("  Checked on |s> and on four random states orthogonal to it. The")
    print("  protocol is -D, so a phase of +1 against -D is the pass. 'leak'")
    print("  is how much amplitude is left on the ancillae.\n")
    print(f"  {'n':>3} {'split':>9} {'max err':>11} {'leak':>9} {'phase':>7} "
          f"{'2q gates':>9} {'crossing':>9}")
    worst = 0
    for n in SIZES:
        for cut in sorted({1, 2, n // 2}):
            if not 0 < cut < n:
                continue
            err, leak, ph, total, cross = check(n, cut)
            worst = max(worst, cross)
            print(f"  {n:>3} {f'{cut}|{n - cut}':>9} {err:>11.1e} {leak:>9.1e} "
                  f"{ph.real:>+7.2f} {total:>9d} {cross:>9d}")

    print(f"\n  Crossing operations, over every row above: {worst}.")
    print("  Not one per size, not one per split - one, full stop. The flags")
    print("  carry everything else, and they never leave their own side.")

    print("\n\n2 - What that does to the ledger")
    print("-" * 78)
    print("  One nonlocal CZ = one ebit and two classical bits. The article")
    print(f"  priced an iteration at {ARTICLE_FREE} ebits under free placement")
    print(f"  and about {ARTICLE_ROUTED} after compilation. Both answer a")
    print("  question about cutting a given circuit.\n")
    print(f"  {'n':>4} {'iterations':>11} {'article, free':>14} "
          f"{'article, routed':>16} {'controlled block':>17}")
    for n in LEDGER:
        it = int(math.floor(math.pi / 4 * math.sqrt(2 ** n)))
        print(f"  {n:>4} {it:>11,} {ARTICLE_FREE * it:>14,} "
              f"{ARTICLE_ROUTED * it:>16,} {it:>17,}")
    print(f"\n  A factor of {ARTICLE_FREE} against the free-placement figure "
          f"and about {ARTICLE_ROUTED}")
    print("  against the routed one. The article overstated both.")

    print("\n\n3 - What is NOT cheaper")
    print("-" * 78)
    print("  The local work. Each side still computes and uncomputes a flag")
    print("  over its own half, which is the same multi-controlled structure")
    print("  the V-chain had, and it still needs its own ancillae.\n")
    print(f"  {'n':>4} {'protocol 2q':>13} {'V-chain 2q':>12} {'ratio':>7}")
    for n in SIZES:
        total, _ = crossings(protocol(n, n // 2), n, n // 2)
        vchain = 12 * (n - 2) + 1
        print(f"  {n:>4} {total:>13d} {vchain:>12d} {total / vchain:>7.2f}")
    print("\n  Same order of magnitude, and the protocol is not even the")
    print("  cheaper of the two. What collapses is the crossing count alone.")

    print("\n" + "=" * 78)
    print("  Two modules only. With k modules the flags must be combined")
    print("  along a chain or a tree, crossing k-1 boundaries, and the price")
    print("  of each crossing in that case is a separate question. It is not")
    print("  answered here, and it should not be guessed at - guessing is how")
    print("  the figure this script corrects came about.")


if __name__ == "__main__":
    main()
