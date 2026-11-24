"""The four figures of "What an Architecture Pays For".

Emits, into figures/out/ as the other scripts here do:

    d_price_balances.svg    section 02 — the ledger as three balances
    d_horizon_rounds.svg    section 06 — the horizon in gate rounds, and the
                            distance figures that were withdrawn
    d_degeneracy_drift.svg  section 09 — optimal in cost, drifting in choice,
                            in two separate studies
    d_two_currencies.svg    section 12 — two execution models, two currencies

Run with --dark for the palette of the teaser images; the default is the light
palette for figures sitting inside the article body.

Every number is quoted from a published QWeb article or from a committed store.
Nothing here is computed and nothing is interpolated — in particular
d_degeneracy_drift.svg plots two studies as two marker sets and deliberately
does not join them into one curve, because whether the mechanism is shared is
not established.

Sources of the numbers:

  d_price_balances      "How Entanglement Lowers the Price of Agreement",
                        "The Mermin-Peres Magic Square Game"
  d_horizon_rounds      "What the Computation Knows About Its Own Organisation";
                        the withdrawn distances are listed in section 06 of the
                        present article
  d_degeneracy_drift    "What the Partitioner Stops Solving" addendum 1 (5 of 21
                        at n = 10, 12 of 20 at n = 26) and
                        calculations/hypercube_global_qubits_scores.json
                        (8, 6, 10 of 21 at n = 12; 8, 3, 8 at n = 16;
                        4, 3, 3 at n = 20, counted as the complement)
  d_two_currencies      sections 11 and 12 of the present article

Ramon Schweiss, QWeb (c) Research, 24 November 2026.
"""
import os
import sys

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")

DARK = "--dark" in sys.argv
if DARK:
    BG, INK, SOFT, RULE, ACCENT = "#0d1b33", "#ffffff", "#8fa8c8", "#3f5a80", "#f0a06a"
else:
    BG, INK, SOFT, RULE, ACCENT = "#ffffff", "#16294a", "#5b7093", "#c3d0e2", "#c2642a"

FONT = 'font-family="DejaVu Serif"'


def head(w, h, alt):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'{FONT} role="img" aria-label="{alt}">'
            f'<rect width="{w}" height="{h}" fill="{BG}"/>')


def txt(x, y, s, size=14, fill=None, anchor="start", weight="normal",
        style="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" '
            f'fill="{fill or INK}" text-anchor="{anchor}" '
            f'font-weight="{weight}" font-style="{style}">{s}</text>')


def write(name, body):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(body + "</svg>\n")
    print("wrote", path)


# ----------------------------------------------------- A1  the three balances
def price_balances():
    W, H = 880, 330
    rows = [
        ("Teleportation", ["1 ebit", "2 classical bits"], ["1 qubit"]),
        ("Superdense coding", ["1 ebit", "1 qubit"], ["2 classical bits"]),
        ("Magic square", ["1 ebit"], ["agreement", "nothing sent"]),
    ]
    p = [head(W, H, "Three exact balances: teleportation costs one ebit and two "
                    "classical bits for one qubit; superdense coding one ebit "
                    "and one qubit for two classical bits; the magic square "
                    "buys agreement with no communication at all.")]
    p.append(txt(40, 44, "The price of agreement, as a ledger", 19,
                 weight="bold"))
    p.append(txt(40, 68, "Exact balances, not analogies. The classical bits are "
                         "the irreducible residue of a measurement.", 13, SOFT))
    y = 110
    for name, left, right in rows:
        p.append(txt(40, y + 4, name, 15, weight="bold"))
        xs = 250
        for i, item in enumerate(left):
            p.append(f'<rect x="{xs}" y="{y - 15}" width="132" height="26" '
                     f'rx="4" fill="none" stroke="{RULE}" stroke-width="1.4"/>')
            p.append(txt(xs + 66, y + 3, item, 13, anchor="middle"))
            xs += 142
            if i < len(left) - 1:
                p.append(txt(xs - 21, y + 4, "+", 15, SOFT, anchor="middle"))
        p.append(txt(xs + 16, y + 4, "&#8594;", 19, ACCENT, anchor="middle"))
        xr = xs + 36
        for i, item in enumerate(right):
            fill = ACCENT if i == 0 else SOFT
            p.append(txt(xr, y + 3, item, 13, fill,
                         style="normal" if i == 0 else "italic"))
            xr += 16 + 8 * len(item)
        y += 62
    p.append(f'<line x1="40" y1="{y - 24}" x2="{W - 40}" y2="{y - 24}" '
             f'stroke="{RULE}" stroke-width="1.2"/>')
    p.append(txt(40, y + 2, "Entanglement lowers the price of agreement — to "
                            "zero where no information flows. It does not "
                            "abolish causality.", 13, SOFT, style="italic"))
    write("d_price_balances.svg", "".join(p))


