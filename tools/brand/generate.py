"""Generate Peace brand SVGs (logo, banner, social preview, diagrams) in light/dark themes.

Usage:  python3 tools/brand/generate.py assets
PNG exports (avatar, social preview) need cairosvg:
  uv run --with cairosvg python -c "import cairosvg; cairosvg.svg2png(url='assets/logo/peace-avatar.svg', write_to='assets/logo/peace-avatar.png')"
"""
import math
import os
import random
import sys
from xml.sax.saxutils import escape

OUT = sys.argv[1]

PALETTE = {
    "leaf": "#22C55E",
    "teal": "#14B8A6",
    "evergreen": "#0F766E",
    "sky": "#38BDF8",
    "violet": "#8B5CF6",
    "ember": "#F97316",
}
THEMES = {
    "dark": dict(bg1="#0B1220", bg2="#0D2A27", text="#F1F5F9", muted="#94A3B8", card="#111A2B",
                 card_stroke="#23324A", line="#3B4A63", decor="#5EEAD4", decor_op=0.10),
    "light": dict(bg1="#F8FAF7", bg2="#E3F5EC", text="#0F172A", muted="#475569", card="#FFFFFF",
                  card_stroke="#CFE0D8", line="#94A3B8", decor="#0F766E", decor_op=0.08),
}
SANS = "Inter, 'Segoe UI', -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', 'SFMono-Regular', Menlo, Consolas, 'DejaVu Sans Mono', monospace"


def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{escape(title)}">\n<title>{escape(title)}</title>\n{body}\n</svg>\n')


def text(x, y, s, size, fill, weight=400, anchor="start", family=SANS, extra=""):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}" {extra}>{escape(s)}</text>')


def mark(x, y, size, pid, mutation=True):
    """The Peace mark: a peace symbol drawn as a lineage tree, with an ember 'mutation' twig."""
    s = size / 256
    g = f"{pid}-grad"
    p = PALETTE
    c, r_end = 128, 80
    d = r_end * math.sqrt(0.5)
    left, right, bottom = (c - d, c + d), (c + d, c + d), (c, c + r_end)
    mid = (c + d * 0.5, c + d * 0.5)
    twig = (mid[0] + 40, mid[1] - 14)
    parts = [
        f'<defs><linearGradient id="{g}" gradientUnits="userSpaceOnUse" x1="20" y1="20" x2="236" y2="236">'
        f'<stop offset="0" stop-color="{p["leaf"]}"/><stop offset="0.5" stop-color="{p["teal"]}"/>'
        f'<stop offset="1" stop-color="{p["sky"]}"/></linearGradient></defs>',
        f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.4f})">',
        f'<circle cx="128" cy="128" r="106" fill="none" stroke="url(#{g})" stroke-width="18"/>',
        f'<g stroke="url(#{g})" stroke-width="14" stroke-linecap="round" fill="none">',
        f'<line x1="128" y1="31" x2="128" y2="{bottom[1]:.1f}"/>',
        f'<line x1="128" y1="128" x2="{left[0]:.1f}" y2="{left[1]:.1f}"/>',
        f'<line x1="128" y1="128" x2="{right[0]:.1f}" y2="{right[1]:.1f}"/>',
    ]
    if mutation:
        parts.append(f'<line x1="{mid[0]:.1f}" y1="{mid[1]:.1f}" x2="{twig[0]:.1f}" y2="{twig[1]:.1f}" '
                     f'stroke="{p["ember"]}" stroke-width="9"/>')
    parts.append('</g>')
    parts += [
        f'<circle cx="128" cy="128" r="12" fill="{p["teal"]}"/>',
        f'<circle cx="{left[0]:.1f}" cy="{left[1]:.1f}" r="13" fill="{p["leaf"]}"/>',
        f'<circle cx="{bottom[0]:.1f}" cy="{bottom[1]:.1f}" r="13" fill="{p["teal"]}"/>',
        f'<circle cx="{right[0]:.1f}" cy="{right[1]:.1f}" r="13" fill="{p["sky"]}"/>',
    ]
    if mutation:
        parts.append(f'<circle cx="{twig[0]:.1f}" cy="{twig[1]:.1f}" r="10" fill="{p["ember"]}"/>')
    parts.append('</g>')
    return "\n".join(parts)


def tree_decor(x, y, depth, length, angle, t, rng, out):
    if depth == 0:
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{t["decor"]}"/>')
        return
    x2 = x + length * math.cos(angle)
    y2 = y + length * math.sin(angle)
    out.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{t["decor"]}" '
               f'stroke-width="{1 + depth * 0.8:.1f}" stroke-linecap="round"/>')
    out.append(f'<circle cx="{x2:.1f}" cy="{y2:.1f}" r="{2 + depth * 0.6:.1f}" fill="{t["decor"]}"/>')
    for da in (-0.45 - rng.random() * 0.2, 0.45 + rng.random() * 0.2):
        tree_decor(x2, y2, depth - 1, length * (0.68 + rng.random() * 0.1), angle + da, t, rng, out)


