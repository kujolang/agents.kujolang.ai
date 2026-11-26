#!/usr/bin/env python3
"""Safely synchronize multiple canonical kujo-agents sets into Kujo SSG."""
from __future__ import annotations
import argparse
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode, urlsplit

SITE_ROOT=Path(__file__).resolve().parents[1]
OUTPUT_ROOT=SITE_ROOT/"content/agents"
STATE_PATH=OUTPUT_ROOT/".sync-state.json"
STATE_SCHEMA = "agents-site.sync-state/v1"
SLUG_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
CHAIN_ORDER=["general-commander","chief-of-staff","systems-architect","product-strategist","planner","spec-writer","research-analyst","risk-officer","core-developer","tooling-developer","frontend-developer","backend-developer","integration-engineer","code-reviewer","qa-lead","triage-agent","visual-qa-agent","release-verifier","security-reviewer","documentation-writer","context-packager","sitrep-agent","routine-worker","test-runner","lint-runner","issue-hygiene-worker","dependency-scanner","receipt-collector"]
SETS={
  "chain-of-command":{"source":"chain-of-command","category":"Chain of Command","tag_field":"Rank/layer","keywords":"Kujo agent, chain of command","order":CHAIN_ORDER,"catalog":None,"public_prefix":""},
  "webops":{"source":"webops","category":"WebOps","tag_field":"Category","keywords":"Kujo agent, WebOps, website operations","order":None,"catalog":"webops-catalog.json","public_prefix":""},
  "publishing-house":{"source":"publishing-house","category":"Publishing House","tag_field":"Desk","keywords":"Kujo agent, Publishing House, editorial operations","order":None,"catalog":"publishing-house-catalog.json","public_prefix":""},
  "videoops":{"source":"videoops","category":"VideoOps","tag_field":"Stage","keywords":"Kujo agent, VideoOps, video production","order":None,"catalog":"videoops-catalog.json","public_prefix":"videoops-"},
}
def field(body:str,name:str)->str:
    match=re.search(rf"^- {re.escape(name)}:\s*(.+)$",body,re.MULTILINE)
    if not match: raise ValueError(f"missing {name}")
    return match.group(1).strip()

def updated_date(repo:Path,contract:Path)->str:
    try:
        rel=contract.relative_to(repo)
        result=subprocess.run(["git","-C",str(repo),"log","-1","--format=%cs","--",str(rel)],text=True,capture_output=True,timeout=10)
        if result.returncode==0 and re.fullmatch(r"\d{4}-\d{2}-\d{2}",result.stdout.strip()): return result.stdout.strip()
    except (ValueError,OSError,subprocess.SubprocessError): pass
    return datetime.fromtimestamp(contract.stat().st_mtime,timezone.utc).date().isoformat()

def current_category(content: str) -> str:
    if content.startswith("---\n"):
        content = content.split("\n---\n", 1)[0]
    match = re.search(r'^categories:\s*\["([^"]+)"\]', content, re.MULTILINE)
    return match.group(1) if match else ""


def checked_slugs(values, description: str) -> list[str]:
    if not isinstance(values, list) or any(
        not isinstance(slug, str) or not SLUG_PATTERN.fullmatch(slug) for slug in values
    ):
        raise ValueError(f"{description} must contain lowercase URL slugs")
    if len(values) != len(set(values)):
        raise ValueError(f"{description} contains duplicate slugs")
    return values


def source_order(source_dir: Path, config: dict, contracts: dict) -> list[str]:
    if config["order"]:
        return config["order"]
    catalog = source_dir / config["catalog"]
    if not catalog.is_file():
        return checked_slugs(sorted(contracts), str(source_dir))
    data = json.loads(catalog.read_text(encoding="utf-8"))
    agents = data.get("agents") if isinstance(data, dict) else None
    if not agents or not isinstance(agents, list) or any(not isinstance(agent, dict) for agent in agents):
        raise ValueError(f"invalid agent catalog: {catalog}")
    return checked_slugs([agent.get("slug") for agent in agents], str(catalog))


PLATFORM_NAMES = {"slack": "Slack", "matrix": "Matrix", "teams": "Microsoft Teams",
                  "paperclip": "Paperclip", "board": "Vercel Board", "mcp": "MCP", "local": "Local"}
QUALIFICATION = {"fixture-only": "fixture tested", "experimental": "experimental",
                 "qualified": "qualified"}


