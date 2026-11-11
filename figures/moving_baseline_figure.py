"""Figure for "What Moves the Baseline": which side of a crossover moves?

Emits figures/out/moving_baseline_figure.svg. No arguments. This script lives in
figures/ because it renders a figure: run_all.py collects calculations/*.py,
and a figure script has nothing to verify.

VERSION 2, 9 November 2026. Version 1 put the grid-truncation family and a
+19% crossover move on one axis. Daniel Hug, who measured it, pointed out that
the +19% is not a truncation effect at all: it is the shift when the
correlation goes from 0.5 to 0 on the SAME grid (+-3.5 sigma), and the 13.35%
smaller amplitude comes from the price falling from 16.22 to 14.06, not from a
wider grid. Version 1 therefore compared two different experiments. This
version separates them into two panels, each with the axis its own quantity
needs. basket_grid_sensitivity.py had it right; version 1 misread it.

Provenance of each value, stated because the figure makes a claim about
attribution:

LEFT PANEL - grid truncation
  CROSSOVER      Daniel Hug's ESTIMATE, from an exchange with him and not from
                 a run on the engine, so drawn with open markers and a dashed
                 connector. Not monotonic. The crossover is a budget of oracle
                 calls - the budget above which amplitude estimation is more
                 accurate than Monte Carlo - and not a problem size.
  CLASSICAL      ours. The band shows the whole range the CLASSICAL side alone
                 accounts for anywhere in the disclosed family: +3.2% to -0.3%
                 of the crossover, drawn around the +-3 sigma value, so about
                 +-200 calls against a swing of some 18,000.

RIGHT PANEL - correlation 0.5 -> 0, same grid
  PREDICTED      ours. From the reported 13.35% smaller amplitude, with
                 amplitude estimation's 1/sqrt(a) scaling.
  OBSERVED       reported by Daniel Hug for his own measurement, at 400
                 repetitions, published on his evidence page since 1 November
                 2026: about 8,100 to 9,400 oracle calls, +16%.
  INTERVAL       likewise reported: the 90% interval at 400 repetitions. It
                 contains zero, so the move is not resolved.

The caption the figure is published with, kept here because the first time it
was handed to a CMS the instruction said to preserve it and no caption existed:

  Figure 1. Which side of the crossover moves, and under which modelling
  decision? The crossover is a budget of oracle calls, not a problem size.
  Left: grid truncation. The open markers are an estimate, not a run, and they
  are not monotonic - +-4.5 sigma sits below +-4 sigma. The thin band is
  everything the classical side alone accounts for anywhere in the disclosed
  family, +3.2% to -0.3% of the crossover; the swing above it is the quantum
  side. Right: a different decision, on the same grid. The correlation going
  from 0.5 to 0 drops the price from 16.22 to 14.06 and the amplitude by
  13.35%, which at 1/sqrt(a) predicts +20%. The reported move is +16% at 400
  repetitions, and its 90% interval contains zero. Estimates and reported
  values are Daniel Hug's (qubit-lab.ch); the classical band and the
  prediction are ours, from
  calculations/basket_grid_sensitivity.py.

Ramon Schweiss, QWeb (c) Research, 9 November 2026.
"""
import sys
from pathlib import Path

# left panel: Daniel Hug's estimate, (sigma level, crossover in oracle calls)
CROSSOVER = [(3.0, 6000), (4.0, 23000), (4.5, 17000), (5.0, 24000)]
CLASSICAL_PC = (3.2, -0.3)      # ours: classical share of the move, per cent
ANCHOR = 6000                   # the +-3 sigma crossover the band sits on

# right panel: correlation 0.5 -> 0 at +-3.5 sigma, per cent
PREDICTED = 20.0                # ours, at 1/sqrt(a)
OBSERVED = 16.0                 # reported, 400 repetitions
INTERVAL = (-6.0, 38.0)         # reported, 90%

W, H = 980, 560
BLUE, GREEN, ORANGE, RED = "#2b6cb0", "#276749", "#b7791f", "#9b2c2c"

# left panel geometry
LX0, LX1 = 92, 452
LY0, LY1 = 150, 420             # top (26,000 calls) to axis (0)
LCAL_LO, LCAL_HI = 2.8, 5.2
LMAX = 26000

# right panel geometry
RX0, RX1 = 568, 928
RY = 206                        # first lane
RAX = 420
RLO, RHI = -12.0, 44.0


def pc(v, dec=0):
    return f"{v:+.{dec}f}%".replace("-", "−")


