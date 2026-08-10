#!/usr/bin/env python3
"""Generate Kujo SSG agent entries from Chain of Command AGENT.md files."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


RANK_ORDER = {
    "Strategic": 100,
    "Planning": 200,
    "Execution": 300,
    "Verification": 400,
    "Knowledge": 500,
    "Routine Worker": 600,
}


def field(body: str, name: str) -> str:
    match = re.search(rf"^- {re.escape(name)}:\s*(.+)$", body, re.MULTILINE)
    if not match:
        raise ValueError(f"missing {name}")
    return match.group(1).strip()


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: sync-agent-content.py /path/to/chain-of-command", file=sys.stderr)
        return 2

    source_root = Path(sys.argv[1]).expanduser().resolve()
    output_root = Path(__file__).resolve().parents[1] / "content" / "agents"
    if not source_root.is_dir():
        print(f"source directory not found: {source_root}", file=sys.stderr)
        return 2

    contracts = sorted(source_root.glob("*/AGENT.md"))
    if not contracts:
        print(f"no agent contracts found in: {source_root}", file=sys.stderr)
        return 1

    output_root.mkdir(parents=True, exist_ok=True)
    generated: set[Path] = set()
    rank_counts: dict[str, int] = {}

    for contract in contracts:
        body = contract.read_text(encoding="utf-8").strip()
        heading, _, remainder = body.partition("\n")
        if not heading.startswith("# "):
            raise ValueError(f"missing title heading: {contract}")

        title = heading[2:].strip()
        rank = field(body, "Rank/layer")
        purpose = field(body, "Purpose")
        model = field(body, "Best model tier")
        rank_counts[rank] = rank_counts.get(rank, 0) + 1
        order = RANK_ORDER.get(rank, 900) + rank_counts[rank]
        slug = contract.parent.name
        source_url = (
            "https://github.com/kujolang/kujo-agents/blob/main/"
            f"chain-of-command/{slug}/AGENT.md"
        )

        frontmatter = [
            "---",
            f"title: {json.dumps(title)}",
            f"custom_url: {json.dumps(slug)}",
            f"description: {json.dumps(purpose)}",
            f"excerpt: {json.dumps(purpose)}",
            f"seo_title: {json.dumps(title)}",
            f"seo_description: {json.dumps(purpose)}",
            f"keywords: {json.dumps('Kujo agent, ' + title + ', chain of command')}",
            f"featured_image: {json.dumps('assets/images/kujo-logomark.svg')}",
            f"tags: [{json.dumps(rank)}]",
            f"order: {order}",
            "---",
            "",
        ]
        source_note = (
            "\n\n## Source\n\n"
            f"[View the canonical {title} contract on GitHub]({source_url}).\n"
        )
        destination = output_root / f"{slug}.md"
        destination.write_text(
            "\n".join(frontmatter) + remainder.lstrip() + source_note,
            encoding="utf-8",
        )
        generated.add(destination)

    for existing in output_root.glob("*.md"):
        if existing not in generated:
            existing.unlink()

    print(f"Generated {len(generated)} agent entries in {output_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
