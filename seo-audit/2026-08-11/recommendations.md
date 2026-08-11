# Recommendations and measurement plan

Audit date: 2026-08-11

## Immediate after deployment

- Submit `https://agents.kujolang.ai/sitemap.xml` in Google Search Console and Bing Webmaster Tools and preserve submission receipts.
- Confirm whether `www.agents.kujolang.ai` should exist; if yes, configure a one-hop permanent redirect to the canonical host with query preservation.
- Apply effective security headers at Cloudflare or another delivery layer supported by the GitHub Pages chain; repository `_headers` files are not executed by GitHub Pages.

## 7-day checks

- Recheck sitemap discovery/processing, canonical selection, indexing coverage, crawler errors, and server/edge logs.
- Compare field or RUM performance if access becomes available; do not use Lighthouse alone as a field-CWV proxy.
- Re-run the four recorded branded/site search observations with a named engine, country, device, and signed-out profile.

## 28-, 60-, and 90-day comparisons

- Export query/page impressions, clicks, CTR, average position, device, country, and search appearance from Search Console and Bing.
- Track `utm_source=chatgpt.com` and other identifiable AI referrals separately from search traffic.
- Repeat the AI benchmark questions in controlled ChatGPT, Perplexity, and Copilot sessions, recording mentions, citations, cited URLs, competing domains, and accuracy.
- Compare the same three Lighthouse templates and any available field CWV without changing test conditions.

## Editorial decisions

- Add a concise agent-selection guide and worked usage examples only when they can link to real source contracts, executions, or measured outcomes.
- Review the 209-character Triage Agent description for SERP concision only if editorial intent permits; length is a review signal, not a ranking rule.
- Optimize the 271 KiB homepage hero through an approved responsive/cropped asset rather than lowering quality blindly; preserve the full-viewport visual system.
