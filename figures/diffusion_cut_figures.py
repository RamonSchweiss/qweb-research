"""
The three figures for "What the Operator Hides From the Partitioner".

Every number here is transcribed from the two measurement scripts and nothing
is recomputed: diffusion_cut_arithmetic.py for figure 1, routed_diffusion_cut.py
for figures 2 and 3. The arrays below are therefore data and not results, and
the comment on each says where it came from. Run with no arguments; writes
three SVGs into figures/out/, which .gitignore excludes - generated output does
not belong in the repository. Pass a directory as the first argument to write
somewhere else.

Needs    : matplotlib.
Runtime  : a second.
"""
import logging
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                   # noqa: E402

# Georgia stays first in the font list below because svg.fonttype is "none":
# the SVG names the family and the reader's browser resolves it, where Georgia
# is present. The machine that renders the file usually has no Georgia and says
# so once per text element, which is noise about a file that is correct.
logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)

# the QWeb palette
INK, SOFT, RULE = "#141821", "#3d4452", "#d9d4c7"
RUST, BLUE, PANEL = "#b5532a", "#2a5d8f", "#f4f6f9"

plt.rcParams.update({
    "font.family": ["Georgia", "DejaVu Serif", "serif"],
    "font.size": 9.5,
    "axes.edgecolor": SOFT,
    "axes.labelcolor": INK,
    "text.color": INK,
    "xtick.color": SOFT,
    "ytick.color": SOFT,
    "axes.linewidth": 0.7,
    "svg.fonttype": "none",
})


def frame(ax):
    """House frame: two spines, a pale horizontal grid, nothing else."""
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", color=RULE, linewidth=0.6, alpha=0.9)
    ax.set_axisbelow(True)
    ax.tick_params(length=3, width=0.7)


# --------------------------------------------------------------- figure 1

def figure_1(path):
    """Crossing fraction of the two decompositions, against data qubits.

    From diffusion_cut_arithmetic.py, sections 1 and 2 of its output. The band
    is P/(2(P-1)) over the sizes shown, which is where a complete interaction
    graph has to sit; both decompositions are plotted against n, the data
    qubits, because that is the parameter they share.
    """
    n = [4, 6, 8, 10, 12]
    vchain = [0.320, 0.163, 0.110, 0.082, 0.066]
    noanc = [0.571, 0.585, 0.565, 0.552, 0.543]

    fig, ax = plt.subplots(figsize=(6.2, 3.5))
    frame(ax)
    ax.axhspan(0.52, 0.60, color=PANEL, zorder=0)
    ax.axhline(0.52, color=RULE, linewidth=0.6)
    ax.axhline(0.60, color=RULE, linewidth=0.6)
    ax.text(12.4, 0.613, "where a complete interaction graph must sit",
            ha="right", va="bottom", fontsize=8.5, color=SOFT)

    ax.plot(n, noanc, "-o", color=BLUE, linewidth=1.6, markersize=4.5,
            label="no ancillae: graph complete at every size")
    ax.plot(n, vchain, "-o", color=RUST, linewidth=1.6, markersize=4.5,
            label="V-chain over n−2 ancillae: a ladder")
    for x, y in zip(n, vchain):
        ax.annotate("8", (x, y), textcoords="offset points", xytext=(0, -13),
                    ha="center", fontsize=8, color=RUST)
    ax.text(3.7, 0.030, "minimum balanced cut, in gates",
            fontsize=8.5, color=RUST)

    ax.set_xlabel("data qubits n")
    ax.set_ylabel("minimum crossing fraction")
    ax.set_xticks(n)
    ax.set_xlim(3.5, 12.5)
    ax.set_ylim(0, 0.68)
    ax.legend(frameon=False, loc="center right", fontsize=8.5,
              handlelength=1.6)
    fig.tight_layout()
    fig.savefig(path, format="svg", transparent=True)
    plt.close(fig)
    return path


# --------------------------------------------------------------- figure 2

