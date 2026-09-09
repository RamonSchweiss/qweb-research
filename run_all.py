"""Run every calculation and report whether each completed."""
import subprocess, sys, pathlib, time

d = pathlib.Path(__file__).parent / "calculations"
scripts = sorted(p.name for p in d.glob("*.py"))
print(f"QWeb (C) Research — running {len(scripts)} calculations\n")
fail = 0
for s in scripts:
    t0 = time.time()
    r = subprocess.run([sys.executable, str(d/s)], capture_output=True, text=True)
    ok = r.returncode == 0
    fail += not ok
    print(f"  {'ok ' if ok else 'FAIL'}  {s:26s} {time.time()-t0:5.2f}s")
    if not ok:
        print("        " + r.stderr.strip().splitlines()[-1])
print(f"\n{len(scripts)-fail} of {len(scripts)} completed.")
print("Run any script on its own to see its output in full.")
sys.exit(1 if fail else 0)
