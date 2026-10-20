"""Generate dot-matrix SHEWART banners (dark + light) as animated SVGs."""
import sys
from pathlib import Path

GLYPHS = {
    "S": [".###.", "#...#", "#....", ".###.", "....#", "#...#", ".###."],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"],
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
}
WORD = "SHEWART"
PAD = 2          # unlit dots around the word
PITCH = 18       # px between dot centres
R = 6.2          # dot radius
MARGIN = 28      # space between grid and card edge

THEMES = {
    "dark":  dict(bg="#0A0A0A", border="#1F1F1F", off="#1C1C1C", on="#FAFAFA", glow=0.55),
    "light": dict(bg="#FFFFFF", border="#E5E5E5", off="#EFEFEF", on="#0A0A0A", glow=0.0),
}


def grid():
    rows = [""] * 7
    for i, ch in enumerate(WORD):
        for r in range(7):
            rows[r] += GLYPHS[ch][r] + ("." if i < len(WORD) - 1 else "")
    width = len(rows[0]) + PAD * 2
    blank = "." * width
    body = ["." * PAD + row + "." * PAD for row in rows]
    return [blank] * PAD + body + [blank] * PAD


def svg(theme):
    t = THEMES[theme]
    g = grid()
    cols, rows = len(g[0]), len(g)
    w = cols * PITCH + MARGIN * 2
    h = rows * PITCH + MARGIN * 2
    ox = oy = MARGIN + PITCH / 2

    off, on = [], []
    for y, row in enumerate(g):
        for x, cell in enumerate(row):
            cx, cy = ox + x * PITCH, oy + y * PITCH
            if cell == "#":
                on.append(f'<circle class="d c{x}" cx="{cx:g}" cy="{cy:g}" r="{R}"/>')
            else:
                off.append(f'<circle cx="{cx:g}" cy="{cy:g}" r="{R}"/>')

    lit_cols = sorted({x for row in g for x, c in enumerate(row) if c == "#"})
    delays = "\n".join(
        f"    .c{x}{{animation-delay:{0.15 + i * 0.035:.3f}s,{2.4 + i * 0.045:.3f}s}}"
        for i, x in enumerate(lit_cols)
    )

    glow = ""
    glow_use = ""
    if t["glow"]:
        glow = f"""
  <filter id="glow" x="-10%" y="-30%" width="120%" height="160%">
    <feGaussianBlur stdDeviation="5"/>
  </filter>"""
        glow_use = f'<g class="glow" fill="{t["on"]}" filter="url(#glow)">{"".join(on)}</g>'

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="Shewart">
  <title>Shewart</title>
  <defs>{glow}
  </defs>
  <style>
    .d{{opacity:0;transform-box:fill-box;transform-origin:center;
       animation:in .55s cubic-bezier(.2,.8,.2,1) both,wave 7s ease-in-out infinite}}
{delays}
    .glow{{opacity:0;animation:glow 1.2s ease-out 1s both}}
    @keyframes glow{{to{{opacity:{t["glow"] * 0.45:g}}}}}
    @keyframes in{{from{{opacity:0;transform:scale(.3)}}to{{opacity:1;transform:scale(1)}}}}
    @keyframes wave{{0%,12%,100%{{opacity:1}}6%{{opacity:.3}}}}
    @media (prefers-reduced-motion:reduce){{.d{{animation:none;opacity:1}}.glow{{animation:none;opacity:{t["glow"] * 0.45:g}}}}}
  </style>
  <rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="22" fill="{t["bg"]}" stroke="{t["border"]}"/>
  <g fill="{t["off"]}">{"".join(off)}</g>
  {glow_use}
  <g fill="{t["on"]}">{"".join(on)}</g>
</svg>
"""


if __name__ == "__main__":
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    for name in THEMES:
        (out / f"header-{name}.svg").write_text(svg(name), encoding="utf-8")
        print(out / f"header-{name}.svg")
