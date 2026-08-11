# Methodology

Audit date: 2026-08-10

## Scope

Full repository, generated-output, production, technical SEO, content/intent, linking, schema, media, lab performance, authority, crawler access, sampled search visibility, and AI-readiness audit for `https://agents.kujolang.ai`. The audit began 2026-08-10 and production verification completed 2026-08-11 America/Detroit.

## Evidence sequence

1. Confirmed clean `main` worktree and repository instructions.
2. Built the untouched site and preserved the complete generated output at `raw/baseline-build/`.
3. Parsed all 33 generated HTML documents and compared sitemap, links, assets, metadata, headings, schema, and source routes.
4. Probed all canonical production pages, unique external destinations, robots, sitemap, host/protocol variants, and six representative crawler user agents.
5. Captured mobile Lighthouse JSON for home, directory, and detail templates.
6. Implemented repository-safe fixes, rebuilt, validated, deployed through GitHub Pages, and repeated the same crawl and production checks.
7. Preserved normalized before/after datasets and raw receipts. Search and AI outcomes remain separate from immediate technical validation.

## Current primary guidance consulted

See `research-sources.md`. Technical claims rely on current first-party Google, Bing, OpenAI, Perplexity, and Schema.org documentation. `llms.txt` remains explicitly experimental.

## Build and crawl commands

```bash
/Users/robertdevore/2026/Kujolang/kujo-repos/kujo/target/release/kujo run ./build.kujo -- --site-url https://agents.kujolang.ai
bash scripts/validate-generated-output.sh output
python3 seo-audit/audit_site.py --root output --repo-root . --origin https://agents.kujolang.ai --phase after --out seo-audit/2026-08-10 --probe-production
python3 seo-audit/summarize_lighthouse.py
```

The documented bare `kujo` command was initially unavailable through the non-login process PATH. Validation used the installed pinned Kujo 1.0.0 release binary above; the full build completed successfully.

## Interpretation limits

- Lighthouse is a lab diagnostic; individual scores and timings vary. Raw bytes and structural fixes are more deterministic than a single score.
- Returned web search results are dated observations, not universal rankings.
- A crawler user-agent returning 200 proves access at probe time, not indexing, ranking, citation, or complete WAF policy.
- Client-side analytics could not substitute for unavailable edge request logs.
- `401`, `403`, `405`, or `429` from third parties would be indeterminate rather than automatically broken; all unique external destinations returned 200 in this run.
- Internal scores are audit heuristics only. They are not Google, Bing, OpenAI, Perplexity, or Lighthouse scores.
