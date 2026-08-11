#!/usr/bin/env python3
"""Create reproducible local and production SEO audit datasets for this site."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path
from urllib import robotparser
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


INVENTORY_FIELDS = [
    "phase", "url", "source_file", "page_type", "local_status", "production_status",
    "indexable", "robots_directives", "canonical", "canonical_target_status", "title",
    "title_length", "meta_description", "description_length", "h1", "heading_structure",
    "word_count", "lang", "published_date", "modified_date", "author", "breadcrumbs",
    "schema_types", "internal_inbound_links", "internal_outbound_links",
    "external_outbound_links", "broken_internal_links", "broken_external_links",
    "image_count", "missing_alt", "missing_dimensions", "page_depth", "orphan",
    "sitemap_included", "duplicate_title", "duplicate_description", "content_hash", "issues",
]
LINK_FIELDS = [
    "phase", "source_url", "destination_url", "anchor_text", "link_context", "http_status",
    "final_url", "chain_length", "verification", "rel", "recommended_action",
]
IMAGE_FIELDS = [
    "phase", "source_url", "image_url", "alt", "width", "height", "loading", "format",
    "bytes", "exists", "issues",
]
SCHEMA_FIELDS = ["phase", "url", "block", "schema_types", "parse_state", "visible_alignment", "issues"]
META_FIELDS = [
    "phase", "url", "title", "title_length", "meta_description", "description_length",
    "h1_count", "canonical", "og_title", "og_description", "og_url", "og_image",
    "twitter_card", "twitter_title", "twitter_description", "twitter_image", "issues",
]
INDEX_FIELDS = [
    "phase", "url", "status", "robots_directives", "canonical", "sitemap_included",
    "indexable", "issues",
]
CRAWLER_FIELDS = ["crawler", "purpose", "robots_access", "live_status", "waf_or_cdn_result", "recommended_action", "action_taken", "evidence"]
CRAWL_FIELDS = ["phase", "url", "page_depth", "internal_inbound_links", "internal_outbound_links", "external_outbound_links", "orphan", "pages_over_three_clicks", "broken_internal_links", "redirect_chain", "crawlable_html_links", "issues"]
REDIRECT_FIELDS = ["phase", "source_url", "source_variant", "http_status", "target_url", "chain_length", "final_status", "canonical_target", "query_preserved", "verification", "issues"]
CONTENT_FIELDS = ["phase", "url", "source_file", "page_type", "primary_purpose", "search_intent", "target_audience", "central_entity", "primary_query_theme", "supporting_topics", "h1", "heading_structure", "word_count", "published_date", "modified_date", "first_hand_signals", "content_gap", "competing_internal_url", "recommended_action"]
KEYWORD_FIELDS = ["phase", "url", "primary_topic", "primary_entity", "search_intent", "primary_query_theme", "secondary_queries", "related_entities", "relevant_questions", "competing_internal_url", "content_gap", "recommended_action"]


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fields,
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def meta_content(soup: BeautifulSoup, *, name: str | None = None, prop: str | None = None) -> str:
    selector = {"name": name} if name else {"property": prop}
    tag = soup.find("meta", attrs=selector)
    return tag.get("content", "").strip() if tag else ""


def route_for_file(root: Path, path: Path) -> str:
    rel = path.relative_to(root).as_posix()
    if rel == "index.html":
        return "/"
    if rel == "404.html":
        return "/404.html"
    if rel.endswith("/index.html"):
        return "/" + rel[: -len("index.html")]
    return "/" + rel


def local_path_for_url(root: Path, absolute_url: str, origin: str) -> Path | None:
    parsed = urlparse(absolute_url)
    if parsed.netloc and parsed.netloc != urlparse(origin).netloc:
        return None
    route = parsed.path or "/"
    candidates = []
    if route.endswith("/"):
        candidates.append(root / route.lstrip("/") / "index.html")
    else:
        candidates.extend([root / route.lstrip("/"), root / route.lstrip("/") / "index.html"])
    return next((candidate for candidate in candidates if candidate.is_file()), candidates[0] if candidates else None)


def source_for_route(route: str, repo_root: Path) -> str:
    if route == "/":
        return "templates/page-home.html"
    if route == "/agents/":
        return "templates/page-agents.html"
    if route in {"/agents/chain-of-command/", "/agents/webops/"}:
        return "templates/page-agent-set.html"
    match = re.fullmatch(r"/agents/([^/]+)/", route)
    if match and (repo_root / "content" / "agents" / f"{match.group(1)}.md").exists():
        return f"content/agents/{match.group(1)}.md"
    if route == "/404.html":
        return "templates/404.html"
    return ""


def schema_types(value) -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        kind = value.get("@type")
        if isinstance(kind, list):
            found.extend(str(item) for item in kind)
        elif kind:
            found.append(str(kind))
        for child in value.values():
            found.extend(schema_types(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(schema_types(child))
    return found


def request_url(session: requests.Session, url: str, user_agent: str | None = None) -> dict:
    headers = {"User-Agent": user_agent} if user_agent else {}
    try:
        response = session.get(url, headers=headers, timeout=20, allow_redirects=True)
        return {
            "status": response.status_code,
            "initial_status": response.history[0].status_code if response.history else response.status_code,
            "final_url": response.url,
            "chain_length": len(response.history),
            "headers": dict(response.headers),
            "bytes": len(response.content),
            "sha256": hashlib.sha256(response.content).hexdigest(),
            "error": "",
        }
    except requests.RequestException as exc:
        return {"status": "", "initial_status": "", "final_url": "", "chain_length": "", "headers": {}, "bytes": "", "sha256": "", "error": str(exc)}


def content_assessment(row: dict) -> tuple[dict, dict]:
    title = row["h1"].split(";", 1)[0] or row["title"]
    if row["page_type"] == "home":
        purpose = "Introduce the Kujo Agents library and route readers to agent sets and source contracts."
        intent = "Branded informational and navigational"
        audience = "Developers and teams designing auditable multi-agent workflows"
        entity = "Kujo Agents"
        theme = "Kujo AI agent library"
        supporting = "AI agent contracts; chain of command; specialized agent roles"
        gap = "No adoption examples or measured outcomes are published."
        action = "Keep the overview concise; add real adoption examples only when evidence exists."
        questions = "What is Kujo Agents?; Which specialist agent should I use?"
    elif row["page_type"] == "listing":
        purpose = "Help readers browse and compare source-grounded agent roles."
        intent = "Informational and navigational"
        audience = "Developers and technical leads assembling agent teams"
        entity = title
        theme = f"{title} agent roles"
        supporting = "agent responsibilities; orchestration; planning; implementation; verification"
        gap = "The listing explains roles through excerpts but has no selection guide or real usage examples."
        action = "Add a concise selection guide when real usage evidence is available."
        questions = f"Which {title.lower()} role fits my task?; How are the agents organized?"
    elif row["page_type"] == "agent":
        purpose = f"Publish the operating contract for the {title} agent role."
        intent = "Informational and implementation-oriented"
        audience = "Developers and operators delegating bounded work to AI agents"
        entity = f"{title} agent"
        theme = f"{title} AI agent contract"
        supporting = "purpose; use cases; inputs; outputs; workflow; evidence; handoffs; escalation; stop conditions"
        gap = "No worked usage example or version history is included beyond the source-linked contract and update date."
        action = "Add only source-grounded examples and change history when they exist."
        questions = f"When should I use a {title} agent?; What inputs and outputs does {title} require?"
    else:
        purpose = "Explain that the requested route is unavailable."
        intent = "Error recovery"
        audience = "Visitors who reached a missing route"
        entity = "Kujo Agents"
        theme = "page not found"
        supporting = "agent directory"
        gap = "Not applicable to search; excluded from indexing."
        action = "Keep noindex and route users to the agent directory."
        questions = ""
    first_hand = "Source-linked operating contract with explicit workflow and evidence requirements." if row["page_type"] == "agent" else "Repository-generated inventory and direct links to source contracts."
    content = {
        "phase": row["phase"], "url": row["url"], "source_file": row["source_file"], "page_type": row["page_type"],
        "primary_purpose": purpose, "search_intent": intent, "target_audience": audience,
        "central_entity": entity, "primary_query_theme": theme, "supporting_topics": supporting,
        "h1": row["h1"], "heading_structure": row["heading_structure"], "word_count": row["word_count"],
        "published_date": row["published_date"], "modified_date": row["modified_date"],
        "first_hand_signals": first_hand, "content_gap": gap, "competing_internal_url": "",
        "recommended_action": action,
    }
    keyword = {
        "phase": row["phase"], "url": row["url"], "primary_topic": purpose,
        "primary_entity": entity, "search_intent": intent, "primary_query_theme": theme,
        "secondary_queries": supporting, "related_entities": "Kujo; AI agents; agent contracts; multi-agent workflows",
        "relevant_questions": questions, "competing_internal_url": "", "content_gap": gap,
        "recommended_action": action,
    }
    return content, keyword


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path, help="Generated site directory")
    parser.add_argument("--repo-root", default=Path.cwd(), type=Path)
    parser.add_argument("--origin", required=True)
    parser.add_argument("--phase", required=True, choices=("baseline", "after"))
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--probe-production", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    repo_root = args.repo_root.resolve()
    origin = args.origin.rstrip("/")
    html_files = sorted(root.rglob("*.html"))
    if not html_files:
        raise SystemExit(f"No HTML files found under {root}")

    sitemap_text = (root / "sitemap.xml").read_text(encoding="utf-8") if (root / "sitemap.xml").exists() else ""
    sitemap_urls = set(re.findall(r"<loc>(.*?)</loc>", sitemap_text))
    pages: dict[str, dict] = {}
    link_rows: list[dict] = []
    image_rows: list[dict] = []
    schema_rows: list[dict] = []
    meta_rows: list[dict] = []
    session = requests.Session()
    session.headers["User-Agent"] = "KujoSEOAudit/1.0 (+https://agents.kujolang.ai/)"
    production_cache: dict[str, dict] = {}

    for path in html_files:
        route = route_for_file(root, path)
        url = origin + route
        soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
        title = soup.title.get_text(" ", strip=True) if soup.title else ""
        description = meta_content(soup, name="description")
        canonical_tag = soup.find("link", rel=lambda value: value and "canonical" in value)
        canonical = canonical_tag.get("href", "").strip() if canonical_tag else ""
        h1s = [tag.get_text(" ", strip=True) for tag in soup.find_all("h1")]
        headings = [f"{tag.name}:{tag.get_text(' ', strip=True)}" for tag in soup.find_all(re.compile(r"^h[1-6]$"))]
        robots = ",".join(filter(None, [meta_content(soup, name="robots"), meta_content(soup, name="googlebot")]))
        text = " ".join(soup.get_text(" ", strip=True).split())
        links = soup.find_all("a", href=True)
        internal_links = []
        external_links = []
        for tag in links:
            destination = urljoin(url, tag["href"])
            parsed = urlparse(destination)
            if parsed.scheme not in {"http", "https"}:
                continue
            clean_destination = destination.split("#", 1)[0]
            is_internal = parsed.netloc == urlparse(origin).netloc
            (internal_links if is_internal else external_links).append(clean_destination)
            local_target = local_path_for_url(root, clean_destination, origin) if is_internal else None
            status = 200 if local_target and local_target.exists() else (404 if is_internal else "")
            verification = "local generated artifact" if is_internal else "not probed per-link; unique external destinations sampled separately"
            link_rows.append({
                "phase": args.phase,
                "source_url": url,
                "destination_url": clean_destination,
                "anchor_text": tag.get_text(" ", strip=True),
                "link_context": tag.parent.name if tag.parent else "",
                "http_status": status,
                "final_url": clean_destination if status == 200 else "",
                "chain_length": 0 if status == 200 else "",
                "verification": verification,
                "rel": " ".join(tag.get("rel", [])),
                "recommended_action": "repair internal destination" if status == 404 else "",
            })

        missing_alt = 0
        missing_dimensions = 0
        for image in soup.find_all("img"):
            src = urljoin(url, image.get("src", ""))
            local_image = local_path_for_url(root, src, origin)
            alt_present = image.has_attr("alt")
            dims_present = image.has_attr("width") and image.has_attr("height")
            missing_alt += 0 if alt_present else 1
            missing_dimensions += 0 if dims_present else 1
            issues = []
            if not alt_present:
                issues.append("missing alt attribute")
            if not dims_present:
                issues.append("missing intrinsic dimensions")
            image_rows.append({
                "phase": args.phase,
                "source_url": url,
                "image_url": src,
                "alt": image.get("alt", ""),
                "width": image.get("width", ""),
                "height": image.get("height", ""),
                "loading": image.get("loading", "eager/default"),
                "format": Path(urlparse(src).path).suffix.lstrip("."),
                "bytes": local_image.stat().st_size if local_image and local_image.exists() else "",
                "exists": bool(local_image and local_image.exists()),
                "issues": "; ".join(issues),
            })

        parsed_schema_types: list[str] = []
        schema_published = ""
        schema_modified = ""
        for block_number, block in enumerate(soup.find_all("script", attrs={"type": "application/ld+json"}), start=1):
            try:
                payload = json.loads(block.string or block.get_text())
                types = schema_types(payload)
                parsed_schema_types.extend(types)
                if isinstance(payload, dict):
                    schema_published = schema_published or str(payload.get("datePublished", ""))
                    schema_modified = schema_modified or str(payload.get("dateModified", ""))
                state = "valid JSON"
                issues = ""
            except (json.JSONDecodeError, TypeError) as exc:
                types = []
                state = "parse error"
                issues = str(exc)
            schema_rows.append({
                "phase": args.phase, "url": url, "block": block_number,
                "schema_types": ";".join(dict.fromkeys(types)), "parse_state": state,
                "visible_alignment": "headline/name/description manually comparable to visible page and metadata",
                "issues": issues,
            })

        production = {"status": "", "headers": {}, "error": ""}
        if args.probe_production and route != "/404.html":
            production = production_cache.setdefault(url, request_url(session, url))
        noindex = "noindex" in robots.lower()
        indexable = route != "/404.html" and not noindex and (not args.probe_production or production["status"] == 200)
        issues = []
        if not title:
            issues.append("missing title")
        if not description:
            issues.append("missing meta description")
        if len(h1s) != 1:
            issues.append(f"h1 count {len(h1s)}")
        if not canonical and route != "/404.html":
            issues.append("missing canonical")
        if route == "/404.html" and not noindex:
            issues.append("404 template lacks noindex")
        if missing_dimensions:
            issues.append(f"{missing_dimensions} images missing dimensions")
        if any(row["http_status"] == 404 and row["source_url"] == url for row in link_rows):
            issues.append("broken internal link")
        local_sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
        production_matches_local = ""
        if args.probe_production and route != "/404.html" and production["status"] == 200:
            production_matches_local = production["sha256"] == local_sha256
            if not production_matches_local:
                issues.append("production HTML differs from generated artifact")
        pages[url] = {
            "phase": args.phase, "url": url, "source_file": source_for_route(route, repo_root),
            "page_type": "404" if route == "/404.html" else ("agent" if re.fullmatch(r"/agents/[^/]+/", route) and route not in {"/agents/chain-of-command/", "/agents/webops/"} else "listing" if route.startswith("/agents/") else "home"),
            "local_status": 404 if route == "/404.html" else 200,
            "production_status": production["status"], "indexable": str(indexable).lower(),
            "robots_directives": robots or "default index,follow", "canonical": canonical,
            "canonical_target_status": 200 if canonical else "", "title": title,
            "title_length": len(title), "meta_description": description,
            "description_length": len(description), "h1": ";".join(h1s),
            "heading_structure": " | ".join(headings), "word_count": len(text.split()),
            "lang": soup.html.get("lang", "") if soup.html else "",
            "published_date": schema_published, "modified_date": schema_modified, "author": meta_content(soup, name="author"),
            "breadcrumbs": bool(soup.select_one('[aria-label="Breadcrumb"]')),
            "schema_types": ";".join(dict.fromkeys(parsed_schema_types)),
            "internal_inbound_links": 0, "internal_outbound_links": len(internal_links),
            "external_outbound_links": len(external_links),
            "broken_internal_links": sum(1 for row in link_rows if row["source_url"] == url and row["http_status"] == 404),
            "broken_external_links": "not fully probed", "image_count": len(soup.find_all("img")),
            "missing_alt": missing_alt, "missing_dimensions": missing_dimensions,
            "page_depth": 0 if route == "/" else len([part for part in route.split("/") if part]),
            "orphan": "", "sitemap_included": canonical in sitemap_urls,
            "duplicate_title": "", "duplicate_description": "",
            "content_hash": hashlib.sha256(text.encode()).hexdigest(), "issues": "; ".join(issues),
            "_route": route, "_internal_links": internal_links, "_production": production,
            "_production_matches_local": production_matches_local,
        }
        meta_rows.append({
            "phase": args.phase, "url": url, "title": title, "title_length": len(title),
            "meta_description": description, "description_length": len(description), "h1_count": len(h1s),
            "canonical": canonical, "og_title": meta_content(soup, prop="og:title"),
            "og_description": meta_content(soup, prop="og:description"), "og_url": meta_content(soup, prop="og:url"),
            "og_image": meta_content(soup, prop="og:image"), "twitter_card": meta_content(soup, name="twitter:card"),
            "twitter_title": meta_content(soup, name="twitter:title"),
            "twitter_description": meta_content(soup, name="twitter:description"),
            "twitter_image": meta_content(soup, name="twitter:image"), "issues": "; ".join(issues),
        })

    canonical_to_url = {page["canonical"]: url for url, page in pages.items() if page["canonical"]}
    incoming = Counter()
    graph: dict[str, set[str]] = defaultdict(set)
    for url, page in pages.items():
        for destination in page["_internal_links"]:
            destination = destination.split("#", 1)[0]
            if destination in canonical_to_url:
                graph[url].add(destination)
                incoming[destination] += 1

    depths = {origin + "/": 0}
    queue = deque([origin + "/"])
    while queue:
        current = queue.popleft()
        for destination in graph.get(current, set()):
            if destination not in depths:
                depths[destination] = depths[current] + 1
                queue.append(destination)

    title_counts = Counter(page["title"] for page in pages.values() if page["title"])
    description_counts = Counter(page["meta_description"] for page in pages.values() if page["meta_description"])
    inventory_rows = []
    index_rows = []
    for url, page in pages.items():
        page["internal_inbound_links"] = incoming[url]
        page["orphan"] = str(url not in depths and page["_route"] != "/404.html").lower()
        page["page_depth"] = depths.get(url, page["page_depth"])
        page["duplicate_title"] = str(bool(page["title"] and title_counts[page["title"]] > 1)).lower()
        page["duplicate_description"] = str(bool(page["meta_description"] and description_counts[page["meta_description"]] > 1)).lower()
        clean = {key: value for key, value in page.items() if not key.startswith("_")}
        inventory_rows.append(clean)
        index_rows.append({
            "phase": args.phase, "url": url, "status": page["production_status"] or page["local_status"],
            "robots_directives": page["robots_directives"], "canonical": page["canonical"],
            "sitemap_included": page["sitemap_included"], "indexable": page["indexable"],
            "issues": page["issues"],
        })

    prefix = "baseline" if args.phase == "baseline" else "after"
    write_csv(args.out / f"{prefix}.csv", INVENTORY_FIELDS, inventory_rows)
    write_csv(args.out / "site-inventory.csv", INVENTORY_FIELDS, inventory_rows)
    write_csv(args.out / "internal-links.csv", LINK_FIELDS, [row for row in link_rows if urlparse(row["destination_url"]).netloc == urlparse(origin).netloc])
    external_rows = [row for row in link_rows if urlparse(row["destination_url"]).netloc != urlparse(origin).netloc]
    external_cache: dict[str, dict] = {}
    if args.probe_production:
        for destination in sorted({row["destination_url"] for row in external_rows}):
            external_cache[destination] = request_url(session, destination)
        for row in external_rows:
            result = external_cache[row["destination_url"]]
            row["http_status"] = result["status"]
            row["final_url"] = result["final_url"]
            row["chain_length"] = result["chain_length"]
            if result["status"] in {401, 403, 405, 429}:
                row["verification"] = "blocked or indeterminate"
            elif result["status"] and int(result["status"]) >= 400:
                row["verification"] = "failed live request"
                row["recommended_action"] = "manually corroborate and repair or remove if confirmed broken"
            elif result["status"]:
                row["verification"] = "live request succeeded"
            else:
                row["verification"] = "request error; indeterminate"
    write_csv(args.out / "external-links.csv", LINK_FIELDS, external_rows)
    write_csv(args.out / "broken-links.csv", LINK_FIELDS, [row for row in link_rows if row["http_status"] == 404])
    write_csv(args.out / "image-audit.csv", IMAGE_FIELDS, image_rows)
    write_csv(args.out / "schema-audit.csv", SCHEMA_FIELDS, schema_rows)
    write_csv(args.out / "metadata-audit.csv", META_FIELDS, meta_rows)
    write_csv(args.out / "indexability.csv", INDEX_FIELDS, index_rows)
    crawl_rows = [{
        "phase": row["phase"], "url": row["url"], "page_depth": row["page_depth"],
        "internal_inbound_links": row["internal_inbound_links"], "internal_outbound_links": row["internal_outbound_links"],
        "external_outbound_links": row["external_outbound_links"], "orphan": row["orphan"],
        "pages_over_three_clicks": str(isinstance(row["page_depth"], int) and row["page_depth"] > 3).lower(),
        "broken_internal_links": row["broken_internal_links"], "redirect_chain": 0,
        "crawlable_html_links": "true", "issues": row["issues"],
    } for row in inventory_rows]
    write_csv(args.out / "crawlability.csv", CRAWL_FIELDS, crawl_rows)
    assessments = [content_assessment(row) for row in inventory_rows]
    write_csv(args.out / "content-audit.csv", CONTENT_FIELDS, [pair[0] for pair in assessments])
    write_csv(args.out / "keyword-map.csv", KEYWORD_FIELDS, [pair[1] for pair in assessments])

    summary = {
        "phase": args.phase,
        "pages_total": len(inventory_rows),
        "canonical_pages": sum(1 for row in inventory_rows if row["canonical"]),
        "indexable_pages": sum(1 for row in inventory_rows if row["indexable"] == "true"),
        "missing_titles": sum(1 for row in inventory_rows if not row["title"]),
        "duplicate_titles": sum(1 for row in inventory_rows if row["duplicate_title"] == "true"),
        "missing_descriptions": sum(1 for row in inventory_rows if not row["meta_description"]),
        "duplicate_descriptions": sum(1 for row in inventory_rows if row["duplicate_description"] == "true"),
        "missing_canonicals": sum(1 for row in inventory_rows if not row["canonical"] and row["page_type"] != "404"),
        "h1_problems": sum(1 for row in meta_rows if row["h1_count"] != 1),
        "broken_internal_link_occurrences": sum(1 for row in link_rows if row["http_status"] == 404),
        "orphans": sum(1 for row in inventory_rows if row["orphan"] == "true"),
        "pages_deeper_than_3": sum(1 for row in inventory_rows if isinstance(row["page_depth"], int) and row["page_depth"] > 3),
        "images_missing_alt": sum(row["missing_alt"] for row in inventory_rows),
        "images_missing_dimensions": sum(row["missing_dimensions"] for row in inventory_rows),
        "schema_parse_errors": sum(1 for row in schema_rows if row["parse_state"] != "valid JSON"),
        "valid_schema_pages": len({row["url"] for row in schema_rows if row["parse_state"] == "valid JSON"}),
        "production_non_200": sum(1 for row in inventory_rows if row["production_status"] not in {"", 200}),
        "production_content_mismatches": sum(1 for page in pages.values() if page["_production_matches_local"] is False),
    }
    (args.out / f"{prefix}-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    raw = args.out / "raw" / args.phase
    raw.mkdir(parents=True, exist_ok=True)
    (raw / "production-responses.json").write_text(json.dumps(production_cache, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (raw / "external-responses.json").write_text(json.dumps(external_cache, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.probe_production:
        robots_result = request_url(session, origin + "/robots.txt")
        sitemap_result = request_url(session, origin + "/sitemap.xml")
        robots_live = session.get(origin + "/robots.txt", timeout=20)
        robots_policy = robotparser.RobotFileParser()
        robots_policy.parse(robots_live.text.splitlines())
        crawler_specs = [
            ("Googlebot", "search discovery and indexing"),
            ("bingbot", "Bing and Copilot search discovery"),
            ("OAI-SearchBot", "OpenAI search discovery and citation"),
            ("ChatGPT-User", "user-triggered OpenAI fetches"),
            ("PerplexityBot", "Perplexity search discovery and citation"),
            ("ClaudeBot", "Anthropic automated crawler; owner policy blocks it"),
            ("GPTBot", "OpenAI training crawler; owner policy blocks it"),
        ]
        crawler_rows = []
        crawler_receipts = {}
        for crawler, purpose in crawler_specs:
            result = request_url(session, origin + "/", crawler)
            crawler_receipts[crawler] = result
            live_ok = result["status"] == 200
            robots_allowed = robots_policy.can_fetch(crawler, origin + "/")
            crawler_rows.append({
                "crawler": crawler, "purpose": purpose, "robots_access": "allowed" if robots_allowed else "disallowed by production robots.txt",
                "live_status": result["status"], "waf_or_cdn_result": "200 through Cloudflare" if live_ok else (result["error"] or "non-200 response"),
                "recommended_action": "none; preserve owner policy" if not robots_allowed else ("none" if live_ok else "inspect Cloudflare and origin logs"),
                "action_taken": "read-only live probe", "evidence": f"{args.phase} GET / with {crawler} user agent",
            })
        write_csv(args.out / "crawler-access.csv", CRAWLER_FIELDS, crawler_rows)
        redirect_variants = [
            ("http canonical host", "http://agents.kujolang.ai/?seo_audit=1"),
            ("https canonical query", "https://agents.kujolang.ai/?seo_audit=1"),
            ("https www", "https://www.agents.kujolang.ai/?seo_audit=1"),
            ("http www", "http://www.agents.kujolang.ai/?seo_audit=1"),
        ]
        redirect_rows = []
        redirect_receipts = {}
        for label, source in redirect_variants:
            result = request_url(session, source)
            redirect_receipts[source] = result
            final_url = result["final_url"]
            query_preserved = "seo_audit=1" in final_url if final_url else "indeterminate"
            redirect_rows.append({
                "phase": args.phase, "source_url": source, "source_variant": label,
                "http_status": result["initial_status"],
                "target_url": final_url, "chain_length": result["chain_length"], "final_status": result["status"],
                "canonical_target": origin + "/", "query_preserved": query_preserved,
                "verification": "live request" if result["status"] else "request failed",
                "issues": result["error"] or ("www host unavailable" if "www." in source and result["status"] != 200 else ""),
            })
        write_csv(args.out / "redirects.csv", REDIRECT_FIELDS, redirect_rows)
        (raw / "crawler-responses.json").write_text(json.dumps(crawler_receipts, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (raw / "redirect-responses.json").write_text(json.dumps(redirect_receipts, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        sitemap_live = session.get(origin + "/sitemap.xml", timeout=20)
        missing_live = session.get(origin + "/seo-audit/missing/deep-path?case=1", timeout=20)
        missing_soup = BeautifulSoup(missing_live.text, "html.parser")
        auxiliary = {
            "robots": {**robots_result, "body": robots_live.text},
            "sitemap": {**sitemap_result, "url_count": sitemap_live.text.count("<loc>"), "sha256": hashlib.sha256(sitemap_live.content).hexdigest()},
            "nested_404": {
                "status": missing_live.status_code,
                "final_url": missing_live.url,
                "robots": meta_content(missing_soup, name="robots"),
                "canonical_present": bool(missing_soup.find("link", rel="canonical")),
                "root_relative_styles": all(tag.get("href", "").startswith("/") for tag in missing_soup.find_all("link", rel="stylesheet")),
                "root_relative_scripts": all(tag.get("src", "").startswith("/") for tag in missing_soup.find_all("script", src=True)),
                "headers": dict(missing_live.headers),
            },
        }
        (raw / "auxiliary-responses.json").write_text(json.dumps(auxiliary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
