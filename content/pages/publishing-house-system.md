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
last_updated: 2026-08-15
nav_hide: true
---

## The roster shows who. This page shows how.

The [Publishing House agent page](/agents/publishing-house/) is the role
directory: it helps you find and inspect the 23 specialists. This companion
page is the operating map: it explains how those roles coordinate through
record-owning tools, lifecycle workflows, operator skills, approval, and
publication boundaries. The house covers leadership, intelligence, creative
development, writing, independent review, adaptation, format production,
publishing operations, and audience learning. Agents work inside role
contracts; tools own durable records; workflows coordinate bounded steps;
skills tell operators how to run and calibrate the system.

The local installation is deterministic, offline-capable, and receipt-driven.
Every agent step loads its canonical house contracts, role contract, role
skill, and Publishing House workflow skill, then records an instruction
checksum. External model, retrieval, and destination adapters remain explicit
operator choices. Publication still requires a checksum-bound human approval.

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

1. [Governance](https://github.com/kujolang/kujo-workflows/tree/main/publishing-house-governance) — set the house mandate, portfolio priorities, and accountable operating handoffs.
2. [Daily Desk](https://github.com/kujolang/kujo-workflows/tree/main/publishing-house-daily-desk) — normalize and route the editorial packet.
3. [Commissioning](https://github.com/kujolang/kujo-workflows/tree/main/publishing-house-commissioning) — create the brief, assignments, and evidence work order.
4. [Evidence Dossier](https://github.com/kujolang/kujo-workflows/tree/main/publishing-house-evidence-dossier) — bind material claims to reviewed evidence and rights records.
5. [Primary Piece](https://github.com/kujolang/kujo-workflows/tree/main/publishing-house-primary-piece) — create the authoritative, evidence-linked artifact.
6. [Asset Production](https://github.com/kujolang/kujo-workflows/tree/main/publishing-house-asset-production) — produce supported, accessible media manifests.
7. [Editorial Review](https://github.com/kujolang/kujo-workflows/tree/main/publishing-house-editorial-review) — run independent review and a bounded revision loop.
8. [Adaptation](https://github.com/kujolang/kujo-workflows/tree/main/publishing-house-adaptation) — create a versioned derivative plan without expanding approved claims.
9. [Format Production](https://github.com/kujolang/kujo-workflows/tree/main/publishing-house-format-production) — produce newsletter, social, case-study, and audiovisual packages.
10. [Approval and Publication](https://github.com/kujolang/kujo-workflows/tree/main/publishing-house-approval-publication) — pause for exact human approval before any bounded PressWire effect.
11. [Post-Publication](https://github.com/kujolang/kujo-workflows/tree/main/publishing-house-post-publication) — record measurements, learning, limits, and a non-commissioning follow-up recommendation.

## Eleven operator skills

Start with [Kujo Publishing House Workflows](https://github.com/kujolang/kujo-skills/tree/main/skills/kujo-publishing-house-workflows) for lifecycle routing. Use the eight tool skills for exact CLI contracts: [StoryDesk](https://github.com/kujolang/kujo-skills/tree/main/skills/kujo-storydesk-workflows), [Dossier](https://github.com/kujolang/kujo-skills/tree/main/skills/kujo-dossier-workflows), [GalleyPack](https://github.com/kujolang/kujo-skills/tree/main/skills/kujo-galleypack-workflows), [BluePencil](https://github.com/kujolang/kujo-skills/tree/main/skills/kujo-bluepencil-workflows), [VersionSeal](https://github.com/kujolang/kujo-skills/tree/main/skills/kujo-versionseal-workflows), [PressWire](https://github.com/kujolang/kujo-skills/tree/main/skills/kujo-presswire-workflows), [ReaderSignal](https://github.com/kujolang/kujo-skills/tree/main/skills/kujo-readersignal-workflows), and [AssetWorks](https://github.com/kujolang/kujo-skills/tree/main/skills/kujo-assetworks-workflows). Complete setup with [Publishing House Profile Setup](https://github.com/kujolang/kujo-skills/tree/main/skills/publishing-house-profile-setup) and [Publishing House Quality Calibration](https://github.com/kujolang/kujo-skills/tree/main/skills/publishing-house-quality-calibration).

## The approval boundary

`OBSERVE`, `PROPOSE`, and `ACT` are upper bounds, not suggestions. BluePencil
review is editorial evidence; Dispatch pause state is orchestration evidence;
neither is publication authority. VersionSeal binds a human decision to exact
GalleyPack bytes, destination, action, conditions, and expiry. If reviewed
bytes change, approval is invalidated. PressWire is the only tool allowed to
create a publication effect and receipt.

## Run the complete local proof

Install the locked toolchain or inspect the all-eleven fixture in the
[Kujo Workflows repository](https://github.com/kujolang/kujo-workflows/tree/main/docs/publishing-house).
The fixture requires no credentials or network access and cannot publish to a
live destination. Its proof covers contract loading, tool versions, record
checksums, revision, pause/resume, idempotency, and the bounded local effect.
