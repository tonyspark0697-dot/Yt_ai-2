"""Step 1: read what is trending on YouTube and extract viral hashtags / tags / titles."""
import math
import re
from collections import Counter

from googleapiclient.discovery import build

import config

HASH_RE = re.compile(r"#(\w{2,30})", re.UNICODE)
DUR_RE = re.compile(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?")


def _seconds(iso: str) -> int:
    h, m, s = DUR_RE.match(iso or "PT0S").groups()
    return int(h or 0) * 3600 + int(m or 0) * 60 + int(s or 0)


def fetch_trending(max_results: int = 50) -> list[dict]:
    yt = build("youtube", "v3", developerKey=config.YOUTUBE_API_KEY)
    resp = yt.videos().list(
        part="snippet,statistics,contentDetails",
        chart="mostPopular",
        regionCode=config.REGION,
        maxResults=max_results,
    ).execute()
    items = resp.get("items", [])
    if config.SHORTS:
        short = [i for i in items if _seconds(i["contentDetails"]["duration"]) <= 90]
        items = short or items  # mostPopular is mostly long videos; keep all if no shorts
    return items


def analyze(items: list[dict]) -> dict:
    """Weight every hashtag/tag by log10(views) so big hits count more."""
    hashtags, tags, cats = Counter(), Counter(), Counter()
    titles = []
    for it in items:
        sn = it["snippet"]
        views = int(it.get("statistics", {}).get("viewCount", 0) or 0)
        w = math.log10(views + 10)
        text = f"{sn.get('title', '')} {sn.get('description', '')}".lower()
        for h in set(HASH_RE.findall(text)):
            hashtags[h] += w
        for t in sn.get("tags", []) or []:
            tags[t.lower()] += w
        cats[sn.get("categoryId", "22")] += w
        titles.append({"title": sn.get("title", ""), "views": views})
    titles.sort(key=lambda t: t["views"], reverse=True)
    return {
        "top_hashtags": [h for h, _ in hashtags.most_common(15)],
        "top_tags": [t for t, _ in tags.most_common(25)],
        "top_category": cats.most_common(1)[0][0] if cats else "22",
        "top_titles": [t["title"] for t in titles[:15]],
    }


def get_trend_report() -> dict:
    return analyze(fetch_trending())
