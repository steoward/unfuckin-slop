#!/usr/bin/env python3
"""Search the local design and component catalogs.

MiniLM and lexical search rank text. Evidence packets identify the original
record and what the snapshot contains. Use --record for the stored payload.
"""

import os
import re
import sys
import json
import argparse
from collections import Counter
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from sklearn.metrics.pairwise import cosine_similarity

SHOWCASES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "design_showcases")
META_PATH = os.path.join(SHOWCASES_DIR, "showcases_meta.json")
EMBS_PATH = os.path.join(SHOWCASES_DIR, "design_embeddings.npy")
FALLBACK_DATASET = os.path.join(SHOWCASES_DIR, "dataset.jsonl")
# Separate UI-component pool (21st.dev + skiper.ui code prompts). Kept apart from the
# 950 full-design showcases so the design benchmark and design search stay clean.
COMPONENTS_META_PATH = os.path.join(SHOWCASES_DIR, "components_meta.json")
COMPONENTS_EMBS_PATH = os.path.join(SHOWCASES_DIR, "component_embeddings.npy")

# Hybrid lexical+semantic ranking. Weight tuned on the dev split of eval/benchmark.json
# by driving the real search() pipeline at each weight (see eval/tune_hybrid.py): w=0.7
# maximizes dev MRR@10 then nDCG@5. Semantic layer is optional: without onnxruntime/tokenizers
# or the bundled encoder, search falls back to the pure lexical pipeline unchanged.
SEMANTIC_WEIGHT = 0.7
_sem_state = {"loaded": False, "enc": None, "emb": None}


def _load_semantic():
    if _sem_state["loaded"]:
        return _sem_state["enc"], _sem_state["emb"]
    _sem_state["loaded"] = True
    try:
        _here = os.path.dirname(os.path.abspath(__file__))
        if _here not in sys.path:
            sys.path.insert(0, _here)
        import semantic_index
        enc = semantic_index.load_encoder()
        if enc is not None and os.path.exists(EMBS_PATH):
            _sem_state["enc"] = enc
            _sem_state["emb"] = np.load(EMBS_PATH)
    except Exception:
        pass
    return _sem_state["enc"], _sem_state["emb"]


# Component pool shares the same bundled encoder but has its own vector index.
_comp_sem_state = {"loaded": False, "enc": None, "emb": None}


def _load_semantic_components():
    if _comp_sem_state["loaded"]:
        return _comp_sem_state["enc"], _comp_sem_state["emb"]
    _comp_sem_state["loaded"] = True
    try:
        _here = os.path.dirname(os.path.abspath(__file__))
        if _here not in sys.path:
            sys.path.insert(0, _here)
        import semantic_index
        enc = semantic_index.load_encoder()
        if enc is not None and os.path.exists(COMPONENTS_EMBS_PATH):
            _comp_sem_state["enc"] = enc
            _comp_sem_state["emb"] = np.load(COMPONENTS_EMBS_PATH)
    except Exception:
        pass
    return _comp_sem_state["enc"], _comp_sem_state["emb"]


def _minmax(x):
    lo, hi = float(np.min(x)), float(np.max(x))
    return (x - lo) / max(hi - lo, 1e-9)

# 3D, WebGL, and Kinetic keywords for filtering and classification
THREED_KEYWORDS = [
    "3d", "webgl", "canvas", "particle", "liquid", "kinetic", "spatial",
    "camera", "mesh", "tilt", "refraction", "orbit", "shader", "glsl",
    "perspective", "physics", "point-cloud", "cyber", "neon", "bento", "glass",
    "three.js", "threejs", "spline", "r3f"
]

# Liquid Glass, Refraction, and Chromatic aberration keywords
LIQUID_GLASS_KEYWORDS = [
    "liquid", "glass", "refraction", "refractive", "chromatic", "aberration",
    "glassmorphism", "frosted glass", "lens distortion", "specular", "caustics", "prism",
    "liquid glass"
]

# Production UI Component Primitives & Atmosphere Tokens
COMPONENT_PRIMITIVES = {
    "lighting_and_atmosphere": {
        "title": "Lighting & Atmosphere Primitives",
        "surface_elevations": {
            "base_canvas": {
                "hex": "#0B0F19",
                "tailwind": "bg-[#0B0F19]",
                "description": "Base dark canvas foundation with deep, neutral slate undertone"
            },
            "card_surface": {
                "hex": "#111827",
                "tailwind": "bg-[#111827]",
                "description": "Primary card and bento container elevation"
            },
            "elevated_surface": {
                "hex": "#1F2937",
                "tailwind": "bg-[#1F2937]",
                "description": "High-elevation popovers, dropdowns, and modals"
            },
            "rim_border_subtle": {
                "rgba": "rgba(255, 255, 255, 0.10)",
                "tailwind": "border-white/10",
                "description": "Hairline structural border on dark backgrounds"
            },
            "rim_border_active": {
                "rgba": "rgba(255, 255, 255, 0.20)",
                "tailwind": "border-white/20",
                "description": "Active state or hover rim border highlight"
            }
        },
        "ambient_glow": {
            "name": "Radial Ambient Glow (Stage Spotlight)",
            "css": "background: radial-gradient(circle 800px at 50% -100px, rgba(99, 102, 241, 0.18), transparent 70%);",
            "tailwind_snippet": '<div className="absolute -top-40 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-gradient-to-b from-indigo-500/20 via-purple-500/10 to-transparent blur-[120px] pointer-events-none -z-10" />',
            "description": "Soft colored spotlight anchored behind the hero section to create spatial depth"
        },
        "rim_light": {
            "name": "Specular Rim Light & Inner Bevel",
            "css": "box-shadow: inset 0 1px 0 0 rgba(255, 255, 255, 0.15);",
            "tailwind": "shadow-[inset_0_1px_0_0_rgba(255,255,255,0.15)]",
            "description": "Crisp top-edge reflection mimicking Apple physical hardware chamfers"
        }
    },
    "button_primitives": {
        "title": "Button Primitives",
        "primary_glow_cta": {
            "name": "Primary Glow CTA",
            "tailwind": "inline-flex items-center justify-center px-6 py-3 rounded-full bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm shadow-[0_0_24px_rgba(99,102,241,0.4)] hover:shadow-[0_0_32px_rgba(99,102,241,0.6)] transition-all duration-200 active:scale-[0.98] focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:ring-offset-2 focus:ring-offset-[#0B0F19]",
            "description": "Primary conversion button with atmospheric ambient glow and crisp active press"
        },
        "secondary_border": {
            "name": "Secondary Border Button",
            "tailwind": "inline-flex items-center justify-center px-5 py-2.5 rounded-full bg-white/5 hover:bg-white/10 text-white/90 hover:text-white font-medium text-sm border border-white/15 hover:border-white/25 backdrop-blur-md transition-all duration-200 active:scale-[0.98]",
            "description": "Balanced secondary action with frosted backdrop and micro-border"
        },
        "subtle_ghost": {
            "name": "Subtle Ghost Button",
            "tailwind": "inline-flex items-center justify-center px-4 py-2 rounded-lg text-neutral-400 hover:text-white hover:bg-white/5 font-medium text-sm transition-colors duration-150",
            "description": "Low-prominence tertiary button for quiet navigation or secondary actions"
        }
    },
    "card_and_bento_primitives": {
        "title": "Card & Bento Primitives",
        "layered_depth_card": {
            "name": "Layered Z-Depth Card",
            "tailwind": "relative rounded-2xl bg-[#111827]/80 hover:bg-[#161F33]/90 border border-white/10 hover:border-white/20 p-6 shadow-2xl backdrop-blur-xl transition-all duration-250 hover:-translate-y-1 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.12)]",
            "description": "Multi-layer surface with interior specular rim and subtle hover lift"
        },
        "bento_feature_cell": {
            "name": "Bento Feature Cell",
            "tailwind": "group relative overflow-hidden rounded-3xl bg-gradient-to-b from-white/[0.07] to-white/[0.02] border border-white/10 hover:border-indigo-500/30 p-8 transition-all duration-300 hover:shadow-[0_20px_40px_-15px_rgba(0,0,0,0.7)]",
            "description": "Feature matrix cell with subtle radial backdrop gradient and highlight border"
        },
        "hover_lift_container": {
            "name": "Hover Lift & Ambient Glow",
            "tailwind": "transition-all duration-300 ease-out hover:-translate-y-1 hover:shadow-[0_12px_32px_-8px_rgba(99,102,241,0.25)]",
            "description": "Clean physical hover response without jarring layout displacement"
        }
    },
    "navigation_primitives": {
        "title": "Navigation Primitives",
        "floating_pill_bar": {
            "name": "Floating Pill Bar",
            "tailwind": "fixed top-6 inset-x-0 mx-auto w-fit max-w-2xl px-5 py-2.5 rounded-full bg-[#0B0F19]/80 backdrop-blur-xl border border-white/10 shadow-2xl z-50 flex items-center gap-6 text-sm text-neutral-300",
            "description": "Centered floating pill navigation dock with glass backdrop blur"
        },
        "minimal_border_header": {
            "name": "Minimal Border Header",
            "tailwind": "sticky top-0 w-full h-16 bg-[#0B0F19]/90 backdrop-blur-md border-b border-white/10 px-8 flex items-center justify-between z-40",
            "description": "Full-width sticky navigation bar with crisp hairline bottom divider"
        },
        "mobile_command_drawer": {
            "name": "Mobile / Command Drawer",
            "tailwind": "fixed inset-y-0 right-0 w-80 bg-[#0B0F19] border-l border-white/10 p-6 shadow-2xl z-50 backdrop-blur-2xl transition-transform duration-300 ease-out",
            "description": "Side drawer panel for off-canvas navigation or command palettes"
        }
    },
    "quiet_transition_specs": {
        "title": "Clean Transition Specs (Quiet Supporting Details)",
        "interactive_standard": {"duration_ms": 200, "curve": "cubic-bezier(0.16, 1, 0.3, 1)", "usage": "Buttons, cards, and toggles"},
        "sheet_reveal": {"duration_ms": 280, "curve": "cubic-bezier(0.16, 1, 0.3, 1)", "usage": "Drawers, sheets, modals"},
        "micro_tap": {"duration_ms": 150, "curve": "cubic-bezier(0.2, 0, 0, 1)", "usage": "Active press and chip selection"}
    }
}

