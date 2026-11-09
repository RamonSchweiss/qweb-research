"""Teaser image for "What Moves the Baseline", in the QWeb house design.

Emits designs/teaser_moving_baseline.svg at 1200x628. No arguments. This script
lives in calculations/ because it carries figures; the image it renders lives
in designs/ with the other teaser assets.

VERSION 2, 9 November 2026. Version 1 showed a single axis with a tight
classical cluster and one moved point - the merged picture that the article's
own correction of 9 November withdrew. The motif now shows the two modelling
decisions apart, as the figure does.

House design, taken from teaser_computation_knows.svg and teaser_stack.svg:
1200x628, DejaVu Serif, background gradient #0d1b33 -> #16294a, orange accent
#f0a06a, body text #cfe0f5, muted labels #8fa8c8, rules #3f5a80.

The three figures in the panel, with provenance, because the article is about
numbers losing it in transit:

  up to x4, non-monotonic   Daniel Hug's ESTIMATE of the truncation effect on
                            the crossover - from an exchange, not a run on the
                            engine. About 6,000 calls at +-3 sigma, 23,000 at
                            +-4, 17,000 at +-4.5, 24,000 at +-5.
  about +-200 calls         ours. Everything the CLASSICAL side accounts for
                            anywhere in the disclosed family, +3.2% to -0.3%
                            of a crossover of 6,000 calls.
  not resolved              about the correlation move Daniel Hug REPORTS:
                            +16% at 400 repetitions, 90% interval -6% to +38%,
                            which contains zero.

All three are printed by calculations/basket_grid_sensitivity.py or stated by
him. The footer names him, because a headline strip is where a credit line
usually gets dropped.

Ramon Schweiss, QWeb (c) Research, 9 November 2026.
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
    "the classical one. Plus one measured case, corrected in public.",
]
STATS = [
    (112, "UNDER GRID TRUNCATION", "up to ×4, non-monotonic", ORANGE),
    (560, "THE CLASSICAL SHARE", "about ±200 calls", "#ffffff"),
    (872, "THE REPORTED MOVE", "not resolved", "#ffffff"),
]
ALT = ("Teaser image: What Moves the Baseline. Two modelling decisions move "
       "the crossover. Grid truncation moves it by up to a factor of four and "
       "not monotonically, the classical side accounts for about two hundred "
       "oracle calls of that, and the reported correlation move is not "
       "resolved.")

# left mini-panel: Daniel Hug's truncation estimate, (sigma, oracle calls)
CROSSOVER = [(3.0, 6000), (4.0, 23000), (4.5, 17000), (5.0, 24000)]


def motif():
    """Two decisions, side by side, as the figure shows them."""
    p = ['<g opacity="0.95">']

    # --- left: truncation, non-monotonic, estimate ---
    x0, x1, yb, yt = 858, 968, 196, 116

    def mx(s):
        return x0 + (s - 3.0) / 2.0 * (x1 - x0)

    def my(c):
        return yb - c / 26000 * (yb - yt)

    p.append(f'<line x1="{x0-6}" y1="{yb}" x2="{x1+6}" y2="{yb}" '
             f'stroke="{RULE}" stroke-width="1.2"/>')
    pts = " ".join(f"{mx(s):.1f},{my(c):.1f}" for s, c in CROSSOVER)
    p.append(f'<polyline points="{pts}" fill="none" stroke="{ORANGE}" '
             f'stroke-width="1.8" stroke-dasharray="5,4" opacity="0.85"/>')
    for s, c in CROSSOVER:
        p.append(f'<circle cx="{mx(s):.1f}" cy="{my(c):.1f}" r="4.6" '
                 f'fill="#16294a" stroke="{ORANGE}" stroke-width="1.8"/>')
    p.append(f'<text x="{(x0+x1)/2:.0f}" y="{yb+20}" font-size="12.5" '
             f'fill="{MUTED}" text-anchor="middle">truncation</text>')

    # --- divider ---
    p.append(f'<line x1="1006" y1="112" x2="1006" y2="200" stroke="{RULE}" '
             f'stroke-width="1" opacity="0.7"/>')

    # --- right: correlation, reported move with an interval over zero ---
    rx0, rx1, ry = 1030, 1128, 156

    def cx(v):                      # per cent, -10 .. +40
        return rx0 + (v + 10) / 50 * (rx1 - rx0)

    p.append(f'<line x1="{cx(0):.1f}" y1="{ry-34}" x2="{cx(0):.1f}" '
             f'y2="{ry+30}" stroke="{BODY}" stroke-width="1.2" '
             f'stroke-dasharray="3,4" opacity="0.6"/>')
    p.append(f'<line x1="{cx(-6):.1f}" y1="{ry}" x2="{cx(38):.1f}" y2="{ry}" '
             f'stroke="{ORANGE}" stroke-width="9" opacity="0.42"/>')
    for v in (-6, 38):
        p.append(f'<line x1="{cx(v):.1f}" y1="{ry-8}" x2="{cx(v):.1f}" '
                 f'y2="{ry+8}" stroke="{ORANGE}" stroke-width="1.5" '
                 f'opacity="0.8"/>')
    p.append(f'<circle cx="{cx(16):.1f}" cy="{ry}" r="6" fill="{ORANGE}"/>')
    p.append(f'<text x="{(rx0+rx1)/2:.0f}" y="{ry+40}" font-size="12.5" '
             f'fill="{MUTED}" text-anchor="middle">correlation</text>')

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

    a(f'<rect x="72" y="70" width="5" height="62" fill="{ORANGE}"/>')
    a(f'<text x="100" y="94" font-size="15.5" fill="{ORANGE}" '
      f'letter-spacing="4">QWEB &#169; RESEARCH</text>')
    a(f'<text x="100" y="124" font-size="15.5" fill="{MUTED}" '
      f'letter-spacing="3">{STRAP}</text>')

    a(f'<text x="72" y="252" font-size="58" fill="#ffffff" '
      f'font-weight="bold">{TITLE}</text>')
    a(f'<rect x="72" y="296" width="132" height="3" fill="{ORANGE}"/>')

    for i, line in enumerate(STANDFIRST):
        a(f'<text x="72" y="{346 + i*32}" font-size="21" fill="{BODY}">'
          f'{line}</text>')

    a(f'<rect x="72" y="446" width="1056" height="92" rx="10" fill="#ffffff" '
      f'opacity="0.06"/>')
    for i, (xp, label, value, colour) in enumerate(STATS):
        if i:
            a(f'<line x1="{xp-40}" y1="464" x2="{xp-40}" y2="522" '
              f'stroke="{RULE}" stroke-width="1.4"/>')
        a(f'<text x="{xp}" y="482" font-size="15" fill="{MUTED}" '
          f'letter-spacing="2">{label}</text>')
        a(f'<text x="{xp}" y="518" font-size="26" fill="{colour}" '
          f'font-weight="bold">{value}</text>')

    a(f'<text x="72" y="598" font-size="16.5" fill="{MUTED}" '
      f'font-style="italic">qweb-quantum.com &#183; estimate and reported '
      f'values by Daniel Hug, qubit-lab.ch &#183; the classical share is '
      f'ours</text>')
    a('</svg>')

    out = "teaser_moving_baseline.svg"
    with open(out, "w", encoding="utf-8") as f:
        f.write("".join(p) + "\n")
    print(f"wrote {out}  ({W}x{H})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