# ------------------------------------------- A2  the horizon, in gate rounds
def horizon_rounds():
    W, H = 880, 330
    p = [head(W, H, "The planning horizon spans a factor of seventeen, from "
                    "about 8 to about 110 concurrent gate rounds, across "
                    "circuits with the same qubit and edge count. Five distance "
                    "figures published earlier have been withdrawn.")]
    p.append(txt(40, 44, "The horizon is measured in gate rounds", 19,
                 weight="bold"))
    p.append(txt(40, 68, "Across graphs with the same qubit count and the same "
                         "edge count.", 13, SOFT))

    x0, x1, yb = 90, W - 120, 150
    lo, hi = 8, 110
    def sx(v):
        import math
        a, b = math.log10(6), math.log10(140)
        return x0 + (math.log10(v) - a) / (b - a) * (x1 - x0)

    p.append(f'<line x1="{x0}" y1="{yb}" x2="{x1}" y2="{yb}" '
             f'stroke="{RULE}" stroke-width="1.4"/>')
    for v in (10, 20, 50, 100):
        p.append(f'<line x1="{sx(v):.1f}" y1="{yb - 5}" x2="{sx(v):.1f}" '
                 f'y2="{yb + 5}" stroke="{RULE}" stroke-width="1.2"/>')
        p.append(txt(sx(v), yb + 24, str(v), 12, SOFT, anchor="middle"))
    p.append(txt((x0 + x1) / 2, yb + 48, "concurrent gate rounds", 12, SOFT,
                 anchor="middle"))
    p.append(f'<line x1="{sx(lo):.1f}" y1="{yb - 30}" x2="{sx(hi):.1f}" '
             f'y2="{yb - 30}" stroke="{ACCENT}" stroke-width="5" '
             f'stroke-linecap="round"/>')
    for v in (lo, hi):
        p.append(f'<circle cx="{sx(v):.1f}" cy="{yb - 30}" r="7" fill="{BG}" '
                 f'stroke="{ACCENT}" stroke-width="3"/>')
    p.append(txt(sx(lo), yb - 48, "about 8", 13, anchor="middle",
                 weight="bold"))
    p.append(txt(sx(hi), yb - 48, "about 110", 13, anchor="middle",
                 weight="bold"))
    p.append(txt((sx(lo) + sx(hi)) / 2, yb - 8, "a factor of 17", 13, ACCENT,
                 anchor="middle", style="italic"))

    p.append(f'<line x1="40" y1="236" x2="{W - 40}" y2="236" '
             f'stroke="{RULE}" stroke-width="1.2"/>')
    p.append(txt(40, 262, "Withdrawn: every conversion of this horizon into a "
                          "distance", 14, weight="bold"))
    xs = 40
    for s in ("70 m", "a few hundred m", "1 km", "1.8 km", "2 km"):
        wd = 12 + 7 * len(s)
        p.append(f'<rect x="{xs}" y="276" width="{wd}" height="26" rx="4" '
                 f'fill="none" stroke="{RULE}" stroke-width="1.2"/>')
        p.append(txt(xs + wd / 2, 294, s, 12.5, SOFT, anchor="middle"))
        p.append(f'<line x1="{xs + 6}" y1="289" x2="{xs + wd - 6}" y2="289" '
                 f'stroke="{SOFT}" stroke-width="1.4"/>')
        xs += wd + 12
    p.append(txt(xs + 10, 294, "the horizon survived; the conversion did not",
                 12.5, SOFT, style="italic"))
    write("d_horizon_rounds.svg", "".join(p))