# The 6 Universal Industry-Standard UI Design System Archetypes
UI_DESIGN_ARCHETYPES = [
    {
        "id": "interactive-dark-bento-grid-feature-section",
        "title": "Modern SaaS & Cloud Platform (Bento Feature Matrix & Metric Telemetry)",
        "archetype": "Modern SaaS & Cloud Platform",
        "archetype_key": 1,
        "category": "SaaS & Dashboard",
        "source_site": "pixlpin.com",
        "source_url": "https://pixlpin.com/d/interactive-dark-bento-grid-feature-section",
        "description": "Production-grade dark SaaS landing page featuring floating pill navigation, centered value proposition hero, 4-cell interactive bento feature matrix, real-time metric counters, and radial ambient lighting.",
        "video_url": "https://pixlpin.com/media/designs/01M4ZCV5Y7Y1HTW5ZG8ZCNSTQT/mp4-baf830c9.mp4",
        "local_video": "videos/interactive-dark-bento-grid-feature-section.mp4",
        "relevance_score": 1.0,
        "is_3d": False,
        "is_liquid_glass": False,
        "design_system": {
            "components": [
                "Top Navigation: Floating frosted pill bar (bg-[#0B0F19]/80, border-white/10, logo, nav links, primary CTA button)",
                "Hero Section: Centered headline with gradient highlight, dual CTA cluster (Primary glow + Secondary border), social proof ticker",
                "Bento Feature Matrix: 4-cell asymmetrical grid with layered Z-depth cards, subtle rim lighting, and hover lift",
                "Interactive Metrics: Real-time telemetry counter pill with pulsing green live status badge (bg-emerald-500/10 text-emerald-400)",
                "Bottom CTA Banner: Radial ambient glow spotlight, email capture input with inline submit"
            ],
            "visual_styling": {
                "surfaces": "Canvas bg-[#0B0F19], Cards bg-[#111827], Elevated border border-white/10",
                "lighting": "Top-centered radial ambient glow (radial-gradient(circle 800px at 50% 0%, rgba(99, 102, 241, 0.15), transparent)), rim light (shadow-[inset_0_1px_0_0_rgba(255,255,255,0.12)])",
                "accents": "Primary Indigo #6366F1, Accent Violet #8B5CF6, Status Emerald #10B981, Foreground #F9FAFB",
                "typography": "Heading Space Grotesk or Plus Jakarta Sans, Body Inter (weights: 400, 500, 600)"
            },
            "transition_spec": {
                "duration_ms": 240,
                "curve": "cubic-bezier(0.16, 1, 0.3, 1)",
                "notes": "Quiet supporting transition detail with hover lift -translate-y-1"
            },
            "code_scaffold": (
                "// Modern SaaS Bento Grid & Ambient Glow Scaffold\n"
                "export function ModernSaaSPlatform() {\n"
                "  return (\n"
                "    <div className=\"min-h-screen bg-[#0B0F19] text-white relative overflow-hidden\">\n"
                "      {/* Radial Ambient Glow */}\n"
                "      <div className=\"absolute -top-40 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-gradient-to-b from-indigo-500/20 via-purple-500/10 to-transparent blur-[120px] pointer-events-none -z-10\" />\n\n"
                "      {/* Floating Pill Nav */}\n"
                "      <header className=\"fixed top-6 inset-x-0 mx-auto w-fit max-w-2xl px-5 py-2.5 rounded-full bg-[#0B0F19]/80 backdrop-blur-xl border border-white/10 shadow-2xl z-50 flex items-center gap-6 text-sm\">\n"
                "        <span className=\"font-bold tracking-tight text-white\">PulseCloud</span>\n"
                "        <nav className=\"flex items-center gap-5 text-neutral-400 text-xs font-medium\">\n"
                "          <a href=\"#features\" className=\"hover:text-white transition-colors\">Platform</a>\n"
                "          <a href=\"#metrics\" className=\"hover:text-white transition-colors\">Metrics</a>\n"
                "          <a href=\"#pricing\" className=\"hover:text-white transition-colors\">Pricing</a>\n"
                "        </nav>\n"
                "        <button className=\"inline-flex items-center px-4 py-1.5 rounded-full bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium shadow-[0_0_16px_rgba(99,102,241,0.4)] transition-all\">\n"
                "          Start Free\n"
                "        </button>\n"
                "      </header>\n\n"
                "      {/* Hero Section */}\n"
                "      <main className=\"pt-36 pb-20 px-6 max-w-6xl mx-auto\">\n"
                "        <div className=\"text-center space-y-6 max-w-3xl mx-auto\">\n"
                "          <div className=\"inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs font-medium\">\n"
                "            <span className=\"w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse\" /> Next-Gen Cloud Telemetry v2.4\n"
                "          </div>\n"
                "          <h1 className=\"text-5xl md:text-6xl font-extrabold tracking-tight text-white\">\n"
                "            Orchestrate Cloud Workflows <span className=\"text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-violet-400\">Without Friction</span>\n"
                "          </h1>\n"
                "          <p className=\"text-neutral-400 text-lg\">\n"
                "            Continuous infrastructure synchronization, sub-millisecond edge metrics, and automated deployment pipelines.\n"
                "          </p>\n"
                "          <div className=\"flex items-center justify-center gap-4 pt-2\">\n"
                "            <button className=\"px-6 py-3 rounded-full bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm shadow-[0_0_24px_rgba(99,102,241,0.4)] transition-all duration-200 active:scale-98\">\n"
                "              Deploy in 60s\n"
                "            </button>\n"
                "            <button className=\"px-5 py-2.5 rounded-full bg-white/5 hover:bg-white/10 text-white/90 border border-white/15 backdrop-blur-md text-sm font-medium transition-all duration-200\">\n"
                "              Live Sandbox\n"
                "            </button>\n"
                "          </div>\n"
                "        </div>\n\n"
                "        {/* Bento Feature Grid */}\n"
                "        <div className=\"grid grid-cols-1 md:grid-cols-3 gap-6 mt-20\">\n"
                "          <div className=\"md:col-span-2 rounded-3xl bg-[#111827]/80 border border-white/10 p-8 shadow-2xl shadow-[inset_0_1px_0_0_rgba(255,255,255,0.12)] hover:border-white/20 transition-all duration-240 hover:-translate-y-1\">\n"
                "            <div className=\"flex items-center justify-between pb-6\">\n"
                "              <h3 className=\"text-xl font-bold\">Real-time Telemetry Feed</h3>\n"
                "              <span className=\"px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-mono\">99.999% Uptime</span>\n"
                "            </div>\n"
                "            <p className=\"text-neutral-400 text-sm\">Sub-millisecond packet processing with distributed Raft consensus.</p>\n"
                "          </div>\n"
                "          <div className=\"rounded-3xl bg-[#111827]/80 border border-white/10 p-8 shadow-2xl shadow-[inset_0_1px_0_0_rgba(255,255,255,0.12)] hover:border-white/20 transition-all duration-240 hover:-translate-y-1\">\n"
                "            <h3 className=\"text-xl font-bold pb-2\">Global Edge</h3>\n"
                "            <p className=\"text-neutral-400 text-sm\">310+ edge PoPs with automatic nearest-neighbor routing.</p>\n"
                "          </div>\n"
                "        </div>\n"
                "      </main>\n"
                "    </div>\n"
                "  );\n"
                "}"
            )
        }
    },
    {
        "id": "highnote",
        "title": "Next-Gen Fintech & Data (Telemetry Feed & High-Contrast Dark)",
        "archetype": "Next-Gen Fintech & Data",
        "archetype_key": 2,
        "category": "Fintech",
        "source_site": "pixlpin.com",
        "source_url": "https://pixlpin.com/d/highnote",
        "description": "Fintech interface featuring high-contrast dark aesthetic, live data telemetry feeds, security compliance badges, sparklines, and precision numerical data display.",
        "video_url": "https://pixlpin.com/media/designs/01M4R69JZD09DQCPPYCRZP4QSR/mp4-aa5bca45.mp4",
        "local_video": "videos/highnote.mp4",
        "relevance_score": 0.98,
        "is_3d": False,
        "is_liquid_glass": False,
        "design_system": {
            "components": [
                "Header & Telemetry Bar: Sticky minimal border navbar with live market ticker & network status dot",
                "Hero Stage: Split layout with bold monetary yield callout, dynamic sparkline telemetry canvas, security certification badge",
                "Security Badges: Monospace SOC2 Type II, 256-bit AES encryption badge with verified shield icon",
                "Live Stats & Data Grid: High-contrast data tables, tabbed stream selector, monospace latency counters (12ms)",
                "Interactive Card: Instant transfer/exchange module with interactive slider and fee breakdown"
            ],
            "visual_styling": {
                "surfaces": "Jet Black bg-[#07090E], Card Surface bg-[#0E131F], Rim border border-white/15",
                "lighting": "Laser cyan / neon blue rim glow (rgba(6, 182, 212, 0.2)), subtle specular card highlights",
                "accents": "Accent Cyan #06B6D4, Neon Green #22C55E, Electric Indigo #4F46E5, Text #F1F5F9",
                "typography": "Display Space Grotesk, Data & Numbers JetBrains Mono or Geist Mono"
            },
            "transition_spec": {
                "duration_ms": 200,
                "curve": "cubic-bezier(0.08, 0.82, 0.17, 1.0)",
                "notes": "Crisp resting state with zero float"
            },
            "code_scaffold": (
                "// Next-Gen Fintech & Data Telemetry Scaffold\n"
                "export function FintechTelemetryPlatform() {\n"
                "  return (\n"
                "    <div className=\"min-h-screen bg-[#07090E] text-[#F1F5F9] font-sans antialiased p-8\">\n"
                "      <div className=\"max-w-6xl mx-auto space-y-8\">\n"
                "        {/* Security & Telemetry Header */}\n"
                "        <div className=\"flex items-center justify-between border-b border-white/10 pb-6\">\n"
                "          <div className=\"flex items-center gap-4\">\n"
                "            <span className=\"text-xl font-bold tracking-tight text-white font-mono\">AETHER::LEDGER</span>\n"
                "            <span className=\"px-2 py-0.5 rounded text-[11px] font-mono bg-cyan-500/10 text-cyan-400 border border-cyan-500/20\">PCI-DSS L1</span>\n"
                "            <span className=\"px-2 py-0.5 rounded text-[11px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20\">SOC2 TYPE II</span>\n"
                "          </div>\n"
                "          <div className=\"flex items-center gap-4 text-xs font-mono text-neutral-400\">\n"
                "            <span className=\"flex items-center gap-1.5\">\n"
                "              <span className=\"w-2 h-2 rounded-full bg-emerald-400 animate-ping\" /> FEED_ONLINE\n"
                "            </span>\n"
                "            <span>LATENCY: 12ms</span>\n"
                "          </div>\n"
                "        </div>\n\n"
                "        {/* Hero Metrics Stage */}\n"
                "        <div className=\"grid grid-cols-1 md:grid-cols-3 gap-6\">\n"
                "          <div className=\"rounded-2xl bg-[#0E131F] border border-white/10 p-6 shadow-2xl shadow-[inset_0_1px_0_0_rgba(255,255,255,0.15)]\">\n"
                "            <p className=\"text-xs font-mono uppercase text-neutral-400\">Global Settlement Volume</p>\n"
                "            <p className=\"text-3xl font-extrabold text-white font-mono mt-2\">$1,482,904,120</p>\n"
                "            <p className=\"text-xs text-emerald-400 font-mono mt-3 flex items-center gap-1\">▲ +18.4% 24h rolling</p>\n"
                "          </div>\n"
                "        </div>\n"
                "      </div>\n"
                "    </div>\n"
                "  );\n"
                "}"
            )
        }
    },
    {
        "id": "united-in-football-interactive-editorial-landing-page",
        "title": "High-End Ecommerce & Fashion (Editorial Showcase & Sticky Buy Stage)",
        "archetype": "High-End Ecommerce & Fashion",
        "archetype_key": 3,
        "category": "Fashion & Ecommerce",
        "source_site": "pixlpin.com",
        "source_url": "https://pixlpin.com/d/united-in-football-interactive-editorial-landing-page",
        "description": "Editorial luxury fashion showcase featuring full-bleed product stage, serif display typography, alternating lookbook grid, and docked sticky buy bar.",
        "video_url": "https://pixlpin.com/media/designs/01M4GAQYD9JH1MY3G3APHVF54W/mp4-83dd1528.mp4",
        "local_video": "videos/united-in-football-interactive-editorial-landing-page.mp4",
        "relevance_score": 0.96,
        "is_3d": False,
        "is_liquid_glass": False,
        "design_system": {
            "components": [
                "Top Editorial Nav: Ultra-minimal monochrome brand masthead with currency selector and slide-over bag trigger",
                "Hero Product Stage: Full-bleed editorial photography canvas, staggered serif typography, floating zoom trigger",
                "Sticky Buy Bar: Bottom-docked translucent bar (bg-[#0A0A0B]/85, backdrop-blur-xl) with variant selector and Pre-Order CTA",
                "Lookbook Masonry: Alternating wide & tall editorial cards with smooth hover parallax and quiet text reveals",
                "Material & Craft Accordion: Micro-collapsible technical specifications with clean rule lines"
            ],
            "visual_styling": {
                "surfaces": "Rich Noir bg-[#0A0A0B], Elevated Card bg-[#141416], Border border-white/10",
                "lighting": "Soft studio diffused light, deep soft drop shadows (shadow-[0_30px_70px_rgba(0,0,0,0.5)])",
                "accents": "Warm Champagne #E2D9C8, Deep Charcoal #1A1A1A, Pure White #FFFFFF, Muted Silver #A1A1AA",
                "typography": "Serif Display (Playfair Display, Cormorant Garamond, or Instrument Serif), Body Inter"
            },
            "transition_spec": {
                "duration_ms": 350,
                "curve": "cubic-bezier(0.25, 1, 0.5, 1)",
                "notes": "Fluid ease-out for luxurious editorial pacing"
            },
            "code_scaffold": (
                "// High-End Ecommerce & Editorial Scaffold\n"
                "export function HighEndFashionShowcase() {\n"
                "  return (\n"
                "    <div className=\"min-h-screen bg-[#0A0A0B] text-neutral-100 selection:bg-[#E2D9C8] selection:text-black\">\n"
                "      {/* Editorial Top Masthead */}\n"
                "      <header className=\"border-b border-white/10 px-8 py-5 flex items-center justify-between text-xs uppercase tracking-widest\">\n"
                "        <span>Collection 04 / Autumn</span>\n"
                "        <span className=\"font-serif text-xl tracking-normal lowercase italic\">maison aether</span>\n"
                "        <div className=\"flex items-center gap-6\">\n"
                "          <span>USD ($)</span>\n"
                "          <button className=\"hover:opacity-60 transition-opacity\">Bag [0]</button>\n"
                "        </div>\n"
                "      </header>\n\n"
                "      {/* Hero Product Stage */}\n"
                "      <section className=\"max-w-7xl mx-auto px-8 py-16 grid grid-cols-1 md:grid-cols-12 gap-12 items-center\">\n"
                "        <div className=\"md:col-span-5 space-y-6\">\n"
                "          <p className=\"text-xs uppercase tracking-widest text-neutral-400\">Limited Atelier Run • 120 Units</p>\n"
                "          <h1 className=\"font-serif text-5xl md:text-6xl font-normal leading-tight text-white\">\n"
                "            The Architectural Trench Coat\n"
                "          </h1>\n"
                "          <p className=\"text-neutral-400 text-sm leading-relaxed\">\n"
                "            Double-faced Italian virgin wool with waterproof membrane bonded interior and horn button closures.\n"
                "          </p>\n"
                "          <p className=\"text-2xl font-serif text-[#E2D9C8]\">$1,250</p>\n"
                "        </div>\n"
                "      </section>\n\n"
                "      {/* Docked Sticky Buy Bar */}\n"
                "      <aside className=\"fixed bottom-6 inset-x-0 mx-auto w-fit max-w-xl px-6 py-3 rounded-full bg-[#0A0A0B]/90 backdrop-blur-2xl border border-white/15 shadow-2xl flex items-center gap-6 z-50\">\n"
                "        <span className=\"text-xs font-serif italic text-[#E2D9C8]\">Maison Trench — $1,250</span>\n"
                "        <button className=\"px-6 py-2 rounded-full bg-white text-black font-medium text-xs uppercase tracking-wider hover:bg-[#E2D9C8] transition-colors\">\n"
                "          Pre-Order Item\n"
                "        </button>\n"
                "      </aside>\n"
                "    </div>\n"
                "  );\n"
                "}"
            )
        }
    },
    {
        "id": "zeroframe-studio-portfolio-framework-motion-showcase",
        "title": "Creative Studio & Portfolio (Kinetic Typography & Work Showcase Cards)",
        "archetype": "Creative Studio & Portfolio",
        "archetype_key": 4,
        "category": "Portfolio & Agency",
        "source_site": "pixlpin.com",
        "source_url": "https://pixlpin.com/d/zeroframe-studio-portfolio-framework-motion-showcase",
        "description": "High-craft design studio portfolio featuring oversized kinetic typography, interactive work showcase cards with hover expansion, magnetic hover CTAs, and live availability badge.",
        "video_url": "https://pixlpin.com/media/designs/01M4HGM3GRE3F6E7SQRANGQ4S3/mp4-2f6d0c45.mp4",
        "local_video": "videos/zeroframe-studio-portfolio-framework-motion-showcase.mp4",
        "relevance_score": 0.94,
        "is_3d": False,
        "is_liquid_glass": False,
        "design_system": {
            "components": [
                "Navigation: Floating capsule nav with live availability status pill (Available for Q2 Projects)",
                "Hero Stage: Massive kinetic display headline with line-reveal clipping and interactive word hover",
                "Work Showcase Reel: Full-width project index cards with hover image expansion and custom cursor follower",
                "Interactive Service Matrix: Horizontal scroll row or accordion grid with hover video scrub",
                "Magnetic CTA Footer: Large contact trigger with mouse-following magnetic button and copy-email quick chip"
            ],
            "visual_styling": {
                "surfaces": "Deep Obsidian bg-[#080808], Secondary Surface bg-[#121212], Hairline divider border-white/12",
                "lighting": "Dynamic spotlight tracking cursor angle, high-contrast monochrome with bright accent pop",
                "accents": "Acid Lime #84CC16 or Vivid Amber #F59E0B, Monochromatic high-contrast #FFFFFF / #737373",
                "typography": "Display Syne or Clash Display (weights 700, 800), Body Inter (weights 400, 500)"
            },
            "transition_spec": {
                "duration_ms": 280,
                "curve": "cubic-bezier(0.19, 1, 0.22, 1)",
                "notes": "Magnetic spring damping with smooth follow-through"
            },
            "code_scaffold": (
                "// Creative Studio Kinetic Portfolio Scaffold\n"
                "export function CreativeStudioPortfolio() {\n"
                "  return (\n"
                "    <div className=\"min-h-screen bg-[#080808] text-white p-8\">\n"
                "      {/* Floating Availability Pill */}\n"
                "      <div className=\"fixed top-6 right-8 z-50 inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-[#121212]/90 border border-white/10 text-xs font-medium\">\n"
                "        <span className=\"w-2 h-2 rounded-full bg-[#84CC16] animate-pulse\" /> Available for Q2 / Q3 Design\n"
                "      </div>\n\n"
                "      {/* Massive Kinetic Headline */}\n"
                "      <section className=\"pt-32 pb-24 max-w-6xl mx-auto\">\n"
                "        <h1 className=\"text-6xl md:text-8xl font-black uppercase tracking-tighter leading-none\">\n"
                "          We Craft <span className=\"text-[#84CC16]\">Digital</span> Hardware Grade Experiences\n"
                "        </h1>\n"
                "      </section>\n\n"
                "      {/* Showcase Cards */}\n"
                "      <section className=\"max-w-6xl mx-auto space-y-4\">\n"
                "        {['Fintech Terminal', 'Spatial Audio Engine', 'Autonomous Agent UI'].map((title, i) => (\n"
                "          <div key={i} className=\"group border-t border-white/15 py-8 flex items-center justify-between hover:px-4 hover:bg-white/5 transition-all duration-280 rounded-xl cursor-pointer\">\n"
                "            <span className=\"text-2xl md:text-3xl font-bold\">{title}</span>\n"
                "            <span className=\"text-sm text-neutral-400 group-hover:text-white transition-colors\">View Project →</span>\n"
                "          </div>\n"
                "        ))}\n"
                "      </section>\n"
                "    </div>\n"
                "  );\n"
                "}"
            )
        }
    },
    {
        "id": "developer-tool-ai-session-replay-interface",
        "title": "Developer Tools & API Platform (Interactive Terminal & Command Palette)",
        "archetype": "Developer Tools & API Platform",
        "archetype_key": 5,
        "category": "Developer Tools",
        "source_site": "pixlpin.com",
        "source_url": "https://pixlpin.com/d/developer-tool-ai-session-replay-interface",
        "description": "Developer platform interface featuring interactive multi-tab terminal, syntax-highlighted code snippets, command palette trigger (Cmd+K), and real-time API latency benchmark pills.",
        "video_url": "https://pixlpin.com/media/designs/01M4YV5YX1PFDXJ1RDDHP5AXSS/mp4-8654f9f7.mp4",
        "local_video": "videos/developer-tool-ai-session-replay-interface.mp4",
        "relevance_score": 0.92,
        "is_3d": False,
        "is_liquid_glass": False,
        "design_system": {
            "components": [
                "Global Header & Command Bar: Top bar with breadcrumb trail, environment picker (Production), and Cmd+K trigger",
                "Hero Interactive Terminal: Multi-tab code editor (Bash, Python, TypeScript) with syntax highlighting and copy button",
                "API Endpoint Feature Cards: Card matrix showcasing payload schemas, SDK install snippets, and latency pills (< 15ms p99)",
                "Architecture Interactive Diagram: Node flow showing API gateway to serverless worker pipeline",
                "Quickstart CLI Drawer: Collapsible bottom drawer with one-line curl or npm i interactive runner"
            ],
            "visual_styling": {
                "surfaces": "Dark Slate bg-[#0D1117], Editor Stage bg-[#161B22], Border border-white/12",
                "lighting": "Subtle top rim-light on terminal header, colored terminal status dots (macOS style: red, yellow, green)",
                "accents": "Emerald #10B981, Amber #F59E0B, Sky #0284C7, Monospace accents",
                "typography": "Body Inter, Code & Terminal JetBrains Mono or Fira Code"
            },
            "transition_spec": {
                "duration_ms": 180,
                "curve": "cubic-bezier(0.16, 1, 0.3, 1)",
                "notes": "Instant tactile feedback for developer ergonomics"
            },
            "code_scaffold": (
                "// Developer Tools & API Terminal Scaffold\n"
                "export function DevToolsPlatform() {\n"
                "  return (\n"
                "    <div className=\"min-h-screen bg-[#0D1117] text-neutral-200 font-sans p-8\">\n"
                "      <div className=\"max-w-5xl mx-auto space-y-8\">\n"
                "        {/* Interactive Terminal Card */}\n"
                "        <div className=\"rounded-2xl bg-[#161B22] border border-white/10 shadow-2xl overflow-hidden font-mono text-sm\">\n"
                "          <div className=\"bg-white/5 px-4 py-3 border-b border-white/10 flex items-center justify-between\">\n"
                "            <div className=\"flex items-center gap-2\">\n"
                "              <div className=\"w-3 h-3 rounded-full bg-rose-500/80\" />\n"
                "              <div className=\"w-3 h-3 rounded-full bg-amber-500/80\" />\n"
                "              <div className=\"w-3 h-3 rounded-full bg-emerald-500/80\" />\n"
                "              <span className=\"ml-3 text-xs text-neutral-400\">quickstart.sh</span>\n"
                "            </div>\n"
                "            <button className=\"px-3 py-1 rounded bg-white/10 hover:bg-white/15 text-xs text-white transition-colors\">Copy</button>\n"
                "          </div>\n"
                "          <div className=\"p-6 space-y-2 text-xs\">\n"
                "            <p className=\"text-neutral-500\"># Install via package manager</p>\n"
                "            <p><span className=\"text-emerald-400\">$</span> npm install @unfslop/engine-core</p>\n"
                "            <p className=\"text-neutral-500 pt-2\"># Initialize live agent runtime</p>\n"
                "            <p><span className=\"text-emerald-400\">$</span> npx unfslop init --archetype=saas</p>\n"
                "          </div>\n"
                "        </div>\n"
                "      </div>\n"
                "    </div>\n"
                "  );\n"
                "}"
            )
        }
    },
    {
        "id": "ai-code-security-assistant-chat-interface",
        "title": "AI-Native Platform & Workflow (Chat Composer & Multi-Agent Canvas)",
        "archetype": "AI-Native Platform & Workflow",
        "archetype_key": 6,
        "category": "AI & Machine Learning",
        "source_site": "pixlpin.com",
        "source_url": "https://pixlpin.com/d/ai-code-security-assistant-chat-interface",
        "description": "AI-native workspace interface featuring split-view canvas, multi-agent status tiles, floating omnibox chat composer, and streaming message feed with code artifacts.",
        "video_url": "https://pixlpin.com/media/designs/01M4Z3FY14Y82GDQJ43VBMJFJE/mp4sm-c8fbc373.mp4",
        "local_video": "videos/ai-code-security-assistant-chat-interface.mp4",
        "relevance_score": 0.90,
        "is_3d": False,
        "is_liquid_glass": False,
        "design_system": {
            "components": [
                "Split-View Canvas Layout: Left sidebar (agent status, workflow history), Center (chat composer & streaming response), Right (live preview/canvas)",
                "Multi-Agent Status Tiles: Status pills displaying reasoning state (Planner, Coder, Reviewer with pulse indicator)",
                "Conversational Stream & Code Artifact: Message bubbles with syntax-highlighted code blocks, diff toggles, and copy buttons",
                "Omnibox Chat Composer: Bottom-docked floating composer with attachment chip, model selector dropdown, and send trigger",
                "Context & Citation Pills: Interactive pill chips showing source documents, search citations, and token count meters"
            ],
            "visual_styling": {
                "surfaces": "Neutral Deep bg-[#0A0D14], Active Panel bg-[#121722], Composer bg-[#182030], Glass Border border-white/10",
                "lighting": "Subtle pulsing gradient border on active agent card (from-indigo-500/30 to-purple-500/30), ambient backdrop blur",
                "accents": "Violet #8B5CF6, Indigo #6366F1, Rose #F43F5E, Canvas text #F8FAFC",
                "typography": "Interface Inter or Geist Sans, Monospace Geist Mono"
            },
            "transition_spec": {
                "duration_ms": 220,
                "curve": "cubic-bezier(0.05, 0.9, 0.1, 1.0)",
                "notes": "Smooth conversational streaming entrance with subtle Y-offset"
            },
            "code_scaffold": (
                "// AI-Native Multi-Agent Canvas & Composer Scaffold\n"
                "export function AINativeCanvasPlatform() {\n"
                "  return (\n"
                "    <div className=\"min-h-screen bg-[#0A0D14] text-white flex flex-col\">\n"
                "      {/* Top Agent Bar */}\n"
                "      <header className=\"h-14 border-b border-white/10 px-6 flex items-center justify-between bg-[#121722]/50 backdrop-blur-md\">\n"
                "        <div className=\"flex items-center gap-3\">\n"
                "          <span className=\"font-bold text-sm\">Workflow Canvas</span>\n"
                "          <span className=\"px-2.5 py-0.5 rounded-full text-xs bg-indigo-500/10 text-indigo-400 border border-indigo-500/20\">4 Agents Active</span>\n"
                "        </div>\n"
                "      </header>\n\n"
                "      {/* Split View Stage */}\n"
                "      <div className=\"flex-1 flex overflow-hidden\">\n"
                "        {/* Left Agent Stream */}\n"
                "        <div className=\"flex-1 p-6 space-y-4 overflow-y-auto max-w-2xl mx-auto\">\n"
                "          <div className=\"rounded-2xl bg-[#121722] border border-white/10 p-5 space-y-2\">\n"
                "            <div className=\"flex items-center gap-2 text-xs font-mono text-indigo-400\">\n"
                "              <span className=\"w-2 h-2 rounded-full bg-indigo-400 animate-pulse\" /> Architect Agent\n"
                "            </div>\n"
                "            <p className=\"text-sm text-neutral-300\">Synthesized 6-archetype UI component library and verified zero slop floor.</p>\n"
                "          </div>\n"
                "        </div>\n"
                "      </div>\n\n"
                "      {/* Floating Omnibox Composer */}\n"
                "      <div className=\"p-6 max-w-2xl mx-auto w-full\">\n"
                "        <div className=\"relative rounded-2xl bg-[#182030] border border-white/15 shadow-2xl p-3 flex items-center gap-3\">\n"
                "          <input placeholder=\"Direct agent swarm or describe design requirement...\" className=\"flex-1 bg-transparent px-3 text-sm focus:outline-none text-white\" />\n"
                "          <button className=\"px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition-colors\">Send</button>\n"
                "        </div>\n"
                "      </div>\n"
                "    </div>\n"
                "  );\n"
                "}"
            )
        }
    }
]

