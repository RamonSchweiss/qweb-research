"""
What a Hamiltonian says: Hermiticity, commutators, and where entanglement comes from.

Article : What a Hamiltonian Actually Says  (Sections 02-03, Figure 2)
Claims  : the worked Hermitian example has eigenvalues -2 and 4; breaking
          Hermiticity gives complex ones; [ZxZ, ZxI] = 0 but [XxI, ZxI] != 0;
          and the ground state of -ZxZ - h(XxI + IxX) is maximally entangled
          at small h, falling away as h grows.

Needs   : numpy
"""
import numpy as np

I = np.eye(2)
X = np.array([[0, 1], [1, 0]])
Z = np.array([[1, 0], [0, -1]])
k = np.kron

print(__doc__)

print("1 - Hermiticity, and why it is not a formality")
print("-" * 62)
A = np.array([[3, 2 + 1j], [2 - 1j, -1]])
print(f"  A          = {A.tolist()}")
print(f"  A-dagger   = {A.conj().T.tolist()}")
print(f"  A = A-dagger ?  {np.allclose(A, A.conj().T)}")
print(f"  eigenvalues: {np.round(np.linalg.eigvalsh(A), 6).tolist()}   both real\n")

B = np.array([[3, 2 + 1j], [5 - 2j, -1]])
print(f"  Break the mirror symmetry: replace 2-i by 5-2i")
print(f"  B = B-dagger ?  {np.allclose(B, B.conj().T)}")
ev = np.linalg.eigvals(B)
print(f"  eigenvalues: {np.round(ev, 4).tolist()}")
print("  Complex, and therefore useless as measurement outcomes.\n")

print("2 - Which term scores, and which term shuffles")
print("-" * 62)
for name, T in (("ZxZ", k(Z, Z)), ("XxI", k(X, I))):
    c = T @ k(Z, I) - k(Z, I) @ T
    print(f"  [{name}, ZxI] = 0 ?  {np.allclose(c, 0)}")
v = np.array([1, 0, 0, 0])
print(f"\n  ZxZ on |00> -> {np.round(k(Z, Z) @ v, 3).tolist()}   stays put; it assigns an energy")
print(f"  XxI on |00> -> {np.round(k(X, I) @ v, 3).tolist()}   moves to |10>; it shuffles")
print("  One acts like a potential, the other like kinetic energy.\n")

print("3 - Entanglement of the ground state (Figure 2)")
print("-" * 62)
def entanglement(h):
    H = -k(Z, Z) - h * (k(X, I) + k(I, X))
    ev, vec = np.linalg.eigh(H)
    g = vec[:, 0]
    s = np.linalg.svd(g.reshape(2, 2), compute_uv=False)
    p = s**2 / (s**2).sum()
    p = p[p > 1e-12]
    return float(-(p * np.log2(p)).sum()), float(ev[1] - ev[0])

print("       h     gap to first excited    entanglement")
for h in (0.0, 0.01, 0.1, 0.5, 1.0, 2.0, 5.0):
    S, gap = entanglement(h)
    note = "  <- degenerate; the question has no single answer" if gap < 1e-9 else ""
    print(f"   {h:6.2f}          {gap:8.4f}            {S:.4f}{note}")
print("\n  At h = 0 the ground state is two-fold degenerate, so the value there")
print("  is an artefact of which vector the routine happens to return.")
print("  For any h > 0 the ground state is unique: maximally entangled at small h,")
print("  falling monotonically as the field term takes over.")
print("\n  Nothing in the Hamiltonian mentions entanglement. It is written entirely")
print("  in terms acting on one qubit or two.")
