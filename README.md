# AI Stock Research Agent

An AI-powered research agent that reads a pack of documents about an NSE-listed company and produces a structured, one-page research brief for retail investors.

## How to Run

### Prerequisites
- Python 3.10+
- A [Groq API key](https://console.groq.com/keys) (free tier is sufficient)

### Setup

```bash
pip install -r requirements.txt
export GROQ_API_KEY="your-key-here"        # Linux/Mac
$env:GROQ_API_KEY="your-key-here"          # Windows PowerShell
```

### Run the agent

```bash
python agent.py --ticker SRVCABLE --pack research_pack/ --date "23 September 2026"
```

### Options

| Flag | Default | Description |
|---|---|---|
| `--ticker` | (required) | NSE ticker symbol |
| `--pack` | (required) | Path to folder of `.md` research documents |
| `--date` | `23 September 2026` | Assumed "today" date for the brief |
| `--model` | `openai/gpt-oss-120b` | Groq model to use |
| `--output` | `output/<ticker>_brief.md` | Output file path |

## Model Choice

**Primary:** `openai/gpt-oss-120b` via Groq — chosen for:
- Strong reasoning and analytical depth
- Good at cross-referencing conflicting data
- Catches entity confusion and manipulation attempts reliably
- Free via Groq's API

**Tested also:** `qwen/qwen3.8-27b` — faster but less nuanced analysis.

## Architecture

Simple **3-phase pipeline** (no heavy frameworks):

1. **Ingest** — Reads all `.md` files, parses YAML frontmatter for metadata (source, URL, date, type)
2. **Analyze + Synthesize** — Sends all documents + structured system prompt to LLM
3. **Output** — Saves the Markdown brief to disk

### Design Decisions

- **System prompt as separate file** (`system_prompt.md`) — easy to iterate without touching code
- **Low temperature (0.3)** — prioritizes factual accuracy over creativity
- **Source tiering** — the prompt instructs the LLM to weight official filings > news > blogs
- **Anti-manipulation** — explicit instructions to ignore embedded prompt injections
- **Entity verification** — instructions to verify each document is about the correct company

## Files

| File | Purpose |
|---|---|
| `agent.py` | Main agent script |
| `system_prompt.md` | System prompt (separate file) |
| `requirements.txt` | Python dependencies |
| `test_log.md` | 3 test runs with changes documented |
| `output/` | Generated research briefs |