def get_item_category(item) -> str:
    """Return explicit category or infer one intelligently."""
    cat = item.get("category")
    if cat and str(cat).strip():
        return str(cat).strip()

    text = f"{item.get('title', '')} {item.get('description', '')}".lower()
    if any(k in text for k in ["liquid", "refraction", "glass", "chromatic"]):
        return "Liquid Glass"
    if any(k in text for k in ["3d", "webgl", "canvas", "particle", "mesh", "orbit", "shader", "point-cloud"]):
        return "3D & Spatial"
    if any(k in text for k in ["crypto", "trading", "fintech", "wallet", "finance", "bank"]):
        return "Fintech"
    if any(k in text for k in ["ai", "agent", "bot", "assistant", "model", "prompt"]):
        return "AI & Machine Learning"
    if any(k in text for k in ["saas", "dashboard", "analytics", "metric", "b2b"]):
        return "SaaS & Dashboard"
    if any(k in text for k in ["fashion", "luxury", "apparel", "wear", "editorial"]):
        return "Fashion"
    if any(k in text for k in ["ecommerce", "shop", "store", "product", "checkout", "cart"]):
        return "Ecommerce"
    if any(k in text for k in ["hero", "headline", "landing"]):
        return "Hero & Landing"
    if any(k in text for k in ["portfolio", "agency", "creator", "studio"]):
        return "Portfolio & Agency"
    if any(k in text for k in ["developer", "code", "terminal", "ide", "api", "replay"]):
        return "Developer Tools"
    return "UI Motion Showcase"

