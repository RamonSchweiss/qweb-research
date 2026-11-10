"""Figure for "What the Partitioner Stops Solving": who finds the optimum?

Emits calculations/partitioner_figure.svg. No arguments.

Every number below is printed by findability.py and findability_large.py and is
copied here rather than recomputed, so that the figure and the measurement
cannot drift apart silently: if either script's output changes, this file no
longer matches it and the mismatch shows up in a diff.

The axis needs explaining, because the honest thing and the convenient thing
differ here. Mean gaps run from 0.05 to 16.10 remote gates, which is four
orders of nothing on a linear axis - so the axis is logarithmic. But
Kernighan-Lin and METIS are at EXACTLY zero at almost every size, and a log
axis has no place for zero. Plotting them at some small positive value would
turn a clean zero into a small number, which is precisely the kind of quiet
substitution this article is about. So the zeros get a rail of their own below
the log region, with a break between, and the rail is labelled for what it is.

Provenance of each series:

  KL, SPECTRAL, GREEDY, STOCH    ours, findability.py (n = 10..24) and
                                 findability_large.py (n = 26, 28)
  METIS                          ours, same scripts. Hollow markers from
                                 n = 20: some answers were not balanced
                                 bipartitions and are excluded from the mean,
                                 so the zero there is over fewer graphs.
  RANDOM                         ours. A random balanced assignment - the
                                 baseline arXiv 2605.01974 normalises seven
                                 partitioners against.

Graph counts: 21 per size to n = 24, then 20, because
partition_topology.make_graph finds no connected scale-free graph at seed 2
with exactly m edges at n = 26 and n = 28.

The caption the figure is published with, kept here so that it travels with the
values it describes:

  Figure 1. Mean gap to the exact minimum balanced gate cut, in remote
  two-qubit gates, against register size. Kernighan-Lin and METIS sit on the
  "exactly zero" rail: that is a true zero, not a small number, which is why it
  is not on the logarithmic axis. METIS is drawn hollow from n = 20, where some
  of its answers are no longer balanced bipartitions and are excluded from the
  mean - it is off by exactly one vertex every time. Kernighan-Lin is measured
  at twenty restarts; at one restart it misses in 2 of 21 graphs at n = 18. The
  random balanced assignment at the top is the baseline the literature
  normalises against. Twenty-one graphs per size to n = 24 and twenty beyond,
  from calculations/findability.py and findability_large.py.

Ramon Schweiss, QWeb (c) Research, 11 November 2026.
"""
import sys
import math

N = [10, 12, 14, 16, 18, 20, 22, 24, 26, 28]
SERIES = [
    ("random",       [4.57, 6.19, 7.05, 7.76, 9.57, 10.33, 12.29, 14.24, 14.90, 16.10], "#718096"),
    ("greedy",       [0.95, 1.52, 1.57, 1.76, 2.19, 2.38, 3.10, 2.48, 2.80, 3.40], "#9b2c2c"),
    ("spectral",     [0.24, 0.33, 0.62, 1.29, 0.48, 0.71, 1.24, 1.10, 1.50, 0.90], "#b7791f"),
    ("stoch. greedy", [0.00, 0.00, 0.29, 0.19, 0.52, 0.38, 0.67, 0.86, 0.70, 0.80], "#2b6cb0"),
    ("METIS",        [0.00, 0.05, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00], "#6b46c1"),
    ("Kernighan–Lin", [0.0] * 10, "#276749"),
]
METIS_UNBALANCED = [0, 0, 0, 0, 0, 5, 8, 4, 9, 2]

W, H = 980, 620
LX, RX = 108, 790                 # plot area, x
TOP, BOT = 116, 400               # log region, y
RAIL = 452                        # the "exactly zero" rail
LO, HI = 0.05, 20.0               # log range


def x(n):
    return LX + (n - N[0]) / (N[-1] - N[0]) * (RX - LX)


def y(v):
    lv = (math.log10(v) - math.log10(LO)) / (math.log10(HI) - math.log10(LO))
    return BOT - lv * (BOT - TOP)


