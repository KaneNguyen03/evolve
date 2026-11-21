"""Generate Evolve brand SVGs (logo, banner, social preview, diagrams) in light/dark themes.

The brand is monochrome: black, white, and two grays. Nothing here uses color.

Usage:  python3 tools/brand/generate.py assets
PNG exports (mark, avatar, social preview) need cairosvg; see docs/brand.md.
"""
import math
import os
import sys
from xml.sax.saxutils import escape

OUT = sys.argv[1]

BLACK, WHITE = "#000000", "#FFFFFF"
THEMES = {
    "dark": dict(bg=BLACK, text=WHITE, muted="#A3A3A3", card="#111111", card_stroke="#333333",
                 line="#737373", soft="#262626"),
    "light": dict(bg=WHITE, text=BLACK, muted="#525252", card=WHITE, card_stroke="#D4D4D4",
                  line="#8A8A8A", soft="#F0F0F0"),
}
SANS = "Inter, 'Segoe UI', -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', 'SFMono-Regular', Menlo, Consolas, 'DejaVu Sans Mono', monospace"


def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{escape(title)}">\n<title>{escape(title)}</title>\n{body}\n</svg>\n')


def text(x, y, s, size, fill, weight=400, anchor="start", family=SANS, extra=""):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}" {extra}>{escape(s)}</text>')


def mark(x, y, size, ink):
    """The Evolve mark: a geometric lowercase e whose tail is a separate dot.

    The ring and crossbar are the current program. The dot sits in the e's opening,
    not yet joined: the next variant, the experiment that may or may not survive.
    Drawn on a 256 grid; one color, no effects.
    """
    s = size / 256
    c, r, w = 128, 84, 30                     # center, ring radius, stroke weight
    end = math.radians(-58)                   # where the ring stops, below the bar
    ex, ey = c + r * math.cos(end), c - r * math.sin(end)
    dot = math.radians(-32)                   # the detached dot, inside the opening
    dx, dy = c + r * math.cos(dot), c - r * math.sin(dot)
    # The ring starts on the crossbar's centerline, so its end is hidden under the bar,
    # and the bar ends where its corners touch the ring's outer edge.
    sx, sy = c + r, c
    bar_end = c + math.sqrt((r + w / 2) ** 2 - (w / 2) ** 2)
    return "\n".join([
        f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.4f})" fill="none" stroke="{ink}" stroke-width="{w}">',
        f'<path d="M{sx:.1f},{sy:.1f} A{r},{r} 0 1 0 {ex:.1f},{ey:.1f}"/>',
        f'<line x1="{c - r}" y1="{c}" x2="{bar_end:.1f}" y2="{c}"/>',
        f'<circle cx="{dx:.1f}" cy="{dy:.1f}" r="{w / 2}" fill="{ink}" stroke="none"/>',
        '</g>',
    ])


def backdrop(w, h, t, rx=28):
    stroke = f' stroke="{t["card_stroke"]}" stroke-width="1"' if t["bg"] == WHITE else ""
    return f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="{rx}" fill="{t["bg"]}"{stroke}/>'


LOOP = ["observe", "vary", "measure", "select", "remember"]


def loop_chips(x, y, t, size=16):
    cw = size * 0.62
    parts = []
    for i, word in enumerate(LOOP):
        w = len(word) * cw + 28
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{size * 2.2:.1f}" rx="{size * 1.1:.1f}" '
                     f'fill="none" stroke="{t["text"]}" stroke-width="1.5"/>')
        parts.append(text(x + w / 2, y + size * 1.48, word, size, t["text"], 600, "middle", MONO))
        x += w
        if i < len(LOOP) - 1:
            my = y + size * 1.1
            parts.append(f'<path d="M{x + 8:.1f},{my:.1f} H{x + 21:.1f} M{x + 16:.1f},{my - 5:.1f} L{x + 22:.1f},{my:.1f} '
                         f'L{x + 16:.1f},{my + 5:.1f}" fill="none" stroke="{t["muted"]}" stroke-width="2" '
                         f'stroke-linecap="round" stroke-linejoin="round"/>')
            x += 30
    return "\n".join(parts)


