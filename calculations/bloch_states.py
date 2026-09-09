"""
The six Pauli eigenstates, their preparation, and why no gate reaches I/2.

Article : Where the Research Areas Converge  (Sections 05, Figures 3 and 5)
Claims  : Six named states, not three. Every surface point is a state.
          Gates rotate the Bloch vector but never shorten it.
"""
import numpy as np
X = np.array([[0,1],[1,0]]); Y = np.array([[0,-1j],[1j,0]]); Z = np.array([[1,0],[0,-1]])
s2 = 1/np.sqrt(2)
H = np.array([[1,1],[1,-1]])*s2
S_ = np.array([[1,0],[0,1j]])
Xg = np.array([[0,1],[1,0]])
k0 = np.array([1,0], dtype=complex)
bloch = lambda r: [float(np.real(np.trace(r@M))) for M in (X,Y,Z)]

print(__doc__)
print("The six eigenstates and their Bloch vectors")
print("-" * 64)
states = {"|0>":k0, "|1>":Xg@k0, "|+>":H@k0, "|->":H@Xg@k0,
          "|+i>":S_@H@k0, "|-i>":S_.conj().T@H@k0}
for name, v in states.items():
    r = np.outer(v, v.conj()); b = bloch(r)
    L = np.sqrt(sum(q*q for q in b))
    axis = ["x","y","z"][int(np.argmax(np.abs(b)))]
    print(f"  {name:5s}  ({b[0]:+.0f}, {b[1]:+.0f}, {b[2]:+.0f})   length {L:.3f}   sharp along {axis}")

print("\nPreparation, all starting from |0>")
print("-" * 64)
for name, gates in (("|0>","no gate"),("|1>","X"),("|+>","H"),
                    ("|->","X, then H"),("|+i>","H, then S"),("|-i>","H, then S+")):
    print(f"  {name:5s}  {gates}")

print("\nAny point of the surface needs only two rotations")
print("-" * 64)
Ry = lambda t: np.array([[np.cos(t/2),-np.sin(t/2)],[np.sin(t/2),np.cos(t/2)]])
Rz = lambda p: np.array([[np.exp(-1j*p/2),0],[0,np.exp(1j*p/2)]])
for t,p in ((0.7,0.0),(1.2,0.9),(2.4,2.0)):
    v = Rz(p) @ Ry(t) @ k0
    r = np.outer(v, v.conj()); b = bloch(r)
    L = np.sqrt(sum(q*q for q in b))
    print(f"  Ry({t}) then Rz({p}): Bloch length {L:.4f}  -> pure, and none of the six")

print("\nWhy no gate reaches the centre")
print("-" * 64)
print("  Gates are unitary. Check that they preserve Bloch length:")
for name, G in (("H",H),("S",S_),("X",Xg),("Ry(1.1)",Ry(1.1))):
    v = G @ (Ry(0.8) @ k0)
    L = np.sqrt(sum(q*q for q in bloch(np.outer(v, v.conj()))))
    print(f"    after {name:8s} -> length {L:.6f}")
print("\n  The vector turns; it never shortens. I/2 has length 0 and is")
print("  therefore unreachable by any gate. A qubit enters the interior")
print("  only by losing information -- to a partner, to noise, or to a coin.")
print("\n  And those three are indistinguishable from the qubit alone:")
mix = 0.5*np.outer(k0,k0) + 0.5*np.outer(Xg@k0,(Xg@k0).conj())
print(f"    coin flip between |0> and |1> gives Bloch length {np.sqrt(sum(q*q for q in bloch(mix))):.4f}")
kk = np.kron
bell = (kk(k0,k0)+kk(Xg@k0,Xg@k0))/np.sqrt(2)
red = np.outer(bell,bell.conj()).reshape(2,2,2,2).trace(axis1=1,axis2=3)
print(f"    half of a Bell pair gives          Bloch length {np.sqrt(sum(q*q for q in bloch(red))):.4f}")
