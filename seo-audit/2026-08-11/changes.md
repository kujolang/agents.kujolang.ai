# Implemented changes

Audit date: 2026-08-11

- Aligned all 56 `SoftwareSourceCode` schema `name` and `headline` values with the visible agent title while retaining separate SERP titles.
- Added accurate latest-child sitemap `lastmod` values to `/`, `/agents/`, `/agents/chain-of-command/`, and `/agents/webops/`.
- Added both agent-set collection URLs to the experimental `llms.txt` index.
- Eager-loaded and prioritized the first portrait in each agent set so directory LCP candidates are not lazy-loaded.
- Added deterministic validation for schema/title alignment, aggregate sitemap freshness, agent-set `llms.txt` coverage, and priority portrait loading.
- Generalized the audit helpers to support dated audit roots and updated WebOps content assessment after the placeholder-to-contract migration.

Deployment: commit `ea33152`; GitHub Pages run `31514456181` completed successfully.
