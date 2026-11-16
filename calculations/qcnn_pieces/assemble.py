"""Assemble the verified pieces into one module file for the repository.

Mechanical on purpose. The pieces have each been checked against something
slower; retyping them into one file by hand would put that behind a step that
nothing checks. This concatenates them, strips the cross-imports that only
exist because they were separate files, and leaves every line of the bodies
untouched. The assembled file is then re-run against the same gates: if they
still pass, the assembly is right.

fast.py is left out. It was the complex batched path, the stepping stone on
the way to real.py; real.py was verified against the reference in qcnn.py
directly, so fast.py carries nothing the repository needs.

qcnn.train and qcnn.accuracy are left out: the study trains through
trainer.train, and the reference's own trainer would only collide with it.
What is kept from qcnn.py is build, forward, expect_z, grad and the gate
application -- the slow reference the fast path is checked against, which has
to ship or the check cannot be repeated by anyone else.
"""
import ast, pathlib, re

HEADER = '''"""Everything behind qcnn_bodyness.py: states, features, circuit, arms, verdicts.

A module, not a script. qcnn_bodyness.py is the script.

Assembled from seven checked pieces. The layers, and what each was checked
against, are in designs/design_qcnn_bodyness_EN_addendum_3.md section A3.6.
The slow reference is included deliberately: the fast path is only as
trustworthy as the check against it, and that check cannot be repeated from a
file that does not contain both sides.

  primitives      Pauli strings, the TFIM Hamiltonian, exact ground states,
                  cat states, reduced density matrices, the two feature
                  routes
  reference       the circuit and its adjoint gradient, written for clarity,
                  one start at a time, complex arithmetic
  fast path       the same thing in real arithmetic, batched over starts,
                  with the gradient contracted into inner products rather
                  than materialised; 2.7x to 4.0x faster and verified against
                  the reference to 1.3e-15
  datasets        D1 (transverse-field Ising ground states, labelled by
                  phase) and D2 (R1 version 2 of addendum 2: the sign of a
                  cat state under local RY)
  arms            the QCNN trainer and the classical bodyness-k classifiers
  verdicts        the resolution rule of section 6 and the four verdicts,
                  which never include "equivalent"
"""
'''

# The modules that only exist because the pieces were separate files. Their
# imports are dropped; every other import is carried over verbatim.
LOCAL = {"prim", "qcnn", "real", "fast", "data", "trainer", "classical",
         "verdict", "qcnn_bodyness_core"}

PIECES = [
    ("prim.py", "primitives: states, Hamiltonians, features", ()),
    ("qcnn.py", "the slow reference circuit and its adjoint gradient",
     ("train", "accuracy")),
    ("real.py", "the fast path: real arithmetic, batched, contracted gradient", ()),
    ("data.py", "the two datasets", ()),
    ("trainer.py", "the QCNN arm", ()),
    ("classical.py", "the classical arms", ()),
    ("verdict.py", "the resolution rule and the four verdicts", ()),
]

HERE = pathlib.Path(__file__).parent
out = [HEADER]
imports = []        # collected from the sources, never typed here


def _is_local(node):
    """True for an import of one of the pieces being assembled."""
    if isinstance(node, ast.ImportFrom):
        return (node.module or "").split(".")[0] in LOCAL
    return any(a.name.split(".")[0] in LOCAL for a in node.names)


for fname, title, drop in PIECES:
    src = pathlib.Path(HERE / fname).read_text()
    tree = ast.parse(src)
    lines = src.splitlines(keepends=True)
    keep = []
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            # Hoisted, not dropped. An earlier version of this script carried
            # a hand-written import list in HEADER and silently lost two of
            # them; the study then died on its first draw with a NameError
            # that every gate had passed. Collected from the sources now, so
            # the list cannot drift from what the bodies use.
            if not _is_local(node):
                imports.append((node, "".join(
                    lines[node.lineno - 1:node.end_lineno]).rstrip()))
            continue
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) \
                and isinstance(node.value.value, str):
            continue                                  # the module docstring
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in drop:
            continue
        a = node.lineno - 1
        for d in getattr(node, "decorator_list", []):
            a = min(a, d.lineno - 1)
        keep.append("".join(lines[a:node.end_lineno]))
    body = "\n\n".join(s.rstrip() for s in keep)
    # these only existed because the pieces were separate files
    # Only the five names that actually appear as cross-references, so a
    # word like "real" inside a sentence is never touched.
    for ref_ in ("prim.cat_ry", "prim.ground", "prim.h_tfim", "real.grads"):
        body = body.replace(ref_, ref_.split(".", 1)[1])
    out.append(f"\n\n# {'=' * 74}\n# {title}\n# {'=' * 74}\n\n{body}\n")

