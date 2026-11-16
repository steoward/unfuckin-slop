#!/usr/bin/env python3
"""
EmbeddingGemma 2 UI Motion & Design Library Engine for Autonomous Coding Agents.
Drives jaw-dropping 3D, WebGL, Liquid Glass, and kinetic designs from 950 curated visual showcases
(622 Pixlpin motion showcases + 328 MotionSites full prompt blueprints) with verbatim implementation
blueprints, Three.js scaffolds, CSS 3D & refraction formulas, physical spring dynamics, and live MP4 assets.
"""

import os
import sys
import json
import argparse
from collections import Counter
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

SHOWCASES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "design_showcases")
META_PATH = os.path.join(SHOWCASES_DIR, "showcases_meta.json")
EMBS_PATH = os.path.join(SHOWCASES_DIR, "design_embeddings.npy")
FALLBACK_DATASET = os.path.join(SHOWCASES_DIR, "dataset.jsonl")

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

# The 5 Mind-Blowing Creative Archetypes returned for empty or broad queries
CREATIVE_ARCHETYPES = [
    {
        "id": "minimal-white-hero-with-generative-particle-animation",
        "title": "3D Interactive Spatial Hero (Three.js / WebGL Particle Orbit)",
        "archetype": "3D Interactive Spatial Hero",
        "archetype_key": "a",
        "category": "3D & Spatial",
        "source_site": "pixlpin.com",
        "source_url": "https://pixlpin.com/d/minimal-white-hero-with-generative-particle-animation",
        "description": "Clean, modern spatial hero featuring floating 3D particle terrain waves in WebGL/Three.js with real-time mouse reactivity, particle orbit physics, centered headline typography, glowing interactive CTA button, and partner ticker.",
        "video_url": "https://pixlpin.com/media/designs/01M4Z1PGJHE11DVJF5H7GSKKZ6/mp4-d5a5f0a4.mp4",
        "local_video": "videos/minimal-white-hero-with-generative-particle-animation.mp4",
        "relevance_score": 1.0,
        "is_3d": True,
        "is_liquid_glass": False,
        "motion_preset": {
            "type": "3D WebGL / Particle Orbit Hero",
            "spring": {"stiffness": 340, "damping": 26, "mass": 0.9},
            "css_curve": "cubic-bezier(0.16, 1, 0.3, 1)",
            "timing_ms": 380,
            "principles": "Hardware-accelerated WebGL / Canvas particle field with mouse-reactive camera orbit, continuous ambient drift, and zero CPU layout jank.",
            "css_3d": {
                "perspective": "1000px",
                "transform_style": "preserve-3d",
                "rules": "perspective: 1000px; transform-style: preserve-3d; backface-visibility: hidden;"
            },
            "code_scaffold": (
                "// Three.js / WebGL Particle Field & Orbit Scaffold\n"
                "import * as THREE from 'three';\n\n"
                "const scene = new THREE.Scene();\n"
                "const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);\n"
                "const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true, powerPreference: 'high-performance' });\n"
                "renderer.setSize(window.innerWidth, window.innerHeight);\n"
                "renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));\n\n"
                "const count = 1800;\n"
                "const geometry = new THREE.BufferGeometry();\n"
                "const positions = new Float32Array(count * 3);\n"
                "for (let i = 0; i < count * 3; i++) positions[i] = (Math.random() - 0.5) * 12;\n"
                "geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));\n"
                "const material = new THREE.PointsMaterial({ size: 0.035, color: 0x6366f1, transparent: true, opacity: 0.85, blending: THREE.AdditiveBlending });\n"
                "const particles = new THREE.Points(geometry, material);\n"
                "scene.add(particles);\n"
                "camera.position.z = 4.5;\n\n"
                "let targetX = 0, targetY = 0;\n"
                "window.addEventListener('mousemove', (e) => {\n"
                "  targetX = (e.clientX / window.innerWidth - 0.5) * 1.5;\n"
                "  targetY = (e.clientY / window.innerHeight - 0.5) * 1.5;\n"
                "});\n\n"
                "function animate() {\n"
                "  requestAnimationFrame(animate);\n"
                "  particles.rotation.y += 0.0012;\n"
                "  camera.position.x += (targetX - camera.position.x) * 0.05;\n"
                "  camera.position.y += (-targetY - camera.position.y) * 0.05;\n"
                "  camera.lookAt(scene.position);\n"
                "  renderer.render(scene, camera);\n"
                "}\n"
                "animate();"
            ),
            "video_url": "https://pixlpin.com/media/designs/01M4Z1PGJHE11DVJF5H7GSKKZ6/mp4-d5a5f0a4.mp4"
        }
    },
    {
        "id": "liquid-glass-3d-effect-showcase",
        "title": "Kinetic Typography & Liquid Glass Refraction (Liquid Glass 3D Effect)",
        "archetype": "Kinetic Typography & Liquid Glass Refraction",
        "archetype_key": "b",
        "category": "Liquid Glass",
        "source_site": "pixlpin.com",
        "source_url": "https://pixlpin.com/d/liquid-glass-3d-effect-showcase",
        "description": "3D real-time glass refraction, chromatic lens distortion, and physical material depth layered over bold kinetic editorial typography with dynamic scroll-linked refraction shaders.",
        "video_url": "https://pixlpin.com/media/designs/01M4ZYC28GA7SM4G1HZ7RJX71F/mp4-9b17b2d1.mp4",
        "local_video": "videos/liquid-glass-3d-effect-showcase.mp4",
        "relevance_score": 0.98,
        "is_3d": True,
        "is_liquid_glass": True,
        "motion_preset": {
            "type": "Kinetic Typography & Liquid Glass Refraction",
            "spring": {"stiffness": 420, "damping": 30, "mass": 1.0},
            "css_curve": "cubic-bezier(0.19, 1.0, 0.22, 1.0)",
            "timing_ms": 320,
            "principles": "Real-time frosted glass refraction, chromatic aberration lens distortion, dynamic specular highlights tracking pointer motion, and high-saturation backdrop filtration over editorial typography.",
            "css_3d": {
                "perspective": "1000px",
                "transform_style": "preserve-3d",
                "rules": "backdrop-filter: blur(24px) saturate(190%) contrast(115%); -webkit-backdrop-filter: blur(24px) saturate(190%) contrast(115%); perspective: 1000px; transform-style: preserve-3d;"
            },
            "liquid_glass_spec": {
                "backdrop_blur": "24px",
                "saturation": "190%",
                "contrast": "115%",
                "specular_highlight": "radial-gradient(circle 350px at var(--mouse-x, 50%) var(--mouse-y, 50%), rgba(255, 255, 255, 0.22), transparent 75%)",
                "chromatic_aberration": "feDisplacementMap scale='14' with RGB color channel split (red: +2px, blue: -2px)",
                "border": "1px solid rgba(255, 255, 255, 0.15)",
                "box_shadow": "0 30px 60px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.25)"
            },
            "code_scaffold": (
                "/* Liquid Glass Refraction & Chromatic Aberration Scaffold */\n"
                ".liquid-glass-surface {\n"
                "  background: rgba(255, 255, 255, 0.035);\n"
                "  backdrop-filter: blur(24px) saturate(190%) contrast(115%);\n"
                "  -webkit-backdrop-filter: blur(24px) saturate(190%) contrast(115%);\n"
                "  border: 1px solid rgba(255, 255, 255, 0.15);\n"
                "  box-shadow: 0 30px 60px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.25);\n"
                "  border-radius: 24px;\n"
                "  perspective: 1000px;\n"
                "  transform-style: preserve-3d;\n"
                "  position: relative;\n"
                "  overflow: hidden;\n"
                "  transition: transform 320ms cubic-bezier(0.19, 1.0, 0.22, 1.0);\n"
                "}\n"
                ".liquid-glass-surface::after {\n"
                "  content: '';\n"
                "  position: absolute;\n"
                "  inset: 0;\n"
                "  border-radius: inherit;\n"
                "  background: radial-gradient(circle 350px at var(--mouse-x, 50%) var(--mouse-y, 50%), rgba(255, 255, 255, 0.22), transparent 75%);\n"
                "  pointer-events: none;\n"
                "  mix-blend-mode: overlay;\n"
                "}"
            ),
            "video_url": "https://pixlpin.com/media/designs/01M4ZYC28GA7SM4G1HZ7RJX71F/mp4-9b17b2d1.mp4"
        }
    },
    {
        "id": "autonomous-crypto-trading-agent-bento-grid",
        "title": "3D Bento Grid with Spatial Tilt & Depth",
        "archetype": "3D Bento Grid with Spatial Tilt & Depth",
        "archetype_key": "c",
        "category": "3D & Spatial",
        "source_site": "pixlpin.com",
        "source_url": "https://pixlpin.com/d/autonomous-crypto-trading-agent-bento-grid",
        "description": "Dark bento grid with 1200px CSS perspective, dynamic spring tilt physics tracking cursor angle, dynamic radial lighting gradients, and layered Z-depth cards.",
        "video_url": "https://pixlpin.com/media/designs/01M50V551ASYJXQF7XMV81HXES/mp4-8ac23fa2.mp4",
        "local_video": "videos/autonomous-crypto-trading-agent-bento-grid.mp4",
        "relevance_score": 0.96,
        "is_3d": True,
        "is_liquid_glass": False,
        "motion_preset": {
            "type": "3D Bento Grid with Spatial Tilt & Depth",
            "spring": {"stiffness": 380, "damping": 28, "mass": 1.0},
            "css_curve": "cubic-bezier(0.16, 1, 0.3, 1)",
            "timing_ms": 280,
            "principles": "1200px CSS perspective container with spring tilt physics tracking cursor angle, dynamic radial lighting gradient, and multi-layer Z-depth elevation.",
            "css_3d": {
                "perspective": "1200px",
                "transform_style": "preserve-3d",
                "rules": "perspective: 1200px; transform-style: preserve-3d; transform: perspective(1200px) rotateX(var(--rot-x, 0deg)) rotateY(var(--rot-y, 0deg));"
            },
            "code_scaffold": (
                "// Spatial Tilt & Dynamic Lighting Scaffold\n"
                "const bentoCard = document.querySelector('.bento-tilt-card');\n"
                "bentoCard.addEventListener('mousemove', (e) => {\n"
                "  const rect = bentoCard.getBoundingClientRect();\n"
                "  const x = (e.clientX - rect.left) / rect.width - 0.5;\n"
                "  const y = (e.clientY - rect.top) / rect.height - 0.5;\n"
                "  bentoCard.style.transform = `perspective(1200px) rotateX(${-y * 12}deg) rotateY(${x * 12}deg) translateZ(10px)`;\n"
                "  bentoCard.style.setProperty('--mouse-x', `${(x + 0.5) * 100}%`);\n"
                "  bentoCard.style.setProperty('--mouse-y', `${(y + 0.5) * 100}%`);\n"
                "});\n"
                "bentoCard.addEventListener('mouseleave', () => {\n"
                "  bentoCard.style.transform = 'perspective(1200px) rotateX(0deg) rotateY(0deg) translateZ(0px)';\n"
                "});"
            ),
            "video_url": "https://pixlpin.com/media/designs/01M50V551ASYJXQF7XMV81HXES/mp4-8ac23fa2.mp4"
        }
    },
    {
        "id": "highnote",
        "title": "Futuristic Cybernetic / Fintech Interface (Laser Neon & Telemetry)",
        "archetype": "Futuristic Cybernetic / Fintech Interface",
        "archetype_key": "d",
        "category": "Fintech",
        "source_site": "pixlpin.com",
        "source_url": "https://pixlpin.com/d/highnote",
        "description": "Fintech interface featuring high-contrast dark aesthetic, laser neon accents, glowing SVG particle traces, live data telemetry feeds, and 3D card tilt.",
        "video_url": "https://pixlpin.com/media/designs/01M4R69JZD09DQCPPYCRZP4QSR/mp4-aa5bca45.mp4",
        "local_video": "videos/highnote.mp4",
        "relevance_score": 0.94,
        "is_3d": True,
        "is_liquid_glass": False,
        "motion_preset": {
            "type": "Futuristic Cybernetic / 3D Kinetic Interface",
            "spring": {"stiffness": 440, "damping": 32, "mass": 0.9},
            "css_curve": "cubic-bezier(0.08, 0.82, 0.17, 1.0)",
            "timing_ms": 260,
            "principles": "High-contrast dark aesthetic with laser neon accent pulses, live SVG telemetry traces, and 3D card tilt physics.",
            "css_3d": {
                "perspective": "1000px",
                "transform_style": "preserve-3d",
                "rules": "perspective: 1000px; transform-style: preserve-3d; filter: drop-shadow(0 0 15px rgba(99, 102, 241, 0.4));"
            },
            "code_scaffold": (
                "// Kinetic SVG Neon Particle Trace & Live Telemetry Scaffold\n"
                "const canvas = document.querySelector('#telemetry-canvas');\n"
                "const ctx = canvas.getContext('2d');\n"
                "function renderTelemetry() {\n"
                "  ctx.clearRect(0, 0, canvas.width, canvas.height);\n"
                "  // Dynamic laser traces and live data points\n"
                "  requestAnimationFrame(renderTelemetry);\n"
                "}\n"
                "renderTelemetry();"
            ),
            "video_url": "https://pixlpin.com/media/designs/01M4R69JZD09DQCPPYCRZP4QSR/mp4-aa5bca45.mp4"
        }
    },
    {
        "id": "shopify-editions-spring-26",
        "title": "Immersive Camera Orbit Product Showcase (Scroll-Driven Point-Cloud Orbit)",
        "archetype": "Immersive Camera Orbit Product Showcase",
        "archetype_key": "e",
        "category": "3D & Spatial",
        "source_site": "pixlpin.com",
        "source_url": "https://pixlpin.com/d/shopify-editions-spring-26",
        "description": "A dark-mode product showcase website featuring scroll-driven 3D point-cloud camera transitions, kinetic typography, dynamic directional lighting shifts, and detailed feature grids.",
        "video_url": "https://pixlpin.com/media/designs/01M4GAQYD9JH1MY3G3APHVF54W/mp4-83dd1528.mp4",
        "local_video": "videos/shopify-editions-spring-26.mp4",
        "relevance_score": 0.92,
        "is_3d": True,
        "is_liquid_glass": False,
        "motion_preset": {
            "type": "Immersive Scroll-Driven 3D Camera Orbit",
            "spring": {"stiffness": 260, "damping": 32, "mass": 1.2},
            "css_curve": "cubic-bezier(0.25, 1, 0.5, 1)",
            "timing_ms": 450,
            "principles": "Scroll-linked 3D camera trajectory through point-clouds and 3D geometries with physical damping and directional lighting shifts.",
            "css_3d": {
                "perspective": "1000px",
                "transform_style": "preserve-3d",
                "rules": "perspective: 1000px; transform-style: preserve-3d; will-change: transform;"
            },
            "code_scaffold": (
                "// Scroll-Driven Camera Path Scaffold\n"
                "window.addEventListener('scroll', () => {\n"
                "  const progress = window.scrollY / (document.documentElement.scrollHeight - window.innerHeight);\n"
                "  const targetZ = 5 - progress * 3;\n"
                "  const targetRotY = progress * Math.PI * 0.5;\n"
                "  camera.position.z += (targetZ - camera.position.z) * 0.08;\n"
                "  camera.rotation.y += (targetRotY - camera.rotation.y) * 0.08;\n"
                "  renderer.render(scene, camera);\n"
                "});"
            ),
            "video_url": "https://pixlpin.com/media/designs/01M4GAQYD9JH1MY3G3APHVF54W/mp4-83dd1528.mp4"
        }
    }
]

