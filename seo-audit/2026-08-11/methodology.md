# Methodology

Audit date: 2026-08-11

## Scope

Full repository, generated output, production delivery, crawl/index controls, metadata, content intent, internal/external links, schema, media, lab performance, authority, crawler access, sampled web-search visibility, and AI-search readiness for `https://agents.kujolang.ai` after expansion to 56 profiles.

## Evidence sequence

1. Confirmed clean `main` at `16058f5` before audit-specific work.
2. Built the untouched site and preserved all generated artifacts at `raw/baseline-build/`.
3. Crawled all 61 generated HTML documents and independently probed the 60 production canonical URLs, external destinations, crawler agents, host variants, robots, sitemap, and nested 404.
4. Captured Lighthouse 13.4.1 mobile JSON for home, directory, and representative agent-detail templates.
5. Sealed the baseline before implementing four repository-safe P2 fixes.
6. Rebuilt, validated, committed, pushed, deployed, and repeated the identical crawl and Lighthouse templates.
7. Kept search/AI outcome measurements separate from immediate technical verification.

## Current primary guidance consulted

See `research-sources.md`. Current conclusions use first-party Google, Bing, OpenAI, Perplexity, and Schema.org documentation. `llms.txt` remains an experimental discovery aid rather than an indexing or ranking requirement.

## Build and crawl commands

```bash
/Users/robertdevore/2026/Kujolang/kujo-repos/kujo/target/release/kujo run ./build.kujo -- --site-url https://agents.kujolang.ai
python3 seo-audit/audit_site.py --root seo-audit/2026-08-11/raw/baseline-build --repo-root . --origin https://agents.kujolang.ai --phase baseline --out seo-audit/2026-08-11 --probe-production
python3 seo-audit/audit_site.py --root seo-audit/2026-08-11/raw/after-build --repo-root . --origin https://agents.kujolang.ai --phase after --out seo-audit/2026-08-11 --probe-production
npx --yes lighthouse URL --only-categories=performance,accessibility,best-practices,seo --output=json --chrome-flags="--headless --no-sandbox" --quiet
python3 seo-audit/summarize_lighthouse.py --audit-root seo-audit/2026-08-11
```

## Interpretation limits

- Lighthouse is a variable lab diagnostic; it does not establish field CWV or ranking impact.
- A crawler user-agent returning 200 proves access only at the recorded time, not indexing or citation.
- The web-search connector observations do not identify or control the underlying engine, locale, device, personalization, or complete result set.
- Third-party access-block statuses would be indeterminate; all observed external destinations returned 200 in this audit.
- Cloudflare-managed robots rules express owner policy. The audit preserved the separation between search/grounding access and training restrictions.
- Internal SEO and AI-readiness scores are transparent audit heuristics only.
