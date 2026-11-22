# Agent connection onboarding

The agent detail page has one platform picker driven by the registry’s
versioned compatibility index. An experimental Slack entry can link to setup
information. An install action requires a qualified agent and platform entry
with a setup route and qualification evidence. Vercel Board and other platforms
can use the same control when their installation is qualified.

## What remains for Slack

1. Use one Slack runtime and one provisioning workflow. The current registry
   contains 85 canonical agents and the shared tooling can generate app
   manifests and look up catalog portraits. Distinct native Slack bots still
   need their own app identity, display name, portrait, event settings,
   credentials, and install qualification. Provision and verify those through
   operator tooling. Start with the two agents that passed private QA.
2. Put the install and signed event receiver on a stable HTTPS service. Add
   workspace enrollment, encrypted credentials, channel scoping, rate and
   spending limits, health checks, and operator controls for revocation and
   recovery. Test across independent workspaces, including a workspace that
   requires app approval. Exercise cancellation, uninstall and reinstall,
   duplicate delivery, and tenant isolation.
3. Test the approved distribution path from the catalog through Slack consent
   and the first in-thread reply. Confirm the name and portrait on Slack,
   explain how to add the bot to a channel if Slack requires it, and record
   the effective capabilities. Release install actions only for the entries
   that pass. Slack describes unlisted distribution for pilots and Marketplace
   review for commercial distribution.
   [Slack distribution](https://docs.slack.dev/app-management/distribution/)

## Model setup belongs to the workspace

An ordinary installer chooses the agent and the destination, approves the
app, and opens the channel. Use a verified workspace default where one exists.
For a first installation without a default, offer a managed route if one is
available under an approved cost policy. Otherwise ask the workspace
administrator to connect and verify a route once for everyone.

The workspace owns model credentials, rate and spending limits, and the
default route. An advanced per-agent deployment override can choose a
different verified host and model. The connector carries messages and
requests. The host advertises actual tools and permissions, and model-fit
checks cover the capabilities an agent needs. Report a missing capability
before starting an effect. Keep credentials and endpoint configuration on the
operator surface, outside the static catalog.

Support cloud models through approved vendor authentication. A local-only
setup requires a reachable authenticated host or local bridge and an explicit
local routing policy. Keep local-only traffic on that host unless the
administrator authorizes another route. OpenCode and Command Code need
qualified host or API connections using their supported credentials and plan
entitlements. Installing a Slack app does not grant access to a subscription.
[OpenCode providers](https://opencode.ai/docs/providers/)
[OpenCode local models](https://opencode.ai/docs/models/)
[Command Code authentication](https://commandcode.ai/docs/quickstart)

Vercel Board has its own authorization and task lifecycle. Qualify onboarding
against its CLI or SDK with the same agent identity and host contract.
[Introducing Vercel Board](https://vercel.com/blog/introducing-vercel-board)
