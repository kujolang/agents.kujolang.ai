# WebOps toolchain 0.1.0 compatibility

The public WebOps agent content consumes the synchronized contract in
`docs/webops-toolchain-contract.json`: SiteProbe `siteprobe.run/v1`,
SearchBridge `searchbridge.result/v1`, and ContentGraph
`contentgraph.graph/v1` with deterministic lexical method v1.

SiteProbe and ContentGraph are read-only at their target/source boundaries.
SearchBridge provider evidence commands are read-only; submission requires the
explicit `index.submission` capability, ACT mode, confirmation, and live
provider authorization. All three tools require explicit output budgets.

The 2026-08-11 release dogfood reproduced the existing 60-page, 1,177-link,
zero-finding SiteProbe baseline and the 60-node, 1,558-edge, zero-orphan
ContentGraph baseline with zero comparison changes.