def lx(s):
    return LX0 + (s - LCAL_LO) / (LCAL_HI - LCAL_LO) * (LX1 - LX0)


def ly(c):
    return LY1 - c / LMAX * (LY1 - LY0)


def rx(v):
    return RX0 + (v - RLO) / (RHI - RLO) * (RX1 - RX0)


def left_panel(a):
    a(f'<text x="{LX0}" y="118" class="ph">Grid truncation</text>')
    a(f'<text x="{LX0}" y="138" class="dim">crossover, oracle calls '
      f'&#183; estimate, not a run</text>')

    # axes
    a(f'<line x1="{LX0}" y1="{LY1}" x2="{LX1}" y2="{LY1}" class="ax"/>')
    a(f'<line x1="{LX0}" y1="{LY0}" x2="{LX0}" y2="{LY1}" class="ax"/>')
    for c in (0, 6000, 12000, 18000, 24000):
        a(f'<line x1="{LX0-5}" y1="{ly(c):.1f}" x2="{LX0}" y2="{ly(c):.1f}" '
          f'class="tick"/>')
        lab = "0" if not c else f"{c//1000}k"
        a(f'<text x="{LX0-10}" y="{ly(c)+4:.1f}" class="dim" '
          f'text-anchor="end">{lab}</text>')
    for s, _ in CROSSOVER:
        a(f'<line x1="{lx(s):.1f}" y1="{LY1}" x2="{lx(s):.1f}" y2="{LY1+5}" '
          f'class="tick"/>')
        a(f'<text x="{lx(s):.1f}" y="{LY1+22:.1f}" class="dim" '
          f'text-anchor="middle">±{s:g}σ</text>')

    # the estimate: dashed connector, open markers
    pts = " ".join(f"{lx(s):.1f},{ly(c):.1f}" for s, c in CROSSOVER)
    a(f'<polyline points="{pts}" fill="none" stroke="{ORANGE}" '
      f'stroke-width="1.8" stroke-dasharray="7,5" opacity="0.8"/>')
    for s, c in CROSSOVER:
        a(f'<circle cx="{lx(s):.1f}" cy="{ly(c):.1f}" r="6" fill="#fff" '
          f'stroke="{ORANGE}" stroke-width="2"/>')

    # the one point that makes it non-monotonic
    a(f'<text x="{lx(4.5):.1f}" y="{ly(17000)+26:.1f}" class="dim" '
      f'text-anchor="middle" fill="{ORANGE}">below ±4σ</text>')

    # what the classical side alone accounts for
    hi = ANCHOR * (1 + CLASSICAL_PC[0] / 100)
    lo = ANCHOR * (1 + CLASSICAL_PC[1] / 100)
    a(f'<rect x="{LX0+1:.1f}" y="{ly(hi):.1f}" width="{LX1-LX0-2:.1f}" '
      f'height="{max(ly(lo)-ly(hi), 2.5):.1f}" fill="{BLUE}" opacity="0.5"/>')
    a(f'<text x="{LX1}" y="{ly(hi)-24:.1f}" class="lbl" text-anchor="end">'
      f'the classical side, whole family</text>')
    a(f'<text x="{LX1}" y="{ly(hi)-7:.1f}" class="dim" text-anchor="end">'
      f'{pc(CLASSICAL_PC[0], 1)} to {pc(CLASSICAL_PC[1], 1)} — about ±200 '
      f'calls</text>')


