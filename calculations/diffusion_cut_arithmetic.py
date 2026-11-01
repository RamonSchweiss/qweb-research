"""
Is the diffusion operator really the workload that cannot be partitioned?

Belongs to designs/design_diffusion_cut_cost_EN.md, sections 3 and 4, and to
the article "What the Operator Hides From the Partitioner". This script is the
arithmetic that refuted the design note's own first hypothesis, which was that
routing an amplification iteration makes every iteration cross every balanced
cut at a cost that does not fall as the partitioner improves. It is
deterministic - no seeds, no selection, no stopping rule - and it needed no
registration for that reason.

Findings : (0) the construction is what it claims to be. The circuit equals
               2|s><s| - I to within 1e-16, up to a global phase of -1 that the
               multi-controlled Z contributes and that amplitude amplification
               cannot observe. The ancillae return to |0>, leakage below 1e-16.
               Nothing below means anything without this check;
           (1) with the multi-controlled Z built as a V-chain over n-2
               ancillae, the interaction graph is NOT complete, and its minimum
               balanced cut is eight gates at every size from n=4 to n=12. The
               V-chain is a ladder; cutting a ladder in the middle severs one
               triangle, and that is the whole cost. The crossing fraction
               therefore falls as 1/n, where a complete graph would hold near
               P/(2(P-1)), about 0.53 at these sizes;
           (2) synthesised WITHOUT ancillae, the same operator does have a
               complete interaction graph at every size, and its crossing
               fraction sits on that floor. The first hypothesis is correct for
               this decomposition and false for the one in use. Gate count is
               why nobody uses it: roughly 3n^2 against the V-chain's 12n, a
               factor of 3.7 at n=12. Not exponential - an earlier guess that
               it would be was wrong;
           (3) therefore an exchange rate. At n=12, ten ancillae turn 240
               crossings into eight, about 23 crossings saved per ancilla. The
               ancillae are spent to reduce gate count and buy the cheap cut as
               a side effect, so the field's choice of decomposition already
               encodes the answer to the question the hypothesis asked;
           (4) and a ledger entry. A nonlocal CX costs one ebit and two
               classical bits, so a distributed iteration costs eight ebits
               whatever the register size, and a full run eight times the
               iteration count - 1,608 ebits at n=16. Bounded, and computable
               before the run.

Reading  : the hypothesis read the operator and not the circuit. D is a
           reflection in which every qubit participates; the routed cost is a
           property of a decomposition of D, and every decomposition in use is
           a chain. The chain does the partitioner's work before the
           partitioner is asked. This is the same distinction as in "What the
           Computation Knows About Its Own Organisation", applied here to one of
           my own hypotheses rather than to someone else's.

Caveats  : one operator, two decompositions, and the second is whatever Qiskit
           synthesises today rather than a canonical ancilla-free construction.
           Cuts are minima over balanced bipartitions under FREE placement of
           the logical qubits, so they are what a perfect partitioner would
           find and not what a compiler achieves - that is the separate
           measurement in section 7 of the design note. The oracle is assumed
           and not counted, exactly as the amplification literature assumes it;
           if its own interaction graph were dense it would dominate the
           iteration and these numbers would be a correct measurement of a
           minor term. The ebit ledger prices a nonlocal CX at one ebit, which
           is the standard protocol and not the only one.

Needs    : numpy, qiskit, and partition_topology.py from calculations/.
Runtime  : about ten seconds, most of it enumerating bipartitions at P=22.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
for cand in (HERE, os.path.join(HERE, "..", "calculations")):
    if os.path.isfile(os.path.join(cand, "partition_topology.py")):
        sys.path.insert(0, os.path.abspath(cand))
        break
import partition_topology as pt                                   # noqa: E402

try:                                                              # noqa: E402
    import qiskit
    from qiskit import QuantumCircuit, transpile
    from qiskit.quantum_info import Operator
except ImportError:                       # same convention as the memQ
    qiskit = None                         # cross-check in gate_vs_state_partition.py

V_CHAIN_SIZES = (4, 6, 8, 10, 12)         # P = 2n-2, so 6 to 22
NO_ANC_SIZES = (4, 6, 8, 10, 12)          # P = n
LEDGER_SIZES = (16, 20, 30)
VERIFY_SIZES = (3, 4, 5, 6)               # small enough for a dense unitary


# ------------------------------------------------------- the declared circuit

def toffoli(qc, a, b, c):
    """CCX written out as six CX plus single-qubit gates.

    Written out rather than left as a three-qubit gate so that the interaction
    graph below is the graph of the circuit that would actually be routed, and
    not of a placeholder the transpiler would later expand however it liked.
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


