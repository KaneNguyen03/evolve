<div align="center">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="../assets/logo/evolve-mark-white.svg">
  <img src="../assets/logo/evolve-mark.svg" width="120" alt="Evolve logo mark"/>
</picture>

# 🎨 Evolve Brand Guide

*How Evolve looks, sounds, and feels.*
</div>

---

## 🧬 The mark

The Evolve logo is a **geometric lowercase e whose tail is a separate dot**:

- **The ring and crossbar** are the program as it runs today: whole, readable, and working.
- **The dot** sits in the e's opening, not yet joined. It is the next variant: an experiment that may fail, and that's the point. Most dots never join. The ones that pass their fitness checks become part of the line.

The mark is drawn on a 256-unit grid with one stroke weight (30 units), so it stays legible down to a 16-pixel favicon.

| Asset | File | Use |
|---|---|---|
| Logo mark, black (transparent) | [`assets/logo/evolve-mark.svg`](../assets/logo/evolve-mark.svg) · [PNG](../assets/logo/evolve-mark.png) | Docs, slides, favicons on light backgrounds |
| Logo mark, white (transparent) | [`assets/logo/evolve-mark-white.svg`](../assets/logo/evolve-mark-white.svg) | Dark backgrounds |
| Avatar (white on black) | [`assets/logo/evolve-avatar.svg`](../assets/logo/evolve-avatar.svg) · [PNG 512²](../assets/logo/evolve-avatar.png) | GitHub org avatar, social profiles |
| Banner (light / dark) | [`assets/banner/`](../assets/banner/) | README headers |
| Social preview | [`assets/social/evolve-social-preview.png`](../assets/social/evolve-social-preview.png) (1280×640) | GitHub social card, link previews |
| Diagrams (light / dark) | [`assets/diagrams/`](../assets/diagrams/) | Evolution loop, architecture, roadmap |

**Do** ✅
- Use the mark in pure black on white, or pure white on black.
- Keep clear space around it of at least ¼ of its width.

**Don't** ❌
- Color the mark, add gradients, shadows, or outlines.
- Join the dot to the ring, or move it.
- Rotate or stretch the mark.

---

## ⚫⚪ Color

Evolve is **monochrome**. Structure, weight, and line style carry meaning, never hue, so every asset prints, photocopies, and reads the same for color-blind viewers.

| Swatch | Name | Hex | Use |
|:---:|---|---|---|
| ![](https://img.shields.io/badge/-%20%20%20%20-000000?style=flat-square) | **Black** | `#000000` | Ink on light; background on dark |
| ![](https://img.shields.io/badge/-%20%20%20%20-FFFFFF?style=flat-square) | **White** | `#FFFFFF` | Background on light; ink on dark |
| ![](https://img.shields.io/badge/-%20%20%20%20-525252?style=flat-square) | **Graphite** | `#525252` | Muted text on light |
| ![](https://img.shields.io/badge/-%20%20%20%20-A3A3A3?style=flat-square) | **Silver** | `#A3A3A3` | Muted text on dark |

In diagrams, emphasis comes from line style:
- **Solid filled circles:** steps of the evolution loop.
- **Heavy outlines:** where evolution happens (`evo-search`, the WASM sandbox).
- **Dashed lines:** feedback, such as fitness results and edits to the CST.

---

## 🔤 Typography

| Use | Typeface | Fallbacks |
|---|---|---|
| Headings & UI | **Inter** (700–800) | Segoe UI, system-ui, Helvetica, Arial |
| Body | **Inter** (400–500) | same |
| Code | **JetBrains Mono** | SF Mono, Menlo, Consolas, monospace |

The wordmark is "Evolve" set in Inter ExtraBold (800) with tight tracking.

---

## 🗣️ Voice and tone

Evolve speaks the way a good mentor reacts to a mistake: **calm, curious, and constructive**.

| We are… | We are not… |
|---|---|
| 🌿 Calm: "This failed. Here's what we learned." | 🚨 Alarmist: "FATAL ERROR!!!" |
| 🔬 Precise: fitness numbers, invariants, lineage | 🪄 Hand-wavy: "AI magically fixes your code" |
| 🤝 Humble: humans hold the final say | 🤖 Grandiose: "No developers needed" |
| 🧬 Playful with biology metaphors, when they clarify | 🎭 Metaphor-first at the expense of meaning |

**Name:** *Evolve* in prose. Source files are `.evo`, the command is `evo`, code fences are `evo`, and crates are `evo-*`.
**Tagline:** *Programs that learn from failure.*
**One-liner:** *Evolve is a programming language in which a program's failures make it better instead of only breaking it.*
**Short pitch:** *Python-readable · Julia data-native · Rust-built · AI-agent ready.*

### Emoji vocabulary

Use emojis as consistent signposts, not decoration:

| Emoji | Means | Emoji | Means |
|:---:|---|:---:|---|
| 🧬 | Evolve (the project), `gene`, evolution | 🩹 | `@heal` |
| 🍂 | Failure, `attempt / learn` | 🏆 | Selection, promotion |
| 🎯 | `fitness` | 🌳 | Lineage |
| 🦴 | Fossil record, Lessons | 📦 | Sandbox |
| 🔒 | `@conserved` | 🦀🐍🔬 | Rust, Python, Julia heritage |
| 🌱🌿🌳🌲🌸🐝🌍 | Roadmap phases, Seed → Forest | | |

---

## 🛠️ Regenerating assets

All SVGs come from one script, so geometry stays consistent. Never edit the SVGs by hand.

```bash
python3 tools/brand/generate.py assets
# PNG exports (mark, avatar, social preview) need cairosvg:
uv run --with cairosvg python - <<'EOF'
import cairosvg
cairosvg.svg2png(url="assets/logo/evolve-avatar.svg", write_to="assets/logo/evolve-avatar.png", output_width=512, output_height=512)
cairosvg.svg2png(url="assets/logo/evolve-mark.svg", write_to="assets/logo/evolve-mark.png", output_width=512, output_height=512)
cairosvg.svg2png(url="assets/social/evolve-social-preview.svg", write_to="assets/social/evolve-social-preview.png", output_width=1280, output_height=640)
EOF
```
