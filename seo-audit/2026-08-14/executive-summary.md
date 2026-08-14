# Executive summary

Audit date: 2026-08-14

## Overall status

PASS WITH RECOMMENDATIONS

## Where the site was

The immutable baseline contained 85 HTML documents: 84 canonical sitemap URLs plus the noindex 404. It included the Publishing House collection and 23 profile pages. All Publishing House metadata, social cards, source links, portraits, canonicals, headings, and contract bodies matched the canonical `kujo-agents` source and live production. One unrelated agent route returned a transient 503 during the automated baseline crawl; it returned 200 on repeat and all 84 canonical URLs passed the independent production crawl.

## What was wrong

No P0 defects were found. The homepage's runtime per-pixel canvas dither caused a P1 lab-performance regression: Lighthouse mobile measured performance 38, 6.39 s LCP, 3,000 ms total blocking time, and 7.2 s of main-thread work. The underlying hero asset was already dithered, so the repeated browser computation had no discovery value. Publishing House profile portraits were above the fold but lazy-loaded. Agent-set structured data did not express its visible membership, detail schema did not link the contract to its page or set, set pages lacked visible update/source provenance, and Twitter cards lacked account attribution.

## What changed

The redundant runtime dither canvas and loop were removed while preserving the existing dithered hero asset. Agent profile portraits now load eagerly with high fetch priority. Agent JSON-LD now links each `SoftwareSourceCode` contract to its main page and parent collection; set `CollectionPage` JSON-LD lists every visible member. Set pages now show update dates and canonical source-contract links. All pages include `twitter:site=@kujolang`. Validators and the audit crawler were extended so these contracts and manifest-defined agent sets remain covered.

## Where the site is now

The deployed after crawl retained all 85 documents and 84 indexable canonical URLs with zero broken internal links, orphans, missing or duplicate titles/descriptions, missing canonicals, H1 defects, missing image alt/dimensions, schema parse errors, production non-200s, or production/build mismatches. All 24 Publishing House URLs and social images return 200. All 587 external-link occurrences in the generated crawl resolved successfully.

Comparable production Lighthouse runs improved the homepage from 38 to 92 performance, LCP from 6.39 s to 2.97 s, TBT from 3,000 ms to 150 ms, and main-thread work from 7.2 s to 1.6 s. The Publishing House collection scored 100 performance and its representative Publisher detail scored 98; accessibility, best practices, and SEO were 100 for all four tested templates. These are lab observations, not field Core Web Vitals.

Internal audit heuristics moved from 86 to 94 SEO health and from 78 to 85 AI-search readiness. These are transparent readiness indicators, not search-platform scores.

## Available measurements

Immutable baseline and after builds, normalized 85-page crawls, live response receipts, crawler and redirect probes, 84-URL production verification, 587 external-link occurrences, 487 image occurrences, social-card verification, and eight Lighthouse JSON receipts are preserved in this directory.

## Unavailable measurements

Google Search Console, Bing Webmaster Tools, analytics, CDN/origin logs, CrUX or other field CWV, backlink data, IndexNow receipts, controlled rankings, and controlled answer-engine citation sessions are `NOT AVAILABLE — DATA ACCESS REQUIRED`. No indexing, ranking, traffic, referral, or citation improvement is claimed.

## Next actions

Monitor the same templates and query set at 7, 28, 60, and 90 days. Add read-only Search Console, Bing, analytics, field performance, and edge-log access. Consider pre-optimizing the 271 KiB homepage hero with visual approval because lab LCP remains above 2.5 s. Treat semantic ordered-list rendering, long title-display signals, `index.html` duplicates, the absent `www` host, and `llms.txt` curation as recommendations rather than launch blockers.
