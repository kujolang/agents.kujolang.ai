# Before and after

Audit date: 2026-08-11

Immediate technical evidence only; search outcomes require post-deployment data and elapsed time.

| Metric | Baseline | After |
| --- | ---: | ---: |
| HTML documents | 61 | 61 |
| Canonical/indexable URLs | 60 | 60 |
| Missing or duplicate titles/descriptions | 0 | 0 |
| Missing canonicals / H1 defects | 0 | 0 |
| Broken internal links / orphans / depth >3 | 0 / 0 / 0 | 0 / 0 / 0 |
| Missing image alt / dimensions | 0 / 0 | 0 / 0 |
| JSON-LD parse errors | 0 | 0 |
| Agent schema names aligned to visible title | 0/56 | 56/56 |
| Aggregate sitemap URLs with accurate `lastmod` | 0/4 | 4/4 |
| Agent-set URLs present in `llms.txt` | 0/2 | 2/2 |
| Open P0 / P1 root causes | 0 / 0 | 0 / 0 |
| Internal SEO health heuristic | 91/100 | 95/100 |
| Internal AI-search readiness heuristic | 81/100 | 84/100 |

## Comparable Lighthouse mobile runs

| Template | Performance | LCP | Accessibility | Best practices | SEO |
| --- | --- | --- | --- | --- | --- |
| Home | 76→81 | 3.77s→3.74s | 100→100 | 100→100 | 100→100 |
| Agent directory | 97→98 | 1.95s→1.90s | 100→100 | 100→100 | 100→100 |
| Agent detail | 97→98 | 1.87s→1.87s | 100→100 | 100→100 | 100→100 |

The Lighthouse deltas are lab observations and do not establish a user or search outcome. Field INP remains unavailable.

## Heuristic scoring basis

SEO weights: crawl/index 20, metadata 15, architecture 15, content 15, schema 10, performance 10, media 5, authority 5, AI readiness 5. AI-readiness weights: crawler access 15, indexability 10, entity clarity 10, attribution 10, original/citable information 15, semantic data 10, topic relationships 10, freshness 5, technical/media 5, measured AI visibility 10. Missing measured AI visibility received 0/10.
