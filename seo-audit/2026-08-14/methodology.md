# Methodology

Audit date: 2026-08-14

## Scope

Full repository, canonical `kujo-agents` synchronization, generated output, production delivery, the Publishing House collection and 23 profiles, crawl/index controls, metadata and social cards, content accuracy, linking, schema, media, lab performance, authority/provenance, crawler access, and AI-search readiness for `https://agents.kujolang.ai`.

## Evidence sequence

1. Confirmed clean `main` at `b2c6bfe` and preserved the untouched 85-document output under `raw/baseline-build/` before editing.
2. Crawled the baseline and probed production, external destinations, crawler user agents, robots, sitemap, redirects, host variants, and nested 404 behavior.
3. Verified all synced Publishing House bodies and metadata against the clean canonical `../kujo-agents` repository at `936ab4d`.
4. Captured Lighthouse 13.4.1 mobile production JSON for home, agent directory, Publishing House directory, and Publisher detail.
5. Implemented evidence-backed systemic fixes, rebuilt with the checked-in Kujo SSG, and ran repository validators.
6. Deployed commit `34367d9` through successful GitHub Pages run `31842442524`.
7. Re-crawled the deployed site, compared generated and production hashes, and repeated the same four Lighthouse templates.

## Current primary guidance

See `research-sources.md`. Technical conclusions use first-party Google, Bing/IndexNow, Schema.org, OpenAI, and Cloudflare documentation. `llms.txt` is treated as experimental and is not counted as an indexing or ranking requirement.

## Interpretation limits

- Lighthouse is a variable lab diagnostic and does not establish field CWV.
- A crawler user agent receiving 200 proves delivery only; robots policy, indexing, and citation are separate.
- Search and answer visibility could not be measured without authorized platform data or controlled sessions.
- Third-party 401/403/405/429 responses would be indeterminate; no external destination failed in the final crawl.
- Internal scores are documented audit heuristics only.
