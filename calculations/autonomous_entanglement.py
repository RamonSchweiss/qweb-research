"""
What does an autonomously stabilised entanglement link actually buy a scheduler?

Companion to the partition_* scripts. Those measure how long a partition stays
viable; this one asks whether a link that refills itself - dissipatively
stabilised entanglement, "entanglement on autopilot" - changes that answer.

Two experiments are the occasion, both Physical Review X 2026:
  Andres-Juanes et al. (ISTA / TU Munich), a two-mode squeezed microwave
  reservoir driving two transmons into a stationary entangled state,
  concurrence 0.10, arXiv:2510.07139;
  Irfan et al. (Illinois / Chicago), a cascaded non-reciprocal waveguide and
  a coherent quantum absorber, concurrence 0.471, arXiv:2509.11872.
Both confirm a prediction of Kraus and Cirac, PRL 92 013602 (2004).

Findings : (1) concurrence maps to fidelity more robustly than expected. For a
               Werner state AND for a pure Schmidt-rank-two state, F = (1+C)/2
               exactly, and over random two-qubit states that expression is an
               upper bound on the fully entangled fraction. So the two
               experiments sit at F = 0.55 and F = 0.74, and this does not
               depend on assuming a particular noise model;
           (2) both are below the hashing threshold for Werner states, F = 0.811.
               One-way distillation yields nothing from them. They are still
               distillable, but only by recurrence - which needs many pairs and
               a two-way classical exchange per round;
           (3) the cost of that is where the argument turns. Reaching a fidelity
               a distributed gate could use takes several rounds and tens of raw
               pairs per output pair, and every round is a classical round trip
               - the very thing the planning limit taxes;
           (4) rate against demand decides it. The measured link delivers about
               12.5 kebit/s. Within one viability window of a QAOA partition on
               a random interaction graph, that is well under a hundredth of one
               entangled pair. Before distillation;
           (5) the staleness inequality does not move. Latency and the horizon
               are the only two quantities in it, and an autonomous link changes
               neither. What it changes is a different constraint - supply - and
               there it changes who decides, not how much arrives.

Reading  : autonomy is not freedom from scheduling. These schemes remove the
           decision to CREATE entanglement and leave the decision to SPEND it,
           and it is the second that the planning limit bounds.

Caveats  : BBPSSW with re-twirling to Werner form after each round is the
           textbook recurrence protocol and not the most efficient one; DEJMPS
           does better on the same states. The fidelity bound in (1) is checked
           numerically over random states, not proved here. Rates are quoted
           from one experiment at one operating point. Nothing here models the
           overhead of the swap that moves a stabilised pair onto computation
           qubits, which the APS viewpoint names as the open question.

Needs    : numpy
Runtime  : a few seconds.
"""
import numpy as np, itertools

# ------------------------------------------------------------ Hilfsfunktionen
PAULI = [np.array([[0, 1], [1, 0]], dtype=complex),
         np.array([[0, -1j], [1j, 0]]),
         np.array([[1, 0], [0, -1]], dtype=complex)]

PHI_PLUS = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)

def concurrence(rho):
    """Wootters' Concurrence eines Zweiqubit-Zustands."""
    sy = np.kron(PAULI[1], PAULI[1])
    R = rho @ sy @ rho.conj() @ sy
    ev = np.sqrt(np.clip(np.linalg.eigvals(R).real, 0, None))
    ev = np.sort(ev)[::-1]
    return float(max(0.0, ev[0] - ev[1] - ev[2] - ev[3]))

def fully_entangled_fraction(rho):
    """Groesste Treue zu einem maximal verschraenkten Zustand, ueber lokale
    Unitaere optimiert. Horodecki et al. 1996: F = (1 + N)/4, wobei N die Summe
    der Singulaerwerte der Korrelationsmatrix T_ij = Tr(rho sigma_i x sigma_j) ist."""
    T = np.array([[np.trace(rho @ np.kron(a, b)).real for b in PAULI] for a in PAULI])
    return float((1.0 + np.linalg.svd(T, compute_uv=False).sum()) / 4.0)

def werner(F):
    """Werner-Zustand mit Treue F zu Phi+."""
    p = (4 * F - 1) / 3.0
    return p * np.outer(PHI_PLUS, PHI_PLUS.conj()) + (1 - p) * np.eye(4) / 4.0

def random_state(rng, rank):
    """Zufaelliger Zweiqubit-Zustand gegebenen Rangs."""
    A = rng.normal(size=(4, rank)) + 1j * rng.normal(size=(4, rank))
    rho = A @ A.conj().T
    return rho / np.trace(rho).real

def shannon(ps):
    ps = np.array([p for p in ps if p > 1e-15])
    return float(-(ps * np.log2(ps)).sum())