def backdrop(w, h, t, pid, rx=28, tree_at=None, tree_len=110):
    parts = [
        f'<defs><linearGradient id="{pid}-bg" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{t["bg1"]}"/><stop offset="1" stop-color="{t["bg2"]}"/></linearGradient>'
        f'<pattern id="{pid}-dots" width="28" height="28" patternUnits="userSpaceOnUse">'
        f'<circle cx="2" cy="2" r="1.4" fill="{t["decor"]}" opacity="0.35"/></pattern></defs>',
        f'<rect width="{w}" height="{h}" rx="{rx}" fill="url(#{pid}-bg)"/>',
        f'<rect width="{w}" height="{h}" rx="{rx}" fill="url(#{pid}-dots)" opacity="{t["decor_op"] * 3:.2f}"/>',
    ]
    if tree_at:
        out = []
        tree_decor(tree_at[0], tree_at[1], 5, tree_len, math.pi / 2, t, random.Random(7), out)
        parts.append(f'<g opacity="{t["decor_op"] * 2.2:.2f}">' + "".join(out) + '</g>')
    return "\n".join(parts)


def tagline_grad(pid, x1, x2):
    p = PALETTE
    return (f'<defs><linearGradient id="{pid}-tg" gradientUnits="userSpaceOnUse" x1="{x1}" y1="0" x2="{x2}" y2="0">'
            f'<stop offset="0" stop-color="{p["leaf"]}"/><stop offset="0.55" stop-color="{p["teal"]}"/>'
            f'<stop offset="1" stop-color="{p["sky"]}"/></linearGradient></defs>')


LOOP = [("observe", "ember"), ("vary", "leaf"), ("measure", "teal"), ("select", "sky"), ("remember", "violet")]


def loop_chips(x, y, t, size=16):
    cw = size * 0.62
    parts = []
    for i, (word, col) in enumerate(LOOP):
        w = len(word) * cw + 28
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{size * 2.2:.1f}" rx="{size * 1.1:.1f}" '
                     f'fill="{PALETTE[col]}" fill-opacity="0.14" stroke="{PALETTE[col]}" stroke-width="1.5"/>')
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
    t, W, H, pid = THEMES[theme], 1280, 420, f"bn{theme}"
    body = [
        backdrop(W, H, t, pid, tree_at=(1130, -20), tree_len=120),
        mark(70, 85, 250, pid),
        tagline_grad(pid, 372, 900),
        text(368, 188, "Peace", 108, t["text"], 800, extra='letter-spacing="-2"'),
        text(372, 244, "Programs that learn from failure.", 33, f"url(#{pid}-tg)", 700),
        text(372, 288, "Python-readable  ·  Julia data-native  ·  Rust-built  ·  AI-agent ready", 21, t["muted"], 500),
        loop_chips(372, 318, t),
    ]
    return svg(W, H, "\n".join(body), "Peace: programs that learn from failure")


def social():
    t, W, H, pid = THEMES["dark"], 1280, 640, "soc"
    body = [
        backdrop(W, H, t, pid, rx=0, tree_at=(1150, -30), tree_len=150),
        mark(100, 160, 320, pid),
        tagline_grad(pid, 480, 1100),
        text(474, 290, "Peace", 136, t["text"], 800, extra='letter-spacing="-3"'),
        text(480, 356, "Programs that learn from failure.", 40, f"url(#{pid}-tg)", 700),
        text(480, 404, "Python-readable · Julia data-native · Rust-built", 25, t["muted"], 500),
        loop_chips(480, 440, t, 17),
        text(640, 590, "github.com/peace-program-project/peace", 22, t["muted"], 500, "middle", MONO),
    ]
    return svg(W, H, "\n".join(body), "Peace programming language")


def avatar():
    W, pid = 512, "av"
    t = THEMES["dark"]
    body = [
        f'<defs><radialGradient id="{pid}-bg" cx="0.5" cy="0.42" r="0.75">'
        f'<stop offset="0" stop-color="#12302D"/><stop offset="1" stop-color="{t["bg1"]}"/></radialGradient></defs>',
        f'<rect width="{W}" height="{W}" fill="url(#{pid}-bg)"/>',
        mark(76, 76, 360, pid),
    ]
    return svg(W, W, "\n".join(body), "Peace logo")


def mark_only():
    return svg(256, 256, mark(0, 0, 256, "mk"), "Peace logo mark")