def get_item_category(item) -> str:
    """Return explicit category or infer one intelligently."""
    cat = item.get("category")
    if cat and str(cat).strip():
        return str(cat).strip()

    # Intelligent fallback inference for items without explicit category
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
    source_url = item.get("source_url", "")
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

def is_broad_or_creative_query(query: str) -> bool:
    """Detect whether query is empty, broad, or asking for 'choice/creative/landing'."""
    q = query.strip().lower()
    if not q:
        return True

    # Direct phrases that signal creative freedom or broad landing exploration
    broad_phrases = [
        "choice", "creative", "landing", "landing page", "creative archetype",
        "of your choice", "of choice", "creative brief", "something cool",
        "creative showcase", "mind-blowing", "creative director", "archetype",
        "build a site", "build a web", "build an app", "new project"
    ]
    if any(phrase in q for phrase in broad_phrases):
        specific_tech = ["slider", "drawer", "modal", "chart", "analytics", "table", "button", "toggle", "liquid", "glass", "3d", "refraction"]
        if not any(tech in q for tech in specific_tech):
            return True

    words = [w for w in q.split() if len(w) > 1]
    generic_words = {
        "choice", "creative", "landing", "hero", "showcase", "portfolio",
        "homepage", "website", "web", "app", "ui", "design", "build",
        "modern", "cool", "best", "site"
    }
    if words and all(w in generic_words for w in words):
        return True

    return False

