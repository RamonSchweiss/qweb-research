"""Does qcnn_bodyness_core.py still come out of its seven source pieces?

The module committed next to this file is assembled, not written. On 15
November the assembly dropped two imports, the module parsed perfectly, five
gates passed, and all five overnight chunks died at draw 0 hours later. That
failure is the reason this check exists: an assembled file that nobody
re-assembles is a file whose sources have stopped meaning anything.

WHAT IT DOES.  Copies qcnn_pieces/ into a temporary directory, runs the
assembly THERE, and compares both of its outputs byte for byte against the
two committed files.

  There are two, and the names are a trap worth stating. assemble.py reads
  qcnn_pieces/qcnn_bodyness.py -- the version that imports the seven pieces
  -- and writes qcnn_bodyness_single.py, the version that imports the one
  assembled module. That output is what is committed one directory up, as
  calculations/qcnn_bodyness.py. So the repository holds two different files
  with the same base name in two directories, and feeding the wrong one to
  the assembly produces a check that passes without checking anything: every
  replacement it performs is already done, so the output equals the input.
  That is how the first version of this file behaved, on 16 November, before
  either was committed.

  It never writes into this directory. assemble.py writes two files whose
  names are the names of committed files, so running it here would overwrite
  them -- and run_all.py executes everything it finds in calculations/. That
  is why assemble.py lives in qcnn_pieces/ where the collection run's glob,
  which is not recursive, cannot reach it, and why this check runs the
  assembly somewhere else entirely.

WHAT A FAILURE MEANS.  Not that the module is wrong. It means the module and
the pieces have drifted, and that one of the two is no longer the thing the
design notes describe. Which one is for a human to decide; the check only
reports that the question has arisen.

LINE ENDINGS ARE NOT DRIFT.  git checks text files out with the line endings
of the platform, and Python writes them the same way, so on Windows the
assembly produces CRLF while a repository stored with LF has LF -- a
difference of exactly one byte per line and of nothing else. Comparing raw
bytes called that drift and reported a mismatch on a tree where nothing had
drifted, on 16 November, the first time this ran on Windows. The comparison
is therefore made on content with line endings normalised, and a difference
in line endings alone is reported as what it is.

Needs pyflakes, which assemble.py uses to reject undefined names. If it is
missing this says so and reports nothing, rather than passing.
"""
import pathlib, shutil, subprocess, sys, tempfile, time

HERE = pathlib.Path(__file__).parent
PIECES_DIR = HERE / "qcnn_pieces"
PIECES = ["prim.py", "qcnn.py", "real.py", "data.py", "trainer.py",
          "classical.py", "verdict.py", "qcnn_bodyness_pieces.py"]
# built in the temp directory  ->  committed next to this file
OUTPUTS = [("qcnn_bodyness_core.py", "qcnn_bodyness_core.py"),
           ("qcnn_bodyness_single.py", "qcnn_bodyness.py")]


def main():
    t0 = time.time()
    print(__doc__.strip().splitlines()[0])
    print()

    missing = [f for f in PIECES + ["assemble.py"]
               if not (PIECES_DIR / f).exists()]
    missing += [c for _, c in OUTPUTS if not (HERE / c).exists()]
    if missing:
        print(f"  sources not present: {', '.join(missing)}")
        print("  nothing to check")
        return 0

    # pyflakes is what makes assemble.py refuse an undefined name. Without it
    # the assembly would report success having checked nothing, so the
    # absence is reported here rather than discovered as a clean run.
    probe = subprocess.run([sys.executable, "-m", "pyflakes", "--version"],
                           capture_output=True, text=True)
    if probe.returncode != 0:
        print("  pyflakes is not installed, and assemble.py needs it to")
        print("  reject undefined names. Install it with")
        print("      pip install pyflakes")
        print("  Reporting nothing rather than a pass that checked nothing.")
        return 0

    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td)
        for f in PIECES + ["assemble.py"]:
            shutil.copy2(PIECES_DIR / f, tmp / f)

        r = subprocess.run([sys.executable, str(tmp / "assemble.py")],
                           cwd=tmp, capture_output=True, text=True)
        for line in r.stdout.strip().splitlines():
            print("  " + line)
        if r.returncode != 0:
            print("  " + (r.stderr.strip().splitlines()
                          or ["assembly failed"])[-1])
            print(f"\n  ASSEMBLY FAILED  [{time.time()-t0:.1f}s]")
            return 1

        print()
        bad = 0
        for built_name, committed_name in OUTPUTS:
            built, committed = tmp / built_name, HERE / committed_name
            if not built.exists():
                print(f"  {built_name} was not produced at all")
                bad = 1
                continue
            raw_b, raw_c = built.read_bytes(), committed.read_bytes()
            norm = lambda s: s.replace(b"\r\n", b"\n")
            if raw_b == raw_c:
                print(f"  {committed_name:<24} re-assembles byte for byte "
                      f"({len(raw_c)} bytes)")
                continue
            if norm(raw_b) == norm(raw_c):
                which = "CRLF" if b"\r\n" in raw_c else "LF"
                print(f"  {committed_name:<24} re-assembles identically "
                      f"({len(norm(raw_c))} bytes, line endings normalised)")
                print(f"    the checked-out file has {which} and the assembly "
                      f"produced the other;")
                print(f"    that is how git checked it out, not a change to "
                      f"the content")
                continue
            bad = 1
            print(f"  {committed_name:<24} DIFFERS from its sources")
            print(f"    committed  {len(norm(raw_c))} bytes")
            print(f"    assembled  {len(norm(raw_b))} bytes   "
                  f"(both counted without line endings)")
            a = norm(raw_c).decode().splitlines()
            b = norm(raw_b).decode().splitlines()
            for i, (x, y) in enumerate(zip(a, b), 1):
                if x != y:
                    print(f"    first difference at line {i}:")
                    print(f"      committed: {x[:68]}")
                    print(f"      assembled: {y[:68]}")
                    break
            else:
                if len(a) != len(b):
                    print(f"    same prefix, different length: "
                          f"{len(a)} against {len(b)} lines")

        if bad:
            print("\n  A committed file and its pieces have drifted. One of")
            print("  them is no longer what the design notes describe; which")
            print("  one is a decision for a person, not for this check.")
            print(f"\n  MISMATCH  [{time.time()-t0:.1f}s]")
            return 1
        print(f"\n  ok  [{time.time()-t0:.1f}s]")
        return 0


if __name__ == "__main__":
    sys.exit(main())