# ------------------------------- A3  optimal in cost, drifting in choice
def degeneracy_drift():
    W, H = 880, 414
    # share of instances in which the rule chose a DIFFERENT member
    kl = [(10, 5 / 21), (26, 12 / 20)]
    hc = [(12, 1 - (8 + 6 + 10) / 63), (16, 1 - (8 + 3 + 8) / 63),
          (20, 1 - (4 + 3 + 3) / 63)]
    p = [head(W, H, "Two separate studies, each showing a rule that attains the "
                    "optimal cost while choosing a different member of the "
                    "optimal set more often as the register grows. The two "
                    "marker sets are not joined, because a shared mechanism is "
                    "not established.")]
    p.append(txt(40, 44, "Optimal in cost, drifting in choice", 19,
                 weight="bold"))
    p.append(txt(40, 68, "Share of instances in which the rule picked a "
                         "different member of the optimal set.", 13, SOFT))
    L, R, T, B = 90, W - 220, 100, 296

    def sx(n):
        return L + (n - 8) / (28 - 8) * (R - L)

    def sy(v):
        return B - v * (B - T)

    p.append(f'<line x1="{L}" y1="{B}" x2="{R}" y2="{B}" stroke="{RULE}" '
             f'stroke-width="1.4"/>')
    p.append(f'<line x1="{L}" y1="{T}" x2="{L}" y2="{B}" stroke="{RULE}" '
             f'stroke-width="1.4"/>')
    for n in (10, 14, 18, 22, 26):
        p.append(txt(sx(n), B + 22, str(n), 12, SOFT, anchor="middle"))
    p.append(txt((L + R) / 2, B + 46, "qubits", 12, SOFT, anchor="middle"))
    for v in (0, 0.25, 0.5, 0.75, 1.0):
        p.append(f'<line x1="{L - 5}" y1="{sy(v):.1f}" x2="{R}" '
                 f'y2="{sy(v):.1f}" stroke="{RULE}" stroke-width="0.8" '
                 f'opacity="0.55"/>')
        p.append(txt(L - 12, sy(v) + 4, f"{int(v*100)} %", 12, SOFT,
                     anchor="end"))

    for (a, b) in ((kl[0], kl[1]),):
        p.append(f'<line x1="{sx(a[0]):.1f}" y1="{sy(a[1]):.1f}" '
                 f'x2="{sx(b[0]):.1f}" y2="{sy(b[1]):.1f}" stroke="{INK}" '
                 f'stroke-width="1.6" stroke-dasharray="3,5" opacity="0.5"/>')
    for i in range(len(hc) - 1):
        a, b = hc[i], hc[i + 1]
        p.append(f'<line x1="{sx(a[0]):.1f}" y1="{sy(a[1]):.1f}" '
                 f'x2="{sx(b[0]):.1f}" y2="{sy(b[1]):.1f}" stroke="{ACCENT}" '
                 f'stroke-width="1.6" stroke-dasharray="3,5" opacity="0.6"/>')
    for n, v in kl:
        p.append(f'<rect x="{sx(n) - 6:.1f}" y="{sy(v) - 6:.1f}" width="12" '
                 f'height="12" fill="{BG}" stroke="{INK}" stroke-width="2.2"/>')
    for n, v in hc:
        p.append(f'<circle cx="{sx(n):.1f}" cy="{sy(v):.1f}" r="6.5" '
                 f'fill="{BG}" stroke="{ACCENT}" stroke-width="2.6"/>')

    lx = R + 24
    p.append(f'<rect x="{lx}" y="{T + 6}" width="12" height="12" fill="{BG}" '
             f'stroke="{INK}" stroke-width="2.2"/>')
    p.append(txt(lx + 20, T + 17, "Kernighan&#8211;Lin,", 12.5))
    p.append(txt(lx + 20, T + 33, "partitioning study", 12.5, SOFT))
    p.append(f'<circle cx="{lx + 6}" cy="{T + 62}" r="6.5" fill="{BG}" '
             f'stroke="{ACCENT}" stroke-width="2.6"/>')
    p.append(txt(lx + 20, T + 67, "information arm,", 12.5))
    p.append(txt(lx + 20, T + 83, "hypercube study", 12.5, SOFT))
    p.append(txt(lx, T + 122, "Two studies.", 12.5, ACCENT, weight="bold"))
    p.append(txt(lx, T + 140, "Not one curve:", 12.5, SOFT))
    p.append(txt(lx, T + 156, "a shared mechanism", 12.5, SOFT))
    p.append(txt(lx, T + 172, "is not established.", 12.5, SOFT))

    p.append(txt(40, 378, "Which member of an optimal set a rule picks is what "
                          "a scheduler pays migration for — the one line in "
                          "the ledger", 13, SOFT, style="italic"))
    p.append(txt(40, 398, "that still has no number against it.", 13, SOFT,
                 style="italic"))
    write("d_degeneracy_drift.svg", "".join(p))


