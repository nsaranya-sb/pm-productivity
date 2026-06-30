# PM Productivity Suite

A lightweight Python tool that generates a daily AI-curated briefing from product management RSS feeds.

Every run fetches the last 24 hours of articles, summarises each one with Claude, scores them for PM relevance, and writes a clean Markdown briefing to `briefings/`.

## How it works

```
rss_poller.py  →  summariser.py  →  curator.py  →  briefings/YYYY-MM-DD.md
```

| Module | Role |
|---|---|
| `rss_poller.py` | Fetches 5 RSS feeds, filters to articles from the last 24 hours |
| `summariser.py` | Calls Claude to produce 3–5 PM-focused bullet points per article |
| `curator.py` | Scores all articles 1–10 for PM relevance in a single LLM call, drops anything below 6, sorts by score |
| `briefing.py` | Orchestrates the pipeline and writes the output Markdown file |

## Feeds

- Mind the Product
- Lenny's Newsletter
- Stratechery
- Benedict Evans
- The Pragmatic Engineer

## Setup

**1. Clone and create a virtual environment**

```bash
git clone <repo-url>
cd pm-productivity
python3 -m venv .venv
source .venv/bin/activate
pip install feedparser anthropic
```

**2. Add your Anthropic API key**

Create a `.env` file in the project root (it's gitignored):

```
ANTHROPIC_API_KEY=sk-ant-...
```

Get a key at [console.anthropic.com](https://console.anthropic.com).

## Usage

```bash
.venv/bin/python briefing.py
```

Output is written to `briefings/YYYY-MM-DD.md`.

## Automate with cron

To run every morning at 7am:

```
0 7 * * * cd /path/to/pm-productivity && .venv/bin/python briefing.py
```
