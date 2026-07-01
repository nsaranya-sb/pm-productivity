"""Generates a competitor analysis using Claude with web search, saved to output/."""

import os
from datetime import datetime, timezone
from pathlib import Path

import anthropic

MODEL = "claude-sonnet-4-6"
SYSTEM_PROMPT_PATH = Path(__file__).parent / "prompts" / "competitor_system_prompt.md"
OUTPUT_DIR = Path(__file__).parent / "output"


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


def generate_competitor_analysis(company: str, market: str) -> Path:
    _load_env()

    system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    client = anthropic.Anthropic()

    user_message = f"Company: {company}\nMarket: {market}"
    print(f"Analysing {company} in '{market}'...\n")

    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=system_prompt,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": user_message}],
    )

    text = "\n".join(
        block.text for block in response.content if block.type == "text"
    )

    print(text)

    OUTPUT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_path = OUTPUT_DIR / f"competitor_{timestamp}.md"
    out_path.write_text(text, encoding="utf-8")

    print(f"\nAnalysis saved to {out_path}")
    return out_path


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 3:
        company_arg, market_arg = sys.argv[1], sys.argv[2]
    else:
        company_arg = "Notion"
        market_arg = "PM productivity tools"

    generate_competitor_analysis(company_arg, market_arg)