# ----------------------------------------------- A4  the two currencies
def two_currencies():
    W, H = 880, 340
    cols = [
        ("Distributed", [
            ("what is paid", "ebits, classical bits,"),
            ("", "remote gates"),
            ("the object that decides", "the interaction graph"),
            ("does the state have a say", "yes"),
        ]),
        ("Amplitude-distributed", [
            ("what is paid", "amplitudes moved across"),
            ("", "node boundaries"),
            ("the object that decides", "the degree sequence"),
            ("does the state have a say", "no"),
        ]),
    ]
    p = [head(W, H, "Two execution models side by side. The distributed model "
                    "pays in ebits and classical bits, is decided by the "
                    "interaction graph, and the state has a say. The "
                    "amplitude-distributed model pays in amplitude traffic, is "
                    "decided by the degree sequence, and the state has none.")]
    p.append(txt(40, 44, "Two models, two currencies", 19, weight="bold"))
    p.append(txt(40, 68, "The same two words — local, global — with opposite "
                         "answers.", 13, SOFT))
    x = [330, 620]
    p.append(f'<line x1="40" y1="92" x2="{W - 40}" y2="92" stroke="{RULE}" '
             f'stroke-width="1.2"/>')
    for i, (name, _) in enumerate(cols):
        p.append(txt(x[i], 116, name, 15, ACCENT if i else INK,
                     weight="bold"))
    y = 152
    labels = ["what is paid", "", "the object that decides",
              "does the state have a say"]
    for r, label in enumerate(labels):
        if label:
            p.append(txt(40, y, label, 13, SOFT))
        for i, (_, rows) in enumerate(cols):
            _, val = rows[r]
            bold = "bold" if r == 3 else "normal"
            p.append(txt(x[i], y, val, 13.5,
                         ACCENT if (r == 3 and i == 1) else INK,
                         weight=bold))
        y += 26 if label == "" else 38
    p.append(f'<line x1="40" y1="282" x2="{W - 40}" y2="282" '
             f'stroke="{RULE}" stroke-width="1.2"/>')
    p.append(txt(40, 308, "Whether entanglement lowers the price is a question "
                          "put to each execution model, in its own currency.",
                 13, SOFT, style="italic"))
    write("d_two_currencies.svg", "".join(p))


if __name__ == "__main__":
    price_balances()
    horizon_rounds()
    degeneracy_drift()
    two_currencies()
