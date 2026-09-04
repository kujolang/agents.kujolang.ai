#!/usr/bin/env python3
"""Generate Howl's deterministic social-card manifest from agent content."""
from __future__ import annotations

import json
import re
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENTS_DIR = ROOT / "content/agents"
FONT = "assets/sitekit/fonts/DepartureMono-Regular.woff2"
HERO = "assets/images/agent-hero-background.webp"


def frontmatter(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---(?:\n|\Z)", text, re.DOTALL)
    if not match:
        raise ValueError(f"missing frontmatter: {path}")

    values: dict[str, object] = {}
    for line in match.group(1).splitlines():
        key, separator, raw = line.partition(":")
        if not separator:
            continue
        raw = raw.strip()
        try:
            values[key.strip()] = json.loads(raw)
        except json.JSONDecodeError:
            values[key.strip()] = raw
    return values


def card(
    card_id: str,
    title: str,
    tagline: str,
    label: str,
    file_path: str,
    background: str = HERO,
) -> dict[str, object]:
    return {
        "id": card_id,
        "title": title,
        "tagline": tagline,
        "file": file_path,
        "variant": "social",
        "label": label,
        "background_image": background,
        "font_file": FONT,
        "show_border": True,
        "show_url": False,
    }


def main() -> int:
    cards = [
        card(
            "home",
            "Kujo Agents",
            "Source-grounded agent systems for ambitious software teams.",
            "Agent systems",
            "README.md",
        ),
        card(
            "agents",
            "Agent Directory",
            "Specialized contracts for planning, building, verifying, and operating.",
            "Agent library",
            "README.md",
        ),
        card(
            "agents-chain-of-command",
            "Chain of Command",
            "A coordinated roster for strategy, execution, verification, and knowledge.",
            "Agent set",
            "README.md",
        ),
        card(
            "agents-webops",
            "WebOps",
            "A coordinated roster for search, content intelligence, and site quality.",
            "Agent set",
            "README.md",
        ),
        card(
            "agents-publishing-house",
            "Publishing House",
            "A standalone editorial roster for strategy, writing, review, and production.",
            "Agent set",
            "README.md",
        ),
        card(
            "agents-videoops",
            "VideoOps",
            "A five-stage production line for planned, evidenced, and independently reviewed video.",
            "Agent set",
            "README.md",
        ),
        card(
            "publishing-house-system",
            "Publishing House System",
            "23 agents, 8 record owners, 11 workflows, and 11 operator skills.",
            "Editorial operating system",
            "content/pages/publishing-house-system.md",
            "assets/images/publishing-house-system.webp",
        ),
        card(
            "agent-development-platform",
            "Build Your Own Kujo Agent",
            "One focused install. One owned project. A working agent you can talk to.",
            "Agent Development Platform",
            "content/pages/agent-development-platform.md",
            "assets/images/agent-development-platform.webp",
        ),
        card(
            "404",
            "Signal Lost",
            "This route is outside the active agent network.",
            "404",
            "README.md",
        ),
    ]

    for path in sorted(AGENTS_DIR.glob("*.md")):
        meta = frontmatter(path)
        slug = str(meta.get("custom_url", path.stem))
        title = str(meta.get("title", path.stem.replace("-", " ").title()))
        tagline = textwrap.shorten(
            str(meta.get("description", "A specialized Kujo agent contract.")),
            width=68,
            placeholder="…",
        )
        categories = meta.get("categories", [])
        label = str(categories[0]) if isinstance(categories, list) and categories else "Kujo agent"
        background = str(meta.get("featured_image", HERO))
        if background.endswith(".svg"):
            background = HERO
        cards.append(card(slug, title, tagline, label, path.relative_to(ROOT).as_posix(), background))

    manifest = {
        "project": {
            "name": "Kujo Agents",
            "tagline": "Source-grounded agent systems for ambitious software teams.",
            "url": "",
        },
        "theme": {"name": "minimal", "mode": "light"},
        "cards": cards,
    }
    (ROOT / "howl.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Generated howl.json with {len(cards)} social cards")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
