# Agents site hardening

## Repository

- Repository `kujolang/agents.kujolang.ai`, production branch `main`
- Starting commit `97b1affa6fc133f561d55ac6a753d2193e09e1ef`
- Verified implementation commit `2a471d2fb3dd3e643ad655757f329403cd8b77e0`
- Static agent catalog generated from canonical contracts in `kujolang/kujo-agents`. Kujo SSG and SiteKit render public routes, and Pages rebuilds and publishes the site. This pass used an isolated sparse worktree and left the pre-existing platform-picker checkout intact.

## Findings

| ID | Priority | Area | Evidence and change | Status |
| --- | --- | --- | --- | --- |
| AS-01 | P0 | Profile ownership | A new slug could overwrite a different set's existing profile before stale-file ownership was checked. Invalid ownership state and duplicate catalog slugs were also accepted. Validate slug format, set membership and existing ownership before any updates. | Fixed |
| AS-02 | P1 | Publication failure | Sync wrote each profile immediately. A later error could leave earlier files changed with the old state. Validate all selected sets, stage replacements, publish state last and restore files if a replacement fails. Keep identical profiles in place. | Fixed |
| AS-03 | P1 | WebMCP | The vendored adapter assigned the shared index fetch to one caller, registered only once even on cached-page restoration, and relied on a check of the initial fetch URL. Adopt the canonical SSG adapter for cancellation, restoration and same-origin mode. | Fixed |
| AS-04 | P1 | Build parity | Kujo 1.1.0 on macOS exited zero with 32 HTML files and missing WebMCP output. The previous Linux Pages deployment was successful. Pin the reviewed 1.10.0 release setup and run source and emitted runtime checks during deployment. | Fixed in source and verified locally with 1.10.0 |

## Review coverage

| Phases | Evidence |
| --- | --- |
| 0–2 | Read the agent guide, canonical set definitions, source projection, generated validator, SSG entrypoint and Pages workflow. Traced managed stale deletions and builder-to-upload flow. |
| 3–4 | Ran the normal sync against all four canonical sets in a disposable site. All 85 identical profiles retained their bytes and filesystem identities. No CPU or memory improvement is claimed. |
| 5–6, 15 | Checked the static WebMCP index, bounded tool results, provider-independent schema and no-JavaScript content. The same 85 individual agent routes and public index bytes are retained. The adapter changes follow canonical SSG, with one lazy same-origin fetch per active page lifetime. |
| 7–9 | Reviewed set boundaries, source and managed symlinks, atomic file staging and failure recovery, generated output resets, same-origin fetch and Pages publication. The deployment gate now verifies the emitted minified adapter. |
| 10–11 | Preserved the sync flags, metadata schema, route layout, public links and set prefixes. The Pages runtime pin changes to 1.10.0. The sync uses Python standard library modules and the already configured Node release. |
| 12–13 | Added regression coverage for collisions, invalid ownership, duplicate entries, multi-set validation, rollback and identical files. Existing content and site validators now gate deployment. |
| 14–16 | Updated the build and sync docs. Preserved the content and tracked output structure and excluded the historical SEO evidence tree and bulk media from the source sweep. |
| 17–18 | Implemented and verified the changes in the receipts below. |

## Verification

- Existing tests passed on the baseline. The candidate passed all nine tests via `python3 tests/test_sync_agent_content.py`.
- `python3 scripts/sync-agent-content.py /path/to/kujo-agents` passed in a disposable site with canonical source commit `d576663aa46718c443f1bbc0f03aa2f23f3dbd3e`. Membership and Markdown matched the published inputs for all four sets.
- `kujo run ./build.kujo -- --site-url https://agents.kujolang.ai` passed with the existing local 1.10.0 runtime. `python3 scripts/validate-agent-content.py` passed for 85 agent profiles. `bash scripts/validate-generated-output.sh output` passed for 94 HTML files.
- `node scripts/test-webmcp-runtime.js "$runtime" output/.well-known/kujo-site-index.json` passed for both raw and minified adapters. Only those two tracked output files changed. `git diff --check` passed.
- The old macOS 1.1.0 artifact failed validation because its index and minified adapter were missing. The Linux Pages result for the baseline succeeded. The candidate's local verification used an existing 1.10.0 build. The Pages workflow selects the checksum-verified release artifact.

## Cross-repository notes

The adapter and runtime contract match `kujolang/ssg@c656da3`. Agent contracts remain sourced from `kujolang/kujo-agents`. Run one sync invocation for the requested sets to apply its validation and rollback as a batch.
