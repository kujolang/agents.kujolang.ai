# Research sources

Audit date: 2026-08-10

| Source | Retrieved | Supported conclusion | Classification |
| --- | --- | --- | --- |
| [Google Search Central: Crawling and indexing](https://developers.google.com/search/docs/crawling-indexing) | 2026-08-10 | Crawlable links, robots controls, metadata, canonicalization, and sitemaps are distinct discovery/indexing controls. | Official documentation |
| [Google: Consolidate duplicate URLs](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls) | 2026-08-10 | Redirects and `rel=canonical` are strong canonical signals; sitemap inclusion is weaker; signals should agree. | Official recommendation |
| [Google: Build and submit a sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap) | 2026-08-10 | Sitemaps should contain fully qualified canonical URLs intended for search; accurate `lastmod` may signal updates. | Official recommendation |
| [Google: Robots meta specifications](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag) | 2026-08-10 | Crawlers must access a page to see `noindex`; page-level directives control indexing and snippets. | Official requirement/recommendation |
| [Bing Webmaster Guidelines](https://www.bing.com/webmasters/help/webmaster-guidelines-30fba23a) | 2026-08-10 | Canonical sitemaps, crawlable internal links, clear structure, accuracy, authority, and freshness support Bing and Copilot grounding eligibility. | Official recommendation |
| [Bing: IndexNow](https://www.bing.com/webmasters/help/indexnow-0z209wby) | 2026-08-10 | IndexNow notifies participating engines of URL changes; it does not prove indexing or ranking. | Official documentation; optional enhancement |
| [OpenAI: Publishers and Developers FAQ](https://help.openai.com/en/articles/12627856-publishers-and-developers-faq) | 2026-08-10 | OAI-SearchBot access helps public content be discovered, summarized, cited, and linked in ChatGPT search; GPTBot policy is separate. | Official documentation |
| [Perplexity crawler documentation](https://docs.perplexity.ai/docs/resources/perplexity-crawlers) | 2026-08-10 | Perplexity recommends allowing PerplexityBot and verifying WAF access for search discovery. | Official recommendation |
| [Cloudflare: Managed robots.txt](https://developers.cloudflare.com/bots/additional-configurations/managed-robots-txt/) | 2026-08-11 | Cloudflare may prepend managed content signals and crawler-specific rules to an existing origin robots file; robots compliance is voluntary unless separately enforced. | Official documentation |
| [Schema.org WebSite](https://schema.org/WebSite) | 2026-08-10 | `WebSite` describes the overall domain-level collection of related pages. | Official vocabulary |
| [Schema.org CollectionPage](https://schema.org/CollectionPage) | 2026-08-10 | `CollectionPage` fits the agent directory and populated set listing. | Official vocabulary |
| [Schema.org SoftwareSourceCode](https://schema.org/SoftwareSourceCode) | 2026-08-10 | Source-linked reusable agent contract artifacts can be described without presenting them as people or organizations. | Official vocabulary; site-specific interpretation |
| `llms.txt` | 2026-08-10 | Kept as a discovery convenience, not treated as an official ranking or citation requirement. | Experimental/emerging practice |
