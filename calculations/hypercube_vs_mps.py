"""
Flat exchange against bond dimension: the crossover at S = 1.4.

Article : What a Node Actually Holds  (Sections 02-04, Figure 3)
Claims  : The hypercube moves 2^(n-1) amplitudes whatever the state.
          A tensor network stores 2*chi^2*n, with chi >= 2^S.
"""
import numpy as np, math
def vn(p):
    p = p[p > 1e-12]; return float(-(p*np.log2(p)).sum())

print(__doc__)
n = 10
np.random.seed(3)

psi_prod = np.zeros(2**n, dtype=complex); psi_prod[0] = 1
t = 0.15*np.pi
psi_weak = np.zeros(2**n, dtype=complex); psi_weak[0], psi_weak[-1] = np.cos(t), np.sin(t)
U = np.linalg.qr(np.random.randn(2**(n//2), 2**(n//2)))[0]
V = np.linalg.qr(np.random.randn(2**(n//2), 2**(n//2)))[0]
sv = np.zeros(2**(n//2)); sv[:8] = np.exp(-0.4*np.arange(8)); sv /= np.linalg.norm(sv)
psi_mid = (U @ np.diag(sv) @ V).reshape(-1)
psi_rand = np.random.randn(2**n) + 1j*np.random.randn(2**n); psi_rand /= np.linalg.norm(psi_rand)

print(f"{n} qubits, cut down the middle, one gate on a global qubit")
print("-" * 72)
print("  state               S     chi   hypercube moves   tensor network stores")
for name, psi in (("product state", psi_prod), ("weakly entangled", psi_weak),
                  ("partly entangled", psi_mid), ("random state", psi_rand)):
    M = psi.reshape(2**(n//2), 2**(n//2))
    s = np.linalg.svd(M, compute_uv=False); p = s**2; p /= p.sum()
    S = vn(p); chi = int((p > 1e-10).sum())
    print(f"  {name:18s} {S:5.2f}  {chi:4d}      {2**(n-1):8d}          {2*chi*chi*n:8d}")

print(f"\n  The hypercube figure never changes. Why: a gate on a global qubit")
print(f"  pairs amplitudes whose global index differs in one bit, and those")
print(f"  sit on different nodes. Half the array changes hands: 2^{n-1} = {2**(n-1)}.")
print("  That count depends on the length of the list and nothing else.\n")

print("Where chi comes from")
print("-" * 72)
print("  The Schmidt rank r must fit on the bond, so chi >= r.")
print("  Entropy is largest when the r weights are equal: S <= log2(r).")
print("  Therefore chi >= r >= 2^S.\n")
for S in (0, 1, 2, 3, 4.3):
    print(f"    S = {S:4.1f} bits -> chi at least {2**S:7.1f}")

print("\nThe crossover")
print("-" * 72)
pts = [(0.0,1),(0.734,2),(1.785,8),(4.301,32)]
mem = [(S, 2*c*c*n) for S,c in pts]
target = 2**(n-1)
for (S0,m0),(S1,m1) in zip(mem, mem[1:]):
    if m0 < target <= m1:
        f = (math.log10(target)-math.log10(m0))/(math.log10(m1)-math.log10(m0))
        print(f"  Curves cross at S = {S0+f*(S1-S0):.3f} bits")
        break
print(f"  Equivalently: 2*chi^2*{n} < {target} holds up to chi = {int((target/(2*n))**0.5)}")
print("\n  Below the crossover the tensor network wins, often by orders")
print("  of magnitude. Above it the flat rate wins, and keeps winning.")
