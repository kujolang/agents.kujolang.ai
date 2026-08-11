# Recommendations and measurement plan

Audit date: 2026-08-10

## Immediate after deployment

- Completed: re-crawl all 31 sitemap URLs plus home, 404, robots, and sitemap; confirm current HTML/assets in production.
- Completed: probe search/user fetchers through Cloudflare; Googlebot, Bingbot, OAI-SearchBot, ChatGPT-User, and PerplexityBot were allowed by the merged production robots policy and returned 200 at probe time.
- Site owner: verify and submit `https://agents.kujolang.ai/sitemap.xml` in Google Search Console and Bing Webmaster Tools.
- Infrastructure owner: decide on www support and configure effective Cloudflare security headers.
- Preserve the existing Cloudflare-managed distinction unless the owner decides otherwise: `search=yes, ai-train=no, use=reference`; GPTBot and ClaudeBot are specifically disallowed even though direct test requests can technically return 200.

## 7-day checks

- Search Console/Bing: sitemap fetch status, indexed/crawled URL samples, canonical selection, coverage reasons, and crawl errors.
- Logs: search and AI crawler status distribution for `/`, `/agents/`, representative agent detail URLs, robots, sitemap, and images.
- Analytics: establish ChatGPT referral reporting using the provider-supplied `utm_source=chatgpt.com` parameter when available.
- Re-run the four stored sampled search observations and eight AI benchmark questions with identical locale/platform settings.

## 28-, 60-, and 90-day comparisons

- Compare query/page impressions, clicks, CTR, average position, country, device, and search appearance using exported platform data.
- Compare indexed canonical URL count, sitemap discovery, crawler error paths, and real request-log status distributions.
- Compare field LCP, INP, and CLS when sufficient CrUX/RUM data exists; do not substitute lab scores for field outcomes.
- Repeat the same Lighthouse URLs and preserve raw JSON; use multiple runs/medians if performance decisions depend on small timing differences.
- Repeat AI questions and record mention, citation, cited URL, order/context, competitors, and factual accuracy without generalizing one session.
- Review which agent pages earn impressions/citations and prioritize real examples or comparisons based on observed demand—not generic word-count expansion.

## Editorial decisions

- Add real implementation/adoption examples only when source maintainers can verify them.
- Publish a selection guide or cross-agent comparison when the distinctions can be reviewed by agent owners.
- Replace WebOps placeholders with real source-grounded contracts before removing `noindex` or restoring sitemap inclusion.
- Consider a short project/about page only if maintainership, governance, and contact details can be stated accurately.