def arrow_marker(pid, color):
    return (f'<defs><marker id="{pid}-arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" '
            f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{color}"/></marker></defs>')


def loop_diagram(theme):
    t, W, H, pid = THEMES[theme], 960, 570, f"lp{theme}"
    cx, cy, R, nr = 480, 295, 185, 38
    steps = [("Observe", "attempt / learn", "ember"), ("Vary", "gene · mutate", "leaf"),
             ("Measure", "fitness · invariant", "teal"), ("Select", "population · promote", "sky"),
             ("Remember", "fossil record · lineage", "violet")]
    body = [backdrop(W, H, t, pid, rx=24), arrow_marker(pid, t["line"])]
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
        mark(cx - 36, cy - 78, 72, pid),
        text(cx, cy + 26, "Peace runtime", 18, t["text"], 700, "middle"),
        text(cx, cy + 48, "sandboxed · budgeted", 13, t["muted"], 500, "middle"),
        text(cx, cy + 66, "human-gated", 13, t["muted"], 500, "middle"),
    ]
    for i, (a, (title, code, col)) in enumerate(zip(angles, steps)):
        ar = math.radians(a)
        nx, ny = cx + R * math.cos(ar), cy + R * math.sin(ar)
        body.append(f'<circle cx="{nx:.1f}" cy="{ny:.1f}" r="{nr + 7}" fill="{PALETTE[col]}" fill-opacity="0.18"/>')
        body.append(f'<circle cx="{nx:.1f}" cy="{ny:.1f}" r="{nr}" fill="{PALETTE[col]}"/>')
        body.append(text(nx, ny + 9, str(i + 1), 26, "#FFFFFF", 800, "middle"))
        c, s = math.cos(ar), math.sin(ar)
        if s < -0.9:      # top
            lx, ly, anc = nx, ny - nr - 40, "middle"
        elif s > 0.5:     # bottom
            lx, ly, anc = nx, ny + nr + 32, "middle"
        else:             # sides
            lx, ly, anc = nx + (nr + 20) * (1 if c > 0 else -1), ny - 2, "start" if c > 0 else "end"
        body.append(text(lx, ly, title, 21, t["text"], 700, anc))
        body.append(text(lx, ly + 22, code, 15, t["muted"], 500, anc, MONO))
    return svg(W, H, "\n".join(body), "The Peace improvement loop: observe, vary, measure, select, remember")


def box(x, y, w, h, title, sub, t, accent):
    return "\n".join([
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{t["card"]}" stroke="{t["card_stroke"]}" stroke-width="1.5"/>',
        f'<rect x="{x}" y="{y + 10}" width="4" height="{h - 20}" rx="2" fill="{PALETTE[accent]}"/>',
        text(x + w / 2 + 2, y + (h / 2 - 2 if sub else h / 2 + 6), title, 16, t["text"], 700, "middle"),
        text(x + w / 2 + 2, y + h / 2 + 18, sub, 12.5, t["muted"], 500, "middle", MONO) if sub else "",
    ])


def architecture(theme):
    t, W, H, pid = THEMES[theme], 1000, 400, f"ar{theme}"
    body = [backdrop(W, H, t, pid, rx=24), arrow_marker(pid, t["line"])]
    row = [(30, 150, ".peace source", "your code", "leaf"), (220, 150, "Lossless CST", "peace-syntax", "leaf"),
           (410, 110, "HIR", "peace-hir", "teal"), (560, 130, "Typed IR", "peace-types", "teal")]
    ry, rh = 98, 64
    for i, (x, w, ti, su, ac) in enumerate(row):
        body.append(box(x, ry, w, rh, ti, su, t, ac))
        if i < len(row) - 1:
            body.append(f'<line x1="{x + w + 4}" y1="{ry + rh / 2}" x2="{row[i + 1][0] - 6}" y2="{ry + rh / 2}" '
                        f'stroke="{t["line"]}" stroke-width="2.5" marker-end="url(#{pid}-arr)"/>')
    targets = [(30, "Cranelift JIT", "REPL · dev", "sky"), (100 + 30, "LLVM AOT", "release binaries", "violet"),
               (200 + 30, "WASM sandbox", "mutations run here", "ember")]
    tx, tw, th = 760, 210, 60
    for (ty, ti, su, ac) in targets:
        body.append(box(tx, ty, tw, th, ti, su, t, ac))
        sy = ry + rh / 2
        ey = ty + th / 2
        body.append(f'<path d="M694,{sy} C727,{sy} 722,{ey} {tx - 6},{ey}" fill="none" stroke="{t["line"]}" '
                    f'stroke-width="2.5" marker-end="url(#{pid}-arr)"/>')
    # evolution layer
    ex, ey, ew, eh = 250, 300, 290, 64
    body.append(box(ex, ey, ew, eh, "peace-evolve", "mutation · fitness · selection", t, "ember"))
    body.append(box(30, ey, 150, eh, "Fossil record", "lessons · lineage", t, "violet"))
    body.append(f'<line x1="{ex - 7}" y1="{ey + eh / 2}" x2="186" y2="{ey + eh / 2}" stroke="{t["line"]}" '
                f'stroke-width="2.5" marker-start="url(#{pid}-arr)" marker-end="url(#{pid}-arr)"/>')
    body.append(f'<line x1="295" y1="{ey - 4}" x2="295" y2="{ry + rh + 8}" stroke="{PALETTE["ember"]}" '
                f'stroke-width="2.5" stroke-dasharray="6 5" marker-end="url(#{pid}-arr)"/>')
    body.append(text(305, 222, "edits the CST / IR,", 13, t["muted"], 500))
    body.append(text(305, 240, "never raw text", 13, t["muted"], 500))
    body.append(f'<path d="M865,294 L865,332 L{ex + ew + 6},332" fill="none" stroke="{PALETTE["ember"]}" stroke-width="2.5" '
                f'stroke-dasharray="6 5" marker-end="url(#{pid}-arr)"/>')
    body.append(text(700, 324, "fitness results", 13, t["muted"], 500, "middle"))
    body.append(text(30, 52, "Built on Rust", 20, t["text"], 800))
    body.append(text(30, 74, "compiler + runtime + sandbox, tracking the beta channel", 14, t["muted"], 500))
    return svg(W, H, "\n".join(body), "Peace architecture: source to CST, HIR, typed IR, then JIT, AOT or WASM sandbox")


