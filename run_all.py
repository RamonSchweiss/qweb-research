"""
Run the verification scripts and report whether each completed.

    python run_all.py           the quick checks, about thirty seconds
    python run_all.py --all     including the slow experiments, half an hour or more

Both figures are measured on one machine and will differ on yours; the script
prints its own total at the end, which is the number to trust.

qdnn_variants.py is a module the QDNN scripts import, not a script to run.
qdnn_sweep.py needs a width argument; see its own docstring.
"""
import subprocess, sys, pathlib, time

HERE = pathlib.Path(__file__).parent / "calculations"
MODULES = {"qdnn_variants.py"}          # importiert, nicht ausgefuehrt
# Nicht im schnellen Lauf. Zwei Gruende, beide vorher festgelegt.
#
# Zu langsam: ueber sieben Sekunden, am 15.11.2026 einmal gemessen und nicht
# geschaetzt. Der schnelle Lauf hatte 29 Skripte und 247 Sekunden gebraucht,
# wovon sechs Dateien 211 Sekunden ausmachten.
#
# Pruefen nichts: qdnn_sweep.py und qdnn_replicate.py drucken ohne Argument
# nur ihre Hilfe. Ihre sechs bis acht Sekunden sind reine Importzeit fuer
# pennylane und sklearn. Nach Zeit allein waere das Paar getrennt worden --
# eines drin, eines draussen --, obwohl beide dasselbe tun.
SLOW    = {"qdnn_ablation.py", "partition_robustness.py",
           "partition_topology.py",
           "horizon_early_signal.py",
           "gate_vs_state_partition.py",
           "entanglement_horizon.py",
           "second_circuit_family.py",
           "staleness_cost.py",
           "drift_cost.py",
           "drift_robustness.py",
           "qcnn_control_probe.py",
           "findability.py",
           "findability_large.py",
           "cut_degeneracy.py",
           "findability_scoping.py",
           "resolution_limit.py",
           "qdnn_replicate.py",
           "qdnn_sweep.py"}
NEEDS_ARG = {"qdnn_sweep.py", "qdnn_replicate.py"}           # erklaert sich selbst, wenn ohne Argument aufgerufen

run_slow = "--all" in sys.argv
scripts = sorted(p.name for p in HERE.glob("*.py") if p.name not in MODULES)
if not run_slow:
    scripts = [s for s in scripts if s not in SLOW]

print(f"QWeb (C) Research - running {len(scripts)} scripts"
      + ("" if run_slow else f", skipping {len(SLOW)} slow ones"))
print()

t_all = time.time()
fail = 0
for s in scripts:
    t0 = time.time()
    r = subprocess.run([sys.executable, str(HERE/s)], capture_output=True, text=True)
    ok = r.returncode == 0
    fail += not ok
    note = "  (prints usage)" if s in NEEDS_ARG else ""
    print(f"  {'ok  ' if ok else 'FAIL'}  {s:24s} {time.time()-t0:6.2f}s{note}")
    if not ok and r.stderr.strip():
        print("          " + r.stderr.strip().splitlines()[-1])

print(f"\n{len(scripts)-fail} of {len(scripts)} completed "
      f"in {time.time()-t_all:.0f}s.")
print(f"Not run: {', '.join(sorted(MODULES))} (a module)"
      + ("" if run_slow else f", and these with --all: "
         f"{', '.join(sorted(SLOW))}"))
print("Run any script on its own to see its output in full.")
sys.exit(1 if fail else 0)
