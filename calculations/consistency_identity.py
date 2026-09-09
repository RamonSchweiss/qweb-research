"""
E + C = 1 for pure states, and the counterexample that breaks it.

Article : Where the Research Areas Converge  (Sections 15-16, Figure 8)
Claims  : For pure bipartite states, entanglement E and local consistency
          C = 1 - S are exactly complementary.
          For mixed states the identity weakens to E + C <= 1.
"""
import numpy as np

def redA(r): return r.reshape(2,2,2,2).trace(axis1=1, axis2=3)
def vn(r):
    ev = np.linalg.eigvalsh(r).real; ev = ev[ev > 1e-12]
    return float(-(ev * np.log2(ev)).sum())

print(__doc__)
print("Pure states: E = S and C = 1 - S, so the sum is 1")
print("-" * 66)
print("  t/pi      S      E = S    C = 1-S    E + C")
for f in (0, 0.05, 0.125, 0.1875, 0.25):
    t = f * np.pi
    psi = np.zeros(4, dtype=complex); psi[0], psi[3] = np.cos(t), np.sin(t)
    S = vn(redA(np.outer(psi, psi.conj())))
    print(f" {f:7.4g}  {S:6.3f}   {S:6.3f}    {1-S:7.3f}   {S + 1 - S:6.3f}")

print("\nThe accounting, checked the other way")
print("-" * 66)
print("  A pure two-qubit state is fully determined: 2 bits' worth.")
print("  The parts together supply 2(1 - S). The difference is 2S,")
print("  which is the mutual information I(A:B) held in the correlation.\n")
print("  t/pi      S    local A  local B   sum    global   surplus    2S")
for f in (0, 0.05, 0.125, 0.25):
    t = f * np.pi
    psi = np.zeros(4, dtype=complex); psi[0], psi[3] = np.cos(t), np.sin(t)
    S = vn(redA(np.outer(psi, psi.conj())))
    la = lb = 1 - S
    print(f" {f:7.4g}  {S:5.3f}   {la:6.3f}  {lb:6.3f}  {la+lb:6.3f}    2.000   {2-(la+lb):7.3f}  {2*S:5.3f}")

print("\nThe counterexample: a classically correlated mixture")
print("-" * 66)
k = np.kron
e0 = np.array([1,0], dtype=complex); e1 = np.array([0,1], dtype=complex)
P = lambda v: np.outer(v, v.conj())
rho = 0.5 * (P(k(e0,e0)) + P(k(e1,e1)))
S = vn(redA(rho))
print(f"  rho = 1/2(|00><00| + |11><11|)")
print(f"  reduced state is I/2, so S = {S:.3f} and C = 1 - S = {1-S:.3f}")
print(f"  but the state is separable: a mixture of product states, so E = 0")
print(f"  E + C = 0 + {1-S:.3f} = {1-S:.3f}   -- not 1\n")
print("  For mixed states the reduced entropy counts entanglement and")
print("  ordinary classical ignorance together, and so overstates E.")
print("  The identity becomes an inequality:  E + C <= 1")