def get_source_info(item):
    """Extract source website and URL cleanly."""
    source_site = item.get("source_site")
    source_url = item.get("source_url") or ""
    if not source_site:
        if "motionsites.ai" in source_url:
            source_site = "motionsites.ai"
        elif "pixlpin.com" in source_url:
            source_site = "pixlpin.com"
        else:
            source_site = "Curated UI Showcase"
    return source_site, source_url

def is_liquid_glass_showcase(item) -> bool:
    """Check if showcase exhibits liquid glass, glassmorphism, or refractive dynamics."""
    if item.get("is_liquid_glass") is True:
        return True
    text = f"{item.get('title', '')} {item.get('description', '')} {item.get('category', '')} {item.get('id', '')} {str(item.get('full_prompt', ''))[:400]}".lower()
    return any(k in text for k in LIQUID_GLASS_KEYWORDS)

def is_3d_showcase(item) -> bool:
    """Check if showcase exhibits 3D, WebGL, particle, kinetic, or spatial dynamics."""
    if item.get("is_3d") is True:
        return True
    text = f"{item.get('title', '')} {item.get('description', '')} {item.get('category', '')} {item.get('id', '')} {str(item.get('full_prompt', ''))[:400]}".lower()
    return any(k in text for k in THREED_KEYWORDS)