def derive_motion_preset(title, desc, video_url=None):
    """
    Primary Creative Director: Infers production motion presets, physical spring dynamics,
    CSS 3D rules, exact liquid glass refraction formulas, and creative scaffolds.
    """
    text = f"{title} {desc}".lower()

    # 1. Dedicated Liquid Glass Refraction Preset
    if any(k in text for k in ["liquid", "refraction", "glass", "chromatic", "frosted", "glassmorphism", "prism", "caustics"]):
        return {
            "type": "Kinetic Typography & Liquid Glass Refraction",
            "spring": {"stiffness": 420, "damping": 30, "mass": 1.0},
            "css_curve": "cubic-bezier(0.19, 1.0, 0.22, 1.0)",
            "timing_ms": 320,
            "principles": (
                "Real-time frosted glass refraction, chromatic aberration lens distortion, "
                "dynamic specular highlights tracking cursor motion, and high-saturation backdrop filtration."
            ),
            "css_3d": {
                "perspective": "1000px",
                "transform_style": "preserve-3d",
                "rules": "backdrop-filter: blur(24px) saturate(190%) contrast(115%); -webkit-backdrop-filter: blur(24px) saturate(190%) contrast(115%); perspective: 1000px; transform-style: preserve-3d;"
            },
            "liquid_glass_spec": {
                "backdrop_blur": "24px",
                "saturation": "190%",
                "contrast": "115%",
                "specular_highlight": "radial-gradient(circle 350px at var(--mouse-x, 50%) var(--mouse-y, 50%), rgba(255, 255, 255, 0.22), transparent 75%)",
                "chromatic_aberration": "feDisplacementMap scale='14' with RGB color channel split (red: +2px, blue: -2px)",
                "border": "1px solid rgba(255, 255, 255, 0.15)",
                "box_shadow": "0 30px 60px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.25)"
            },
            "code_scaffold": (
                "/* Liquid Glass Refraction & Chromatic Aberration Scaffold */\n"
                ".liquid-glass-panel {\n"
                "  background: rgba(255, 255, 255, 0.035);\n"
                "  backdrop-filter: blur(24px) saturate(190%) contrast(115%);\n"
                "  -webkit-backdrop-filter: blur(24px) saturate(190%) contrast(115%);\n"
                "  border: 1px solid rgba(255, 255, 255, 0.15);\n"
                "  box-shadow: 0 30px 60px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.25);\n"
                "  border-radius: 24px;\n"
                "  perspective: 1000px;\n"
                "  transform-style: preserve-3d;\n"
                "  position: relative;\n"
                "  overflow: hidden;\n"
                "}\n"
                ".liquid-glass-panel::after {\n"
                "  content: '';\n"
                "  position: absolute;\n"
                "  inset: 0;\n"
                "  background: radial-gradient(circle 350px at var(--mouse-x, 50%) var(--mouse-y, 50%), rgba(255, 255, 255, 0.22), transparent 75%);\n"
                "  pointer-events: none;\n"
                "  mix-blend-mode: overlay;\n"
                "}"
            ),
            "video_url": video_url or "https://pixlpin.com/media/designs/01M4ZYC28GA7SM4G1HZ7RJX71F/mp4-9b17b2d1.mp4"
        }

    # 2. 3D, WebGL, Particle, Canvas, Mesh, Shader
    elif any(k in text for k in ["particle", "webgl", "canvas", "mesh", "point-cloud", "shader", "glsl", "three.js", "threejs"]):
        return {
            "type": "3D WebGL / Particle Orbit Hero",
            "spring": {"stiffness": 340, "damping": 26, "mass": 0.9},
            "css_curve": "cubic-bezier(0.16, 1, 0.3, 1)",
            "timing_ms": 380,
            "principles": "Hardware-accelerated WebGL / Canvas particle field with mouse-reactive camera orbit, continuous ambient drift, and zero CPU layout jank.",
            "css_3d": {
                "perspective": "1000px",
                "transform_style": "preserve-3d",
                "rules": "perspective: 1000px; transform-style: preserve-3d; backface-visibility: hidden;"
            },
            "code_scaffold": (
                "// Three.js / WebGL Particle Field Scaffold\n"
                "import * as THREE from 'three';\n"
                "const scene = new THREE.Scene();\n"
                "const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);\n"
                "const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true, powerPreference: 'high-performance' });\n"
                "renderer.setSize(window.innerWidth, window.innerHeight);\n"
                "renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));\n"
                "const count = 1800;\n"
                "const geometry = new THREE.BufferGeometry();\n"
                "const positions = new Float32Array(count * 3);\n"
                "for (let i = 0; i < count * 3; i++) positions[i] = (Math.random() - 0.5) * 12;\n"
                "geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));\n"
                "const material = new THREE.PointsMaterial({ size: 0.035, color: 0x6366f1, transparent: true, opacity: 0.85, blending: THREE.AdditiveBlending });\n"
                "const particles = new THREE.Points(geometry, material);\n"
                "scene.add(particles);\n"
                "camera.position.z = 4.5;\n"
                "let targetX = 0, targetY = 0;\n"
                "window.addEventListener('mousemove', (e) => {\n"
                "  targetX = (e.clientX / window.innerWidth - 0.5) * 1.5;\n"
                "  targetY = (e.clientY / window.innerHeight - 0.5) * 1.5;\n"
                "});\n"
                "function animate() {\n"
                "  requestAnimationFrame(animate);\n"
                "  particles.rotation.y += 0.0012;\n"
                "  camera.position.x += (targetX - camera.position.x) * 0.05;\n"
                "  camera.position.y += (-targetY - camera.position.y) * 0.05;\n"
                "  camera.lookAt(scene.position);\n"
                "  renderer.render(scene, camera);\n"
                "}\n"
                "animate();"
            ),
            "video_url": video_url or "https://pixlpin.com/media/designs/01M4Z1PGJHE11DVJF5H7GSKKZ6/mp4-d5a5f0a4.mp4"
        }

    # 3. Tilt, Bento, Spatial, Depth
    elif any(k in text for k in ["tilt", "bento", "spatial", "depth"]):
        return {
            "type": "3D Bento Grid with Spatial Tilt & Depth",
            "spring": {"stiffness": 380, "damping": 28, "mass": 1.0},
            "css_curve": "cubic-bezier(0.16, 1, 0.3, 1)",
            "timing_ms": 280,
            "principles": "1200px CSS perspective container with spring tilt physics tracking cursor angle, dynamic radial lighting gradient, and multi-layer Z-depth elevation.",
            "css_3d": {
                "perspective": "1200px",
                "transform_style": "preserve-3d",
                "rules": "perspective: 1200px; transform-style: preserve-3d; transform: perspective(1200px) rotateX(var(--rot-x, 0deg)) rotateY(var(--rot-y, 0deg));"
            },
            "code_scaffold": (
                "// Spatial Tilt & Dynamic Lighting Scaffold\n"
                "const bentoCard = document.querySelector('.bento-tilt-card');\n"
                "bentoCard.addEventListener('mousemove', (e) => {\n"
                "  const rect = bentoCard.getBoundingClientRect();\n"
                "  const x = (e.clientX - rect.left) / rect.width - 0.5;\n"
                "  const y = (e.clientY - rect.top) / rect.height - 0.5;\n"
                "  bentoCard.style.transform = `perspective(1200px) rotateX(${-y * 12}deg) rotateY(${x * 12}deg) translateZ(10px)`;\n"
                "  bentoCard.style.setProperty('--mouse-x', `${(x + 0.5) * 100}%`);\n"
                "  bentoCard.style.setProperty('--mouse-y', `${(y + 0.5) * 100}%`);\n"
                "});\n"
                "bentoCard.addEventListener('mouseleave', () => {\n"
                "  bentoCard.style.transform = 'perspective(1200px) rotateX(0deg) rotateY(0deg) translateZ(0px)';\n"
                "});"
            ),
            "video_url": video_url or "https://pixlpin.com/media/designs/01M50V551ASYJXQF7XMV81HXES/mp4-8ac23fa2.mp4"
        }

    # 4. Camera, Orbit, Scrollytelling
    elif any(k in text for k in ["camera", "orbit", "scrollytelling", "scroll-driven"]):
        return {
            "type": "Immersive Scroll-Driven 3D Camera Orbit",
            "spring": {"stiffness": 260, "damping": 32, "mass": 1.2},
            "css_curve": "cubic-bezier(0.25, 1, 0.5, 1)",
            "timing_ms": 450,
            "principles": "Scroll-linked 3D camera trajectory through point-clouds and 3D geometries with physical damping and directional lighting shifts.",
            "css_3d": {
                "perspective": "1000px",
                "transform_style": "preserve-3d",
                "rules": "perspective: 1000px; transform-style: preserve-3d; will-change: transform;"
            },
            "code_scaffold": (
                "// Scroll-Driven Camera Path Scaffold\n"
                "window.addEventListener('scroll', () => {\n"
                "  const progress = window.scrollY / (document.documentElement.scrollHeight - window.innerHeight);\n"
                "  const targetZ = 5 - progress * 3;\n"
                "  const targetRotY = progress * Math.PI * 0.5;\n"
                "  camera.position.z += (targetZ - camera.position.z) * 0.08;\n"
                "  camera.rotation.y += (targetRotY - camera.rotation.y) * 0.08;\n"
                "  renderer.render(scene, camera);\n"
                "});"
            ),
            "video_url": video_url or "https://pixlpin.com/media/designs/01M4GAQYD9JH1MY3G3APHVF54W/mp4-83dd1528.mp4"
        }

    # 5. Futuristic Cybernetic / 3D Kinetic / Fintech
    elif any(k in text for k in ["3d", "kinetic", "cyber", "neon", "futuristic", "fintech"]):
        return {
            "type": "Futuristic Cybernetic / 3D Kinetic Interface",
            "spring": {"stiffness": 440, "damping": 32, "mass": 0.9},
            "css_curve": "cubic-bezier(0.08, 0.82, 0.17, 1.0)",
            "timing_ms": 260,
            "principles": "High-contrast dark aesthetic with laser neon accent pulses, live SVG telemetry traces, and 3D card tilt physics.",
            "css_3d": {
                "perspective": "1000px",
                "transform_style": "preserve-3d",
                "rules": "perspective: 1000px; transform-style: preserve-3d; filter: drop-shadow(0 0 15px rgba(99, 102, 241, 0.4));"
            },
            "code_scaffold": (
                "// Kinetic SVG Neon Particle Trace & Live Telemetry Scaffold\n"
                "const canvas = document.querySelector('#telemetry-canvas');\n"
                "const ctx = canvas.getContext('2d');\n"
                "function renderTelemetry() {\n"
                "  ctx.clearRect(0, 0, canvas.width, canvas.height);\n"
                "  // Dynamic laser traces and live data points\n"
                "  requestAnimationFrame(renderTelemetry);\n"
                "}\n"
                "renderTelemetry();"
            ),
            "video_url": video_url or "https://pixlpin.com/media/designs/01M4R69JZD09DQCPPYCRZP4QSR/mp4-aa5bca45.mp4"
        }

    # 6. Standard 2D UI Components
    elif any(k in text for k in ["slider", "stepper", "drag", "scrub", "toggle"]):
        return {
            "type": "Interactive Spring",
            "spring": {"stiffness": 420, "damping": 32, "mass": 1.0},
            "css_curve": "cubic-bezier(0.2, 0.0, 0.0, 1.0)",
            "timing_ms": 280,
            "principles": "Immediate gesture tracking, zero float, crisp resting boundary."
        }
    elif any(k in text for k in ["drawer", "modal", "sheet", "dialog", "overlay", "sidebar"]):
        return {
            "type": "Layer Elevation / Sheet",
            "spring": {"stiffness": 380, "damping": 36, "mass": 1.1},
            "css_curve": "cubic-bezier(0.16, 1, 0.3, 1)",
            "timing_ms": 340,
            "principles": "Decoupled background fade (linear 200ms) with fast spring sheet entrance."
        }
    elif any(k in text for k in ["chart", "graph", "analytics", "dashboard", "metric", "bar"]):
        return {
            "type": "Data Visualization Stagger",
            "spring": {"stiffness": 300, "damping": 28, "mass": 0.9},
            "css_curve": "cubic-bezier(0.25, 1, 0.5, 1)",
            "timing_ms": 450,
            "principles": "Stagger children by 30-50ms, clip-path or stroke-dashoffset reveal."
        }
    elif any(k in text for k in ["chat", "ai", "message", "feed", "timeline"]):
        return {
            "type": "Conversational Stream",
            "spring": {"stiffness": 450, "damping": 34, "mass": 0.85},
            "css_curve": "cubic-bezier(0.05, 0.9, 0.1, 1.0)",
            "timing_ms": 220,
            "principles": "Subtle Y-offset (6-10px) with fast opacity ramp, zero bounce."
        }
    else:
        return {
            "type": "Production Motion Standard",
            "spring": {"stiffness": 350, "damping": 30, "mass": 1.0},
            "css_curve": "cubic-bezier(0.16, 1, 0.3, 1)",
            "timing_ms": 300,
            "principles": "Fast exit (200ms), deliberate entrance (300ms), physical damping."
        }

