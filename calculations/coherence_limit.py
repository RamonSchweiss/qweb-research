"""
Round trip against coherence time: the 30 km bound.

Article : Where the Research Areas Converge  (Section 20, Figure 11)
Claim   : At roughly 30 km one round trip consumes the entire coherence
          time of a superconducting qubit, so live distributed gates
          become impossible.
"""
c = 299_792_458
T2 = 200e-6          # a good superconducting coherence time
print(__doc__)
print(f"  assumed coherence time: {T2*1e6:.0f} us")
print(f"  light travels {c/1e6:.1f} m per microsecond\n")
print("  distance          round trip     share of coherence   verdict")
print("-" * 68)
for name, km in (("in a rack",0.01),("data centre",0.5),("campus",5),
                 ("metro",30),("regional",300),("transatlantic",6200)):
    rt = 2*km*1000/c
    q = rt/T2
    v = "fine" if q < 0.05 else ("marginal" if q < 1 else "impossible")
    print(f"  {name:15s} {rt*1e6:9.1f} us   {q:14.2%}   {v}")

lim = T2*c/2/1000
print(f"\n  The line is crossed at {lim:.1f} km. Light speed only --")
print("  no switching, no repeaters, no processing.")
print("\n  Trapped ions hold coherence for seconds rather than")
print("  microseconds, which moves the line but does not remove it:")
for T, label in ((1e-3,"1 ms"), (1.0,"1 s")):
    print(f"    coherence {label:5s} -> limit at {T*c/2/1000:,.0f} km")
