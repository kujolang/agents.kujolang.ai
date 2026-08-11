#!/usr/bin/env python3
"""Validate required audit artifacts and completion gates."""

from __future__ import annotations

import csv
import json
from pathlib import Path


root = Path(__file__).resolve().parent / "2026-08-10"
required = [
    "executive-summary.md", "methodology.md", "research-sources.md", "data-availability.md",
    "site-inventory.csv", "baseline.csv", "baseline-summary.json", "after.csv", "after-summary.json",
    "metadata-audit.csv", "content-audit.csv", "keyword-map.csv", "search-rankings.csv",
    "ai-search-benchmark.csv", "internal-links.csv", "external-links.csv", "broken-links.csv",
    "schema-audit.csv", "indexability.csv", "crawlability.csv", "crawler-access.csv",
    "performance.csv", "image-audit.csv", "redirects.csv", "issues.csv", "changes.md",
    "before-after.md", "unresolved.md", "recommendations.md",
]
missing = [name for name in required if not (root / name).is_file()]
assert not missing, f"Missing artifacts: {missing}"

for path in root.glob("*.csv"):
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert all(None not in row for row in rows), f"Malformed row in {path.name}"

baseline = json.loads((root / "baseline-summary.json").read_text(encoding="utf-8"))
after = json.loads((root / "after-summary.json").read_text(encoding="utf-8"))
assert baseline["pages_total"] == after["pages_total"] == 33
assert after["broken_internal_link_occurrences"] == 0
assert after["images_missing_alt"] == 0
assert after["images_missing_dimensions"] == 0
assert after["schema_parse_errors"] == 0
assert after["production_non_200"] == 0
assert after["production_content_mismatches"] == 0

with (root / "issues.csv").open(newline="", encoding="utf-8") as handle:
    issues = list(csv.DictReader(handle))
open_critical = [row["id"] for row in issues if row["severity"] in {"P0", "P1"} and row["status"] != "completed"]
assert not open_critical, f"Open P0/P1 issues: {open_critical}"

for phase in ("baseline", "after"):
    for slug in ("home", "agents", "agent-detail"):
        receipt = root / "raw" / phase / f"lighthouse-{slug}.json"
        payload = json.loads(receipt.read_text(encoding="utf-8"))
        assert payload["categories"]["seo"]["score"] == 1

assert (root / "raw" / "baseline-build" / "index.html").is_file()
assert (root / "raw" / "after-build" / "index.html").is_file()
print("Audit validation passed: 33 pages, 0 open P0/P1 issues, production matches generated output")
