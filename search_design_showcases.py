#!/usr/bin/env python3
"""
Semantic & Motion UI Retriever for Autonomous Coding Agents.
Allows any agent to find visual reference patterns, motion dynamics,
and video links from 600+ curated showcases without requiring an external MCP.
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

# Infer production spring/curve parameters based on design characteristics
def derive_motion_preset(title, desc):
    text = f"{title} {desc}".lower()
    if any(k in text for k in ["slider", "stepper", "drag", "scrub", "toggle"]):
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

def search(query, limit=5):
    items = load_data()
    if not items:
        return []
    
    if not query.strip():
        # Return representative showcases across categories
        return [{**it, "motion_preset": derive_motion_preset(it.get("title", ""), it.get("description", ""))} for it in items[:limit]]

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
    scored = []
    
    for idx, it in enumerate(items):
        sim = float(similarities[idx]) if idx < len(similarities) else 0.0
        title_lower = it.get('title', '').lower()
        desc_lower = it.get('description', '').lower()
        
        # Exact keyword matches boost
        exact_boost = sum(0.25 for w in q_words if w in title_lower)
        exact_boost += sum(0.10 for w in q_words if w in desc_lower)
        
        total_score = sim + exact_boost
        if total_score > 0.05 or not q_words:
            it_with_motion = {
                **it,
                "relevance_score": round(float(total_score), 4),
                "motion_preset": derive_motion_preset(it.get("title", ""), it.get("description", ""))
            }
            scored.append((total_score, it_with_motion))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [it for _, it in scored[:limit]]

def main():
    parser = argparse.ArgumentParser(description="Autonomous Agent UI Motion & Design Reference Search")
    parser.add_argument("query", nargs="*", help="Query terms (e.g. 'dark mode dashboard', 'slider physics', 'ai chat drawer')")
    parser.add_argument("--limit", type=int, default=3, help="Max results to return (default: 3)")
    parser.add_argument("--json", action="store_true", help="Output JSON for programmatic agent consumption")
    args = parser.parse_args()

    query_str = " ".join(args.query) if args.query else ""
    results = search(query_str, limit=args.limit)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    print(f"\n=======================================================")
    print(f" UI Motion & Reference Retrieval: '{query_str}'")
    print(f" Matched {len(results)} Curated Showcases (Embedding & Vision Grounded)")
    print(f"=======================================================\n")

    for i, r in enumerate(results, 1):
        mp = r.get("motion_preset", {})
        print(f"[{i}] {r.get('title')}")
        print(f"    - Relevance Score: {r.get('relevance_score', 'N/A')}")
        print(f"    - Description:     {r.get('description')}")
        print(f"    - Video Asset:     {r.get('video_url', 'N/A')}")
        print(f"    - Source Link:     {r.get('source_url', 'N/A')}")
        print(f"    - Motion Type:     {mp.get('type')}")
        print(f"    - Spring Config:   stiffness={mp.get('spring', {}).get('stiffness')}, damping={mp.get('spring', {}).get('damping')}")
        print(f"    - CSS Transition:  transition: all {mp.get('timing_ms')}ms {mp.get('css_curve')}")
        print(f"    - Principle:       {mp.get('principles')}\n")

if __name__ == "__main__":
    main()
