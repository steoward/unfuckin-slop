#!/usr/bin/env python3
"""Distill a compact UI-element signature from a verbatim MotionSites prompt.

Research artifact for the UI-element training experiments (see README > Fine-tuning).
The deployed index representation remains "{title}: {description}"; injecting the
raw prompt UI signal into training was tested two ways and rejected because dev
retrieval got worse. This module is kept so the extraction is inspectable and the
experiments reproducible.

Three views of the same prompt:
  extract_signature  - full signature (engine, motion, layout, fonts, palette, stack)
  ui_query           - distinctive-only natural design query (drops generic boilerplate)
  concept_signature  - compact engine+motion+layout terms used to enrich the index in Exp B

Deterministic and cheap (regex only); no model needed.
"""
import re

# reference palette for hex -> color-name (RGB nearest)
_PALETTE = {
    "black": (10, 10, 12), "charcoal": (30, 32, 38), "slate": (51, 65, 85),
    "gray": (107, 114, 128), "silver": (203, 213, 225), "white": (248, 250, 252),
    "cream": (245, 240, 225), "beige": (226, 217, 200), "sand": (214, 199, 170),
    "red": (220, 38, 38), "crimson": (190, 18, 60), "rose": (244, 63, 94),
    "pink": (236, 72, 153), "fuchsia": (217, 70, 239), "orange": (249, 115, 22),
    "amber": (245, 158, 11), "gold": (212, 175, 55), "yellow": (234, 179, 8),
    "lime": (132, 204, 22), "green": (34, 197, 94), "emerald": (16, 185, 129),
    "teal": (20, 184, 166), "cyan": (6, 182, 212), "sky": (14, 165, 233),
    "blue": (59, 130, 246), "cobalt": (47, 99, 255), "indigo": (99, 102, 241),
    "violet": (139, 92, 246), "purple": (168, 85, 247), "lavender": (196, 181, 253),
    "navy": (15, 23, 42), "midnight": (11, 15, 25), "espresso": (24, 10, 6),
    "copper": (168, 78, 10), "bronze": (176, 141, 87), "mint": (167, 243, 208),
}

_FONTS = [
    "Helvetica Now Display", "Helvetica Now", "Neue Montreal", "PP Neue Montreal",
    "GT Walsheim", "Clash Display", "Cabinet Grotesk", "General Sans", "Satoshi",
    "Space Grotesk", "Playfair Display", "Instrument Serif", "Source Serif 4",
    "Source Serif", "JetBrains Mono", "IBM Plex Mono", "IBM Plex Sans", "Fira Code",
    "DM Sans", "DM Serif Display", "DM Serif", "Plus Jakarta Sans", "Bricolage Grotesque",
    "Fraunces", "Unbounded", "Monument Extended", "Syne", "Sora", "Manrope", "Outfit",
    "Geist", "Anton", "Archivo", "Archivo Black", "Inter", "Roboto", "Open Sans",
    "Lato", "Montserrat", "Poppins", "Raleway", "Oswald", "Bebas Neue", "Work Sans",
    "Nunito", "Rubik", "Karla", "Libre Baskerville", "Cormorant", "EB Garamond",
    "Courier", "Georgia", "Times New Roman", "Arial", "Helvetica Neue", "Helvetica",
    "Circular", "Avenir", "Futura", "Garamond", "Baskerville", "Didot", "Bodoni",
]

_ENGINE = [
    (r"liquid glass|refraction|chromatic aberration|fedisplacementmap|glassmorphism|frosted glass|backdrop-filter:\s*blur", "liquid glass"),
    (r"three\.js|@react-three|webgl|glsl|shader|particle orbit|spatial canvas|\b3d\b", "3d webgl"),
    (r"aurora|mesh gradient|gradient mesh|northern lights", "aurora gradient"),
    (r"film grain|svg turbulence|\bgrain\b|noise texture|feTurbulence", "grain texture"),
    (r"brutalis|neo-brutalis|swiss style|editorial grid", "brutalist editorial"),
    (r"glassmorphic|glass card|glass panel", "glass surfaces"),
]
_MOTION = [
    (r"scroll[- ]scrub|scrolltrigger|scroll-driven|\.currenttime|scrubbed", "scroll-scrubbed video"),
    (r"mousemove|mouse[- ]track|cursor follow|magnetic|pointer-reactive|trackpad", "cursor-reactive"),
    (r"parallax", "parallax"),
    (r"marquee|ticker|infinite horizontal", "marquee"),
    (r"hover tilt|tilt|perspective|rotatex|rotatey|card tilt", "hover tilt"),
    (r"spring|stiffness|damping|framer-motion|usespring|react-spring", "spring physics"),
    (r"\bdrag\b|swipe|snap point|gesture", "drag gesture"),
    (r"stagger|intersectionobserver|entrance animation|scroll reveal|fade-up", "staggered reveal"),
    (r"gsap|lenis|locomotive|smooth scroll", "smooth scroll"),
    (r"typewriter|text scramble|count[- ]up|odometer", "animated numerals"),
]
_LAYOUT = [
    (r"bento", "bento grid"), (r"navbar|navigation bar|masthead", "navbar"),
    (r"\bhero\b", "hero"), (r"dashboard", "dashboard"), (r"carousel", "carousel"),
    (r"sidebar", "sidebar"), (r"masonry", "masonry"), (r"pricing", "pricing"),
    (r"portfolio", "portfolio"), (r"ecommerce|e-commerce|product grid|add to cart|shop", "ecommerce"),
    (r"modal|dialog", "modal"), (r"\bcanvas\b", "canvas"), (r"split[- ]screen|split layout", "split layout"),
    (r"full[- ]screen|fullscreen", "fullscreen"), (r"sticky", "sticky sections"),
    (r"footer", "footer"), (r"testimonial", "testimonials"), (r"faq|accordion", "accordion"),
]
_STACK = [
    (r"next\.js|nextjs", "Next.js"), (r"\breact\b", "React"), (r"\bvite\b", "Vite"),
    (r"typescript", "TypeScript"), (r"tailwind", "Tailwind"), (r"three\.js", "Three.js"),
    (r"gsap", "GSAP"), (r"framer-motion", "Framer Motion"), (r"\bvue\b", "Vue"),
    (r"svelte", "Svelte"), (r"webgl", "WebGL"), (r"\bsvg\b", "SVG"),
]
_TW = re.compile(r"\b(?:bg|text|border|from|to|via|ring|fill|stroke)-(slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose)-\d{2,3}\b")
_HEX = re.compile(r"#([0-9a-fA-F]{6})\b")
_GFONT = re.compile(r"family=([A-Za-z0-9+]+)")
_FFAMILY = re.compile(r"font-family:\s*['\"]?([A-Za-z0-9 \-]+)", re.I)

