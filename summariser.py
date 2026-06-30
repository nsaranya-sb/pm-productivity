import anthropic

MODEL = "claude-haiku-4-5"

SYSTEM_PROMPT = (
    "You are a research assistant for a senior product manager. "
    "Summarise the article below in 3–5 bullet points. Focus on: "
    "strategic implications, market signals, and actionable takeaways for a PM. "
    "Be concise and specific. Output only the bullet points, no preamble."
)

_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic()
    return _client


def _summarise_article(article: dict) -> str:
    content = f"Title: {article['title']}\nSource: {article['source']}\n\n{article['summary']}"
    client = _get_client()
    with client.messages.stream(
        model=MODEL,
        max_tokens=512,
system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": content}],
    ) as stream:
        return stream.get_final_message().content[-1].text


def summarise(articles: list[dict]) -> list[dict]:
    """Return articles enriched with a `claude_summary` field."""
    enriched = []
    for i, article in enumerate(articles, 1):
        print(f"[{i}/{len(articles)}] Summarising: {article['title'][:60]}")
        try:
            summary = _summarise_article(article)
        except Exception as e:
            print(f"  ERROR: {e}")
            summary = ""
        enriched.append({**article, "claude_summary": summary})
    return enriched


if __name__ == "__main__":
    from rss_poller import fetch_articles

    articles = fetch_articles()
    if not articles:
        print("No articles found in the last 24 hours.")
    else:
        results = summarise(articles)
        for r in results:
            print(f"\n{'='*60}")
            print(f"[{r['source']}] {r['title']}")
            print(f"URL: {r['url']}")
            print(r["claude_summary"])