def compatibility(source_root: Path, source: str) -> dict[str, list[dict]]:
    index = source_root / "collaboration-integrations.json"
    if not index.is_file():
        return {}
    payload = json.loads(index.read_text(encoding="utf-8"))
    if (payload.get("schema") != "kujo.collaboration.compatibility/v1"
            or not isinstance(payload.get("entries"), list)):
        raise ValueError("unsupported collaboration index")
    registry = json.loads((source_root / "agent-registry.json").read_text(encoding="utf-8"))
    paths = {row["id"]: row["path"] for row in registry["agents"]}
    selected: dict[str, list[dict]] = {}
    seen = set()
    for row in payload["entries"]:
        platform, state, host = row.get("platform"), row.get("status"), row.get("host")
        agents = row.get("agent_ids")
        operations = row.get("operations")
        if (platform not in PLATFORM_NAMES or state not in QUALIFICATION or row.get("protocol_major") != 1
                or not isinstance(host, str) or not re.fullmatch(r"[a-z0-9-]{1,60}", host)
                or not isinstance(agents, list) or not agents
                or not isinstance(operations, list) or not operations
                or any(not isinstance(op, str) or not re.fullmatch(r"[a-z.-]{1,48}", op) for op in operations)):
            raise ValueError("invalid collaboration entry")
        if state == "qualified":
            for key in ("setup_url", "qualification_url"):
                value = row.get(key, "")
                url = urlsplit(value)
                if (url.scheme != "https" or url.netloc not in {"agents.kujolang.ai", "github.com"}
                        or url.query or url.fragment or not re.fullmatch(r"/[A-Za-z0-9_./-]+", url.path)):
                    raise ValueError("untrusted collaboration qualification link")
        if "preview_url" in row:
            preview = row["preview_url"]
            if (state != "experimental" or platform != "slack" or not isinstance(preview, str)
                    or not re.fullmatch(r"https://agents[.]kujolang[.]ai/connect-slack(?:-[a-z0-9-]+)?/", preview)):
                raise ValueError("untrusted Slack preview link")
        for agent in agents:
            key = (agent, platform, host)
            if agent not in paths or key in seen:
                raise ValueError("unknown or duplicate collaboration profile")
            seen.add(key)
            directory, _, slug = paths[agent].partition("/")
            if directory == source:
                selected.setdefault(slug, []).append({**row, 'agent_id': agent})
    return selected


DESTINATION_ORDER = ("slack", "board", "teams", "paperclip", "matrix", "mcp", "local")


def connection_options(entries: list[dict]) -> list[dict]:
    options = []
    for platform in DESTINATION_ORDER:
        matches = [row for row in entries if row["platform"] == platform]
        if not matches and platform in {"mcp", "local"}:
            continue
        ordered = sorted(matches, key=lambda row: (
            row["status"] != "qualified", "preview_url" not in row,
            row["status"] != "experimental", row["host"],
        ))
        option = {"name": PLATFORM_NAMES[platform], "status": "unavailable"}
        if ordered:
            chosen = ordered[0]
            option["status"] = chosen["status"]
            if chosen["status"] == "qualified":
                option.update(url=chosen["setup_url"], evidence=chosen["qualification_url"])
            elif "preview_url" in chosen:
                path = urlsplit(chosen["preview_url"]).path
                if path == "/connect-slack/":
                    path += "?" + urlencode({"agent": chosen["agent_id"]})
                option["url"] = path
        options.append(option)
    return options


def render_set(source_root: Path, set_id: str) -> dict[str, str]:
    config = SETS[set_id]
    source_dir = source_root / config["source"]
    if not source_dir.is_dir() or source_dir.is_symlink():
        raise ValueError(f"source directory not found: {source_dir}")
    contracts = {path.parent.name: path for path in source_dir.glob("*/AGENT.md")}
    if not contracts:
        raise ValueError(f"no agent contracts found in: {source_dir}")
    order = source_order(source_dir, config, contracts)
    missing = set(order) - contracts.keys()
    if missing:
        raise ValueError(f"{set_id} order references missing contracts: {sorted(missing)}")

    compatibility_by_slug = compatibility(source_root, config["source"])
    generated = {}
    for position, slug in enumerate(order, 1):
        contract = contracts[slug]
        if contract.is_symlink() or contract.parent.is_symlink():
            raise ValueError(f"agent contract must be a local file: {contract}")
        body = contract.read_text(encoding="utf-8").strip()
        heading, _, remainder = body.partition("\n")
        if not heading.startswith("# "):
            raise ValueError(f"missing title heading: {contract}")
        title = heading[2:].strip()
        purpose = field(body, "Purpose")
        public_slug = config["public_prefix"] + slug
        portrait = f"content/media/agents/{public_slug}.webp"
        featured = portrait if (SITE_ROOT / portrait).is_file() else "assets/images/kujo-logomark.svg"
        source_url = f"https://github.com/kujolang/kujo-agents/blob/main/{config['source']}/{slug}/AGENT.md"
        fields = {
            "title": title, "custom_url": public_slug, "description": purpose, "excerpt": purpose,
            "seo_title": f"{title} | Kujo {config['category']}", "seo_description": purpose,
            "keywords": f"{config['keywords']}, {title}", "featured_image": featured,
            "categories": [config["category"]], "tags": [field(body, config["tag_field"])],
            "order": position,
             "connection_options": json.dumps(connection_options(compatibility_by_slug.get(slug, []))),
        }
        frontmatter = ["---", *(f"{key}: {json.dumps(value)}" for key, value in fields.items()),
                       f"last_updated: {updated_date(source_root, contract)}",
                       f"source_url: {json.dumps(source_url)}", "---", ""]
        remainder = re.sub(r"(^- (?:Required KUJO skills|WebOps domain skills|Existing Kujo skills):\s*)(.+)$",
                           lambda match: match.group(1) + match.group(2).replace("`", ""),
                           remainder, flags=re.MULTILINE)
        generated[public_slug] = "\n".join(frontmatter) + remainder.lstrip() + "\n"
    return generated