def banner(theme):
    t, W, H = THEMES[theme], 1280, 420
    body = [
        backdrop(W, H, t),
        mark(80, 85, 250, t["text"]),
        text(380, 190, "Evolve", 112, t["text"], 800, extra='letter-spacing="-3"'),
        text(384, 246, "Programs that learn from failure.", 33, t["text"], 600),
        text(384, 290, "Python-readable  ·  Julia data-native  ·  Rust-built  ·  AI-agent ready", 21, t["muted"], 500),
        loop_chips(384, 320, t),
    ]
    return svg(W, H, "\n".join(body), "Evolve: programs that learn from failure")


def social():
    t, W, H = THEMES["dark"], 1280, 640
    body = [
        backdrop(W, H, t, rx=0),
        mark(110, 160, 320, t["text"]),
        text(486, 292, "Evolve", 140, t["text"], 800, extra='letter-spacing="-4"'),
        text(492, 358, "Programs that learn from failure.", 40, t["text"], 600),
        text(492, 406, "Python-readable · Julia data-native · Rust-built", 25, t["muted"], 500),
        loop_chips(492, 442, t, 17),
        text(640, 590, "github.com/peace-program-project/peace", 22, t["muted"], 500, "middle", MONO),
    ]
    return svg(W, H, "\n".join(body), "Evolve programming language")


def avatar():
    W = 512
    body = [f'<rect width="{W}" height="{W}" fill="{BLACK}"/>', mark(96, 96, 320, WHITE)]
    return svg(W, W, "\n".join(body), "Evolve logo")


def mark_only(ink):
    return svg(256, 256, mark(0, 0, 256, ink), "Evolve logo mark")


