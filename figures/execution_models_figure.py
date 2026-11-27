"""The core thesis of QWeb © Research on one plate, for the front page.

Emits figures/out/d_execution_models.svg. Light palette by default, --dark
renders the same plate in the house teaser palette.

What it draws. The programme's distinctive finding is not that distributed
quantum computing is hard. It is that the price of agreement is an account, and
that WHICH account depends on the execution model - so whether entanglement
lowers that price is a question to put to each model rather than an assumption
to carry into it. Section 12 of "What an Architecture Pays For" establishes
that, and this plate is that section at a glance.

Three columns, and they are deliberately not three equal alternatives:

  One processor. The degenerate case, drawn dimmed. There is no node boundary,
  so there is nothing to pay. It is on the plate because it is the baseline the
  other two are priced against, not because it is a competing architecture.

  Distributed, paying in entanglement. Qubits live on separate processors and
  a remote gate is paid for in shared pairs and classical bits. Teleportation
  is the exact balance: one ebit and two classical bits deliver one qubit, and
  the two bits are the irreducible residue of a four-outcome measurement, not
  an engineering margin. Here the state has a say: what to cut depends on where
  the correlations are.

  Amplitude-distributed. One state vector spread across many nodes, the node
  address being the global bit pattern. There are no ebits at all; the price is
  amplitudes crossing a node boundary. The selection of global qubits has a
  closed form - the cost of a set is the sum of its members' degrees plus twice
  its size - which the circuit's degree sequence settles before the state
  exists. Here the state has no say.

Every figure and formula on the plate is from a published article or a
committed store. Nothing is computed here.

Contrast, measured rather than assumed. The dimmed column has two greys: its
TEXT is #8097b6, which measures 5.75:1 against #0d1b33 and 4.84:1 against
#16294a, the two ends of the house gradient, and so clears the 4.5:1 bar at
both; its box and dots are #6b82ab at 4.43:1 and 3.73:1, which clears the 3:1
bar that non-text graphics have to meet. The first version of this plate used
#5c7299 throughout and measured 2.98:1 at the lighter end, which fails both.
The column still reads as the dimmed one - it has no panel behind it, and both
greys sit well below the #8fa8c8 of the live columns at 7.04:1 and 5.93:1.

Ramon Schweiss, QWeb (c) Research, 27 November 2026.
"""
import os
import sys

W, H = 980, 540
DARK = "--dark" in sys.argv

if DARK:
    BG, INK, MUTED, GRID, ACCENT = ("#0d1b33", "#ffffff", "#8fa8c8",
                                    "#3f5a80", "#f0a06a")
    PANEL, DIM, DIM_TEXT = "#ffffff", "#6b82ab", "#8097b6"
else:
    BG, INK, MUTED, GRID, ACCENT = ("#ffffff", "#15243d", "#6b7f9c",
                                    "#d4dce8", "#c2651f")
    PANEL, DIM, DIM_TEXT = "#f4f6fa", "#aab6c8", "#8a97a9"
PANEL_OP = "0.06" if DARK else "1"

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")

LAB = 158                                  # right edge of the label column
COLS = [(188, 434), (456, 702), (724, 960)]
MOT_T, MOT_B = 108, 214                    # motif band
ROWS = [268, 330, 392]                     # the three attribute rows

ALT = ("Three execution models side by side. One processor, dimmed, with no "
       "node boundary and nothing to pay. A distributed model that pays for "
       "agreement in shared entangled pairs and classical bits, where the "
       "state has a say in the layout. And an amplitude-distributed model with "
       "no entanglement at all, which pays in amplitudes crossing a node "
       "boundary and where the node address decides before the state exists.")

TITLES = ["one processor", "distributed", "amplitude-distributed"]
SUB = ["the degenerate case", "pays in entanglement", "pays in amplitudes"]
PAYS = ["nothing — there is no boundary",
        "1 ebit + 2 classical bits per qubit",
        "amplitudes across a boundary"]
DECIDES = ["nothing to decide",
           "where the correlations are",
           "the circuit's degree sequence"]
SAY = ["—", "yes", "no"]


def write(name, body):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(body + "</svg>\n")
    print(f"wrote {path}")


def node(x, y, w, h, colour):
    return (f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" '
            f'rx="6" fill="none" stroke="{colour}" stroke-width="1.8"/>')


def dots(cx, cy, n, colour, spread=46):
    p = []
    for i in range(n):
        x = cx - spread / 2 + i * (spread / max(n - 1, 1))
        p.append(f'<circle cx="{x:.0f}" cy="{cy:.0f}" r="4" fill="{colour}"/>')
    return "".join(p)


def motif_mono(cx, ytop=None):
    y = (MOT_T if ytop is None else ytop) + 24
    return (node(cx - 62, y, 124, 58, DIM)
            + dots(cx, y + 20, 4, DIM)
            + dots(cx, y + 40, 4, DIM))