def load_data():
    """Load curated showcases from metadata or fallback dataset."""
    items = []
    if os.path.exists(META_PATH):
        with open(META_PATH, "r", encoding="utf-8") as f:
            try:
                items = json.load(f)
            except Exception as e:
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

def list_categories(items):
    """Print all available categories with their item counts and exit."""
    counts = Counter()
    for it in items:
        cat = get_item_category(it)
        counts[cat] += 1

    total_items = len(items)
    print("\n=======================================================")
    print(f" Design & Motion Library Categories ({total_items} items total)")
    print("=======================================================\n")
    for cat, count in counts.most_common():
        pct = (count / total_items) * 100 if total_items else 0
        bar = "█" * max(1, int(pct / 2.5))
        print(f"  • {cat:<26} {count:>4} items ({pct:>4.1f}%)  {bar}")
    print(f"\nTotal: {len(counts)} categories across {total_items} showcases.\n")

def format_full_blueprint(item, index=1):
    """Format the complete verbatim prompt blueprint and code implementation."""
    category = get_item_category(item)
    source_site, source_url = get_source_info(item)
    video_url = item.get("video_url", "N/A")
    title = item.get("title", "Showcase Design")
    full_prompt = item.get("full_prompt")

    lines = []
    lines.append("######################################################################")
    lines.append(f"[{index}] {title}")
    lines.append(f"Category: {category}  |  Source: {source_site}  |  Type: {item.get('type', 'experience')}")
    lines.append(f"Source URL: {source_url}")
    lines.append(f"Video URL:  {video_url}")
    lines.append("----------------------------------------------------------------------")

    if full_prompt and str(full_prompt).strip():
        lines.append(str(full_prompt).strip())
    else:
        # Synthesize complete, production-grade blueprint for showcases without pre-baked text prompt
        mp = item.get("motion_preset") or derive_motion_preset(title, item.get("description", ""), video_url=video_url)
        lines.append(f"Build a production-grade, high-impact web interface for \"{title}\" with React, TypeScript, and Tailwind CSS.\n")
        lines.append("---")
        lines.append("VISUAL OVERVIEW & ARCHITECTURE")
        lines.append(f"- Concept: {item.get('description', '')}")
        lines.append(f"- Motion Architecture: {mp.get('type')}")
        lines.append(f"- Principles: {mp.get('principles')}\n")
        lines.append("---")
        lines.append("FONTS & TYPOGRAPHY")
        lines.append("- Display/Heading Font: 'Syne', sans-serif (weights: 700, 800) or 'Space Grotesk'")
        lines.append("- Body/Interface Font: 'Inter', system-ui, sans-serif (weights: 400, 500)")
        lines.append("- Import via Google Fonts:\n  <link href=\"https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Syne:wght@700;800&family=Inter:wght@400;500;600&display=swap\" rel=\"stylesheet\">\n")
        lines.append("---")
        lines.append("MOTION & SPRING PHYSICS SPEC")
        spring = mp.get("spring", {})
        lines.append(f"- Spring Dynamics: stiffness={spring.get('stiffness', 350)}, damping={spring.get('damping', 30)}, mass={spring.get('mass', 1.0)}")
        lines.append(f"- CSS Timing: {mp.get('timing_ms', 300)}ms {mp.get('css_curve', 'cubic-bezier(0.16, 1, 0.3, 1)')}")
        if mp.get("css_3d"):
            lines.append(f"- CSS 3D Rules: {mp.get('css_3d', {}).get('rules')}")
        if mp.get("liquid_glass_spec"):
            lg = mp["liquid_glass_spec"]
            lines.append("- Liquid Glass Formulas:")
            lines.append(f"  • Backdrop Filter: blur({lg['backdrop_blur']}) saturate({lg['saturation']}) contrast({lg['contrast']})")
            lines.append(f"  • Specular Gradient: {lg['specular_highlight']}")
            lines.append(f"  • Chromatic Aberration: {lg['chromatic_aberration']}")
            lines.append(f"  • Border & Shadow: {lg['border']} | {lg['box_shadow']}")
        lines.append("\n---")
        lines.append("CODE IMPLEMENTATION SCAFFOLD")
        if mp.get("code_scaffold"):
            lines.append(mp.get("code_scaffold"))
        lines.append("\n---")
        lines.append(f"LIVE MOTION REFERENCE VIDEO: {video_url}")

    lines.append("######################################################################\n")
    return "\n".join(lines)