def matches_category(item, category_query: str) -> bool:
    """Case-insensitive substring or exact match on category."""
    if not category_query:
        return True
    cat = get_item_category(item).lower()
    cq = category_query.strip().lower()
    return cq in cat or cq == cat

# Words that carry no specific design subject on their own. A query made up
# entirely of these (plus English stopwords) is genuinely vague and falls back
# to the archetype defaults; any real subject word makes it a retrieval query.
_GENERIC_QUERY_WORDS = frozenset({
    "creative", "creativity", "landing", "hero", "showcase", "portfolio",
    "homepage", "website", "web", "site", "page", "app", "application",
    "ui", "ux", "design", "build", "modern", "cool", "best", "great",
    "awesome", "nice", "beautiful", "stunning", "something", "anything",
    "archetype", "archetypes", "brief", "project", "new", "mind", "blowing",
    "director", "system", "components", "component", "explore", "exploration",
    "inspiration", "ideas", "idea", "concept", "demo", "choice", "choose",
    "pick", "select", "example", "examples", "sample", "samples", "random",
    "whatever", "stuff", "things", "thing", "kind", "sort", "type", "types",
    "style", "styles", "look", "feel", "vibe", "vibes", "aesthetic",
})


def is_broad_or_creative_query(query: str) -> bool:
    """True only for empty or genuinely subject-free queries.

    A specific product/service brief (e.g. 'space travel brand landing page
    selling seats to mars') must retrieve real showcases, not archetype
    defaults. Strip English stopwords and generic web/design filler; if any
    substantive subject word remains, the query is specific and gets retrieved.
    """
    q = query.strip().lower()
    if not q:
        return True
    words = [w for w in re.split(r"[^a-z0-9]+", q) if len(w) > 1]
    content = [w for w in words
               if w not in ENGLISH_STOP_WORDS and w not in _GENERIC_QUERY_WORDS]
    return len(content) == 0

def derive_ui_design_spec(item) -> dict:
    """
    Derives production UI component architecture, surface tokens, lighting atmospheres,
    and quiet transition specs for any curated showcase.
    """
    title = item.get("title", "")
    desc = item.get("description", "")
    cat = get_item_category(item)
    text = f"{title} {desc} {cat}".lower()

    if any(k in text for k in ["fintech", "crypto", "trading", "wallet", "ledger", "bank"]):
        return {
            "components": [
                "Header & Telemetry Bar: Sticky minimal navbar with live currency ticker and network health dot",
                "Hero Metrics Stage: Split layout with large financial yield callout and sparkline telemetry graph",
                "Trust information: Only display product claims supported by the brief and verified evidence",
                "Transaction Feed: Filterable high-contrast table with tabbed stream controls",
                "Quick Action Card: Instant transfer/exchange module with slider input"
            ],
            "visual_styling": {
                "surfaces": "Jet Black bg-[#07090E], Card bg-[#0E131F], Rim border border-white/15",
                "lighting": "Laser cyan / neon blue rim glow (rgba(6, 182, 212, 0.2)), subtle specular card highlights",
                "accents": "Cyan #06B6D4, Emerald #22C55E, Electric Indigo #4F46E5",
                "typography": "Display Space Grotesk, Data & Numbers JetBrains Mono"
            },
            "transition_spec": {
                "duration_ms": 200,
                "curve": "cubic-bezier(0.08, 0.82, 0.17, 1.0)",
                "notes": "Crisp resting state with zero float"
            }
        }
    elif any(k in text for k in ["fashion", "apparel", "luxury", "editorial"]):
        return {
            "components": [
                "Top Editorial Nav: Ultra-minimal monochrome brand masthead with currency selector",
                "Hero Product Stage: Full-bleed product photography, staggered serif typography, zoom trigger",
                "Lookbook Masonry: Alternating wide & tall editorial cards with smooth hover parallax",
                "Sticky Buy Bar: Bottom-docked translucent bar with variant selector and Pre-Order CTA",
                "Material Specs Accordion: Collapsible technical specifications with clean rule lines"
            ],
            "visual_styling": {
                "surfaces": "Rich Noir bg-[#0A0A0B], Elevated Card bg-[#141416], Border border-white/10",
                "lighting": "Soft studio diffused light, deep soft drop shadows (shadow-[0_30px_70px_rgba(0,0,0,0.5)])",
                "accents": "Warm Champagne #E2D9C8, Pure White #FFFFFF, Muted Silver #A1A1AA",
                "typography": "Serif Display (Playfair Display or Instrument Serif), Body Inter"
            },
            "transition_spec": {
                "duration_ms": 350,
                "curve": "cubic-bezier(0.25, 1, 0.5, 1)",
                "notes": "Fluid ease-out for luxurious editorial pacing"
            }
        }
    elif any(k in text for k in ["developer", "code", "terminal", "ide", "api", "replay", "sdk"]):
        return {
            "components": [
                "Global Command Header: Top bar with breadcrumb path, environment pill, and Cmd+K trigger",
                "Interactive Terminal Stage: Multi-tab code snippet runner (Bash, TypeScript) with syntax colors",
                "API Endpoint Cards: Payload schemas and SDK snippets drawn from the actual API",
                "Architecture Flow: Node diagram showing request routing from edge gateway to worker",
                "CLI Quickstart Drawer: Collapsible sheet with one-click package manager copy runner"
            ],
            "visual_styling": {
                "surfaces": "Dark Slate bg-[#0D1117], Editor Stage bg-[#161B22], Border border-white/12",
                "lighting": "Top rim-light on terminal header, colored terminal status dots (macOS style)",
                "accents": "Emerald #10B981, Amber #F59E0B, Sky #0284C7",
                "typography": "Body Inter, Code & Terminal JetBrains Mono"
            },
            "transition_spec": {
                "duration_ms": 180,
                "curve": "cubic-bezier(0.16, 1, 0.3, 1)",
                "notes": "Instant tactile feedback for developer ergonomics"
            }
        }
    elif any(k in text for k in ["ai", "agent", "assistant", "model", "chat", "copilot"]):
        return {
            "components": [
                "Split-View Canvas Layout: Left sidebar (agent status), Center (chat composer), Right (preview canvas)",
                "Multi-Agent Status Tiles: Status pills displaying reasoning state (Planner, Coder, Reviewer)",
                "Conversational Stream: Message cards with syntax-highlighted code blocks and diff toggles",
                "Omnibox Chat Composer: Bottom-docked floating composer with attachment chip and model selector",
                "Context & Citation Pills: Interactive pill chips showing source documents and token meters"
            ],
            "visual_styling": {
                "surfaces": "Neutral Deep bg-[#0A0D14], Active Panel bg-[#121722], Composer bg-[#182030], Border border-white/10",
                "lighting": "Subtle pulsing gradient border on active agent card, ambient backdrop blur",
                "accents": "Violet #8B5CF6, Indigo #6366F1, Rose #F43F5E",
                "typography": "Interface Inter or Geist Sans, Monospace Geist Mono"
            },
            "transition_spec": {
                "duration_ms": 220,
                "curve": "cubic-bezier(0.05, 0.9, 0.1, 1.0)",
                "notes": "Smooth conversational streaming entrance with subtle Y-offset"
            }
        }
    elif any(k in text for k in ["portfolio", "agency", "creator", "studio"]):
        return {
            "components": [
                "Navigation: Floating capsule nav with live availability status pill (Available for Work)",
                "Hero Stage: Massive kinetic display headline with line-reveal clipping and word hover",
                "Work Showcase Reel: Full-width project index cards with hover expansion",
                "Interactive Service Matrix: Horizontal scroll row or accordion grid with hover video scrub",
                "Magnetic CTA Footer: Large contact trigger with mouse-following magnetic button"
            ],
            "visual_styling": {
                "surfaces": "Deep Obsidian bg-[#080808], Secondary Surface bg-[#121212], Divider border-white/12",
                "lighting": "Dynamic spotlight tracking cursor angle, high-contrast monochrome with bright accent pop",
                "accents": "Acid Lime #84CC16 or Vivid Amber #F59E0B, Pure White #FFFFFF",
                "typography": "Display Syne or Clash Display (weights 700, 800), Body Inter"
            },
            "transition_spec": {
                "duration_ms": 280,
                "curve": "cubic-bezier(0.19, 1, 0.22, 1)",
                "notes": "Magnetic spring damping with smooth follow-through"
            }
        }
    else:
        # Default / SaaS & Dashboard
        return {
            "components": [
                "Navigation: Floating frosted pill bar (bg-[#0B0F19]/80, border-white/10, logo, nav links, primary CTA)",
                "Hero Section: Centered headline with gradient highlight, dual CTA cluster, social proof ticker",
                "Bento Feature Matrix: 4-cell asymmetrical grid with layered Z-depth cards and subtle rim lighting",
                "Interactive Metrics: Real-time telemetry counter pill with pulsing green live status badge",
                "Bottom CTA Banner: Radial ambient glow spotlight, email capture input with inline submit"
            ],
            "visual_styling": {
                "surfaces": "Canvas bg-[#0B0F19], Cards bg-[#111827], Elevated border border-white/10",
                "lighting": "Top-centered radial ambient glow, rim light (shadow-[inset_0_1px_0_0_rgba(255,255,255,0.12)])",
                "accents": "Primary Indigo #6366F1, Accent Violet #8B5CF6, Status Emerald #10B981",
                "typography": "Heading Space Grotesk, Body Inter (weights: 400, 500, 600)"
            },
            "transition_spec": {
                "duration_ms": 240,
                "curve": "cubic-bezier(0.16, 1, 0.3, 1)",
                "notes": "Quiet supporting transition detail with hover lift -translate-y-1"
            }
        }