def arrow_marker(pid, color):
    return (f'<defs><marker id="{pid}-arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" '
            f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{color}"/></marker></defs>')


def loop_diagram(theme):
    t, W, H, pid = THEMES[theme], 960, 570, f"lp{theme}"
    cx, cy, R, nr = 480, 295, 185, 38
    steps = [("Observe", "attempt / learn"), ("Vary", "gene · mutate"),
             ("Measure", "fitness · invariant"), ("Select", "population · promote"),
             ("Remember", "fossil record · lineage")]
    body = [backdrop(W, H, t, rx=24), arrow_marker(pid, t["line"])]
    angles = [-90 + 72 * i for i in range(5)]
    gap = 17
    for i, a in enumerate(angles):
        a1, a2 = math.radians(a + gap), math.radians(a + 72 - gap)
        x1, y1 = cx + R * math.cos(a1), cy + R * math.sin(a1)
        x2, y2 = cx + R * math.cos(a2), cy + R * math.sin(a2)
        body.append(f'<path d="M{x1:.1f},{y1:.1f} A{R},{R} 0 0 1 {x2:.1f},{y2:.1f}" fill="none" '
                    f'stroke="{t["line"]}" stroke-width="3" stroke-dasharray="{"7 6" if i == 4 else "none"}" '
                    f'marker-end="url(#{pid}-arr)"/>')
    body += [
        f'<circle cx="{cx}" cy="{cy}" r="104" fill="{t["card"]}" stroke="{t["card_stroke"]}" stroke-width="2"/>',
        mark(cx - 32, cy - 76, 64, t["text"]),
        text(cx, cy + 26, "Evolve runtime", 18, t["text"], 700, "middle"),
        text(cx, cy + 48, "sandboxed · budgeted", 13, t["muted"], 500, "middle"),
        text(cx, cy + 66, "human-gated", 13, t["muted"], 500, "middle"),
    ]
    for i, (a, (title, code)) in enumerate(zip(angles, steps)):
        ar = math.radians(a)
        nx, ny = cx + R * math.cos(ar), cy + R * math.sin(ar)
        body.append(f'<circle cx="{nx:.1f}" cy="{ny:.1f}" r="{nr + 7}" fill="{t["soft"]}"/>')
        body.append(f'<circle cx="{nx:.1f}" cy="{ny:.1f}" r="{nr}" fill="{t["text"]}"/>')
        body.append(text(nx, ny + 9, str(i + 1), 26, t["bg"], 800, "middle"))
        c, s = math.cos(ar), math.sin(ar)
        if s < -0.9:      # top
            lx, ly, anc = nx, ny - nr - 40, "middle"
        elif s > 0.5:     # bottom
            lx, ly, anc = nx, ny + nr + 32, "middle"
        else:             # sides
            lx, ly, anc = nx + (nr + 20) * (1 if c > 0 else -1), ny - 2, "start" if c > 0 else "end"
        body.append(text(lx, ly, title, 21, t["text"], 700, anc))
        body.append(text(lx, ly + 22, code, 15, t["muted"], 500, anc, MONO))
    return svg(W, H, "\n".join(body), "The Evolve improvement loop: observe, vary, measure, select, remember")


def box(x, y, w, h, title, sub, t, strong=False):
    """A labelled box. `strong` boxes (the evolution layer) get a heavier outline."""
    stroke, sw = (t["text"], 2.5) if strong else (t["card_stroke"], 1.5)
    return "\n".join([
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{t["card"]}" stroke="{stroke}" stroke-width="{sw}"/>',
        text(x + w / 2 + 2, y + (h / 2 - 2 if sub else h / 2 + 6), title, 16, t["text"], 700, "middle"),
        text(x + w / 2 + 2, y + h / 2 + 18, sub, 12.5, t["muted"], 500, "middle", MONO) if sub else "",
    ])


def architecture(theme):
    t, W, H, pid = THEMES[theme], 1000, 400, f"ar{theme}"
    body = [backdrop(W, H, t, rx=24), arrow_marker(pid, t["line"])]
    row = [(30, 150, ".evo source", "your code"), (220, 150, "Lossless CST", "evo-syntax"),
           (410, 110, "HIR", "evo-hir"), (560, 130, "Typed IR", "evo-types")]
    ry, rh = 98, 64
    for i, (x, w, ti, su) in enumerate(row):
        body.append(box(x, ry, w, rh, ti, su, t))
        if i < len(row) - 1:
            body.append(f'<line x1="{x + w + 4}" y1="{ry + rh / 2}" x2="{row[i + 1][0] - 6}" y2="{ry + rh / 2}" '
                        f'stroke="{t["line"]}" stroke-width="2.5" marker-end="url(#{pid}-arr)"/>')
    targets = [(30, "Cranelift JIT", "REPL · dev"), (100 + 30, "LLVM AOT", "release binaries"),
               (200 + 30, "WASM sandbox", "mutations run here")]
    tx, tw, th = 760, 210, 60
    for (ty, ti, su) in targets:
        body.append(box(tx, ty, tw, th, ti, su, t, strong=ti.startswith("WASM")))
        sy = ry + rh / 2
        ey = ty + th / 2
        body.append(f'<path d="M694,{sy} C727,{sy} 722,{ey} {tx - 6},{ey}" fill="none" stroke="{t["line"]}" '
                    f'stroke-width="2.5" marker-end="url(#{pid}-arr)"/>')
    # evolution layer
    ex, ey, ew, eh = 250, 300, 290, 64
    body.append(box(ex, ey, ew, eh, "evo-search", "mutation · fitness · selection", t, strong=True))
    body.append(box(30, ey, 150, eh, "Fossil record", "lessons · lineage", t))
    body.append(f'<line x1="{ex - 7}" y1="{ey + eh / 2}" x2="186" y2="{ey + eh / 2}" stroke="{t["line"]}" '
                f'stroke-width="2.5" marker-start="url(#{pid}-arr)" marker-end="url(#{pid}-arr)"/>')
    body.append(f'<line x1="295" y1="{ey - 4}" x2="295" y2="{ry + rh + 8}" stroke="{t["text"]}" '
                f'stroke-width="2.5" stroke-dasharray="6 5" marker-end="url(#{pid}-arr)"/>')
    body.append(text(305, 222, "edits the CST / IR,", 13, t["muted"], 500))
    body.append(text(305, 240, "never raw text", 13, t["muted"], 500))
    body.append(f'<path d="M865,294 L865,332 L{ex + ew + 6},332" fill="none" stroke="{t["text"]}" stroke-width="2.5" '
                f'stroke-dasharray="6 5" marker-end="url(#{pid}-arr)"/>')
    body.append(text(700, 324, "fitness results", 13, t["muted"], 500, "middle"))
    body.append(text(30, 52, "Built on Rust", 20, t["text"], 800))
    body.append(text(30, 74, "compiler + runtime + sandbox, tracking the beta channel", 14, t["muted"], 500))
    return svg(W, H, "\n".join(body), "Evolve architecture: source to CST, HIR, typed IR, then JIT, AOT or WASM sandbox")


def roadmap(theme):
    t, W, H = THEMES[theme], 1100, 270
    phases = [("Seed", "v0.0", "Feb 2027", "RFCs · grammar", "EvoBench spec"),
              ("Sprout", "v0.1", "Jun 2027", "Python engine", "interpreter"),
              ("Root", "v0.2", "Oct 2027", "arrays · frames", "units · ±"),
              ("Branch", "v0.3", "Jan 2028", "gene · fitness", "lineage"),
              ("Bloom", "v0.4", "Apr 2028", "JIT · WASM", "@heal"),
              ("Pollinate", "v0.5", "Aug 2028", "MCP · agents", "LSP"),
              ("Forest", "v1.0", "H2 2028", "AOT · packages", "stable 1.0")]
    body = [backdrop(W, H, t, rx=24),
            f'<rect x="70" y="127" width="960" height="4" rx="2" fill="{t["line"]}"/>']
    for i, (name, ver, date, h1, h2) in enumerate(phases):
        x = 100 + i * 150
        if i == 0:
            body.append(f'<circle cx="{x}" cy="129" r="24" fill="none" stroke="{t["text"]}" stroke-width="2" stroke-dasharray="4 4"/>')
            body.append(text(x, 40, "WE ARE HERE", 11, t["text"], 800, "middle", extra='letter-spacing="1.5"'))
        body.append(f'<circle cx="{x}" cy="129" r="15" fill="{t["card"]}" stroke="{t["text"]}" stroke-width="4"/>')
        body.append(f'<circle cx="{x}" cy="129" r="5" fill="{t["text"] if i == 0 else t["line"]}"/>')
        body.append(text(x, 76, name, 18, t["text"], 800, "middle"))
        body.append(text(x, 96, ver, 13, t["muted"], 700, "middle", MONO))
        body.append(text(x, 176, date, 14, t["text"], 700, "middle"))
        body.append(text(x, 198, h1, 13, t["muted"], 500, "middle"))
        body.append(text(x, 216, h2, 13, t["muted"], 500, "middle"))
    body.append(text(W / 2, 252, "engine first (Python bindings)  ·  language converges in Branch  ·  1.0 in Forest",
                     13, t["muted"], 500, "middle", MONO))
    return svg(W, H, "\n".join(body), "Evolve roadmap from Seed (v0.0) to Forest (v1.0)")


def write(rel, content):
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print(rel)


write("logo/evolve-mark.svg", mark_only(BLACK))
write("logo/evolve-mark-white.svg", mark_only(WHITE))
write("logo/evolve-avatar.svg", avatar())
write("social/evolve-social-preview.svg", social())
for th in THEMES:
    write(f"banner/evolve-banner-{th}.svg", banner(th))
    write(f"diagrams/evolution-loop-{th}.svg", loop_diagram(th))
    write(f"diagrams/architecture-{th}.svg", architecture(th))
    write(f"diagrams/roadmap-{th}.svg", roadmap(th))
