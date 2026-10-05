"""TECHi: RSS Headline Collector (source ZR-26-00741).

A Streamlit app: paste RSS/Atom feed URLs (tech-news defaults included),
fetch + parse them with feedparser, and browse the latest headlines in a
clean table with source, published time and link. Includes a keyword
filter and a refresh button.
"""

from __future__ import annotations

import os
import time
import urllib.request
from datetime import datetime, timezone

import feedparser
import streamlit as st

# ---------------------------------------------------------------------------
# Pure logic (import-safe: no Streamlit calls in here)
# ---------------------------------------------------------------------------

DEFAULT_FEEDS = """https://techcrunch.com/feed/
https://www.theverge.com/rss/index.xml
https://feeds.arstechnica.com/arstechnica/index
https://www.wired.com/feed/rss
https://hnrss.org/frontpage
https://www.technologyreview.com/feed/"""

FETCH_TIMEOUT = int(os.getenv("FETCH_TIMEOUT_SECONDS", "15"))  # seconds per feed


def parse_feed_urls(text: str) -> list[str]:
    urls: list[str] = []
    for line in (text or "").splitlines():
        url = line.strip()
        if url and url not in urls:
            urls.append(url)
    return urls


def download_bytes(url: str, timeout: int = FETCH_TIMEOUT) -> bytes:
    req = urllib.request.Request(
        url, headers={"User-Agent": "TECHi-RSS-Collector/1.0"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def entry_published(entry: dict) -> datetime | None:
    for key in ("published_parsed", "updated_parsed"):
        parsed = entry.get(key)
        if parsed:
            try:
                return datetime(*parsed[:6], tzinfo=timezone.utc)
            except (TypeError, ValueError):
                continue
    return None


def parse_feed(url: str, max_items: int = 10) -> tuple[str, list[dict], str | None]:
    """Fetch + parse one feed.

    Returns (source_title, items, error). Each item: title, link,
    published (datetime|None), source.
    """
    try:
        raw = download_bytes(url)
    except Exception as exc:  # network / HTTP / timeout errors
        return url, [], f"Download failed: {exc.__class__.__name__}: {exc}"
    try:
        feed = feedparser.parse(raw)
    except Exception as exc:
        return url, [], f"Parse failed: {exc.__class__.__name__}: {exc}"
    if getattr(feed, "bozo", False) and not feed.entries:
        reason = getattr(feed, "bozo_exception", "unknown error")
        return url, [], f"Feed invalid: {reason}"
    source = (feed.feed.get("title") or url).strip()
    items: list[dict] = []
    for entry in feed.entries[:max_items]:
        items.append(
            {
                "title": (entry.get("title") or "(no title)").strip(),
                "link": (entry.get("link") or "").strip(),
                "published": entry_published(entry),
                "source": source,
            }
        )
    return source, items, None


def collect_headlines(urls: list[str], max_items: int) -> tuple[list[dict], list[str]]:
    """Returns (items sorted newest-first, per-feed status lines)."""
    all_items: list[dict] = []
    status: list[str] = []
    for url in urls:
        source, items, error = parse_feed(url, max_items)
        if error:
            status.append(f"❌ {url} — {error}")
        else:
            status.append(f"✅ {source} — {len(items)} headlines")
            all_items.extend(items)
    all_items.sort(
        key=lambda i: i["published"] or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )
    return all_items, status


def filter_by_keyword(items: list[dict], keyword: str) -> list[dict]:
    kw = (keyword or "").strip().lower()
    if not kw:
        return items
    return [i for i in items if kw in i["title"].lower()]