def figure_2(path):
    """Routed crossing fraction against the logical minimum, both families.

    From routed_diffusion_cut.py. Only non-degenerate sizes appear: the grid at
    P = 12, 16, 18, 20 and 24, heavy-hex at P = 22 and 24. m is eight divided
    by the routed gate count, so it moves with the routing.
    """
    g_P = [12, 16, 18, 20, 24]
    g_r = [0.172, 0.155, 0.136, 0.120, 0.096]
    g_m = [0.090, 0.067, 0.052, 0.053, 0.043]
    h_P = [22, 24]
    h_r = [0.084, 0.094]
    h_m = [0.035, 0.031]

    fig, ax = plt.subplots(figsize=(6.2, 3.5))
    frame(ax)
    ax.fill_between(g_P, g_m, g_r, color=RUST, alpha=0.10, zorder=1)
    ax.fill_between(h_P, h_m, h_r, color=BLUE, alpha=0.10, zorder=1)

    ax.plot(g_P, g_r, "-o", color=RUST, linewidth=1.6, markersize=4.5,
            label="grid, routed")
    ax.plot(g_P, g_m, "--o", color=RUST, linewidth=1.2, markersize=3.5,
            markerfacecolor="white", label="grid, minimum")
    ax.plot(h_P, h_r, "-s", color=BLUE, linewidth=1.6, markersize=4.5,
            label="heavy-hex, routed")
    ax.plot(h_P, h_m, "--s", color=BLUE, linewidth=1.2, markersize=3.5,
            markerfacecolor="white", label="heavy-hex, minimum")

    ax.text(13.1, 0.118, "the gap is × 2.4 on average,\n"
            "flat across sizes and\nboth families",
            fontsize=8.5, color=SOFT, ha="left", va="center")

    ax.set_xlabel("physical qubits P")
    ax.set_ylabel("minimum crossing fraction")
    ax.set_xticks([12, 16, 18, 20, 22, 24])
    ax.set_ylim(0, 0.20)
    ax.legend(frameon=False, loc="upper right", fontsize=8.5,
              handlelength=1.8, ncol=1)
    fig.tight_layout()
    fig.savefig(path, format="svg", transparent=True)
    plt.close(fig)
    return path


# --------------------------------------------------------------- figure 3

def figure_3(path):
    """Three workloads at P = 24, on both coupling-map families.

    From the contrast table of routed_diffusion_cut.py at P = 24.
    """
    labels = ["community\nQAOA layer", "the diffusion", "regular\nQAOA layer"]
    grid = [0.027, 0.096, 0.111]
    hhex = [0.067, 0.094, 0.112]

    fig, ax = plt.subplots(figsize=(6.2, 3.3))
    frame(ax)
    x = range(len(labels))
    w = 0.34
    ax.bar([i - w / 2 for i in x], grid, w, color=RUST, label="grid 4×6")
    ax.bar([i + w / 2 for i in x], hhex, w, color=BLUE,
           label="heavy-hex, 24 nodes")
    for i, (a, b) in enumerate(zip(grid, hhex)):
        ax.text(i - w / 2, a + 0.003, f"{a:.3f}", ha="center", fontsize=8.5,
                color=RUST)
        ax.text(i + w / 2, b + 0.003, f"{b:.3f}", ha="center", fontsize=8.5,
                color=BLUE)

    ax.annotate("", xy=(1 - w / 2, 0.088), xytext=(1 + w / 2, 0.088),
                arrowprops=dict(arrowstyle="<->", color=SOFT, linewidth=0.7))
    ax.text(1, 0.079, "0.002", ha="center", fontsize=8, color=SOFT)

    ax.set_xticks(list(x))
    ax.set_xticklabels(labels)
    ax.set_ylabel("minimum crossing fraction")
    ax.set_ylim(0, 0.135)
    ax.legend(frameon=False, loc="upper left", fontsize=8.5, handlelength=1.2)
    fig.tight_layout()
    fig.savefig(path, format="svg", transparent=True)
    plt.close(fig)
    return path


def main():
    # "out" beside this file, as qubit_bloch.py already does, so that the
    # generated SVGs land in the directory .gitignore excludes
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "out")
    os.makedirs(out, exist_ok=True)
    for i, fn in enumerate((figure_1, figure_2, figure_3), start=1):
        p = fn(os.path.join(out, f"diffusion_cut_figure_{i}.svg"))
        print("wrote", p)


if __name__ == "__main__":
    main()
