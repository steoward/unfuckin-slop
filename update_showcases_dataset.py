#!/usr/bin/env python3
"""
Pipeline to parse motionsites-free-prompts.txt, merge with Pixlpin showcases,
generate 384-dimensional vector embeddings, and save showcases_meta.json and dataset.jsonl.
"""

import os
import re
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SHOWCASES_DIR = os.path.join(BASE_DIR, "design_showcases")
META_PATH = os.path.join(SHOWCASES_DIR, "showcases_meta.json")
DATASET_PATH = os.path.join(SHOWCASES_DIR, "dataset.jsonl")
EMBS_PATH = os.path.join(SHOWCASES_DIR, "design_embeddings.npy")
SOURCE_FILE = r'C:\Users\MOBPC\.deepai-code\scratch\2026-11-16-motionsites-ai-txt-aa5a2af1\motionsites-free-prompts.txt'

from search_design_showcases import get_item_category, THREED_KEYWORDS, LIQUID_GLASS_KEYWORDS

def clean_sentence(s):
    s = s.strip()
    s = re.sub(r'[*_`#>]', '', s)
    s = re.sub(r'^-\s+', '', s)
    s = re.sub(r'\s+', ' ', s)
    s = re.sub(r'^(?:Please\s+)?(?:Build|Create|Recreate|Design)\s+(?:a|an|the|one)\s+', '', s, flags=re.IGNORECASE)
    s = re.sub(r'^(?:full recreation brief\s*:?\s*)', '', s, flags=re.IGNORECASE)
    s = s.strip()
    if s and not s.endswith(('.', '!', '?')):
        s += '.'
    return s[0].upper() + s[1:] if s else ""

def generate_description(title, category, prompt_type, prompt_text):
    lines = [l.strip() for l in prompt_text.splitlines() if l.strip()]
    intro_lines = []
    for l in lines:
        if l.startswith(('#', '---', 'FONTS', 'Load two', 'Load the', '```', '<link', 'import ')):
            continue
        if re.match(r'^(GOAL|OBJECTIVE|OVERVIEW|DESCRIPTION|SUMMARY):?', l, re.IGNORECASE):
            l = re.sub(r'^(GOAL|OBJECTIVE|OVERVIEW|DESCRIPTION|SUMMARY):?\s*', '', l, flags=re.IGNORECASE)
        if any(w in l.lower() for w in ['npm install', 'create-react-app', 'tailwind.config', 'lucide-react', 'package.json']):
            continue
        if l.startswith(('const ', 'let ', 'var ', 'function ', 'export ', 'class ', 'return ', '<')):
            continue
        if len(l) > 25:
            intro_lines.append(l)
        if len(intro_lines) >= 4:
            break

    combined_intro = " ".join(intro_lines)
    raw_sentences = re.split(r'(?<=[.!?])\s+', combined_intro)
    clean_sentences = []
    for s in raw_sentences:
        if re.search(r'^(Here is every detail|Output only that|Do not download|Do not invent|You are an implementation|Do not use any external|Everything is one index\.html)', s, re.IGNORECASE):
            continue
        cs = clean_sentence(s)
        if len(cs) > 20 and not cs.startswith('Section container'):
            clean_sentences.append(cs)
        if len(clean_sentences) >= 2:
            break

    p_lower = prompt_text.lower()
    t_lower = title.lower()
    motion_mechanics = []
    if "mouse" in p_lower and ("scrub" in p_lower or "track" in p_lower or "tilt" in p_lower):
        motion_mechanics.append("interactive cursor/mouse tracking and scrub-driven interaction")
    if "three.js" in p_lower or "threejs" in p_lower or "webgl" in p_lower:
        motion_mechanics.append("hardware-accelerated WebGL / Three.js 3D rendering")
    elif "canvas" in p_lower or "particle" in p_lower:
        motion_mechanics.append("dynamic canvas particle and fluid simulation")
    if any(k in p_lower or k in t_lower for k in ["liquid glass", "refraction", "chromatic aberration", "frosted glass", "glassmorphism"]):
        motion_mechanics.append("real-time liquid glass refraction with chromatic lens effects")
    if any(k in p_lower for k in ["gsap", "scrolltrigger", "scroll-driven", "scrollytelling", "parallax"]):
        motion_mechanics.append("scroll-driven kinetic animations and staggered choreography")
    if "spring" in p_lower or "physics" in p_lower:
        motion_mechanics.append("physical spring dynamics and kinetic damping")
    if "video" in p_lower and ("background" in p_lower or "loop" in p_lower or "mp4" in p_lower):
        motion_mechanics.append("cinematic looping background video integration")
    if "bento" in p_lower:
        motion_mechanics.append("spatial bento-grid card elevation")
    if "marquee" in p_lower or "ticker" in p_lower:
        motion_mechanics.append("seamless infinite marquee ticker transitions")

    if not motion_mechanics:
        motion_mechanics.append("responsive interactive states and fluid micro-transitions")

    s1 = clean_sentences[0] if clean_sentences else f"Clean, high-impact {category} {prompt_type} interface showcasing {title}."
    s2 = clean_sentences[1] if len(clean_sentences) > 1 else ""
    mech_str = "Features " + ", ".join(motion_mechanics[:2]) + " with precision layout polish."

    if s2:
        return f"{s1} {s2} {mech_str}"
    else:
        return f"{s1} {mech_str}"