def mcz_vchain(qc, data, anc):
    """Phase flip on |1...1> over `data`, through a V-chain over `anc`.

    anc[0] holds data[0] AND data[1]; anc[i] holds anc[i-1] AND data[i+1]. The
    ladder is run forward, the controlled phase applied, and the ladder undone,
    which is why the ancillae come back empty and why there are 2(n-2)
    Toffolis.
    """
    n = len(data)
    if len(anc) != n - 2:
        raise ValueError(f"V-chain over {n} qubits needs {n - 2} ancillae")
    toffoli(qc, data[0], data[1], anc[0])
    for i in range(1, n - 2):
        toffoli(qc, anc[i - 1], data[i + 1], anc[i])
    qc.cz(anc[n - 3], data[n - 1])
    for i in range(n - 3, 0, -1):
        toffoli(qc, anc[i - 1], data[i + 1], anc[i])
    toffoli(qc, data[0], data[1], anc[0])


def diffusion_vchain(n):
    """D = 2|s><s| - I over n data qubits, on 2n-2 physical qubits."""
    data, anc = list(range(n)), list(range(n, 2 * n - 2))
    qc = QuantumCircuit(2 * n - 2)
    qc.h(data); qc.x(data)
    mcz_vchain(qc, data, anc)
    qc.x(data); qc.h(data)
    return qc


def diffusion_noancilla(n):
    """The same operator with the multi-controlled Z synthesised on n qubits."""
    qc = QuantumCircuit(n)
    qc.h(range(n)); qc.x(range(n))
    qc.h(n - 1)
    qc.mcx(list(range(n - 1)), n - 1)
    qc.h(n - 1)
    qc.x(range(n)); qc.h(range(n))
    out = transpile(qc, basis_gates=["u", "cx"], optimization_level=1)
    if out.num_qubits != n:
        raise RuntimeError(f"synthesis used {out.num_qubits} qubits, not {n}")
    return out


# --------------------------------------------------------------- the two tests

def verify(n):
    """Does the circuit equal the operator it is named after?

    The ancillae are the high-order qubits, so the top-left 2^n block of the
    unitary is the action on the data when the ancillae start and end in |0>.
    A global phase is allowed: amplitude amplification cannot see one.
    """
    qc = diffusion_vchain(n)
    U = Operator(qc).data
    d = 2 ** n
    s = np.ones(d) / 2 ** (n / 2)
    want = 2 * np.outer(s, s) - np.eye(d)
    blk = U[:d, :d]
    phase = blk[0, 0] / want[0, 0]
    return (float(np.abs(blk / phase - want).max()),
            float(np.abs(U[:d, d:]).max()),
            complex(phase))


def graph(qc, P):
    """Interaction graph of the two-qubit gates, and its minimum balanced cut.

    The cut is a minimum over ALL balanced bipartitions of the P qubits, under
    free placement. It is what a perfect partitioner would find, which is the
    right null for a claim about partitioner quality.
    """
    pairs = [tuple(sorted((qc.find_bit(ins.qubits[0]).index,
                           qc.find_bit(ins.qubits[1]).index)))
             for ins in qc.data if len(ins.qubits) == 2]
    W = np.zeros((P, P))
    for a, b in pairs:
        W[a, b] += 1.0
        W[b, a] += 1.0
    lo = float(pt.cut_costs(W, pt.partitions(P)).min())
    return len(pairs), len(set(pairs)), lo, lo / len(pairs)


# --------------------------------------------------------------------- the run

def rule(txt):
    print(f"\n{txt}\n" + "-" * 78)


def table(rows, header):
    print(header)
    for r in rows:
        print(r)


