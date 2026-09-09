"""
No-cloning, checked numerically.

Article : Two Answers to One Question — Quantum Security and the Key
          Distribution Problem  (Section 04)
Claim   : No unitary can copy an arbitrary unknown quantum state.
"""
import numpy as np

print(__doc__)
print("The proof in three lines")
print("-" * 60)
print("  Suppose U(|psi>|0>) = |psi>|psi> for every |psi>.")
print("  Unitary maps preserve inner products, so for any |a>, |b>:")
print("      <a|b> = <a|b>^2      writing x = <a|b>:   x = x^2")
print("  which forces x = 0 or x = 1. Only orthogonal or identical")
print("  states survive. An arbitrary unknown state cannot be copied.\n")

print("Numerical check: solve x = x^2 and confirm nothing else works")
print("-" * 60)
for x in (0.0, 0.25, 0.5, 0.707, 0.9, 1.0):
    ok = abs(x - x * x) < 1e-12
    print(f"  <a|b> = {x:5.3f}   x - x^2 = {x - x*x:+.4f}   {'consistent' if ok else 'contradiction'}")

print("\nSo a cloner could work only for a basis known in advance.")
print("Verify that: try to clone within a known orthonormal basis.")
print("-" * 60)
e0, e1 = np.array([1, 0]), np.array([0, 1])
basis = {"|0>": e0, "|1>": e1}
# CNOT copies computational basis states
CNOT = np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]])
for name, v in basis.items():
    got = CNOT @ np.kron(v, e0)
    want = np.kron(v, v)
    print(f"  CNOT({name}|0>) = {name}{name} ?  {np.allclose(got, want)}")

print("\nNow the same gate on a superposition, which is the general case:")
plus = (e0 + e1) / np.sqrt(2)
got = CNOT @ np.kron(plus, e0)
want = np.kron(plus, plus)
print(f"  CNOT(|+>|0>) = |+>|+> ?  {np.allclose(got, want)}")
print(f"    produced : {np.round(got, 4)}   (a Bell state, entangled)")
print(f"    wanted   : {np.round(want, 4)}   (two independent copies)")
print("\n  The gate entangles instead of copying. That is the theorem.")
