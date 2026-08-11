# Data availability

Audit date: 2026-08-10

| Source | Available | Scope / limitation |
| --- | --- | --- |
| Repository source and Git history | Yes | Clean main branch at baseline; repository-safe changes authorized by the request. |
| Untouched generated baseline | Yes | Preserved at `raw/baseline-build/` before implementation. |
| Production HTTP/CDN responses | Yes | Read-only probes of canonical URLs, host variants, crawlers, robots, sitemap, redirects, and headers. |
| Production deployment | Yes | GitHub Pages workflow completed successfully; live HTML and assets were independently re-probed. |
| Lighthouse lab data | Yes | One comparable mobile production run for home, directory, and agent detail before and after; lab variance applies. |
| Sampled web search observations | Yes | Four dated returned result sets; not a universal rank tracker. |
| Google Search Console | No | NOT AVAILABLE — DATA ACCESS REQUIRED |
| Bing Webmaster Tools / IndexNow history | No | NOT AVAILABLE — DATA ACCESS REQUIRED |
| Analytics and ChatGPT referral reporting | No | NOT AVAILABLE — DATA ACCESS REQUIRED |
| CDN/origin request logs | No | NOT AVAILABLE — DATA ACCESS REQUIRED |
| CrUX / field Core Web Vitals | No | NOT AVAILABLE — DATA ACCESS REQUIRED |
| Backlink index | No | NOT AVAILABLE — DATA ACCESS REQUIRED |
| Controlled AI-answer sessions and citations | No | NOT AVAILABLE — DATA ACCESS REQUIRED |
| Training-crawler policy decision | Existing edge policy observed | Cloudflare prepends `search=yes, ai-train=no, use=reference` and blocks named training crawlers including GPTBot and ClaudeBot. No policy change was authorized or made. |
