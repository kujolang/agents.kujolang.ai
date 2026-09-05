#!/usr/bin/env python3
"""Create reproducible SEO crawl datasets from a generated Kujo site.

The script intentionally uses the rendered output as its primary evidence layer.
It emits the stable CSV fields used by the repository's dated SEO audits and can
optionally probe the production equivalent of every canonical route.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path

from bs4 import BeautifulSoup


INVENTORY_FIELDS = [
    "phase", "url", "source_file", "page_type", "local_status",
    "production_status", "indexable", "robots_directives", "canonical",
    "canonical_target_status", "title", "title_length", "meta_description",
    "description_length", "h1", "heading_structure", "word_count", "lang",
    "published_date", "modified_date", "author", "breadcrumbs", "schema_types",
    "internal_inbound_links", "internal_outbound_links", "external_outbound_links",
    "broken_internal_links", "broken_external_links", "image_count", "missing_alt",
    "missing_dimensions", "page_depth", "orphan", "sitemap_included",
    "duplicate_title", "duplicate_description", "content_hash", "issues",
]

LINK_FIELDS = [
    "phase", "source_url", "destination_url", "anchor_text", "link_context",
    "http_status", "final_url", "chain_length", "verification", "rel",
    "recommended_action",
]

IMAGE_FIELDS = [
    "phase", "source_url", "image_url", "source_file", "alt", "width", "height",
    "loading", "format", "bytes", "exists", "srcset", "sizes",
    "responsive_candidates", "responsive_missing", "issues",
]

SCHEMA_FIELDS = [
    "phase", "url", "block", "parse_state", "schema_types", "visible_alignment",
    "rich_result_eligibility", "issues",
]

INDEXABILITY_FIELDS = [
    "phase", "url", "local_status", "production_status", "robots_directives",
    "canonical", "canonical_target_status", "sitemap_included", "indexable", "issues",
]

CRAWLABILITY_FIELDS = [
    "phase", "url", "page_depth", "internal_inbound_links", "orphan",
    "broken_internal_links", "robots_allowed", "issues",
]

METADATA_FIELDS = [
    "phase", "url", "title", "title_length", "duplicate_title", "meta_description",
    "description_length", "duplicate_description", "h1", "h1_count", "canonical",
    "lang", "og_title", "og_description", "og_url", "og_image", "twitter_card",
    "author", "issues",
]

CONTENT_FIELDS = [
    "phase", "url", "page_type", "purpose", "audience", "intent", "topic_entity",
    "word_count", "original_evidence", "currentness", "citation_worthiness",
    "competing_url", "gap", "action",
]


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def first_meta(soup: BeautifulSoup, *, name: str | None = None, prop: str | None = None) -> str:
    attrs = {"name": name} if name else {"property": prop}
    tag = soup.find("meta", attrs=attrs)
    return clean_text(tag.get("content", "")) if tag else ""


def canonical_route_for_file(output: Path, html_file: Path) -> str:
    rel = html_file.relative_to(output).as_posix()
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[: -len("index.html")]
    return "/" + rel


def local_file_for_url(output: Path, url: str, origin: str) -> Path | None:
    parsed = urllib.parse.urlparse(url)
    if parsed.netloc and parsed.netloc != urllib.parse.urlparse(origin).netloc:
        return None
    path = urllib.parse.unquote(parsed.path or "/")
    candidates = []
    if path == "/":
        candidates.append(output / "index.html")
    else:
        clean = path.lstrip("/")
        candidates.extend([output / clean, output / clean / "index.html"])
        if not Path(clean).suffix:
            candidates.append(output / f"{clean.rstrip('/')}" / "index.html")
            candidates.append(output / f"{clean.rstrip('/')}.html")
    return next((candidate for candidate in candidates if candidate.is_file()), None)


def parse_sitemap(output: Path) -> set[str]:
    sitemap = output / "sitemap.xml"
    if not sitemap.exists():
        return set()
    root = ET.parse(sitemap).getroot()
    return {
        clean_text(node.text or "")
        for node in root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
    }


def source_map(repo: Path) -> dict[str, str]:
    result = {
        "/": "templates/page-home.html",
        "/ecosystem/": "templates/page-ecosystem.html",
        "/ecosystem/primitives/": "templates/page-ecosystem-section.html",
        "/ecosystem/tooling/": "templates/page-ecosystem-section.html",
        "/ecosystem/showcase/": "templates/page-ecosystem-section.html",
        "/writing/": "templates/page-writing.html",
    }
    for source in sorted((repo / "content").glob("**/*.md")):
        text = source.read_text(encoding="utf-8")
        match = re.search(r"^custom_url:\s*[\"']?([^\"'\n]+)", text, re.MULTILINE)
        if not match:
            continue
        slug = match.group(1).strip()
        collection = source.parent.name
        prefix = f"/ecosystem/{collection}/" if collection in {"skills", "workflows"} else ("/ecosystem/" if collection == "ecosystem" else "/")
        result[f"{prefix}{slug}/"] = source.relative_to(repo).as_posix()
    return result


def page_type(route: str) -> str:
    if route == "/":
        return "home"
    if route in {"/ecosystem/", "/ecosystem/primitives/", "/ecosystem/tooling/", "/ecosystem/showcase/", "/ecosystem/skills/", "/ecosystem/workflows/"}:
        return "collection"
    if route.startswith("/ecosystem/"):
        return "software-detail"
    if route == "/writing/":
        return "writing-index"
    return "page"


def schema_type_values(value) -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        current = value.get("@type")
        if isinstance(current, list):
            found.extend(str(item) for item in current)
        elif current:
            found.append(str(current))
        for nested in value.values():
            found.extend(schema_type_values(nested))
    elif isinstance(value, list):
        for nested in value:
            found.extend(schema_type_values(nested))
    return found


def context_for_link(tag) -> str:
    parent = tag.find_parent(["nav", "header", "footer", "main", "article", "aside"])
    return parent.name if parent else "body"


def probe(url: str, user_agent: str = "KujolangSEOAudit/1.0", timeout: int = 12) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": user_agent})
    context = ssl.create_default_context()
    try:
        with urllib.request.urlopen(request, timeout=timeout, context=context) as response:
            return {
                "status": response.status,
                "final_url": response.geturl(),
                "headers": dict(response.headers.items()),
                "error": "",
            }
    except urllib.error.HTTPError as error:
        return {
            "status": error.code,
            "final_url": error.geturl(),
            "headers": dict(error.headers.items()) if error.headers else {},
            "error": str(error),
        }
    except Exception as error:  # Network evidence should be preserved, not fatal.
        return {"status": "", "final_url": url, "headers": {}, "error": str(error)}


def normalize_internal_url(url: str, origin: str) -> str:
    parsed = urllib.parse.urlparse(url)
    origin_parts = urllib.parse.urlparse(origin)
    if parsed.netloc != origin_parts.netloc:
        return url
    path = parsed.path or "/"
    if path.endswith("/index.html"):
        path = path[: -len("index.html")]
    return urllib.parse.urlunparse((origin_parts.scheme, origin_parts.netloc, path, "", parsed.query, ""))


def infer_content_fields(row: dict) -> dict:
    kind = row["page_type"]
    if kind == "home":
        purpose, intent, topic = "Introduce Kujo and route visitors", "brand/category", "Kujo programming language"
    elif kind == "collection":
        purpose, intent, topic = "Explain and index the ecosystem", "exploration", "Kujo ecosystem"
    elif kind == "software-detail":
        purpose, intent, topic = "Explain one Kujo project and link its source", "technical adoption", row["h1"]
    elif kind == "writing-index":
        purpose, intent, topic = "List Kujo technical writing", "informational", "Kujo writing"
    else:
        purpose, intent, topic = "Explain a Kujo site topic", "informational", row["h1"]
    evidence = "Repository/source links and explicit operating boundaries" if kind == "software-detail" else "First-party project information"
    if kind == "writing-index" and row["word_count"] < 100:
        evidence = "No published articles"
    return {
        "phase": row["phase"], "url": row["url"], "page_type": kind,
        "purpose": purpose, "audience": "Developers and AI-software teams",
        "intent": intent, "topic_entity": topic, "word_count": row["word_count"],
        "original_evidence": evidence, "currentness": "No rendered modified date",
        "citation_worthiness": "Medium" if kind == "software-detail" else "Low to medium",
        "competing_url": "", "gap": "Measurement/editorial review required",
        "action": "Preserve factual specificity; add dated primary evidence when available",
    }


def crawl(args: argparse.Namespace) -> None:
    repo = Path(args.repo).resolve()
    output = Path(args.output).resolve()
    audit = Path(args.audit_dir).resolve()
    origin = args.origin.rstrip("/")
    sitemap_urls = parse_sitemap(output)
    sources = source_map(repo)
    canonical_files = [output / "index.html"] + sorted(
        path for path in output.rglob("index.html") if path != output / "index.html"
    )
    canonical_files = [path for path in canonical_files if path.is_file()]

    pages: list[dict] = []
    links: list[dict] = []
    images: list[dict] = []
    schema_rows: list[dict] = []
    outbound_internal: dict[str, list[str]] = defaultdict(list)
    production_receipts: dict[str, dict] = {}

    for html_file in canonical_files:
        route = canonical_route_for_file(output, html_file)
        url = origin + route
        soup = BeautifulSoup(html_file.read_text(encoding="utf-8"), "lxml")
        canonical_tag = soup.find("link", rel=lambda value: value and "canonical" in value)
        canonical = clean_text(canonical_tag.get("href", "")) if canonical_tag else ""
        robots = first_meta(soup, name="robots")
        title = clean_text(soup.title.get_text(" ")) if soup.title else ""
        description = first_meta(soup, name="description")
        author = first_meta(soup, name="author")
        h1_tags = soup.find_all("h1")
        h1 = " | ".join(clean_text(tag.get_text(" ")) for tag in h1_tags)
        headings = [f"{tag.name.upper()}:{clean_text(tag.get_text(' '))}" for tag in soup.find_all(re.compile("^h[1-6]$"))]
        content_soup = BeautifulSoup(str(soup), "lxml")
        for tag in content_soup.find_all(["script", "style", "nav", "header", "footer", "button"]):
            tag.decompose()
        visible_text = clean_text(content_soup.get_text(" "))
        words = re.findall(r"\b[\w][\w'-]*\b", visible_text)

        page_schema_types: list[str] = []
        schema_blocks = soup.find_all("script", attrs={"type": "application/ld+json"})
        for block_index, block in enumerate(schema_blocks, start=1):
            parse_state, types, schema_issues = "valid JSON", [], ""
            try:
                payload = json.loads(block.string or block.get_text())
                types = sorted(set(schema_type_values(payload)))
            except Exception as error:
                parse_state, schema_issues = "invalid JSON", str(error)
            page_schema_types.extend(types)
            schema_rows.append({
                "phase": args.phase, "url": url, "block": block_index,
                "parse_state": parse_state, "schema_types": "|".join(types),
                "visible_alignment": "manual review required",
                "rich_result_eligibility": "Not inferred from Schema.org validity",
                "issues": schema_issues,
            })

        for anchor in soup.find_all("a", href=True):
            raw = anchor.get("href", "").strip()
            if not raw or raw.startswith(("#", "mailto:", "tel:", "javascript:")):
                continue
            absolute = urllib.parse.urljoin(url, raw)
            parsed = urllib.parse.urlparse(absolute)
            is_internal = parsed.netloc == urllib.parse.urlparse(origin).netloc
            destination = normalize_internal_url(absolute, origin) if is_internal else absolute
            local_target = local_file_for_url(output, destination, origin) if is_internal else None
            status = 200 if local_target else (404 if is_internal else "")
            verification = "rendered local route" if is_internal else "not probed in crawl"
            action = "fix or remove" if is_internal and not local_target else "none"
            row = {
                "phase": args.phase, "source_url": url, "destination_url": destination,
                "anchor_text": clean_text(anchor.get_text(" ") or anchor.get("aria-label", "")),
                "link_context": context_for_link(anchor), "http_status": status,
                "final_url": destination, "chain_length": 0,
                "verification": verification, "rel": " ".join(anchor.get("rel", [])),
                "recommended_action": action,
            }
            links.append(row)
            if is_internal:
                outbound_internal[url].append(destination.split("?", 1)[0])

        rendered_images = [image for image in soup.find_all("img") if image.get("src", "").strip()]
        for image in rendered_images:
            raw_src = image.get("src", "").strip()
            image_url = urllib.parse.urljoin(url, raw_src)
            local_image = local_file_for_url(output, image_url, origin)
            width, height = image.get("width", ""), image.get("height", "")
            raw_srcset = image.get("srcset", "").strip()
            responsive_urls = [
                urllib.parse.urljoin(url, candidate.strip().split()[0])
                for candidate in raw_srcset.split(",")
                if candidate.strip()
            ]
            missing_responsive = [
                candidate for candidate in responsive_urls
                if urllib.parse.urlparse(candidate).netloc == urllib.parse.urlparse(origin).netloc
                and not local_file_for_url(output, candidate, origin)
            ]
            issue_parts = []
            if image.get("alt") is None:
                issue_parts.append("missing alt attribute")
            if not width or not height:
                issue_parts.append("missing intrinsic dimensions")
            if not local_image:
                issue_parts.append("missing local asset")
            if missing_responsive:
                issue_parts.append("missing responsive candidate")
            images.append({
                "phase": args.phase, "source_url": url, "image_url": image_url,
                "source_file": local_image.relative_to(output).as_posix() if local_image else "",
                "alt": image.get("alt", ""), "width": width, "height": height,
                "loading": image.get("loading", ""),
                "format": local_image.suffix.lstrip(".") if local_image else Path(raw_src).suffix.lstrip("."),
                "bytes": local_image.stat().st_size if local_image else "",
                "exists": bool(local_image), "srcset": raw_srcset,
                "sizes": image.get("sizes", ""),
                "responsive_candidates": len(responsive_urls),
                "responsive_missing": len(missing_responsive),
                "issues": "; ".join(issue_parts),
            })

        production_status = ""
        if args.probe_production:
            receipt = probe(url)
            production_receipts[url] = receipt
            production_status = receipt["status"]

        page_issues = []
        if not title:
            page_issues.append("missing title")
        if not description:
            page_issues.append("missing description")
        if len(h1_tags) != 1:
            page_issues.append(f"h1 count {len(h1_tags)}")
        if canonical != url:
            page_issues.append("canonical mismatch")
        if "noindex" in robots.lower():
            page_issues.append("noindex")

        pages.append({
            "phase": args.phase, "url": url, "source_file": sources.get(route, "generated route"),
            "page_type": page_type(route), "local_status": 200,
            "production_status": production_status,
            "indexable": "no" if "noindex" in robots.lower() else "yes",
            "robots_directives": robots or "default index,follow", "canonical": canonical,
            "canonical_target_status": 200 if local_file_for_url(output, canonical, origin) else 404,
            "title": title, "title_length": len(title), "meta_description": description,
            "description_length": len(description), "h1": h1,
            "h1_count": len(h1_tags), "heading_structure": " > ".join(headings),
            "word_count": len(words), "lang": soup.html.get("lang", "") if soup.html else "",
            "published_date": first_meta(soup, prop="article:published_time"),
            "modified_date": first_meta(soup, prop="article:modified_time"), "author": author,
            "breadcrumbs": "yes" if soup.find(attrs={"aria-label": re.compile("breadcrumb", re.I)}) else "no",
            "schema_types": "|".join(sorted(set(page_schema_types))),
            "internal_inbound_links": 0, "internal_outbound_links": len(outbound_internal[url]),
            "external_outbound_links": sum(
                1 for link in links if link["source_url"] == url and urllib.parse.urlparse(link["destination_url"]).netloc != urllib.parse.urlparse(origin).netloc
            ),
            "broken_internal_links": sum(
                1 for link in links if link["source_url"] == url and link["http_status"] == 404
            ),
            "broken_external_links": "NOT AVAILABLE — DATA ACCESS REQUIRED",
            "image_count": len(rendered_images),
            "missing_alt": sum(1 for image in rendered_images if image.get("alt") is None),
            "missing_dimensions": sum(1 for image in rendered_images if not image.get("width") or not image.get("height")),
            "page_depth": 0 if route == "/" else len([part for part in route.split("/") if part]),
            "orphan": "", "sitemap_included": "yes" if url in sitemap_urls else "no",
            "duplicate_title": "", "duplicate_description": "",
            "content_hash": hashlib.sha256(visible_text.encode()).hexdigest(),
            "issues": "; ".join(page_issues),
            "og_title": first_meta(soup, prop="og:title"),
            "og_description": first_meta(soup, prop="og:description"),
            "og_url": first_meta(soup, prop="og:url"), "og_image": first_meta(soup, prop="og:image"),
            "twitter_card": first_meta(soup, name="twitter:card"),
        })

    page_urls = {row["url"] for row in pages}
    inbound = Counter()
    for destinations in outbound_internal.values():
        for destination in destinations:
            if destination in page_urls:
                inbound[destination] += 1

    depths = {origin + "/": 0}
    queue = deque([origin + "/"])
    while queue:
        current = queue.popleft()
        for destination in outbound_internal.get(current, []):
            if destination in page_urls and destination not in depths:
                depths[destination] = depths[current] + 1
                queue.append(destination)

    title_counts = Counter(row["title"].lower() for row in pages if row["title"])
    description_counts = Counter(row["meta_description"].lower() for row in pages if row["meta_description"])
    for row in pages:
        row["internal_inbound_links"] = inbound[row["url"]]
        row["page_depth"] = depths.get(row["url"], row["page_depth"])
        row["orphan"] = "yes" if row["url"] != origin + "/" and inbound[row["url"]] == 0 else "no"
        row["duplicate_title"] = "yes" if title_counts[row["title"].lower()] > 1 else "no"
        row["duplicate_description"] = "yes" if description_counts[row["meta_description"].lower()] > 1 else "no"
        if row["orphan"] == "yes":
            row["issues"] = "; ".join(filter(None, [row["issues"], "orphan page"]))
        if row["sitemap_included"] == "no":
            row["issues"] = "; ".join(filter(None, [row["issues"], "not in sitemap"]))

    metadata_rows = []
    indexability_rows = []
    crawlability_rows = []
    content_rows = []
    for row in pages:
        metadata_issues = []
        if not row["title"]:
            metadata_issues.append("missing title")
        if not row["meta_description"]:
            metadata_issues.append("missing description")
        if row["duplicate_title"] == "yes":
            metadata_issues.append("duplicate title")
        if row["duplicate_description"] == "yes":
            metadata_issues.append("duplicate description")
        if row["h1_count"] != 1:
            metadata_issues.append(f"h1 count {row['h1_count']}")
        metadata_rows.append({**row, "issues": "; ".join(metadata_issues)})
        indexability_rows.append({**row, "issues": row["issues"]})
        crawlability_rows.append({
            **row, "robots_allowed": "yes",
            "issues": "; ".join(filter(None, ["orphan" if row["orphan"] == "yes" else "", "broken internal links" if row["broken_internal_links"] else ""])),
        })
        content_rows.append(infer_content_fields(row))

    write_csv(audit / f"{args.phase}.csv", INVENTORY_FIELDS, pages)
    if args.phase == "baseline":
        write_csv(audit / "site-inventory.csv", INVENTORY_FIELDS, pages)
    write_csv(audit / "metadata-audit.csv", METADATA_FIELDS, metadata_rows)
    write_csv(audit / "content-audit.csv", CONTENT_FIELDS, content_rows)
    write_csv(audit / "internal-links.csv", LINK_FIELDS, [row for row in links if urllib.parse.urlparse(row["destination_url"]).netloc == urllib.parse.urlparse(origin).netloc])
    write_csv(audit / "external-links.csv", LINK_FIELDS, [row for row in links if urllib.parse.urlparse(row["destination_url"]).netloc != urllib.parse.urlparse(origin).netloc])
    write_csv(audit / "broken-links.csv", LINK_FIELDS, [row for row in links if row["http_status"] == 404])
    write_csv(audit / "image-audit.csv", IMAGE_FIELDS, images)
    write_csv(audit / "schema-audit.csv", SCHEMA_FIELDS, schema_rows)
    write_csv(audit / "indexability.csv", INDEXABILITY_FIELDS, indexability_rows)
    write_csv(audit / "crawlability.csv", CRAWLABILITY_FIELDS, crawlability_rows)

    issue_counts = Counter()
    for row in pages:
        for issue in filter(None, row["issues"].split("; ")):
            issue_counts[issue] += 1
    summary = {
        "phase": args.phase,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "origin": origin,
        "canonical_pages": len(pages),
        "production_200_pages": sum(1 for row in pages if row["production_status"] == 200),
        "indexable_pages": sum(1 for row in pages if row["indexable"] == "yes"),
        "sitemap_urls": len(sitemap_urls),
        "missing_titles": sum(1 for row in pages if not row["title"]),
        "duplicate_titles": sum(1 for row in pages if row["duplicate_title"] == "yes"),
        "missing_descriptions": sum(1 for row in pages if not row["meta_description"]),
        "duplicate_descriptions": sum(1 for row in pages if row["duplicate_description"] == "yes"),
        "h1_issues": sum(1 for row in pages if row["h1_count"] != 1),
        "missing_canonicals": sum(1 for row in pages if not row["canonical"]),
        "canonical_mismatches": sum(1 for row in pages if row["canonical"] != row["url"]),
        "broken_internal_links": sum(1 for row in links if row["http_status"] == 404),
        "orphan_pages": sum(1 for row in pages if row["orphan"] == "yes"),
        "pages_deeper_than_three_clicks": sum(1 for row in pages if int(row["page_depth"]) > 3),
        "images": len(images),
        "missing_alt": sum(1 for row in images if "missing alt" in row["issues"]),
        "missing_dimensions": sum(1 for row in images if "missing intrinsic dimensions" in row["issues"]),
        "responsive_images": sum(1 for row in images if row["responsive_candidates"]),
        "missing_responsive_candidates": sum(int(row["responsive_missing"]) for row in images),
        "schema_parse_errors": sum(1 for row in schema_rows if row["parse_state"] != "valid JSON"),
        "schema_coverage_pages": sum(1 for row in pages if row["schema_types"]),
        "issue_counts": dict(sorted(issue_counts.items())),
    }
    (audit / f"{args.phase}-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    if production_receipts:
        raw_dir = audit / "raw" / "live"
        raw_dir.mkdir(parents=True, exist_ok=True)
        (raw_dir / f"{args.phase}-page-probes.json").write_text(json.dumps(production_receipts, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--output", default="output")
    parser.add_argument("--audit-dir", required=True)
    parser.add_argument("--phase", choices=("baseline", "after"), required=True)
    parser.add_argument("--origin", default="https://kujolang.ai")
    parser.add_argument("--probe-production", action="store_true")
    args = parser.parse_args()
    crawl(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
