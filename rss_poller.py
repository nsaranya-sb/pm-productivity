import json
import feedparser
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path

FEEDS = [
    {"source": "Mind the Product", "url": "https://www.mindtheproduct.com/feed/"},
    {"source": "Lenny's Newsletter", "url": "https://www.lennysnewsletter.com/feed"},
    {"source": "Stratechery", "url": "https://stratechery.com/feed/"},
    {"source": "Benedict Evans", "url": "https://www.ben-evans.com/benedictevans?format=rss"},
    {"source": "The Pragmatic Engineer", "url": "https://newsletter.pragmaticengineer.com/feed"},
]

LOOKBACK_HOURS = 24
SEEN_URLS_FILE = Path(__file__).parent / ".seen_urls.json"


def _load_seen() -> set[str]:
    if SEEN_URLS_FILE.exists():
        return set(json.loads(SEEN_URLS_FILE.read_text()))
    return set()


def _save_seen(seen: set[str]) -> None:
    SEEN_URLS_FILE.write_text(json.dumps(sorted(seen)))


def _parse_date(entry) -> datetime | None:
    for field in ("published", "updated"):
        raw = entry.get(field)
        if raw:
            try:
                return parsedate_to_datetime(raw).astimezone(timezone.utc)
            except Exception:
                pass
    if entry.get("published_parsed"):
        return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
    return None


def fetch_articles() -> list[dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=LOOKBACK_HOURS)
    seen = _load_seen()
    articles = []
    new_urls: set[str] = set()

    for feed_meta in FEEDS:
        source = feed_meta["source"]
        feed = feedparser.parse(feed_meta["url"])
        count = 0

        for entry in feed.entries:
            pub_date = _parse_date(entry)
            if pub_date is None or pub_date < cutoff:
                continue

            url = entry.get("link", "")
            if url in seen:
                continue

            articles.append({
                "title": entry.get("title", "").strip(),
                "url": url,
                "summary": entry.get("summary", "").strip(),
                "source": source,
                "published_date": pub_date.isoformat(),
            })
            new_urls.add(url)
            count += 1

        print(f"{source}: {count} new article(s) in the last {LOOKBACK_HOURS}h")

    _save_seen(seen | new_urls)
    return articles


if __name__ == "__main__":
    articles = fetch_articles()
    print(f"\nTotal: {len(articles)} article(s) found across all sources")