def right_panel(a):
    a(f'<text x="{RX0}" y="118" class="ph">Correlation 0.5 → 0</text>')
    a(f'<text x="{RX0}" y="138" class="dim">same grid, ±3.5σ &#183; change in '
      f'the crossover</text>')

    a(f'<line x1="{RX0}" y1="{RAX}" x2="{RX1}" y2="{RAX}" class="ax"/>')
    for v in (-10, 0, 10, 20, 30, 40):
        a(f'<line x1="{rx(v):.1f}" y1="{RAX}" x2="{rx(v):.1f}" y2="{RAX+5}" '
          f'class="tick"/>')
        a(f'<text x="{rx(v):.1f}" y="{RAX+22}" class="dim" '
          f'text-anchor="middle">{pc(v)}</text>')
    a(f'<line x1="{rx(0):.1f}" y1="{RY-30}" x2="{rx(0):.1f}" y2="{RAX+5}" '
      f'stroke="#333" stroke-width="1" stroke-dasharray="2,3"/>')

    # predicted, ours
    a(f'<circle cx="{rx(PREDICTED):.1f}" cy="{RY}" r="5.5" fill="{GREEN}"/>')
    a(f'<text x="{rx(PREDICTED):.1f}" y="{RY-16}" class="lbl" '
      f'text-anchor="middle">predicted at 1/√a: {pc(PREDICTED)}</text>')

    # observed, reported, with its 90% interval
    yo = RY + 70
    a(f'<line x1="{rx(INTERVAL[0]):.1f}" y1="{yo}" '
      f'x2="{rx(INTERVAL[1]):.1f}" y2="{yo}" class="ivl"/>')
    for v in INTERVAL:
        a(f'<line x1="{rx(v):.1f}" y1="{yo-8}" x2="{rx(v):.1f}" y2="{yo+8}" '
          f'stroke="{ORANGE}" stroke-width="1.6" opacity="0.75"/>')
    a(f'<circle cx="{rx(OBSERVED):.1f}" cy="{yo}" r="6" fill="{ORANGE}"/>')
    a(f'<text x="{rx(OBSERVED):.1f}" y="{yo-16}" class="lbl" '
      f'text-anchor="middle">reported {pc(OBSERVED)}</text>')
    a(f'<text x="{RX1}" y="{yo+28}" class="dim" text-anchor="end">'
      f'90% interval at 400 repetitions, {pc(INTERVAL[0])} to '
      f'{pc(INTERVAL[1])}</text>')
    a(f'<text x="{RX1}" y="{yo+46}" class="dim" text-anchor="end">'
      f'— it contains zero</text>')


def main():
    p = []
    a = p.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
      f'font-family="Georgia, serif" font-size="14">')
    a('<style>'
      '.ax{stroke:#333;stroke-width:1.2}'
      '.tick{stroke:#999;stroke-width:1}'
      '.lbl{fill:#333}.dim{fill:#777;font-size:12.5}'
      '.ph{font-size:15.5px;fill:#111;font-weight:bold}'
      '.ttl{font-size:19px;fill:#111}.sub{font-size:13px;fill:#666}'
      f'.ivl{{stroke:{ORANGE};stroke-width:7;opacity:.30;stroke-linecap:butt}}'
      '</style>')
    a(f'<rect width="{W}" height="{H}" fill="#fff"/>')

    a(f'<text x="{LX0}" y="46" class="ttl">Which side of the crossover moves, '
      f'and under which decision?</text>')
    a(f'<text x="{LX0}" y="68" class="sub">Basket option, two correlated '
      f'shares, 8-qubit grid. The crossover is a budget of oracle calls, not a '
      f'problem size.</text>')

    left_panel(a)
    right_panel(a)
    a(f'<line x1="510" y1="100" x2="510" y2="450" stroke="#ddd" '
      f'stroke-width="1"/>')

    y0 = 492
    a(f'<text x="{LX0}" y="{y0}" class="lbl">Two modelling decisions, two '
      f'different effects, and neither of them appears in a result summary. '
      f'Truncation moves the</text>')
    a(f'<text x="{LX0}" y="{y0+21}" class="lbl">crossover by far more than the '
      f'classical side can account for, and not monotonically. Correlation '
      f'moves it by the amount the</text>')
    a(f'<text x="{LX0}" y="{y0+42}" class="lbl">amplitude predicts — but at '
      f'400 repetitions that move is still not resolved.</text>')
    a('</svg>')

    # next to this file, not in the current directory: where the SVG lands
    # should not depend on where the script was started from
    out = Path(__file__).resolve().parent / "out" / "moving_baseline_figure.svg"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(p) + "\n")
    print(f"wrote {out}")
    print("\nValues drawn, with provenance:")
    print("  LEFT - grid truncation")
    for s, c in CROSSOVER:
        print(f"    ±{s:g}σ  {c:>6,} calls      D. Hug, estimate, no engine run")
    print(f"    classical share  {CLASSICAL_PC[0]:+.1f}% to "
          f"{CLASSICAL_PC[1]:+.1f}%   ours")
    print("  RIGHT - correlation 0.5 -> 0 at ±3.5σ")
    print(f"    predicted at 1/sqrt(a)  {PREDICTED:+.0f}%         ours")
    print(f"    reported, 400 reps      {OBSERVED:+.0f}%         D. Hug")
    print(f"    90% interval            {INTERVAL[0]:+.0f}% to "
          f"{INTERVAL[1]:+.0f}%  D. Hug")
    return 0


if __name__ == "__main__":
    sys.exit(main())
