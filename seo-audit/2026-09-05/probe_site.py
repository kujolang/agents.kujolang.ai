#!/usr/bin/env python3
"""Probe production delivery variants, crawler access, and external links."""

from __future__ import annotations

import argparse
import csv
import json
import socket
import ssl
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from datetime import datetime, timezone
from pathlib import Path


REDIRECT_FIELDS = [
    "phase", "source_url", "source_variant", "http_status", "target_url",
    "chain_length", "final_status", "canonical_target", "query_preserved",
    "verification", "issues",
]

CRAWLER_FIELDS = [
    "phase", "crawler", "category", "user_agent", "robots_allowed",
    "robots_status", "homepage_status", "key_page_status", "sitemap_status",
    "cdn_waf_result", "policy", "evidence", "issues",
]

LINK_FIELDS = [
    "phase", "source_url", "destination_url", "anchor_text", "link_context",
    "http_status", "final_url", "chain_length", "verification", "rel",
    "recommended_action",
]


class ChainHandler(urllib.request.HTTPRedirectHandler):
    def __init__(self):
        self.chain: list[dict] = []

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        self.chain.append({"status": code, "source": req.full_url, "target": newurl})
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def request(url: str, user_agent: str, timeout: int = 15) -> dict:
    chain_handler = ChainHandler()
    opener = urllib.request.build_opener(chain_handler, urllib.request.HTTPSHandler(context=ssl.create_default_context()))
    req = urllib.request.Request(url, headers={"User-Agent": user_agent})
    try:
        with opener.open(req, timeout=timeout) as response:
            return {
                "requested_url": url, "status": response.status, "final_url": response.geturl(),
                "chain": chain_handler.chain, "headers": dict(response.headers.items()), "error": "",
            }
    except urllib.error.HTTPError as error:
        return {
            "requested_url": url, "status": error.code, "final_url": error.geturl(),
            "chain": chain_handler.chain, "headers": dict(error.headers.items()) if error.headers else {},
            "error": str(error),
        }
    except Exception as error:
        return {
            "requested_url": url, "status": "", "final_url": url,
            "chain": chain_handler.chain, "headers": {}, "error": str(error),
        }


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def redirects(
    origin: str,
    phase: str,
    key_path: str,
    probe_www: bool,
    feed_path: str | None,
) -> tuple[list[dict], dict]:
    host = urllib.parse.urlparse(origin).netloc
    key_path = "/" + key_path.strip("/") + "/"
    flat_alias = key_path.rstrip("/") + ".html"
    variants = [
        (f"http://{host}/", "apex HTTP"),
        (f"https://{host}/", "apex HTTPS"),
        (f"https://{host}{key_path}", "nested canonical"),
        (f"https://{host}{key_path.rstrip('/')}", "nested no trailing slash"),
        (f"https://{host}{flat_alias}", "flat HTML alias"),
        (f"https://{host}{key_path}?audit=1", "query string"),
        (f"https://{host}/robots.txt", "robots"),
        (f"https://{host}/sitemap.xml", "sitemap"),
        (f"https://{host}/llms.txt", "llms experimental"),
        (f"https://{host}/seo-audit-missing-route-20260810/", "404"),
    ]
    if probe_www:
        variants[2:2] = [
            (f"http://www.{host}/", "www HTTP"),
            (f"https://www.{host}/", "www HTTPS"),
        ]
    if feed_path:
        variants.insert(-2, (f"https://{host}/" + feed_path.strip("/"), "feed"))
    receipts = {}
    rows = []
    canonical_host = f"https://{host}"
    for url, label in variants:
        receipt = request(url, "KujolangSEOAudit/1.0")
        receipts[url] = receipt
        first_status = receipt["chain"][0]["status"] if receipt["chain"] else receipt["status"]
        final_url = receipt["final_url"]
        source_query = urllib.parse.urlparse(url).query
        final_query = urllib.parse.urlparse(final_url).query
        query_preserved = "n/a" if not source_query else ("yes" if source_query == final_query else "no")
        issues = []
        if label in {"apex HTTP", "www HTTP", "www HTTPS", "nested no trailing slash"}:
            if first_status not in (301, 308):
                issues.append("non-permanent or missing canonical redirect")
        if label == "flat HTML alias" and receipt["status"] != 404:
            issues.append("retired flat alias did not return 404")
        if label == "404" and receipt["status"] != 404:
            issues.append("unexpected missing-route status")
        if receipt["status"] not in (200, 404):
            issues.append("unexpected final status")
        rows.append({
            "phase": phase, "source_url": url, "source_variant": label,
            "http_status": first_status, "target_url": final_url,
            "chain_length": len(receipt["chain"]), "final_status": receipt["status"],
            "canonical_target": "n/a" if label in {"flat HTML alias", "404"} else ("yes" if final_url.startswith(canonical_host) else "no"),
            "query_preserved": query_preserved,
            "verification": "live request with redirects followed",
            "issues": "; ".join(issues + ([receipt["error"]] if receipt["error"] and not (label in {"404", "flat HTML alias"} and receipt["status"] == 404) else [])),
        })
    return rows, receipts


