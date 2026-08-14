#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="${1:-output}"

if [[ ! -d "$OUT_DIR" ]]; then
	echo "ERROR: output directory not found: $OUT_DIR"
	exit 1
fi

failures=0
html_count=0
social_images_file="$(mktemp)"
trap 'rm -f "$social_images_file"' EXIT

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

	social_image="$(grep -Eio '<meta property="og:image" content="[^"]+"' "$html_file" | sed -E 's/.*content="([^"]+)"/\1/' | head -n 1)"
	if [[ -z "$social_image" ]]; then
		record_failure "FAIL og-image: $html_file"
	else
		printf '%s\t%s\n' "$social_image" "$html_file" >> "$social_images_file"
		if [[ ! "$social_image" =~ ^https://agents\.kujolang\.ai/assets/images/social/[a-z0-9-]+\.jpg$ ]]; then
			record_failure "FAIL og-image-url: $html_file uses $social_image"
		else
			social_asset="${social_image#https://agents.kujolang.ai/}"
			if [[ ! -f "$OUT_DIR/$social_asset" ]]; then
				record_failure "FAIL og-image-file: $html_file references missing $OUT_DIR/$social_asset"
			fi
		fi
	fi

	for required_social_meta in 'og:image:type' 'og:image:width' 'og:image:height' 'og:image:alt' 'twitter:image' 'twitter:image:alt'; do
		if ! grep -Fq "$required_social_meta" "$html_file"; then
			record_failure "FAIL social-meta-$required_social_meta: $html_file"
		fi
	done

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
	if grep -qi '<meta name="robots" content="noindex' "$OUT_DIR/agents/webops/index.html"; then
		record_failure "FAIL webops-indexability: populated collection must be indexable"
	fi
	if [[ -f "$OUT_DIR/sitemap.xml" ]] && ! grep -q 'https://agents.kujolang.ai/agents/webops/' "$OUT_DIR/sitemap.xml"; then
		record_failure "FAIL webops-sitemap: populated collection is missing from sitemap"
	fi
	webops_count="$(find "$OUT_DIR/agents" -mindepth 2 -maxdepth 2 -name index.html -type f -exec grep -l 'WebOps' {} + | wc -l | tr -d ' ')"
	if [[ "$webops_count" -lt 28 ]]; then record_failure "FAIL webops-count: expected at least 28 individual WebOps pages, found $webops_count"; fi
	if ! grep -q 'class="card-grid agent-category-grid"' "$OUT_DIR/agents/webops/index.html"; then record_failure "FAIL webops-collection: missing agent card grid"; fi
	if grep -Eqi 'coming soon|placeholder|lorem ipsum' "$OUT_DIR/agents/webops/index.html"; then record_failure "FAIL webops-placeholder: collection contains placeholder copy"; fi
	if grep -q 'listing-card-image--mark' "$OUT_DIR/agents/webops/index.html"; then record_failure "FAIL webops-fallback-image: generic Kujo card image remains after portrait rollout"; fi
	webops_portraits="$(grep -Eo '/images/[a-z0-9-]+-[a-f0-9]{12}\.webp' "$OUT_DIR/agents/webops/index.html" | sort -u | wc -l | tr -d ' ')"
	if [[ "$webops_portraits" -lt 28 ]]; then record_failure "FAIL webops-portraits: expected 28 unique portraits, found $webops_portraits"; fi
	if ! grep -Eq 'alt="Agent image for Trend Scout"[^>]*loading="eager"[^>]*fetchpriority="high"' "$OUT_DIR/agents/webops/index.html"; then record_failure "FAIL webops-priority-image: first portrait is not prioritized"; fi
fi

if [[ -f "$OUT_DIR/agents/chain-of-command/index.html" ]] && ! grep -Eq 'alt="Agent image for General Commander"[^>]*loading="eager"[^>]*fetchpriority="high"' "$OUT_DIR/agents/chain-of-command/index.html"; then
	record_failure "FAIL chain-priority-image: first portrait is not prioritized"
fi

if [[ -f "$OUT_DIR/agents/index.html" ]]; then
	agent_directory_carousels="$(grep -o 'class="agent-carousel"' "$OUT_DIR/agents/index.html" | wc -l | tr -d ' ')"
	if [[ "$agent_directory_carousels" -ne 3 ]]; then record_failure "FAIL agent-directory-carousels: expected 3 agent-set carousels, found $agent_directory_carousels"; fi
	if grep -Eq 'data-agent-category-filter|data-agent-sort|class="agent-filter-bar"' "$OUT_DIR/agents/index.html"; then record_failure "FAIL agent-directory-filters: category or sort controls remain"; fi
	if [[ "$(grep -o 'data-carousel-prev' "$OUT_DIR/agents/index.html" | wc -l | tr -d ' ')" -ne 3 ]] || [[ "$(grep -o 'data-carousel-next' "$OUT_DIR/agents/index.html" | wc -l | tr -d ' ')" -ne 3 ]]; then record_failure "FAIL agent-directory-controls: expected previous and next controls for every set"; fi
	if ! grep -q '&lt;</button>' "$OUT_DIR/agents/index.html" || ! grep -q '&gt;</button>' "$OUT_DIR/agents/index.html"; then record_failure "FAIL agent-directory-control-symbols: carousel controls must use less-than and greater-than symbols"; fi
fi

if [[ -f "$OUT_DIR/agents/publishing-house/index.html" ]]; then
	if grep -qi '<meta name="robots" content="noindex' "$OUT_DIR/agents/publishing-house/index.html"; then record_failure "FAIL publishing-house-indexability: populated collection must be indexable"; fi
	if [[ -f "$OUT_DIR/sitemap.xml" ]] && ! grep -q 'https://agents.kujolang.ai/agents/publishing-house/' "$OUT_DIR/sitemap.xml"; then record_failure "FAIL publishing-house-sitemap: populated collection is missing from sitemap"; fi
	publishing_count="$(find "$OUT_DIR/agents" -mindepth 2 -maxdepth 2 -name index.html -type f -exec grep -l 'Publishing House' {} + | wc -l | tr -d ' ')"
	if [[ "$publishing_count" -lt 23 ]]; then record_failure "FAIL publishing-house-count: expected at least 23 individual Publishing House pages, found $publishing_count"; fi
	if ! grep -q 'class="card-grid agent-category-grid"' "$OUT_DIR/agents/publishing-house/index.html"; then record_failure "FAIL publishing-house-collection: missing agent card grid"; fi
	if grep -Eqi 'coming soon|placeholder|lorem ipsum' "$OUT_DIR/agents/publishing-house/index.html"; then record_failure "FAIL publishing-house-placeholder: collection contains placeholder copy"; fi
	if grep -q 'listing-card-image--mark' "$OUT_DIR/agents/publishing-house/index.html"; then record_failure "FAIL publishing-house-fallback-image: generic Kujo card image remains after portrait rollout"; fi
	publishing_portraits="$(grep -Eo '/images/[a-z0-9-]+-[a-f0-9]{12}\.webp' "$OUT_DIR/agents/publishing-house/index.html" | sort -u | wc -l | tr -d ' ')"
	if [[ "$publishing_portraits" -lt 23 ]]; then record_failure "FAIL publishing-house-portraits: expected 23 unique portraits, found $publishing_portraits"; fi
	if ! grep -Eq 'alt="Agent image for Publisher"[^>]*loading="eager"[^>]*fetchpriority="high"' "$OUT_DIR/agents/publishing-house/index.html"; then record_failure "FAIL publishing-house-priority-image: first agent image is not prioritized"; fi
fi

if [[ "$html_count" -eq 0 ]]; then
	record_failure "FAIL no-html: no HTML files found in $OUT_DIR"
fi

unique_social_images="$(cut -f1 "$social_images_file" | sort -u | wc -l | tr -d ' ')"
if [[ "$unique_social_images" -ne "$html_count" ]]; then
	record_failure "FAIL social-image-uniqueness: $html_count pages use $unique_social_images unique images"
fi

if [[ -f "$OUT_DIR/sitemap.xml" ]]; then
	if ! grep -q '<urlset' "$OUT_DIR/sitemap.xml"; then
		record_failure "FAIL sitemap-format: $OUT_DIR/sitemap.xml"
	fi
	for aggregate_url in 'https://agents.kujolang.ai/' 'https://agents.kujolang.ai/agents/' 'https://agents.kujolang.ai/agents/chain-of-command/' 'https://agents.kujolang.ai/agents/webops/' 'https://agents.kujolang.ai/agents/publishing-house/'; do
		if ! grep -A1 -F "<loc>$aggregate_url</loc>" "$OUT_DIR/sitemap.xml" | grep -Eq '<lastmod>[0-9]{4}-[0-9]{2}-[0-9]{2}</lastmod>'; then
			record_failure "FAIL sitemap-lastmod: $aggregate_url has no freshness date"
		fi
	done
fi

if [[ -f "$OUT_DIR/llms.txt" ]]; then
	for agent_set_url in 'https://agents.kujolang.ai/agents/chain-of-command/' 'https://agents.kujolang.ai/agents/webops/' 'https://agents.kujolang.ai/agents/publishing-house/'; do
		if ! grep -Fq "$agent_set_url" "$OUT_DIR/llms.txt"; then record_failure "FAIL llms-agent-set: missing $agent_set_url"; fi
	done
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
	if ! grep -q 'id="webops"' "$OUT_DIR/index.html"; then
		record_failure "FAIL agent-set: homepage does not render the WebOps set"
	fi
	if ! grep -q 'id="publishing-house"' "$OUT_DIR/index.html"; then
		record_failure "FAIL agent-set: homepage does not render the Publishing House set"
	fi
	if ! grep -q 'href="/agents/chain-of-command/">Chain of Command</a>' "$OUT_DIR/index.html" || ! grep -q 'href="/agents/webops/">WebOps</a>' "$OUT_DIR/index.html" || ! grep -q 'href="/agents/publishing-house/">Publishing House</a>' "$OUT_DIR/index.html"; then
		record_failure "FAIL agent-navigation: homepage does not render all direct agent-set links"
	fi
	if grep -q 'site-nav-dropdown' "$OUT_DIR/index.html"; then
		record_failure "FAIL agent-navigation: homepage still renders the old Agents dropdown"
	fi
	if grep -q 'card-grid agent-grid' "$OUT_DIR/index.html"; then
		record_failure "FAIL homepage-grid: homepage still renders the old agent grid"
	fi
	if ! grep -q 'class="sk-button source-link"' "$OUT_DIR/index.html" || ! grep -q 'M9 19c-4.3 1.4' "$OUT_DIR/index.html"; then
		record_failure "FAIL mobile-source-icon: header source link does not render the Tabler GitHub icon"
	fi
	if ! grep -q 'data-mobile-menu-toggle' "$OUT_DIR/index.html" || ! grep -q 'data-mobile-navigation' "$OUT_DIR/index.html"; then
		record_failure "FAIL mobile-navigation: header toggle or menu overlay is missing"
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
