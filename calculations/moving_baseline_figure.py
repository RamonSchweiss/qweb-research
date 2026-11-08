"""Figure for "What Moves the Baseline": which side of a crossover moves?

Emits calculations/moving_baseline_figure.svg. No arguments.

Every number below is printed by calculations/basket_grid_sensitivity.py and is
copied here rather than recomputed, so that the figure and the calculation
cannot drift apart silently: if the script's output changes, this file no longer
matches it and the mismatch is visible in a diff.

Provenance of each value, stated because the figure makes a claim about
attribution:

  TRUNC_FAMILY   this script's own measurement. The contribution of the
                 CLASSICAL side to the crossover, across the disclosed
                 truncation family, +-3 sigma to +-5 sigma. Sign flips between
                 +-3.75 and +-4.
  EQUIPROB       measured, but OUTSIDE the disclosed family: equal-probability
                 bins do not reproduce the reference prices at r = 3%, so this
                 bounds nothing. Drawn hollow for that reason.
  OBSERVED       reported by Daniel Hug (qubit-lab.ch) for his own measurement:
                 the crossover moves from about 8,100 to 9,600 oracle calls at
                 200 repetitions. Not our number.
  INTERVAL       likewise reported: the 90% interval on that move. The script
                 puts the repetitions needed to lift its lower bound to zero at
                 about 600; the reading line below quotes that figure and must
                 be changed with it.
  PREDICTED      this script's prediction from the reported 13.35% smaller
                 amplitude, with amplitude estimation's 1/sqrt(a) scaling.
  SUPERSEDED     what this script said until 1 November 2026, using 1/a. It
                 matched a reported +43% to within a point, and that agreement
                 was two errors cancelling. Drawn because leaving it out would
                 make the figure tidier than the history.

The caption the figure is published with, kept here because the first time it
was handed to a CMS the instruction said to preserve it and no caption existed:

  Figure 1. Which side of the crossover moves? Shift in the quantum/classical
  crossover, in per cent, for a basket option on an 8-qubit grid. Each row
  carries one claim. The classical truncation family (blue) covers the whole
  disclosed range, +-3 sigma to +-5 sigma, and changes sign near +-3.9 sigma;
  the hollow marker is an equal-probability binning, which sits outside that
  family and bounds nothing. The observed move and its 90% interval are
  reported by Daniel Hug (qubit-lab.ch) about his own measurement, and the
  interval contains zero. The prediction at 1/sqrt(a) and the superseded value
  at 1/a are ours. Every plotted value comes from
  calculations/basket_grid_sensitivity.py.

Ramon Schweiss, QWeb (c) Research, 8 November 2026.
"""
import sys

TRUNC_FAMILY = [(3.0, 3.2), (3.25, 1.8), (3.5, 1.0), (3.75, 0.4),
                (4.0, -0.1), (4.5, -0.3), (5.0, -0.3)]
EQUIPROB = 10.6
OBSERVED = 19.0
INTERVAL = (-12.0, 52.0)
PREDICTED = 20.0
SUPERSEDED = 42.0

W, H = 980, 520
L, R = 90, 900                      # plot area, x
AX = 400                            # axis baseline, y
LO, HI = -20.0, 58.0                # axis range in per cent

# one lane per claim, so that nothing has to share a row with anything else
Y_SUP, Y_PRED, Y_OBS, Y_FAM, Y_EQ = 150, 212, 272, 330, 372


def x(v):
    return L + (v - LO) / (HI - LO) * (R - L)


def pc(v, dec=0):
    """Per cent with a typographic minus, so the figure reads consistently."""
    return f"{v:+.{dec}f}%".replace("-", "−")