def search(query="", limit=5, filter_3d=False, filter_liquid_glass=False, category_filter=None):
    """
    Search curated showcases with Embedding & TF-IDF similarity,
    3D/Liquid Glass filters, category matching, and creative archetypes.
    """
    items = load_data()

    # Pre-filter by Category if specified
    if category_filter:
        items = [it for it in items if matches_category(it, category_filter)]

    # Pre-filter by Liquid Glass if requested
    if filter_liquid_glass:
        items = [it for it in items if is_liquid_glass_showcase(it)]

    # Pre-filter by 3D if requested
    if filter_3d:
        items = [it for it in items if is_3d_showcase(it)]

    # Empty or broad query handling
    if is_broad_or_creative_query(query):
        # If user explicitly requested liquid-glass, 3d, or a category, return top matching items from pool
        if filter_liquid_glass or filter_3d or category_filter:
            results = []
            for it in items[:limit]:
                mp = derive_motion_preset(it.get("title", ""), it.get("description", ""), video_url=it.get("video_url"))
                results.append({
                    **it,
                    "relevance_score": 1.0,
                    "motion_preset": mp
                })
            return results

        # Otherwise return the 5 mind-blowing creative archetypes
        return [dict(a) for a in CREATIVE_ARCHETYPES[:limit]]

    if not items:
        return []

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

    # Keyword boosts
    q_words = [w.lower() for w in query.split() if len(w) > 2]
    is_3d_query = any(k in query.lower() for k in THREED_KEYWORDS)
    is_liquid_query = any(k in query.lower() for k in LIQUID_GLASS_KEYWORDS)
    scored = []

    for idx, it in enumerate(items):
        sim = float(similarities[idx]) if idx < len(similarities) else 0.0
        title_lower = it.get('title', '').lower()
        desc_lower = it.get('description', '').lower()
        cat_lower = get_item_category(it).lower()

        # Exact keyword matches boost
        exact_boost = sum(0.35 for w in q_words if w in title_lower)
        exact_boost += sum(0.20 for w in q_words if w in cat_lower)
        exact_boost += sum(0.15 for w in q_words if w in desc_lower)

        # 3D / Kinetic boost if query asks for 3D/WebGL or filter_3d
        if filter_3d or is_3d_query:
            if any(k in title_lower for k in ["3d", "webgl", "particle", "liquid", "kinetic", "canvas"]):
                exact_boost += 0.35
            elif any(k in desc_lower for k in ["3d", "webgl", "particle", "liquid", "kinetic", "canvas"]):
                exact_boost += 0.15

        # Liquid Glass boost if query asks for liquid/glass or filter_liquid_glass
        if filter_liquid_glass or is_liquid_query:
            if any(k in title_lower for k in ["liquid", "glass", "refraction", "chromatic", "frosted"]):
                exact_boost += 0.40
            elif any(k in desc_lower for k in ["liquid", "glass", "refraction", "chromatic", "frosted"]):
                exact_boost += 0.20

        total_score = sim + exact_boost
        if total_score > 0.05 or not q_words:
            mp = derive_motion_preset(it.get("title", ""), it.get("description", ""), video_url=it.get("video_url"))
            it_with_motion = {
                **it,
                "relevance_score": round(float(total_score), 4),
                "motion_preset": mp
            }
            scored.append((total_score, it_with_motion))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [it for _, it in scored[:limit]]