def publish(changes: dict[Path, str | None]) -> None:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".sync-", dir=OUTPUT_ROOT) as directory:
        scratch = Path(directory)
        originals = {}
        staged = {}
        for position, (path, content) in enumerate(changes.items()):
            if path.exists():
                original = scratch / f"original-{position}"
                os.link(path, original)
                originals[path] = original
            if content is not None:
                updated = scratch / f"staged-{position}"
                updated.write_text(content, encoding="utf-8")
                if path in originals:
                    updated.chmod(stat.S_IMODE(originals[path].stat().st_mode))
                staged[path] = updated

        applied = []
        try:
            for path in changes:
                if path in staged:
                    staged[path].replace(path)
                else:
                    path.unlink()
                applied.append(path)
        except (OSError, KeyboardInterrupt):
            for path in reversed(applied):
                if path in originals:
                    originals[path].replace(path)
                else:
                    path.unlink()
            raise


def sync_sets(source_root: Path, selected: list[str], state: dict | None = None) -> dict[str, list[str]]:
    if OUTPUT_ROOT.is_symlink() or not OUTPUT_ROOT.resolve().is_relative_to(SITE_ROOT.resolve()):
        raise ValueError(f"unsafe managed content directory: {OUTPUT_ROOT}")
    if STATE_PATH.is_symlink():
        raise ValueError(f"unsafe sync state: {STATE_PATH}")
    if state is None:
        state = json.loads(STATE_PATH.read_text(encoding="utf-8")) if STATE_PATH.is_file() else {}
    if not isinstance(state, dict) or state.get("schema", STATE_SCHEMA) != STATE_SCHEMA:
        raise ValueError("unsupported sync state")
    previous_sets = state.get("sets", {})
    if not isinstance(previous_sets, dict) or any(set_id not in SETS for set_id in previous_sets):
        raise ValueError("invalid agent set ownership in sync state")

    owners = {}
    for set_id, slugs in previous_sets.items():
        for slug in checked_slugs(slugs, set_id):
            if slug in owners:
                raise ValueError(f"multiple owners for {slug}: {owners[slug]} and {set_id}")
            owners[slug] = set_id

    changes = {}
    generated_sets = {}
    for set_id in dict.fromkeys(selected):
        generated = render_set(source_root, set_id)
        category = SETS[set_id]["category"]
        for slug, projection in generated.items():
            path = OUTPUT_ROOT / f"{slug}.md"
            if owners.setdefault(slug, set_id) != set_id:
                raise ValueError(f"{slug} is already owned by {owners[slug]}")
            if path.is_symlink() or (path.exists() and not path.is_file()):
                raise ValueError(f"invalid managed agent file: {path}")
            existing = path.read_text(encoding="utf-8") if path.exists() else None
            if existing is not None and current_category(existing) != category:
                raise ValueError(f"{slug} is outside the {set_id} set")
            if existing != projection:
                changes[path] = projection

        previous = previous_sets.get(set_id) or [
            path.stem for path in OUTPUT_ROOT.glob("*.md")
            if path.is_file() and not path.is_symlink()
            and current_category(path.read_text(encoding="utf-8")) == category
        ]
        for stale in sorted(set(previous) - generated.keys()):
            path = OUTPUT_ROOT / f"{stale}.md"
            if (owners.get(stale, set_id) == set_id and path.is_file() and not path.is_symlink()
                    and current_category(path.read_text(encoding="utf-8")) == category):
                changes[path] = None
        generated_sets[set_id] = list(generated)

    updated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    state = {**state, "schema": STATE_SCHEMA, "sets": {**previous_sets, **generated_sets},
             "updated_at": updated_at}
    changes[STATE_PATH] = json.dumps(state, indent=2) + "\n"
    publish(changes)
    return generated_sets


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path, help="path to kujo-agents root (legacy set directory also accepted)")
    parser.add_argument("--set", dest="sets", action="append", choices=sorted(SETS))
    args = parser.parse_args()
    source = args.source.expanduser().resolve()
    selected = args.sets or sorted(SETS)
    if source.name in SETS and (source / "README.md").is_file():
        selected = [source.name]
        source = source.parent
    if not any((source / set_id).is_dir() for set_id in SETS):
        print(f"kujo-agents root not found: {source}", file=sys.stderr)
        return 2

    try:
        results = sync_sets(source, selected)
    except (OSError, ValueError) as exc:
        print(f"sync failed: {exc}", file=sys.stderr)
        return 1

    for set_id, slugs in results.items():
        print(f"Generated {len(slugs)} {SETS[set_id]['category']} agent entries")
    print(f"Generated {sum(map(len, results.values()))} agent entries in {OUTPUT_ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
