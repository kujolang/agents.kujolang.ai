# Methodology

Audit date: 2026-08-14

## Scope

The full repository and generated site, the Publishing House collection and 23
profiles, the new system overview, canonical source synchronization, metadata,
links, schema, media, social previews, responsive rendering, crawl/index
controls, production delivery, and AI-search discoverability.

## Evidence sequence

1. Confirmed clean `main` at `6727778` and preserved the untouched 85-document
   generated output under `raw/baseline-build/` before editing.
2. Crawled baseline output and probed production.
3. Synchronized the canonical Publishing House contracts from `kujo-agents`.
4. Added the system page, dither hero, Howl card, navigation, and SSG support.
5. Rebuilt through Kujo SSG, validated 86 generated HTML files, and performed
   desktop plus 390 px responsive visual QA.
6. Crawled the generated after state and ran Lighthouse 13.4.1 mobile against
   the new page.
7. Committed and deployed through GitHub Pages, then re-probed production and
   compared generated and delivered content.

## Current primary guidance consulted

See `research-sources.md`. Conclusions use current first-party Google Search
Central, Bing Webmaster, Schema.org, and OpenAI publisher guidance. `llms.txt`
is treated as an experimental discovery aid, not an indexing requirement.

## Build and crawl commands

`python3 scripts/sync-agent-content.py ../kujo-agents --set publishing-house`

`HOWL=../howl/bin/howl KUJO=../kujo/target/release/kujo bash scripts/render-social-cards.sh`

`../kujo/target/release/kujo run ./build.kujo -- --site-url https://agents.kujolang.ai`

`python3 seo-audit/audit_site.py --root output --repo-root . --origin https://agents.kujolang.ai --phase <baseline|after> --out seo-audit/publishing-house-refresh/2026-08-14 --probe-production`

## Interpretation limits

Lighthouse is variable lab evidence, not field Core Web Vitals. Successful bot
delivery does not prove indexing, ranking, inclusion, or citation. Search and
answer visibility require authorized platform data and elapsed time. Internal
audit scores are diagnostics only.
