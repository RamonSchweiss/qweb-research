"""Teaser image for "What Moves the Baseline", in the QWeb house design.

Emits designs/teaser_moving_baseline.svg at 1200x628. No arguments. This
script lives in calculations/ because it carries figures; the image it renders
lives in designs/ with the other teaser assets.

House design, taken from teaser_computation_knows.svg and teaser_stack.svg:
1200x628, DejaVu Serif, background gradient #0d1b33 -> #16294a, orange accent
#f0a06a, body text #cfe0f5, muted labels #8fa8c8, rules #3f5a80. Brand block
top left, a motif top right, title at 58px bold, orange rule, standfirst,
a three-cell statistics panel at 6% white, italic footer.

The three figures in the panel, with provenance, because the article is about
numbers losing it in transit:

  +3 % at most      ours. The largest contribution of the CLASSICAL side to the
                    crossover anywhere in the disclosed truncation family.
  +20 %, predicted  ours. From the reported 13.35% smaller amplitude, at
                    amplitude estimation's 1/sqrt(a).
  not resolved      about the move REPORTED by Daniel Hug (qubit-lab.ch): its
                    90% interval at 200 repetitions runs -12% to +52% and so
                    contains no movement at all. The footer names him, because
                    a headline figure without its source is exactly the failure
                    the article describes.

All three are printed by calculations/basket_grid_sensitivity.py.

Ramon Schweiss, QWeb (c) Research, 8 November 2026.
"""
import sys

W, H = 1200, 628
ORANGE = "#f0a06a"
BODY = "#cfe0f5"
MUTED = "#8fa8c8"
RULE = "#3f5a80"

TITLE = "What Moves the Baseline"
STRAP = "METHODOLOGY"
STANDFIRST = [
    "A comparison has two sides, and both of them move — and in the",
    "best-documented cases, the quantum claim is itself what moved",
    "the classical one. One measured case, on which side it sits.",
]
STATS = [
    (112, "THE CLASSICAL SIDE", "+3 % at most", "#ffffff"),
    (472, "THE QUANTUM SIDE", "+20 %, predicted", ORANGE),
    (872, "THE OBSERVED MOVE", "not resolved", "#ffffff"),
]
ALT = ("Teaser image: What Moves the Baseline. A comparison has two sides and "
       "both of them move. The classical side contributes at most three per "
       "cent, the quantum side twenty per cent as predicted, and the observed "
       "move is not resolved.")


def motif():
    """A tight classical cluster, a long move, and an unresolved interval."""
    y = 150
    p = [f'<g opacity="0.95">']
    # the unresolved interval around the moved point, drawn first so that the
    # axis is not showing through it as a muddy stripe
    p.append(f'<line x1="1000" y1="{y}" x2="1144" y2="{y}" stroke="{ORANGE}" '
             f'stroke-width="11" opacity="0.42" stroke-linecap="butt"/>')
    for cx in (1000, 1144):
        p.append(f'<line x1="{cx}" y1="{y-9}" x2="{cx}" y2="{y+9}" '
                 f'stroke="{ORANGE}" stroke-width="1.6" opacity="0.75"/>')
    # the measurement axis, only where the interval does not already cover it
    p.append(f'<line x1="856" y1="{y}" x2="1000" y2="{y}" stroke="{RULE}" '
             f'stroke-width="1.4"/>')
    # where the baseline stood, and where it moved to
    for cx in (915, 1085):
        p.append(f'<line x1="{cx}" y1="{y-74}" x2="{cx}" y2="{y+40}" '
                 f'stroke="#7fb0e6" stroke-width="1.5" stroke-dasharray="6,7" '
                 f'opacity="0.45"/>')
    # the classical side: five points, and they barely separate
    for dx in (-12, -6, 0, 5, 12):
        p.append(f'<circle cx="{915+dx}" cy="{y}" r="5.5" fill="{BODY}" '
                 f'opacity="0.9"/>')
    # the quantum side: one point, a long way off
    p.append(f'<circle cx="1085" cy="{y}" r="9.5" fill="{ORANGE}"/>')
    # the move itself
    p.append(f'<line x1="930" y1="{y-52}" x2="1068" y2="{y-52}" '
             f'stroke="{ORANGE}" stroke-width="2.1" opacity="0.9"/>')
    p.append(f'<path d="M1085 {y-52} L1068 {y-59} L1068 {y-45} Z" '
             f'fill="{ORANGE}" opacity="0.9"/>')
    p.append('</g>')
    return "".join(p)


def main():
    p = []
    a = p.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
      f'font-family="DejaVu Serif" role="img" aria-label="{ALT}">')
    a('<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
      '<stop offset="0" stop-color="#0d1b33"/>'
      '<stop offset="1" stop-color="#16294a"/></linearGradient></defs>')
    a(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')

    a(motif())

    # brand block
    a(f'<rect x="72" y="70" width="5" height="62" fill="{ORANGE}"/>')
    a(f'<text x="100" y="94" font-size="15.5" fill="{ORANGE}" '
      f'letter-spacing="4">QWEB &#169; RESEARCH</text>')
    a(f'<text x="100" y="124" font-size="15.5" fill="{MUTED}" '
      f'letter-spacing="3">{STRAP}</text>')

    # title and rule
    a(f'<text x="72" y="252" font-size="58" fill="#ffffff" '
      f'font-weight="bold">{TITLE}</text>')
    a(f'<rect x="72" y="296" width="132" height="3" fill="{ORANGE}"/>')

    # standfirst
    for i, line in enumerate(STANDFIRST):
        a(f'<text x="72" y="{346 + i*32}" font-size="21" fill="{BODY}">'
          f'{line}</text>')

    # statistics panel
    a(f'<rect x="72" y="446" width="1056" height="92" rx="10" fill="#ffffff" '
      f'opacity="0.06"/>')
    for i, (xp, label, value, colour) in enumerate(STATS):
        if i:
            a(f'<line x1="{xp-40}" y1="464" x2="{xp-40}" y2="522" '
              f'stroke="{RULE}" stroke-width="1.4"/>')
        a(f'<text x="{xp}" y="482" font-size="15" fill="{MUTED}" '
          f'letter-spacing="2">{label}</text>')
        a(f'<text x="{xp}" y="518" font-size="30" fill="{colour}" '
          f'font-weight="bold">{value}</text>')

    # footer
    a(f'<text x="72" y="598" font-size="16.5" fill="{MUTED}" '
      f'font-style="italic">qweb-quantum.com &#183; figures from the measured '
      f'case reported by Daniel Hug, qubit-lab.ch &#183; each with its '
      f'calculation</text>')
    a('</svg>')

    out = "teaser_moving_baseline.svg"
    with open(out, "w", encoding="utf-8") as f:
        f.write("".join(p) + "\n")
    print(f"wrote {out}  ({W}x{H})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