_GENERIC_FONTS = {"inter", "arial", "helvetica", "helvetica neue", "helvetica now",
                  "roboto", "open sans", "lato", "georgia", "times new roman",
                  "courier", "sans-serif", "serif", "monospace", "system-ui"}


def _hex_name(h):
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    best, bd = None, 1e9
    for name, (pr, pg, pb) in _PALETTE.items():
        d = (r - pr) ** 2 + (g - pg) ** 2 + (b - pb) ** 2
        if d < bd:
            bd, best = d, name
    return best


def _dedupe(seq):
    seen, out = set(), []
    for x in seq:
        if x and x not in seen:
            seen.add(x); out.append(x)
    return out


def _pick(table, low):
    return _dedupe([label for pat, label in table if re.search(pat, low)])


def extract_signature(fp, max_chars=230):
    """Full UI signature: engine; motion; layout; fonts; palette; stack."""
    if not fp:
        return ""
    low = fp.lower()
    engine = _pick(_ENGINE, low)
    motion = _pick(_MOTION, low)
    layout = _pick(_LAYOUT, low)[:6]
    stack = _pick(_STACK, low)[:5]

    fonts = []
    for f in _FONTS:
        if re.search(re.escape(f.lower()), low):
            fonts.append(f)
    for m in _GFONT.finditer(fp):
        fonts.append(m.group(1).replace("+", " "))
    for m in _FFAMILY.finditer(fp):
        nm = m.group(1).strip()
        if nm and nm.lower() not in ("inherit", "sans-serif", "serif", "monospace", "var"):
            fonts.append(nm)
    fonts = _dedupe(fonts)[:3]

    colors = [m.group(1) for m in _TW.finditer(low)]
    colors += [_hex_name(h) for h in _HEX.findall(fp)]
    colors = _dedupe([c for c in colors if c not in ("white", "black", "gray", "silver")])[:5]

    parts = []
    if engine: parts.append(", ".join(engine))
    if motion: parts.append(", ".join(motion[:4]))
    if layout: parts.append(", ".join(layout))
    if fonts: parts.append("fonts " + ", ".join(fonts))
    if colors: parts.append("palette " + ", ".join(colors))
    if stack: parts.append(", ".join(stack))
    return "; ".join(parts)[:max_chars].rstrip(";, ")


def ui_query(fp, max_words=18):
    """Distinctive-only natural design query (Exp A anchor). Drops generic fonts/stack."""
    if not fp:
        return ""
    low = fp.lower()
    engine = _pick(_ENGINE, low)
    motion = _pick(_MOTION, low)[:4]
    layout = _pick(_LAYOUT, low)[:5]
    fonts = []
    for f in _FONTS:
        if f.lower() not in _GENERIC_FONTS and re.search(re.escape(f.lower()), low):
            fonts.append(f)
    for m in _GFONT.finditer(fp):
        nm = m.group(1).replace("+", " ")
        if nm.lower() not in _GENERIC_FONTS:
            fonts.append(nm)
    fonts = _dedupe(fonts)[:2]
    colors = [m.group(1) for m in _TW.finditer(low)]
    colors += [_hex_name(h) for h in _HEX.findall(fp)]
    colors = _dedupe([c for c in colors if c not in ("white", "black", "gray", "silver", "cream")])[:3]

    head = " ".join(engine + motion + layout)
    tail = []
    if fonts:
        tail.append("in " + " and ".join(fonts))
    if colors:
        tail.append(", ".join(colors) + " palette")
    q = head + (" " + " ".join(tail) if tail else "")
    return " ".join(q.split()[:max_words]).lower().rstrip(".,;:")


def concept_signature(fp, max_terms=12):
    """Compact engine+motion+layout terms used to enrich the index in Exp B."""
    if not fp:
        return ""
    low = fp.lower()
    terms = _pick(_ENGINE, low) + _pick(_MOTION, low)[:4] + _pick(_LAYOUT, low)[:5]
    return " ".join(terms[:max_terms])


if __name__ == "__main__":
    import json
    import os
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(repo, "design_showcases", "showcases_meta.json"), encoding="utf-8") as f:
        meta = json.load(f)
    ms = [m for m in meta if m.get("source_site") == "motionsites.ai"]
    print(f"motionsites items with a verbatim prompt: {len(ms)}")
    for m in ms[:5]:
        fp = m.get("full_prompt") or ""
        print(f"\n### {m['title']}  ({m['category']})")
        print("signature:", extract_signature(fp))
        print("ui_query :", ui_query(fp))
        print("concept  :", concept_signature(fp))