def crawler_access(origin: str, phase: str, key_path: str) -> tuple[list[dict], dict]:
    bots = [
        ("Googlebot", "search indexing", "Googlebot"),
        ("Bingbot", "search indexing and grounding", "bingbot"),
        ("OAI-SearchBot", "AI search indexing", "OAI-SearchBot"),
        ("ChatGPT-User", "user-triggered fetch", "ChatGPT-User"),
        ("GPTBot", "model training", "GPTBot"),
        ("Claude-SearchBot", "AI search indexing", "Claude-SearchBot"),
        ("Claude-User", "user-triggered fetch", "Claude-User"),
        ("ClaudeBot", "model training", "ClaudeBot"),
        ("PerplexityBot", "AI search indexing", "PerplexityBot"),
        ("Perplexity-User", "user-triggered fetch", "Perplexity-User"),
    ]
    robots_url = origin + "/robots.txt"
    try:
        robot_parser = urllib.robotparser.RobotFileParser(robots_url)
        robot_parser.read()
    except Exception:
        robot_parser = None
    rows, receipts = [], {}
    key_url = origin + "/" + key_path.strip("/") + "/"
    for name, category, agent in bots:
        bot_receipts = {
            "robots": request(robots_url, agent),
            "homepage": request(origin + "/", agent),
            "key_page": request(key_url, agent),
            "sitemap": request(origin + "/sitemap.xml", agent),
        }
        receipts[name] = bot_receipts
        statuses = [bot_receipts[key]["status"] for key in ("robots", "homepage", "key_page", "sitemap")]
        allowed = robot_parser.can_fetch(agent, key_url) if robot_parser else None
        issue = "" if statuses == [200, 200, 200, 200] else "one or more live requests did not return 200"
        policy = "robots allow" if allowed else ("robots disallow" if allowed is False else "robots policy unknown")
        if "training" in category:
            policy += "; training policy unchanged"
        rows.append({
            "phase": phase, "crawler": name, "category": category, "user_agent": agent,
            "robots_allowed": "yes" if allowed else ("no" if allowed is False else "unknown"),
            "robots_status": statuses[0], "homepage_status": statuses[1],
            "key_page_status": statuses[2], "sitemap_status": statuses[3],
            "cdn_waf_result": "accessible" if statuses == [200, 200, 200, 200] else "blocked or indeterminate",
            "policy": policy, "evidence": "live requests plus robots.txt parsing", "issues": issue,
        })
    return rows, receipts


def probe_external_links(audit: Path, phase: str) -> tuple[list[dict], dict]:
    path = audit / "external-links.csv"
    if not path.exists():
        return [], {}
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    unique_urls = sorted({row["destination_url"] for row in rows})
    receipts = {url: request(url, "Mozilla/5.0 (compatible; KujolangSEOAudit/1.0)") for url in unique_urls}
    for row in rows:
        receipt = receipts[row["destination_url"]]
        status = receipt["status"]
        row["phase"] = phase
        row["http_status"] = status
        row["final_url"] = receipt["final_url"]
        row["chain_length"] = len(receipt["chain"])
        if status in (401, 403, 405, 429) or status == "":
            row["verification"] = "blocked or indeterminate"
            row["recommended_action"] = "manual verification only if business-critical"
        elif status in (404, 410):
            row["verification"] = "confirmed unavailable by live request"
            row["recommended_action"] = "review destination"
        else:
            row["verification"] = "live request"
            row["recommended_action"] = "none"
    write_csv(path, LINK_FIELDS, rows)
    broken_path = audit / "broken-links.csv"
    broken = list(csv.DictReader(broken_path.open(encoding="utf-8"))) if broken_path.exists() else []
    broken.extend(row for row in rows if str(row["http_status"]) in {"404", "410"})
    write_csv(broken_path, LINK_FIELDS, broken)
    return rows, receipts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit-dir", required=True)
    parser.add_argument("--origin", default="https://kujolang.ai")
    parser.add_argument("--phase", choices=("baseline", "after"), required=True)
    parser.add_argument("--skip-external", action="store_true")
    parser.add_argument("--key-path", default="/ecosystem/kujo/", help="Canonical nested page used for redirect and crawler checks")
    parser.add_argument("--skip-www", action="store_true", help="Skip www.<host> probes when that hostname is not part of the site contract")
    parser.add_argument("--feed-path", default="/feed/index.xml", help="Expected feed path; pass an empty value when the site has no feed")
    args = parser.parse_args()
    audit = Path(args.audit_dir).resolve()
    origin = args.origin.rstrip("/")
    redirect_rows, redirect_receipts = redirects(
        origin, args.phase, args.key_path, not args.skip_www, args.feed_path or None
    )
    crawler_rows, crawler_receipts = crawler_access(origin, args.phase, args.key_path)
    external_rows, external_receipts = ([], {}) if args.skip_external else probe_external_links(audit, args.phase)
    write_csv(audit / "redirects.csv", REDIRECT_FIELDS, redirect_rows)
    write_csv(audit / "crawler-access.csv", CRAWLER_FIELDS, crawler_rows)
    raw = audit / "raw" / "live"
    raw.mkdir(parents=True, exist_ok=True)
    dns = {}
    hostnames = [urllib.parse.urlparse(origin).netloc]
    if not args.skip_www:
        hostnames.append("www." + urllib.parse.urlparse(origin).netloc)
    for hostname in hostnames:
        try:
            dns[hostname] = sorted({item[4][0] for item in socket.getaddrinfo(hostname, 443)})
        except Exception as error:
            dns[hostname] = {"error": str(error)}
    receipt = {
        "phase": args.phase, "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "dns": dns, "redirects": redirect_receipts, "crawlers": crawler_receipts,
        "external_links": external_receipts,
    }
    (raw / f"{args.phase}-production-diagnostics.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "redirect_variants": len(redirect_rows),
        "redirect_issues": sum(1 for row in redirect_rows if row["issues"]),
        "crawler_profiles": len(crawler_rows),
        "crawler_access_issues": sum(1 for row in crawler_rows if row["issues"]),
        "external_links": len(external_rows),
        "unique_external_destinations": len(external_receipts),
        "confirmed_external_404_or_410": sum(1 for row in external_rows if str(row["http_status"]) in {"404", "410"}),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
