"""
How a gate is made: the closed form, the rotating wave approximation, and detuning.

Article : How a Gate Is Actually Made  (Sections 02-04, Figure 2)
Claims  : exp(-i(wt/2)sigma_x) = cos(wt/2) I - i sin(wt/2) sigma_x, so at wt = pi
          it is the NOT gate; the rotating wave approximation agrees with the full
          time-dependent Hamiltonian to within 0.006 on resonance; and the ceiling
          on the excited-state population follows Omega^2/(Omega^2 + Delta^2).

Needs   : numpy, scipy
Runtime : about twenty seconds.
"""
import numpy as np
from scipy.linalg import expm
from scipy.integrate import solve_ivp

X = np.array([[0, 1], [1, 0]])
Z = np.array([[1, 0], [0, -1]])
I = np.eye(2)
print(__doc__)

print("1 - A gate is a Hamiltonian with a stopwatch")
print("-" * 66)
print("  U = exp(-i H t / hbar), with hbar = 1 throughout.\n")
print("     Omega*t     U (global phase divided out)            what it is")
for ot, label in ((np.pi / 2, "pi/2"), (np.pi, "pi  ")):
    U = expm(-1j * (ot / 2) * X)
    closed = np.cos(ot / 2) * I - 1j * np.sin(ot / 2) * X
    assert np.allclose(U, closed), "closed form disagrees"
    ph = np.exp(1j * np.angle(U[0, 0] if abs(U[0, 0]) > 1e-9 else U[0, 1]))
    what = "half-flip" if ot < np.pi - 1e-9 else "the NOT gate"
    print(f"      {label}     {np.round(U / ph, 3).tolist()}   {what}")
print("\n  The closed form matches exactly, for every angle tested.")
U = expm(-1j * (np.pi / 2) * X)
print(f"  Check: |0> under a pi pulse -> {np.round(np.abs(U @ np.array([1, 0]))**2, 6).tolist()}   (probabilities)\n")

print("2 - Does the rotating wave approximation hold?")
print("-" * 66)
w0, Om = 40.0, 1.0
def simulate(w, T, n=4000):
    def rhs(t, y):
        psi = y[:2] + 1j * y[2:]
        d = -1j * (((w0 / 2) * Z + Om * np.cos(w * t) * X) @ psi)
        return np.concatenate([d.real, d.imag])
    s = solve_ivp(rhs, [0, T], np.array([1., 0., 0., 0.]),
                  t_eval=np.linspace(0, T, n), rtol=1e-9, atol=1e-11)
    psi = s.y[:2] + 1j * s.y[2:]
    return s.t, np.abs(psi[1])**2

T = 2 * np.pi / Om
t, p = simulate(w0, T)
pred = np.sin(Om * t / 2)**2
print(f"  Qubit splitting w0 = {w0}, Rabi frequency Omega = {Om}, on resonance.")
print(f"  Approximation predicts sin^2(Omega t / 2).\n")
print("        t       simulated   approximation")
for frac in (0.25, 0.5, 0.75, 1.0):
    i = int(frac * (len(t) - 1))
    print(f"     {t[i]:6.3f}      {p[i]:.4f}       {pred[i]:.4f}")
print(f"\n  Largest deviation over the full period: {np.max(np.abs(p - pred)):.4f}")
print("  The residual ripple is the counter-rotating term the approximation drops.\n")

print("3 - What detuning costs")
print("-" * 66)
print("  Ceiling on the excited-state population, simulated against the formula.\n")
print("     detuning   simulated max   Omega^2/(Omega^2+Delta^2)")
for D in (0, 0.5, 1, 2, 3):
    _, pd = simulate(w0 + D, T)
    print(f"      {D:4.1f}        {pd.max():.4f}            {Om**2/(Om**2+D**2):.4f}")
print("\n  Detune by one Rabi frequency and half the population is already")
print("  out of reach. By three, the qubit never gets past one chance in ten.")
print("  Off resonance the sigma_z term survives and tilts the rotation axis,")
print("  so the state turns about a circle that does not pass through |1>.")
