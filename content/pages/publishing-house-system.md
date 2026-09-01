---
title: "Kujo Publishing House System"
custom_url: "publishing-house-system"
nav_title: "Publishing House System"
description: "The complete Kujo Publishing House: 23 specialized agents, 8 record-owning tools, 11 lifecycle workflows, and 11 operator skills with evidence, approval, and publication boundaries."
seo_title: "Kujo Publishing House Agents, Tools, Workflows & Skills"
seo_description: "Explore the complete Kujo Publishing House system: 23 agents, 8 editorial tools, 11 lifecycle workflows, and 11 operator skills for evidence-bound publishing."
keywords: "Kujo Publishing House, AI publishing agents, editorial workflow agents, publishing automation, content operations"
featured_image: "assets/images/publishing-house-system.webp"
social_image: "/assets/images/social/publishing-house-system.jpg"
template: "publishing-house-system"
date: 2026-08-14
last_updated: 2026-09-01
nav_hide: true
---

## Operating model

The [Publishing House agent page](/agents/publishing-house/) is the directory for the 23 specialist roles. This page is the operating map: it shows how those roles move work through record-owning tools, bounded workflows, operator skills, review, approval, publication, and learning.

The local system is deterministic, offline-capable, and receipt-driven. Every agent step loads the canonical house contract, role contract, role skill, and workflow skill before recording an instruction checksum. External model, retrieval, and destination adapters remain explicit operator choices.

### Four contracts keep the house accountable

- **Agents perform bounded roles.** Leadership, intelligence, creative, writing, review, adaptation, production, publishing, and audience roles stay inside inspectable contracts.
- **Tools own durable records.** Editorial state, evidence, artifacts, reviews, approvals, publication receipts, measurements, and media provenance each have a named system of record.
- **Workflows coordinate transitions.** Every lifecycle stage defines its inputs, outputs, checks, and next accountable handoff.
- **Humans authorize publication.** No review result or orchestration state can substitute for a checksum-bound approval.

## Eight record-owning tools

| Tool | Owns |
| --- | --- |
| [StoryDesk](https://github.com/kujolang/storydesk) | Ideas, campaigns, briefs, assignments, editorial state, queues, and handoffs |
| [Dossier](https://github.com/kujolang/dossier) | Claims, sources, evidence, rights, conflicts, and readiness packets |
| [GalleyPack](https://github.com/kujolang/galleypack) | Versioned artifacts, packages, manifests, lineage, and frozen publication units |
| [BluePencil](https://github.com/kujolang/bluepencil) | Independent reviews, rubric decisions, findings, and revision requirements |
| [VersionSeal](https://github.com/kujolang/versionseal) | Human approval requests and exact package, checksum, destination, action, condition, and expiry decisions |
| [PressWire](https://github.com/kujolang/presswire) | Publication preflight, bounded effects, idempotency, and publication receipts |
| [ReaderSignal](https://github.com/kujolang/readersignal) | Measurements, feedback, learning, attribution limits, and follow-up recommendations |
| [AssetWorks](https://github.com/kujolang/assetworks) | Media plans, captions, accessibility, rights references, provenance, and asset manifests |

## Eleven lifecycle workflows

- **[Governance](https://github.com/kujolang/kujo-workflows/tree/main/publishing-house-governance)** sets the house mandate, portfolio priorities, and accountable operating handoffs.
- **[Daily Desk](https://github.com/kujolang/kujo-workflows/tree/main/publishing-house-daily-desk)** normalizes and routes the editorial packet.
- **[Commissioning](https://github.com/kujolang/kujo-workflows/tree/main/publishing-house-commissioning)** creates the brief, assignments, and evidence work order.
- **[Evidence Dossier](https://github.com/kujolang/kujo-workflows/tree/main/publishing-house-evidence-dossier)** binds material claims to reviewed evidence and rights records.
- **[Primary Piece](https://github.com/kujolang/kujo-workflows/tree/main/publishing-house-primary-piece)** creates the authoritative, evidence-linked artifact.
- **[Asset Production](https://github.com/kujolang/kujo-workflows/tree/main/publishing-house-asset-production)** produces supported, accessible media manifests.
- **[Editorial Review](https://github.com/kujolang/kujo-workflows/tree/main/publishing-house-editorial-review)** runs independent review and a bounded revision loop.
- **[Adaptation](https://github.com/kujolang/kujo-workflows/tree/main/publishing-house-adaptation)** creates a versioned derivative plan without expanding approved claims.
- **[Format Production](https://github.com/kujolang/kujo-workflows/tree/main/publishing-house-format-production)** produces newsletter, social, case-study, and audiovisual packages.
- **[Approval and Publication](https://github.com/kujolang/kujo-workflows/tree/main/publishing-house-approval-publication)** pauses for exact human approval before any bounded PressWire effect.
- **[Post-Publication](https://github.com/kujolang/kujo-workflows/tree/main/publishing-house-post-publication)** records measurements, learning, limits, and a non-commissioning follow-up recommendation.

## Eleven operator skills

- **Route the lifecycle.** [Kujo Publishing House Workflows](https://github.com/kujolang/kujo-skills/tree/main/skills/kujo-publishing-house-workflows) tells operators which bounded workflow to run and what proof to expect.
- **Operate the records.** Use the exact tool contracts for [StoryDesk](https://github.com/kujolang/kujo-skills/tree/main/skills/kujo-storydesk-workflows), [Dossier](https://github.com/kujolang/kujo-skills/tree/main/skills/kujo-dossier-workflows), [GalleyPack](https://github.com/kujolang/kujo-skills/tree/main/skills/kujo-galleypack-workflows), [BluePencil](https://github.com/kujolang/kujo-skills/tree/main/skills/kujo-bluepencil-workflows), [VersionSeal](https://github.com/kujolang/kujo-skills/tree/main/skills/kujo-versionseal-workflows), [PressWire](https://github.com/kujolang/kujo-skills/tree/main/skills/kujo-presswire-workflows), [ReaderSignal](https://github.com/kujolang/kujo-skills/tree/main/skills/kujo-readersignal-workflows), and [AssetWorks](https://github.com/kujolang/kujo-skills/tree/main/skills/kujo-assetworks-workflows).
- **Set up and calibrate.** [Publishing House Profile Setup](https://github.com/kujolang/kujo-skills/tree/main/skills/publishing-house-profile-setup) installs the working profile, while [Publishing House Quality Calibration](https://github.com/kujolang/kujo-skills/tree/main/skills/publishing-house-quality-calibration) aligns review standards and thresholds.

## The approval boundary

> Observe, propose, and act are upper bounds, not suggestions. BluePencil review is editorial evidence and Dispatch pause state is orchestration evidence; neither grants publication authority. VersionSeal binds a human decision to exact GalleyPack bytes, destination, action, conditions, and expiry. Any byte change invalidates approval. PressWire alone may create the publication effect and receipt.

## Run the complete local proof

Install the locked toolchain or inspect the all-eleven fixture in the [Kujo Workflows repository](https://github.com/kujolang/kujo-workflows/tree/main/docs/publishing-house). It requires no credentials or network access and cannot publish to a live destination.

- Contract and role instruction loading
- Locked tool versions and record checksums
- Independent review and bounded revision
- Approval pause and exact resume state
- Idempotent publication simulation and local receipt
