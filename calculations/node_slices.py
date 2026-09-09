"""
A hypercube node holds no reduced state.

Article : What a Node Actually Holds  (Section 01, Figure 1)
Claim   : rho = M+M is a sum with one term per node. A single node
          recovers only its own share, never the whole.
"""
import numpy as np

print(__doc__)
np.random.seed(4)
n, ng = 4, 2
psi = np.random.randn(2**n); psi /= np.linalg.norm(psi)
psi = np.round(psi, 2); psi /= np.linalg.norm(psi)
M = psi.reshape(2**ng, 2**(n-ng))

print(f"{n} qubits, {ng} global bits -> {2**ng} nodes of {2**(n-ng)} amplitudes each")
print("-" * 62)
print("         l=00      l=01      l=10      l=11    (row norm)^2")
for g in range(4):
    row = "  ".join(f"{v:+8.3f}" for v in M[g])
    print(f"  g={g:02b} {row}      {np.dot(M[g],M[g]):.4f}")
print(f"\n  sum of squared row norms: {sum(np.dot(M[g],M[g]) for g in range(4)):.4f}")

print("\nThe reduced state of the local qubits")
print("-" * 62)
rho_all = M.conj().T @ M
print(f"  rho = M+M, summing over every row  ->  trace = {np.trace(rho_all).real:.4f}")
for g in range(4):
    part = np.outer(M[g].conj(), M[g])
    print(f"  term from node {g:02b} alone            ->  trace = {np.trace(part).real:.4f}")

print(f"\n  Node 00 owns one of four terms. What it can build has trace")
print(f"  {np.trace(np.outer(M[0].conj(), M[0])).real:.4f} -- precisely its own share, and no route to the rest.")

print("\nThe same at a larger size, to show it is not an artefact")
print("-" * 62)
for nq in (6, 8, 10):
    np.random.seed(7)
    p = np.random.randn(2**nq) + 1j*np.random.randn(2**nq); p /= np.linalg.norm(p)
    sl = p[:2**(nq-2)]
    print(f"  {nq:2d} qubits, {2**nq:5d} amplitudes, node 00 holds {2**(nq-2):4d}"
          f"  ->  trace {np.vdot(sl,sl).real:.4f}")
print("\n  In every case: a node holds its share of the numbers,")
print("  not a share of the state.")
