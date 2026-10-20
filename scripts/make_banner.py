"""Generate "< Shewart />" banners (dark + light) styled as a GitHub contribution graph.

The name is drawn in the busiest green; every other cell is a quieter day.

    python scripts/make_banner.py assets          # single-line strokes (7 rows, like the real graph)
    python scripts/make_banner.py assets 2        # double-line strokes
    python scripts/make_banner.py assets 3        # triple-line strokes
"""
import random
import sys
from pathlib import Path

GLYPHS = {
    "<": ["...", "..#", ".#.", "#..", ".#.", "..#", "..."],
    ">": ["...", "#..", ".#.", "..#", ".#.", "#..", "..."],
    "/": ["..#", "..#", ".#.", ".#.", ".#.", "#..", "#.."],
    " ": [""] * 7,
    "S": [".###.", "#...#", "#....", ".###.", "....#", "#...#", ".###."],
    "h": ["#...", "#...", "###.", "#..#", "#..#", "#..#", "#..#"],
    "e": ["....", "....", ".##.", "#..#", "####", "#...", ".###"],
    "w": [".....", ".....", "#...#", "#...#", "#.#.#", "#.#.#", ".#.#."],
    "a": ["....", "....", ".##.", "...#", ".###", "#..#", ".###"],
    "r": ["....", "....", "#.##", "##..", "#...", "#...", "#..."],
    "t": [".#.", ".#.", "###", ".#.", ".#.", ".#.", "..#"],
}
WORD = "< Shewart />"
WEEKS = 53       # columns in a year of the real graph
GRID_W = 800     # px available for cells
SEED = 23

# GitHub's contribution levels 0-4
THEMES = {
    "dark": dict(bg="#0D1117", border="#30363D", text="#7D8590",
                 levels=["#161B22", "#0E4429", "#006D32", "#26A641", "#39D353"]),
    "light": dict(bg="#FFFFFF", border="#D0D7DE", text="#656D76",
                  levels=["#EBEDF0", "#9BE9A8", "#40C463", "#30A14E", "#216E39"]),
}
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"


def word_mask(weight):
    rows = []
    for r in range(7):
        line = ""
        for i, ch in enumerate(WORD):
            line += GLYPHS[ch][r] + ("." if i < len(WORD) - 1 else "")
        rows.append(line)
    return ["".join(c * weight for c in row) for row in rows for _ in range(weight)]


def levels(weight):
    """Cell level for every (row, col): name at 4, the rest quiet."""
    mask = word_mask(weight)
    rows = len(mask)
    cols = max(WEEKS, len(mask[0]) + 4 * weight)
    left = (cols - len(mask[0])) // 2
    rng = random.Random(SEED)

    def lit(r, c):
        c -= left
        return 0 <= c < len(mask[0]) and mask[r][c] == "#"

    grid = []
    for r in range(rows):
        row = []
        for c in range(cols):
            if lit(r, c):
                row.append(4)
                continue
            # distance to the nearest letter cell, so activity fades in away from the name
            dist = next((d for d in range(1, 3 * weight + 1)
                         if any(lit(r + dr, c + dc)
                                for dr in range(-d, d + 1) for dc in range(-d, d + 1)
                                if 0 <= r + dr < rows)), None)
            roll = rng.random()
            if dist is not None and dist <= weight:
                row.append(0)
            elif dist is not None and dist <= 2 * weight:
                row.append(1 if roll < 0.14 else 0)
            else:
                row.append(2 if roll < 0.05 else 1 if roll < 0.28 else 0)
        grid.append(row)
    return grid


def svg(theme, weight):
    t = THEMES[theme]
    grid = levels(weight)
    rows, cols = len(grid), len(grid[0])
    pitch = GRID_W / cols
    cell = pitch * 0.78
    rx = max(cell * 0.2, 1)

    label_w = 34 if weight == 1 else 0
    pad, top, bottom = 24, 30, 34
    gx, gy = pad + label_w, pad + top
    w = gx + cols * pitch + pad
    h = gy + rows * pitch + bottom + pad - 12

    cells = []
    for r, row in enumerate(grid):
        for c, lvl in enumerate(row):
            cls = f"k c{c}" + (" n" if lvl >= 3 else "")
            cells.append(
                f'<rect class="{cls}" x="{gx + c * pitch:.2f}" y="{gy + r * pitch:.2f}" '
                f'width="{cell:.2f}" height="{cell:.2f}" rx="{rx:.2f}" fill="{t["levels"][lvl]}"/>'
            )

    delays = "\n".join(
        f"    .c{c}{{animation-delay:{0.1 + c * 0.018:.3f}s}}"
        f".n.c{c}{{animation-delay:{0.1 + c * 0.018:.3f}s,{2.6 + c * 0.03:.3f}s}}"
        for c in range(cols)
    )

    text = []
    for i, m in enumerate(MONTHS):
        x = gx + (i * cols / 12) * pitch
        text.append(f'<text x="{x:.1f}" y="{gy - 10}">{m}</text>')
    if weight == 1:
        for r, d in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
            text.append(f'<text x="{pad}" y="{gy + r * pitch + cell * 0.85:.1f}">{d}</text>')

    lg = 11
    ly = gy + rows * pitch + 14
    lx = gx + cols * pitch - (5 * (lg + 4)) - 34
    text.append(f'<text x="{lx - 32:.1f}" y="{ly + lg - 1.5:.1f}">Less</text>')
    legend = "".join(
        f'<rect x="{lx + i * (lg + 4):.1f}" y="{ly:.1f}" width="{lg}" height="{lg}" rx="2" fill="{t["levels"][i]}"/>'
        for i in range(5)
    )
    text.append(f'<text x="{lx + 5 * (lg + 4) + 4:.1f}" y="{ly + lg - 1.5:.1f}">More</text>')

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" width="{w:.0f}" height="{h:.0f}" role="img" aria-label="&lt; Shewart /&gt;">
  <title>&lt; Shewart /&gt;</title>
  <style>
    .k{{opacity:0;animation:in .4s ease-out both}}
    .n{{animation:in .4s ease-out both,pulse 8s ease-in-out infinite}}
{delays}
    @keyframes in{{from{{opacity:0}}to{{opacity:1}}}}
    @keyframes pulse{{0%,10%,100%{{opacity:1}}5%{{opacity:.7}}}}
    @media (prefers-reduced-motion:reduce){{.k,.n{{animation:none;opacity:1}}}}
    text{{font:12px {FONT};fill:{t["text"]}}}
  </style>
  <rect x=".5" y=".5" width="{w - 1:.0f}" height="{h - 1:.0f}" rx="12" fill="{t["bg"]}" stroke="{t["border"]}"/>
  {"".join(text)}
  {legend}
  {"".join(cells)}
</svg>
"""


if __name__ == "__main__":
    out = Path(sys.argv[1])
    weight = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    out.mkdir(parents=True, exist_ok=True)
    for name in THEMES:
        path = out / f"header-{name}.svg"
        path.write_text(svg(name, weight), encoding="utf-8")
        print(path, f"{path.stat().st_size // 1024} KB")
