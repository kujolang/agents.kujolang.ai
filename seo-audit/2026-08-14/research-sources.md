# Research sources

Retrieved: 2026-08-14

- [Google robots.txt guidance](https://developers.google.com/search/docs/crawling-indexing/robots/intro) — official requirement/recommendation. Robots controls crawling, not guaranteed de-indexing; search resources must remain crawlable.
- [Google sitemap guidance](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap) — official recommendation. Include canonical, indexable absolute URLs and truthful `lastmod` values.
- [Google title-link guidance](https://developers.google.com/search/docs/appearance/title-link) — official recommendation. Titles should be descriptive and distinct; character counts are review signals, not fixed limits.
- [Google snippet guidance](https://developers.google.com/search/docs/appearance/snippet) — official recommendation. Descriptions should accurately summarize each page; Google may choose other snippet text.
- [Google structured-data introduction](https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data) and [general guidelines](https://developers.google.com/search/docs/appearance/structured-data/sd-policies) — official requirements/recommendations. JSON-LD must truthfully represent visible content; valid markup does not guarantee rich results.
- [Google Core Web Vitals guidance](https://developers.google.com/search/docs/appearance/core-web-vitals) — official recommendation. Field LCP, INP, and CLS are the outcome measures; Lighthouse remains lab evidence only.
- [Schema.org SoftwareSourceCode](https://schema.org/SoftwareSourceCode), [CollectionPage](https://schema.org/CollectionPage), and [Person](https://schema.org/Person) — vocabulary definitions. Schema validity and Google rich-result eligibility are separate questions.
- [OpenAI crawler guidance](https://developers.openai.com/api/docs/bots) — official documentation. `OAI-SearchBot`, `ChatGPT-User`, and `GPTBot` have distinct purposes and controls.
- [Cloudflare managed robots.txt](https://developers.cloudflare.com/bots/additional-configurations/managed-robots-txt/) — official delivery-layer documentation. Production robots content may be managed or prepended at the Cloudflare edge.
- [IndexNow documentation](https://www.indexnow.org/documentation) — provider documentation. Submission is optional discovery notification, not an indexing or ranking guarantee.

`llms.txt` remains an emerging, voluntary convention. Its presence is recorded but it receives no ranking credit.
