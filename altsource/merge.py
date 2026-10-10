"""Merge several AltStore/SideStore sources into one source.json.

Each source's last good copy is kept in cache/, so a source that is down
during a build keeps its apps instead of dropping them.
"""
import hashlib
import json
import os
import sys
import urllib.request

OWNER = "benwilllopez"
REPO = "altsource"

SOURCE_INFO = {
    "name": "Ben's Merged Source",
    "identifier": f"io.github.{OWNER}.{REPO}",
    "subtitle": "Many sources, one link.",
    "sourceURL": f"https://raw.githubusercontent.com/{OWNER}/{REPO}/main/source.json",
    "website": f"https://github.com/{OWNER}/{REPO}",
    "tintColor": "#5B6CFF",
}

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache")


def read_urls():
    with open(os.path.join(HERE, "sources.txt")) as f:
        return [l.strip() for l in f if l.strip() and not l.lstrip().startswith("#")]


def cache_path(url):
    return os.path.join(CACHE, hashlib.sha1(url.encode()).hexdigest()[:16] + ".json")


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 altsource-merge"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.loads(r.read().decode("utf-8-sig"))
    if not isinstance(data, dict) or not isinstance(data.get("apps"), list):
        raise ValueError("not an AltStore source (no apps list)")
    return data


def load(url):
    path = cache_path(url)
    try:
        data = fetch(url)
        with open(path, "w") as f:
            json.dump(data, f)
        return data, "ok"
    except Exception as e:
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f), f"cached ({type(e).__name__})"
        return None, f"FAILED ({type(e).__name__}: {e})"


def main():
    os.makedirs(CACHE, exist_ok=True)
    urls = read_urls()
    apps, news, seen_apps, seen_news = [], [], set(), set()
    loaded = 0

    for url in urls:
        data, status = load(url)
        added = 0
        if data:
            loaded += 1
            for app in data.get("apps", []):
                bid = app.get("bundleIdentifier") if isinstance(app, dict) else None
                if bid and bid not in seen_apps:
                    seen_apps.add(bid)
                    apps.append(app)
                    added += 1
            for item in data.get("news", []) or []:
                nid = item.get("identifier") if isinstance(item, dict) else None
                if nid and nid not in seen_news:
                    seen_news.add(nid)
                    news.append(item)
        print(f"{status:<12} +{added:<5} {url}")

    if not apps:
        sys.exit("No apps loaded; keeping the existing source.json.")

    out = dict(SOURCE_INFO, apps=apps, news=news)
    with open(os.path.join(HERE, "source.json"), "w") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    print(f"\n{len(apps)} unique apps from {loaded}/{len(urls)} sources")


if __name__ == "__main__":
    main()