def main():
    print(__doc__)
    if qiskit is None:
        print("qiskit is not installed; nothing to compute.")
        return

    rule("0 - The construction is what it claims to be")
    print("  Nothing below means anything if the circuit is not the operator.")
    print("  A global phase is allowed because amplitude amplification cannot")
    print("  observe one; the -1 comes from the multi-controlled Z.\n")
    print("     n   max |U - D|   ancilla leak   global phase")
    for n in VERIFY_SIZES:
        err, leak, ph = verify(n)
        print(f"   {n:3d}      {err:.1e}        {leak:.1e}   "
              f"{ph.real:+.3f}{ph.imag:+.3f}i")

    rule("1 - V-chain over n-2 ancillae: the decomposition in use")
    print("  Cut is the minimum over all balanced bipartitions of the P")
    print("  physical qubits. 'complete' asks whether every pair of qubits")
    print("  appears in some two-qubit gate.\n")
    print("     n    P   2q gates   distinct pairs  complete   min cut   fraction")
    v = {}
    for n in V_CHAIN_SIZES:
        P = 2 * n - 2
        g, d, lo, fr = graph(diffusion_vchain(n), P)
        v[n] = (g, lo, fr)
        full = P * (P - 1) // 2
        print(f"   {n:3d}  {P:3d}   {g:8d}   {d:6d} / {full:<5d} "
              f"{'yes' if d == full else 'no':>8}   {lo:7.0f}   {fr:8.3f}")
    print("\n  The cut is eight gates at every size. The V-chain is a ladder,")
    print("  and cutting a ladder in the middle severs one triangle. A complete")
    print("  interaction graph would instead hold near P/(2(P-1)):")
    print("   " + "   ".join(f"P={2*n-2}: {(2*n-2)/(2*(2*n-3)):.3f}"
                             for n in V_CHAIN_SIZES))

    rule("2 - No ancillae, same operator: where the hypothesis holds")
    print("  This is the one permitted departure from the declared")
    print("  decomposition, reported separately for that reason.\n")
    print("     n    P   2q gates   distinct pairs  complete   min cut   fraction")
    a = {}
    for n in NO_ANC_SIZES:
        try:
            qc = diffusion_noancilla(n)
        except RuntimeError as e:
            print(f"   {n:3d}   -- {e}")
            continue
        g, d, lo, fr = graph(qc, n)
        a[n] = (g, lo, fr)
        full = n * (n - 1) // 2
        print(f"   {n:3d}  {n:3d}   {g:8d}   {d:6d} / {full:<5d} "
              f"{'yes' if d == full else 'no':>8}   {lo:7.0f}   {fr:8.3f}")
    print("\n  Complete at every size, and the crossing fraction sits on the")
    print("  floor. The hypothesis was right about this decomposition and")
    print("  wrong about the one in use. Gate count is why it is not used:")
    print("     n    V-chain   no ancillae   ratio")
    for n in sorted(set(v) & set(a)):
        print(f"   {n:3d}   {v[n][0]:8d}   {a[n][0]:11d}   {a[n][0]/v[n][0]:5.2f}")

    rule("3 - The exchange rate the two tables imply")
    for n in sorted(set(v) & set(a)):
        saved = a[n][1] - v[n][1]
        print(f"   n={n:2d}:  {n-2:2d} ancillae turn {a[n][1]:4.0f} crossings "
              f"into {v[n][1]:2.0f}  --  {saved/(n-2):5.1f} per ancilla")
    print("\n  The smallest size is degenerate and is left in the table rather")
    print("  than dropped: at n=4 the no-ancilla circuit is smaller than the")
    print("  V-chain and both cuts are eight, so nothing is bought and the rate")
    print("  is zero. Six physical qubits have no interior to keep traffic in.")
    print("\n  Above it, the ancillae are spent to reduce gate count and the")
    print("  cheap cut comes with them, unasked for. That is why the field's")
    print("  choice of decomposition already answers the hypothesis's question.")

    rule("4 - The ledger entry, at one ebit per nonlocal CX")
    print("  Eight crossings per iteration, independent of register size. The")
    print("  oracle is not counted - see the caveats.\n")
    print("        n              N   iterations   ebits per run")
    for n in LEDGER_SIZES:
        N = 2 ** n
        it = int(np.floor(np.pi / 4 * np.sqrt(N)))
        print(f"      {n:3d}  {N:13,d}   {it:10,d}   {8*it:13,d}")
    print("\n  Bounded, and computable before the run. It grows with the")
    print("  algorithm's own iteration count and not with the register.")

    print("\n" + "=" * 78)
    print("  What this does not settle: whether a compiler realises the cheap")
    print("  cut. These are minima under free placement. The routed question is")
    print("  section 7 of the design note and a separate script.")


if __name__ == "__main__":
    main()
