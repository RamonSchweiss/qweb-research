"""Which gates actually move amplitudes between hypercube nodes.

Evidence for addendum 1 to designs/design_hypercube_global_qubits_EN.md,
written before the first run of the study and before the measurement script
exists. Nothing here is a result of the study; it checks the cost model the
study is built on, which section 3 of the note asserted and did not verify.

Model. The amplitude vector of n qubits is distributed over 2^g nodes, and the
node address is the top g bits of the global index. A gate moves amplitudes
between nodes exactly when it has a non-zero matrix element between two indices
whose global bits differ.

Method. For each gate the full 2^n x 2^n operator is built and its non-zero
off-diagonal structure is inspected directly. No simulation, no sampling, no
approximation: the crossing count is read off the operator.

Ramon Schweiss, QWeb (c) Research, 23 November 2026.
"""
import numpy as np

N = 6
G = 2          # the top G qubits are global


def op_on(mat, qs, n):
    """The 2^n x 2^n operator of `mat` acting on qubits `qs`, identity else."""
    full = np.zeros((2 ** n, 2 ** n), dtype=complex)
    k = len(qs)
    for i in range(2 ** n):
        bits = [(i >> (n - 1 - q)) & 1 for q in range(n)]
        sub_in = 0
        for q in qs:
            sub_in = (sub_in << 1) | bits[q]
        for sub_out in range(2 ** k):
            v = mat[sub_out, sub_in]
            if abs(v) < 1e-14:
                continue
            ob = list(bits)
            for t, q in enumerate(qs):
                ob[q] = (sub_out >> (k - 1 - t)) & 1
            j = 0
            for b in ob:
                j = (j << 1) | b
            full[j, i] += v
    return full


def crossings(full, n, g):
    """Amplitudes that change node, and the distinct node pairs involved."""
    mask = ((1 << g) - 1) << (n - g)
    moved, pairs = set(), set()
    for j in range(2 ** n):
        for i in range(2 ** n):
            if abs(full[j, i]) > 1e-12 and (i & mask) != (j & mask):
                moved.add(i)
                pairs.add((min(i & mask, j & mask), max(i & mask, j & mask)))
    return len(moved), len(pairs)


gamma, beta, delta = 0.37, 0.61, 0.23
ZZ = np.diag(np.exp(-1j * gamma * np.array([1., -1., -1., 1.])))
RX = np.array([[np.cos(beta), -1j * np.sin(beta)],
               [-1j * np.sin(beta), np.cos(beta)]])
CNOT = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]],
                dtype=complex)
XY = np.array([[1, 0, 0, 0],
               [0, np.cos(delta), -1j * np.sin(delta), 0],
               [0, -1j * np.sin(delta), np.cos(delta), 0],
               [0, 0, 0, 1]], dtype=complex)

CASES = [
    ("ZZ(gamma)      both qubits global", ZZ, [0, 1]),
    ("ZZ(gamma)      one qubit global", ZZ, [0, 3]),
    ("ZZ(gamma)      no qubit global", ZZ, [3, 4]),
    ("RX(beta)       on a global qubit", RX, [0]),
    ("RX(beta)       on a local qubit", RX, [3]),
    ("CNOT           control global, target local", CNOT, [0, 3]),
    ("CNOT           control local, target global", CNOT, [3, 0]),
    ("CNOT           both global", CNOT, [0, 1]),
    ("XX+YY(delta)   both global", XY, [0, 1]),
    ("XX+YY(delta)   one global", XY, [0, 3]),
    ("XX+YY(delta)   none global", XY, [3, 4]),
]

print(__doc__)
print(f"n = {N} qubits, g = {G} global, {2 ** N} amplitudes, "
      f"{2 ** G} nodes of {2 ** (N - G)}")
print(f"  for reference: 2^(n-1) = {2 ** (N - 1)}, "
      f"2^(n-2) = {2 ** (N - 2)}\n")
print(f"{'gate and placement':46s} {'indices':>9s} {'one way':>9s} "
      f"{'node pairs':>11s}")
print("-" * 78)
for name, m, qs in CASES:
    moved, pairs = crossings(op_on(m, qs, N), N, G)
    print(f"{name:46s} {moved:9d} {moved // 2:9d} {pairs:11d}")
print("\n  'indices' counts amplitude slots with a crossing matrix element;")
print("  'one way' is the traffic in one direction, which is half of it and")
print("  the figure the design note calls the cost of a gate.")

print("""
What this says, and it is not what the note assumed.

  1. A diagonal gate never moves an amplitude, however many of its qubits are
     global. Each node multiplies its own slice in place, because it knows its
     own global bits. The whole QAOA cost layer is of this kind.

  2. A gate costs exactly when it acts NON-DIAGONALLY on a global qubit.
     Being global is not by itself expensive; being acted on is.

  3. CNOT is therefore asymmetric. With the control global and the target
     local nothing crosses a node boundary. With the target global it does.
     The object that decides the cost is not the interaction graph, which is
     undirected, but which qubits are written to.

  4. The amount is not one figure. A full single-qubit rotation on a global
     qubit moves 2^(n-1) amplitudes; CNOT with both qubits global moves
     2^(n-2), because only the half with control = 1 is touched.
""")