# ------------------------------------------------------------- Destillation
def bbpssw_step(F):
    """Ein Rekursionsschritt nach Bennett et al. 1996, mit Rueckfuehrung auf
    Werner-Form. Zwei Paare hinein, eines heraus - mit Wahrscheinlichkeit p."""
    q = (1 - F) / 3.0
    p = F**2 + 2 * F * q + 5 * q**2
    return (F**2 + q**2) / p, p

def distil(F0, target):
    """Wie viele Runden, Rohpaare und klassische Umlaeufe bis zur Zieltreue?"""
    F, rounds, pairs = F0, 0, 1.0
    while F < target:
        if rounds > 60: return None
        Fn, p = bbpssw_step(F)
        if Fn <= F + 1e-12: return None      # konvergiert nicht
        F, rounds = Fn, rounds + 1
        pairs = 2 * pairs / p                # erwartete Rohpaare je Ausgangspaar
    return rounds, pairs, F

# --------------------------------------------------------- gemessene Werte
C_ISTA, C_UIUC = 0.10, 0.471
RATE_EBIT_S = 12.5e3          # ISTA, Qubit-Seite, am besten Arbeitspunkt
GATE_NS = 60.0                # wie in den partition_*-Skripten
H_V_LAYERS, ROUNDS_PER_LAYER = 1.25, 6.0   # QAOA, Zufallsgraph, n=12, m=18
C_LIGHT = 299_792_458

def hashing_yield(F):
    """Ausbeute der Einweg-Destillation (Hashing) fuer einen Werner-Zustand."""
    q = (1 - F) / 3.0
    return 1.0 - shannon([F, q, q, q])

def hashing_threshold():
    """Treue, ab der die Hashing-Schranke positiv wird."""
    lo, hi = 0.5, 1.0
    for _ in range(80):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if hashing_yield(mid) < 0 else (lo, mid)
    return (lo + hi) / 2

F_HASH = hashing_threshold()

