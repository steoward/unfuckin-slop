import os
import re
import json
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SHOWCASE_DIR = os.path.join(BASE_DIR, "design_showcases")
VIDEOS_DIR = os.path.join(SHOWCASE_DIR, "videos")
CACHE_DIR = os.path.join(BASE_DIR, ".slop-cache")
METADATA_FILE = os.path.join(CACHE_DIR, "pixlpin-scrape.jsonl")

os.makedirs(VIDEOS_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
}

def fetch_url(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=12) as resp:
            return resp.read()
    except Exception:
        return None

def download_file(url, target_path):
    if os.path.exists(target_path) and os.path.getsize(target_path) > 1000:
        return True
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=20) as resp:
            with open(target_path, "wb") as f:
                f.write(resp.read())
        return True
    except Exception:
        return False

def collect_multi_category_slugs(max_categories=25, target_items=200):
    print(f"[*] Discovering category feeds from Pixlpin sitemap...")
    sitemap_html = fetch_url("https://pixlpin.com/sitemap")
    if not sitemap_html:
        return []
    soup = BeautifulSoup(sitemap_html, "html.parser")
    cat_links = [a["href"] for a in soup.find_all("a", href=True) if a["href"].startswith("/designs/")]
    print(f"[*] Found {len(cat_links)} categories. Crawling up to {max_categories} feeds for {target_items} items...")
    
    slugs = set()
    for idx, c in enumerate(cat_links[:max_categories], 1):
        if len(slugs) >= target_items:
            break
        c_html = fetch_url(f"https://pixlpin.com{c}")
        if not c_html:
            continue
        c_soup = BeautifulSoup(c_html, "html.parser")
        for a in c_soup.find_all("a", href=True):
            href = a["href"]
            if href.startswith("/d/"):
                slugs.add(href)
        print(f"  [Feed {idx}/{max_categories}] {c} -> {len(slugs)} unique designs collected so far.")
        
    return list(slugs)[:target_items]

def process_item(slug):
    detail_url = f"https://pixlpin.com{slug}"
    html = fetch_url(detail_url)
    if not html:
        return None
    soup = BeautifulSoup(html, "html.parser")
    raw_slug = slug.replace("/d/", "").strip()
    title_el = soup.find("title")
    title = title_el.get_text(strip=True) if title_el else raw_slug.replace("-", " ").title()
    title = re.sub(r"\s+by\s+.*$", "", title).strip()
    meta_desc = soup.find("meta", {"name": "description"})
    desc = meta_desc["content"].strip() if meta_desc and "content" in meta_desc.attrs else f"Fluid interactive UI motion design showcasing {title}."
    
    video_url = None
    for v in soup.find_all("video"):
        src = v.get("src") or [s.get("src") for s in v.find_all("source") if s.get("src")]
        if src:
            video_url = src[0] if isinstance(src, list) else src
            break
            
    if not video_url:
        return None
        
    v_filename = f"{raw_slug}.mp4"
    v_dest = os.path.join(VIDEOS_DIR, v_filename)
    download_file(video_url, v_dest)
    
    return {
        "id": raw_slug,
        "title": title,
        "description": desc,
        "video_url": video_url,
        "local_video": f"videos/{v_filename}",
        "source_site": "pixlpin.com",
        "source_url": detail_url
    }

def main():
    slugs = collect_multi_category_slugs(max_categories=20, target_items=150)
    print(f"[*] Ingesting {len(slugs)} showcases using 12 parallel threads...")
    
    # Load existing
    existing_ids = set()
    records = []
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        r = json.loads(line)
                        existing_ids.add(r["id"])
                        records.append(r)
                    except Exception:
                        pass

    to_fetch = [s for s in slugs if s.replace("/d/", "").strip() not in existing_ids]
    print(f"[*] Already have {len(existing_ids)} cached. Fetching {len(to_fetch)} new showcases...")
    
    with ThreadPoolExecutor(max_workers=12) as pool:
        futures = [pool.submit(process_item, s) for s in to_fetch]
        for f in as_completed(futures):
            res = f.result()
            if res:
                records.append(res)
                
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            
    print(f"\n[+] Total showcases now indexed: {len(records)}")
    print(f"[+] Total videos in {VIDEOS_DIR}: {len(os.listdir(VIDEOS_DIR))}")

if __name__ == "__main__":
    main()
