"""The figure of "What a Registered Rule Assumes".

Emits figures/out/d_blind_spot.svg. Light palette by default, --dark renders
the same plate in the house teaser palette.

One plate, drawn for section 08. Meta-research on pre-registration measures two
quantities. How VAGUE a registration is, which is what strictness and
specificity instruments score. And how far a study DEPARTS from its plan, which
is what plan-to-study consistency and deviation reporting score. Both are real
and both are worth measuring.

The plate puts them on two axes and marks where the four cases of this article
sit: in the corner where a registration is perfectly precise and was followed
exactly. Both instruments read clean there, because both measure a distance
between the plan and what was done, and in all four cases that distance was
zero. The error was inside the plan.

Nothing here is computed. The axes are qualitative and the plate says so; the
only quantity on it is the count of four, which is from the article.

Ramon Schweiss, QWeb (c) Research, 27 November 2026.
"""
import os
import sys

W, H = 760, 500
DARK = "--dark" in sys.argv

if DARK:
    BG, INK, MUTED, GRID, ACCENT = ("#0d1b33", "#ffffff", "#8fa8c8",
                                    "#3f5a80", "#f0a06a")
    PANEL = "#16294a"
else:
    BG, INK, MUTED, GRID, ACCENT = ("#ffffff", "#15243d", "#6b7f9c",
                                    "#d4dce8", "#c2651f")
    PANEL = "#f4f6fa"

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")

L, R, T, B = 108, 724, 74, 386        # plot box


def write(name, body):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(body + "</svg>\n")
    print(f"wrote {path}")


def head():
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
            f'font-family="DejaVu Serif" role="img" aria-label="{ALT}">'
            f'<rect width="{W}" height="{H}" fill="{BG}"/>')


ALT = ("Two axes: how vague a registration is, and how far a study departs "
       "from its plan. Three corners are covered by existing instruments. The "
       "fourth, where the plan is precise and was followed exactly, is where "
       "the four mis-specified rules of this article sit, and neither "
       "instrument reads anything there.")


def main():
    p = [head()]
    a = p.append
    mx, my = (L + R) / 2, (T + B) / 2

    a(f'<text x="{L}" y="40" font-size="16.5" fill="{INK}" '
      f'font-weight="bold">What meta-research measures, and the corner it '
      f'does not reach</text>')

    # the three covered quadrants, then the blind one
    a(f'<rect x="{mx}" y="{T}" width="{R-mx}" height="{my-T}" '
      f'fill="{PANEL}"/>')
    a(f'<rect x="{L}" y="{T}" width="{mx-L}" height="{my-T}" '
      f'fill="{PANEL}"/>')
    a(f'<rect x="{mx}" y="{my}" width="{R-mx}" height="{B-my}" '
      f'fill="{PANEL}"/>')
    a(f'<rect x="{L}" y="{T}" width="{R-L}" height="{B-T}" fill="none" '
      f'stroke="{GRID}" stroke-width="1.4"/>')
    a(f'<line x1="{mx}" y1="{T}" x2="{mx}" y2="{B}" stroke="{GRID}" '
      f'stroke-width="1.2" stroke-dasharray="4,4"/>')
    a(f'<line x1="{L}" y1="{my}" x2="{R}" y2="{my}" stroke="{GRID}" '
      f'stroke-width="1.2" stroke-dasharray="4,4"/>')

    quad = [
        (L + 20, T + 30, "vague, and followed",
         "strictness instruments see it"),
        (mx + 20, T + 30, "vague, and departed from",
         "both instruments see it"),
        (mx + 20, my + 30, "precise, and departed from",
         "consistency instruments see it"),
    ]
    for x, y, t1, t2 in quad:
        a(f'<text x="{x}" y="{y}" font-size="13.5" fill="{INK}">{t1}</text>')
        a(f'<text x="{x}" y="{y+20}" font-size="12.5" fill="{MUTED}">'
          f'{t2}</text>')

    # the blind corner
    a(f'<text x="{L+20}" y="{my+30}" font-size="13.5" fill="{ACCENT}" '
      f'font-weight="bold">precise, and followed exactly</text>')
    a(f'<text x="{L+20}" y="{my+50}" font-size="12.5" fill="{ACCENT}">'
      f'neither instrument reads anything here</text>')

    labels = ["threshold inside its own noise", "rule checked in the wrong "
              "place", "inference the model does not support",
              "comparison with no resolution rule"]
    for i, lab in enumerate(labels):
        cy = my + 78 + i * 22
        a(f'<circle cx="{L+30}" cy="{cy-4}" r="5" fill="{ACCENT}"/>')
        a(f'<text x="{L+44}" y="{cy}" font-size="12.5" fill="{INK}">'
          f'{lab}</text>')

    a(f'<text x="{L}" y="{B+28}" font-size="12.5" fill="{MUTED}">followed '
      f'exactly</text>')
    a(f'<text x="{R}" y="{B+28}" font-size="12.5" fill="{MUTED}" '
      f'text-anchor="end">departed from</text>')
    a(f'<text x="{mx}" y="{B+50}" font-size="13" fill="{INK}" '
      f'text-anchor="middle">distance between the plan and what was '
      f'done</text>')
    a(f'<text x="{L-16}" y="{T+14}" font-size="12.5" fill="{MUTED}" '
      f'text-anchor="end">vague</text>')
    a(f'<text x="{L-16}" y="{B}" font-size="12.5" fill="{MUTED}" '
      f'text-anchor="end">precise</text>')
    a(f'<text x="28" y="{my}" font-size="13" fill="{INK}" '
      f'text-anchor="middle" transform="rotate(-90 28 {my})">how the plan is '
      f'written</text>')

    a(f'<text x="{L}" y="{H-34}" font-size="12.5" fill="{MUTED}">The four '
      f'cases of this article all sit in the lower left corner: each rule was '
      f'precise,</text>')
    a(f'<text x="{L}" y="{H-16}" font-size="12.5" fill="{MUTED}">each was '
      f'followed exactly as written, and each was wrong as written.</text>')

    write("d_blind_spot.svg", "".join(p))
    return 0


if __name__ == "__main__":
    sys.exit(main())
