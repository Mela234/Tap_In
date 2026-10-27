import html
import re
from calendar import timegm
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

import feedparser
import httpx

from app.news.feeds import FEEDS

USER_AGENT = "Mozilla/5.0 (compatible; TapIn/1.0; +https://tapinpointo.netlify.app)"
MAX_AGE = timedelta(hours=48)
SUMMARY_CHARS = 400


@dataclass
class Article:
    topic: str
    source: str
    title: str
    summary: str
    url: str
    published: Optional[datetime]


def _clean(text: str) -> str:
    """Strip HTML tags and collapse whitespace from a feed snippet."""
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def _published(entry) -> Optional[datetime]:
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if not parsed:
        return None
    return datetime.fromtimestamp(timegm(parsed), tz=timezone.utc)


def _fetch_feed(topic: str, source: str, url: str) -> list[Article]:
    try:
        response = httpx.get(url, headers={"User-Agent": USER_AGENT}, timeout=15, follow_redirects=True)
        response.raise_for_status()
    except httpx.HTTPError as e:
        print(f"  ⚠️  {source} ({topic}) skipped: {e}")
        return []

    feed = feedparser.parse(response.content)
    cutoff = datetime.now(timezone.utc) - MAX_AGE
    articles = []

    for entry in feed.entries:
        title = _clean(entry.get("title", ""))
        link = entry.get("link", "")
        if not title or not link:
            continue

        published = _published(entry)
        if published and published < cutoff:
            continue

        articles.append(
            Article(
                topic=topic,
                source=source,
                title=title,
                summary=_clean(entry.get("summary", ""))[:SUMMARY_CHARS],
                url=link,
                published=published,
            )
        )

    print(f"  📰 {source} ({topic}): {len(articles)} recent stories")
    return articles


def collect_articles() -> list[Article]:
    """Fetch every configured feed in parallel and return the recent articles."""
    jobs = [(topic, source, url) for topic, feeds in FEEDS.items() for source, url in feeds]

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = pool.map(lambda job: _fetch_feed(*job), jobs)

    return [article for batch in results for article in batch]
