#!/usr/bin/env python3
"""Normalize saved Lighthouse JSON receipts into performance.csv."""

from __future__ import annotations

import csv
import json
from pathlib import Path


AUDIT_ROOT = Path(__file__).resolve().parent / "2026-08-10"
FIELDS = [
    "phase", "url", "template", "run_date", "environment", "lighthouse_version",
    "html_bytes", "css_bytes", "js_bytes", "image_bytes", "font_bytes", "requests",
    "lcp_ms", "inp_ms", "cls", "ttfb_ms", "source", "notes",
]
TEMPLATES = {
    "home": "home",
    "agents": "agent directory",
    "agent-detail": "agent detail",
}


def summary_map(payload: dict) -> dict:
    items = payload["audits"].get("resource-summary", {}).get("details", {}).get("items", [])
    return {item["resourceType"]: item for item in items}


rows = []
for phase in ("baseline", "after"):
    for slug, template in TEMPLATES.items():
        path = AUDIT_ROOT / "raw" / phase / f"lighthouse-{slug}.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        resources = summary_map(payload)
        audits = payload["audits"]
        inp = audits.get("interaction-to-next-paint", {}).get("numericValue")
        notes = {
            "performance_score": round(payload["categories"]["performance"]["score"] * 100),
            "seo_score": round(payload["categories"]["seo"]["score"] * 100),
            "accessibility_score": round(payload["categories"]["accessibility"]["score"] * 100),
            "best_practices_score": round(payload["categories"]["best-practices"]["score"] * 100),
            "total_blocking_time_ms": audits["total-blocking-time"]["numericValue"],
            "speed_index_ms": audits["speed-index"]["numericValue"],
            "lab_only": True,
        }
        rows.append({
            "phase": phase,
            "url": payload.get("finalDisplayedUrl", payload.get("finalUrl", "")),
            "template": template,
            "run_date": payload["fetchTime"],
            "environment": "Lighthouse mobile lab run against production",
            "lighthouse_version": payload["lighthouseVersion"],
            "html_bytes": resources.get("document", {}).get("transferSize", ""),
            "css_bytes": resources.get("stylesheet", {}).get("transferSize", ""),
            "js_bytes": resources.get("script", {}).get("transferSize", ""),
            "image_bytes": resources.get("image", {}).get("transferSize", ""),
            "font_bytes": resources.get("font", {}).get("transferSize", ""),
            "requests": resources.get("total", {}).get("requestCount", ""),
            "lcp_ms": audits["largest-contentful-paint"]["numericValue"],
            "inp_ms": inp if inp is not None else "NOT AVAILABLE — DATA ACCESS REQUIRED",
            "cls": audits["cumulative-layout-shift"]["numericValue"],
            "ttfb_ms": audits["server-response-time"]["numericValue"],
            "source": str(path.relative_to(AUDIT_ROOT)),
            "notes": json.dumps(notes, separators=(",", ":")),
        })

with (AUDIT_ROOT / "performance.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
