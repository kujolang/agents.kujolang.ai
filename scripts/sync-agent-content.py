#!/usr/bin/env python3
"""Generate Kujo SSG agent entries from Chain of Command AGENT.md files."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


DEMO_ORDER = [
    "general-commander",
    "chief-of-staff",
    "systems-architect",
    "product-strategist",
    "planner",
    "spec-writer",
    "research-analyst",
    "risk-officer",
    "core-developer",
    "tooling-developer",
    "frontend-developer",
    "backend-developer",
    "integration-engineer",
    "code-reviewer",
    "qa-lead",
    "triage-agent",
    "visual-qa-agent",
    "release-verifier",
    "security-reviewer",
    "archivist",
    "documentation-writer",
    "context-packager",
    "sitrep-agent",
    "routine-worker",
    "test-runner",
    "lint-runner",
    "issue-hygiene-worker",
    "dependency-scanner",
    "receipt-collector",
]

ORDER_BY_SLUG = {slug: index for index, slug in enumerate(DEMO_ORDER, start=1)}

AGENT_IMAGES = {
    "general-commander": "content/media/agents/general-commander.png",
    "chief-of-staff": "content/media/agents/chief-of-staff.png",
    "systems-architect": "content/media/agents/systems-architect.png",
    "product-strategist": "content/media/agents/product-strategist.png",
    "planner": "content/media/agents/planner.png",
    "spec-writer": "content/media/agents/spec-writer.png",
    "research-analyst": "content/media/agents/research-analyst.jpg",
    "risk-officer": "content/media/agents/risk-officer.jpg",
    "core-developer": "content/media/agents/core-developer.jpg",
    "tooling-developer": "content/media/agents/tooling-developer.jpg",
    "frontend-developer": "content/media/agents/frontend-developer.jpg",
    "backend-developer": "content/media/agents/backend-developer.jpg",
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
    for contract in contracts:
        body = contract.read_text(encoding="utf-8").strip()
        heading, _, remainder = body.partition("\n")
        if not heading.startswith("# "):
            raise ValueError(f"missing title heading: {contract}")

        title = heading[2:].strip()
        rank = field(body, "Rank/layer")
        purpose = field(body, "Purpose")
        model = field(body, "Best model tier")
        slug = contract.parent.name
        order = ORDER_BY_SLUG.get(slug, 1000)
        featured_image = AGENT_IMAGES.get(slug, "assets/images/kujo-logomark.svg")
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
            f"featured_image: {json.dumps(featured_image)}",
            f"categories: [{json.dumps('Chain of Command')}]",
            f"tags: [{json.dumps(rank)}]",
            f"order: {order}",
            "last_updated: 2026-08-10",
            f"source_url: {json.dumps(source_url)}",
            "---",
            "",
        ]
        remainder = re.sub(
            r"(^- Required KUJO skills:\s*)(.+)$",
            lambda match: match.group(1) + match.group(2).replace("`", ""),
            remainder,
            flags=re.MULTILINE,
        )
        destination = output_root / f"{slug}.md"
        destination.write_text(
            "\n".join(frontmatter) + remainder.lstrip() + "\n",
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
