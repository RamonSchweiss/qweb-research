"""
Entanglement entropy of the standard family, and rank against entropy.

Article : Where the Research Areas Converge  (Sections 04-05, Figures 2-4)
Claims  : S(t) = -cos^2 t log2 cos^2 t - sin^2 t log2 sin^2 t
          The Schmidt rank jumps; the entropy rises smoothly.
"""
import numpy as np

def reduced(psi):
    return np.outer(psi, psi.conj()).reshape(2,2,2,2).trace(axis1=1, axis2=3)

def vn(rho):
    ev = np.linalg.eigvalsh(rho).real
    ev = ev[ev > 1e-12]
    return float(-(ev * np.log2(ev)).sum())

print(__doc__)
print("  t/pi     cos^2 t   sin^2 t      S     Schmidt rank")
print("-" * 60)
for f in (0, 0.02, 0.05, 0.125, 0.1875, 0.25):
    t = f * np.pi
    psi = np.zeros(4, dtype=complex)
    psi[0], psi[3] = np.cos(t), np.sin(t)
    rho = reduced(psi)
    S = vn(rho)
    rank = int((np.linalg.eigvalsh(rho).real > 1e-12).sum())
    print(f" {f:7.4g}   {np.cos(t)**2:7.4f}   {np.sin(t)**2:7.4f}   {S:6.3f}        {rank}")

print("\nClosed form check: the same S from the explicit formula")
print("-" * 60)
for f in (0.05, 0.125, 0.25):
    t = f * np.pi
    c, s = np.cos(t)**2, np.sin(t)**2
    closed = -sum(q * np.log2(q) for q in (c, s) if q > 1e-12)
    psi = np.zeros(4, dtype=complex); psi[0], psi[3] = np.cos(t), np.sin(t)
    print(f"  t = {f}pi : from rho = {vn(reduced(psi)):.6f}, from formula = {closed:.6f}")

print("\nThe two extremes by hand")
print("-" * 60)
print("  t = 0    : weights 1 and 0. log2(1) = 0, and 0 contributes nothing.  S = 0")
print("  t = pi/4 : weights 1/2 and 1/2. Each gives 1/2 x 1.                  S = 1")
print("\nNote the rank jumps from 1 to 2 the instant t leaves zero,")
print("while S rises continuously. Two different questions, two answers.")
