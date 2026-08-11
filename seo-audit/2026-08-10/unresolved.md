# Unresolved items

Audit date: 2026-08-10

1. **WWW host variants (P2, infrastructure):** `www.agents.kujolang.ai` did not resolve over HTTP or HTTPS. Decide whether to support it; if yes, add DNS/Cloudflare routing and a one-hop permanent redirect to the canonical host.
2. **Effective security headers (P2, infrastructure):** production did not serve the headers declared in `_headers`; GitHub Pages does not interpret that file. Configure equivalent Cloudflare response-header rules.
3. **Search/index platform data:** Google Search Console and Bing Webmaster Tools were unavailable. Sitemap processing, coverage, queries, clicks, impressions, CTR, and crawl issues are `NOT AVAILABLE — DATA ACCESS REQUIRED`.
4. **Outcome/field data:** analytics, CDN logs, CrUX/field CWV, backlinks, and ChatGPT referral reporting are `NOT AVAILABLE — DATA ACCESS REQUIRED`.
5. **AI visibility:** comparable authorized ChatGPT, Perplexity, Copilot, Gemini/AI Overview, or other answer sessions were unavailable. Mentions and citations are `NOT AVAILABLE — DATA ACCESS REQUIRED`.
6. **Editorial evidence:** agent contracts would become more citation-worthy with real usage examples, outcomes, and version history. Do not invent these; editorial/source-owner input is required.
7. **Workflow maintenance:** the GitHub Pages deployment succeeded but warned that referenced actions still target deprecated Node.js 20 and are currently forced onto Node.js 24. Update pinned action revisions when maintainers publish the appropriate runtime updates.
