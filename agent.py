"""
AI Stock Research Agent for Super Investing
============================================
Reads a research_pack/ of documents about an NSE-listed company
and produces a structured research brief using Groq.

Usage:
    python agent.py --ticker SRVCABLE --pack research_pack/ --date "23 September 2026"

Requires GROQ_API_KEY environment variable.
"""

import argparse
import os
import sys
import glob

sys.stdout.reconfigure(encoding='utf-8')

from groq import Groq


def load_system_prompt(path: str = "system_prompt.md") -> str:
    """Load the system prompt from a markdown file."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def load_research_pack(pack_dir: str) -> list[dict]:
    """
    Load all .md files from the research pack directory.
    Returns a list of dicts with 'filename', 'content', and parsed metadata.
    """
    documents = []
    md_files = sorted(glob.glob(os.path.join(pack_dir, "*.md")))

    if not md_files:
        print(f"Error: No .md files found in '{pack_dir}'")
        sys.exit(1)

    for filepath in md_files:
        filename = os.path.basename(filepath)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse YAML-like frontmatter for metadata
        metadata = {}
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                for line in parts[1].strip().split("\n"):
                    if ":" in line:
                        key, val = line.split(":", 1)
                        metadata[key.strip()] = val.strip()

        documents.append({
            "filename": filename,
            "content": content,
            "source": metadata.get("source", "Unknown"),
            "url": metadata.get("url", ""),
            "published": metadata.get("published", "Unknown"),
            "type": metadata.get("type", "Unknown"),
        })

    return documents


def build_user_prompt(ticker: str, today: str, documents: list[dict]) -> str:
    """
    Build the user prompt containing the ticker, date, and all documents.
    """
    doc_sections = []
    for i, doc in enumerate(documents, 1):
        doc_sections.append(
            f"### Document {i}: {doc['filename']}\n"
            f"- **Source:** {doc['source']}\n"
            f"- **URL:** {doc['url']}\n"
            f"- **Published:** {doc['published']}\n"
            f"- **Type:** {doc['type']}\n\n"
            f"```\n{doc['content']}\n```\n"
        )

    documents_text = "\n---\n\n".join(doc_sections)

    return (
        f"## Research Request\n\n"
        f"**NSE Ticker:** {ticker}\n"
        f"**Today's Date:** {today}\n"
        f"**Number of documents:** {len(documents)}\n\n"
        f"Please analyze the following documents and produce a research brief.\n\n"
        f"---\n\n"
        f"{documents_text}"
    )


def run_agent(ticker: str, pack_dir: str, today: str, model_name: str = "openai/gpt-oss-120b") -> str:
    """
    Run the research agent pipeline:
    1. Load system prompt
    2. Load and parse all documents
    3. Send to Groq LLM with structured prompts
    4. Return the generated research brief
    """
    # Configure API
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("Error: GROQ_API_KEY environment variable not set.")
        print("Get a free key at: https://console.groq.com/keys")
        sys.exit(1)

    client = Groq(api_key=api_key)

    # Phase 1: Ingest
    print(f"[Phase 1] Loading documents from '{pack_dir}'...")
    documents = load_research_pack(pack_dir)
    print(f"  Loaded {len(documents)} documents:")
    for doc in documents:
        print(f"    - {doc['filename']} ({doc['type']}, {doc['published']})")

    # Phase 2 & 3: Analyze + Synthesize
    print(f"\n[Phase 2-3] Analyzing and synthesizing with {model_name}...")
    system_prompt = load_system_prompt()
    user_prompt = build_user_prompt(ticker, today, documents)

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,  # Low temperature for factual accuracy
        max_tokens=2048,
    )

    brief = response.choices[0].message.content
    print(f"\n[Done] Generated brief ({len(brief)} characters)")
    return brief


def main():
    parser = argparse.ArgumentParser(
        description="AI Stock Research Agent — generates research briefs from document packs"
    )
    parser.add_argument(
        "--ticker", required=True,
        help="NSE ticker symbol (e.g. SRVCABLE)"
    )
    parser.add_argument(
        "--pack", required=True,
        help="Path to the research_pack directory containing .md files"
    )
    parser.add_argument(
        "--date", default="23 September 2026",
        help="Today's date for the brief (default: '23 September 2026')"
    )
    parser.add_argument(
        "--model", default="openai/gpt-oss-120b",
        help="Groq model name (default: openai/gpt-oss-120b)"
    )
    parser.add_argument(
        "--output", default=None,
        help="Output file path (default: output/<ticker>_brief.md)"
    )

    args = parser.parse_args()

    # Run the agent
    brief = run_agent(args.ticker, args.pack, args.date, args.model)

    # Save output
    output_path = args.output or os.path.join("output", f"{args.ticker.lower()}_brief.md")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(brief)

    print(f"\nBrief saved to: {output_path}")
    print("\n" + "=" * 60)
    print(brief)
    print("=" * 60)


if __name__ == "__main__":
    main()
