# Executive summary

Audit date: 2026-08-11

## Overall status

PASS WITH RECOMMENDATIONS

## Where the site was

The post-expansion baseline contained 61 HTML documents: 60 canonical, indexable sitemap URLs plus the noindex 404. All 56 agent profiles, the main directory, both agent-set directories, and the homepage returned 200 in production and matched the untouched generated baseline byte-for-byte. Titles, descriptions, H1s, canonicals, social metadata, image attributes, internal links, and JSON-LD parsing had no crawl defects. Search and answer crawlers were allowed and returned 200 through Cloudflare; training crawlers remained blocked by owner policy.

## What was wrong

No P0 or P1 defects were found. Four systemic P2 opportunities remained after the content expansion: 56 `SoftwareSourceCode` schema names used SERP title suffixes instead of the visible agent name; four aggregate sitemap entries omitted `lastmod`; `llms.txt` omitted the two new agent-set directories; and the first portrait on agent directories was lazy-loaded despite becoming a mobile LCP candidate. The homepage hero remained the largest lab-performance opportunity at 271 KiB source weight, with a baseline mobile Lighthouse performance score of 76 and LCP of 3.77 seconds.

The sampled web-search connector did not surface `agents.kujolang.ai` for four branded/site queries. This is a dated observation with uncontrolled provider, locale, and personalization—not proof of Google or Bing index status. Search Console, Bing Webmaster Tools, analytics, CDN logs, field CWV, backlinks, and controlled answer-engine sessions were unavailable.

## What changed

The generator now keeps structured-data names aligned with visible agent names, assigns accurate newest-child `lastmod` dates to the homepage and three aggregate directories, exposes both agent-set directories in `llms.txt`, and prioritizes each set's first portrait instead of lazy-loading it. Validation now enforces these contracts. Commit `ea33152` was deployed by GitHub Pages run `31514456181`.

## Where the site is now

The after crawl retained all 61 documents and 60 indexable URLs with zero broken internal links, orphans, missing/duplicate titles or descriptions, missing canonicals, H1 defects, missing image alt/dimensions, schema parse errors, non-200 production pages, or production/build mismatches. All 56 agent schema names match their visible titles, all four aggregate URLs have sitemap freshness dates, and both agent sets are discoverable in `llms.txt`.

Comparable Lighthouse mobile runs scored 81/98/98 for home, directory, and agent detail performance, while SEO, accessibility, and best practices remained 100 for all three templates. Homepage LCP measured 3.74 seconds; the remaining hero optimization is a recommendation, not evidence of field CWV. Internal audit heuristics moved from 91→95 SEO health and 81→84 AI-search readiness. These are documented internal trend scores, not search-platform scores.

## Available measurements

Immutable generated baseline and after builds, normalized 61-page crawls, live-response hashes and headers, 418 external-link occurrences with successful live responses, crawler and redirect probes, sitemap/robots/404 receipts, and six Lighthouse JSON receipts are preserved in this directory.

## Unavailable measurements

Google Search Console, Bing Webmaster Tools, analytics, CDN/origin logs, CrUX or other field CWV, backlink data, IndexNow receipts, and controlled ChatGPT/Perplexity/Copilot citation sessions are `NOT AVAILABLE — DATA ACCESS REQUIRED`. No ranking, traffic, indexing, citation, or referral gain is claimed.

## Next actions

Submit and monitor the updated sitemap in Google Search Console and Bing Webmaster Tools; add read-only analytics and edge-log access; measure the same templates after 7, 28, 60, and 90 days; decide whether the absent `www.agents.kujolang.ai` host should redirect; apply security headers at the effective Cloudflare/GitHub Pages delivery layer; and optimize the homepage hero only with visual approval and comparable tests. Add usage examples or a selection guide only when source-grounded evidence exists.