def main():
    print(__doc__)

    print("1 - From concurrence to fidelity, without choosing a noise model")
    print("-" * 78)
    print("  The experiments report concurrence. A distributed gate cares about")
    print("  fidelity. The step between them normally needs an assumption - so the")
    print("  first question is how much the answer depends on it.\n")
    print("   state family                      C       F to Phi+    (1+C)/2")
    for name, rho in (("Werner, F = 0.80", werner(0.80)),
                      ("Werner, F = 0.60", werner(0.60))):
        C = concurrence(rho)
        print(f"   {name:30s}  {C:5.3f}     {fully_entangled_fraction(rho):5.3f}       {(1+C)/2:5.3f}")
    for th in (np.pi/4, np.pi/8, np.pi/16):
        psi = np.array([np.cos(th), 0, 0, np.sin(th)], dtype=complex)
        rho = np.outer(psi, psi.conj())
        C = concurrence(rho)
        print(f"   {'pure, theta = ' + f'{th:.4f}':30s}  {C:5.3f}     "
              f"{fully_entangled_fraction(rho):5.3f}       {(1+C)/2:5.3f}")

    rng = np.random.default_rng(11)
    worst, viol = 0.0, 0
    N = 4000
    TOLERANZ = 1e-6          # Rundungsrauschen der Singulaerwertzerlegung, nicht Verletzung
    for _ in range(N):
        rho = random_state(rng, int(rng.integers(1, 5)))
        C, F = concurrence(rho), fully_entangled_fraction(rho)
        d = F - (1 + C) / 2
        worst = max(worst, d)
        viol += d > TOLERANZ
    print(f"\n  Over {N} random two-qubit states of mixed rank, F never exceeds (1+C)/2")
    print(f"  ({viol} exceedances beyond numerical noise; the largest excess of any")
    print(f"  kind is {worst:+.0e}). So (1+C)/2 is not an assumption about the noise but")
    print("  a ceiling - and for the two families most likely to describe these")
    print("  experiments it is attained exactly.\n")
    print("   experiment                        C        F at most")
    for label, C in (("ISTA, squeezed reservoir", C_ISTA),
                     ("Illinois, cascaded absorber", C_UIUC)):
        print(f"   {label:32s} {C:5.3f}      {(1+C)/2:5.3f}")

    print("\n\n2 - What those pairs cost before a gate can use them")
    print("-" * 78)
    print("  One-way distillation first. For a Werner state the hashing bound gives")
    print("  a positive yield only above a threshold fidelity; below it, one-way")
    print("  protocols return nothing at all.\n")

    F_hash = F_HASH
    print(f"   hashing threshold      F = {F_hash:.4f}   (concurrence {2*F_hash-1:.4f})")
    print(f"   ISTA                   F = {(1+C_ISTA)/2:.4f}   -> yield "
          f"{hashing_yield((1+C_ISTA)/2):+.3f} ebit per pair")
    print(f"   Illinois               F = {(1+C_UIUC)/2:.4f}   -> yield "
          f"{hashing_yield((1+C_UIUC)/2):+.3f} ebit per pair")
    print("\n  Both are below it. The states are still distillable - every two-qubit")
    print("  state with F above one half is - but only by recurrence, which consumes")
    print("  pairs in twos and needs both ends to compare a measurement each round.\n")
    print("   start          target    rounds   raw pairs per output   classical round trips")
    for label, C in (("ISTA", C_ISTA), ("Illinois", C_UIUC)):
        for target in (0.90, 0.99):
            r = distil((1 + C) / 2, target)
            if r is None:
                print(f"   {label:12s}   {target:.2f}         -            does not converge          -")
            else:
                rounds, pairs, Ffin = r
                print(f"   {label:12s}   {target:.2f}      {rounds:5d}            {pairs:11.1f}"
                      f"            {rounds:5d}")
    print("\n  The rightmost column is the one that matters here. Every round is a")
    print("  two-way classical exchange between the two ends - the same round trip")
    print("  the planning limit is about. Autonomy on the quantum side does not")
    print("  remove classical traffic; it moves it from asking for a link to")
    print("  cleaning one up.")

    print("\n\n3 - Rate against demand")
    print("-" * 78)
    gate_slots = 1.0 / (GATE_NS * 1e-9)
    print(f"  A two-qubit gate takes {GATE_NS:.0f} ns, so one gate line offers")
    print(f"  {gate_slots:,.0f} slots per second. The measured link delivers")
    print(f"  {RATE_EBIT_S:,.0f} entangled pairs per second.\n")
    print(f"   ratio of local gate slots to delivered pairs      1 : {gate_slots/RATE_EBIT_S:,.0f}")

    tl = (ROUNDS_PER_LAYER * GATE_NS + 20.0) * 1e-9
    window = H_V_LAYERS * tl
    print(f"\n  Against the viability horizon measured in partition_topology.py -")
    print(f"  {H_V_LAYERS:.2f} layers for QAOA on a random interaction graph, at")
    print(f"  {tl*1e6:.2f} us per layer, so a window of {window*1e6:.2f} us:\n")
    print(f"   raw pairs delivered within one viability window     {RATE_EBIT_S*window:.4f}")

    # Rate und Guete stammen aus DERSELBEN Arbeit - sonst mischt man zwei Experimente.
    r = distil((1 + C_ISTA) / 2, 0.90)
    if r:
        per_usable = r[1] / RATE_EBIT_S
        print(f"\n  That is the raw figure. Rate and quality both come from the same")
        print(f"  experiment, so they can be combined: at concurrence {C_ISTA:.2f} the")
        print(f"  recurrence needs {r[1]:,.0f} raw pairs for one at F = 0.90, and the")
        print(f"  link supplies {RATE_EBIT_S:,.0f} per second.\n")
        print(f"   time to produce ONE usable pair                     {per_usable:,.0f} s"
              f"  ({per_usable/60:.1f} min)")
        print(f"   viability windows that pass meanwhile               {per_usable/window:,.0f}")

    r2 = distil((1 + C_UIUC) / 2, 0.90)
    if r2:
        print(f"\n  The better link is the Illinois one, at concurrence {C_UIUC:.3f}, which")
        print(f"  needs only {r2[1]:.0f} raw pairs per usable one. No rate is published for")
        print(f"  it, so the following is a what-if and not a measurement: at the ISTA")
        print(f"  rate it would come to {r2[1]/RATE_EBIT_S*1e3:.1f} ms per usable pair, or")
        print(f"  {RATE_EBIT_S*window/r2[1]:.5f} of a pair per viability window.")
    print("\n  Either way the supply is not close, and the gap is not one that")
    print("  better bookkeeping closes.")

    print("\n\n4 - Does the staleness inequality move?")
    print("-" * 78)
    print("  S = latency / H_v. Two quantities, and an autonomous link is in")
    print("  neither of them: it does not slow the computation down, and it does")
    print("  not shorten the path a message takes. What central planning needs is")
    print("  simply that the round trip fits inside the horizon.\n")
    print("   separation    round trip    H_v needed    H_v measured (QAOA, random)")
    for d in (10, 70, 300, 1000):
        rt = 2 * d / C_LIGHT
        print(f"   {d:5d} m      {rt*1e6:6.2f} us     {rt/tl:6.2f} layers    "
              f"{H_V_LAYERS:6.2f} layers")
    print("\n  The link rate does not appear anywhere in that table, because it")
    print("  belongs to a different constraint:\n")
    print("    planning    latency  <=  H_v            unchanged by an autonomous link")
    print("    supply      ebit rate >= gate demand    autonomous, and short by ~1:1300")
    print("\n  So the honest account is not that these schemes help or do not help.")
    print("  They address the second constraint and leave the first untouched - and")
    print("  on the second what changes is who decides, not how much arrives. The")
    print("  scheduler no longer has to ask for entanglement. It still has to decide")
    print("  where to spend it, and that decision is the one under the clock.")


if __name__ == "__main__":
    main()
