# Kujo Agents

Static library for the [Kujo Chain of Command](https://github.com/kujolang/kujo-agents/tree/main/chain-of-command) and [Kujo WebOps](https://github.com/kujolang/kujo-agents/tree/main/webops), built with [Kujo SSG](https://github.com/kujolang/ssg) and the vendored SiteKit distribution.

## Build

```bash
kujo run ./build.kujo -- --site-url https://agents.kujolang.ai
bash scripts/validate-generated-output.sh output
```

Preview the generated site:

```bash
kujo serve output --port 4173
```

## Agent sets

Every agent remains in the `content/agents/` content type. The first `categories` value names the set that owns the agent; `tags` describe the agent's role inside that set:

```yaml
categories: ["WebOps"]
tags: ["Monitoring"]
```

The SSG groups those categories into independent, single-row carousels that show three cards on desktop. When adding a new set, also add its destination to the Agents dropdown in `templates/layout.html`.

## Refresh canonical agent content

The checked-in `content/agents/` files are generated from the source agent contracts. Refresh them from a local `kujo-agents` checkout, then rebuild:

```bash
python3 scripts/sync-agent-content.py /path/to/kujo-agents
kujo run ./build.kujo -- --site-url https://agents.kujolang.ai
```

Use `--set chain-of-command` or `--set webops` for a scoped refresh. The sync
state owns slugs per set, so a scoped refresh can remove stale pages from that
set but cannot delete another set. `last_updated` comes from each canonical
contract's Git history (or filesystem modification date when Git evidence is
unavailable). WebOps uses the generic Kujo logomark until custom portraits are
added.

## GitHub Pages and Cloudflare

The generated `output/` directory is committed and deployed by `.github/workflows/pages.yml`:

- GitHub Pages custom domain: `agents.kujolang.ai`
- Cloudflare CNAME: `agents` to `kujolang.github.io` with proxying enabled
- Production branch: `main`

Run the local build and validation before committing content or template changes.

## Design assets

`assets/sitekit/` is the unmodified SiteKit v1 distribution, including its license and Departure Mono license. The Kujo logomark is sourced from the `kujolang.ai` site assets. The portraits in `content/media/agents/` are copied from the original Kujo Chain of Command design demo and optimized by the SSG during builds.