def load_data():
    """Load curated showcases from metadata or fallback dataset."""
    items = []
    if os.path.exists(META_PATH):
        with open(META_PATH, "r", encoding="utf-8") as f:
            try:
                items = json.load(f)
            except Exception:
                pass
    if not items and os.path.exists(FALLBACK_DATASET):
        with open(FALLBACK_DATASET, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        items.append(json.loads(line))
                    except Exception:
                        pass
    return items

def load_components():
    """Load the separate UI-component pool (21st.dev + skiper.ui code prompts)."""
    if os.path.exists(COMPONENTS_META_PATH):
        with open(COMPONENTS_META_PATH, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                pass
    return []

def list_categories(items):
    """Print all available categories with their item counts and exit."""
    counts = Counter()
    for it in items:
        cat = get_item_category(it)
        counts[cat] += 1

    total_items = len(items)
    print("\n=======================================================")
    print(f" UI Design System & Component Library Categories ({total_items} items total)")
    print("=======================================================\n")
    for cat, count in counts.most_common():
        pct = (count / total_items) * 100 if total_items else 0
        bar = "█" * max(1, int(pct / 2.5))
        print(f"  • {cat:<26} {count:>4} items ({pct:>4.1f}%)  {bar}")
    print(f"\nTotal: {len(counts)} categories across {total_items} showcases.\n")

def print_component_tokens(as_json=False):
    """Output ready-to-use production UI component tokens and primitives."""
    if as_json:
        print(json.dumps(COMPONENT_PRIMITIVES, indent=2, ensure_ascii=False))
        return

    print("======================================================================")
    print(" UI DESIGN SYSTEM: PRODUCTION COMPONENT & ATMOSPHERE PRIMITIVES")
    print(" Production-ready Tailwind CSS & styling tokens for high-craft interfaces")
    print("======================================================================\n")

    # 1. Lighting & Atmosphere
    la = COMPONENT_PRIMITIVES["lighting_and_atmosphere"]
    print(f"[1] {la['title'].upper()}")
    print("----------------------------------------------------------------------")
    print("• Surface Elevation Tokens:")
    for k, v in la["surface_elevations"].items():
        print(f"  - {v['description']:<36} {v.get('tailwind', ''):<20} (Value: {v.get('hex') or v.get('rgba')})")
    print(f"\n• {la['ambient_glow']['name']}:")
    print(f"  - Description: {la['ambient_glow']['description']}")
    print(f"  - Inline CSS:  {la['ambient_glow']['css']}")
    print(f"  - JSX Snippet: {la['ambient_glow']['tailwind_snippet']}")
    print(f"\n• {la['rim_light']['name']}:")
    print(f"  - Tailwind:    {la['rim_light']['tailwind']}")
    print(f"  - Description: {la['rim_light']['description']}\n")

    # 2. Buttons
    btn = COMPONENT_PRIMITIVES["button_primitives"]
    print(f"[2] {btn['title'].upper()}")
    print("----------------------------------------------------------------------")
    for k in ["primary_glow_cta", "secondary_border", "subtle_ghost"]:
        b = btn[k]
        print(f"• {b['name']}:")
        print(f"  - Role:  {b['description']}")
        print(f"  - Class: {b['tailwind']}\n")

    # 3. Cards & Bento
    cb = COMPONENT_PRIMITIVES["card_and_bento_primitives"]
    print(f"[3] {cb['title'].upper()}")
    print("----------------------------------------------------------------------")
    for k in ["layered_depth_card", "bento_feature_cell", "hover_lift_container"]:
        c = cb[k]
        print(f"• {c['name']}:")
        print(f"  - Role:  {c['description']}")
        print(f"  - Class: {c['tailwind']}\n")

    # 4. Navigation
    nav = COMPONENT_PRIMITIVES["navigation_primitives"]
    print(f"[4] {nav['title'].upper()}")
    print("----------------------------------------------------------------------")
    for k in ["floating_pill_bar", "minimal_border_header", "mobile_command_drawer"]:
        n = nav[k]
        print(f"• {n['name']}:")
        print(f"  - Role:  {n['description']}")
        print(f"  - Class: {n['tailwind']}\n")

    # 5. Transitions
    tr = COMPONENT_PRIMITIVES["quiet_transition_specs"]
    print(f"[5] {tr['title'].upper()}")
    print("----------------------------------------------------------------------")
    for k in ["interactive_standard", "sheet_reveal", "micro_tap"]:
        t = tr[k]
        print(f"• {t['usage']:<28} duration: {t['duration_ms']}ms | ease: {t['curve']}")
    print("\n======================================================================\n")

def format_full_blueprint(item, index=1):
    """Format the complete verbatim prompt blueprint and code implementation."""
    category = get_item_category(item)
    source_site, source_url = get_source_info(item)
    video_url = item.get("video_url", "N/A")
    title = item.get("title", "Showcase Design")
    full_prompt = item.get("full_prompt")
    ds = item.get("design_system") or {}

    lines = []
    lines.append("######################################################################")
    lines.append(f"[{index}] {title}")
    lines.append(f"Category: {category}  |  Source: {source_site}  |  Type: {item.get('type', 'experience')}")
    lines.append(f"Source URL: {source_url}")
    lines.append(f"Direct Video Asset: {video_url}")
    lines.append("----------------------------------------------------------------------")

    if full_prompt and str(full_prompt).strip():
        lines.append(str(full_prompt).strip())
    elif item.get("archetype"):
        ds = ds or derive_ui_design_spec(item)
        lines.append("Built-in archetype (authored preset)")
        lines.append(f"Build a production-grade, high-impact web interface for \"{title}\" with React, TypeScript, and Tailwind CSS.\n")
        lines.append("---")
        lines.append("UI ARCHITECTURE & COMPONENT BREAKDOWN")
        for comp in ds.get("components", []):
            lines.append(f"- {comp}")
        lines.append("\n---")
        lines.append("SURFACE TOKENS, LIGHTING & ATMOSPHERE")
        vs = ds.get("visual_styling", {})
        lines.append(f"- Surface Elevations: {vs.get('surfaces')}")
        lines.append(f"- Lighting Spotlight: {vs.get('lighting')}")
        lines.append(f"- Color Palette:     {vs.get('accents')}")
        lines.append(f"- Typography:        {vs.get('typography')}\n")
        lines.append("---")
        lines.append("FONTS & GOOGLE FONTS IMPORT")
        lines.append("- Display/Heading Font: 'Space Grotesk' or 'Syne' (weights: 700, 800)")
        lines.append("- Body/Interface Font: 'Inter' or 'Geist Sans' (weights: 400, 500, 600)")
        lines.append("- Import Link:\n  <link href=\"https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;700&family=Syne:wght@700;800&display=swap\" rel=\"stylesheet\">\n")
        lines.append("---")
        lines.append("CLEAN TRANSITION SPEC (QUIET SUPPORTING DETAILS)")
        ts = ds.get("transition_spec", {})
        lines.append(f"- Duration: {ts.get('duration_ms', 240)}ms")
        lines.append(f"- Easing:   {ts.get('curve', 'cubic-bezier(0.16, 1, 0.3, 1)')}")
        lines.append(f"- Notes:    {ts.get('notes', 'Natural dampening with zero float')}\n")
        lines.append("---")
        lines.append("PRODUCTION CODE IMPLEMENTATION SCAFFOLD")
        scaffold = item.get("code_scaffold") or ds.get("code_scaffold")
        if scaffold:
            lines.append(scaffold)
        lines.append("\n---")
        lines.append(f"DIRECT MP4 VIDEO ASSET: {video_url}")

    else:
        lines.append("Catalog description")
        lines.append(item.get("description", ""))
        lines.append("This catalog record has no source blueprint. Inspect its source or video for further visual detail.")

    lines.append("######################################################################\n")
    return "\n".join(lines)

def search(query="", limit=None, filter_3d=False, filter_liquid_glass=False, category_filter=None, *, source_filter=None, diagnostics=None, records=None, include_specs=True):
    """
    Search curated showcases with UI Design System Archetypes,
    Embedding & TF-IDF similarity, and component-first blueprints.
    """
    items = load_data() if records is None else records
    n_total = len(items)
    indexed = [(i, item) for i, item in enumerate(items)
               if source_filter is None or get_source_info(item)[0] == source_filter]

    # Pre-filter by Category if specified
    if category_filter:
        indexed = [(i, it) for i, it in indexed if matches_category(it, category_filter)]

    # Pre-filter by Liquid Glass if requested
    if filter_liquid_glass:
        indexed = [(i, it) for i, it in indexed if is_liquid_glass_showcase(it)]

    # Pre-filter by 3D if requested
    if filter_3d:
        indexed = [(i, it) for i, it in indexed if is_3d_showcase(it)]

    items = [it for _, it in indexed]
    if diagnostics is not None:
        diagnostics["catalog_available"] = n_total > 0

    # Empty or broad query handling: return the 6 Universal UI Design System Archetypes
    if is_broad_or_creative_query(query):
        # If user explicitly requested liquid-glass, 3d, or a category, return top matching items from pool
        if filter_liquid_glass or filter_3d or category_filter or source_filter:
            results = []
            eff_limit = limit if limit is not None else 5
            for it in items[:eff_limit]:
                result = {**it, "relevance_score": 1.0}
                if include_specs:
                    result["design_system"] = derive_ui_design_spec(it)
                    result["design_system_origin"] = "category_heuristic"
                results.append(result)
            return results

        eff_limit = limit if limit is not None else len(UI_DESIGN_ARCHETYPES)
        return [dict(a) for a in UI_DESIGN_ARCHETYPES[:eff_limit]]

    if not items:
        return []

    eff_limit = limit if limit is not None else 5

    # Build corpus for hybrid TF-IDF + token similarity
    corpus = [
        f"{it.get('title', '')} {it.get('title', '')} {get_item_category(it)} {it.get('description', '')} {it.get('id', '').replace('-', ' ')}"
        for it in items
    ]

    try:
        vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
        tfidf_matrix = vectorizer.fit_transform(corpus)
        query_vec = vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()
    except Exception:
        similarities = np.zeros(len(items))

    q_words = [w.lower() for w in query.split() if len(w) > 2]
    is_3d_query = any(k in query.lower() for k in THREED_KEYWORDS)
    is_liquid_query = any(k in query.lower() for k in LIQUID_GLASS_KEYWORDS)

    # Optional semantic similarity from the fine-tuned vector index
    enc, emb = _load_semantic()
    sem = None
    if enc is not None and emb is not None and emb.shape[0] == n_total and items:
        qv = enc.encode([query])[0]
        sem = emb[[i for i, _ in indexed]] @ qv

    if diagnostics is not None:
        diagnostics["backend"] = "hybrid" if sem is not None else "lexical"

    lex_scores = []
    for idx, it in enumerate(items):
        sim = float(similarities[idx]) if idx < len(similarities) else 0.0
        title_lower = it.get('title', '').lower()
        desc_lower = it.get('description', '').lower()
        cat_lower = get_item_category(it).lower()

        exact_boost = sum(0.35 for w in q_words if w in title_lower)
        exact_boost += sum(0.20 for w in q_words if w in cat_lower)
        exact_boost += sum(0.15 for w in q_words if w in desc_lower)

        if filter_3d or is_3d_query:
            if any(k in title_lower for k in ["3d", "webgl", "particle", "liquid", "kinetic", "canvas"]):
                exact_boost += 0.35
            elif any(k in desc_lower for k in ["3d", "webgl", "particle", "liquid", "kinetic", "canvas"]):
                exact_boost += 0.15

        if filter_liquid_glass or is_liquid_query:
            if any(k in title_lower for k in ["liquid", "glass", "refraction", "chromatic", "frosted"]):
                exact_boost += 0.40
            elif any(k in desc_lower for k in ["liquid", "glass", "refraction", "chromatic", "frosted"]):
                exact_boost += 0.20

        lex_scores.append(sim + exact_boost)

    lex_scores = np.asarray(lex_scores)
    if sem is not None:
        final_scores = (1.0 - SEMANTIC_WEIGHT) * _minmax(lex_scores) + SEMANTIC_WEIGHT * _minmax(sem)
    else:
        final_scores = lex_scores

    scored = []
    for idx, it in enumerate(items):
        total_score = float(final_scores[idx])
        if total_score > 0.05 or not q_words:
            scored.append((total_score, it))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = []
    for score, item in scored[:eff_limit]:
        result = {**item, "relevance_score": round(float(score), 4)}
        if include_specs:
            result["design_system"] = derive_ui_design_spec(item)
            result["design_system_origin"] = "category_heuristic"
        results.append(result)
    return results

def search_components(query="", limit=None, filter_3d=False, filter_liquid_glass=False, category_filter=None, *, source_filter=None, diagnostics=None, records=None):
    """Search the separate UI-component pool (21st.dev + skiper.ui) with the same
    hybrid lexical+semantic ranking used for designs. Components carry
    source snapshots or registry instructions rather than interaction video."""
    items = load_components() if records is None else records
    n_total = len(items)
    indexed = [(i, item) for i, item in enumerate(items)
               if source_filter is None or get_source_info(item)[0] == source_filter]

    if category_filter:
        indexed = [(i, it) for i, it in indexed if matches_category(it, category_filter)]
    if filter_liquid_glass:
        indexed = [(i, it) for i, it in indexed if is_liquid_glass_showcase(it)]
    if filter_3d:
        indexed = [(i, it) for i, it in indexed if is_3d_showcase(it)]

    items = [it for _, it in indexed]
    if diagnostics is not None:
        diagnostics["catalog_available"] = n_total > 0
    eff_limit = limit if limit is not None else 5

    # Components have no archetype defaults; a subject-free query returns the first
    # matching components from the (optionally filtered) pool.
    if is_broad_or_creative_query(query):
        return [{**it, "relevance_score": 1.0} for it in items[:eff_limit]]

    if not items:
        return []

    corpus = [
        f"{it.get('title', '')} {it.get('title', '')} {get_item_category(it)} {it.get('description', '')} {it.get('id', '').replace('-', ' ')} {' '.join(it.get('tags', []))}"
        for it in items
    ]

    try:
        vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
        tfidf_matrix = vectorizer.fit_transform(corpus)
        query_vec = vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()
    except Exception:
        similarities = np.zeros(len(items))

    q_words = [w.lower() for w in query.split() if len(w) > 2]
    is_3d_query = any(k in query.lower() for k in THREED_KEYWORDS)
    is_liquid_query = any(k in query.lower() for k in LIQUID_GLASS_KEYWORDS)

    enc, emb = _load_semantic_components()
    sem = None
    if enc is not None and emb is not None and emb.shape[0] == n_total and items:
        qv = enc.encode([query])[0]
        sem = emb[[i for i, _ in indexed]] @ qv

    if diagnostics is not None:
        diagnostics["backend"] = "hybrid" if sem is not None else "lexical"

    lex_scores = []
    for idx, it in enumerate(items):
        sim = float(similarities[idx]) if idx < len(similarities) else 0.0
        title_lower = it.get('title', '').lower()
        desc_lower = it.get('description', '').lower()
        cat_lower = get_item_category(it).lower()
        tags_lower = ' '.join(it.get('tags', [])).lower()

        exact_boost = sum(0.35 for w in q_words if w in title_lower)
        exact_boost += sum(0.20 for w in q_words if w in cat_lower)
        exact_boost += sum(0.15 for w in q_words if w in desc_lower)
        exact_boost += sum(0.10 for w in q_words if w in tags_lower)

        if filter_3d or is_3d_query:
            if any(k in title_lower for k in ["3d", "webgl", "particle", "liquid", "kinetic", "canvas"]):
                exact_boost += 0.35
            elif any(k in desc_lower for k in ["3d", "webgl", "particle", "liquid", "kinetic", "canvas"]):
                exact_boost += 0.15

        if filter_liquid_glass or is_liquid_query:
            if any(k in title_lower for k in ["liquid", "glass", "refraction", "chromatic", "frosted"]):
                exact_boost += 0.40
            elif any(k in desc_lower for k in ["liquid", "glass", "refraction", "chromatic", "frosted"]):
                exact_boost += 0.20

        lex_scores.append(sim + exact_boost)

    lex_scores = np.asarray(lex_scores)
    if sem is not None:
        final_scores = (1.0 - SEMANTIC_WEIGHT) * _minmax(lex_scores) + SEMANTIC_WEIGHT * _minmax(sem)
    else:
        final_scores = lex_scores

    scored = []
    for idx, it in enumerate(items):
        total_score = float(final_scores[idx])
        if total_score > 0.05 or not q_words:
            scored.append((total_score, {**it, "relevance_score": round(float(total_score), 4)}))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [it for _, it in scored[:eff_limit]]

def format_component_blueprint(item, index=1):
    """Format a component's verbatim prompt / code implementation and install metadata."""
    category = get_item_category(item)
    source_site, source_url = get_source_info(item)
    title = item.get("title", "Component")

    lines = []
    lines.append("######################################################################")
    lines.append(f"[{index}] {title}")
    lines.append(f"Category: {category}  |  Source: {source_site}  |  Type: component")
    lines.append(f"URL: {source_url}")
    if item.get("author"):
        lines.append(f"Author: {item['author']}")
    if item.get("license"):
        lines.append(f"License: {item['license']}")
    if item.get("npm_deps"):
        lines.append(f"Install deps: {item['npm_deps']}")
    if item.get("tags"):
        lines.append(f"Tags: {', '.join(item['tags'])}")
    lines.append(f"Overview: {item.get('description', '')}")
    lines.append("----------------------------------------------------------------------")
    full_prompt = item.get("full_prompt")
    if full_prompt:
        lines.append("VERBATIM PROMPT / CODE:")
        lines.append(full_prompt)
    lines.append("######################################################################\n")
    return "\n".join(lines)

REFERENCE_SOURCES = {
    "designs": ("motionsites.ai", "pixlpin.com"),
    "components": ("skiper-ui.com", "21st.dev"),
}

SOURCE_MATERIAL = {
    "motionsites.ai": "design_prompt",
    "pixlpin.com": "description",
    "skiper-ui.com": "component_source_snapshot",
    "21st.dev": "registry_instructions",
}


def pack_reference(item):
    source, url = get_source_info(item)
    body = (item.get("full_prompt") or "").strip()
    material = {
        "kind": SOURCE_MATERIAL.get(source, "catalog_text") if body else "description",
        "characters": len(body),
        "excerpt_truncated": len(body) > 550,
    }
    for key in ("author", "license", "npm_deps"):
        if item.get(key):
            material[key] = item[key]
    return {
        "id": item.get("id"), "title": item["title"], "source": source,
        "url": url or None, "video_url": item.get("video_url") or None,
        "description": (item.get("description") or "")[:750],
        "blueprint_excerpt": body[:550] or None,
        "material": material,
    }


def exact_references(query, rows):
    """Try a canonical ID or source URL before matching titles."""
    key = query.strip()
    if not key:
        return []
    identified = [row for row in rows
                  if row.get("id") == key or get_source_info(row)[1].rstrip("/") == key.rstrip("/")]
    if identified:
        return identified
    title = " ".join(key.casefold().split())
    return [row for row in rows if " ".join(row["title"].casefold().split()) == title]


def reference_evidence(query, pool, *, limit=3, filter_3d=False,
                       filter_liquid_glass=False, category_filter=None, source_filter=None):
    """Return catalog evidence. Preserve the existing hybrid ranking for briefs."""
    if source_filter and source_filter not in REFERENCE_SOURCES[pool]:
        return {"status": "invalid_source", "backend": None, "references": [],
                "reason": f"Choose a {pool} source: {', '.join(REFERENCE_SOURCES[pool])}."}
    constrained = filter_3d or filter_liquid_glass or category_filter or source_filter
    broad = is_broad_or_creative_query(query)
    records = load_components() if pool == "components" else load_data()
    if not records:
        return {"status": "unavailable", "backend": None, "references": [],
                "reason": f"The {pool} catalog could not be loaded."}
    candidates = (row for row in records
                  if (not source_filter or get_source_info(row)[0] == source_filter)
                  and (not category_filter or matches_category(row, category_filter))
                  and (not filter_3d or is_3d_showcase(row))
                  and (not filter_liquid_glass or is_liquid_glass_showcase(row)))
    # Materialize once so both ID and title checks see the same candidates.
    exact = exact_references(query, list(candidates))
    if len(exact) == 1:
        return {"status": "ok" if limit else "no_matches", "backend": "catalog_exact",
                "exact_matches": len(exact), "references": [pack_reference(row) for row in exact[:limit]]}

    if not exact and query.strip().startswith(("https://", "http://")):
        return {"status": "no_matches", "backend": "catalog_exact", "exact_matches": 0, "references": []}
    if broad and not constrained and not exact:
        return {"status": "needs_specific_query", "backend": None, "references": []}

    details = {"backend": "catalog_filter" if broad else None}
    # Preserve the existing ranking when multiple records share an exact title.
    rank_limit = len(records) if exact else limit
    options = dict(limit=rank_limit, filter_3d=filter_3d, filter_liquid_glass=filter_liquid_glass,
                   category_filter=category_filter, source_filter=source_filter, diagnostics=details, records=records)
    if pool == "components":
        matches = search_components(query, **options)
    else:
        matches = search(query, include_specs=False, **options)
    if exact:
        rank = {row["id"]: i for i, row in enumerate(matches)}
        exact.sort(key=lambda row: rank.get(row["id"], len(rank)))
        return {"status": "ok" if limit else "no_matches", "backend": "catalog_exact",
                "exact_matches": len(exact), "references": [pack_reference(row) for row in exact[:limit]]}
    return {"status": "ok" if matches else "no_matches", "backend": details["backend"],
            "references": [pack_reference(row) for row in matches]}


def main():
    # Windows consoles default to cp1252, which cannot encode characters such as
    # U+2212 (minus) present in some showcase descriptions. Force UTF-8 so --json
    # and blueprint output never crash on non-ASCII content.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except (ValueError, OSError):
                pass
    parser = argparse.ArgumentParser(
        description="Search UI design and component references"
    )
    parser.add_argument(
        "query",
        nargs="*",
        help="Creative prompt or query terms (e.g. 'SaaS dashboard', 'fintech telemetry', 'editorial ecommerce', 'developer tools')"
    )
    parser.add_argument(
        "--components",
        action="store_true",
        help="Print built-in token presets. Use --pool components to search provider records."
    )
    parser.add_argument(
        "--pool",
        choices=["designs", "components"],
        default="designs",
        help="Which retrievable pool to search: 'designs' (950 full-design showcases, default) or 'components' (9735 UI component code prompts from 21st.dev + skiper.ui)"
    )
    parser.add_argument(
        "--3d",
        dest="three_d",
        action="store_true",
        help="Filter exclusively for 3D, Three.js, WebGL, particle field, and spatial designs"
    )
    parser.add_argument(
        "--liquid-glass",
        dest="liquid_glass",
        action="store_true",
        help="Filter specifically for liquid glass, glassmorphism, chromatic aberration, and refractive shader designs"
    )
    parser.add_argument(
        "--category",
        type=str,
        default=None,
        help="Filter by category (e.g. SaaS, Fintech, Fashion, Portfolio, Developer Tools, AI & Machine Learning)"
    )
    parser.add_argument(
        "--list-categories",
        action="store_true",
        help="Print all available categories with their item counts and exit"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Print the stored reference text where available."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Max results to return (default: 6 for archetypes, 5 for search)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON for programmatic agent consumption"
    )
    parser.add_argument("--evidence", action="store_true",
                        help="Return a compact JSON packet of source descriptions and media for the design agent")
    parser.add_argument("--source", choices=sorted(SOURCE_MATERIAL), help="Filter evidence by provider")
    parser.add_argument("--record", metavar="ID", help="Print one original catalog record as JSON")
    args = parser.parse_args()
    if args.evidence:
        if args.limit is not None and args.limit < 0:
            parser.error("--limit must be nonnegative")
        result = reference_evidence(" ".join(args.query), args.pool,
                                    limit=3 if args.limit is None else args.limit,
                                    filter_3d=args.three_d, filter_liquid_glass=args.liquid_glass,
                                    category_filter=args.category, source_filter=args.source)
        print(json.dumps(result, ensure_ascii=False))
        return

    # Resolve a selected reference by its stable ID without a second ranking pass.
    if args.record:
        if args.source:
            parser.error('--source requires --evidence')
        records = load_components() if args.pool == "components" else load_data()
        record = next((r for r in records if r.get("id") == args.record), None)
        if record is None:
            parser.error(f"unknown {args.pool} record {args.record!r}")
        print(json.dumps(record, ensure_ascii=False, indent=2))
        return

    if args.source:
        parser.error("--source requires --evidence")

    # Handle --components early
    if args.components:
        print_component_tokens(as_json=args.json)
        return

    # Handle --list-categories early
    if args.list_categories:
        items = load_components() if args.pool == "components" else load_data()
        list_categories(items)
        return

    query_str = " ".join(args.query) if args.query else ""
    if args.pool == "components":
        results = search_components(
            query=query_str,
            limit=args.limit,
            filter_3d=args.three_d,
            filter_liquid_glass=args.liquid_glass,
            category_filter=args.category
        )
    else:
        results = search(
            query=query_str,
            limit=args.limit,
            filter_3d=args.three_d,
            filter_liquid_glass=args.liquid_glass,
            category_filter=args.category
        )

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    filter_tags = []
    if args.pool == "components":
        filter_tags.append("--pool components")
    if args.three_d:
        filter_tags.append("--3d")
    if args.liquid_glass:
        filter_tags.append("--liquid-glass")
    if args.category:
        filter_tags.append(f"--category '{args.category}'")
    tag_str = f" [{' '.join(filter_tags)}]" if filter_tags else ""

    if args.pool == "components":
        if args.full:
            print(f"\n=======================================================")
            print(f" UI Component Library (21st.dev + skiper.ui): '{query_str}'{tag_str} [FULL PROMPT]")
            print(f" Showing {len(results)} Verbatim Component Prompts & Implementations")
            print(f"=======================================================\n")
            for i, r in enumerate(results, 1):
                print(format_component_blueprint(r, index=i))
            return

        print(f"\n=======================================================")
        print(f" UI Component Library (21st.dev + skiper.ui): '{query_str}'{tag_str}")
        print(f" Matched {len(results)} Components (Code Prompts & Install Commands)")
        print(f"=======================================================\n")
        for i, r in enumerate(results, 1):
            category = get_item_category(r)
            source_site, source_url = get_source_info(r)
            print(f"[{i}] {r.get('title')}")
            print(f"    - Category:        {category}")
            print(f"    - Source:          {source_site} ({source_url})")
            print(f"    - Relevance Score: {r.get('relevance_score', 'N/A')}")
            print(f"    - Overview:        {r.get('description')}")
            if r.get('tags'):
                print(f"    - Tags:            {', '.join(r['tags'])}")
            if r.get('npm_deps'):
                print(f"    - Install deps:    {r['npm_deps']}")
            if r.get('full_prompt'):
                print(f"    - Prompt/Code:     Pass --full to view the verbatim prompt and implementation\n")
            else:
                print()
        return

    if args.full:
        print(f"\n=======================================================")
        print(f" UI Design System & Component Library: '{query_str}'{tag_str} [FULL BLUEPRINT]")
        print(f" Showing {len(results)} Complete Implementation Blueprints")
        print(f"=======================================================\n")
        for i, r in enumerate(results, 1):
            print(format_full_blueprint(r, index=i))
        return

    print(f"\n=======================================================")
    print(f" UI Design System & Component Library Engine: '{query_str}'{tag_str}")
    print(f" Matched {len(results)} Curated Showcases (Component Blueprints & Video Grounded)")
    print(f"=======================================================\n")

    for i, r in enumerate(results, 1):
        arch = r.get("archetype")
        arch_label = f" [Archetype: {arch}]" if arch else ""
        category = get_item_category(r)
        source_site, source_url = get_source_info(r)
        video_url = r.get("video_url", "N/A")
        ds = r.get("design_system") or derive_ui_design_spec(r)

        print(f"[{i}]{arch_label} {r.get('title')}")
        print(f"    - Category:             {category}")
        print(f"    - Source:               {source_site} ({source_url})")
        print(f"    - Direct Video Asset:   {video_url}")
        print(f"    - Relevance Score:      {r.get('relevance_score', 'N/A')}")
        print(f"    - Overview:             {r.get('description')}")
        if not r.get("archetype"):
            if r.get("full_prompt"):
                print("    - Source blueprint:     available with --record " + str(r.get("id")))
            else:
                print("    - Source blueprint:     unavailable; inspect the linked source or video")
            print()
            continue
        print("    - Built-in archetype / authored component suggestions:")
        for comp in ds.get("components", []):
            print(f"      * {comp}")
        print(f"    - Visual Styling & Lighting:")
        vs = ds.get("visual_styling", {})
        print(f"      * Surfaces:           {vs.get('surfaces', 'Canvas #0B0F19, Cards #111827, Border border-white/10')}")
        print(f"      * Lighting:           {vs.get('lighting', 'Radial ambient glow, specular rim light')}")
        print(f"      * Colors / Accents:   {vs.get('accents', 'Indigo #6366F1, Violet #8B5CF6')}")
        print(f"      * Typography:         {vs.get('typography', 'Display Space Grotesk, Body Inter')}")
        ts = ds.get("transition_spec", {})
        print(f"    - Transition Spec:      {ts.get('duration_ms', 240)}ms {ts.get('curve', 'cubic-bezier(0.16, 1, 0.3, 1)')} (Quiet supporting detail)")
        if r.get('code_scaffold') or ds.get('code_scaffold'):
            print(f"    - Code Blueprint:       Pass --full to view complete React + Tailwind component implementation\n")
        else:
            print(f"    - Blueprint:            Pass --full to view entire verbatim prompt blueprint\n")

if __name__ == "__main__":
    main()
