"""
Bloch-sphere animation for QWeb Research, article "What a Qubit Actually Is".

Physics (exact, not illustrative):

  Phase 1  A single qubit is prepared: Ry(theta) takes |0> (north pole) to |+> (+x).
           The Bloch vector keeps length 1 throughout.

  Phase 2  A second qubit joins, also in |+>. Product state, both vectors length 1.

  Phase 3  A ZZ interaction acts:  U = exp(-i (alpha/2) Z (x) Z)  on |+>|+>.
           The reduced state of each qubit is

               rho_A = [[1/2, cos(alpha)/2], [cos(alpha)/2, 1/2]]

           so r_x = cos(alpha), r_y = r_z = 0, and the eigenvalues are
           (1 +/- cos alpha)/2.  As alpha runs 0 -> pi/2 both Bloch vectors
           shrink along +x to the origin and S rises from 0 to exactly 1 ebit.

  Phase 4  Hold at the centre: locally maximally mixed, S = 1.

Palette is the QWeb article palette.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrow
from matplotlib.animation import FuncAnimation, PillowWriter

# ---------------------------------------------------------------- palette
INK   = "#141821"
SOFT  = "#3d4452"
RULE  = "#d9d4c7"
RUST  = "#b5532a"
BLUE  = "#2a5d8f"
PANEL = "#f4f6f9"
BG    = "#ffffff"

# ---------------------------------------------------------------- camera
ELEV = np.deg2rad(18.0)
AZIM = np.deg2rad(32.0)


def project(v):
    """Orthographic projection of a 3-vector. Returns (sx, sy, depth)."""
    x, y, z = v
    horiz = x * np.cos(AZIM) + y * np.sin(AZIM)
    sx = -x * np.sin(AZIM) + y * np.cos(AZIM)
    sy = -horiz * np.sin(ELEV) + z * np.cos(ELEV)
    depth = horiz * np.cos(ELEV) + z * np.sin(ELEV)
    return sx, sy, depth


# ---------------------------------------------------------------- physics
def entropy_from_alpha(alpha):
    """von Neumann entropy in bits of the reduced state after exp(-i a/2 ZZ) on |+>|+>."""
    c = np.cos(alpha)
    lam = np.array([(1.0 + c) / 2.0, (1.0 - c) / 2.0])
    lam = lam[lam > 1e-12]
    return float(-np.sum(lam * np.log2(lam)))


# ---------------------------------------------------------------- timing
# The sequence runs forward and then all the way back, so the loop closes on
# itself and the reverse leg makes its own point: every step is unitary.
PHASES = [
    ("prepare",   52, 1),   # |0> -> |+>
    ("join",      24, 2),   # qubit B fades in
    ("entangle",  70, 3),   # alpha 0 -> pi/2
    ("hold",      36, 4),   # both spheres empty
    ("unwind",    58, 5),   # alpha pi/2 -> 0
    ("part",      22, 6),   # qubit B fades out
    ("unprepare", 42, 7),   # |+> -> |0>
    ("rest",      14, 8),   # brief rest at the north pole
]
NFRAMES = sum(n for _, n, _ in PHASES)
FPS = 20

PLUS = np.array([1.0, 0.0, 0.0])
ZERO = np.array([0.0, 0.0, 1.0])


def ease(t):
    """Smooth-step easing on [0, 1]."""
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def vec_at_theta(th):
    return np.array([np.sin(th), 0.0, np.cos(th)])


def state_at(i):
    """Return (rA, rB, S, bFade, phase) for frame i."""
    for name, n, phase in PHASES:
        if i < n:
            u = ease(i / max(n - 1, 1))
            if name == "prepare":
                return vec_at_theta(u * np.pi / 2), None, 0.0, 0.0, phase
            if name == "join":
                return PLUS, PLUS.copy(), 0.0, u, phase
            if name == "entangle":
                a = u * np.pi / 2
                r = np.array([np.cos(a), 0.0, 0.0])
                return r, r.copy(), entropy_from_alpha(a), 1.0, phase
            if name == "hold":
                return np.zeros(3), np.zeros(3), 1.0, 1.0, phase
            if name == "unwind":
                a = (1.0 - u) * np.pi / 2
                r = np.array([np.cos(a), 0.0, 0.0])
                return r, r.copy(), entropy_from_alpha(a), 1.0, phase
            if name == "part":
                return PLUS, PLUS.copy(), 0.0, 1.0 - u, phase
            if name == "unprepare":
                return vec_at_theta((1.0 - u) * np.pi / 2), None, 0.0, 0.0, phase
            return ZERO, None, 0.0, 0.0, phase
        i -= n
    return ZERO, None, 0.0, 0.0, 8


# ---------------------------------------------------------------- drawing
R = 1.45
CA = np.array([-2.35, 0.42])
CB = np.array([2.35, 0.42])


def ring(ax, centre, pts3, alpha_scale=1.0, lw=0.9):
    """Draw a great circle, dashed where it lies behind the sphere."""
    proj = np.array([project(p) for p in pts3])
    for k in range(len(pts3) - 1):
        d = 0.5 * (proj[k, 2] + proj[k + 1, 2])
        ax.plot(
            centre[0] + R * proj[k:k + 2, 0],
            centre[1] + R * proj[k:k + 2, 1],
            color=RULE, lw=lw,
            linestyle="-" if d >= 0 else (0, (2, 2.6)),
            alpha=(1.0 if d >= 0 else 0.75) * alpha_scale,
            solid_capstyle="round", zorder=3,
        )


def sphere(ax, centre, r, label, fade=1.0):
    if fade <= 0.01:
        return
    ax.add_patch(Circle(centre, R, facecolor=PANEL, edgecolor=RULE,
                        lw=1.2, alpha=fade, zorder=2))

    t = np.linspace(0, 2 * np.pi, 121)
    ring(ax, centre, np.stack([np.cos(t), np.sin(t), np.zeros_like(t)], 1), fade)        # equator
    ring(ax, centre, np.stack([np.sin(t), np.zeros_like(t), np.cos(t)], 1), fade, 0.75)  # meridian

    # polar axis
    top, bot = project((0, 0, 1)), project((0, 0, -1))
    ax.plot([centre[0] + R * top[0], centre[0] + R * bot[0]],
            [centre[1] + R * top[1], centre[1] + R * bot[1]],
            color=RULE, lw=0.9, alpha=fade, zorder=3)
    ax.text(centre[0] + R * top[0], centre[1] + R * top[1] + 0.20, "|0⟩",
            ha="center", va="bottom", color=SOFT, fontsize=9.5, alpha=fade, zorder=6)
    ax.text(centre[0] + R * bot[0], centre[1] + R * bot[1] - 0.20, "|1⟩",
            ha="center", va="top", color=SOFT, fontsize=9.5, alpha=fade, zorder=6)

    # Bloch vector
    n = float(np.linalg.norm(r))
    if n > 1e-3:
        sx, sy, _ = project(r)
        ax.add_patch(FancyArrow(centre[0], centre[1], R * sx, R * sy,
                                width=0.028, head_width=0.16, head_length=0.20,
                                length_includes_head=True, color=BLUE,
                                alpha=fade, zorder=7))
    else:
        ax.add_patch(Circle(centre, 0.085, facecolor=RUST, edgecolor="none",
                            alpha=fade, zorder=7))

    ax.text(centre[0], centre[1] - R - 0.46, label, ha="center", va="top",
            color=INK, fontsize=11.5, alpha=fade, zorder=6)
    ax.text(centre[0], centre[1] - R - 0.76, f"|r| = {n:0.2f}", ha="center", va="top",
            color=SOFT if n > 1e-3 else RUST, fontsize=10, alpha=fade, zorder=6,
            family="monospace")


CAPTIONS = {
    1: ("One qubit, being prepared",
        "A rotation takes |0⟩ to |+⟩. The arrow keeps its full length: this picture says everything there is to say."),
    2: ("A second qubit, still separate",
        "A product state. Each sphere describes its own qubit completely, and nothing is shared."),
    3: ("A ZZ interaction switches on",
        "exp(−iα/2 · Z⊗Z) acting on |+⟩|+⟩. Each arrow shortens to cos α as the correlation builds."),
    4: ("Both spheres are empty. Nothing was lost.",
        "Each qubit is now maximally mixed. All four Bell states look exactly like this: the information is in the correlation."),
    5: ("The same interaction, running backwards",
        "exp(+iα/2 · Z⊗Z). The arrows grow back and S returns to zero — the entanglement is undone as exactly as it was made."),
    6: ("Separate again",
        "A product state once more. Everything that was in the correlation is back inside the two spheres."),
    7: ("And back to where it started",
        "The rotation of the first step, reversed."),
    8: ("Nothing here was a measurement",
        "Every step was unitary, and every step could be undone. Measurement is the one operation in the story that cannot."),
}


def draw(ax, i):
    ax.clear()
    ax.set_xlim(-5.25, 5.25)
    ax.set_ylim(-2.95, 2.55)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_facecolor(BG)

    rA, rB, S, fade, phase = state_at(i)

    # correlation cord between the spheres
    if S > 1e-3:
        xs = np.linspace(CA[0] + R + 0.08, CB[0] - R - 0.08, 100)
        mid = 0.5 * (CA[0] + CB[0])
        sag = 0.30 * S * np.cos(np.pi * (xs - mid) / (xs[-1] - xs[0]))
        ax.plot(xs, CA[1] - 0.05 - sag, color=RUST, lw=1.0 + 4.6 * S,
                alpha=0.30 + 0.70 * S, solid_capstyle="round", zorder=1)

    sphere(ax, CA, rA, "qubit A", 1.0)
    if rB is not None:
        sphere(ax, CB, rB, "qubit B", fade)

    # entropy meter
    bx, by, bw, bh = -2.3, -2.26, 4.6, 0.17
    ax.add_patch(plt.Rectangle((bx, by), bw, bh, facecolor=PANEL,
                               edgecolor=RULE, lw=0.9, zorder=4))
    if S > 1e-4:
        ax.add_patch(plt.Rectangle((bx, by), bw * S, bh, facecolor=RUST,
                                   edgecolor="none", zorder=5))
    ax.text(bx - 0.18, by + bh / 2, "entanglement entropy", ha="right", va="center",
            color=SOFT, fontsize=9.5, zorder=5)
    ax.text(bx + bw + 0.18, by + bh / 2, f"S = {S:0.2f}", ha="left", va="center",
            color=RUST if S > 0.01 else SOFT, fontsize=10, family="monospace", zorder=5)

    head, sub = CAPTIONS[phase]
    ax.text(0, 2.26, head, ha="center", va="center", color=INK, fontsize=13.5, zorder=6)
    ax.text(0, -2.68, sub, ha="center", va="center", color=SOFT, fontsize=9.8, zorder=6)
    ax.text(5.22, -2.90, "QWeb © Research", ha="right", va="bottom",
            color=RULE, fontsize=8.5, zorder=6)


def build(outdir):
    fig, ax = plt.subplots(figsize=(10.0, 5.6), dpi=84)
    fig.patch.set_facecolor(BG)
    fig.subplots_adjust(0, 0, 1, 1)

    anim = FuncAnimation(fig, lambda i: draw(ax, i), frames=NFRAMES, interval=1000 / FPS)
    anim.save(f"{outdir}/qubit_bloch.gif", writer=PillowWriter(fps=FPS))

    p = {n: sum(k for _, k, _ in PHASES[:j]) for j, (n, _, _) in enumerate(PHASES)}
    for name, idx in [("1_prepared", p["join"] - 1),
                      ("2_separate", p["entangle"] - 1),
                      ("3_halfway", p["entangle"] + 35),
                      ("4_entangled", p["hold"] + 20),
                      ("5_unwinding", p["unwind"] + 29)]:
        draw(ax, idx)
        fig.savefig(f"{outdir}/qubit_bloch_{name}.svg", format="svg", facecolor=BG)
        fig.savefig(f"{outdir}/qubit_bloch_{name}.png", dpi=170, facecolor=BG)
    plt.close(fig)


if __name__ == "__main__":
    import sys, os
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "out")
    os.makedirs(out, exist_ok=True)
    build(out)
    print(f"{NFRAMES} frames at {FPS} fps "
          f"({NFRAMES / FPS:.1f} s) written to {out}")
