# Kujo Agents Site Instructions

`kujo-agents` is canonical. Do not hand-maintain divergent agent contract
copies. Synchronize all sets with `python3 scripts/sync-agent-content.py
/path/to/kujo-agents`, build through the checked-in Kujo SSG, and commit the
generated `output/` deployed by GitHub Pages.

VideoOps public profile slugs are prefixed with `videoops-` because canonical
role names such as `creative-director` may also exist in another agent set.

Preserve Chain of Command URLs, SiteKit, the current visual system, the
`agents.kujolang.ai` domain, and generic fallback images for agents without
portraits. Scoped sync may delete only stale slugs owned by that set.

Validate with:

```bash
python3 tests/test_sync_agent_content.py
python3 scripts/validate-agent-content.py
kujo run ./build.kujo -- --site-url https://agents.kujolang.ai
bash scripts/validate-generated-output.sh output
git diff --check
```
