# Implemented changes

Audit date: 2026-08-14

- Removed the redundant per-pixel runtime hero dither; the source hero asset is already dithered.
- Prioritized above-fold agent profile portraits with eager loading and high fetch priority.
- Added `mainEntityOfPage` and agent-set `isPartOf` relationships to agent contract JSON-LD.
- Added complete visible membership through `CollectionPage.hasPart` on all three agent-set pages.
- Added visible update/source provenance to agent-set pages.
- Added `twitter:site=@kujolang` to all social metadata.
- Made audit route classification manifest-driven so Publishing House and future declared sets are audited as collections.
- Extended validators for schema relationships, collection membership, profile-image priority, provenance, Twitter attribution, and removal of runtime dither work.

Deployment: commit `34367d9`; GitHub Pages run `31842442524` completed successfully.