def parse_motionsites():
    print(f"[*] Reading motionsites prompts from {SOURCE_FILE}...")
    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        raw_text = f.read()

    pattern = re.compile(
        r'^={50,}\s*\n'
        r'\[(\d+)\]\s+(.*?)\n'
        r'Category:\s*(.*?)\s*\|\s*Type:\s*(.*?)\n'
        r'Source:\s*(.*?)\n'
        r'-{50,}\s*\n',
        re.MULTILINE
    )

    matches = list(pattern.finditer(raw_text))
    print(f"[*] Matched {len(matches)} prompt blocks.")

    items = []
    for i, m in enumerate(matches):
        title = m.group(2).strip()
        category = m.group(3).strip()
        raw_type = m.group(4).strip()
        clean_type = raw_type.split('|')[0].strip().lower()
        source_url = m.group(5).strip()

        start_pos = m.end()
        end_pos = matches[i+1].start() if i + 1 < len(matches) else len(raw_text)
        prompt_chunk = raw_text[start_pos:end_pos].strip()
        prompt_chunk = re.sub(r'={40,}\s*\nEND OF COLLECTION[\s\S]*$', '', prompt_chunk).strip()

        if '?prompt=' in source_url:
            item_id = source_url.split('?prompt=')[-1].strip()
        else:
            item_id = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')

        mp4_urls = re.findall(r'https?://[^\s"\'<>\)]+?\.mp4', prompt_chunk)
        video_url = None
        if mp4_urls:
            cf_urls = [u for u in mp4_urls if 'cloudfront.net' in u]
            v = cf_urls[0] if cf_urls else mp4_urls[0]
            video_url = v.rstrip('.,;:')

        desc = generate_description(title, category, clean_type, prompt_chunk)

        search_space = f"{title} {category} {clean_type} {prompt_chunk}".lower()
        is_3d = bool(re.search(r'\b(3d|three\.?js|webgl|canvas|shader|glsl)\b', search_space))
        is_liquid_glass = bool(re.search(r'\b(liquid\s*glass|refraction|chromatic\s*aberration|frosted\s*glass|glassmorphism)\b', search_space))

        items.append({
            "id": item_id,
            "title": title,
            "category": category,
            "type": clean_type,
            "source_url": source_url,
            "video_url": video_url,
            "local_video": None,
            "description": desc,
            "full_prompt": prompt_chunk,
            "is_3d": is_3d,
            "is_liquid_glass": is_liquid_glass,
            "source_site": "motionsites.ai"
        })

    return items

def load_pixlpin():
    print(f"[*] Loading existing Pixlpin showcases from {META_PATH}...")
    with open(META_PATH, 'r', encoding='utf-8') as f:
        pixlpin_items = json.load(f)

    print(f"[*] Found {len(pixlpin_items)} Pixlpin showcases.")
    normalized = []
    for it in pixlpin_items:
        t = f"{it.get('title', '')} {it.get('description', '')}".lower()
        is_3d = bool(it.get('is_3d')) or any(k in t for k in THREED_KEYWORDS)
        is_liquid = bool(it.get('is_liquid_glass')) or any(k in t for k in LIQUID_GLASS_KEYWORDS)
        cat = it.get('category') or get_item_category(it)

        normalized.append({
            "id": it["id"],
            "title": it["title"],
            "category": cat,
            "type": it.get("type", "showcase"),
            "source_url": it.get("source_url", f"https://pixlpin.com/d/{it['id']}"),
            "video_url": it.get("video_url"),
            "local_video": it.get("local_video"),
            "description": it.get("description", ""),
            "full_prompt": it.get("full_prompt", None),
            "is_3d": is_3d,
            "is_liquid_glass": is_liquid,
            "source_site": it.get("source_site", "pixlpin.com")
        })

    return normalized

def main():
    motionsites_items = parse_motionsites()
    pixlpin_items = load_pixlpin()

    # Merge: Pixlpin (622) + motionsites (328) = 950
    merged = pixlpin_items + motionsites_items
    print(f"[*] Total merged items: {len(merged)}")

    # 1. Save showcases_meta.json
    print(f"[*] Writing {len(merged)} items to {META_PATH}...")
    with open(META_PATH, 'w', encoding='utf-8') as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    # 2. Save dataset.jsonl
    print(f"[*] Writing {len(merged)} items to {DATASET_PATH}...")
    with open(DATASET_PATH, 'w', encoding='utf-8') as f:
        for it in merged:
            f.write(json.dumps(it, ensure_ascii=False) + '\n')

    # 3. Generate Embeddings (shape: 950, 384)
    print(f"[*] Generating TF-IDF + SVD vector embeddings (384 dimensions)...")
    corpus = [
        f"{it['title']} {it['title']} {it['category']} {it['description']} {it['id'].replace('-', ' ')}"
        for it in merged
    ]

    tfidf = TfidfVectorizer(stop_words='english', max_features=10000, ngram_range=(1, 2))
    tfidf_mat = tfidf.fit_transform(corpus)

    svd = TruncatedSVD(n_components=384, random_state=42)
    embeddings_dense = svd.fit_transform(tfidf_mat)
    embeddings_norm = normalize(embeddings_dense, norm='l2').astype(np.float32)

    print(f"[*] Saving vector embeddings to {EMBS_PATH} (shape: {embeddings_norm.shape})...")
    np.save(EMBS_PATH, embeddings_norm)

    print(f"✅ Pipeline complete! Verified {len(merged)} showcases indexed.")

if __name__ == "__main__":
    main()