def motif_distributed(cx, ytop=None):
    y = (MOT_T if ytop is None else ytop) + 24
    p = [node(cx - 96, y, 82, 58, GRID), node(cx + 14, y, 82, 58, GRID)]
    p.append(dots(cx - 55, y + 18, 3, INK, 34))
    p.append(dots(cx + 55, y + 18, 3, INK, 34))
    # the shared pair, and the two classical bits that travel with it
    p.append(f'<line x1="{cx-55}" y1="{y+42}" x2="{cx+55}" y2="{y+42}" '
             f'stroke="{ACCENT}" stroke-width="1.8"/>')
    for dx in (-55, 55):
        p.append(f'<circle cx="{cx+dx}" cy="{y+42}" r="5" fill="{BG}" '
                 f'stroke="{ACCENT}" stroke-width="2"/>')
    p.append(f'<text x="{cx}" y="{y+76}" font-size="11.5" fill="{ACCENT}" '
             f'text-anchor="middle">1 ebit + 2 bits</text>')
    return "".join(p)


def motif_amplitude(cx, ytop=None):
    y = (MOT_T if ytop is None else ytop) + 24
    p = [node(cx - 96, y, 192, 58, GRID)]
    s, g = 15, 6
    x0 = cx - (8 * s + 7 * g) / 2
    for i in range(8):
        fill = ACCENT if i in (3, 4) else MUTED
        p.append(f'<rect x="{x0 + i*(s+g):.0f}" y="{y+14}" width="{s}" '
                 f'height="{s}" rx="2" fill="{fill}" opacity="0.85"/>')
    p.append(f'<line x1="{cx}" y1="{y+6}" x2="{cx}" y2="{y+52}" '
             f'stroke="{INK}" stroke-width="1.4" stroke-dasharray="4,4"/>')
    p.append(f'<path d="M {cx-26} {y+44} L {cx+26} {y+44}" stroke="{ACCENT}" '
             f'stroke-width="2"/>')
    p.append(f'<path d="M {cx+26} {y+44} l -7 -4 l 0 8 z" fill="{ACCENT}"/>')
    p.append(f'<text x="{cx}" y="{y+76}" font-size="11.5" fill="{ACCENT}" '
             f'text-anchor="middle">no ebits at all</text>')
    return "".join(p)


# ------------------------------------------------- the narrow-screen version
SW, SH = 420, 1080                      # one column, for phones
FOOT = [
    "In the amplitude-distributed model the selection of global",
    "qubits has a closed form, cost(S) = &#931; deg(v) + 2|S|, which",
    "the circuit settles before the state exists. So whether",
    "entanglement lowers the price of agreement is a question put",
    "to each model, not an assumption carried into it.",
]


def stacked_plate():
    """The same content in one column, for a screen too narrow for the table.

    Not a shrunk copy: at 390 pixels the wide plate renders its 12.5 pixel
    text at about 5 pixels, which is why this exists. Same figures, same
    wording, same palette, three blocks under one another.
    """
    defs = ('<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
            '<stop offset="0" stop-color="#0d1b33"/>'
            '<stop offset="1" stop-color="#16294a"/></linearGradient></defs>'
            if DARK else "")
    fill = "url(#bg)" if DARK else BG
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SW} {SH}" '
         f'font-family="DejaVu Serif" role="img" aria-label="{ALT}">'
         f'{defs}<rect width="{SW}" height="{SH}" fill="{fill}"/>']
    a = p.append
    a(f'<text x="20" y="40" font-size="19" fill="{INK}" font-weight="bold">'
      f'Three execution models,</text>')
    a(f'<text x="20" y="64" font-size="19" fill="{INK}" font-weight="bold">'
      f'two currencies</text>')
    a(f'<text x="20" y="90" font-size="13" fill="{MUTED}">The price of '
      f'agreement is an account.</text>')
    a(f'<text x="20" y="108" font-size="13" fill="{MUTED}">Which account '
      f'depends on the machine.</text>')

    labels = ["pays in", "layout decided by", "state has a say"]
    values = [PAYS, DECIDES, SAY]
    motifs = [motif_mono, motif_distributed, motif_amplitude]
    top = 134
    for i in range(3):
        h = 244
        if i:
            a(f'<rect x="16" y="{top}" width="{SW-32}" height="{h}" rx="10" '
              f'fill="{PANEL}" opacity="{PANEL_OP}"/>')
        cx = SW / 2
        col = DIM_TEXT if i == 0 else INK
        a(f'<text x="{cx}" y="{top+28}" font-size="16" fill="{col}" '
          f'text-anchor="middle" font-weight="bold">{TITLES[i]}</text>')
        a(f'<text x="{cx}" y="{top+48}" font-size="12" fill="{MUTED}" '
          f'text-anchor="middle">{SUB[i]}</text>')
        a(motifs[i](cx, top + 44))
        for r in range(3):
            y = top + 160 + r * 26
            a(f'<text x="30" y="{y}" font-size="11.5" fill="{MUTED}">'
              f'{labels[r]}</text>')
            vcol = DIM_TEXT if i == 0 else INK
            if r == 2 and i == 2:
                vcol = ACCENT
            weight = ' font-weight="bold"' if r == 2 and i else ""
            a(f'<text x="{SW-30}" y="{y}" font-size="12" fill="{vcol}" '
              f'text-anchor="end"{weight}>{values[r][i]}</text>')
        top += h + 14

    for i, line in enumerate(FOOT):
        a(f'<text x="20" y="{top + 24 + i*19}" font-size="12" fill="{INK}">'
          f'{line}</text>')
    a(f'<text x="20" y="{SH-34}" font-size="11" fill="{MUTED}" '
      f'font-style="italic">QWeb &#169; Research &#183; What an '
      f'Architecture Pays For</text>')
    a(f'<text x="20" y="{SH-16}" font-size="11" fill="{MUTED}" '
      f'font-style="italic">qweb-quantum.com</text>')
    write("d_execution_models_stacked.svg", "".join(p))
    return 0


