# Implemented changes

Audit date: 2026-08-10

- Replaced 12 oversized portrait sources with 640×640 optimized WebP files and rebuilt hashed output assets.
- Added intrinsic dimensions to every generated portrait/detail image occurrence.
- Replaced semantically misleading agent `ProfilePage` schema with `SoftwareSourceCode`, source repository, visible/structured maintainer, publisher, and modification date.
- Added visible maintainer, update date, and source-contract provenance on 28 agent pages.
- Made the placeholder-only WebOps set `noindex,follow` and removed it from the sitemap without removing navigation.
- Corrected 404 behavior: no canonical-to-home, no structured data, `noindex,follow`, and root-relative assets/navigation for nested missing paths.
- Aligned sitewide brand links with the canonical root URL.
- Added a unique agent-directory description and social images for home/listing pages.
- Emitted 28 accurate sitemap `lastmod` values from existing source dates.
- Removed empty RSS autodiscovery on a site with no posts.
- Reduced the hero dither from a continuous half-resolution animation to one static one-sixth-resolution pass.
- Expanded generated-output validation for image dimensions, error-page directives, root-relative 404 resources, WebOps indexability, and sitemap exclusion.
- Added reproducible crawl, production-probe, content/intent, query-map, Lighthouse normalization, and before/after audit artifacts.

Implementation commits: `452d32f`, `5aa7fc5`, and `51e092a`. Both GitHub Pages deployments completed successfully.