def main():
    p = []
    a = p.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
      f'font-family="Georgia, serif" font-size="14">')
    a('<style>'
      '.ax{stroke:#333;stroke-width:1.2}'
      '.tick{stroke:#999;stroke-width:1}'
      '.lbl{fill:#333}.dim{fill:#777;font-size:12.5}'
      '.ttl{font-size:19px;fill:#111}.sub{font-size:13px;fill:#666}'
      '.band{fill:#2b6cb0;opacity:.14}'
      '.ivl{stroke:#b7791f;stroke-width:7;opacity:.30;stroke-linecap:butt}'
      '</style>')
    a(f'<rect width="{W}" height="{H}" fill="#fff"/>')

    a(f'<text x="{L}" y="46" class="ttl">Which side of the crossover moves?</text>')
    a(f'<text x="{L}" y="68" class="sub">Shift in the quantum/classical '
      f'crossover, in per cent. Basket option, 8-qubit grid.</text>')

    # zero line and axis
    a(f'<line x1="{L}" y1="{AX}" x2="{R}" y2="{AX}" class="ax"/>')
    for v in (-20, -10, 0, 10, 20, 30, 40, 50):
        a(f'<line x1="{x(v):.1f}" y1="{AX}" x2="{x(v):.1f}" y2="{AX+6}" '
          f'class="tick"/>')
        a(f'<text x="{x(v):.1f}" y="{AX+24}" class="dim" '
          f'text-anchor="middle">{pc(v)}</text>')
    a(f'<line x1="{x(0):.1f}" y1="{Y_SUP-30}" x2="{x(0):.1f}" y2="{AX+6}" '
      f'stroke="#333" stroke-width="1" stroke-dasharray="2,3"/>')

    # lane 1 - superseded, ours, wrong until 1 November
    a(f'<circle cx="{x(SUPERSEDED):.1f}" cy="{Y_SUP}" r="5" fill="none" '
      f'stroke="#9b2c2c" stroke-width="1.4"/>')
    a(f'<text x="{x(SUPERSEDED):.1f}" y="{Y_SUP-16}" class="dim" '
      f'text-anchor="middle" fill="#9b2c2c">ours until 1 Nov, at 1/a: '
      f'{pc(SUPERSEDED)}</text>')

    # lane 2 - predicted, ours
    a(f'<circle cx="{x(PREDICTED):.1f}" cy="{Y_PRED}" r="5.5" '
      f'fill="#276749"/>')
    a(f'<text x="{x(PREDICTED):.1f}" y="{Y_PRED-16}" class="lbl" '
      f'text-anchor="middle">predicted from the amplitude, at 1/√a: '
      f'{pc(PREDICTED)}</text>')

    # lane 3 - observed, reported by D. Hug, with its 90% interval
    a(f'<line x1="{x(INTERVAL[0]):.1f}" y1="{Y_OBS}" '
      f'x2="{x(INTERVAL[1]):.1f}" y2="{Y_OBS}" class="ivl"/>')
    for v in INTERVAL:
        a(f'<line x1="{x(v):.1f}" y1="{Y_OBS-8}" x2="{x(v):.1f}" '
          f'y2="{Y_OBS+8}" stroke="#b7791f" stroke-width="1.4" '
          f'opacity=".65"/>')
    a(f'<circle cx="{x(OBSERVED):.1f}" cy="{Y_OBS}" r="6" fill="#b7791f"/>')
    a(f'<text x="{x(OBSERVED):.1f}" y="{Y_OBS-16}" class="lbl" '
      f'text-anchor="middle">observed {pc(OBSERVED)}, reported</text>')
    # anchored at the bar's right end and running left, to keep clear of the
    # dashed zero line
    a(f'<text x="{x(INTERVAL[1]):.1f}" y="{Y_OBS+26}" class="dim" '
      f'text-anchor="end">90% interval at 200 repetitions, '
      f'{pc(INTERVAL[0])} to {pc(INTERVAL[1])} — it contains zero</text>')

    # lane 4 - the whole classical truncation family, ours
    a(f'<rect x="{x(-0.3)-7:.1f}" y="{Y_FAM-20}" '
      f'width="{x(3.2)-x(-0.3)+14:.1f}" height="40" class="band"/>')
    for s, v in TRUNC_FAMILY:
        a(f'<circle cx="{x(v):.1f}" cy="{Y_FAM}" r="4.2" fill="#2b6cb0"/>')
    a(f'<text x="{x(3.2)+18:.1f}" y="{Y_FAM-5}" class="lbl">'
      f'the whole classical truncation family, ±3σ to ±5σ</text>')
    a(f'<text x="{x(3.2)+18:.1f}" y="{Y_FAM+14}" class="dim">'
      f'+3.2% down to −0.3%, sign flipping near ±3.9σ — our measurement</text>')

    # lane 5 - equiprobable bins, measured but outside the family
    a(f'<circle cx="{x(EQUIPROB):.1f}" cy="{Y_EQ}" r="5" fill="none" '
      f'stroke="#2b6cb0" stroke-width="1.6" stroke-dasharray="3,2"/>')
    a(f'<text x="{x(EQUIPROB)+14:.1f}" y="{Y_EQ+4}" class="dim">'
      f'equiprobable bins — outside the disclosed family, bounds '
      f'nothing</text>')

    # the reading
    y0 = AX + 58
    a(f'<text x="{L}" y="{y0}" class="lbl">The classical side accounts for at '
      f'most a sixth of the observed move. The cause sits on the quantum side: '
      f'a 13.35% smaller</text>')
    a(f'<text x="{L}" y="{y0+21}" class="lbl">amplitude, at 1/√a, predicts the '
      f'move almost exactly. And the move itself is not resolved at 200 '
      f'repetitions —</text>')
    a(f'<text x="{L}" y="{y0+42}" class="lbl">its interval contains zero. '
      f'About 600 repetitions would put the lower bound above it.</text>')
    a('</svg>')

    out = "moving_baseline_figure.svg"
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(p) + "\n")
    print(f"wrote {out}")
    print("\nValues drawn, with provenance:")
    print(f"  classical truncation family  {TRUNC_FAMILY[0][1]:+.1f}% .. "
          f"{TRUNC_FAMILY[-1][1]:+.1f}%   ours")
    print(f"  equiprobable, outside family {EQUIPROB:+.1f}%          ours, "
          f"bounds nothing")
    print(f"  observed move                {OBSERVED:+.1f}%          "
          f"reported by D. Hug")
    print(f"  90% interval                 {INTERVAL[0]:+.0f}% to "
          f"{INTERVAL[1]:+.0f}%   reported by D. Hug")
    print(f"  predicted at 1/sqrt(a)       {PREDICTED:+.1f}%          ours")
    print(f"  superseded, at 1/a           {SUPERSEDED:+.1f}%          "
          f"ours, wrong until 1 Nov")
    return 0


if __name__ == "__main__":
    sys.exit(main())