def main():
    if "--stacked" in sys.argv:
        return stacked_plate()
    defs = ('<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
            '<stop offset="0" stop-color="#0d1b33"/>'
            '<stop offset="1" stop-color="#16294a"/></linearGradient></defs>'
            if DARK else "")
    fill = "url(#bg)" if DARK else BG
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
         f'font-family="DejaVu Serif" role="img" aria-label="{ALT}">'
         f'{defs}<rect width="{W}" height="{H}" fill="{fill}"/>']
    a = p.append

    a(f'<text x="40" y="44" font-size="19" fill="{INK}" font-weight="bold">'
      f'Three execution models, two currencies</text>')
    a(f'<text x="40" y="70" font-size="13.5" fill="{MUTED}">The price of '
      f'agreement is an account. Which account depends on the machine.</text>')

    for i, (x0, x1) in enumerate(COLS):
        cx = (x0 + x1) / 2
        if i:
            a(f'<rect x="{x0-12}" y="{MOT_T-28}" width="{x1-x0+24}" '
              f'height="{ROWS[-1]-MOT_T+66}" rx="10" fill="{PANEL}" '
              f'opacity="{PANEL_OP}"/>')
        col = DIM_TEXT if i == 0 else INK
        a(f'<text x="{cx}" y="{MOT_T-8}" font-size="15" fill="{col}" '
          f'text-anchor="middle" font-weight="bold">{TITLES[i]}</text>')
        a(f'<text x="{cx}" y="{MOT_T+10}" font-size="11.5" fill="{MUTED}" '
          f'text-anchor="middle">{SUB[i]}</text>')
        a([motif_mono, motif_distributed, motif_amplitude][i](cx))

    labels = ["pays in", "layout decided by", "state has a say"]
    values = [PAYS, DECIDES, SAY]
    for r, y in enumerate(ROWS):
        a(f'<line x1="40" y1="{y-20}" x2="{W-40}" y2="{y-20}" '
          f'stroke="{GRID}" stroke-width="1.2"/>')
        a(f'<text x="{LAB}" y="{y}" font-size="12" fill="{MUTED}" '
          f'text-anchor="end">{labels[r]}</text>')
        for i, (x0, x1) in enumerate(COLS):
            cx = (x0 + x1) / 2
            col = DIM_TEXT if i == 0 else INK
            if r == 2 and i == 2:
                col = ACCENT
            weight = ' font-weight="bold"' if r == 2 and i else ""
            a(f'<text x="{cx}" y="{y}" font-size="12.5" fill="{col}" '
              f'text-anchor="middle"{weight}>{values[r][i]}</text>')

    a(f'<line x1="40" y1="{ROWS[-1]+24}" x2="{W-40}" y2="{ROWS[-1]+24}" '
      f'stroke="{GRID}" stroke-width="1.2"/>')
    a(f'<text x="40" y="{ROWS[-1]+52}" font-size="12.5" fill="{INK}">'
      f'In the amplitude-distributed model the selection of global qubits has '
      f'a closed form, cost(S) = &#931; deg(v) + 2|S|, which the circuit '
      f'settles</text>')
    a(f'<text x="40" y="{ROWS[-1]+72}" font-size="12.5" fill="{INK}">'
      f'before the state exists. So whether entanglement lowers the price of '
      f'agreement is a question put to each model, not an assumption carried '
      f'into it.</text>')
    a(f'<text x="40" y="{H-16}" font-size="11.5" fill="{MUTED}" '
      f'font-style="italic">QWeb &#169; Research &#183; What an Architecture '
      f'Pays For, sections 02 and 11 to 12 &#183; qweb-quantum.com</text>')

    write("d_execution_models.svg", "".join(p))
    return 0


if __name__ == "__main__":
    sys.exit(main())
