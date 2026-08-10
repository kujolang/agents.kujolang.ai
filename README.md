# Kujo Agents

Static directory for the [Kujo Chain of Command](https://github.com/kujolang/kujo-agents/tree/main/chain-of-command), built with [Kujo SSG](https://github.com/kujolang/ssg) and the vendored SiteKit distribution.

## Build

```bash
kujo run ./build.kujo -- --site-url https://agents.kujolang.ai
bash scripts/validate-generated-output.sh output
```

Preview the generated site:

```bash
kujo serve output --port 4173
```

## Refresh agent content

The checked-in `content/agents/` files are generated from the source agent contracts. Refresh them from a local `kujo-agents` checkout, then rebuild:

```bash
python3 scripts/sync-agent-content.py /path/to/kujo-agents/chain-of-command
kujo run ./build.kujo -- --site-url https://agents.kujolang.ai
```

## Cloudflare Pages

The generated `output/` directory is committed so Cloudflare Pages can deploy without installing Kujo in its build image:

- Production branch: `main`
- Build command: leave blank
- Build output directory: `output`

Run the local build and validation before committing content or template changes.

## Design assets

`assets/sitekit/` is the unmodified SiteKit v1 distribution, including its license and Departure Mono license. The Kujo logomark is sourced from the `kujolang.ai` site assets.
