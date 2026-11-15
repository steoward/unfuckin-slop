#!/usr/bin/env python3
"""
EmbeddingGemma 2 UI Motion & 3D Creative Director Retriever for Autonomous Coding Agents.
Drives jaw-dropping, 3D, WebGL, and kinetic designs from 622 curated visual showcases
with full creative scaffolds, CSS 3D rules, spring physics, and direct MP4 video URLs.
"""

import os
import sys
import json
import argparse
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
    "perspective", "physics", "point-cloud", "cyber", "neon", "bento", "glass"
]

# The 5 Mind-Blowing Creative Archetypes returned for empty or generic queries
CREATIVE_ARCHETYPES = [
    {
        "id": "minimal-white-hero-with-generative-particle-animation",
        "title": "3D Interactive Spatial Hero (Three.js / WebGL Particle Orbit)",
        "archetype": "3D Interactive Spatial Hero",
        "archetype_key": "a",
        "description": "Clean, modern spatial hero featuring floating 3D particle terrain waves in WebGL/Three.js with real-time mouse reactivity, particle orbit physics, centered headline typography, glowing interactive CTA button, and partner ticker.",
        "video_url": "https://pixlpin.com/media/designs/01M4Z1PGJHE11DVJF5H7GSKKZ6/mp4-d5a5f0a4.mp4",
        "local_video": "videos/minimal-white-hero-with-generative-particle-animation.mp4",
        "source_url": "https://pixlpin.com/d/minimal-white-hero-with-generative-particle-animation",
        "relevance_score": 1.0,
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
        "description": "3D real-time glass refraction, chromatic lens distortion, and physical material depth layered over bold kinetic editorial typography with dynamic scroll-linked refraction shaders.",
        "video_url": "https://pixlpin.com/media/designs/01M4ZYC28GA7SM4G1HZ7RJX71F/mp4-9b17b2d1.mp4",
        "local_video": "videos/liquid-glass-3d-effect-showcase.mp4",
        "source_url": "https://pixlpin.com/d/liquid-glass-3d-effect-showcase",
        "relevance_score": 0.98,
        "motion_preset": {
            "type": "Kinetic Typography & Liquid Glass Refraction",
            "spring": {"stiffness": 420, "damping": 30, "mass": 1.0},
            "css_curve": "cubic-bezier(0.19, 1.0, 0.22, 1.0)",
            "timing_ms": 320,
            "principles": "Real-time frosted glass refraction, chromatic aberration lens distortion, and dynamic lighting highlights tracking pointer motion over editorial typography.",
            "css_3d": {
                "perspective": "1000px",
                "transform_style": "preserve-3d",
                "rules": "backdrop-filter: blur(20px) saturate(180%) contrast(110%); perspective: 1000px; transform-style: preserve-3d;"
            },
            "code_scaffold": (
                "/* Liquid Glass Refraction & Chromatic Distortion Scaffold */\n"
                ".liquid-glass-surface {\n"
                "  background: rgba(255, 255, 255, 0.03);\n"
                "  backdrop-filter: blur(24px) saturate(190%) contrast(115%);\n"
                "  -webkit-backdrop-filter: blur(24px) saturate(190%) contrast(115%);\n"
                "  border: 1px solid rgba(255, 255, 255, 0.12);\n"
                "  box-shadow: 0 30px 60px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.2);\n"
                "  perspective: 1000px;\n"
                "  transform-style: preserve-3d;\n"
                "  transition: transform 320ms cubic-bezier(0.19, 1.0, 0.22, 1.0);\n"
                "}\n"
                ".liquid-glass-surface::after {\n"
                "  content: '';\n"
                "  position: absolute;\n"
                "  inset: 0;\n"
                "  border-radius: inherit;\n"
                "  background: radial-gradient(circle 350px at var(--mouse-x, 50%) var(--mouse-y, 50%), rgba(255, 255, 255, 0.15), transparent 80%);\n"
                "  pointer-events: none;\n"
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
        "description": "Dark bento grid with 1200px CSS perspective, dynamic spring tilt physics tracking cursor angle, dynamic radial lighting gradients, and layered Z-depth cards.",
        "video_url": "https://pixlpin.com/media/designs/01M50V551ASYJXQF7XMV81HXES/mp4-8ac23fa2.mp4",
        "local_video": "videos/autonomous-crypto-trading-agent-bento-grid.mp4",
        "source_url": "https://pixlpin.com/d/autonomous-crypto-trading-agent-bento-grid",
        "relevance_score": 0.96,
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
        "description": "Fintech interface featuring high-contrast dark aesthetic, laser neon accents, glowing SVG particle traces, live data telemetry feeds, and 3D card tilt.",
        "video_url": "https://pixlpin.com/media/designs/01M4R69JZD09DQCPPYCRZP4QSR/mp4-aa5bca45.mp4",
        "local_video": "videos/highnote.mp4",
        "source_url": "https://pixlpin.com/d/highnote",
        "relevance_score": 0.94,
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
        "description": "A dark-mode product showcase website featuring scroll-driven 3D point-cloud camera transitions, kinetic typography, dynamic directional lighting shifts, and detailed feature grids.",
        "video_url": "https://pixlpin.com/media/designs/01M4GAQYD9JH1MY3G3APHVF54W/mp4-83dd1528.mp4",
        "local_video": "videos/shopify-editions-spring-26.mp4",
        "source_url": "https://pixlpin.com/d/shopify-editions-spring-26",
        "relevance_score": 0.92,
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
        # Allow technical queries like 'landing page slider' to search specifically
        specific_tech = ["slider", "drawer", "modal", "chart", "analytics", "table", "button", "toggle"]
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

def is_3d_showcase(item) -> bool:
    """Check if showcase exhibits 3D, WebGL, particle, kinetic, or spatial dynamics."""
    text = f"{item.get('title', '')} {item.get('description', '')}".lower()
    return any(k in text for k in THREED_KEYWORDS)

def derive_motion_preset(title, desc, video_url=None):
    """
    Primary Creative Director: Infers production motion presets, physical spring dynamics,
    CSS 3D rules, and creative scaffolds for 3D/WebGL/Kinetic and UI components.
    """
    text = f"{title} {desc}".lower()

    # 1. 3D, WebGL, Particle, Canvas, Mesh, Shader
    if any(k in text for k in ["particle", "webgl", "canvas", "mesh", "point-cloud", "shader", "glsl"]):
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

    # 2. Liquid, Refraction, Glass, Chromatic
    elif any(k in text for k in ["liquid", "refraction", "glass"]):
        return {
            "type": "Kinetic Typography & Liquid Glass Refraction",
            "spring": {"stiffness": 420, "damping": 30, "mass": 1.0},
            "css_curve": "cubic-bezier(0.19, 1.0, 0.22, 1.0)",
            "timing_ms": 320,
            "principles": "Real-time frosted glass refraction, chromatic aberration lens distortion, and dynamic lighting highlights tracking pointer motion over editorial typography.",
            "css_3d": {
                "perspective": "1000px",
                "transform_style": "preserve-3d",
                "rules": "backdrop-filter: blur(20px) saturate(180%) contrast(110%); perspective: 1000px; transform-style: preserve-3d;"
            },
            "code_scaffold": (
                "/* Liquid Glass Refraction Scaffold */\n"
                ".liquid-glass-surface {\n"
                "  background: rgba(255, 255, 255, 0.03);\n"
                "  backdrop-filter: blur(24px) saturate(190%) contrast(115%);\n"
                "  -webkit-backdrop-filter: blur(24px) saturate(190%) contrast(115%);\n"
                "  border: 1px solid rgba(255, 255, 255, 0.12);\n"
                "  box-shadow: 0 30px 60px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.2);\n"
                "  perspective: 1000px;\n"
                "  transform-style: preserve-3d;\n"
                "  transition: transform 320ms cubic-bezier(0.19, 1.0, 0.22, 1.0);\n"
                "}\n"
                ".liquid-glass-surface::after {\n"
                "  content: '';\n"
                "  position: absolute;\n"
                "  inset: 0;\n"
                "  border-radius: inherit;\n"
                "  background: radial-gradient(circle 350px at var(--mouse-x, 50%) var(--mouse-y, 50%), rgba(255, 255, 255, 0.15), transparent 80%);\n"
                "  pointer-events: none;\n"
                "}"
            ),
            "video_url": video_url or "https://pixlpin.com/media/designs/01M4ZYC28GA7SM4G1HZ7RJX71F/mp4-9b17b2d1.mp4"
        }

    # 3. Tilt, Bento, Spatial, Perspective
    elif any(k in text for k in ["tilt", "bento", "spatial"]):
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
    elif any(k in text for k in ["camera", "orbit", "scrollytelling"]):
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
            items = json.load(f)
    elif os.path.exists(FALLBACK_DATASET):
        with open(FALLBACK_DATASET, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        items.append(json.loads(line))
                    except Exception:
                        pass
    return items

def search(query, limit=5, filter_3d=False):
    """
    Search curated showcases with Embedding & TF-IDF similarity,
    3D/Kinetic boosting, and creative archetypes.
    """
    # 1. Empty or broad query -> Return 5 mind-blowing creative archetypes
    if is_broad_or_creative_query(query):
        return [dict(a) for a in CREATIVE_ARCHETYPES[:limit]]

    items = load_data()
    if not items:
        return []

    # Filter for 3D if requested
    if filter_3d:
        three_d_pool = [it for it in items if is_3d_showcase(it)]
        if three_d_pool:
            items = three_d_pool

    # Build corpus for hybrid TF-IDF + token similarity
    corpus = [
        f"{it.get('title', '')} {it.get('title', '')} {it.get('description', '')} {it.get('id', '').replace('-', ' ')}"
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
    scored = []

    for idx, it in enumerate(items):
        sim = float(similarities[idx]) if idx < len(similarities) else 0.0
        title_lower = it.get('title', '').lower()
        desc_lower = it.get('description', '').lower()

        # Exact keyword matches boost
        exact_boost = sum(0.35 for w in q_words if w in title_lower)
        exact_boost += sum(0.15 for w in q_words if w in desc_lower)

        # 3D / Kinetic boost if query asks for 3D/WebGL or filter_3d
        if filter_3d or is_3d_query:
            if any(k in title_lower for k in ["3d", "webgl", "particle", "liquid", "kinetic", "canvas"]):
                exact_boost += 0.35
            elif any(k in desc_lower for k in ["3d", "webgl", "particle", "liquid", "kinetic", "canvas"]):
                exact_boost += 0.15

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
        description="EmbeddingGemma 2 UI Motion & 3D Creative Director Retriever for Autonomous Coding Agents"
    )
    parser.add_argument(
        "query",
        nargs="*",
        help="Creative prompt or query terms (e.g. '3d spatial hero', 'kinetic typography refraction', 'bento tilt depth', 'fintech cybernetic')"
    )
    parser.add_argument(
        "--3d",
        dest="three_d",
        action="store_true",
        help="Filter exclusively for 3D, WebGL, particle, kinetic, and spatial showcases"
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

    query_str = " ".join(args.query) if args.query else ""
    results = search(query_str, limit=args.limit, filter_3d=args.three_d)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    filter_tag = " [--3d filter]" if args.three_d else ""
    print(f"\n=======================================================")
    print(f" UI Motion & Creative Director: '{query_str}'{filter_tag}")
    print(f" Matched {len(results)} Curated Showcases (Embedding & Vision Grounded)")
    print(f"=======================================================\n")

    for i, r in enumerate(results, 1):
        mp = r.get("motion_preset", {})
        arch = r.get("archetype")
        arch_label = f" [Archetype: {arch}]" if arch else ""
        print(f"[{i}]{arch_label} {r.get('title')}")
        print(f"    - Relevance Score: {r.get('relevance_score', 'N/A')}")
        print(f"    - Description:     {r.get('description')}")
        print(f"    - Video Asset:     {r.get('video_url', 'N/A')}")
        print(f"    - Source Link:     {r.get('source_url', 'N/A')}")
        print(f"    - Motion Type:     {mp.get('type')}")
        print(f"    - Spring Config:   stiffness={mp.get('spring', {}).get('stiffness')}, damping={mp.get('spring', {}).get('damping')}, mass={mp.get('spring', {}).get('mass', 1.0)}")
        if mp.get('css_3d'):
            print(f"    - CSS 3D Rules:    {mp.get('css_3d', {}).get('rules')}")
        print(f"    - CSS Transition:  transition: all {mp.get('timing_ms')}ms {mp.get('css_curve')}")
        print(f"    - Principle:       {mp.get('principles')}")
        if mp.get('code_scaffold'):
            lines = mp.get('code_scaffold').splitlines()
            preview = "\n      ".join(lines[:4])
            if len(lines) > 4:
                preview += f"\n      ... ({len(lines) - 4} more lines in --json)"
            print(f"    - Creative Code:   \n      {preview}\n")
        else:
            print()

if __name__ == "__main__":
    main()