# One line per module, names merged, order of first appearance kept. Two
# pieces importing different names from itertools must not produce two
# itertools lines in a file meant to be read.
plain, froms = [], {}
for node, line in imports:
    if isinstance(node, ast.ImportFrom) and not any(a.asname for a in node.names):
        froms.setdefault(node.module, [])
        for a in node.names:
            if a.name not in froms[node.module]:
                froms[node.module].append(a.name)
    elif line not in plain:
        plain.append(line)

uniq = list(plain) + [f"from {m} import {', '.join(n)}" for m, n in froms.items()]
out.insert(1, "\n".join(uniq) + "\n")

text = "\n".join(out)
target = HERE / "qcnn_bodyness_core.py"
target.write_text(text)
ast.parse(text)                                       # it must at least parse
print(f"{target.name}: {len(text.splitlines())} lines, parses, "
      f"{len(uniq)} imports carried over from the sources")

# No name may be defined twice: a silent redefinition would replace a checked
# function with another checked function and no gate would notice.
seen = {}
for node in ast.parse(text).body:
    nm = None
    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
        nm = node.name
    elif isinstance(node, ast.Assign):
        for t in node.targets:
            if isinstance(t, ast.Name):
                nm = t.id
    if nm:
        if nm in seen:
            raise SystemExit(f"collision: {nm} defined twice")
        seen[nm] = True
print(f"{len(seen)} top-level names, none defined twice")


# The script, rewritten against the single module.
# The input is qcnn_bodyness_pieces.py and not qcnn_bodyness.py.
# The repository commits this script's OUTPUT under the latter name,
# so an input of that name would be a second, different file sharing
# it -- and an upload into the wrong directory would silently replace
# the committed one. No two files in this repository share a name.
script = pathlib.Path(HERE / "qcnn_bodyness_pieces.py").read_text()
script = script.replace("""import qcnn as ref
import data, trainer, classical, verdict""", "import qcnn_bodyness_core as core")
for pref in ("data.prim.", "classical.", "verdict.", "trainer.", "data.", "ref."):
    script = script.replace(pref, "core.")
pathlib.Path(HERE / "qcnn_bodyness_single.py").write_text(script)
import ast as _ast
_ast.parse(script)
left = sorted(set(re.findall(r"\b(?:prim|data|real|ref|fast|verdict|classical|trainer)\.[a-zA-Z_]+", script)))
print(f"qcnn_bodyness_single.py: {len(script.splitlines())} lines, parses; "
      f"remaining module references: {left or 'none'}")


# Undefined names in the assembled files are fatal. Parsing does not find
# them -- a missing import parses perfectly and raises NameError at the line
# that uses it, which can be hours into a run. This is the check that the
# hand-written import list did not have.
import subprocess, sys
r = subprocess.run([sys.executable, "-m", "pyflakes",
                    "qcnn_bodyness_core.py", "qcnn_bodyness_single.py"],
                   cwd=HERE, capture_output=True, text=True)
# If pyflakes is not installed this returns non-zero with "No module named
# pyflakes" and no line matching "undefined name", so the filter below comes
# up empty and the assembly would report a clean check having performed
# none. Found on 16 November by the assembly check, before either file was
# committed. A gate that cannot fail is worse than no gate, because it is
# believed.
if "No module named pyflakes" in r.stderr:
    raise SystemExit("pyflakes is not installed; the undefined-name check "
                     "cannot run, and this is the check that the 15 November "
                     "failure needed. Install it: pip install pyflakes")
undef = [ln for ln in (r.stdout + r.stderr).splitlines()
         if "undefined name" in ln]
if undef:
    for ln in undef:
        print("  " + ln)
    raise SystemExit("assembly has undefined names -- not written out as usable")
print("no undefined names in either assembled file")
