"""
The CHSH bounds, and where the Bell bound sits on the scale.

Article : Two Answers to One Question  (Section 06, Figure 4)
Claims  : classical bound 2, quantum bound 2*sqrt(2), and the Bell bound
          lies at 70.7% of the quantum maximum, not halfway.
"""
import numpy as np
print(__doc__)
cl, qm = 2.0, 2*np.sqrt(2)
print(f"  classical (local hidden variables) : {cl:.4f}")
print(f"  quantum (Tsirelson)                : {qm:.4f}")
print(f"  ratio                              : {cl/qm:.4f}  = {100*cl/qm:.1f}%")
print("\n  So on a scale from 0 to the quantum maximum, the classical")
print("  bound sits at 70.7%, not at 50%. The window quantum mechanics")
print("  opens is narrower than it is usually drawn.\n")

print("Achieving the quantum bound with explicit measurement angles")
print("-" * 62)
def E(a, b):
    return -np.cos(2*(a-b))     # correlation for the singlet
a0, a1 = 0, np.pi/4
b0, b1 = np.pi/8, 3*np.pi/8
S = abs(E(a0,b0) - E(a0,b1) + E(a1,b0) + E(a1,b1))
print(f"  angles: a0=0, a1=pi/4, b0=pi/8, b1=3pi/8")
print(f"  CHSH value = {S:.4f}   (Tsirelson bound {qm:.4f})")
print(f"  reaches the bound: {abs(S-qm) < 1e-9}")