def main():
    p = []
    a = p.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
      f'font-family="Georgia, serif" font-size="14">')
    a('<style>'
      '.ax{stroke:#333;stroke-width:1.2}.tick{stroke:#999;stroke-width:1}'
      '.grid{stroke:#e8e8e8;stroke-width:1}'
      '.lbl{fill:#333}.dim{fill:#777;font-size:12.5}'
      '.ttl{font-size:19px;fill:#111}.sub{font-size:13px;fill:#666}'
      '</style>')
    a(f'<rect width="{W}" height="{H}" fill="#fff"/>')

    a(f'<text x="{LX}" y="46" class="ttl">Who finds the exact minimum '
      f'balanced cut?</text>')
    a(f'<text x="{LX}" y="68" class="sub">Mean gap in remote two-qubit gates. '
      f'Twenty-one graphs per size to n = 24, twenty beyond.</text>')

    # log grid and ticks
    for v in (0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 20):
        a(f'<line x1="{LX}" y1="{y(v):.1f}" x2="{RX}" y2="{y(v):.1f}" '
          f'class="grid"/>')
        a(f'<text x="{LX-10}" y="{y(v)+4:.1f}" class="dim" '
          f'text-anchor="end">{v:g}</text>')
    a(f'<line x1="{LX}" y1="{TOP}" x2="{LX}" y2="{BOT}" class="ax"/>')

    # the axis break, then the rail for exact zeros
    for dy in (0, 7):
        a(f'<path d="M{LX-8} {BOT+18+dy} l8 -5 l8 5" fill="none" '
          f'stroke="#333" stroke-width="1.2"/>')
    a(f'<line x1="{LX}" y1="{RAIL}" x2="{RX}" y2="{RAIL}" class="ax"/>')
    a(f'<text x="{LX-10}" y="{RAIL+4}" class="dim" text-anchor="end">0</text>')
    a(f'<text x="{RX}" y="{RAIL-12}" class="dim" font-style="italic" '
      f'text-anchor="end">exactly zero — a true zero, not a small '
      f'number</text>')

    # x axis
    for n in N:
        a(f'<line x1="{x(n):.1f}" y1="{RAIL}" x2="{x(n):.1f}" y2="{RAIL+6}" '
          f'class="tick"/>')
        a(f'<text x="{x(n):.1f}" y="{RAIL+22}" class="dim" '
          f'text-anchor="middle">{n}</text>')
    a(f'<text x="{(LX+RX)/2:.0f}" y="{RAIL+46}" class="dim" '
      f'text-anchor="middle">register size n</text>')

    # series
    labels = []
    for name, vals, colour in SERIES:
        pts = []
        for n, v in zip(N, vals):
            pts.append((x(n), RAIL if v <= 0 else y(v), v <= 0))
        # connect, dashing any segment that crosses the break
        for (x1, y1, z1), (x2, y2, z2) in zip(pts, pts[1:]):
            dash = ' stroke-dasharray="4,4"' if z1 != z2 else ''
            a(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" '
              f'y2="{y2:.1f}" stroke="{colour}" stroke-width="2"{dash} '
              f'opacity="0.85"/>')
        for i, (px, py, _) in enumerate(pts):
            hollow = (name == "METIS" and METIS_UNBALANCED[i] > 0)
            if hollow:
                a(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5" fill="#fff" '
                  f'stroke="{colour}" stroke-width="2"/>')
            else:
                a(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4.2" '
                  f'fill="{colour}"/>')
        labels.append([pts[-1][1], name, colour])

    # right-hand labels, pushed apart so that no two overlap
    # anything sitting on the zero rail is stacked UPWARDS, or it would land
    # in the row of x-axis tick labels
    rail = [r for r in labels if r[0] >= RAIL - 1]
    rest = [r for r in labels if r[0] < RAIL - 1]
    for i, r in enumerate(rail):
        r[0] = RAIL - 6 - 19 * i
    rest.sort(key=lambda r: r[0])
    for i in range(1, len(rest)):
        if rest[i][0] - rest[i - 1][0] < 19:
            rest[i][0] = rest[i - 1][0] + 19
    for ly, name, colour in rest + rail:
        a(f'<text x="{RX+12}" y="{ly+4:.1f}" class="lbl" fill="{colour}">'
          f'{name}</text>')

    # the one thing the hollow markers mean
    a(f'<circle cx="{LX+6}" cy="{RAIL+74}" r="5" fill="#fff" '
      f'stroke="#6b46c1" stroke-width="2"/>')
    a(f'<text x="{LX+20}" y="{RAIL+78}" class="dim">hollow: some METIS '
      f'answers were not balanced and are excluded from the mean</text>')

    y0 = 576
    a(f'<text x="{LX}" y="{y0}" class="lbl">Kernighan–Lin reaches the exact '
      f'optimum everywhere, at twenty restarts; at one restart it misses twice '
      f'at n = 18.</text>')
    a(f'<text x="{LX}" y="{y0+21}" class="lbl">METIS matches it — and from '
      f'n = 20 some of its answers are no longer balanced at all.</text>')
    a('</svg>')

    out = "partitioner_figure.svg"
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(p) + "\n")
    print(f"wrote {out}")
    for name, vals, _ in SERIES:
        print(f"  {name:16s} {vals[0]:5.2f} -> {vals[-1]:5.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
