"""
Why central scheduling fails before coherence does.

Article : Where the Research Areas Converge  (Section 24, Figure 13)
Claim   : Gathering the state costs a round trip; the weights move
          meanwhile. For plausible drift rates the scheduling bound is
          tighter than the coherence bound.
"""
c = 299_792_458
tg = 60e-9           # two-qubit gate time, superconducting
print(__doc__)
print("  How long do the entropies stay usable? Expressed in gate counts.\n")
print("  gates until drift   drift time    scheduling limit")
print("-" * 56)
for ng in (50, 200, 1000, 5000):
    T = ng*tg
    print(f"  {ng:>10d}          {T*1e6:8.1f} us    {T*c/2/1000:9.1f} km")

print("\n  Against the coherence bound of about 30 km:")
print("  for 50 to 1000 gates the scheduling limit is tighter.")
print("  Only if the weights stay usable for several thousand gates")
print("  does coherence bind first. The ordering is not universal,")
print("  but it holds for plausible values.\n")

T = 200*tg
print(f"  Taking 200 gates ({T*1e6:.0f} us) as the reference:")
print("  distance          round trip    share of drift time")
print("-" * 56)
for name, km in (("rack",0.01),("data centre",0.5),("campus",5),("metro",30)):
    rt = 2*km*1000/c
    print(f"  {name:15s} {rt*1e6:8.1f} us   {rt/T:12.1%}")
print(f"\n  Central planning is sound while the round trip is short")
print(f"  against the drift -- so up to roughly {T*c/2/1000:.1f} km.")
