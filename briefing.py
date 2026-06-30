"""Orchestrator — fetches RSS articles, summarises them, and writes a daily briefing."""

import os
from datetime import datetime, timezone
from pathlib import Path


def _load_env() -> None:
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


_load_env()

from rss_poller import fetch_articles
from summariser import summarise
from curator import curate

BRIEFINGS_DIR = Path(__file__).parent / "briefings"


def _render_markdown(articles: list[dict]) -> str:
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [f"# PM Daily Briefing — {date_str}\n"]

    if not articles:
        lines.append("_No articles found in the last 24 hours._\n")
        return "\n".join(lines)

    by_source: dict[str, list[dict]] = {}
    for a in articles:
        by_source.setdefault(a["source"], []).append(a)

    for source, items in by_source.items():
        lines.append(f"## {source}\n")
        for a in items:
            lines.append(f"### [{a['title']}]({a['url']})")
            lines.append(f"_Published: {a['published_date']}_\n")
            lines.append(a.get("claude_summary", "_No summary available._"))
            lines.append("")

    return "\n".join(lines)


def run() -> Path:
    print("Step 1/2: Fetching RSS articles...")
    articles = fetch_articles()
    print(f"  {len(articles)} article(s) fetched.\n")

    print("Step 2/3: Summarising articles...")
    enriched = summarise(articles)

    print("\nStep 3/3: Curating and ranking...")
    enriched = curate(enriched)

    BRIEFINGS_DIR.mkdir(exist_ok=True)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out_path = BRIEFINGS_DIR / f"{date_str}.md"
    out_path.write_text(_render_markdown(enriched), encoding="utf-8")

    print(f"\nBriefing written to {out_path}")
    return out_path


if __name__ == "__main__":
    run()
