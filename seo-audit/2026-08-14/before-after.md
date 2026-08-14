# Before and after

| Metric | Baseline | After |
|---|---:|---:|
| HTML documents | 85 | 85 |
| Canonical/indexable pages | 83 during automated live pass* | 84 |
| Missing/duplicate titles | 0 / 0 | 0 / 0 |
| Missing/duplicate descriptions | 0 / 0 | 0 / 0 |
| Missing canonicals / H1 problems | 0 / 0 | 0 / 0 |
| Broken internal links / orphans | 0 / 0 | 0 / 0 |
| Missing image alt / dimensions | 0 / 0 | 0 / 0 |
| Schema parse errors | 0 | 0 |
| Production non-200 / build mismatches | 1* / 0 | 0 / 0 |
| Homepage Lighthouse performance | 38 | 92 |
| Homepage LCP | 6,388 ms | 2,968 ms |
| Homepage TBT | 3,000 ms | 150 ms |
| Homepage main-thread work | 7.2 s | 1.6 s |
| Publishing House directory performance | 94 | 100 |
| Publisher detail performance | 98 | 98 |
| Internal SEO health heuristic | 86/100 | 94/100 |
| Internal AI-readiness heuristic | 78/100 | 85/100 |
| P0 / P1 open | 0 / 1 | 0 / 0 |

*One unrelated route returned a transient 503 during the baseline automation. It returned 200 on repeat, and the independent full production crawl found all 84 canonical URLs healthy.

Scores are internal heuristics. Lighthouse values are comparable mobile lab runs against production, not field CWV or ranking evidence.
