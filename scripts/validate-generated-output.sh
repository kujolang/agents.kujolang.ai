#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="${1:-output}"

if [[ ! -d "$OUT_DIR" ]]; then
	echo "ERROR: output directory not found: $OUT_DIR"
	exit 1
fi

failures=0
html_count=0

record_failure() {
	echo "$1"
	failures=$((failures + 1))
}

while IFS= read -r html_file; do
	html_count=$((html_count + 1))

	if ! grep -Eqi '^<!doctype html>' "$html_file"; then
		record_failure "FAIL doctype: $html_file"
	fi

	if ! grep -Eqi '<html[^>]* lang="[^"]+"' "$html_file"; then
		record_failure "FAIL html-lang: $html_file"
	fi

	if ! grep -Eqi '<main[ >]' "$html_file"; then
		record_failure "FAIL main-landmark: $html_file"
	fi

	if grep -Eqi '<a[^>]*></a>' "$html_file"; then
		record_failure "FAIL empty-link: $html_file"
	fi

	if grep -Eqi '<img[[:space:]][^>]*>' "$html_file"; then
		if grep -Eio '<img[[:space:]][^>]*>' "$html_file" | grep -Eiv ' alt="' >/dev/null; then
			record_failure "FAIL image-alt: $html_file"
		fi
		if grep -Eio '<img[[:space:]][^>]*>' "$html_file" | grep -Eiv ' width="[0-9]+"[^>]* height="[0-9]+"| height="[0-9]+"[^>]* width="[0-9]+"' >/dev/null; then
			record_failure "FAIL image-dimensions: $html_file"
		fi
	fi

	if grep -qi 'class="skip-link"' "$html_file"; then
		if ! grep -qi 'id="main-content"' "$html_file"; then
			record_failure "FAIL skip-link-target: $html_file"
		fi
	fi

done < <(find "$OUT_DIR" -name '*.html' -type f | sort)

if [[ -f "$OUT_DIR/404.html" ]]; then
	if ! grep -qi '<meta name="robots" content="noindex,follow">' "$OUT_DIR/404.html"; then
		record_failure "FAIL 404-indexability: missing noindex,follow"
	fi
	if grep -qi 'rel="canonical"' "$OUT_DIR/404.html"; then
		record_failure "FAIL 404-canonical: error page should not canonicalize to an indexable URL"
	fi
	if grep -Eq '(href|src)="(\.\.?/|assets/|agents/)' "$OUT_DIR/404.html"; then
		record_failure "FAIL 404-relative-resource: nested 404 requests require root-relative internal resources"
	fi
fi

if [[ -f "$OUT_DIR/agents/webops/index.html" ]]; then
	if ! grep -qi '<meta name="robots" content="noindex,follow">' "$OUT_DIR/agents/webops/index.html"; then
		record_failure "FAIL webops-indexability: placeholder collection must be noindex,follow"
	fi
	if [[ -f "$OUT_DIR/sitemap.xml" ]] && grep -q 'https://agents.kujolang.ai/agents/webops/' "$OUT_DIR/sitemap.xml"; then
		record_failure "FAIL webops-sitemap: noindex placeholder collection is in sitemap"
	fi
fi

if [[ "$html_count" -eq 0 ]]; then
	record_failure "FAIL no-html: no HTML files found in $OUT_DIR"
fi

if [[ -f "$OUT_DIR/sitemap.xml" ]]; then
	if ! grep -q '<urlset' "$OUT_DIR/sitemap.xml"; then
		record_failure "FAIL sitemap-format: $OUT_DIR/sitemap.xml"
	fi
fi

if [[ -f "$OUT_DIR/feed/index.xml" ]]; then
	if ! grep -q '<rss' "$OUT_DIR/feed/index.xml"; then
		record_failure "FAIL rss-format: $OUT_DIR/feed/index.xml"
	fi
fi

if [[ -f "$OUT_DIR/index.html" ]]; then
	if ! grep -q 'class="agent-carousel"' "$OUT_DIR/index.html"; then
		record_failure "FAIL agent-carousel: homepage does not render grouped agent carousels"
	fi
	if ! grep -q 'id="chain-of-command"' "$OUT_DIR/index.html"; then
		record_failure "FAIL agent-set: homepage does not render the Chain of Command set"
	fi
	if ! grep -q 'href="/agents/chain-of-command/">Chain of Command</a>' "$OUT_DIR/index.html" || ! grep -q 'href="/agents/webops/">WebOps</a>' "$OUT_DIR/index.html"; then
		record_failure "FAIL agent-navigation: homepage does not render both direct agent-set links"
	fi
	if grep -q 'site-nav-dropdown' "$OUT_DIR/index.html"; then
		record_failure "FAIL agent-navigation: homepage still renders the old Agents dropdown"
	fi
	if grep -q 'card-grid agent-grid' "$OUT_DIR/index.html"; then
		record_failure "FAIL homepage-grid: homepage still renders the old agent grid"
	fi
	if ! grep -q '/images/general-commander-' "$OUT_DIR/index.html"; then
		record_failure "FAIL demo-portrait: homepage does not render the original agent portrait assets"
	fi
fi

echo "Checked HTML files: $html_count"

if [[ "$failures" -gt 0 ]]; then
	echo "Validation failed: $failures issue(s)"
	exit 1
fi

echo "Validation passed"
