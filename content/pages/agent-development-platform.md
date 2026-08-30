---
title: "Build Your Own Kujo Agent"
custom_url: "agent-development-platform"
nav_title: "Build an Agent"
description: "Install Kujo's agent toolchain, create a repository-owned AI agent, and start talking to it with local-first profiles, reusable credentials, tools, knowledge, workflows, evaluation, and production controls."
seo_title: "Kujo Agent Development Platform"
seo_description: "Build repository-owned AI agents with one focused Kujo install, reusable provider credentials, seven profiles, local evaluation, and explicit production controls."
keywords: "Kujo agents, AI agent development platform, local AI agents, repository-owned agents, agent tools"
featured_image: "assets/images/agent-development-platform.webp"
social_image: "/assets/images/social/agent-development-platform.jpg"
template: "agent-development-platform"
date: 2026-08-30
last_updated: 2026-08-30
nav_hide: true
---

## One project you can inspect and own

An Agent Project is a normal repository. Its instructions, model choice,
skills, tools, knowledge, policies, workflows, evaluations, dependency pins,
and runtime boundaries are files your team can review and change. Kujo does not
hide the working contract in a hosted dashboard.

Install the focused Agent Development Platform:

```bash
curl -fsSL https://kujolang.ai/install.sh | bash -s -- --group agent
```

Create a ready-to-run offline agent:

```bash
kujo agent new my-agent --profile basic --install
```

Talk to it:

```bash
cd my-agent && kujo agent run "What can you help me with?"
```

The `basic` profile needs no API key, network connection, Watchdog, or
RunLedger. It gives every developer a deterministic first run before they add a
live model or external connector.

## Seven profiles, one ownership model

| Profile | Use it for |
| --- | --- |
| `basic` | Offline Agents SDK fixture execution and Eval |
| `tools` | Project tools and MCP integrations |
| `knowledge` | Local RAG, retrieval, and citations |
| `workflow` | Resumable Dispatch workflows |
| `hardened` | Least-privilege declarations and Workcell isolation |
| `observable` | Watchdog telemetry and RunLedger receipts |
| `full` | The compatible local composition, including Relay |

Start small. `kujo agent inspect` separates required dependencies, optional
services, credential names, policies, and generated integration paths before a
run. `kujo doctor agent` verifies the installed platform, and `kujo agent eval`
runs the project's acceptance checks.

## Save credentials once, reuse them safely

```bash
kujo agent auth set openai
kujo agent auth status openai
```

Kujo accepts masked input and stores reusable provider keys in macOS Keychain,
Windows Credential Manager, or Linux Secret Service. Automation can use stdin
or an existing environment variable. Project-specific overrides stay in an
owner-only, Git-ignored `.env.local`. Status and diagnostic output report the
credential source without printing the secret.

Named API-key connectors use the same contract:

```bash
kujo agent auth set --name LINEAR_API_TOKEN
```

## Local first, production controls when needed

Kujo capabilities authorize effects, but do not pretend to be a sandbox. The
`hardened` profile adds an explicit Workcell container boundary with a read-only
root, resource limits, bounded commands, and a receipt. Eval provides repeatable
acceptance checks. Watchdog and RunLedger remain optional until the project
needs telemetry or durable run history.

Read the [complete Agent Project documentation](https://docs.kujolang.ai/build/owned-agent-projects/),
explore the [agent library](/agents/), or inspect the [Kujo source](https://github.com/kujolang/kujo).