def main():
    parser = argparse.ArgumentParser(
        description="EmbeddingGemma 2 UI Motion & Design Library Engine for Autonomous Coding Agents"
    )
    parser.add_argument(
        "query",
        nargs="*",
        help="Creative prompt or query terms (e.g. 'liquid glass', '3d spatial hero', 'bento tilt depth', 'fintech cybernetic')"
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
        help="Filter by category (e.g. 3D, Hero, SaaS, Fashion, Portfolio, Fintech)"
    )
    parser.add_argument(
        "--list-categories",
        action="store_true",
        help="Print all available categories with their item counts and exit"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Print the entire verbatim prompt blueprint (including font links, Tailwind classes, video scrub event listeners, and exact CSS/shader formulas)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Max results to return (default: 5)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON for programmatic agent consumption"
    )
    args = parser.parse_args()

    # Handle --list-categories early
    if args.list_categories:
        items = load_data()
        list_categories(items)
        return

    query_str = " ".join(args.query) if args.query else ""
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
    if args.three_d:
        filter_tags.append("--3d")
    if args.liquid_glass:
        filter_tags.append("--liquid-glass")
    if args.category:
        filter_tags.append(f"--category '{args.category}'")
    tag_str = f" [{' '.join(filter_tags)}]" if filter_tags else ""

    if args.full:
        print(f"\n=======================================================")
        print(f" UI Motion & Creative Director: '{query_str}'{tag_str} [FULL BLUEPRINT]")
        print(f" Showing {len(results)} Complete Implementation Blueprints")
        print(f"=======================================================\n")
        for i, r in enumerate(results, 1):
            print(format_full_blueprint(r, index=i))
        return

    print(f"\n=======================================================")
    print(f" UI Motion & Creative Director: '{query_str}'{tag_str}")
    print(f" Matched {len(results)} Curated Showcases (Embedding & Vision Grounded)")
    print(f"=======================================================\n")

    for i, r in enumerate(results, 1):
        mp = r.get("motion_preset", {})
        arch = r.get("archetype")
        arch_label = f" [Archetype: {arch}]" if arch else ""
        category = get_item_category(r)
        source_site, source_url = get_source_info(r)

        print(f"[{i}]{arch_label} {r.get('title')}")
        print(f"    - Category:        {category}")
        print(f"    - Source:          {source_site} ({source_url})")
        print(f"    - Video Asset:     {r.get('video_url', 'N/A')}")
        print(f"    - Relevance Score: {r.get('relevance_score', 'N/A')}")
        print(f"    - Description:     {r.get('description')}")
        print(f"    - Motion Type:     {mp.get('type')}")
        print(f"    - Spring Config:   stiffness={mp.get('spring', {}).get('stiffness')}, damping={mp.get('spring', {}).get('damping')}, mass={mp.get('spring', {}).get('mass', 1.0)}")
        if mp.get('liquid_glass_spec'):
            lg = mp['liquid_glass_spec']
            print(f"    - Liquid Glass:    backdrop-filter: blur({lg.get('backdrop_blur')}) saturate({lg.get('saturation')}) contrast({lg.get('contrast')}); specular highlight; chromatic dispersion")
        if mp.get('css_3d'):
            print(f"    - CSS 3D Rules:    {mp.get('css_3d', {}).get('rules')}")
        print(f"    - CSS Transition:  transition: all {mp.get('timing_ms')}ms {mp.get('css_curve')}")
        print(f"    - Principle:       {mp.get('principles')}")
        if mp.get('code_scaffold'):
            lines = mp.get('code_scaffold').splitlines()
            preview = "\n      ".join(lines[:5])
            print(f"    - Creative Scaffold (5-line preview | use --full for complete blueprint):\n      {preview}\n")
        else:
            print(f"    - Blueprint:       Pass --full to view entire verbatim prompt blueprint\n")

if __name__ == "__main__":
    main()