def roadmap(theme):
    t, W, H, pid = THEMES[theme], 1100, 270, f"rm{theme}"
    phases = [("Seed", "v0.0", "Feb 2027", "RFCs · grammar", "PeaceBench spec"),
              ("Sprout", "v0.1", "Jun 2027", "Python engine", "interpreter"),
              ("Root", "v0.2", "Oct 2027", "arrays · frames", "units · ±"),
              ("Branch", "v0.3", "Jan 2028", "gene · fitness", "lineage"),
              ("Bloom", "v0.4", "Apr 2028", "JIT · WASM", "@heal"),
              ("Pollinate", "v0.5", "Aug 2028", "MCP · agents", "LSP"),
              ("Forest", "v1.0", "H2 2028", "AOT · packages", "stable 1.0")]
    cols = ["leaf", "leaf", "teal", "teal", "sky", "sky", "violet"]
    p = PALETTE
    body = [backdrop(W, H, t, pid, rx=24),
            f'<defs><linearGradient id="{pid}-ln" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{p["leaf"]}"/>'
            f'<stop offset="0.5" stop-color="{p["teal"]}"/><stop offset="1" stop-color="{p["violet"]}"/></linearGradient></defs>',
            f'<rect x="70" y="126" width="960" height="6" rx="3" fill="url(#{pid}-ln)" opacity="0.85"/>']
    for i, ((name, ver, date, h1, h2), col) in enumerate(zip(phases, cols)):
        x = 100 + i * 150
        if i == 0:
            body.append(f'<circle cx="{x}" cy="129" r="24" fill="none" stroke="{p["ember"]}" stroke-width="2" stroke-dasharray="4 4"/>')
            body.append(text(x, 40, "WE ARE HERE", 11, p["ember"], 800, "middle", extra='letter-spacing="1.5"'))
        body.append(f'<circle cx="{x}" cy="129" r="15" fill="{t["card"]}" stroke="{p[col]}" stroke-width="5"/>')
        body.append(f'<circle cx="{x}" cy="129" r="5" fill="{p[col]}"/>')
        body.append(text(x, 76, name, 18, t["text"], 800, "middle"))
        body.append(text(x, 96, ver, 13, p[col], 700, "middle", MONO))
        body.append(text(x, 176, date, 14, t["text"], 700, "middle"))
        body.append(text(x, 198, h1, 13, t["muted"], 500, "middle"))
        body.append(text(x, 216, h2, 13, t["muted"], 500, "middle"))
    body.append(text(W / 2, 252, "engine first (Python bindings)  ·  language converges in Branch  ·  1.0 in Forest",
                     13, t["muted"], 500, "middle", MONO))
    return svg(W, H, "\n".join(body), "Peace roadmap from Seed (v0.0) to Forest (v1.0)")


def write(rel, content):
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print(rel)


write("logo/peace-mark.svg", mark_only())
write("logo/peace-avatar.svg", avatar())
write("social/peace-social-preview.svg", social())
for th in THEMES:
    write(f"banner/peace-banner-{th}.svg", banner(th))
    write(f"diagrams/evolution-loop-{th}.svg", loop_diagram(th))
    write(f"diagrams/architecture-{th}.svg", architecture(th))
    write(f"diagrams/roadmap-{th}.svg", roadmap(th))
