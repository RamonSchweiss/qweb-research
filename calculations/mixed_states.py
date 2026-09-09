"""
Wootters' concurrence, the shortfall S - E, and where it peaks.

Article : Where the Research Areas Converge  (Section 16, Figure 9)
Claims  : E + C <= 1 for mixed states; the shortfall vanishes at both
          ends of the family and is largest in between.
"""
import numpy as np
sy = np.array([[0,-1j],[1j,0]]); k = np.kron

def redA(r): return r.reshape(2,2,2,2).trace(axis1=1, axis2=3)
def vn(r):
    ev = np.linalg.eigvalsh(r).real; ev = ev[ev > 1e-12]
    return float(-(ev*np.log2(ev)).sum())
def hbin(x):
    if x <= 1e-12 or x >= 1-1e-12: return 0.0
    return float(-x*np.log2(x) - (1-x)*np.log2(1-x))
def EoF(rho):
    """Entanglement of formation via Wootters' concurrence (exact for 2 qubits)."""
    R = rho @ k(sy,sy) @ rho.conj() @ k(sy,sy)
    ev = np.sqrt(np.clip(np.linalg.eigvals(R).real, 0, None))
    ev = np.sort(ev)[::-1]
    C = max(0.0, ev[0]-ev[1]-ev[2]-ev[3])
    return hbin((1 + np.sqrt(max(0, 1-C**2)))/2)

print(__doc__)
e0 = np.array([1,0], dtype=complex); e1 = np.array([0,1], dtype=complex)
bell = (k(e0,e0) + k(e1,e1))/np.sqrt(2)
P = lambda v: np.outer(v, v.conj())

print("Family: rho = p |Phi+><Phi+| + (1-p) |00><00|")
print("-" * 70)
print("    p       S       E     C=1-S    E+C    shortfall  S_AB (whole)")
data = []
for p in np.linspace(0, 1, 21):
    r = p*P(bell) + (1-p)*P(k(e0,e0))
    S, E, SAB = vn(redA(r)), EoF(r), vn(r)
    data.append((p, S, E))
    if abs(p*20 - round(p*20)) < 1e-9 and round(p*20) % 2 == 0:
        print(f"  {p:4.2f}  {S:6.3f}  {E:6.3f}  {1-S:6.3f}  {E+1-S:6.3f}   {S-E:7.3f}    {SAB:6.3f}")

m = max(data, key=lambda t: t[1]-t[2])
print(f"\nShortfall peaks at p = {m[0]:.2f}: S = {m[1]:.3f}, E = {m[2]:.3f}, gap = {m[1]-m[2]:.3f}")
print(f"E + C there = {m[2]+1-m[1]:.3f}, which is 1 - gap. The two are mirror images.")

print("\nWhy it vanishes at both ends, for opposite reasons")
print("-" * 70)
print("  p = 0 : pure product state |00>. No entanglement, no mixing.")
print("  p = 1 : pure Bell state.        Maximal entanglement, no mixing.")
print("  Both ends are PURE. The gap exists only where the whole is mixed,")
print("  which the S_AB column above confirms.")

print("\nWhere E = C, and how noise moves that point")
print("-" * 70)
prev = None
for p, S, E in data:
    d = E - (1-S)
    if prev is not None and prev[0]*d < 0:
        p0, S0, E0 = prev[1]
        f = abs(prev[0])/(abs(prev[0])+abs(d))
        print(f"  mixed family : E = C at S = {S0+f*(S-S0):.3f}, both = {E0+f*(E-E0):.3f}")
        break
    prev = (d, (p, S, E))
print(f"  pure states  : E = C at S = 0.500, both = 0.500")
print("  Noise pushes the balance point right and drives it down.")
