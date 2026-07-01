"""Generates a PRD from a problem statement using Claude, saved to output/."""

import os
from datetime import datetime, timezone
from pathlib import Path

import anthropic

MODEL = "claude-sonnet-4-6"
SYSTEM_PROMPT_PATH = Path(__file__).parent / "prompts" / "prd_system_prompt.md"
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


def generate_prd(problem_statement: str) -> Path:
    _load_env()

    system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    client = anthropic.Anthropic()

    print(f"Generating PRD for: {problem_statement}\n")

    prd_text = ""
    with client.messages.stream(
        model=MODEL,
        max_tokens=4096,
        thinking={"type": "adaptive"},
        system=system_prompt,
        messages=[{"role": "user", "content": problem_statement}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            prd_text += text

    OUTPUT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_path = OUTPUT_DIR / f"prd_{timestamp}.md"
    out_path.write_text(prd_text, encoding="utf-8")

    print(f"\n\nPRD saved to {out_path}")
    return out_path


if __name__ == "__main__":
    import sys

    problem = (
        " ".join(sys.argv[1:])
        if len(sys.argv) > 1
        else "PMs need a faster way to assess job fit without reading full JDs manually"
    )
    generate_prd(problem)
