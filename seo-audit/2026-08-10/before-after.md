# Before and after

Audit date: 2026-08-10

Immediate technical evidence only; search outcomes require post-deployment data and elapsed time.

| Metric | Baseline | After | Interpretation |
| --- | ---: | ---: | --- |
| Generated HTML documents audited | 33 | 33 | Includes the custom 404 document. |
| Indexable pages | 32 | 31 | Intentional: the placeholder-only WebOps set is now `noindex,follow`. |
| Canonical tags | 33 | 32 | Intentional: the 404 no longer canonicalizes to the homepage. |
| Duplicate descriptions (affected pages) | 2 | 0 | Home and directory now have distinct descriptions. |
| Broken internal link occurrences | 0 | 0 | Generated-artifact verification. |
| Orphans | 0 | 0 | All indexable pages remained reachable from HTML links. |
| Images missing alt attributes | 0 | 0 | No regression. |
| Image occurrences missing dimensions | 112 | 0 | Systemic generator fix. |
| Sitemap URLs | 32 | 31 | Placeholder WebOps removed. |
| Sitemap URLs with accurate `lastmod` | 0 | 28 | Existing agent `last_updated` values only. |
| Agent pages with semantically aligned schema | 0/28 | 28/28 | `ProfilePage` replaced by source-linked `SoftwareSourceCode`. |
| P0 issues | 0 | 0 | — |
| P1 root causes | 3 | 0 | 404 signals/resources, placeholder indexation, excessive portrait payload. |
| Internal SEO health heuristic | 70/100 | 91/100 | Weights documented below. |
| Internal AI-search readiness heuristic | 69/100 | 87/100 | Measured AI visibility remains 0/10 because access was unavailable. |

## Representative production Lighthouse receipts

| Template | Baseline total bytes | After total bytes | Baseline → after performance | Baseline → after LCP | Baseline → after CLS |
| --- | ---: | ---: | ---: | ---: | ---: |
| Home | 5,146,560 | 470,170 | 87 → 90 | 3,190 ms → 3,210 ms | 0 → 0.0002 |
| Agent directory | 4,017,784 | 167,166 | 76 → 94 | 5,904 ms → 1,891 ms | 0 → 0.0006 |
| Agent detail | 247,140 | 84,972 | 91 → 96 | 2,596 ms → 1,740 ms | 0.1368 → 0.0029 |

Single mobile lab runs are not field outcomes. Directory speed index and home TBT varied in the after samples even as transfer weight, directory/detail LCP, and detail CLS improved materially; see raw JSON and `performance.csv`.

## Heuristic weights

SEO health uses: crawl/index 20, metadata 15, architecture 15, content 15, structured data 10, performance evidence 10, media 5, authority 5, AI readiness 5. Field CWV access was unavailable, limiting performance credit.

AI readiness uses: search crawler access 15, indexability 10, entity clarity 10, attribution 10, original/citable information 15, semantics 10, topic relationships 10, freshness 5, technical/media 5, measured AI visibility 10. The final measured-visibility component is 0/10, not inferred.
