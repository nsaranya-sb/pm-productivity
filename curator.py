"""Ranks and filters summarised articles by PM relevance using a single LLM call."""

import json
import anthropic

MODEL = "claude-haiku-4-5"

SYSTEM_PROMPT = (
    "You are a research assistant for a senior product manager. "
    "You will be given a list of articles (as JSON). "
    "Score each article 1–10 for relevance to a senior PM (strategy, market signals, "
    "product craft, tech trends, leadership). "
    "Return ONLY a JSON array of objects with keys 'index' (0-based) and 'score'. "
    "No explanation, no markdown fences."
)

_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic()
    return _client


def _score_articles(articles: list[dict]) -> list[int]:
    payload = [
        {"index": i, "title": a["title"], "source": a["source"], "summary": a.get("claude_summary", a.get("summary", ""))}
        for i, a in enumerate(articles)
    ]
    response = _get_client().messages.create(
        model=MODEL,
        max_tokens=256,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": json.dumps(payload)}],
    )
    text = next(b.text for b in response.content if b.type == "text")
    # strip markdown fences if the model wraps its output
    text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    scores_raw: list[dict] = json.loads(text)
    score_map = {item["index"]: item["score"] for item in scores_raw}
    return [score_map.get(i, 0) for i in range(len(articles))]


def curate(articles: list[dict], min_score: int = 6) -> list[dict]:
    """Return articles filtered to min_score and sorted by score descending."""
    if not articles:
        return []

    print(f"Curating {len(articles)} article(s)...")
    scores = _score_articles(articles)

    ranked = sorted(
        [{"score": s, **a} for s, a in zip(scores, articles)],
        key=lambda x: x["score"],
        reverse=True,
    )
    kept = [a for a in ranked if a["score"] >= min_score]
    print(f"  {len(kept)}/{len(articles)} article(s) passed relevance filter (score ≥ {min_score}).")
    return kept
